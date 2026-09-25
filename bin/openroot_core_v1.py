#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""openroot_core_v1.py — hybrid FTS5+vector search, sha256 inventory,
tamper-evident hash-linked wisdom ledger (NOT proof-of-work), priority router.

Env: OPENROOT_CORE_HOME (default /home/jesse/openroot/data).
Subcommands: initdb | add-doc TITLE CONTENT | search QUERY [alpha] [topk] |
  inventory DIR | chain-append SHA256 PATH PROBLEM SOLUTION NODE METRIC |
  chain-verify | route | ingest-jsonl FILE
"""
import argparse, hashlib, json, math, os, struct, sys, time, urllib.request

HOME_DIR = os.environ.get("OPENROOT_CORE_HOME", "/home/jesse/openroot/data")
DB_PATH = os.path.join(HOME_DIR, "openroot_core.db")
CHAIN_PATH = os.path.join(HOME_DIR, "wisdom_chain.json")
INVENTORY_PATH = os.path.join(HOME_DIR, "inventory_hashes.jsonl")
OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"

# ---------- vector utils ----------
def pack_vec(vec): return struct.pack(f"{len(vec)}f", *vec)
def unpack_vec(blob):
    return list(struct.unpack(f"{len(blob)//4}f", blob)) if blob else None

def cos_sim(a, b):
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a)); nb = math.sqrt(sum(y*y for y in b))
    return dot/(na*nb) if na and nb else 0.0

def embed(text):
    req = urllib.request.Request(OLLAMA_URL,
        data=json.dumps({"model": EMBED_MODEL, "prompt": text}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())["embedding"]

# ---------- schema (FIX defect #1: FK enforced; full trigger set) ----------
def get_conn():
    os.makedirs(HOME_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON;")  # cascade now actually fires
    conn.execute("""CREATE TABLE IF NOT EXISTS docs(
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT,
        embedding BLOB)""")
    conn.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(
        title, content, content='docs', content_rowid='id')""")
    conn.executescript("""
    CREATE TRIGGER IF NOT EXISTS docs_ai AFTER INSERT ON docs BEGIN
      INSERT INTO docs_fts(rowid, title, content) VALUES(new.id, new.title, new.content);
    END;
    CREATE TRIGGER IF NOT EXISTS docs_au AFTER UPDATE ON docs BEGIN
      INSERT INTO docs_fts(docs_fts, rowid, title, content)
        VALUES('delete', old.id, old.title, old.content);
      INSERT INTO docs_fts(rowid, title, content) VALUES(new.id, new.title, new.content);
    END;
    CREATE TRIGGER IF NOT EXISTS docs_ad AFTER DELETE ON docs BEGIN
      INSERT INTO docs_fts(docs_fts, rowid, title, content)
        VALUES('delete', old.id, old.title, old.content);
    END;
    CREATE TABLE IF NOT EXISTS embeddings(
      doc_id INTEGER PRIMARY KEY,
      vector BLOB NOT NULL,
      FOREIGN KEY(doc_id) REFERENCES docs(id) ON DELETE CASCADE);
    """)
    conn.commit()
    return conn

def cmd_initdb(_args):
    conn = get_conn(); conn.close()
    print(f"[ORCV1][initdb] ready -> {DB_PATH}")

def cmd_add_doc(args):
    conn = get_conn()
    try:
        vec = embed(args.content)
        cur = conn.execute("INSERT INTO docs(title, content) VALUES(?,?)",
                           (args.title, args.content))
        conn.execute("INSERT INTO embeddings(doc_id, vector) VALUES(?,?)",
                     (cur.lastrowid, pack_vec(vec)))
        conn.commit()
        print(f"[ORCV1][banked] doc id={cur.lastrowid} '{args.title}' + embedding")
    finally:
        conn.close()

# ---------- hybrid search (FIX defect #2: full-vector scan, FTS boost) ----------
def cmd_search(args):
    alpha = args.alpha; topk = args.topk
    try:
        qvec = embed(args.query); have_vec = True
    except Exception as e:
        print(f"[ORCV1][warn] embed unavailable ({e}); keyword-only mode"); have_vec = False
    conn = get_conn(); cur = conn.cursor()

    fts_scores = {}
    try:
        cur.execute("SELECT rowid, rank FROM docs_fts WHERE docs_fts MATCH ? ORDER BY rank LIMIT 200;", (args.query,))
        for rid, rank in cur.fetchall():
            fts_scores[rid] = 1.0/(1.0 + abs(rank))   # BM25 neg-rank -> [0,1]
    except sqlite3.OperationalError:
        pass

    results = []
    cur.execute("SELECT d.id, d.title, d.content, e.vector FROM docs d LEFT JOIN embeddings e ON d.id=e.doc_id;")
    for did, title, content, blob in cur.fetchall():
        cs = cos_sim(qvec, unpack_vec(blob)) if (have_vec and blob) else 0.0
        fs = fts_scores.get(did, 0.0)
        score = (alpha*cs + (1-alpha)*fs) if have_vec else fs
        if score > 0:
            results.append({"id": did, "title": title, "score": round(score, 4),
                            "cosine": round(cs, 4), "fts": round(fs, 4)})
    conn.close()
    results.sort(key=lambda r: r["score"], reverse=True)
    print(json.dumps(results[:topk], indent=2))
    if not results: print("[ORCV1] no hits (empty index or zero overlap)")

