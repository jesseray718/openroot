#!/usr/bin/env python3
"""Embed Kai9000/agape-une markdown docs into local vector store."""
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
        f"{SERVER}/embedding", data=data,
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            if isinstance(result, list) and result:
                emb = result[0].get("embedding", [])
                return emb[0] if emb and isinstance(emb[0], list) else emb
            elif isinstance(result, dict):
                emb = result.get("embedding", [])
                return emb[0] if emb and isinstance(emb[0], list) else emb
            return []
    except urllib.error.URLError as e:
        print(f"     ❌ Server error: {e}")
        return None

def main():
    os.makedirs(OUTPUT.parent, exist_ok=True)
    print(f"🔌 Connecting to embedding server at {SERVER}...")
    md_files = list(SRC_DIR.glob("**/*.md"))
    all_records = []
    for md_path in md_files:
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        chunks = ch
