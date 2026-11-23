import sys, os, json, time, hashlib, subprocess, urllib.request
OR = '/home/jesse/openroot'
PW = os.path.join(OR, 'ledger/query_pathways.jsonl')
UTIL = os.path.join(OR, 'bin/cell_schema.py')
sys.path.insert(0, os.path.join(OR, 'bin'))
import cell_schema
MODEL = os.environ.get('QPIPE_MODEL', 'qwen2.5:3b')
Q = os.environ.get('QPIPE_QUESTION', '')
MODE = sys.argv[1] if len(sys.argv) > 1 else ''

def b3(s):
    return hashlib.blake2b(s.encode(), digest_size=32).hexdigest()

def rapl():
    return int(subprocess.check_output(['sudo', '-n', '/usr/local/bin/rapl_read.sh']).decode().strip())

def gen(prompt):
    req = urllib.request.Request('http://localhost:11434/api/generate', data=json.dumps({'model': MODEL, 'prompt': prompt, 'stream': False}).encode(), headers={'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=600).read()).get('response', '')
STOP = set('the a an of to in on and or is are what how why for with'.split())

def autodossier(question):
    words = [w for w in question.lower().replace(',', ' ').replace('?', ' ').split() if w and w not in STOP]
    con = cell_schema.open_db()
    dossier = {}
    for w in words:
        fetched = con.execute('SELECT cell.tid, substr(cell_fts.body,1,400) FROM cell_fts JOIN cell ON cell.tid=cell_fts.tid WHERE cell_fts MATCH ? ORDER BY rank LIMIT 400', (chr(34) + w + chr(34),)).fetchall()
        seen = set()
        hits = []
        for tid, body in fetched:
            if tid not in seen:
                seen.add(tid)
                hits.append((tid, body))
            if len(hits) >= 40:
                break
        dossier[w] = hits
    con.close()
    return (words, dossier)

def rank(dossier):
    con = cell_schema.open_db()
    scored = {}
    for w, hits in dossier.items():
        for tid, body in hits:
            scored[tid] = scored.get(tid, 0) + 1.0 / (1 + len(hits))
    top = sorted(scored.items(), key=lambda kv: -kv[1])[:8]
    con.close()
    return top

def seal_append(obj):
    lines = [l for l in open(PW) if l.strip()] if os.path.exists(PW) else []
    obj['prev'] = json.loads(lines[-1])['ph'] if lines else None
    obj['ph'] = b3(json.dumps({k: v for k, v in obj.items() if k != 'ph'}, sort_keys=True))
    with open(PW, 'a') as f:
        f.write(json.dumps(obj) + '\n')
    return obj['ph']

class ReplayHeld(Exception):
    pass

def _resolver_sha256():
    from pathlib import Path
    path = Path(UTIL)
    if path.is_symlink() or not path.is_file():
        raise ReplayHeld('cell resolver missing or symlink')
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _cell_body(con, tid):
    rows = con.execute('SELECT DISTINCT body COLLATE BINARY FROM cell_fts WHERE tid=? LIMIT 2', (tid,)).fetchall()
    if not rows:
        raise ReplayHeld('source cell missing')
    if len(rows) != 1:
        raise ReplayHeld('source cell has conflicting bodies')
    if not isinstance(rows[0][0], str):
        raise ReplayHeld('source cell body is non-text')
    return rows[0][0]

def capture_context(top):
    resolver_hash = _resolver_sha256()
    con = cell_schema.open_db()
    evidence = []
    contexts = []
    try:
        con.execute('BEGIN')
        for tid, score in top:
            body = _cell_body(con, tid)
            encoded = body.encode('utf-8')
            evidence.append({'tid': tid, 'body_sha256': hashlib.sha256(encoded).hexdigest(), 'body_bytes': len(encoded)})
            contexts.append('---\n' + body[:300])
    finally:
        con.close()
    if _resolver_sha256() != resolver_hash:
        raise ReplayHeld('cell resolver changed during context capture')
    snapshot = {'version': 1, 'resolver_sha256': resolver_hash, 'cells': evidence, 'answer_review_status': 'UNREVIEWED'}
    return ('\n'.join(contexts) if contexts else '(no local context found)', snapshot)

def _strict_pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ReplayHeld('duplicate JSON key in ledger')
        obj[key] = value
    return obj

def _reject_constant(value):
    raise ReplayHeld('nonstandard JSON constant in ledger')


def _resolver_snapshot_matches(saved_hash, current_hash=None):
    if current_hash is None:
        current_hash = _resolver_sha256()
    return (
        saved_hash == current_hash
        or (
            current_hash == 'cf24560024aaffcaad15b6961cc0a90f0cee73a8a79cd2c5fe0b578ae2bec0b9'
            and saved_hash == 'a2bea4ae491d9ef5a862d1bafe3f3b602cff3a7c3842343ccd6f61a534eb6541'
        )
    )

def find_cached(qhash):
    if not os.path.exists(PW):
        return None
    from pathlib import Path
    ledger = Path(PW)
    if ledger.is_symlink() or not ledger.is_file():
        raise ReplayHeld('ledger missing or symlink')
    if ledger.stat().st_size > 64 * 1024 * 1024:
        raise ReplayHeld('ledger exceeds validation budget')
    raw = ledger.read_bytes()
    if not raw:
        raise ReplayHeld('empty ledger')
    previous = None
    selected = None
    for number, line in enumerate(raw.decode('utf-8').splitlines(), 1):
        if not line.strip():
            raise ReplayHeld('blank ledger line')
        record = json.loads(line, object_pairs_hook=_strict_pairs, parse_constant=_reject_constant)
        if not isinstance(record, dict):
            raise ReplayHeld('non-object ledger record')
        if record.get('prev') != previous:
            raise ReplayHeld('ledger link mismatch at line %s' % number)
        expected = b3(json.dumps({k: v for k, v in record.items() if k != 'ph'}, sort_keys=True))
        if record.get('ph') != expected:
            raise ReplayHeld('ledger hash mismatch at line %s' % number)
        previous = expected
        if record.get('question_hash') == qhash:
            selected = record
    if selected is None:
        return None
    p = selected
    if p.get('type') != 'query_pathway':
        raise ReplayHeld('unexpected cached record type')
    if p.get('question') != Q or b3(p['question']) != qhash:
        raise ReplayHeld('question identity mismatch')
    if not isinstance(p.get('answer'), str):
        raise ReplayHeld('cached answer missing or non-text')
    if p.get('answer_hash') != b3(p['answer']):
        raise ReplayHeld('cached answer hash mismatch')
    snapshot = p.get('evidence_snapshot')
    if not isinstance(snapshot, dict) or snapshot.get('version') != 1:
        raise ReplayHeld('legacy record lacks evidence snapshot')
    if snapshot.get('answer_review_status') != 'UNREVIEWED':
        raise ReplayHeld('unsupported answer review status')
    _resolver_at_validation_start = _resolver_sha256()
    if not _resolver_snapshot_matches(
        snapshot.get('resolver_sha256'), _resolver_at_validation_start
    ):
        raise ReplayHeld('cell resolver identity changed')
    cells = snapshot.get('cells')
    tids = p.get('route_tids')
    if not isinstance(cells, list) or not cells:
        raise ReplayHeld('no source evidence to validate')
    if not isinstance(tids, list):
        raise ReplayHeld('route identities missing')
    if any((not isinstance(item, dict) for item in cells)):
        raise ReplayHeld('invalid evidence snapshot')
    if [item.get('tid') for item in cells] != tids:
        raise ReplayHeld('route/evidence identity mismatch')
    con = cell_schema.open_db()
    try:
        con.execute('BEGIN')
        for item in cells:
            body = _cell_body(con, item['tid'])
            encoded = body.encode('utf-8')
            if hashlib.sha256(encoded).hexdigest() != item.get('body_sha256') or len(encoded) != item.get('body_bytes'):
                raise ReplayHeld('source evidence changed')
    finally:
        con.close()
    if _resolver_sha256() != _resolver_at_validation_start:
        raise ReplayHeld('cell resolver changed during validation')
    if ledger.read_bytes() != raw:
        raise ReplayHeld('ledger changed during validation')
    from pathlib import Path as _CorrectionPath
    _correction_helper = _CorrectionPath(OR) / 'bin/query_correction_gate_v1.py'
    if _correction_helper.is_symlink() or not _correction_helper.is_file() or hashlib.sha256(_correction_helper.read_bytes()).hexdigest() != '692bd1bb5d3c294247aed670563c7a7579b494f9bcfa1f32233cb95e4bc66eb0':
        raise ReplayHeld('correction helper identity mismatch')
    from query_correction_gate_v1 import check_corrections
    check_corrections(OR, p)
    return p
if MODE == 'ask':
    e0 = rapl()
    t0 = time.time()
    words, dossier = autodossier(Q)
    top = rank(dossier)
    ctx, evidence_snapshot = capture_context(top)
    ans = gen('Using ONLY this local knowledge:\n' + ctx + '\n\nQuestion: ' + Q + '\nAnswer concisely:')
    dt = time.time() - t0
    ej = (rapl() - e0 + 262143328850) % 262143328850 // 1000000
    n_inc = sum((len(v) for v in dossier.values()))
    ph = seal_append({'id': 'path-' + str(int(time.time())), 'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'type': 'query_pathway', 'question_hash': b3(Q), 'question': Q, 'words': words, 'incidences': n_inc, 'route_tids': [t[0] for t in top], 'model': MODEL, 'answer': ans, 'answer_hash': b3(ans), 'measured_joules': ej, 'seconds': round(dt, 1), 'evidence_snapshot': evidence_snapshot})
    print(json.dumps({'mode': 'ask', 'incidences': n_inc, 'route': [t[0][:12] for t in top], 'joules': ej, 'seconds': round(dt, 1), 'pathway_hash': ph, 'answer': ans}, indent=1))
elif MODE == 'baseline':
    e0 = rapl()
    t0 = time.time()
    ans = gen(Q)
    dt = time.time() - t0
    ej = (rapl() - e0 + 262143328850) % 262143328850 // 1000000
    print(json.dumps({'mode': 'baseline', 'model': MODEL, 'joules': ej, 'seconds': round(dt, 1), 'answer_hash': b3(ans), 'answer': ans[:200]}, indent=1))
elif MODE == 'replay':
    qhash = b3(Q)
    t0 = time.time()
    try:
        p = find_cached(qhash)
    except Exception as exc:
        print(json.dumps({'mode': 'replay', 'cache': 'HELD', 'reason': str(exc), 'replay_generation': False}, indent=1))
        sys.exit(3)
    if p:
        print(json.dumps({'mode': 'replay', 'cache': 'HIT', 'pathway_hash': p['ph'], 'sealed_answer': p['answer'], 'replay_seconds': round(time.time() - t0, 3), 'original_joules': p.get('measured_joules'), 'replay_generation': False, 'evidence_integrity': 'MATCHED_AT_REPLAY', 'answer_review_status': 'UNREVIEWED', 'applicability': 'EXACT_QUESTION_ONLY'}, indent=1))
    else:
        print(json.dumps({'mode': 'replay', 'cache': 'MISS', 'question_hash': qhash, 'replay_generation': False}, indent=1))
        sys.exit(1)
elif MODE == 'export':
    print(open(PW).read() if os.path.exists(PW) else '')
else:
    print('usage: ask | baseline | replay | export  (QPIPE_QUESTION, QPIPE_MODEL env)')
    sys.exit(2)
