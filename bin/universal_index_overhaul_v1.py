# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""CANARY:OPENROOT-UNIVERSAL-INDEX-OVERHAUL-V1
Phase 1: Index every file in [~/openroot, ~, A15 corpus] -> FTS5 + sha256 + mtime + metadata.
Phase 2: Per-keyword dossier resolver (instant, cached).
Phase 3: Feed 7B coder live dossiers -> writes openroot overhaul + fixes broken files.
Resume-safe: file state keyed by (path, mtime, sha256). No socket timeout."""
import json, os, re, sqlite3, sys, time, hashlib, urllib.request
from pathlib import Path

DB = Path.home()/"pods/pod_universal/pod.db"
LOG_DIR = Path.home()/"openroot/logs"
MODEL = "qwen2.5-coder:7b"
OLLAMA = "http://localhost:11434/api/generate"
SKIP_DIRS = {".git","node_modules","__pycache__","venv",".venv",".cache","cache",
             "target","build","dist","logs",".gradle",".terraform","site-packages",
             ".cargo",".rustup","consolidation-backups","unpacked","vendor","vendored",
             "registry","crates",".npm",".m2",".tox",".eggs","site-packages",".local",".cache2"}
TEXT_EXT = {".txt",".md",".py",".sh",".json",".jsonl",".yaml",".yml",".toml",".cfg",
            ".ini",".csv",".tsv",".html",".css",".js",".ts",".rs",".go",".c",".h",
            ".cpp",".sql",".xml",".log",".conf",".service",".env",".gitignore",".lock"}
MAX_BYTES = 2_000_000

def sha(t): return hashlib.sha256(t.encode()).hexdigest()

def schema(db):
    db.executescript("""
    CREATE TABLE IF NOT EXISTS files(file_sha256 TEXT PRIMARY KEY, path TEXT UNIQUE, size INTEGER,
      mtime REAL, ext TEXT, source TEXT, ingested_utc TEXT);
    CREATE TABLE IF NOT EXISTS chunks(chunk_id INTEGER PRIMARY KEY, doc_sha256 TEXT NOT NULL,
      ordinal INTEGER, section_path TEXT, text TEXT NOT NULL, char_start INTEGER, char_end INTEGER);
    CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(text, section_path,
      content='chunks', content_rowid='chunk_id', tokenize='porter unicode61');
    CREATE TABLE IF NOT EXISTS embed_cache(input_sha256 TEXT PRIMARY KEY, vec BLOB, cached_utc TEXT);
    CREATE TABLE IF NOT EXISTS dossiers(word TEXT PRIMARY KEY, dossier TEXT, word_sha256 TEXT,
      built_utc TEXT);
    CREATE TABLE IF NOT EXISTS corrections(id INTEGER PRIMARY KEY, path TEXT, issue TEXT,
      fix TEXT, status TEXT, fixed_utc TEXT);
    CREATE TABLE IF NOT EXISTS pathways(task_sha256 TEXT PRIMARY KEY, kind TEXT, answer TEXT,
      model TEXT, banked_utc TEXT);
    CREATE TABLE IF NOT EXISTS seals(id INTEGER PRIMARY KEY, kind TEXT, root TEXT, sealed_utc TEXT);
    CREATE INDEX IF NOT EXISTS idx_files_mtime ON files(mtime);
    CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks(doc_sha256);
    """)

def roots():
    r = [("openroot", Path.home()/"openroot"),
         ("home", Path.home()),
         ("a15-shared", Path("/mnt/sdb1")),  # SD mount; A15 corpus reachable here when mounted
         ("a15-termux", Path("/mnt/sdb1/termux-home"))]
    return [(n,p) for n,p in r if p.exists()]

def scan_and_ingest(db):
    n_new = n_skip = n_err = 0
    def maybe_commit():
        if n_new and n_new % 2500 == 0:
            db.commit(); db.execute("PRAGMA wal_checkpoint(PASSIVE)")
    for source, root in roots():
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".git")]
            for fn in filenames:
                p = Path(dirpath)/fn
                try:
                    st = p.stat()
                    if st.st_size > MAX_BYTES or st.st_size == 0: continue
                    if p.suffix.lower() not in TEXT_EXT and not p.is_file(): continue
                    row = db.execute("SELECT file_sha256, mtime FROM files WHERE path=?", (str(p),)).fetchone()
                    if row and abs(row[1]-st.st_mtime) < 0.001: n_skip+=1; continue
                    raw = p.read_bytes()
                    try: text = raw.decode("utf-8")
                    except UnicodeDecodeError:
                        if p.suffix.lower() not in TEXT_EXT: continue
                        text = raw.decode("utf-8", errors="replace")
                    fsha = hashlib.sha256(raw).hexdigest()
                    if row and row[0]==fsha: n_skip+=1; continue  # unchanged content
                    db.execute("INSERT OR REPLACE INTO files VALUES (?,?,?,?,?,?,?)",
                        (fsha, str(p), st.st_size, st.st_mtime, p.suffix, source,
                         time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
                    # re-chunk (fresh doc = fresh chunks; old ones replaced below)
                    db.execute("DELETE FROM chunks WHERE doc_sha256=? AND section_path LIKE 'f/%'",
                               (fsha,))
                    ordi = 0
                    for piece in re.split(r"(?<=[.!?])\s+|\n\n+", text):
                        piece = piece.strip()
                        if len(piece) < 20: continue
                        cur = db.cursor()
                        cur.execute("INSERT INTO chunks(doc_sha256,ordinal,section_path,text,"
                                    "char_start,char_end) VALUES (?,?,?,?,?,?)",
                                    (fsha, ordi, f"f/{p.name}", piece, 0, len(piece)))
                        db.execute("INSERT INTO chunks_fts(rowid,text,section_path) "
                                   "SELECT chunk_id,text,section_path FROM chunks WHERE chunk_id=?",
                                   (cur.lastrowid,))
                        ordi += 1
                        if ordi >= 60: break  # cap chunks/file: metadata-rich, not exhaustive
                    n_new += 1
                    maybe_commit()
                except Exception as e:
                    n_err += 1
        db.commit()
        print(f"[phase1] source={source} new={n_new} skip={n_skip} err={n_err}", flush=True)
    return n_new, n_skip, n_err

def dossier(word):
    db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=30)
    db.execute("PRAGMA busy_timeout=30000")
    cached = db.execute("SELECT dossier FROM dossiers WHERE word=?", (word,)).fetchone()
    if cached: db.close(); return cached[0]
    parts = []
    for r in db.execute("SELECT rowid, snippet(chunks_fts,0,'[',']','…',10) "
                        "FROM chunks_fts WHERE chunks_fts MATCH ? LIMIT 25", (word,)):
        parts.append(f"{r[1]}")
    # attach file metadata for top file-paths containing the word
    for r in db.execute("SELECT cf.rowid, f.path, f.size, datetime(f.mtime,'unixepoch'), f.source "
                        "FROM chunks_fts cf JOIN chunks c ON c.chunk_id=cf.rowid "
                        "JOIN files f ON f.file_sha256=c.doc_sha256 "
                        "WHERE cf MATCH ? GROUP BY f.path LIMIT 12", (word,)):
        parts.append(f"[file {r[1]} size={r[2]} mtime={r[3]} src={r[4]}]")
    d = "\n".join(parts)[:6000] if parts else "(no index hits)"
    wdb = sqlite3.connect(DB, timeout=120); wdb.execute("PRAGMA busy_timeout=120000")
    wdb.execute("INSERT OR REPLACE INTO dossiers VALUES (?,?,?,?)",
                (word, d, sha(word), time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
    wdb.commit(); wdb.close(); db.close()
    return d

def broken_files_report():
    db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=30)
    out = []
    for r in db.execute("SELECT path FROM files WHERE ext='.py' AND path LIKE '%openroot/bin%'"):
        p = r[0]
        try:
            compile(Path(p).read_text(), p, "exec")
        except SyntaxError as e:
            out.append((p, f"SyntaxError line {e.lineno}: {e.msg}"))
        except Exception as e:
            out.append((p, repr(e)))
    db.close(); return out

def ollama(prompt):
    req = urllib.request.Request(OLLAMA, data=json.dumps({
        "model": MODEL, "prompt": prompt, "stream": False,
        "options": {"temperature": 0.1, "num_ctx": 16384}}).encode(),
        headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def ask_coder(task, keywords):
    ctx = "\n".join(f"--- DOSSIER: {w} ---\n{dossier(w)}" for w in keywords)
    prompt = f"""You are OpenRoot's master engineer. Live keyword dossiers (sha256+mtime+
