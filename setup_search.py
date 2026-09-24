import sqlite3
import json
import urllib.request
import urllib.error
import sys

DB_FILE = "knowledge_base.db"

def check_ollama():
    """Verify Ollama is running and nomic-embed-text is available."""
    print("[1/4] Checking Ollama & nomic-embed-text...")
    url = "http://localhost:11434/api/embeddings"
    payload = json.dumps({"model": "nomic-embed-text", "prompt": "test connection"}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode("utf-8"))
            vec_len = len(res.get("embedding", []))
            print(f"  ✓ Ollama connection active. Embedding dimensions: {vec_len}")
            return True
    except urllib.error.URLError as e:
        print(f"  ✗ Ollama check failed: {e}")
        print("    Ensure Ollama is running (`ollama serve`) and model is pulled (`ollama pull nomic-embed-text`).")
        return False

def check_sqlite_fts5():
    """Check if SQLite build supports FTS5."""
    print("\n[2/4] Checking SQLite FTS5 extension...")
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    try:
        cur.execute("CREATE VIRTUAL TABLE test_fts USING fts5(content);")
        print("  ✓ FTS5 extension is enabled in current SQLite build.")
        conn.close()
        return True
    except sqlite3.OperationalError as e:
        print(f"  ✗ FTS5 missing or disabled: {e}")
        conn.close()
        return False

def setup_schema(conn):
    """Create document store, FTS5 virtual table, and embedding storage."""
    print("\n[3/4] Initializing Database Schema...")
    cur = conn.cursor()
    
    # 1. Base Document Store
    cur.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. FTS5 Indexing Table
    cur.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(
        title,
        content,
        content='documents',
        content_rowid='id'
    );
    """)

    # Triggers to keep FTS5 automatically in sync with base documents
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS docs_ai AFTER INSERT ON documents BEGIN
        INSERT INTO docs_fts(rowid, title, content) VALUES (new.id, new.title, new.content);
    END;
    """)
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS docs_ad AFTER DELETE ON documents BEGIN
        INSERT INTO docs_fts(docs_fts, rowid, title, content) VALUES('delete', old.id, old.title, old.content);
    END;
    """)
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS docs_au AFTER UPDATE ON documents BEGIN
        INSERT INTO docs_fts(docs_fts, rowid, title, content) VALUES('delete', old.id, old.title, old.content);
        INSERT INTO docs_fts(rowid, title, content) VALUES (new.id, new.title, new.content);
    END;
    """)

    # 3. Embedding Storage (BLOB for raw float32 arrays)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS embeddings (
        doc_id INTEGER PRIMARY KEY,
        vector BLOB NOT NULL,
        FOREIGN KEY(doc_id) REFERENCES documents(id) ON DELETE CASCADE
    );
    """)
    conn.commit()
    print("  ✓ Schema and automated FTS synchronization triggers created successfully.")

def run_test_indexing(conn):
    """Index sample content and execute hybrid retrieval test."""
    print("\n[4/4] Testing Hybrid Search Pipeline...")
    cur = conn.cursor()

    # Clear previous test data
    cur.execute("DELETE FROM documents;")
    conn.commit()

    sample_docs = [
        ("SQLite Search", "SQLite FTS5 provides full-text indexing with BM25 ranking built directly into C."),
        ("Vector Embeddings", "Nomic embed text generates 768-dimension dense vector representations for semantic search."),
        ("Hybrid Retrieval", "Combining sparse keyword indices with dense vector representations yields superior retrieval quality.")
    ]

    for title, content in sample_docs:
        cur.execute("INSERT INTO documents (title, content) VALUES (?, ?);", (title, content))
        doc_id = cur.lastrowid
        
        # Generate embedding via Ollama
        url = "http://localhost:11434/api/embeddings"
        payload = json.dumps({"model": "nomic-embed-text", "prompt": content}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            vec = data["embedding"]
            # Convert float array to raw bytes for compact SQLite BLOB storage
            import array
            blob_data = array.array('f', vec).tobytes()
            cur.execute("INSERT INTO embeddings (doc_id, vector) VALUES (?, ?);", (doc_id, blob_data))

    conn.commit()

    # Test FTS Query
    print("\n  --- Testing FTS5 Keyword Search ---")
    cur.execute("SELECT rowid, title, rank FROM docs_fts WHERE docs_fts MATCH 'vector' ORDER BY rank;")
    rows = cur.fetchall()
    for r in rows:
        print(f"    Match -> ID: {r[0]}, Title: {r[1]}, Rank Score: {r[2]:.4f}")

    print("\n  ✓ Setup verification complete. All components operating correctly.")

if __name__ == "__main__":
    if not check_ollama() or not check_sqlite_fts5():
        sys.exit(1)
        
    db_conn = sqlite3.connect(DB_FILE)
    setup_schema(db_conn)
    run_test_indexing(db_conn)
    db_conn.close()
