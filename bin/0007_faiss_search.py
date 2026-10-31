import json
import glob
import sys
from pathlib import Path

print("=== GROK-NODE: FAISS index types + practical implementation ===")
print("Nodes: Local AI Infrastructure + OpenRoot docs + AeroCement thermal/PoPW/UNE")
print("Goal: Learn FAISS index types + build a fast local index from your nomic jsonl")

# ===================== FAISS INDEX TYPES EXPLAINED =====================
# 1. IndexFlat (exact search)
#    - IndexFlatIP : Inner Product (best when vectors are L2-normalized → cosine similarity)
#    - IndexFlatL2 : Euclidean distance
#    - Pros: 100% accurate, no training, simple. 
#    - Cons: O(N) scan → slow when you have >50k–100k vectors.
#    - Best starting point for your phone right now (openroot has a few hundred .md files).

# 2. IndexHNSW (Hierarchical Navigable Small World) - graph-based ANN
#    - IndexHNSWFlat, IndexHNSWPQ, etc.
#    - Pros: Excellent speed/recall tradeoff, no training needed, very good for local use.
#    - Cons: Higher memory than Flat, build time longer.
#    - Great next step when your collection grows.

# 3. IndexIVF (Inverted File) + clustering
#    - IndexIVFFlat, IndexIVFPQ (Product Quantization)
#    - Needs training (kmeans on a subset of vectors).
#    - Pros: Very fast for large N, can combine with PQ for compression.
#    - Cons: Approximate, needs training step, more complex parameters (nlist, nprobe).

# 4. Product Quantization (PQ) variants
#    - IndexPQ, IndexIVFPQ, IndexHNSWPQ
#    - Compresses vectors (very important on phone RAM).
#    - Trade accuracy for much lower memory footprint.

# 5. Scalar Quantizer
#    - IndexScalarQuantizer (float16 or int8)
#    - Simple compression, low overhead.

# Recommendation for your A15 + nomic 768-dim embeddings:
#   Start with IndexFlatIP (exact + simple)
#   Move to IndexHNSWFlat when you have thousands of vectors or want sub-10ms queries.
#   Use PQ/quantization only if memory becomes a problem.

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    print("faiss not installed. Run: pip install faiss-cpu")
    print("Then re-run this script. Falling back to numpy version (slower but works).")

jsonl_files = sorted(glob.glob(str(Path.home() / "nomic_embeddings_*.jsonl")))
if not jsonl_files:
    print("No jsonl found. Run batch embed first (after fixing Ollama context).")
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
    print("jsonl empty. Fix Ollama reachability (same shell/context as kai9000 sandbox) then re-run batch.")
    sys.exit(0)

# Prepare data
import numpy as np
embeddings = np.array([r["embedding"] for r in records], dtype=np.float32)
# Normalize for IP = cosine
faiss.normalize_L2(embeddings)

if HAS_FAISS:
    print("\nBuilding FAISS IndexFlatIP (exact, recommended starting point)...")
    index = faiss.IndexFlatIP(embeddings.shape[1])   # 768
    index.add(embeddings)

    # Optional: switch to HNSW for speed later
    # index = faiss.IndexHNSWFlat(embeddings.shape[1], 32)  # 32 = efConstruction
    # index.add(embeddings)

    print(f"Index built with {index.ntotal} vectors")

    # Save for reuse
    index_path = str(Path.home() / "openroot_faiss.index")
    faiss.write_index(index, index_path)
    print(f"Saved to: {index_path}")

    def search(query_emb, k=5):
        q = np.array([query_emb], dtype=np.float32)
        faiss.normalize_L2(q)
        D, I = index.search(q, k)
        return list(zip(D[0], I[0]))

else:
    # Fallback to numpy (from previous optimized script)
    print("Using numpy fallback...")
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-12
    embs = embeddings / norms
    def search(query_emb, k=5):
        q = np.array(query_emb, dtype=np.float32)
        q = q / (np.linalg.norm(q) + 1e-12)
        sims = embs @ q
        top_idx = np.argsort(sims)[-k:][::-1]
        return [(float(sims[i]), int(i)) for i in top_idx]

# Demo search
def get_query_embedding(query):
    payload = {"model": "nomic-embed-text", "input": query}
    proc = subprocess.run(
        ["curl", "-s", "http://localhost:11434/api/embed",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=60
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        print("Embed failed. Fix Ollama context first.")
        sys.exit(1)
    data = json.loads(proc.stdout)
    return data["embeddings"][0]

query = "H-003 thermal cascade efficiency Stirling PoPW volumetric aerocement"
print(f"\nQuery: {query}")
qemb = get_query_embedding(query)

results = search(qemb, k=5)

print("\nTop matches:")
for rank, (score, idx) in enumerate(results, 1):
    rec = records[idx]
    print(f"{rank}. {rec['file']} (sim: {score:.4f})")
    print(f"   {rec['preview'][:200]}...")
    print()

print("=== FAISS learning complete. Index saved. Ready for production RAG on phone. ===")
print("Next steps: pip install faiss-cpu  →  switch to IndexHNSWFlat for speed  →  add to kai9000 workflow")
