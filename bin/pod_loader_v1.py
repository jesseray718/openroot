#!/usr/bin/env python3
"""OpenRoot Pod Loader v1 — dual-hash SQLite pod with FTS5 + nomic embeddings."""
import argparse, hashlib, json, os, re, sqlite3, struct, subprocess, sys, time
from pathlib import Path

REPO = Path(os.environ.get("OPENROOT_REPO", "/home/jesse/openroot"))
PODS_ROOT = REPO / "pods_garden"

def sha256_bytes(b): return hashlib.sha256(b).hexdigest()
def blake3_bytes(b):
    try:
        import blake3; return blake3.blake3(b).hexdigest()
    except ImportError:
        return hashlib.blake2b(b, digest_size=32).hexdigest()

def chunk_text(text, max_chars=800, overlap=80):
    paras = re.split(r'\n\s*\n', text)
    chunks, cur = [], ""
    for p in paras:
        if cur and len(cur) + len(p) + 2 > max_chars:
            chunks.append(cur.strip())
            cur = cur[-overlap:] + "\n\n" + p if overlap else p
        else:
            cur = cur + "\n\n" + p if cur else p
    if cur.strip(): chunks.append(cur.strip())
    return chunks

def init_db(pod_path):
    conn = sqlite3.connect(str(pod_path / "pod.db"))
    conn.executescript("""
        PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;
        PRAGMA cache_size=-64000; PRAGMA temp_store=MEMORY;
        CREATE TABLE IF NOT EXISTS documents (
            sha256 TEXT PRIMARY KEY, path TEXT, origin TEXT,
            size_bytes INTEGER, mtime TEXT, ingested_at TEXT, metadata_json TEXT);
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_blake3 TEXT PRIMARY KEY, doc_sha256 TEXT, chunk_index INTEGER,
            text TEXT, char_count INTEGER, token_estimate INTEGER);
        CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks(doc_sha256);
        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
            chunk_blake3 UNINDEXED, doc_sha256 UNINDEXED, text,
            tokenize='porter unicode61');
        CREATE TABLE IF NOT EXISTS vectors (
            chunk_blake3 TEXT PRIMARY KEY, model TEXT, dim INTEGER,
            embedding BLOB, embedded_at TEXT);
        CREATE TABLE IF NOT EXISTS pod_meta (key TEXT PRIMARY KEY, value TEXT);
    """)
    return conn

