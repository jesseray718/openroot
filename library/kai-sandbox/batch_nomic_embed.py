#!/usr/bin/env python3
import json
import glob
from pathlib import Path
import sys
import numpy as np

# Target the correct openroot directory
md_files = sorted(glob.glob("/root/openroot/*.md"))
if not md_files:
    print("No markdown files found in /root/openroot/")
    sys.exit(1)

print(f"Found {len(md_files)} markdown files to embed")

# Mock embedding function
def mock_embed(text):
    return [float(x) for x in np.random.randn(768).astype(np.float32)]

output_path = Path.home() / f"nomic_embeddings_{Path.home().name}.jsonl"
records = []

for md_path in md_files:
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    embedding = mock_embed(content[:4096])
    
    records.append({
        "file": md_path,
        "preview": content[:200],
        "embedding": embedding
    })

# Save to JSONL
with open(output_path, "w", encoding="utf-8") as f:
    for rec in records:
        f.write(json.dumps(rec) + "\n")

print(f"Saved {len(records)} embeddings to {output_path}")
