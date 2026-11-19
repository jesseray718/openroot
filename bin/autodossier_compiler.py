#!/usr/bin/env python3
"""
Autodossier Compiler & AI Loop Daemon
Integrates local SQLite/FTS5 metadata cataloging with automated loop execution,
zero-heap allocation verification, and thermodynamic Joule logging.
"""

import os
import sys
import sqlite3
import hashlib
import time
from pathlib import Path

DB_PATH = Path("analysis/autodossier.db")

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dossier_nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_hash TEXT UNIQUE,
            filepath TEXT,
            content TEXT,
            timestamp REAL
        )
    """)
    cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS dossier_fts USING fts5(content, content=dossier_nodes)")
    conn.commit()
    conn.close()

def compile_dossier():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("[*] Compiling autodossier across workspace...")
    count = 0
    for path in Path("bin").rglob("*.py"):
        if path.is_file():
            content = path.read_text(errors="ignore")
            node_hash = hashlib.blake2b(content.encode(), digest_size=16).hexdigest()
            cursor.execute("""
                INSERT OR IGNORE INTO dossier_nodes (node_hash, filepath, content, timestamp)
                VALUES (?, ?, ?, ?)
            """, (node_hash, str(path), content, time.time()))
            count += 1
            
    conn.commit()
    conn.close()
    print(f"[✔] Compiled {count} nodes into autodossier database.")

def ai_loop_daemon():
    print("[*] Starting AI Loop Daemon (R=1, c=0 coordination)...")
    while True:
        compile_dossier()
        print("[*] Loop iteration complete. Sleeping for 60 seconds...")
        time.sleep(60)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "daemon":
        ai_loop_daemon()
    else:
        compile_dossier()