metadata-indexed corpus extracts) are provided. Use them; do NOT ask for more info.
Write ONE complete runnable Python script. No preamble, only a single ```python block.

TASK: {task}

DOSSIERS:
{ctx}"""
    res = ollama(prompt)
    ans = res.get("response","")
    m = re.search(r"```(?:python)?\s*(.*?)```", ans, re.S)
    return (m.group(1).strip() if m else ans.strip()), res

def main():
    LOG_DIR.mkdir(exist_ok=True, parents=True)
    DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB, timeout=120)
    db.execute("PRAGMA busy_timeout=120000"); db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=NORMAL"); db.execute("PRAGMA journal_size_limit=268435456")
    db.execute("PRAGMA wal_autocheckpoint=2000")
    schema(db); db.commit()

    print(f"[phase1][gate] roots={[str(p) for _,p in roots()]}", flush=True)
    n_new, n_skip, n_err = scan_and_ingest(db)
    stats = db.execute("SELECT (SELECT COUNT(*) FROM files),(SELECT COUNT(*) FROM chunks),"
                       "(SELECT COUNT(DISTINCT path) FROM files WHERE path LIKE '%openroot%')").fetchone()
    print(f"[phase1][banked] files={stats[0]} chunks={stats[1]} openroot-files={stats[2]}", flush=True)

    # Phase 2 demo dossier — proves instant resolution
    d = dossier("openroot")
    print(f"[phase2][banked] sample dossier 'openroot' len={len(d)} first-hit: {d[:100]}", flush=True)

    # Phase 3: broken files -> fix specs
    broken = broken_files_report()
    for p, err in broken:
        db.execute("INSERT INTO corrections(path,issue,fix,status,fixed_utc) VALUES (?,?,NULL,'open',NULL)",
                   (p, err))
    db.commit()
    print(f"[phase3][gate] broken-bin-py={len(broken)}", flush=True)

    tasks = [
        ("overhaul-openroot",
         "Write a comprehensive openroot OVERHAUL script: scans /home/jesse/openroot, "
         "deduplicates via sha256, prunes dead-path references from README/docs, enforces "
         "py_compile + bash -n gates on all bin/ scripts, reports a Merkle-rooted summary. "
         "Idempotent, safe (read-mostly, destructive ops behind CONFIRM=1).",
         ["openroot","overhaul","sha256","merkle","py_compile","idempotent"]),
        ("fix-broken-files",
         "Write a repair script that reads broken-file paths+errors from a JSON list and "
         "rewrites each file's minimal fix (syntax errors first), validating with py_compile, "
         f"backing up originals with timestamped .bak suffixes. Broken list: "
         f"{json.dumps(broken[:20])}",
         ["py_compile","repair","backup","validation"]),
        ("deliver-scripts",
         "Write a delivery script that collects all completed scripts from openroot/bin "
         "and openroot-ops, verifies each with py_compile/bash -n, computes sha256 per file, "
         "generates a manifest JSONL, and stages them into context_bridge/harvest/ for commit.",
         ["delivery","manifest","sha256","harvest","commit"]),
    ]
    for tid, task, kws in tasks:
        th = sha(tid)
        if db.execute("SELECT 1 FROM pathways WHERE task_sha256=?", (th,)).fetchone():
            print(f"[phase3][cache-hit] {tid}", flush=True); continue
        try:
            ans, res = ask_coder(task, kws)
            db.execute("INSERT OR REPLACE INTO pathways VALUES (?,?,?,?,?)",
                       (th, tid, ans, MODEL, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
            db.commit()
            print(f"[phase3][banked] {tid} ev={res.get('eval_count',0)} len={len(ans)}", flush=True)
        except Exception as e:
            print(f"[phase3][held] {tid}: {e!r}", flush=True)

    root = sha("|".join(sorted(r[0] for r in db.execute("SELECT task_sha256 FROM pathways"))))
    db.execute("INSERT INTO seals VALUES (NULL,'merkle',?,?)",
               (root, time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
    db.commit()
    print(f"SEAL {root[:16]}... [end] [banked] run complete", flush=True)

if __name__ == "__main__":
    main()
