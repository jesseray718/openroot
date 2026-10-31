#!/usr/bin/env python3
import sqlite3
import os
import json
import re

SOURCE_DB = "file_map.sqlite"
SAFE_DB = "file_map_safe.sqlite"
SECRETS_DB = "file_map_secrets.sqlite"
CONTEXT_OUT = "coder_context.json"

# Regex patterns to flag sensitive files
SECRET_PATTERNS = [
    r'\.env', r'id_rsa', r'id_ed25519', r'\.pem$', r'\.key$', r'\.crt$',
    r'secret', r'token', r'credential', r'password', r'auth', r'shadow'
]

def is_secret(filepath):
    path_lower = filepath.lower()
    return any(re.search(pat, path_lower) for pat in SECRET_PATTERNS)

def split_databases():
    if not os.path.exists(SOURCE_DB):
        print(f"[!] Source database {SOURCE_DB} not found. Run map_files.py first.")
        return

    # Clean previous outputs
    for db in [SAFE_DB, SECRETS_DB]:
        if os.path.exists(db):
            os.remove(db)

    src_conn = sqlite3.connect(SOURCE_DB)
    safe_conn = sqlite3.connect(SAFE_DB)
    sec_conn = sqlite3.connect(SECRETS_DB)

    schema = """
        CREATE TABLE file_map (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_path TEXT UNIQUE,
            directory TEXT,
            filename TEXT,
            extension TEXT,
            size_bytes INTEGER,
            mtime REAL
        );
        CREATE INDEX idx_dir ON file_map(directory);
        CREATE INDEX idx_ext ON file_map(extension);
    """
    safe_conn.executescript(schema)
    sec_conn.executescript(schema)

    cursor = src_conn.execute("SELECT full_path, directory, filename, extension, size_bytes, mtime FROM file_map")
    
    safe_batch = []
    sec_batch = []
    
    for row in cursor:
        if is_secret(row[0]):
            sec_batch.append(row)
        else:
            safe_batch.append(row)

    query = "INSERT INTO file_map (full_path, directory, filename, extension, size_bytes, mtime) VALUES (?, ?, ?, ?, ?, ?)"
    safe_conn.executemany(query, safe_batch)
    sec_conn.executemany(query, sec_batch)

    safe_conn.commit()
    sec_conn.commit()
    
    print(f"[+] Safe DB created: {len(safe_batch):,} entries -> {SAFE_DB}")
    print(f"[+] Secrets DB created: {len(sec_batch):,} entries -> {SECRETS_DB}")
    
    src_conn.close()
    safe_conn.close()
    sec_conn.close()

def generate_context():
    conn = sqlite3.connect(SAFE_DB)

    # Auto-detect Project Roots
    roots = conn.execute("""
        SELECT DISTINCT directory FROM file_map 
        WHERE filename IN ('pyproject.toml', 'package.json', 'Cargo.toml', 'requirements.txt')
          AND directory NOT LIKE '%node_modules%'
          AND directory NOT LIKE '%.git%'
        ORDER BY directory ASC
    """).fetchall()

    # Auto-detect SQLite Databases
    dbs = conn.execute("""
        SELECT full_path FROM file_map 
        WHERE extension = '.sqlite' OR extension = '.db'
        ORDER BY size_bytes DESC
        LIMIT 5
    """).fetchall()

    context = {
        "project_roots": [r[0] for r in roots],
        "pathways": {
            "sqlite_databases": [d[0] for d in dbs],
            "safe_file_map_db": os.path.abspath(SAFE_DB),
            "notes_and_prompts": "/storage/emulated/0/Documents/markor/"
        },
        "rules": [
            f"ALWAYS query {os.path.abspath(SAFE_DB)} via 'SELECT full_path FROM file_map WHERE filename = :target' before assuming a file does not exist.",
            "NEVER request or attempt to query secrets or credential files.",
            "IGNORE directories matching %node_modules%, %.git/objects%, or %__pycache%%."
        ]
    }

    with open(CONTEXT_OUT, "w") as f:
        json.dump(context, f, indent=2)

    print(f"[+] Generated coder context -> {CONTEXT_OUT}")
    conn.close()

if __name__ == "__main__":
    split_databases()
    generate_context()