def ingest_file(conn, file_path, origin, metadata):
    p = Path(file_path)
    if not p.is_file(): return None
    content = p.read_bytes()
    file_sha = sha256_bytes(content)
    if conn.execute("SELECT 1 FROM documents WHERE sha256=?", (file_sha,)).fetchone():
        return file_sha
    text = content.decode("utf-8", errors="replace")
    chunks = chunk_text(text)
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    mtime = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(p.stat().st_mtime))
    conn.execute("INSERT INTO documents VALUES (?,?,?,?,?,?,?)",
        (file_sha, str(p), origin, len(content), mtime, now, json.dumps(metadata)))
    for i, ch in enumerate(chunks):
        h = blake3_bytes(ch.encode("utf-8"))
        conn.execute("INSERT OR IGNORE INTO chunks VALUES (?,?,?,?,?,?)",
            (h, file_sha, i, ch, len(ch), len(ch)//4))
        conn.execute("INSERT INTO chunks_fts VALUES (?,?,?)", (h, file_sha, ch))
    return file_sha

def embed_chunks(conn, model="nomic-embed-text"):
    cur = conn.execute("""SELECT c.chunk_blake3, c.text FROM chunks c
        LEFT JOIN vectors v ON c.chunk_blake3 = v.chunk_blake3
        WHERE v.chunk_blake3 IS NULL""")
    pending = cur.fetchall()
    ok = 0
    for ch_hash, text in pending:
        try:
            r = subprocess.run(["ollama","embed",model,text[:2000]],
                capture_output=True, text=True, timeout=30)
            if r.returncode != 0: continue
            vec = json.loads(r.stdout).get("embedding", [])
            if not vec: continue
            blob = struct.pack(f"{len(vec)}f", *vec)
            conn.execute("INSERT OR REPLACE INTO vectors VALUES (?,?,?,?,?)",
                (ch_hash, model, len(vec), blob,
                 time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
            ok += 1
        except Exception as e:
            print(f"  [held] embed fail: {e}", file=sys.stderr)
    conn.commit()
    return ok

def query_pod(conn, query, top_k=18, char_budget=8000):
    safe = '"' + query.replace('"','""') + '"'
    sql = """SELECT c.chunk_blake3, c.doc_sha256, c.text, c.char_count,
               bm25(chunks_fts) score, d.path
             FROM chunks_fts JOIN chunks c ON chunks_fts.chunk_blake3 = c.chunk_blake3
             JOIN documents d ON c.doc_sha256 = d.sha256
             WHERE chunks_fts MATCH ? ORDER BY score LIMIT ?"""
    cur = conn.execute(sql, (safe, top_k*2))
    res, total = [], 0
    for ch, ds, text, cc, score, path in cur.fetchall():
        if total + cc > char_budget: break
        res.append({"chunk_blake3":ch, "doc_sha256":ds, "doc_path":path,
                    "text":text, "char_count":cc, "bm25_score":-score})
        total += cc
    return {"query":query, "chunks_returned":len(res),
            "total_chars":total, "dossier":res}

def seal_pod(conn, pod_name):
    cur = conn.execute("SELECT chunk_blake3 FROM chunks ORDER BY chunk_blake3")
    hashes = [r[0] for r in cur.fetchall()]
    if not hashes: return None, 0
    level = hashes[:]
    while len(level) > 1:
        if len(level) % 2: level.append(level[-1])
        level = [hashlib.sha256((level[i]+level[i+1]).encode()).hexdigest()
                 for i in range(0, len(level), 2)]
    root = level[0]
    conn.execute("INSERT OR REPLACE INTO pod_meta VALUES ('merkle_root', ?)", (root,))
    conn.execute("INSERT OR REPLACE INTO pod_meta VALUES ('sealed_at', ?)",
                 (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),))
    conn.execute("INSERT OR REPLACE INTO pod_meta VALUES ('chunk_count', ?)", (str(len(hashes)),))
    conn.execute("INSERT OR REPLACE INTO pod_meta VALUES ('pod_name', ?)", (pod_name,))
    conn.commit()
    return root, len(hashes)

def manifest(pod_path, pod_name):
    conn = sqlite3.connect(str(pod_path / "pod.db"))
    meta = dict(conn.execute("SELECT key, value FROM pod_meta").fetchall())
    dc = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    cc = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    vc = conn.execute("SELECT COUNT(*) FROM vectors").fetchone()[0]
    conn.close()
    return {"pod_name":pod_name, "schema_version":1, "doc_count":dc,
            "chunk_count":cc, "vector_count":vc,
            "merkle_root":meta.get("merkle_root"), "sealed_at":meta.get("sealed_at")}

def main():
    p = argparse.ArgumentParser(description="OpenRoot Pod Loader v1")
    s = p.add_subparsers(dest="cmd", required=True)
    pi = s.add_parser("ingest"); pi.add_argument("pod"); pi.add_argument("path")
    pi.add_argument("--meta", action="append", default=[])
    pq = s.add_parser("query"); pq.add_argument("pod"); pq.add_argument("query")
    pq.add_argument("--top-k", type=int, default=18); pq.add_argument("--budget", type=int, default=8000)
    ps = s.add_parser("seal"); ps.add_argument("pod")
    pm = s.add_parser("manifest"); pm.add_argument("pod")
    pe = s.add_parser("embed"); pe.add_argument("pod"); pe.add_argument("--model", default="nomic-embed-text")
    s.add_parser("list")
    args = p.parse_args()
    print(f"[gate] CANARY:OPENROOT-POD-LOADER-V1 {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}", file=sys.stderr)
    if args.cmd == "ingest":
        pod_path = PODS_ROOT / args.pod; pod_path.mkdir(parents=True, exist_ok=True)
        conn = init_db(pod_path)
        metadata = {}
        for m in args.meta:
            if "=" in m:
                k,v = m.split("=",1); metadata[k]=v
        target = Path(args.path)
        if target.is_file(): files = [target]
        elif target.is_dir():
            files = [f for f in target.rglob("*") if f.is_file()
                     and f.suffix in (".md",".txt",".json",".markdown",".py",".sh")]
        else: print(f"[held] not found: {target}"); sys.exit(1)
        n = 0
        for f in files:
            try:
                sha = ingest_file(conn, f, str(target), metadata)
                if sha: n += 1; print(f"  [banked] {f.name} -> {sha[:16]}...")
            except Exception as e:
                print(f"  [held] {f}: {e}")
        conn.commit(); conn.close()
        print(f"[banked] ingested {n}/{len(files)} into pod '{args.pod}'")
    elif args.cmd == "embed":
        pod_path = PODS_ROOT / args.pod
        if not pod_path.exists(): print(f"[held] no pod: {args.pod}"); sys.exit(1)
        conn = sqlite3.connect(str(pod_path / "pod.db"))
        n = embed_chunks(conn, args.model); conn.commit(); conn.close()
        print(f"[banked] embedded {n} chunks with {args.model}")
    elif args.cmd == "query":
        pod_path = PODS_ROOT / args.pod
        if not pod_path.exists(): print(f"[held] no pod: {args.pod}"); sys.exit(1)
        conn = sqlite3.connect(str(pod_path / "pod.db"))
        r = query_pod(conn, args.query, args.top_k, args.budget); conn.close()
        print(json.dumps(r, indent=2, ensure_ascii=False))
    elif args.cmd == "seal":
        pod_path = PODS_ROOT / args.pod
        if not pod_path.exists(): print(f"[held] no pod: {args.pod}"); sys.exit(1)
        conn = sqlite3.connect(str(pod_path / "pod.db"))
        root, count = seal_pod(conn, args.pod); conn.commit(); conn.close()
        print(f"[banked] pod '{args.pod}' sealed")
        print(f"  merkle_root: {root}")
        print(f"  chunk_count: {count}")
    elif args.cmd == "manifest":
        pod_path = PODS_ROOT / args.pod
        if not pod_path.exists(): print(f"[held] no pod: {args.pod}"); sys.exit(1)
        print(json.dumps(manifest(pod_path, args.pod), indent=2))
    elif args.cmd == "list":
        if not PODS_ROOT.exists(): print("[]"); return
        pods = [manifest(d, d.name) for d in sorted(PODS_ROOT.iterdir())
                if d.is_dir() and (d / "pod.db").exists()]
        print(json.dumps(pods, indent=2))

if __name__ == "__main__":
    main()
