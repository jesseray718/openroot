#!/usr/bin/env python3
"""
popw_tidbit_worker.py — Scans cas_blobs for unanalyzed code chunks, feeds them to 
Qwen2.5-Coder-7B to extract modular tidbits, and records PoPW entries into the ledger.
"""

import sqlite3
import json
import time
import urllib.request
import zlib
from pathlib import Path

DB_PATH = Path("/home/jesse/openroot/kit/cas_ledger.sqlite")
LLAMA_URL = "http://127.0.0.1:8080/v1/chat/completions"
MODEL_NAME = "qwen2.5-coder-7b"

def decompress_bytes(data: bytes) -> bytes:
    try:
        import zstandard as zstd
        return zstd.ZstdDecompressor().decompress(data)
    except ImportError:
        return zlib.decompress(data)

def call_qwen_tidbit(snippet_text: str) -> dict:
    prompt = (
        "Extract a modular code tidbit from this snippet.\n"
        "Return ONLY a valid JSON object: {\"category\": \"string\", \"summary\": \"string\", \"keywords\": [\"string\"]}\n\n"
        f"Snippet:\n{snippet_text[:1500]}"
    )
    payload = json.dumps({
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 200
    }).encode("utf-8")
    
    req = urllib.request.Request(LLAMA_URL, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            content = json.loads(resp.read().decode())["choices"][0]["message"]["content"]
            s = content.find("{")
            e = content.rfind("}")
            if s != -1 and e != -1:
                return json.loads(content[s:e+1])
    except Exception as err:
        pass
    return {"category": "general", "summary": "Code snippet chunk", "keywords": []}

def run_worker():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    
    print("[*] Starting PoPW Tidbit Extraction Worker against Qwen 7B...")
    
    while True:
        # Find blobs that do not yet have a tidbit entry
        query = """
            SELECT b.hash, b.compressed_data 
            FROM cas_blobs b 
            LEFT JOIN tidbits t ON b.hash = t.chunk_hash 
            WHERE t.chunk_hash IS NULL AND b.raw_size < 50000 
            LIMIT 50;
        """
        rows = conn.execute(query).fetchall()
        if not rows:
            print("[+] All available chunks analyzed for tidbits. Sleeping 10s...")
            time.sleep(10)
            continue

        for chunk_hash, comp_bytes in rows:
            try:
                raw_bytes = decompress_bytes(comp_bytes)
                text = raw_bytes.decode("utf-8", errors="ignore")
                
                if len(text.strip()) < 50:
                    tidbit_meta = {"category": "empty", "summary": "Short or non-text snippet", "keywords": []}
                else:
                    tidbit_meta = call_qwen_tidbit(text)

                tidbit_id = f"T_{chunk_hash[:12]}"
                conn.execute("""
                    INSERT OR REPLACE INTO tidbits (tidbit_id, chunk_hash, repo_origin, category, summary, embedding_json)
                    VALUES (?, ?, ?, ?, ?, ?);
                """, (tidbit_id, chunk_hash, "knowledge-node", tidbit_meta.get("category"), tidbit_meta.get("summary"), json.dumps(tidbit_meta.get("keywords"))))
                conn.commit()
                print(f"  [PoPW] Extracted Tidbit {tidbit_id} | Category: {tidbit_meta.get('category')}")
            except Exception as e:
                print(f"[!] Error processing chunk {chunk_hash[:8]}: {e}")

if __name__ == "__main__":
    run_worker()
