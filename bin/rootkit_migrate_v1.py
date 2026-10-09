#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
rootkit_migrate_v1.py
Additive, idempotent schema unification for hash-spine pipeline.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/jesse/openroot")
DATA = ROOT / "data"

DBS = {
    "universal": DATA / "universal_doc_ledger.db",
    "file_ledger": DATA / "file_ledger.db",
    "lumo_ingest": DATA / "lumo_ingest.db",
    "provenance": DATA / "provenance.db",
    "rootkit": DATA / "rootkit.db",
}

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def ensure_dir():
    DATA.mkdir(parents=True, exist_ok=True)

def col_exists(con, table, col):
    rows = con.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r[1] == col for r in rows)

def add_col_if_missing(con, table, col_def):
    col = col_def.split()[0]
    if not col_exists(con, table, col):
        con.execute(f"ALTER TABLE {table} ADD COLUMN {col_def}")

def migrate_rootkit_db(path: Path):
    con = sqlite3.connect(path)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA busy_timeout=60000")

    con.execute("""
    CREATE TABLE IF NOT EXISTS objects (
        sha256 TEXT PRIMARY KEY,
        size_bytes INTEGER,
        media_type TEXT,
        created_ts TEXT NOT NULL,
        origin TEXT,
        path_hint TEXT
    )
    """)
    con.execute("""
    CREATE TABLE IF NOT EXISTS object_locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sha256 TEXT NOT NULL,
        domain TEXT,
        relpath TEXT,
        abs_path TEXT,
        mtime REAL,
        seen_ts TEXT NOT NULL,
        source_system TEXT,
        UNIQUE(sha256, domain, relpath, abs_path),
        FOREIGN KEY (sha256) REFERENCES objects(sha256)
    )
    """)
    con.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
        chunk_sha256 TEXT PRIMARY KEY,
        parent_sha256 TEXT,
        ordinal INTEGER,
        byte_start INTEGER,
        byte_end INTEGER,
        created_ts TEXT NOT NULL,
        FOREIGN KEY (parent_sha256) REFERENCES objects(sha256)
    )
    """)
    con.execute("""
    CREATE TABLE IF NOT EXISTS index_registry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sha256 TEXT NOT NULL,
        index_kind TEXT NOT NULL,
        index_ref TEXT NOT NULL,
        indexed_ts TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'ok',
        UNIQUE(sha256, index_kind, index_ref),
        FOREIGN KEY (sha256) REFERENCES objects(sha256)
    )
    """)
    con.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        job_id TEXT PRIMARY KEY,
        spec_sha256 TEXT,
        input_sha256 TEXT NOT NULL,
        output_sha256 TEXT,
        toolchain TEXT,
        status TEXT NOT NULL,
        started_ts TEXT,
        ended_ts TEXT,
        notes TEXT,
        FOREIGN KEY (input_sha256) REFERENCES objects(sha256),
        FOREIGN KEY (output_sha256) REFERENCES objects(sha256)
    )
    """)
    con.execute("""
    CREATE TABLE IF NOT EXISTS attestations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT NOT NULL,
        meter_kind TEXT NOT NULL,
        joules_human REAL,
        joules_useful REAL,
        k_delta REAL,
        measured_ts TEXT NOT NULL,
        verifier TEXT,
        note TEXT,
        FOREIGN KEY (job_id) REFERENCES jobs(job_id)
    )
    """)
    con.execute("""
    CREATE TABLE IF NOT EXISTS mints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT NOT NULL,
        block_hash TEXT,
        chain_name TEXT NOT NULL,
        tx_ref TEXT,
        minted_ts TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'ok',
        UNIQUE(job_id, chain_name),
        FOREIGN KEY (job_id) REFERENCES jobs(job_id)
    )
    """)
    con.execute("""
    CREATE TABLE IF NOT EXISTS publish_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        output_sha256 TEXT NOT NULL,
        channel TEXT NOT NULL,
        ref TEXT,
        published_ts TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'ok',
        FOREIGN KEY (output_sha256) REFERENCES objects(sha256)
    )
    """)
    con.execute("""
    CREATE TABLE IF NOT EXISTS migration_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        migration_name TEXT NOT NULL,
        applied_ts TEXT NOT NULL,
        note TEXT
    )
    """)

    con.execute("CREATE INDEX IF NOT EXISTS idx_object_locations_sha ON object_locations(sha256)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_chunks_parent ON chunks(parent_sha256)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_attest_job ON attestations(job_id)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_mints_job ON mints(job_id)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_publish_sha ON publish_events(output_sha256)")

    con.execute(
        "INSERT INTO migration_log(migration_name, applied_ts, note) VALUES (?,?,?)",
        ("rootkit_migrate_v1", now(), "additive baseline schema")
    )

    con.commit()
    con.close()

