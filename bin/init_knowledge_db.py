#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0
# init_knowledge_db.py — Local FTS5 & Document Indexer for Local LLM RAG

import sqlite3
from pathlib import Path

ROOT = Path.home() / "openroot"
DB_PATH = ROOT / "data" / "fts_index.db"

def setup_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create Full-Text Search (FTS5) virtual table
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
            filepath,
            title,
            content,
            tokenize='porter ascii'
        );
    """)
    
    # Index Markdown and Python files
    indexed_count = 0
    for ext in ("*.md", "*.py", "*.jsonl"):
        for file_path in ROOT.rglob(ext):
            if ".git" in file_path.parts:
                continue
            try:
                text = file_path.read_text(encoding="utf-8", errors="ignore")
                cursor.execute(
                    "INSERT INTO knowledge_fts (filepath, title, content) VALUES (?, ?, ?);",
                    (str(file_path.relative_to(ROOT)), file_path.name, text)
                )
                indexed_count += 1
            except Exception as e:
                print(f"[!] Error indexing {file_path}: {e}")
                
    conn.commit()
    conn.close()
    print(f"[+] Knowledge DB initialized at {DB_PATH}. Indexed {indexed_count} files.")

if __name__ == "__main__":
    setup_database()
