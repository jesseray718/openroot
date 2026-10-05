#!/usr/bin/env python3
import os
import sys
import json
import hashlib
import sqlite3
from datetime import datetime, timezone

LEDGER_DIR = os.getenv("OPENROOT_HOME", os.path.expanduser("~/openroot")) + "/data"
LEDGER_FILE = os.path.join(LEDGER_DIR, "knowledge_ledger.jsonl")
DB_FILE = os.path.join(LEDGER_DIR, "knowledge.db")

def init_db():
    os.makedirs(LEDGER_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Create FTS5 table for full-text search indexing
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS ledger_fts USING fts5(
            entry_id,
            content,
            tags
        );
    """)
    conn.commit()
    conn.close()

def compute_hash(prev_hash, data_str):
    block_string = f"{prev_hash}:{data_str}"
    return hashlib.sha256(block_string.encode('utf-8')).hexdigest()

def get_last_hash_and_index():
    if not os.path.exists(LEDGER_FILE):
        return "0" * 64, 0
    
    last_hash = "0" * 64
    count = 0
    with open(LEDGER_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                count += 1
                try:
                    record = json.loads(line)
                    last_hash = record.get("hash", last_hash)
                except json.JSONDecodeError:
                    continue
    return last_hash, count

def append_entry(content, tags=""):
    init_db()
    prev_hash, index = get_last_hash_and_index()
    
    timestamp = datetime.now(timezone.utc).isoformat()
    payload = {
        "index": index + 1,
        "timestamp": timestamp,
        "content": content,
        "tags": tags,
        "prev_hash": prev_hash
    }
    
    # Compute block hash excluding the hash field itself
    payload_str = json.dumps(payload, sort_keys=True)
    block_hash = compute_hash(prev_hash, payload_str)
    
    record = {**payload, "hash": block_hash}
    
    # Append to JSONL
    with open(LEDGER_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
        
    # Index in SQLite FTS5
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO ledger_fts(entry_id, content, tags) VALUES (?, ?, ?);",
        (str(index + 1), content, tags)
    )
    conn.commit()
    conn.close()
    print(f"Successfully appended entry #{index + 1} [Hash: {block_hash[:12]}...]")

def search_ledger(query):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT entry_id, content, tags FROM ledger_fts WHERE ledger_fts MATCH ?;",
        (query,)
    )
    results = cursor.fetchall()
    conn.close()
    
    print(f"Found {len(results)} matching entries for query: '{query}'")
    for r in results:
        print(f"[{r[0]}] Tags: {r[2]} \nContent: {r[1]}\n{'-'*40}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ledger.py [append|search] [arguments]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "append":
        content = sys.argv[2] if len(sys.argv) > 2 else "Genesis block test entry"
        tags = sys.argv[3] if len(sys.argv) > 3 else "test"
        append_entry(content, tags)
    elif cmd == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else "*"
        search_ledger(query)
    else:
        print(f"Unknown command: {cmd}")
