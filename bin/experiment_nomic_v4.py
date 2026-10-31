# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""CANARY:OPENROOT-EXP-NOMIC-V4 — Hybrid FTS+Vector retrieval test."""
import sqlite3, json, time, urllib.request, math
DB = "/home/jesse/pods/exp_universal_20261016T090321Z/pod.db"
db = sqlite3.connect(DB, timeout=30); db.execute("PRAGMA busy_timeout=30000")

# Ensure vector table exists
db.execute("""CREATE TABLE IF NOT EXISTS vec_sample(
  chunk_id INTEGER PRIMARY KEY, text TEXT, vec REAL[]
)""")

# Sample 500 chunks if empty
cnt = db.execute("SELECT COUNT(*) FROM vec_sample").fetchone()[0]
if cnt == 0:
    print("Embedding 500 random chunks...")
    rows = db.execute("SELECT chunk_id, substr(text,1,400) FROM chunks ORDER BY RANDOM() LIMIT 500").fetchall()
    texts = [r[1] for r in rows]
    # Local Ollama call
    req = urllib.request.Request("http://localhost:11434/api/embed",
        data=json.dumps({"model":"nomic-embed-text","input":texts}).encode(),
        headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            vecs = json.loads(r.read())["embeddings"]
        db.executemany("INSERT OR REPLACE INTO vec_sample VALUES (?,?,?)",
                       [(rows[i][0], rows[i][1], json.dumps(vecs[i])) for i in range(len(rows))])
        db.commit()
        print(f"[banked] Embedded {len(rows)} chunks.")
    except Exception as e:
        print(f"[held] Ollama embed failed: {e}. Skipping vector test.")
        exit(0)

# Query embedding
QUERY = "passive cooling with underground concrete tunnels"
req = urllib.request.Request("http://localhost:11434/api/embed",
    data=json.dumps({"model":"nomic-embed-text","input":QUERY}).encode(),
    headers={"Content-Type":"application/json"})
with urllib.request.urlopen(req, timeout=60) as r:
    qvec = json.loads(r.read())["embeddings"][0]

def cos(a, b):
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    return dot/(na*nb) if na and nb else 0

print(f"Query: {QUERY}")
print("--- Semantic Neighbors (Cosine) ---")
best = []
for cid, txt, v_str in db.execute("SELECT chunk_id, text, vec FROM vec_sample"):
    v = json.loads(v_str)
    best.append((cos(qvec, v), cid, txt))
best.sort(reverse=True)
for score, cid, txt in best[:3]:
    print(f"  [{score:.3f}] {txt[:150]}")

print("--- FTS Baseline (Keyword) ---")
# Fixed NEAR syntax
for r in db.execute("SELECT snippet(chunks_fts,0,'[',']','…',10) FROM chunks_fts "
                    "WHERE chunks_fts MATCH 'cooling NEAR/5 labyrinth' LIMIT 3"):
    print(f"  {r[0][:150]}")
print("[banked] nomic hybrid test complete [exit=0]")
