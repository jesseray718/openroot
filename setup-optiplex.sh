#!/usr/bin/env bash
set -Eeuo pipefail

echo "==> Deploying pipeline tools directly to OptiPlex..."

ssh optiplex "mkdir -p ~/openroot/tools"

ssh optiplex "cat << 'REMOTE_EOF' > ~/openroot/tools/task-loop.py
#!/usr/bin/env python3
import sqlite3
import os
import sys

DB_DIR = os.path.expanduser('~/.local/share/openroot')
DB_PATH = os.path.join(DB_DIR, 'ledger.db')

def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
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
    ''')
    conn.commit()
    conn.close()

def record_task(task_id, repo, branch, goal):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO task_ledger (task_id, repo, branch, goal, status)
        VALUES (?, ?, ?, ?, 'pending')
    ''', (task_id, repo, branch, goal))
    conn.commit()
    conn.close()

def update_task(task_id, status, commit_sha=None, pr_num=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE task_ledger 
        SET status = ?, commit_sha = COALESCE(?, commit_sha), pr_num = COALESCE(?, pr_num)
        WHERE task_id = ?
    ''', (status, commit_sha, pr_num, task_id))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'init':
        init_db()
    elif cmd == 'record' and len(sys.argv) >= 5:
        record_task(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif cmd == 'update' and len(sys.argv) >= 3:
        sha = sys.argv[4] if len(sys.argv) > 4 else None
        pr = sys.argv[5] if len(sys.argv) > 5 else None
        update_task(sys.argv[2], sys.argv[3], sha, pr)
REMOTE_EOF"

ssh optiplex "cat << 'REMOTE_EOF' > ~/openroot/tools/context_injector.py
#!/usr/bin/env python3
import sqlite3
import os

DB_PATH = os.path.expanduser('~/.local/share/openroot/ledger.db')

def get_db_context(limit=5):
    if not os.path.exists(DB_PATH):
        return 'No prior database context.'
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT task_id, goal, status, commit_sha, pr_num 
            FROM task_ledger 
            ORDER BY rowid DESC LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            return 'No prior tasks logged.'
        return '\n'.join([f'- Task: {r[0]} | Goal: {r[1]} | Status: {r[2]}' for r in rows])
    except Exception as e:
        return f'Context warning: {e}'

if __name__ == '__main__':
    print(get_db_context())
REMOTE_EOF"

ssh optiplex "cat << 'REMOTE_EOF' > ~/openroot/enable_vector_embeddings.py
#!/usr/bin/env python3
import sys, sqlite3, json, argparse, urllib.request, os

def get_embedding(text, model='nomic-embed-text', ollama_url='http://localhost:11434'):
    url = f'{ollama_url}/api/embeddings'
    payload = json.dumps({'model': model, 'prompt': text}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            return json.dumps(res.get('embedding', []))
    except Exception:
        return json.dumps([])

def sync_embeddings(db_path, model):
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_ledger (
            task_id TEXT PRIMARY KEY, repo TEXT, branch TEXT, goal TEXT, status TEXT, commit_sha TEXT, pr_num TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_embeddings (
            task_id TEXT PRIMARY KEY, embedding TEXT, model_used TEXT, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    cursor.execute('SELECT task_id, goal FROM task_ledger')
    tasks = cursor.fetchall()
    for task_id, goal in tasks:
        cursor.execute('SELECT task_id FROM task_embeddings WHERE task_id = ?', (task_id,))
        if not cursor.fetchone() and goal:
            vec_json = get_embedding(goal, model=model)
            cursor.execute('INSERT INTO task_embeddings (task_id, embedding, model_used) VALUES (?, ?, ?)', (task_id, vec_json, model))
            conn.commit()
    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', required=True)
    parser.add_argument('--model', default='nomic-embed-text')
    args = parser.parse_args()
    sync_embeddings(args.db, args.model)
REMOTE_EOF"

ssh optiplex "chmod +x ~/openroot/enable_vector_embeddings.py ~/openroot/tools/*.py"
ssh optiplex "python3 ~/openroot/tools/task-loop.py init"

echo "==> Setup Complete! OptiPlex is fully provisioned."
