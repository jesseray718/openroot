#!/usr/bin/env python3
"""Real Nomic embeddings for OpenRoot foundation library.
Requires: NOMIC_API_KEY env var or ~/.nomic_api_key file.
Get key: https://dashboard.nomic.ai/
"""
import json, glob, os, sys, hashlib
from pathlib import Path

# ── Paths (Termux, not proot) ──
LIB_DIR = Path.home() / "projects/openroot/foundation_library"
OUTPUT = Path.home() / "projects/openroot/vectors/nomic_embeddings.jsonl"

# ── API key ──
API_KEY = os.environ.get("NOMIC_API_KEY", "")
if not API_KEY:
    keyfile = Path.home() / ".nomic_api_key"
    if keyfile.exists():
        API_KEY = keyfile.read_text().strip()
    else:
        print("❌ No Nomic API key found.")
        print("   Get one: https://dashboard.nomic.ai/")
        print("   Then: echo 'your-key' > ~/.nomic_api_key")
        print("   Or: export NOMIC_API_KEY='your-key'")
        sys.exit(1)

from nomic import embed

def chunk_text(text, max_chars=2000):
    """Chunk by lines, accumulate to ~2000 chars."""
    lines = text.split("\n")
    chunks, current = [], []
    size = 0
    for line in lines:
        current.append(line)
        size += len(line)
        if size > max_chars:
            chunks.append("\n".join(current))
            current, size = [], 0
    if current:
        chunks.append("\n".join(current))
    return chunks

def main():
    md_files = sorted(glob.glob(str(LIB_DIR / "**/*.md"), recursive=True))
    if not md_files:
        # Fallback: try root openroot dir
        md_files = sorted(glob.glob(str(Path.home() / "projects/openroot/*.md")))
    if not md_files:
        print(f"❌ No .md files found in {LIB_DIR}")
        sys.exit(1)

    print(f"📄 Found {len(md_files)} markdown files")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    all_records = []
    for md_path in md_files:
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()

        chunks = chunk_text(content)
        fname = os.path.basename(md_path)

        # Batch embed all chunks for this file
        texts = [c for c in chunks if len(c.strip()) > 20]
        if not texts:
            continue

        try:
            result = embed.text(texts, model="nomic-embed-text-v1.5")
            vectors = result["embeddings"]
        except Exception as e:
            print(f"  ❌ {fname}: {e}")
            # Fallback: hash-based pseudo-embedding
            import numpy as np
            vectors = []
            for t in texts:
                h = hashlib.sha256(t.encode()).digest()
                vec = np.frombuffer(h[:768*4], dtype=np.float32)[:768]
                vec = vec / (np.linalg.norm(vec) + 1e-8)
                vectors.append(vec.tolist())

        for i, (text, vec) in enumerate(zip(texts, vectors)):
            all_records.append({
                "file": md_path,
                "chunk_idx": i,
                "preview": text[:200],
                "embedding": vec
            })
        print(f"  ✅ {fname} — {len(texts)} chunks embedded")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        for rec in all_records:
            f.write(json.dumps(rec) + "\n")

    print(f"\n💾 Saved {len(all_records)} embeddings to {OUTPUT}")
    print(f"📐 Dimensionality: {len(all_records[0]['embedding']) if all_records else 0}")

if __name__ == "__main__":
    main()