def migrate_universal_doc_ledger(path: Path):
    if not path.exists():
        return
    con = sqlite3.connect(path)
    tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "docs" in tables:
        add_col_if_missing(con, "docs", "origin TEXT")
        add_col_if_missing(con, "docs", "content_sha256 TEXT")
        add_col_if_missing(con, "docs", "ingest_ts TEXT")
        con.execute("CREATE INDEX IF NOT EXISTS idx_docs_sha256 ON docs(sha256)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_docs_content_sha256 ON docs(content_sha256)")
    con.commit()
    con.close()

def migrate_file_ledger(path: Path):
    if not path.exists():
        return
    con = sqlite3.connect(path)
    tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "files" in tables:
        add_col_if_missing(con, "files", "origin TEXT")
        add_col_if_missing(con, "files", "first_seen_ts TEXT")
        con.execute("CREATE INDEX IF NOT EXISTS idx_files_sha256 ON files(sha256)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_files_domain_relpath ON files(domain, relpath)")
    con.commit()
    con.close()

def migrate_lumo_ingest(path: Path):
    if not path.exists():
        return
    con = sqlite3.connect(path)
    tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "ingested" in tables:
        add_col_if_missing(con, "ingested", "origin TEXT")
        add_col_if_missing(con, "ingested", "size_bytes INTEGER")
        con.execute("CREATE INDEX IF NOT EXISTS idx_ingested_sha256 ON ingested(sha256)")
    con.commit()
    con.close()

def migrate_provenance(path: Path):
    if not path.exists():
        return
    con = sqlite3.connect(path)
    con.execute("""
    CREATE TABLE IF NOT EXISTS migration_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        migration_name TEXT NOT NULL,
        applied_ts TEXT NOT NULL,
        note TEXT
    )
    """)
    con.execute(
        "INSERT INTO migration_log(migration_name, applied_ts, note) VALUES (?,?,?)",
        ("rootkit_migrate_v1", now(), "non-destructive stamp")
    )
    con.commit()
    con.close()

def seed_rootkit_from_file_ledger(rootkit_db: Path, file_db: Path):
    if not file_db.exists():
        return
    src = sqlite3.connect(file_db)
    dst = sqlite3.connect(rootkit_db)
    tables = {r[0] for r in src.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "files" not in tables:
        src.close(); dst.close()
        return

    rows = src.execute("""
        SELECT domain, relpath, size, mtime, sha256
        FROM files
        WHERE sha256 IS NOT NULL AND sha256 != '' AND sha256 != '-unreadable-'
    """).fetchall()

    ts = now()
    for domain, relpath, size, mtime, sha in rows:
        dst.execute("""
            INSERT OR IGNORE INTO objects(sha256, size_bytes, media_type, created_ts, origin, path_hint)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sha, size, "application/octet-stream", ts, "file_ledger_v2", relpath))
        dst.execute("""
            INSERT OR IGNORE INTO object_locations
            (sha256, domain, relpath, abs_path, mtime, seen_ts, source_system)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (sha, domain, relpath, None, mtime, ts, "file_ledger_v2"))
    dst.commit()
    src.close()
    dst.close()

def main():
    ensure_dir()
    print(f"[ROOTKIT-MIGRATE] start {now()}")
    migrate_rootkit_db(DBS["rootkit"])
    print(f"[banked] rootkit schema: {DBS['rootkit']}")

    migrate_universal_doc_ledger(DBS["universal"])
    print(f"[banked] universal_doc_ledger additive migration checked")

    migrate_file_ledger(DBS["file_ledger"])
    print(f"[banked] file_ledger additive migration checked")

    migrate_lumo_ingest(DBS["lumo_ingest"])
    print(f"[banked] lumo_ingest additive migration checked")

    migrate_provenance(DBS["provenance"])
    print(f"[banked] provenance additive migration checked")

    seed_rootkit_from_file_ledger(DBS["rootkit"], DBS["file_ledger"])
    print(f"[banked] rootkit seed from file_ledger complete")

    print(f"[ROOTKIT-MIGRATE] done {now()}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
