#!/usr/bin/env python3
"""
cas_tidbit_engine.py — High-density CAS deduplication, ZStandard compression, 
7B-driven tidbit chunking, and PoPW ledger recorder.
"""

import os
import sys
import json
import sqlite3
import hashlib
import urllib.request
import zlib  # Standard library fallback; use zstandard if available
from pathlib import Path

DB_PATH = Path("/home/jesse/openroot/kit/cas_ledger.sqlite")
LLAMA_URL = "http://127.0.0.1:8080/v1/chat/completions"
MODEL_NAME = "qwen2.5-coder-7b"

def init_cas_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    with conn:
        # Physical Blob Storage (Deduplicated)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cas_blobs (
                hash TEXT PRIMARY KEY,
                compressed_data BLOB,
                raw_size INTEGER,
                compressed_size INTEGER,
                ref_count INTEGER DEFAULT 1,
                created_at REAL DEFAULT (strftime('%s', 'now'))
            );
        """)
        # File Manifest Mapping
        conn.execute("""
            CREATE TABLE IF NOT EXISTS file_manifests (
                path TEXT PRIMARY KEY,
                size INTEGER,
                mtime REAL,
                chunk_hashes TEXT -- JSON Array of hashes
            );
        """)
        # PoPW & Modular Tidbits
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tidbits (
                tidbit_id TEXT PRIMARY KEY,
                chunk_hash TEXT,
                repo_origin TEXT,
                category TEXT,
                summary TEXT,
                embedding_json TEXT,
                FOREIGN KEY(chunk_hash) REFERENCES cas_blobs(hash)
            );
        """)
    conn.close()

def compress_bytes(data: bytes) -> bytes:
    try:
        import zstandard as zstd
        cctx = zstd.ZstdCompressor(level=3)
        return cctx.compress(data)
    except ImportError:
        return zlib.compress(data, level=6)

def decompress_bytes(data: bytes) -> bytes:
    try:
        import zstandard as zstd
        dctx = zstd.ZstdDecompressor()
        return dctx.decompress(data)
    except ImportError:
        return zlib.decompress(data)

def ask_7b_summarize_tidbit(code_snippet: str) -> dict:
    """Invokes local Qwen2.5-Coder-7B to extract modular architectural tidbits."""
    prompt = (
        "Extract a concise technical tidbit summary and category from this codebase chunk.\n"
        "Return ONLY a JSON object with keys: 'category', 'summary', 'keywords'.\n\n"
        f"Snippet:\n{code_snippet[:2000]}"
    )
    payload = json.dumps({
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 256
    }).encode("utf-8")
    
    req = urllib.request.Request(LLAMA_URL, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = json.loads(resp.read().decode())["choices"][0]["message"]["content"]
            # Extract JSON payload
            clean_json = raw[raw.find("{"):raw.rfind("}")+1]
            return json.loads(clean_json)
    except Exception:
        return {"category": "general", "summary": "Codebase chunk", "keywords": []}

def ingest_file(file_path: str, chunk_size=1024*1024):
    init_cas_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    path_obj = Path(file_path)
    if not path_obj.exists():
        print(f"[!] Path non-existent: {file_path}")
        return

    st = path_obj.stat()
    chunk_hashes = []
    
    with open(file_path, "rb") as f:
        while True:
            raw_chunk = f.read(chunk_size)
            if not raw_chunk:
                break
            
            chunk_hash = hashlib.blake2b(raw_chunk).hexdigest()
            chunk_hashes.append(chunk_hash)
            
            # Check if blob already exists in CAS
            cursor.execute("SELECT ref_count FROM cas_blobs WHERE hash = ?", (chunk_hash,))
            row = cursor.fetchone()
            
            if row:
                cursor.execute("UPDATE cas_blobs SET ref_count = ref_count + 1 WHERE hash = ?", (chunk_hash,))
            else:
                comp_data = compress_bytes(raw_chunk)
                cursor.execute(
                    "INSERT INTO cas_blobs (hash, compressed_data, raw_size, compressed_size) VALUES (?, ?, ?, ?)",
                    (chunk_hash, comp_data, len(raw_chunk), len(comp_data))
                )
                
                # If text snippet, generate 7B tidbit
                if len(raw_chunk) < 50000 and any(file_path.endswith(ext) for ext in ['.py', '.md', '.json', '.sh', '.rs', '.cpp']):
                    try:
                        text_content = raw_chunk.decode('utf-8', errors='ignore')
                        tidbit_meta = ask_7b_summarize_tidbit(text_content)
                        tidbit_id = f"T_{chunk_hash[:8]}"
                        cursor.execute(
                            "INSERT OR REPLACE INTO tidbits (tidbit_id, chunk_hash, repo_origin, category, summary) VALUES (?, ?, ?, ?, ?)",
                            (tidbit_id, chunk_hash, file_path, tidbit_meta.get("category", "code"), tidbit_meta.get("summary", ""))
                        )
                    except Exception:
                        pass

    cursor.execute(
        "INSERT OR REPLACE INTO file_manifests (path, size, mtime, chunk_hashes) VALUES (?, ?, ?, ?)",
        (str(file_path), st.st_size, st.st_mtime, json.dumps(chunk_hashes))
    )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        print(f"[*] Ingesting into CAS & Tidbit Ledger: {target}")
        if os.path.isfile(target):
            ingest_file(target)
        else:
            for root, _, files in os.walk(target):
                for f in files:
                    ingest_file(os.path.join(root, f))
        print("[+] CAS Ingestion complete.")
    else:
        print("Usage: python3 cas_tidbit_engine.py <file_or_directory_path>")
