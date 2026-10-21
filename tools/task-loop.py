#!/usr/bin/env python3
import sqlite3
import os
import sys

DB_DIR = os.path.expanduser("~/.local/share/openroot")
DB_PATH = os.path.join(DB_DIR, "ledger.db")

def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_ledger (
            task_id TEXT PRIMARY KEY,
            repo TEXT,
            branch TEXT,
            goal TEXT,
            status TEXT,
            commit_sha TEXT,
            pr_num TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

def record_task(task_id, repo, branch, goal):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO task_ledger (task_id, repo, branch, goal, status)
        VALUES (?, ?, ?, ?, 'pending')
    """, (task_id, repo, branch, goal))
    conn.commit()
    conn.close()

def update_task(task_id, status, commit_sha=None, pr_num=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE task_ledger 
        SET status = ?, commit_sha = COALESCE(?, commit_sha), pr_num = COALESCE(?, pr_num)
        WHERE task_id = ?
    """, (status, commit_sha, pr_num, task_id))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "init":
        init_db()
    elif cmd == "record" and len(sys.argv) >= 5:
        record_task(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif cmd == "update" and len(sys.argv) >= 3:
        sha = sys.argv[4] if len(sys.argv) > 4 else None
        pr = sys.argv[5] if len(sys.argv) > 5 else None
        update_task(sys.argv[2], sys.argv[3], sha, pr)
