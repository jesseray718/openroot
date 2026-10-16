# SPDX-License-Identifier: GPL-3.0-only
#!/usr/bin/env python3
"""CANARY:OPENROOT-ANYDATASET-TO-POD-V1
Any dataset -> pod.db: chunked, sha256-per-chunk, FTS5, Nomic embeddings.
Usage: python3 any_dataset_to_pod_v1.py <input_dir_or_files...> <pod_name>
PDFs (if pdftotext present) and .txt/.md/.json/.csv/.html ingested.
"""
import sqlite3, hashlib, sys, os, re, json, time, urllib.request, pathlib, subprocess

MIN_TOKENS, OVERLAP = 30, 2   # sentence-window chunking: window of sentences
STOP = set("the a an and or but if then of to in on at by for with is are was were be been i it its this that as".split())

def read_text(p):
    if p.suffix.lower() == ".pdf":
        try:
            r = subprocess.run(["pdftotext", str(p), "-"], capture_output=True, timeout=60)
            if r.returncode == 0: return r.stdout.decode("utf-8", "replace")
        except FileNotFoundError: pass
        return None
    if p.suffix.lower() in (".txt", ".md", ".json", ".jsonl", ".csv", ".html", ".xml", ".yml", ".yaml", ".tex", ".srt"):
        try:
            return p.read_text(encoding="utf-8", errors="replace")
        except Exception: return None
    return None

def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

def chunks_from(sent_list):
    out, cur = [], []
    for s in sent_list:
        cur.append(s)
        if len(cur) >= MIN_TOKENS + OVERLAP and len(" ".join(cur)) > 400:
            out.append(" ".join(cur)); cur = cur[-OVERLAP:]
    if cur: out.append(" ".join(cur))
    return out

def embed(texts):
    req = urllib.request.Request("http://localhost:11434/api/embed",
        data=json.dumps({"model":"nomic-embed-text","input":texts}).encode(),
        headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())["embeddings"]

def build(inputs, pod_path):
    os.makedirs(os.path.dirname(pod_path), exist_ok=True)
    db = sqlite3.connect(pod_path, timeout=30)
    db.executescript("""
      PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL; PRAGMA wal_autocheckpoint=2000;
      CREATE TABLE IF NOT EXISTS files(path TEXT PRIMARY KEY, sha256 TEXT, mtime REAL, size INT);
      CREATE TABLE IF NOT EXISTS chunks(chunk_id INTEGER PRIMARY KEY, file_path TEXT, idx INT,
        sha256 TEXT UNIQUE, text TEXT, created_utc TEXT);
      CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(text, content='chunks', content_rowid='chunk_id');
      CREATE TABLE IF NOT EXISTS vec_chunks(chunk_id INTEGER PRIMARY KEY, vec TEXT);
    """)
    files, pending = [], []
    for inp in inputs:
        p = pathlib.Path(inp)
        cand = [p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file())
        for f in cand:
            t = read_text(f)
            if not t or len(t) < 40: continue
            fh = hashlib.sha256(t.encode()).hexdigest()
            files.append((str(f), fh, f.stat().st_mtime, f.stat().st_size))
            for i, c in enumerate(chunks_from(sentences(t))):
                ch = hashlib.sha256((fh + ":" + str(i)).encode()).hexdigest()
                db.execute("INSERT OR IGNORE INTO chunks(file_path,idx,sha256,text,created_utc) VALUES(?,?,?,?,?)",
                           (str(f), i, ch, c, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
            pending.append(f)
    db.executemany("INSERT OR REPLACE INTO files VALUES(?,?,?,?)", files)
    db.commit()
    print(f"[gate] {len(files)} files, {db.execute('SELECT COUNT(*) FROM chunks').fetchone()[0]} chunks")
    db.execute("INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild')")
    rows = db.execute("SELECT chunk_id, text FROM chunks WHERE chunk_id NOT IN (SELECT chunk_id FROM vec_chunks)").fetchall()
    for i in range(0, len(rows), 64):
        batch = rows[i:i+64]
        vecs = embed([r[1][:512] for r in batch])
        db.executemany("INSERT OR REPLACE INTO vec_chunks VALUES(?,?)",
                       [(batch[j][0], json.dumps(v)) for j, v in enumerate(vecs)])
        db.commit()
        print(f"[gate] embedded {min(i+64,len(rows))}/{len(rows)}")
    print(f"[banked] pod sealed: {pod_path} files={len(files)} chunks={db.execute('SELECT COUNT(*) FROM chunks').fetchone()[0]} vecs={db.execute('SELECT COUNT(*) FROM vec_chunks').fetchone()[0]}")
    print("[exit=0]")

if __name__ == "__main__":
    build(sys.argv[1:-1], f"/home/jesse/pods/{sys.argv[-1]}/pod.db")
