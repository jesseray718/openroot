#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
import sys
import sqlite3
import json
import argparse
import urllib.request
import os

def get_embedding(text, model="nomic-embed-text", ollama_url="http://localhost:11434"):
    url = f"{ollama_url}/api/embeddings"
    payload = json.dumps({"model": model, "prompt": text}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode("utf-8"))
            return json.dumps(res.get("embedding", []))
    except Exception as e:
        print(f"Warning: Could not fetch embedding from Ollama ({e}). Storing NULL vector.", file=sys.stderr)
        return json.dumps([])

def setup_tables(db_path):
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_embeddings (
            task_id TEXT PRIMARY KEY,
            embedding TEXT,
            model_used TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

def sync_embeddings(db_path, model):
    setup_tables(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT task_id, goal FROM task_ledger")
    tasks = cursor.fetchall()
    
    if not tasks:
        print("No tasks found in task_ledger to embed.")
    
    for task_id, goal in tasks:
        cursor.execute("SELECT task_id FROM task_embeddings WHERE task_id = ?", (task_id,))
        if not cursor.fetchone() and goal:
            print(f"Generating embedding for task: {task_id}")
            vec_json = get_embedding(goal, model=model)
            cursor.execute(
                "INSERT INTO task_embeddings (task_id, embedding, model_used) VALUES (?, ?, ?)",
                (task_id, vec_json, model)
            )
            conn.commit()
            
    conn.close()
    print("Vector embedding synchronization complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embed task ledger entries using Ollama.")
    parser.add_argument("--db", required=True, help="Path to SQLite database ledger")
    parser.add_argument("--model", default="nomic-embed-text", help="Embedding model name")
    args = parser.parse_args()
    
    sync_embeddings(args.db, args.model)
