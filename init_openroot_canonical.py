#!/usr/bin/env python3
"""
OpenRoot Canonical Pod Architecture V1 - Initialization & Bootstrap Script
Target Database: /home/jesse/recovery-evidence/openroot_canonical_v1.db
"""

import os
import sqlite3

DB_PATH = "/home/jesse/recovery-evidence/openroot_canonical_v1.db"

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

-- 1. SOURCES TABLE
CREATE TABLE IF NOT EXISTS sources (
    sha256 TEXT PRIMARY KEY,
    path TEXT NOT NULL,
    source_uri TEXT,
    source_class TEXT NOT NULL,
    source_db TEXT,
    source_rowid INTEGER,
    mime_type TEXT,
    size_bytes INTEGER NOT NULL,
    mtime_epoch INTEGER NOT NULL,
    captured_at TEXT NOT NULL,
    license TEXT,
    revision TEXT,
    ingest_batch_id TEXT NOT NULL
);

-- 2. RECORDS TABLE
CREATE TABLE IF NOT EXISTS records (
    record_sha256 TEXT PRIMARY KEY,
    source_sha256 TEXT NOT NULL,
    record_type TEXT NOT NULL,
    title TEXT,
    canonical_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (source_sha256) REFERENCES sources(sha256)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- 3. CHUNKS TABLE
CREATE TABLE IF NOT EXISTS chunks (
    chunk_sha256 TEXT PRIMARY KEY,
    source_sha256 TEXT NOT NULL,
    record_sha256 TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    char_start INTEGER NOT NULL,
    char_end INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (source_sha256) REFERENCES sources(sha256)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (record_sha256) REFERENCES records(record_sha256)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- 4. EMBEDDINGS TABLE
CREATE TABLE IF NOT EXISTS embeddings (
    sha256 TEXT PRIMARY KEY,
    model TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    vector BLOB NOT NULL,
    embedded_at TEXT NOT NULL,
    FOREIGN KEY (sha256) REFERENCES chunks(chunk_sha256)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

-- 5. CHUNKS FTS (FTS5 External-Content Index)
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    chunk_text,
    content=chunks,
    content_rowid=rowid
);

-- Triggers for FTS synchronization
CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
    INSERT INTO chunks_fts(rowid, chunk_text) VALUES (new.rowid, new.chunk_text);
END;

CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
    INSERT INTO chunks_fts(chunks_fts, rowid, chunk_text) VALUES('delete', old.rowid, old.chunk_text);
END;

CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
    INSERT INTO chunks_fts(chunks_fts, rowid, chunk_text) VALUES('delete', old.rowid, old.chunk_text);
    INSERT INTO chunks_fts(rowid, chunk_text) VALUES (new.rowid, new.chunk_text);
END;

-- 6. QUERIES TABLE
CREATE TABLE IF NOT EXISTS queries (
    query_id TEXT PRIMARY KEY,
    question TEXT NOT NULL,
    question_sha256 TEXT NOT NULL,
    retrieved_chunk_sha256s TEXT NOT NULL,
    answer TEXT NOT NULL,
    answer_sha256 TEXT NOT NULL,
    model TEXT NOT NULL,
    verdict TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- 7. CORRECTIONS TABLE
CREATE TABLE IF NOT EXISTS corrections (
    correction_id TEXT PRIMARY KEY,
    query_id TEXT NOT NULL,
    label TEXT NOT NULL,
    corrected_answer TEXT NOT NULL,
    reviewer TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (query_id) REFERENCES queries(query_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- 8. PATHWAYS TABLE
CREATE TABLE IF NOT EXISTS pathways (
    pathway_sha256 TEXT PRIMARY KEY,
    input_conditions TEXT NOT NULL,
    procedure TEXT NOT NULL,
    evidence_sha256s TEXT NOT NULL,
    verification_status TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- 9. COMMANDS TABLE
CREATE TABLE IF NOT EXISTS commands (
    command_id TEXT PRIMARY KEY,
    command_text TEXT NOT NULL,
    command_sha256 TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT NOT NULL,
    exit_code INTEGER NOT NULL,
    stdout_sha256 TEXT NOT NULL,
    stderr_sha256 TEXT NOT NULL,
    receipt_path TEXT NOT NULL
);

-- 10. MODEL CALLS TABLE
CREATE TABLE IF NOT EXISTS model_calls (
    call_id TEXT PRIMARY KEY,
    command_id TEXT,
    model TEXT NOT NULL,
    prompt_sha256 TEXT NOT NULL,
    answer_sha256 TEXT NOT NULL,
    evidence_command_ids TEXT NOT NULL,
    created_at TEXT NOT NULL,
    verdict TEXT NOT NULL,
    detail TEXT,
    FOREIGN KEY (command_id) REFERENCES commands(command_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_records_source ON records(source_sha256);
CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_sha256);
CREATE INDEX IF NOT EXISTS idx_chunks_record ON chunks(record_sha256);
CREATE INDEX IF NOT EXISTS idx_model_calls_command ON model_calls(command_id);

-- Pod Views
CREATE VIEW IF NOT EXISTS pod_view_sources AS SELECT * FROM sources;

CREATE VIEW IF NOT EXISTS pod_view_records AS 
SELECT r.*, s.source_class, s.source_uri, s.path AS source_path 
FROM records r JOIN sources s ON r.source_sha256 = s.sha256;

CREATE VIEW IF NOT EXISTS pod_view_chunks AS 
SELECT c.chunk_sha256, c.source_sha256, c.record_sha256, c.chunk_index, c.chunk_text, 
       c.char_start, c.char_end, e.model AS embedding_model, e.dimensions, 
       CASE WHEN e.sha256 IS NOT NULL THEN 1 ELSE 0 END AS has_embedding, s.source_class
FROM chunks c JOIN sources s ON c.source_sha256 = s.sha256 LEFT JOIN embeddings e ON c.chunk_sha256 = e.sha256;
"""

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    print(f"Initializing OpenRoot canonical database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
    print("Database schema successfully created with foreign keys, FTS5 triggers, and pod views enabled.")

if __name__ == "__main__":
    init_db()
