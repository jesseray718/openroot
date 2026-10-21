#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# [EMBEDCACHEV1] Persistent vector cache for nomic-embed-text — canary marker
"""
embed_cache.py — sha-keyed embedding persistence for OpenRoot solve.py Tier 1.

Eliminates O(n) re-embedding per query: cache hit = zero Ollama calls, zero joules.
Schema (data/embed_cache.db, RUNTIME STATE — never git-add):
    embeddings(content_sha TEXT PRIMARY KEY, model TEXT, dim INTEGER,
               vec BLOB, created_at REAL, hit_count INTEGER)

Integration (solve.py Tier 1):
    from embed_cache import embed_cached
    vecs = embed_cached([t for t in corpus_texts])   # one HTTP call for misses only
CLI: embed_cache.py stats | smoke | warm <file.md>
"""
import hashlib, json, sqlite3, sys, time, os, array, urllib.request
from pathlib import Path

DB_PATH = "/home/jesse/openroot/data/embed_cache.db"
OLLAMA = "http://localhost:11434"
MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
CANARY = "[EMBEDCACHEV1]"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def conn() -> sqlite3.Connection:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.execute("""CREATE TABLE IF NOT EXISTS embeddings(
        content_sha TEXT PRIMARY KEY, model TEXT, dim INTEGER,
        vec BLOB, created_at REAL, hit_count INTEGER DEFAULT 0)""")
    return c


def _decode(blob: bytes) -> list:
    a = array.array("f")
    a.frombytes(blob)
    return a.tolist()


def _encode(vec: list) -> bytes:
    a = array.array("f", vec)
    return a.tobytes()


def _ollama_embed_batch(texts: list) -> list:
    """One HTTP call for all misses. Tries /api/embed (list), falls back per-item."""
    try:
        req = urllib.request.Request(
            f"{OLLAMA}/api/embed",
            data=json.dumps({"model": MODEL, "input": texts}).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            out = json.load(r)
        return [e["embedding"] for e in out["embeddings"]]
    except Exception:
        vecs = []
        for t in texts:
            req = urllib.request.Request(
                f"{OLLAMA}/api/embeddings",
                data=json.dumps({"model": MODEL, "prompt": t}).encode(),
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                vecs.append(json.load(r)["embedding"])
        return vecs


def embed_cached(texts: list, model: str = MODEL) -> list:
    """Return embeddings for texts. Hits: zero Ollama calls. Misses: one batch call."""
    now = time.time()
    out: dict[int, list] = {}
    shas = {i: sha(t) for i, t in enumerate(texts)}
    with conn() as db:
        # dedupe within-request + lookup
        seen_sha: dict[str, list] = {}
        miss_idx, miss_sha, miss_text = [], [], []
        for i, t in enumerate(texts):
            s = shas[i]
            if s in seen_sha:
                out[i] = seen_sha[s]
                continue
            row = db.execute(
                "SELECT vec FROM embeddings WHERE content_sha=? AND model=?",
                (s, model)).fetchone()
            if row:
                db.execute("UPDATE embeddings SET hit_count=hit_count+1 WHERE content_sha=?",
                           (s,))
                out[i] = _decode(row[0])
                seen_sha[s] = out[i]
            else:
                miss_idx.append(i); miss_sha.append(s); miss_text.append(t)
        db.commit()
    if miss_text:
        vecs = _ollama_embed_batch(miss_text)
        with conn() as db:
            for i, s, v in zip(miss_idx, miss_sha, vecs):
                db.execute("""INSERT OR REPLACE INTO embeddings
                    (content_sha, model, dim, vec, created_at, hit_count)
                    VALUES(?,?,?,?,?,0)""",
                    (s, model, len(v), _encode(v), now))
            db.commit()
            for i, v in zip(miss_idx, vecs):
                out[i] = v
                seen_sha[sha(texts[i])] = v
    return [out[i] for i in range(len(texts))]


def _stats():
    with conn() as db:
        n = db.execute("SELECT COUNT(*), SUM(hit_count) FROM embeddings").fetchone()
    print(f"{CANARY} cache entries={n[0] or 0} total_hits={n[1] or 0} db={DB_PATH}")


def _smoke():
    probes = ["openroot smoke test alpha", "openroot smoke test beta"]
    t0 = time.time()
    v1 = embed_cached(probes)            # misses -> embed
    t_miss = time.time() - t0
    t0 = time.time()
    v2 = embed_cached(probes)             # hits -> zero ollama calls
    t_hit = time.time() - t0
    assert len(v1[0]) == len(v2[0]) == len(v1[1]), "dim mismatch"
    assert abs(v1[0][0] - v2[0][0]) < 1e-6, "cached vector drift"
    print(f"{CANARY} SMOKE PASS dims={len(v1[0])} "
          f"miss_pass={t_miss:.2f}s hit_pass={t_hit:.3f}s "
          f"(speedup x{t_miss/max(t_hit,1e-9):.0f})")


def _warm(path: str):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    chunks = [text[i:i+1500] for i in range(0, min(len(text), 500_000), 1500)] or [text]
    t0 = time.time()
    embed_cached(chunks)
    print(f"{CANARY} WARM {path}: {len(chunks)} chunks in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if cmd == "stats":
        _stats()
    elif cmd == "smoke":
        _smoke()
    elif cmd == "warm" and len(sys.argv) > 2:
        _warm(sys.argv[2])
    else:
        print(f"usage: {cmd} <stats|smoke|warm <file>>"); sys.exit(2)
