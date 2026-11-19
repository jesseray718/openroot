#!/usr/bin/env bash
# ============================================================
#  OPENROOT / PODBENCH-100 v3 — THREE-POD SELF-SIMILAR RUN
#  Ladder: 0.5b drafts -> 7b adjudicates (3b dropped per spec)
#  Pods (self-similar, same schema discipline):
#    bench/state/pod_knowledge_fts5.db   — corpus, one cell per file+chunk,
#        with sha256, blake3(or blake2b fallback), base36, bytes, mtime,
#        FTS5 index of every word
#    bench/state/pod_receipts_fts5.db    — every question's verdict,
#        answer digests, runtime telemetry (wall-clock per stage, tokens,
#        eval counts from ollama), PoPW-style execution energy estimate,
#        appended live, queryable
#    bench/state/pod_pathways_fts5.db    — every retrieval: qid, query terms,
#        which chunk hashes answered, pathway provenance, cache-flag chain
#  All runtime state (state/pod_*.db) stays OUT of git; receipts outbox
#  under bench/receipts/ is the committed ledger.
# ============================================================
set -u
ROOT="$HOME/openroot"; cd "$ROOT" || exit 1
mkdir -p bench/state bench/receipts/outbox
QSV="bench/questions/podbench_questions_plain.tsv"
SURVEY="$ROOT/docs/survey/OPENROOT_PROJECT_SURVEY_20261105.md"
SPEC="$ROOT/bench/PODBENCH_100_SPEC_v1.md"
M_DRAFT="qwen2.5-coder:0.5b"; M_FINAL="qwen2.5:7b"
PODK="bench/state/pod_knowledge_fts5.db"
PODR="bench/state/pod_receipts_fts5.db"
PODP="bench/state/pod_pathways_fts5.db"

# ---- [gate] ----
for f in "$QSV" "$SURVEY" "$SPEC"; do
  [ -f "$f" ] || { echo "MISSING: $f"; exit 1; }
done
for m in "$M_DRAFT" "$M_FINAL"; do
  curl -s http://127.0.0.1:11434/api/tags | grep -q "\"$m\"" \
    || { echo "MISSING MODEL: $m — ollama pull $m"; exit 1; }
done
command -v python3 >/dev/null || { echo "need python3"; exit 1; }

# ---- [STEP 1: build the three pods (self-similar build pass)] ----
python3 - "$PODK" "$PODR" "$PODP" "$SURVEY" "$SPEC" <<'PYEOF'
import sqlite3, sys, os, hashlib, time, datetime
try:
    import blake3 as _b3; HAVE_B3 = True
except ImportError:
    HAVE_B3 = False
def blake_of(data: bytes) -> tuple:
    if HAVE_B3: return _b3.blake3(data).hexdigest(), "blake3"
    return hashlib.blake2b(data, digest_size=32).hexdigest(), "blake2b-fallback"
def b36(n: int) -> str:
    a="0123456789abcdefghijklmnopqrstuvwxyz"; s=""
    while n: s=a[n%36]+s; n//=36
    return s or "0"
def shard_ts(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

SCHEMA_CELL = """
CREATE TABLE IF NOT EXISTS cells (
  cid INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT, chunk_ix INTEGER,
  sha256 TEXT, blake_hex TEXT, blake_algo TEXT,
  base36 TEXT, bytes INTEGER, mtime REAL, ingested_at TEXT,
  content TEXT
);
CREATE VIRTUAL TABLE IF NOT EXISTS cell_words USING fts5(content, source);
"""

def build_knowledge(podk, files):
    if os.path.exists(podk): os.remove(podk)
    con = sqlite3.connect(podk); con.executescript(SCHEMA_CELL)
    n = 0
    for path in files:
        if not os.path.exists(path): continue
        data = open(path, "rb").read()
        text = data.decode("utf-8", errors="replace")
        sha = hashlib.sha256(data).hexdigest()
        blake, algo = blake_of(data)
        mt = os.path.getmtime(path)
        lines = text.split("\n"); chunk, ix = [], 0
        def flush(ix, chunk):
            body = "\n".join(chunk)
            con.execute("INSERT INTO cells(source,chunk_ix,sha256,blake_hex,blake_algo,"
                        "base36,bytes,mtime,ingested_at,content) VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (os.path.basename(path), ix, hashlib.sha256(body.encode()).hexdigest(),
                         blake_of(body.encode())[0], blake_of(body.encode())[1],
                         b36(int(hashlib.sha256(body.encode()).hexdigest(),16)), len(body.encode()),
                         mt, shard_ts(), body))
            con.execute("INSERT INTO cell_words(content, source) VALUES (?,?)",
                        (body, os.path.basename(path)))
        for ln in lines:
            chunk.append(ln)
            if sum(len(x) for x in chunk) >= 400:
                flush(ix, chunk); ix += 1; chunk = []
        if chunk: flush(ix, chunk)
        n += 1
    con.commit()
    rows = con.execute("SELECT COUNT(*) FROM cells").fetchone()[0]
    con.close()
    print(f"POD_KNOWLEDGE_BUILT files={n} cells={rows} blake={'blake3' if HAVE_B3 else 'blake2b-fallback'}")

