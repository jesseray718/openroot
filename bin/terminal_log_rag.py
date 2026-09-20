#!/usr/bin/env python3
"""terminal_log_rag.py — RAG ingestion for Reh1t #53"""
import os, sys
from pathlib import Path
import sqlite3

LOG_DIR = os.path.expanduser("~/openroot/context_bridge/")
DB = os.path.expanduser("~/openroot/data/terminal_log.db")

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        content TEXT,
        timestamp TEXT,
        embedding TEXT
    )""")
    conn.commit()
    return conn

def ingest_logs(conn):
    log_files = list(Path(LOG_DIR).glob("session-*.md")) + list(Path(LOG_DIR).glob("*.log"))
    inserted = 0
    for lf in log_files:
        content = lf.read_text(errors="replace")
        conn.execute(
            "INSERT INTO logs (filename, content, timestamp) VALUES (?, ?, ?)",
            (lf.name, content[:10000], datetime.utcnow().isoformat())
        )
        inserted += 1
    conn.commit()
    return inserted

def search(query):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT filename, content FROM logs WHERE content LIKE ?", (f"%{query}%",))
    return cur.fetchall()

if __name__ == "__main__":
    from datetime import datetime
    conn = init_db()
    count = ingest_logs(conn)
    print(f"[RAG] Ingested {count} logs into {DB}")
    if len(sys.argv) > 1:
        results = search(sys.argv[1])
        print(f"[SEARCH] {len(results)} hits")
