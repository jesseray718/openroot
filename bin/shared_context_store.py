#!/usr/bin/env python3
"""
shared_context_store.py - Cross-window state persistence v1.0
Stores/retrieves data accessible by all Lumo windows via SQLite
CANARY: CONTEXT_STORE_V1_20260924
"""
import sqlite3
import json
import hashlib
import os
import sys
from pathlib import Path
from datetime import datetime

BASE = Path("/home/jesse/openroot")
DB_PATH = BASE / "data" / "shared_context.db"

def init_db():
    """Initialize database schema"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS context (
        key TEXT PRIMARY KEY,
        value TEXT,
        timestamp TEXT,
        session_id TEXT,
        hash TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        name TEXT,
        started TEXT,
        last_active TEXT
    )''')
    conn.commit()
    conn.close()

def store(key, value, session_id=None):
    """Store data with hash verification"""
    if session_id is None:
        session_id = os.environ.get('SESSION_ID', 'anonymous')
    timestamp = datetime.now().isoformat()
    value_str = json.dumps(value) if isinstance(value, dict) else str(value)
    hash_val = hashlib.sha256(f"{key}{value_str}{timestamp}".encode()).hexdigest()[:16]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO context (key, value, timestamp, session_id, hash) VALUES (?, ?, ?, ?, ?)',
              (key, value_str, timestamp, session_id, hash_val))
    conn.commit()
    conn.close()
    print(f"[STORED] {key} @ {hash_val}")
    return hash_val

def get(key):
    """Retrieve data by key"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT value, timestamp, hash FROM context WHERE key = ?', (key,))
    row = c.fetchone()
    conn.close()
    if row:
        try:
            value = json.loads(row[0])
        except:
            value = row[0]
        return {"value": value, "timestamp": row[1], "hash": row[2]}
    return None

def register_session(session_id, name="worker"):
    """Register active session"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('INSERT OR REPLACE INTO sessions (id, name, started, last_active) VALUES (?, ?, ?, ?)',
              (session_id, name, now, now))
    conn.commit()
    conn.close()
    print(f"[REGISTERED] {session_id} ({name})")

def list_sessions():
    """List all active sessions"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, started, last_active FROM sessions ORDER BY last_active DESC')
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "started": r[2], "last_active": r[3]} for r in rows]

def main():
    init_db()
    if len(sys.argv) < 2:
        print("Usage:")
        print("  store <key> <value>")
        print("  get <key>")
        print("  register <session_id> [name]")
        print("  sessions")
        return
    command = sys.argv[1].lower()
    if command == 'store' and len(sys.argv) >= 4:
        store(sys.argv[2], sys.argv[3], os.environ.get('SESSION_ID'))
    elif command == 'get' and len(sys.argv) >= 3:
        result = get(sys.argv[2])
        if result:
            print(json.dumps(result, indent=2))
        else:
            print(f"Key '{sys.argv[2]}' not found")
    elif command == 'register' and len(sys.argv) >= 3:
        register_session(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "worker")
    elif command == 'sessions':
        sessions = list_sessions()
        print(json.dumps(sessions, indent=2))
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