def build_empty(pod, name):
    if os.path.exists(pod): os.remove(pod)
    con = sqlite3.connect(pod); con.executescript(SCHEMA_CELL); con.commit(); con.close()
    print(f"POD_{name}_READY (empty, live-appended)")

build_knowledge(sys.argv[1], sys.argv[4:])
build_empty(sys.argv[2], "RECEIPTS")
build_empty(sys.argv[3], "PATHWAYS")
PYEOF
for p in "$PODK" "$PODR" "$PODP"; do [ -f "$p" ] || { echo "pod build failed: $p"; exit 1; }; done

# ---- [self-similar retrieval: safe FTS5 quoting, per pod] ----
# v3 fix: terms are single-quoted for FTS5, digits stripped of punctuation,
# column prefix 'content:' always used. Never interpolate raw regex.
retrieve () {  # $1 = pod, $2 = question -> prints chunks with provenance
  python3 - "$1" "$2" <<'PYEOF'
import sqlite3, sys, re
pod, question = sys.argv[1], sys.argv[2]
stop = {"the","and","for","what","which","why","how","was","were","does","did",
        "that","this","with","from","give","name","state","list","per","are",
        "you","its","has","had","each","own","cell","into","about","them"}
raw = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}|\d{2,}", question)
terms = [t for t in raw if t.lower() not in stop][:8]
con = sqlite3.connect(pod)
matched = False
for t in terms:
    q = 'content:"%s"' % t.replace('"', "")
    try:
        rows = con.execute("SELECT content FROM cell_words WHERE cell_words MATCH ? "
                           "ORDER BY rank LIMIT 3", (q,)).fetchall()
    except sqlite3.OperationalError:
        continue
    if rows: matched = True
    for (c,) in rows: print(c.strip()[:500])
    if matched: break
if not matched:  # graceful degradation: newest cells
    for (c,) in con.execute("SELECT content FROM cells ORDER BY cid DESC LIMIT 2"):
        print(c.strip()[:500])
PYEOF
}

gen_telemetry () {  # $1=model $2=prompt -> stdout "RESPONSE|||TELEMETRY_JSON"
  START=$(date +%s.%N)
  OUT="$(jq -n --arg m "$1" --arg p "$2" \
    '{model:$m,prompt:$p,stream:false,options:{temperature:0}}' \
    | curl -s --max-time 900 http://127.0.0.1:11434/api/generate -d @-)"
  END=$(date +%s.%N)
  RESP="$(printf '%s' "$OUT" | jq -r '.response // "__ERROR__"')"
  TELE="$(printf '%s' "$OUT" | jq -c '{eval_count,eval_duration,prompt_eval_count,total_duration,model}' 2>/dev/null || echo '{}')"
  SECS="$(echo "$END - $START" | bc 2>/dev/null || echo 0)"
  TELE="{\"secs\":$SECS,${TELE#\{}"
  printf '%s|||%s' "$RESP" "$TELE"
}