# ---------- inventory (FIX defect #4: python-walk, newline-safe) ----------
def cmd_inventory(args):
    hashes = {}
    rows = []
    for root, dirs, files in os.walk(args.directory):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fn in files:
            p = os.path.join(root, fn)
            if "/.git/" in p or "/.venv/" in p or "/node_modules/" in p: continue
            h = hashlib.sha256(open(p, "rb").read()).hexdigest()
            st = os.stat(p)
            rows.append({"sha256": h, "file_path": p, "size_bytes": st.st_size,
                         "modified_epoch": int(st.st_mtime), "duplicate": None})
            hashes[h] = hashes.get(h, 0) + 1
    for r in rows:
        r["duplicate"] = hashes[r["sha256"]] > 1
    os.makedirs(HOME_DIR, exist_ok=True)
    with open(INVENTORY_PATH, "w") as f:
        for r in rows: f.write(json.dumps(r) + "\n")
    dupes = sum(1 for r in rows if r["duplicate"])
    print(f"[ORCV1][banked] {len(rows)} files hashed, {dupes} duplicate-slots -> {INVENTORY_PATH}")

# ---------- wisdom ledger (FIX defect #3: honest labeling — tamper-evident, not PoW) ----------
def _calc_hash(idx, prev, ts, payload):
    return hashlib.sha256(f"{idx}{prev}{ts}{json.dumps(payload, sort_keys=True)}".encode()).hexdigest()

def _load_chain():
    if os.path.exists(CHAIN_PATH):
        return json.load(open(CHAIN_PATH))
    return []

def _save_chain(chain):
    os.makedirs(HOME_DIR, exist_ok=True)
    json.dump(chain, open(CHAIN_PATH, "w"), indent=2)

def cmd_chain_append(args):
    chain = _load_chain()
    if not chain:
        ts = int(time.time())
        chain = [{"index": 0, "timestamp": ts, "previous_hash": "0", "payload":
            {"note": "genesis — fragmented knowledge, imbalanced distribution"},
            "hash": _calc_hash(0, "0", ts, {"note": "genesis — fragmented knowledge, imbalanced distribution"})}]
    last = chain[-1]; idx = last["index"] + 1; ts = int(time.time())
    payload = {"asset_sha256": args.sha256, "asset_path": args.path,
               "problem": args.problem, "solution": args.solution,
               "routing": {"target_node_id": args.node,
                           "starvation_metric": args.metric,
                           "distribution_status": "OPEN_ACCESS"}}
    blk = {"index": idx, "timestamp": ts, "previous_hash": last["hash"],
           "payload": payload, "hash": _calc_hash(idx, last["hash"], ts, payload)}
    chain.append(blk); _save_chain(chain)
    print(f"[ORCV1][banked] block #{idx} hash={blk['hash'][:12]} linked to {args.sha256[:12]}")

def cmd_chain_verify(_args):
    chain = _load_chain()
    for i in range(1, len(chain)):
        c, p = chain[i], chain[i-1]
        if c["previous_hash"] != p["hash"]:
            print(f"[FAIL] link broken at #{c['index']}"); return 1
        if c["hash"] != _calc_hash(c["index"], c["previous_hash"], c["timestamp"], c["payload"]):
            print(f"[FAIL] payload tampered at #{c['index']}"); return 1
    print(f"[ORCV1][GREEN] chain verified: {len(chain)} blocks, tamper-evident (hash-linked)")
    return 0

def cmd_route(_args):
    chain = _load_chain()
    ok = cmd_chain_verify(_args)
    if ok: return ok
    items = [{"block": b["index"], **b["payload"], **b["payload"].get("routing", {})}
             for b in chain[1:]]
    items.sort(key=lambda x: x.get("starvation_metric", 0), reverse=True)
    print("\n--- PRIORITY ROUTE (most-starved first) ---")
    for it in items:
        print(f"P[{it.get('starvation_metric', 0):.2f}] node={it.get('target_node_id')} "
              f"asset={it['asset_sha256'][:12]} problem='{it['problem'][:60]}'")
    return 0

# ---------- jsonl ingest (batch add-doc without network; embeddings optional) ----------
def cmd_ingest_jsonl(args):
    conn = get_conn(); n = 0
    for line in open(args.file):
        line = line.strip()
        if not line: continue
        rec = json.loads(line)
        conn.execute("INSERT INTO docs(title, content) VALUES(?,?)",
                     (rec.get("title", ""), rec.get("content", "")))
        n += 1
    conn.commit(); conn.close()
    print(f"[ORCV1][banked] ingested {n} docs (embeddings deferred: run 're-embed' task separately)")

def main():
    ap = argparse.ArgumentParser(prog="openroot_core_v1")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("initdb").set_defaults(fn=cmd_initdb)
    p = sub.add_parser("add-doc"); p.add_argument("title"); p.add_argument("content"); p.set_defaults(fn=cmd_add_doc)
    p = sub.add_parser("search"); p.add_argument("query"); p.add_argument("alpha", nargs="?", type=float, default=0.5)
    p.add_argument("topk", nargs="?", type=int, default=5); p.set_defaults(fn=cmd_search)
    p = sub.add_parser("inventory"); p.add_argument("directory"); p.set_defaults(fn=cmd_inventory)
    p = sub.add_parser("chain-append")
    for a, nm in [("sha256", "sha256"), ("path", "path"), ("problem", "problem"), ("solution", "solution"), ("node", "node")]:
        p.add_argument(a); p.set_defaults(**{})
    p.add_argument("metric", nargs="?", type=float, default=1.0); p.set_defaults(fn=cmd_chain_append)
    sub.add_parser("chain-verify").set_defaults(fn=cmd_chain_verify)
    sub.add_parser("route").set_defaults(fn=cmd_route)
    p = sub.add_parser("ingest-jsonl"); p.add_argument("file"); p.set_defaults(fn=cmd_ingest_jsonl)
    args = ap.parse_args()
    rc = args.fn(args)
    sys.exit(rc if isinstance(rc, int) else 0)

if __name__ == "__main__":
    import sqlite3  # imported late so --help works without DB touch
    main()
