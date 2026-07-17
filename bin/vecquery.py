#!/usr/bin/env python3
"""Semantic search over OpenRoot embeddings."""
import json, sys, os, math
from pathlib import Path
import urllib.request

SERVER = "http://127.0.0.1:9998"
DB = Path("/data/data/com.termux/files/home/projects/openroot/vectors/nomic_embeddings.jsonl")

def embed_query(text):
    data = json.dumps({"content": text}).encode("utf-8")
    req = urllib.request.Request(
        f"{SERVER}/embedding",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
        if isinstance(result, list) and result:
            emb = result[0].get("embedding", [])
            if emb and isinstance(emb[0], list):
                return emb[0]
            return emb
        elif isinstance(result, dict):
            emb = result.get("embedding", [])
            if emb and isinstance(emb[0], list):
                return emb[0]
            return emb
        return []

def cosine(a, b):
    dot = sum(x*y for x, y in zip(a, b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    return dot / (na * nb + 1e-8)

def search(query, top_k=5):
    if not DB.exists():
        print(f"❌ No embeddings at {DB}")
        print("   Run: embed-docs")
        return
    qvec = embed_query(query)
    records = []
    with open(DB) as f:
        for line in f:
            rec = json.loads(line)
            sim = cosine(qvec, rec["embedding"])
            records.append((sim, rec))
    records.sort(key=lambda x: x[0], reverse=True)
    print(f"\n🔍 \"{query}\"")
    print(f"📊 Searched {len(records)} chunks\n")
    for i, (sim, rec) in enumerate(records[:top_k]):
        fname = os.path.basename(rec["file"])
        preview = rec["preview"][:150].replace("\n", " ")
        print(f"{'─'*60}")
        print(f"#{i+1} | {fname} chunk#{rec['chunk_idx']} | sim={sim:.3f}")
        print(f"    {preview}...")
    if records:
        try:
            import subprocess
            subprocess.run(["termux-clipboard-set", records[0][1]["preview"][:500]])
            print(f"\n📋 Top result → clipboard")
        except:
            pass

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else input("Query: ")
    search(q)
