#!/usr/bin/env python3
import os
import sys
import sqlite3
import hashlib
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

CHUNK_SIZE = 1024 * 1024  # 1 MB Chunks
DB_PATH = Path("/home/jesse/openroot/kit/chunk_index.sqlite")

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS files (
                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE,
                size INTEGER,
                mtime REAL,
                indexed_at REAL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER,
                chunk_index INTEGER,
                offset INTEGER,
                length INTEGER,
                hash TEXT,
                FOREIGN KEY(file_id) REFERENCES files(file_id)
            );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_file_path ON files(path);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_chunk_hash ON chunks(hash);")
    conn.close()

def hash_file_chunks(file_path):
    """Worker task: reads file in 1MB chunks and hashes each chunk using BLAKE2b."""
    try:
        stat = os.stat(file_path)
        chunks_data = []
        offset = 0
        chunk_idx = 0

        with open(file_path, "rb") as f:
            while True:
                buf = f.read(CHUNK_SIZE)
                if not buf:
                    break
                h = hashlib.blake2b(buf).hexdigest()
                chunks_data.append((chunk_idx, offset, len(buf), h))
                offset += len(buf)
                chunk_idx += 1

        return {
            "path": str(file_path),
            "size": stat.st_size,
            "mtime": stat.st_mtime,
            "chunks": chunks_data,
            "error": None
        }
    except Exception as e:
        return {"path": str(file_path), "error": str(e)}

def scan_target_directory(target_dir, db_path):
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Pre-load known files and mtimes for incremental caching
    known_files = {row[0]: (row[1], row[2], row[3]) for row in cursor.execute("SELECT path, file_id, size, mtime FROM files").fetchall()}

    files_to_process = []
    skipped_count = 0

    print(f"[*] Scanning paths in {target_dir}...")
    for root, _, filenames in os.walk(target_dir):
        for fname in filenames:
            full_path = os.path.join(root, fname)
            try:
                st = os.stat(full_path)
                if full_path in known_files:
                    _, k_size, k_mtime = known_files[full_path]
                    if k_size == st.st_size and k_mtime == st.st_mtime:
                        skipped_count += 1
                        continue
                files_to_process.append(full_path)
            except OSError:
                continue

    print(f"[*] Found {len(files_to_process)} modified/new files. ({skipped_count} unchanged skipped)")
    if not files_to_process:
        print("[+] Index up to date. Nothing to process.")
        conn.close()
        return

    workers = max(1, os.cpu_count() - 1)
    print(f"[*] Processing files using {workers} parallel CPU workers...")
    
    start_time = time.time()
    processed = 0

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(hash_file_chunks, p): p for p in files_to_process}
        
        for future in as_completed(futures):
            res = future.result()
            if res.get("error"):
                continue
                
            path = res["path"]
            size = res["size"]
            mtime = res["mtime"]
            chunks = res["chunks"]

            with conn:
                # Remove existing chunks/records if re-indexing modified file
                if path in known_files:
                    old_file_id = known_files[path][0]
                    cursor.execute("DELETE FROM chunks WHERE file_id = ?", (old_file_id,))
                    cursor.execute("DELETE FROM files WHERE file_id = ?", (old_file_id,))

                cursor.execute(
                    "INSERT INTO files (path, size, mtime, indexed_at) VALUES (?, ?, ?, ?)",
                    (path, size, mtime, time.time())
                )
                file_id = cursor.lastrowid

                chunk_rows = [(file_id, c[0], c[1], c[2], c[3]) for c in chunks]
                cursor.executemany(
                    "INSERT INTO chunks (file_id, chunk_index, offset, length, hash) VALUES (?, ?, ?, ?, ?)",
                    chunk_rows
                )

            processed += 1
            if processed % 100 == 0 or processed == len(files_to_process):
                print(f"  [+] Indexed {processed}/{len(files_to_process)} files...")

    conn.close()
    elapsed = time.time() - start_time
    print(f"[+] Chunk indexing completed in {elapsed:.2f}s.")

if __name__ == "__main__":
    scan_dir = sys.argv[1] if len(sys.argv) > 1 else "/home/jesse/openroot"
    scan_target_directory(scan_dir, DB_PATH)
