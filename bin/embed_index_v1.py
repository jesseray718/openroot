#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""embed_index_v1.py — semantic repo index via nomic-embed-text.
Replaces the grep concept-sweep with vector search (ms, concept not substring).
Incremental: re-embeds a chunk only if content hash changed.
Usage: build+demo:    python3 embed_index_v1.py
      query later:   python3 embed_index_v1.py "newton chain"
Table data/embeddings.db: chunks(sha256 PK, path, chunk, embedding BLOB)
"""
import hashlib, json, math, os, sqlite3, sys
sys.path.insert(0, "/home/jesse/openroot/bin")
from lumo_lib import embed

ROOT = "/home/jesse/openroot"
DB = os.path.join(ROOT, "data", "embeddings.db")
SKIP_DIRS = {".git", "venv", "node_modules", "__pycache__", ".aider",
             "dist", "attic", "salvage", "build", "data"}
EXTS = (".md", ".json", ".jsonl", ".py", ".sh", ".txt")
CHUNK_CHARS = 1500

def iter_files():
    """Yield indexable file paths below the repository root."""
    for cur, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(EXTS):
                yield os.path.join(cur, f)

def chunk_text(text):
    """Return chunks formed while accumulating the input's lines."""
    paras, buf = [], ""
    for line in text.splitlines(keepends=True):
        buf += line
        if len(buf) >= CHUNK_CHARS:
            paras.append(buf[:CHUNK_CHARS]); buf = buf[CHUNK_CHARS:]
    if buf.strip():
        paras.append(buf)
    return paras

def sha(t):
    """Return the SHA-256 digest of text encoded as UTF-8 with replacement."""
    return hashlib.sha256(t.encode("utf-8", "replace")).hexdigest()

def build():
    """Embed previously unseen repository chunks and store them in the index."""
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS chunks (
        sha256 TEXT PRIMARY KEY, path TEXT, chunk TEXT, embedding BLOB)""")
    known = {r[0] for r in con.execute("SELECT sha256 FROM chunks")}
    embedded_total, new, skipped = 0, 0, 0
    for path in iter_files():
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            continue
        for chunk in chunk_text(text):
            ckey = sha(path + "\x00" + chunk)
            if ckey in known:
                skipped += 1; continue
            vec = embed(chunk)
            con.execute("INSERT OR REPLACE INTO chunks VALUES (?,?,?,?)",
                        (ckey, os.path.relpath(path, ROOT),
                         chunk[:400], json.dumps(vec).encode()))
            new += 1
            embedded_total += 1
            if new % 250 == 0:
                con.commit()   # v1.1: batch-commit so crashed runs resume, not restart
    con.commit(); con.close()
    print("[banked] embeddings.db: %d new, %d unchanged (skipped), "
          "%d total chunks" % (new, skipped, new + skipped))

def query(qtext, k=5):
    """Print the top indexed chunks ranked by cosine similarity to a query."""
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT path, chunk, embedding FROM chunks").fetchall()
    con.close()
    if not rows:
        print("[held] index empty — run build first"); return
    qv = embed(qtext)
    scored = []
    for path, chunk, blob in rows:
        cv = json.loads(bytes(blob))
        dot = sum(a*b for a, b in zip(qv, cv))
        na = math.sqrt(sum(a*a for a in qv)); nb = math.sqrt(sum(b*b for b in cv))
        if na and nb:
            scored.append((dot/(na*nb), path, chunk))
    scored.sort(reverse=True)
    print("[query] %r — top %d of %d chunks" % (qtext, k, len(rows)))
    for score, path, chunk in scored[:k]:
        print("  %.3f  %s :: %s" % (score, path, chunk[:110].replace("\n", " ")))

def main():
    """Run query mode, or build the index and execute demonstration queries."""
    if len(sys.argv) > 1:              # query mode — instant, no rebuild
        query(" ".join(sys.argv[1:])); return
    print("[stage-1] incremental embed of %s (exts: %s)" % (ROOT, ",".join(EXTS)))
    build()
    print("[stage-2] semantic search demo — replaces grep sweep")
    for concept in ("synergetics isotropic vector matrix",
                    "newton chain mechanics",
                    "agape nodes coordination cooperation",
                    "core atomic functions"):
        query(concept, k=3)
    print("[exit=0]")

if __name__ == "__main__":
    main()
# [exit=0]
