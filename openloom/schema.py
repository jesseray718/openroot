import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
  sha256 TEXT PRIMARY KEY,
  source_uri TEXT,
  source_class TEXT NOT NULL,
  source_db TEXT,
  source_rowid INTEGER,
  mime_type TEXT,
  size_bytes INTEGER,
  mtime_epoch INTEGER,
  captured_at TEXT NOT NULL,
  ingest_batch_id TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS records (
  record_sha256 TEXT PRIMARY KEY,
  source_sha256 TEXT NOT NULL REFERENCES sources(sha256),
  record_type TEXT NOT NULL,
  title TEXT,
  canonical_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chunks (
  chunk_sha256 TEXT PRIMARY KEY,
  source_sha256 TEXT NOT NULL REFERENCES sources(sha256),
  record_sha256 TEXT REFERENCES records(record_sha256),
  chunk_index INTEGER NOT NULL,
  chunk_text TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
  chunk_text,
  content='chunks',
  content_rowid='rowid'
);

CREATE TABLE IF NOT EXISTS embeddings (
  sha256 TEXT PRIMARY KEY,
  model TEXT NOT NULL,
  dimensions INTEGER NOT NULL,
  vector TEXT NOT NULL,
  embedded_at TEXT NOT NULL,
  FOREIGN KEY (sha256) REFERENCES chunks(chunk_sha256)
);

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

CREATE TABLE IF NOT EXISTS corrections (
  correction_id TEXT PRIMARY KEY,
  query_id TEXT NOT NULL REFERENCES queries(query_id),
  label TEXT NOT NULL,
  corrected_answer TEXT,
  reviewer TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pathways (
  pathway_sha256 TEXT PRIMARY KEY,
  input_conditions TEXT NOT NULL,
  procedure TEXT NOT NULL,
  evidence_sha256s TEXT NOT NULL,
  verification_status TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
  INSERT INTO chunks_fts(rowid, chunk_text)
  VALUES (new.rowid, new.chunk_text);
END;

CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
  INSERT INTO chunks_fts(chunks_fts, rowid, chunk_text)
  VALUES ('delete', old.rowid, old.chunk_text);
END;

CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
  INSERT INTO chunks_fts(chunks_fts, rowid, chunk_text)
  VALUES ('delete', old.rowid, old.chunk_text);
  INSERT INTO chunks_fts(rowid, chunk_text)
  VALUES (new.rowid, new.chunk_text);
END;
"""

def init_pod(path):
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA)
    connection.commit()
    connection.close()
