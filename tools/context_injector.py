#!/usr/bin/env python3
import sqlite3
import os
import sys

DB_PATH = os.path.expanduser("~/.local/share/openroot/ledger.db")

def get_db_context(limit=5):
    if not os.path.exists(DB_PATH):
        return "No local database history found."
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Pull recent tasks from ledger
        cursor.execute("""
            SELECT task_id, goal, status, commit_sha, pr_num 
            FROM task_ledger 
            ORDER BY rowid DESC LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "No prior task entries in database."
            
        context_lines = []
        for r in rows:
            line = f"- Task: {r[0]} | Goal: {r[1]} | Status: {r[2]}"
            if r[3]:
                line += f" | SHA: {r[3]}"
            if r[4]:
                line += f" | PR: #{r[4]}"
            context_lines.append(line)
            
        return "\n".join(context_lines)
    except Exception as e:
        return f"Database read warning: {e}"

if __name__ == "__main__":
    print(get_db_context())
