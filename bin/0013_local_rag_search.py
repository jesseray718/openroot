import json
import subprocess
import sys
import glob
from pathlib import Path

print("=== GROK-NODE optimized vector search (pre-normalized pure Python) ===")
print("Nodes: Local AI + OpenRoot docs + AeroCement H-003/PoPW/UNE")
print("Opt: Pre-normalize embeddings once at load → fast dot-product cosine")
print("Further options for later: FAISS, Annoy, sqlite-vec, float16 quantization, .npz index")

jsonl_files = sorted(glob.glob(str(Path.home() / "nomic_embeddings_*.jsonl")))
if not jsonl_files:
    print("No jsonl found. Run batch embed first.")
    sys.exit(1)

latest = jsonl_files[-1]
print(f"Using: {latest}")

records = []
with open(latest, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            records.append(json.loads(line))

print(f"Loaded {len(records)} vectors")

if len(records) == 0:
    print("jsonl is empty.")
    print("Fix: Make sure you run 'ollama serve' + python scripts in the SAME context")
    print("(either both in main Termux, or both inside kai9000 Linux sandbox).")
    print("Then re-run: python3 $HOME/batch_nomic_embed.py")
    sys.exit(0)

# Pre-normalize once for fast cosine = dot product
norms = []
for r in records:
    vec = r["embedding"]
    n = sum(x*x for x in vec)**0.5 + 1e-12
    norms.append(n)

def get_query_embedding(query):
    payload = {"model": "nomic-embed-text", "input": query}
    proc = subprocess.run(
        ["curl", "-s", "http://localhost:11434/api/embed",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=60
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        print("Embed failed. Start ollama serve in the correct environment (kai9000 sandbox or Termux).")
        sys.exit(1)
    data = json.loads(proc.stdout)
    return data.get("embeddings", [[]])[0]

if len(sys.argv) > 1:
    query = " ".join(sys.argv[1:])
else:
    query = "H-003 thermal cascade efficiency Stirling PoPW volumetric aerocement"

print(f"Query: {query}")
qemb = get_query_embedding(query)

qn = sum(x*x for x in qemb)**0.5 + 1e-12

scored = []
for i, r in enumerate(records):
    vec = r["embedding"]
    n = norms[i]
    dot = sum(a*b for a,b in zip(vec, qemb))
    scored.append((dot / (n * qn), r["file"], r["preview"]))

scored.sort(reverse=True)

print("\nTop matches:")
for rank, (score, fname, preview) in enumerate(scored[:5], 1):
    print(f"{rank}. {fname} (sim: {score:.4f})")
    print(f"   {preview[:220]}...")
    print()

print("=== Vector search ready (optimized). Later: pip install numpy for big speedup ===")
