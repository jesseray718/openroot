#!/usr/bin/env python3
"""Embed Kai9000 markdown docs into local vector store."""
import json, os, time, urllib.request, urllib.error
from pathlib import Path

SERVER = "http://127.0.0.1:9998"
SRC_DIR = Path("/data/data/com.termux/files/home/projects/agape-une")
OUTPUT = SRC_DIR / "vectors/kai_embeddings.jsonl"

def chunk_text(text, max_size=500, overlap=50):
    chunks = []
    pos = 0
    while pos < len(text):
        end = min(pos + max_size, len(text))
        if end < len(text) and "\n" in text[pos:end]:
            end = text.rfind("\n", pos, end) + 1
        chunks.append(text[pos:end])
        pos = end - overlap if end < len(text) else end
    return chunks

def embed_text(text):
    data = json.dumps({"content": text}).encode("utf-8")
    req = urllib.request.Request(
        f"{SERVER}/embedding",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            if isinstance(result, list):
                return result
            return result.get("embedding", [])
    except urllib.error.URLError as e:
        print(f"     ❌ Server error: {e}")
        return None

def main():
    import sys
    os.makedirs(OUTPUT.parent, exist_ok=True)
    
    print(f"🔌 Checking embedding server at {SERVER}...")
    try:
        with urllib.request.urlopen(SERVER, timeout=2) as r:
            if r.status != 200: raise Exception("Bad status")
    except:
        print(f"❌ Embedding server not running on {SERVER}")
        print(f"   Start it: embed-start")
        sys.exit(1)
    
    md_files = list(SRC_DIR.glob("**/*.md"))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    
    all_records = []
    for md_path in md_files:
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        chunks = chunk_text(content)
        fname = os.path.basename(md_path)
        print(f"  📄 {fname} — {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) < 20:
                continue
            vec = embed_text(chunk)
            if vec is None:
                print(f"     ❌ chunk {i} failed")
                continue
            all_records.append({
                "file": str(md_path),
                "chunk_idx": i,
                "preview": chunk[:200],
                "embedding": vec
            })
            time.sleep(0.1)
    
    with open(OUTPUT, "w", encoding="utf-8") as f:
        for rec in all_records:
            f.write(json.dumps(rec) + "\n")
    
    print(f"\n✅ {len(all_records)} embeddings saved to {OUTPUT}")
    print(f"📐 Dimensions: {len(all_records[0]['embedding']) if all_records else 0}")
    print(f"💾 Size: {os.path.getsize(OUTPUT) // 1024}KB")

if __name__ == "__main__":
    main()
