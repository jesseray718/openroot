# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""CANARY:OPENROOT-DOSSIER-AGENT-BENCH-V3
Full dossier pack upfront -> qwen2.5-coder:7b -> script, NO socket timeout.
Self-similar pod at ~/pods/pod_dossier-bench/pod.db, resume-safe."""
import json, re, sqlite3, time, hashlib, urllib.request, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from run_universal_100_test import QUESTIONS, significant_words

MODEL = "qwen2.5-coder:7b"
OLLAMA = "http://localhost:11434/api/generate"
POD = Path.home() / "pods/pod_dossier-bench/pod.db"
CTX_CAP = 16000

SYSTEM = """You are a code-generation engine. Rules:
1. The COMPLETE research dossier is already provided below. Do NOT search, do NOT
   reason about where information came from, do NOT explain your process.
2. Write the answer as ONE complete runnable Python script, in ONE ```python code block.
3. No preamble, no commentary, no follow-up questions. Code block only."""
USER_TMPL = """{system}

DOSSIER (complete, pre-fetched — trust it, use it):
<<<BEGIN DOSSIER>>>
{ctx}
<<<END DOSSIER>>>

TASK: Write the Python script that accomplishes: {q}
Output: one ```python code block, nothing else."""

def sha(t): return hashlib.sha256(t.encode()).hexdigest()

def pod_schema(db):
    db.executescript("""
    CREATE TABLE IF NOT EXISTS ledger(doc_sha256 TEXT PRIMARY KEY, source TEXT, ingested_utc TEXT);
    CREATE TABLE IF NOT EXISTS chunks(chunk_id INTEGER PRIMARY KEY, doc_sha256 TEXT NOT NULL,
      ordinal INTEGER, section_path TEXT, text TEXT NOT NULL, char_start INTEGER, char_end INTEGER);
    CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(text, section_path,
      content='chunks', content_rowid='chunk_id', tokenize='porter unicode61');
    CREATE TABLE IF NOT EXISTS queries(q_id TEXT PRIMARY KEY, question TEXT, q_sha256 TEXT);
    CREATE TABLE IF NOT EXISTS ask_runs(run_id INTEGER PRIMARY KEY, q_sha256 TEXT, model TEXT,
      ctx_chars INTEGER, prompt_sha256 TEXT, answer TEXT, eval_count INTEGER,
      total_duration_ns INTEGER, status TEXT, ran_utc TEXT);
    CREATE TABLE IF NOT EXISTS pathways(q_sha256 TEXT PRIMARY KEY, run_id INTEGER,
      pathway TEXT, cache TEXT, banked_utc TEXT);
    CREATE TABLE IF NOT EXISTS seals(id INTEGER PRIMARY KEY, kind TEXT, root TEXT, sealed_utc TEXT);
    """)

def dossier_pack(q, conns):
    parts, seen = [], set()
    for w in significant_words(q):
        for name, conn, has_fts in conns:
            try:
                if has_fts:
                    rows = conn.execute("SELECT rowid, snippet(chunks_fts,0,'[',']','…',16) "
                                       "FROM chunks_fts WHERE chunks_fts MATCH ? LIMIT 3",(w,)).fetchall()
                else:
                    rows = conn.execute("SELECT chunk_id, substr(text,1,480) FROM chunks "
                                       "WHERE text LIKE ? LIMIT 2",(f"%{w}%",)).fetchall()
                for cid, snip in rows:
                    key = (name, cid)
                    if key in seen: continue
                    seen.add(key)
                    parts.append(f"[pod={name} chunk={cid} word={w}]\n{snip}")
            except Exception:
                pass
    return "\n".join(parts)[:CTX_CAP]

def ollama(prompt):
    req = urllib.request.Request(OLLAMA, data=json.dumps({
        "model": MODEL, "prompt": prompt, "stream": False,
        "options": {"temperature": 0.1, "num_ctx": 16384}}).encode(),
        headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req) as r:  # no timeout: wait indefinitely
        return json.loads(r.read())

def main():
    POD.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(POD, timeout=120)
    db.execute("PRAGMA busy_timeout=120000")
    db.execute("PRAGMA journal_mode=WAL")
    pod_schema(db)
    conns = []
    for pdb in sorted(Path.home().glob("pods/*/pod.db")):
        if pdb.resolve() == POD.resolve(): continue
        try:
            c = sqlite3.connect(f"file:{pdb}?mode=ro", uri=True, timeout=30); c.execute("PRAGMA busy_timeout=30000")
            t = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")]
            conns.append((pdb.parent.name, c, "chunks_fts" in t))
        except Exception: pass
    done = {r[0] for r in db.execute("SELECT q_sha256 FROM pathways")}
    print(f"[{time.strftime('%H:%M:%S')}] pods={len(conns)} resumed-skip={len(done)} [gate]")
    for idx, q in enumerate(QUESTIONS, 1):
        qh = sha(q)
        if qh in done:
            print(f"[{idx:3d}/100] [cache-hit] {q[:45]}..."); continue
        db.execute("INSERT OR IGNORE INTO queries VALUES (?,?,?)", (qh, q, qh))
        ctx = dossier_pack(q, conns)
        prompt = USER_TMPL.format(system=SYSTEM, ctx=ctx, q=q)
        ph = sha(prompt)
        try:
            res = ollama(prompt)
            ans = res.get("response","")
            m = re.search(r"```(?:python)?\s*(.*?)```", ans, re.S)
            if m: ans = m.group(1).strip()
            status = "ok" if len(ans) > 150 else "thin"
            cur = db.cursor()
            cur.execute("INSERT INTO ask_runs(q_sha256,model,ctx_chars,prompt_sha256,answer,"
                        "eval_count,total_duration_ns,status,ran_utc) VALUES (?,?,?,?,?,?,?,?,?)",
                        (qh, MODEL, len(ctx), ph, ans, res.get("eval_count",0),
                         res.get("total_duration",0), status,
                         time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
            rid = cur.lastrowid
            dsha = sha(ans)
            ordi = db.execute("SELECT COALESCE(MAX(ordinal),-1)+1 FROM chunks WHERE doc_sha256=?", (dsha,)).fetchone()[0]
            db.execute("INSERT INTO chunks(doc_sha256,ordinal,section_path,text,char_start,char_end) "
                       "VALUES (?,?,?,?,?,?)", (dsha, ordi, f"q/{idx}", ans, 0, len(ans)))
            db.execute("INSERT INTO chunks_fts(rowid, text, section_path) "
                       "SELECT chunk_id, text, section_path FROM chunks WHERE doc_sha256=? AND ordinal=?",
                       (dsha, ordi))
            db.execute("INSERT OR REPLACE INTO ledger VALUES (?,?,?)",
                       (dsha, MODEL, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
            db.execute("INSERT OR REPLACE INTO pathways VALUES (?,?,?,?,?)",
                       (qh, rid, f"dossier->{MODEL}->script", "hit",
                        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
            db.commit()
            print(f"[{idx:3d}/100] [banked] ctx={len(ctx)}c ev={res.get('eval_count',0)} {q[:40]}...")
        except Exception as e:
            db.execute("INSERT INTO ask_runs(q_sha256,model,ctx_chars,prompt_sha256,answer,eval_count,"
                       "total_duration_ns,status,ran_utc) VALUES (?,?,?,?,?,?,?,?,?)",
                       (qh, MODEL, 0, ph, "", 0, 0, f"error:{e!r}",
                        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
            db.commit(); print(f"[{idx:3d}/100] [held] {e!r}")
    root = sha("|".join(sorted(r[0] for r in db.execute("SELECT q_sha256 FROM pathways"))))
    db.execute("INSERT INTO seals(kind,root,sealed_utc) VALUES (?,?,?)",
               ("merkle", root, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
    db.commit()
    print(f"SEAL ROOT {root[:16]}...\n[end] [banked] run complete")

if __name__ == "__main__":
    main()
