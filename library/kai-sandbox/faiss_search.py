#!/usr/bin/env python3
import json
import glob
from pathlib import Path
import sys
import numpy as np

# Load the latest embeddings
jsonl_files = sorted(glob.glob(str(Path.home() / "nomic_embeddings_*.jsonl")))
if not jsonl_files:
    print("No jsonl found. Run batch embed first.")
    sys.exit(1)

latest = jsonl_files[-1]
print(f"Loading embeddings from: {latest}")

records = []
with open(latest, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            records.append(json.loads(line))

print(f"Loaded {len(records)} vectors (768 dim)")

if len(records) == 0:
    print("jsonl empty. Fix embedding pipeline first.")
    sys.exit(0)

# Prepare data
embeddings = np.array([r["embedding"] for r in records], dtype=np.float32)
norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-12
embs = embeddings / norms

def search(query_emb, k=5):
    q = np.array(query_emb, dtype=np.float32)
    q = q / (np.linalg.norm(q) + 1e-12)
    sims = embs @ q
    top_idx = np.argsort(sims)[-k:][::-1]
    return [(float(sims[i]), int(i)) for i in top_idx]

# Mock query embedding
def get_query_embedding(query):
    return [float(x) for x in np.random.randn(768).astype(np.float32)]

query = sys.argv[1] if len(sys.argv) > 1 else "H-003 thermal cascade efficiency Stirling PoPW"
print(f"\nQuery: {query}")
qemb = get_query_embedding(query)

results = search(qemb, k=5)

print("\nTop matches:")
for rank, (score, idx) in enumerate(results, 1):
    rec = records[idx]
    print(f"{rank}. {rec['file']} (sim: {score:.4f})")
    print(f"   {rec['preview'][:200]}...")
    print()
