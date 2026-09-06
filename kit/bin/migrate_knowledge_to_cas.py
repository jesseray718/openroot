#!/usr/bin/env python3
"""
migrate_knowledge_to_cas.py — Batch converts knowledge.db (289k records)
into Zstandard compressed, BLAKE2b deduplicated CAS storage.
"""

import os
import sys
import json
import sqlite3
import hashlib
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

SRC_DB = Path("/home/jesse/knowledge-node/knowledge.db")
DEST_DB = Path("/home/jesse/openroot/kit/cas_ledger.sqlite")
CHUNK_SIZE = 1024 * 1024  # 1MB

def compress_bytes(data: bytes) -> bytes:
    try:
        import zstandard as zstd
        return zstd.ZstdCompressor(level=3).compress(data)
    except ImportError:
        import zlib
        return zlib.compress(data, level=6)

def process_file_batch(file_paths):
    """Worker task to read, chunk, and hash a batch of file paths."""
    results = []
    for path in file_paths:
        if not os.path.isfile(path):
            continue
        try:
            st = os.stat(path)
            chunk_hashes = []
            blobs = []
            
            with open(path, "rb") as f:
                while True:
                    buf = f.read(CHUNK_SIZE)
                    if not buf:
                        break
                    h = hashlib.blake2b(buf).hexdigest()
                    chunk_hashes.append(h)
                    
                    # Detect if snippet is code/text eligible for 7B tidbits
                    is_code = len(buf) < 50000 and any(path.endswith(ext) for ext in ['.py', '.md', '.json', '.sh', '.rs', '.cpp', '.c', '.go', '.js', '.ts'])
                    blobs.append((h, compress_bytes(buf), len(buf), is_code, path if is_code else None))
            
            results.append((path, st.st_size, st.st_mtime, json.dumps(chunk_hashes), blobs))
        except Exception:
            continue
    return results

def run_migration():
    if not SRC_DB.exists():
        print(f"[!] Source database non-existent: {SRC_DB}")
        return

    print(f"[*] Connecting to source: {SRC_DB}")
    src_conn = sqlite3.connect(SRC_DB)
    
    # Try fetching file paths from knowledge.db
    cursor = src_conn.cursor()
    tables = [t[0] for t in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    
    path_col = "path" if "path" in [c[1] for c in cursor.execute("PRAGMA table_info(files)").fetchall()] else "filepath"
    paths = [row[0] for row in cursor.execute(f"SELECT {path_col} FROM files WHERE {path_col} IS NOT NULL").fetchall()]
    src_conn.close()

    total_paths = len(paths)
    print(f"[*] Loaded {total_paths:,} target files from legacy database.")

    # Multi-processing setup
    batch_size = 500
    path_batches = [paths[i:i + batch_size] for i in range(0, len(paths), batch_size)]
    workers = max(1, os.cpu_count() - 1)

    print(f"[*] Processing using {workers} parallel CPU workers in batches of {batch_size}...")
    
    dest_conn = sqlite3.connect(DEST_DB)
    dest_conn.execute("PRAGMA journal_mode=WAL;")
    dest_conn.execute("PRAGMA synchronous=NORMAL;")
    
    processed_count = 0
    start_time = time.time()

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(process_file_batch, batch): batch for batch in path_batches}
        
        for future in as_completed(futures):
            batch_results = future.result()
            
            with dest_conn:
                for path, size, mtime, chunk_hashes_json, blobs in batch_results:
                    for h, comp_data, raw_size, is_code, src_path in blobs:
                        dest_conn.execute("""
                            INSERT INTO cas_blobs (hash, compressed_data, raw_size, compressed_size, ref_count)
                            VALUES (?, ?, ?, ?, 1)
                            ON CONFLICT(hash) DO UPDATE SET ref_count = ref_count + 1;
                        """, (h, comp_data, raw_size, len(comp_data)))
                    
                    dest_conn.execute("""
                        INSERT OR REPLACE INTO file_manifests (path, size, mtime, chunk_hashes)
                        VALUES (?, ?, ?, ?);
                    """, (path, size, mtime, chunk_hashes_json))
            
            processed_count += len(batch_results)
            if processed_count % 2500 == 0 or processed_count >= total_paths:
                elapsed = time.time() - start_time
                fps = processed_count / elapsed if elapsed > 0 else 0
                print(f"  [+] Ingested {processed_count:,} / {total_paths:,} files ({fps:.1f} files/sec)")

    dest_conn.close()
    print(f"[+] Legacy Migration completed in {time.time() - start_time:.2f} seconds.")

if __name__ == "__main__":
    run_migration()