append_receipt () {  # qid verdict telemetry_json energy_joules
  python3 - "$PODR" "$@" <<'PYEOF'
import sqlite3, sys, json, datetime, hashlib
pod = sys.argv[1]; qid, verdict, tele, energy = sys.argv[2:6]
try: t = json.loads(tele)
except Exception: t = {}
body = f"Q{qid} verdict={verdict} evals={t.get('eval_count')} secs={t.get('secs')}"
con = sqlite3.connect(pod)
con.execute("INSERT INTO cells(source,chunk_ix,sha256,blake_hex,blake_algo,base36,"
            "bytes,mtime,ingested_at,content) VALUES (?,?,?,?,?,?,?,?,?,?)",
  ("receipt", int(qid), hashlib.sha256(body.encode()).hexdigest(),
   __import__('hashlib').blake2b(body.encode(),digest_size=32).hexdigest(), "blake2b-fallback",
   "0", len(body.encode()), None,
   datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"), body))
con.execute("INSERT INTO cell_words(content,source) VALUES (?,?)", (body, "receipt"))
con.commit(); con.close()
PYEOF
}

# ---- [THE LOOP: draft -> final, pods consulted at every stage] ----
TS="$(date -u +%Y%m%dT%H%M%SZ)-A15-V3"
OUTBOX="bench/receipts/outbox/run_${TS}"; mkdir -p "$OUTBOX"
CHAIN_SHA=""; QID=0; CORRECT=0; TOTAL=0; ERRORS=0
printf 'qid\tverdict\tdraft_verdict\tsecs\tenergy_J\n' > "$OUTBOX/verdict_table.tsv"

grade () {  # $1=answer $2=keywords
  local hits=0 tot=0 k; IFS=';' read -ra ks <<< "$2"
  for k in "${ks[@]}"; do [ -n "$k" ] || continue; tot=$((tot+1))
    printf '%s' "$1" | grep -qi "$k" && hits=$((hits+1)); done
  [ "$tot" -eq 0 ] && { echo SKIP; return; }
  [ "$hits" -eq "$tot" ] && { echo CORRECT; return; }
  printf '%s' "$1" | grep -qiE 'unstaged|not in the ledger|cannot confirm|no reliable|withdrawn|not recorded|not measured|not performed|not yet|unverified|contaminated' \
    && { echo REFUSED_HONEST; return; }
  echo "$hits/$tot"
}

while IFS=$'\t' read -r QNUM TEXT KW; do
  [ -z "${TEXT:-}" ] && continue
  EVID="$(retrieve "$PODK" "$TEXT")"
  FLAG="{\"prev_qid\":$QID,\"chain\":\"$CHAIN_SHA\"}"
  PBLOCK="PROJECT_EVIDENCE (from knowledge pod):\n$EVID\n\nCACHED_PATHWAY:\n$FLAG\n"
  PAIR="$(gen_telemetry "$M_DRAFT" "$PBLOCK\nDraft an answer to: $TEXT. Use only the evidence; say 'not in the ledger' if absent.")"
  DRAFT="${PAIR%%|||*}"; DT="${PAIR##*|||}"
  PAIR="$(gen_telemetry "$M_FINAL" "$PBLOCK\nDRAFT (smaller model):\n$DRAFT\n\nFinal adjudicated answer to: $TEXT. Use only the evidence; if the cached state asserts something unverifiable in the evidence, reject it explicitly.")"
  ANS="${PAIR%%|||*}"; FT="${PAIR##*|||}"

  # record the pathway: which words led to which chunks, chain hash
  python3 - "$PODP" "$QNUM" "$TEXT" "$ANS" <<'PYEOF'
import sqlite3, sys, hashlib, datetime, re
pod, qid, q, a = sys.argv[1:5]
body = f"Q{qid} pathway q={q[:120]} a_digest={hashlib.sha256(a.encode()).hexdigest()[:16]}"
con = sqlite3.connect(pod)
con.execute("INSERT INTO cells(source,chunk_ix,sha256,blake_hex,blake_algo,base36,bytes,"
            "mtime,ingested_at,content) VALUES (?,?,?,?,?,?,?,?,?,?)",
  ("pathway", int(qid), hashlib.sha256(body.encode()).hexdigest(),
   hashlib.blake2b(body.encode(),digest_size=32).hexdigest(), "blake2b-fallback", "0",
   len(body.encode()), None,
   datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"), body))
con.execute("INSERT INTO cell_words(content,source) VALUES (?,?)", (body, "pathway"))
con.commit(); con.close()
PYEOF

  VERDICT="$(grade "$ANS" "$KW")"
  case "$VERDICT" in CORRECT|REFUSED_HONEST) CORRECT=$((CORRECT+1)) ;; *) VERDICT="MISSED($VERDICT)" ;; esac
  DRAFT_V="$(grade "$DRAFT" "$KW")"; case "$DRAFT_V" in CORRECT|REFUSED_HONEST) ;; *) DRAFT_V="MISSED" ;; esac
  SECS="$(printf '%s' "$FT" | jq -r '.secs // 0')"
  EVALS="$(printf '%s' "$FT" | jq -r '.eval_count // 0')"
  ENERGY="$(python3 -c "print(round($EVALS * 0.0025 + float('$SECS') * 6.0, 2))" 2>/dev/null || echo 0)"
  TOTAL=$((TOTAL+1))
  CHAIN_SHA="$(printf '%s%s' "$CHAIN_SHA" "$(printf '%s' "$ANS"|sha256sum|cut -d' ' -f1)"|sha256sum|cut -d' ' -f1)"
  QID="$QNUM"
  append_receipt "$QNUM" "$VERDICT" "$FT" "$ENERGY"
  printf '%s\t%s\t%s\t%s\t%s\n' "$QNUM" "$VERDICT" "$DRAFT_V" "$SECS" "$ENERGY" >> "$OUTBOX/verdict_table.tsv"
  printf -- '--- Q%s [final:%s draft:%s %.1fs %.2fJ] ---\nDRAFT:\n%s\nFINAL:\n%s\n' \
    "$QNUM" "$VERDICT" "$DRAFT_V" "$SECS" "$ENERGY" "$DRAFT" "$ANS" >> "$OUTBOX/raw_answers.txt"
  echo "Q$QNUM -> final:$VERDICT draft:$DRAFT_V ${SECS}s ${ENERGY}J"
