import os
import sqlite3

DB_NAME = "local_wisdom.db"
SCAN_DIR = "."

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Create SQLite FTS5 virtual table for ultra-fast full-text search
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(
            filepath,
            filename,
            content
        );
    """)
    conn.commit()
    conn.close()

def scan_and_index():
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Clear previous index
    cursor.execute("DELETE FROM docs_fts;")
    
    indexed_count = 0
    print("Scanning local files in wisdom-scaffold...")
    
    for root, _, files in os.walk(SCAN_DIR):
        for file in files:
            if file.endswith(('.md', '.txt', '.json', '.yaml')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        text = f.read()
                    
                    cursor.execute(
                        "INSERT INTO docs_fts (filepath, filename, content) VALUES (?, ?, ?)",
                        (path, file, text)
                    )
                    indexed_count += 1
                except Exception as e:
                    print(f"Error reading {path}: {e}")
                    
    conn.commit()
    conn.close()
    print(f"Successfully indexed {indexed_count} local files into {DB_NAME}.")

def search_local(query):
    if not os.path.exists(DB_NAME):
        print("Database not found. Please run scan first!")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # FTS5 Match Query with BM25 Ranking
    cursor.execute("""
        SELECT filepath, snippet(docs_fts, 2, '>>> ', ' <<<', '...', 10) as match_snippet
        FROM docs_fts
        WHERE docs_fts MATCH ?
        ORDER BY rank
        LIMIT 5;
    """, (query,))
    
    results = cursor.fetchall()
    conn.close()
    
    print(f"\n--- Local Search Results for: '{query}' ---")
    if not results:
        print("No matches found.")
    for path, snippet in results:
        print(f"\nFile: {path}\nSnippet: {snippet}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--search":
        search_query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "aerocement"
        search_local(search_query)
    else:
        scan_and_index()
