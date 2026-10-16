#!/usr/bin/env python3
"""
OpenRoot Canonical Pod Architecture V1 - Phase 2 Ingestion Script
Target Database: /home/jesse/recovery-evidence/openroot_canonical_v1.db
Objective: Ingest the first 5 local documents into the canonical store with full provenance.
"""

import os
import sqlite3
import hashlib
import json
from datetime import datetime, timezone

DB_PATH = "/home/jesse/recovery-evidence/openroot_canonical_v1.db"
BATCH_ID = "bootstrap-5-docs-v1"

# Target local documents to bootstrap (adjust paths if needed to match your workspace)
TARGET_DOCS = [
    "/home/jesse/openroot/docs/CANONICAL_POD_ARCHITECTURE_V1.md",
    # Add other core local text/markdown documents here if available, 
    # ensuring fallback creation if specific files are test-simulated.
]

def compute_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

def run_phase2_ingestion():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Canonical database not found at {DB_PATH}. Run Phase 1 initialization first.")

    print(f"Connecting to canonical database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    
    cursor = conn.cursor()
    captured_at = datetime.now(timezone.utc).isoformat()

    # Fallback simulation if paths are template references, or load actual files if present
    documents_to_process = [
        {"path": "/home/jesse/openroot/docs/CANONICAL_POD_ARCHITECTURE_V1.md", "class": "architecture_doc"},
    ]

    # Discover any markdown files in openroot docs if they exist
    docs_dir = "/home/jesse/openroot/docs"
    if os.path.exists(docs_dir):
        for root, _, files in os.walk(docs_dir):
            for file in files:
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    if not any(d["path"] == full_path for d in documents_to_process):
                        documents_to_process.append({"path": full_path, "class": "local_markdown"})

    print(f"Found {len(documents_to_process)} candidate source documents for ingestion.")

    try:
        conn.execute("BEGIN TRANSACTION;")
        
        for doc in documents_to_process:
            path = doc["path"]
            if not os.path.exists(path):
                print(f"Skipping missing path: {path}")
                continue

            with open(path, "rb") as f:
                content_bytes = f.read()

            file_hash = compute_sha256(content_bytes)
            file_size = len(content_bytes)
            mtime = int(os.path.getmtime(path))
            
            # 1. Insert into sources
            cursor.execute("""
                INSERT OR IGNORE INTO sources (
                    sha256, path, source_uri, source_class, source_db, source_rowid,
                    mime_type, size_bytes, mtime_epoch, captured_at, license, revision, ingest_batch_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                file_hash, path, f"file://{path}", doc["class"], None, None,
                "text/markdown", file_size, mtime, captured_at, "Internal", "v1", BATCH_ID
            ))

            # 2. Insert into records
            record_json = json.dumps({"path": path, "size": file_size, "class": doc["class"]})
            record_sha256 = compute_sha256(record_json.encode("utf-8"))
            
            cursor.execute("""
                INSERT OR IGNORE INTO records (
                    record_sha256, source_sha256, record_type, title, canonical_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                record_sha256, file_hash, "document_normalization", os.path.basename(path), record_json, captured_at
            ))

            # 3. Simple paragraph/block chunking
            text_content = content_bytes.decode("utf-8", errors="ignore")
            chunks = [c.strip() for c in text_content.split("\n\n") if c.strip()]
            
            for idx, chunk_text in enumerate(chunks):
                chunk_sha256 = compute_sha256(chunk_text.encode("utf-8"))
                char_start = text_content.find(chunk_text)
                char_end = char_start + len(chunk_text)

                cursor.execute("""
                    INSERT OR IGNORE INTO chunks (
                        chunk_sha256, source_sha256, record_sha256, chunk_index,
                        chunk_text, char_start, char_end, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chunk_sha256, file_hash, record_sha256, idx,
                    chunk_text, char_start, char_end, captured_at
                ))

            print(f"Successfully ingested source: {path} [SHA256: {file_hash[:12]}...] with {len(chunks)} chunks.")

        conn.commit()
        print("Phase 2 incremental ingestion completed successfully and committed atomically.")

    except Exception as e:
        conn.rollback()
        print(f"Ingestion failed, transaction rolled back: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_phase2_ingestion()
