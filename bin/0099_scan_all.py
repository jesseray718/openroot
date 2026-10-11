import os
import sqlite3
import sys

DB_NAME = "all_notes_repos.db"
# Scans Termux home, projects, and phone storage
SEARCH_PATHS = [
    os.path.expanduser("~"),
    "/sdcard/Documents",
    "/sdcard/Download",
    "/sdcard/Obsidian",
    "/sdcard/Notes"
]

EXTENSIONS = ('.md', '.txt', '.json', '.yaml', '.py', '.c', '.cpp', '.h', '.rs', '.sh', '.org')

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS global_fts USING fts5(
            filepath,
            filename,
            content
        );
    """)
    conn.commit()
    conn.close()

def scan_all():
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM global_fts;")
    
    indexed_count = 0
    print("Beginning deep scan of all notes and repositories...")
    
    for base_path in SEARCH_PATHS:
        if not os.path.exists(base_path):
            continue
        for root, dirs, files in os.walk(base_path):
            # Skip heavy hidden build folders
            dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '__pycache__', '.venv', 'build', 'target')]
            
            for file in files:
                if file.endswith(EXTENSIONS):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            text = f.read()
                        cursor.execute(
                            "INSERT INTO global_fts (filepath, filename, content) VALUES (?, ?, ?)",
                            (path, file, text)
                        )
                        indexed_count += 1
                        if indexed_count % 100 == 0:
                            print(f"Indexed {indexed_count} files...")
                    except Exception:
                        pass

    conn.commit()
    conn.close()
    print(f"\nFinished! Indexed {indexed_count} files into {DB_NAME}.")

def query_global(term):
    if not os.path.exists(DB_NAME):
        print("Database not built yet. Run 'python scan_all.py --build' first.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT filepath, snippet(global_fts, 2, '>>> ', ' <<<', '...', 8)
        FROM global_fts
        WHERE global_fts MATCH ?
        ORDER BY rank
        LIMIT 10;
    """, (term,))
    
    rows = cursor.fetchall()
    conn.close()
    
    print(f"\n--- Global Search Results for: '{term}' ---")
    if not rows:
        print("No matches found.")
    for path, snippet in rows:
        print(f"\nFile: {path}\nMatch: {snippet}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--build":
        scan_all()
    elif len(sys.argv) > 1:
        query_global(" ".join(sys.argv[1:]))
    else:
        query_text = input("Enter search query: ")
        query_global(query_text)
