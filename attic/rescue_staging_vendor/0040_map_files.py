#!/usr/bin/env python3
import os
import sqlite3
import time

DB_PATH = "file_map.sqlite"
# Target roots to scan (add any custom SD card mount paths here)
TARGET_PATHS = [
    os.path.expanduser("~"),
    "/sdcard",
    "/storage",
    "/mnt"
]

def init_db(conn):
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=OFF;")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS file_map (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_path TEXT UNIQUE,
            directory TEXT,
            filename TEXT,
            extension TEXT,
            size_bytes INTEGER,
            mtime REAL
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_dir ON file_map(directory);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ext ON file_map(extension);")
    conn.commit()

def scan_and_index():
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    
    batch = []
    total_files = 0
    start_time = time.time()
    
    print("[*] Starting file scan...")
    for root_target in TARGET_PATHS:
        if not os.path.exists(root_target):
            continue
        print(f"[-] Scanning: {root_target}")
        for root, _, files in os.walk(root_target):
            for file in files:
                full_path = os.path.join(root, file)
                try:
                    stat = os.stat(full_path)
                    ext = os.path.splitext(file)[1].lower()
                    batch.append((
                        full_path,
                        root,
                        file,
                        ext,
                        stat.st_size,
                        stat.st_mtime
                    ))
                    total_files += 1
                except (PermissionError, FileNotFoundError, OSError):
                    continue

                if len(batch) >= 10000:
                    conn.executemany("""
                        INSERT OR REPLACE INTO file_map 
                        (full_path, directory, filename, extension, size_bytes, mtime)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, batch)
                    conn.commit()
                    batch.clear()

    if batch:
        conn.executemany("""
            INSERT OR REPLACE INTO file_map 
            (full_path, directory, filename, extension, size_bytes, mtime)
            VALUES (?, ?, ?, ?, ?, ?)
        """, batch)
        conn.commit()
        
    conn.close()
    print(f"[+] Done. Indexed {total_files:,} files in {round(time.time() - start_time, 2)}s.")

if __name__ == "__main__":
    scan_and_index()
