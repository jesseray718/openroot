#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0
"""FTS5 QA router, cached pathways, doc staging. Keys from env ONLY.
Usage: index | ask "<q>" | stage <file> | cache-report
Provider order: GEMINI_API_KEY -> OPENROUTER_API_KEY -> local qwen2.5:3b."""
import hashlib, json, os, re, sqlite3, subprocess, sys, time, urllib.request
from pathlib import Path
ROOT="/home/jesse/openroot"; DB=f"{ROOT}/data/qa_corpus.db"
S="""CREATE TABLE IF NOT EXISTS chunks(id INTEGER PRIMARY KEY,path TEXT,heading TEXT,body TEXT,sig TEXT);
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(body,path UNINDEXED,heading UNINDEXED);
CREATE TABLE IF NOT EXISTS answers(qhash TEXT PRIMARY KEY,question TEXT,answer TEXT,provider TEXT,joules REAL,ts TEXT,corpus_ver TEXT);"""

def split_chunks(path, text):
    """Yield (heading, body) per heading-delimited section — pure, no shared state."""
    sections, heading, buf = [], "", []
    for ln in text.splitlines():
        m = re.match(r"^#{1,3}\s+(.*)", ln)
        if m:
            if buf: sections.append((heading or "(top)", "\n".join(buf)))
            heading, buf = m.group(1).strip(), []
        else: buf.append(ln)
    if buf: sections.append((heading or "(top)", "\n".join(buf)))
    return [(h, b) for h, b in sections if b.strip()]

def index():
    d = sqlite3.connect(DB); d.executescript(S)
    d.execute("DELETE FROM chunks"); d.execute("DELETE FROM chunks_fts")
    n, h0 = 0, hashlib.sha256()
    for p in Path(ROOT).rglob("*.md"):
        s = str(p)
        if any(x in s for x in ("/.git/", "node_modules")): continue
        try: txt = p.read_text(errors="replace")
        except OSError: continue
        for heading, body in split_chunks(s, txt):
            sig = hashlib.sha256((heading+body).encode()).hexdigest()[:12]
            c = d.execute("INSERT INTO chunks(path,heading,body,sig) VALUES(?,?,?,?)",
                          (s, heading, body, sig)).lastrowid
            d.execute("INSERT INTO chunks_fts(rowid,body,path,heading) VALUES(?,?,?,?)",
                      (c, body, s, heading))
            n += 1; h0.update(sig.encode())
    d.commit()
    ver = h0.hexdigest()[:16]
    print(f"[INDEX] {n} chunks | corpus_ver={ver}")
    return d, ver

def retrieve(d, q, limit=5):
    terms = " ".join(f'"{w}"' for w in re.findall(r"\w+", q)[:8])
    try:
        return d.execute("SELECT path,heading,snippet(chunks_fts,0,'[','…',']',12) "
                         "FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY rank LIMIT ?",
                         (terms, limit)).fetchall()
    except sqlite3.OperationalError as e:
        print(f"[FTS5] {e}"); return []

def api(url, hdr, payload):
    r = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=hdr)
    with urllib.request.urlopen(r, timeout=120) as x: return json.loads(x.read())

def ask(q):
    d, ver = index()
    qh = hashlib.sha256((q+ver).encode()).hexdigest()[:16]
    hit = d.execute("SELECT answer,provider,ts FROM answers WHERE qhash=?", (qh,)).fetchone()
    if hit:
        print(f"[CACHE-HIT] {qh} ({hit[2]}, {hit[1]}) — 0 J, 0 API cost\n{hit[0]}"); return
    ctx = retrieve(d, q)
    if not ctx: print("[HELD] no passages matched — broaden or check index"); return
    prompt = ("Answer using ONLY these repo passages; cite file paths; say so if absent.\n"
              "Question: "+q+"\n\n"
              +"\n\n".join(f"[{p} :: {h}]\n{s}" for p, h, s in ctx))
    j, prov = 0.0, "none"
    if os.environ.get("GEMINI_API_KEY"):
        r = api(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={os.environ['GEMINI_API_KEY']}",
                {"Content-Type": "application/json"},
                {"contents": [{"parts": [{"text": prompt}]}]})
        ans = r["candidates"][0]["content"]["parts"][0]["text"]; prov = "gemini"
    elif os.environ.get("OPENROUTER_API_KEY"):
        r = api("https://openrouter.ai/api/v1/chat/completions",
                {"Authorization": "Bearer "+os.environ["OPENROUTER_API_KEY"],
                 "Content-Type": "application/json"},
                {"model": os.environ.get("OR_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
                 "messages": [{"role": "user", "content": prompt}]})
        ans = r["choices"][0]["message"]["content"]; prov = "openrouter"
    else:
        out = subprocess.run(["python3", f"{ROOT}/bin/popw_ledger.py", "call", "qa",
                              "qwen2.5:3b", prompt],
                             capture_output=True, text=True, timeout=400)
        ans = out.stdout; prov = "local:popw-jouled"
    d.execute("INSERT OR REPLACE INTO answers VALUES(?,?,?,?,?,?,?)",
              (qh, q, ans, prov, j, time.strftime("%Y-%m-%dT%H:%M:%S"), ver)); d.commit()
    print(f"[ANSWERED] provider={prov} pathway={qh} — now cached\n{ans}")

def stage(path):
    import shutil
    dst = f"{ROOT}/context_bridge/staged-docs/{Path(path).name}"
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dst); index()
    with open(f"{ROOT}/context_bridge/INBOX.md", "a") as f:
        f.write(f"## {time.strftime('%Y-%m-%dT%H:%M:%S')} staged: {dst} — review & commit\n")
    print(f"[STAGED] {dst}")

def rep():
    d = sqlite3.connect(DB); d.executescript(S)
    print(f"[QA-CACHE] {d.execute('SELECT COUNT(*) FROM answers').fetchone()[0]} cached pathways")
    for q, p, t in d.execute("SELECT question,provider,ts FROM answers ORDER BY ts DESC LIMIT 10"):
        print(f"  [{t}|{p}] {q[:70]}")

a = sys.argv[1:]
if a[:1] == ["index"]: index()
elif a[:1] == ["ask"]: ask(" ".join(a[1:]))
elif a[:1] == ["stage"]: stage(a[1])
elif a[:1] == ["cache-report"]: rep()
else: print(__doc__)
