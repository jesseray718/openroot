#!/usr/bin/env python3
import sqlite3
from pathlib import Path

DB_PATH = Path("/home/jesse/openroot/kit/cas_ledger.sqlite")

def init_cas_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    with conn:
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS file_manifests (
                path TEXT PRIMARY KEY,
                size INTEGER,
                mtime REAL,
                chunk_hashes TEXT
            );
        """)
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
    print("[+] Database schema initialized successfully at:", DB_PATH)

if __name__ == "__main__":
    init_cas_db()