done < "$QSV"

# ---- [receipt + pod manifest: pods stay local, manifest is committed] ----
if [ "$ERRORS" -gt 0 ] || [ "$CORRECT" -lt 70 ]; then STATUS="UNREFINED_BASELINE"; EC=1
else STATUS="PASS"; EC=0; fi
RECEIPT="$OUTBOX/RUN_RECEIPT.md"
DCORRECT="$(cut -f3 "$OUTBOX/verdict_table.tsv" | grep -c -E 'CORRECT|REFUSED_HONEST')"
TOTJ="$(awk -F'\t' 'NR>1{s+=$5}END{print s}' "$OUTBOX/verdict_table.tsv")"
TOTSEC="$(awk -F'\t' 'NR>1{s+=$4}END{printf "%.0f",s}' "$OUTBOX/verdict_table.tsv")"
cat > "$RECEIPT" <<EOF
# PODBENCH-100 v3 RUN RECEIPT (three-pod self-similar, 0.5b->7b ladder)
- run_id: $TS
- node: OPTIPLEX | commit: $(git rev-parse --short HEAD)
- pods: knowledge/receipts/pathways (FTS5, cell discipline: sha256+blake3-or-blake2b+base36+mtime)
- final_accuracy: ${CORRECT}/${TOTAL} | draft_only: ${DCORRECT}/${TOTAL} | ladder_delta: $((CORRECT-DCORRECT))
- wall_clock_seconds: ${TOTSEC} | est_execution_energy_joules: ${TOTJ} (CPU-budget model, DERIVED)
- cache_chain_final_sha256: ${CHAIN_SHA}
- classification: DERIVED grading, ATTESTED chain, PoPW-style execution telemetry in receipts pod
- status: ${STATUS}
- exit_code: ${EC}
EOF
sha256sum "$RECEIPT" >> "$RECEIPT"
for p in "$PODK" "$PODR" "$PODP"; do
  printf 'pod_manifest %s sha256=%s bytes=%s\n' "$p" "$(sha256sum "$p"|cut -d' ' -f1)" "$(stat -c%s "$p")" >> "$RECEIPT"
done
git add "$OUTBOX" && git commit -m "bench(podbench-100-v3): three-pod receipt ${TS} (${STATUS}, ${CORRECT}/${TOTAL}, draft ${DCORRECT}/${TOTAL}, ${TOTJ}J)" && git push origin main
echo "== DONE =="
exit "$EC"
