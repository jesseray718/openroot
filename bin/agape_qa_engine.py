#!/usr/bin/env python3
# agape_qa_engine.py — SQLite + FTS5 + nomic-embed RAG Q&A over the OpenRoot corpus
# Jesse Ray / OpenRoot v1.0 | DB does retrieval (microseconds), model reads only top-K chunks
# Commands: embed | stats | ask "question" | chat | templates
import os, sys, json, glob, sqlite3, struct, math, re, time, urllib.request

OLLAMA    = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
EMBED_MDL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
CHAT_MDL  = os.environ.get("QA_MODEL", "qwen2.5-coder:7b")
TOP_K     = int(os.environ.get("TOP_K", "5"))
OUT       = "/home/jesse/openroot/data/universal_index"
RAG_DB    = os.path.join(OUT, "agape_rag.db")
TEXT_EXT  = {".py", ".md", ".txt", ".sh", ".json", ".rs", ".csv", ".tsv", ".yaml", ".yml", ".toml"}
MAX_FILE  = 300_000      # bytes — skip monsters, they are build artifacts anyway
CHUNK_SZ  = 1200         # chars per embedding chunk
LIVE_ROOTS = ["/home/jesse/openroot", "/home/jesse/src/openroot"]

def canary(): print("[canary] paste intact | engine armed |", CHAT_MDL)

def http(path, payload, timeout=120):
    req = urllib.request.Request(
        OLLAMA + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def embed(text):
    out = http("/api/embeddings",
               {"model": EMBED_MDL, "prompt": text[:8000], "keep_alive": "30m"})
    return out.get("embedding") or []

def gen(prompt):
    out = http("/api/generate",
               {"model": CHAT_MDL, "prompt": prompt, "stream": False,
                "keep_alive": "30m",
                "options": {"temperature": 0.1, "num_ctx": 8192}},
               timeout=int(os.environ.get("TIMEOUT", "600")))
    return out.get("response", "")

def vec_blob(v): return struct.pack("<%df" % len(v), *v)
def vec_load(b): return list(struct.unpack("<%df" % (len(b)//4), b))
def cos(a, b):
    d = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a)); nb = math.sqrt(sum(x*x for x in b))
    return d/(na*nb) if na and nb else 0.0

def connect():
    os.makedirs(OUT, exist_ok=True)
    con = sqlite3.connect(RAG_DB)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS chunks ("
                "id INTEGER PRIMARY KEY, path TEXT, chunk_idx INT,"
                "text TEXT, embedding BLOB)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_path ON chunks(path)")
    try:
        cur.execute("CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(path, text)")
    except Exception:
        pass
    con.commit()
    return con, cur

def source_files(cur):
    """Prefer the universal index files table; fall back to live tree walk."""
    rows = []
    idx_dbs = sorted(glob.glob(os.path.join(OUT, "universal_index_*.db")))
    if idx_dbs:
        try:
            ic = sqlite3.connect(idx_dbs[-1])
            rows = [r[0] for r in ic.execute(
                "SELECT extracted_to FROM files WHERE size_bytes < ? "
                "AND (filename LIKE '%.py' OR filename LIKE '%.md' "
                "OR filename LIKE '%.sh' OR filename LIKE '%.txt' "
                "OR filename LIKE '%.json' OR filename LIKE '%.rs' "
                "OR filename LIKE '%.yaml' OR filename LIKE '%.csv') "
                "ORDER BY size_bytes DESC", (MAX_FILE,))]
            ic.close()
            if rows:
                print(f"[source] universal index: {len(rows)} candidate files")
                return rows
        except Exception as e:
            print(f"[hold] index db unreadable: {e}")
    for root in LIVE_ROOTS:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in
                          (".git", "__pycache__", "node_modules", "build")]
            for fn in filenames:
                p = os.path.join(dirpath, fn)
                try:
                    if os.path.getsize(p) < MAX_FILE and \
                       os.path.splitext(fn)[1] in TEXT_EXT:
                        rows.append(p)
                except OSError:
                    pass
    print(f"[source] live tree fallback: {len(rows)} candidate files")
    return rows

def chunk_text(t):
    t = t.strip()
    while t:
        yield t[:CHUNK_SZ]
        t = t[CHUNK_SZ:].lstrip()

def cmd_embed(cur, con):
    files = source_files(cur)
    done_paths = {r[0] for r in cur.execute("SELECT DISTINCT path FROM chunks")}
    todo = [p for p in files if p not in done_paths]
    print(f"[observe] embedded already: {len(done_paths)} | to embed: {len(todo)}")
    t0 = time.time(); n = 0
    for p in todo:
        try:
            text = open(p, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for i, ch in enumerate(chunk_text(text)):
            try:
                v = embed(ch)
            except Exception as e:
                print(f"[hold] embed down ({e}) — stop, resume later"); return
            if not v:
                continue
            cur.execute("INSERT INTO chunks (path, chunk_idx, text, embedding) "
                        "VALUES (?,?,?,?)", (p, i, ch, vec_blob(v)))
            try:
                cur.execute("INSERT INTO chunks_fts (path, text) VALUES (?,?)", (p, ch))
            except Exception:
                pass
            n += 1
        con.commit()
        if n and n % 25 == 0:
            r = n / max(time.time()-t0, 1)
            print(f"[embed] chunks={n} rate={r:.1f}/s elapsed={int(time.time()-t0)}s")
    print(f"[banked] {n} new chunks embedded -> {RAG_DB}")

def cmd_stats(cur):
    total = cur.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    paths = cur.execute("SELECT COUNT(DISTINCT path) FROM chunks").fetchone()[0]
    print(f"[stats] chunks={total} files={paths} db={RAG_DB}")

def fts_hits(cur, q):
    terms = [w for w in re.findall(r"[A-Za-z_]{3,}", q)][:8]
    if not terms:
        return []
    match = " OR ".join(terms)
    try:
        return [r[0] for r in cur.execute(
            "SELECT path FROM chunks_fts WHERE chunks_fts MATCH ? "
            "LIMIT 200", (match,))]
    except Exception:
        like = "%" + terms[0] + "%"
        return [r[0] for r in cur.execute(
            "SELECT DISTINCT path FROM chunks WHERE text LIKE ? LIMIT 200", (like,))]

def retrieve(cur, q):
    qv = embed(q)
    if not qv:
        print("[hold] embedder down — keyword-only retrieval")
        return fts_hits(cur, q)[:TOP_K], []
    kw_paths = set(fts_hits(cur, q))
    rows = cur.execute("SELECT id, path, text, embedding FROM chunks").fetchall()
    scored = sorted(((cos(qv, vec_load(r[3])), r) for r in rows),
                    key=lambda x: -x[0])
    sem = [(s, r[1], r[2]) for s, r in scored[:TOP_K]]
    kwp = [p for p in kw_paths if p not in {s[1] for s in sem}][:2]
    return sem, kwp

def route_template(con, q):
    cur = con.cursor()
    for tid, title, pat, tmpl in cur.execute(
            "SELECT template_id, title, question_pattern, template_prompt "
            "FROM qa_templates"):
        if re.search(pat, q, re.I):
            return tid, title, tmpl
    return None, "freeform", ("Answer this OpenRoot question precisely: " + q +
                              "\nContext:\n{context}\nUse ONLY the context if "
                              "it suffices; say when it does not.")

def build_prompt(tmpl, q, sem, kwp, history):
    ctx = []
    for i, (s, path, text) in enumerate(sem):
        ctx.append(f"[{i}] {path} (sim {s:.3f}) ::\n{text[:700]}")
    for path in kwp:
        row = None
        cur = connect()[1]
        row = cur.execute("SELECT text FROM chunks WHERE path=? "
                          "LIMIT 1", (path,)).fetchone()
        if row:
            ctx.append(f"[kw] {path} ::\n{row[0][:700]}")
    if not ctx:
        ctx = ["(no local context found — answer from general knowledge and say so)"]
    hist = "\n".join(f"Q: {h[0]}\nA: {h[1][:500]}" for h in history[-3:])
    prompt = (f"Conversation so far:\n{hist or '(new session)'}\n\n"
              f"Task template:\n{tmpl}\n\nLocal context (retrieved):\n" +
              "\n\n".join(ctx) +
              f"\n\nUser question: {q}\n"
              "Answer with specifics (paths, functions, numbers) from context.")
    return prompt

def answer(con, q, history):
    sem, kwp = retrieve(con.cursor(), q)
    tid, title, tmpl = route_template(con, q)
    print(f"[route] template={tid} ({title}) | semantic hits={len(sem)} keyword extras={len(kwp)}")
    for s, p, _ in sem:
        print(f"  [hit] {s:.3f} {p}")
    prompt = build_prompt(tmpl, q, sem, kwp, history)
    print("[send] ->", CHAT_MDL)
    resp = gen(prompt)
    print("\n" + resp + "\n")
    history.append((q, resp))
    return resp

def main():
    canary()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    con, _ = connect()
    if cmd == "embed":   cmd_embed(con.cursor(), con)
    elif cmd == "stats": cmd_stats(con.cursor())
    elif cmd == "templates":
        for t in con.cursor().execute("SELECT template_id, title FROM qa_templates"):
            print(f"  {t[0]:15s} {t[1]}")
    elif cmd == "ask":
        if len(sys.argv) < 3: sys.exit("usage: ask \"question\"")
        answer(con, " ".join(sys.argv[2:]), [])
    elif cmd == "chat":
        hist = []
        print("[chat] rounds of Q&A — empty line exits")
        while True:
            try:
                q = input("you> ").strip()
            except EOFError:
                break
            if not q: break
            answer(con, q, hist)
        print("[chat] session closed |", len(hist), "rounds")
    else:
        sys.exit("commands: embed | stats | templates | ask \"q\" | chat")

if __name__ == "__main__":
    main()
