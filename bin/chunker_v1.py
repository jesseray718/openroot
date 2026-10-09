#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
chunker_v1.py - fixed-size chunker; every file becomes a hash tree.

  chunk_sha256 = sha256(chunk bytes)
  root_sha256  = chunk hash if exactly 1 chunk,
                 sha256(b"") if empty file,
                 else sha256(concat of hex chunk hashes in ordinal order)
  file_sha256  = sha256(whole file)   (the object id used everywhere else)

Idempotent: a file whose sha256 is already in file_roots is not re-chunked.
Exit: 0 banked, 2 error.
"""
import argparse
import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/jesse/openroot")
DATA = ROOT / "data"
DB = DATA / "rootkit.db"
MANIFEST = DATA / "chunk_manifest.jsonl"
DEFAULT_CHUNK = 1024 * 1024

EXCLUDE_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules",
                ".cache", ".mypy_cache", ".pytest_cache"}
SKIP_FILES = {DB.resolve(), MANIFEST.resolve()}
SKIP_SUFFIX = (".db-wal", ".db-shm", ".db-journal")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def ensure_schema(con):
    con.executescript("""
    CREATE TABLE IF NOT EXISTS objects (
        sha256 TEXT PRIMARY KEY, size_bytes INTEGER, media_type TEXT,
        created_ts TEXT NOT NULL, origin TEXT, path_hint TEXT);
    CREATE TABLE IF NOT EXISTS object_locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT, sha256 TEXT NOT NULL,
        domain TEXT, relpath TEXT, abs_path TEXT, mtime REAL,
        seen_ts TEXT NOT NULL, source_system TEXT,
        UNIQUE(sha256, domain, relpath, abs_path));
    CREATE TABLE IF NOT EXISTS chunks (
        chunk_sha256 TEXT PRIMARY KEY, parent_sha256 TEXT, ordinal INTEGER,
        byte_start INTEGER, byte_end INTEGER, created_ts TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS file_chunks (
        parent_sha256 TEXT NOT NULL, ordinal INTEGER NOT NULL,
        chunk_sha256 TEXT NOT NULL, byte_start INTEGER, byte_end INTEGER,
        PRIMARY KEY (parent_sha256, ordinal));
    CREATE TABLE IF NOT EXISTS file_roots (
        file_sha256 TEXT PRIMARY KEY, root_sha256 TEXT NOT NULL,
        chunk_count INTEGER NOT NULL, chunk_size INTEGER NOT NULL,
        created_ts TEXT NOT NULL);
    CREATE INDEX IF NOT EXISTS idx_file_chunks_chunk ON file_chunks(chunk_sha256);
    """)
    con.commit()


def chunk_file(path, chunk_size):
    """Single pass: returns (file_sha, root_sha, size, [(chunk_sha, start, end), ...])."""
    fh = hashlib.sha256()
    chunks = []
    start = 0
    with open(path, "rb") as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            fh.update(data)
            chunks.append((sha256_bytes(data), start, start + len(data) - 1))
            start += len(data)
    if not chunks:
        root = sha256_bytes(b"")
    elif len(chunks) == 1:
        root = chunks[0][0]
    else:
        root = sha256_bytes("".join(c[0] for c in chunks).encode("utf-8"))
    return fh.hexdigest(), root, start, chunks


def iter_files(target):
    if target.is_file():
        yield target
        return
    for dirpath, dirnames, filenames in os.walk(target):
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDE_DIRS)
        for fn in sorted(filenames):
            p = Path(dirpath) / fn
            if p.is_symlink() or not p.is_file():
                continue
            if p.resolve() in SKIP_FILES or fn.endswith(SKIP_SUFFIX):
                continue
            yield p


def main():
    ap = argparse.ArgumentParser(description="fixed-size chunker")
    ap.add_argument("target", help="file or directory")
    ap.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK)
    a = ap.parse_args()
    if a.chunk_size < 1:
        print("[ERROR] --chunk-size must be >= 1", file=sys.stderr)
        return 2

    target = Path(a.target).resolve()
    if not target.exists():
        print(f"[ERROR] missing target: {target}", file=sys.stderr)
        return 2

    DATA.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB, timeout=60)
    con.execute("PRAGMA busy_timeout=60000")
    ensure_schema(con)
    base = target if target.is_dir() else target.parent
    domain = base.name

    new = dup = held = 0
    for p in iter_files(target):
        try:
            file_sha, root, size, chunks = chunk_file(p, a.chunk_size)
            mtime = p.stat().st_mtime
        except OSError as e:
            print(f"[held] unreadable {p}: {e}", file=sys.stderr)
            held += 1
            continue

        ts = now()
        rel = str(p.relative_to(base))
        con.execute("INSERT OR IGNORE INTO objects VALUES (?,?,?,?,?,?)",
                    (file_sha, size, "application/octet-stream", ts, "chunker_v1", str(p)))
        con.execute("""INSERT OR IGNORE INTO object_locations
                       (sha256,domain,relpath,abs_path,mtime,seen_ts,source_system)
                       VALUES (?,?,?,?,?,?,?)""",
                    (file_sha, domain, rel, str(p), mtime, ts, "chunker_v1"))

        if con.execute("SELECT 1 FROM file_roots WHERE file_sha256=?", (file_sha,)).fetchone():
            dup += 1
            con.commit()
            continue

        for i, (ch, s, e) in enumerate(chunks):
            con.execute("INSERT OR IGNORE INTO chunks VALUES (?,?,?,?,?,?)",
                        (ch, file_sha, i, s, e, ts))
            con.execute("INSERT OR IGNORE INTO file_chunks VALUES (?,?,?,?,?)",
                        (file_sha, i, ch, s, e))
        con.execute("INSERT OR IGNORE INTO file_roots VALUES (?,?,?,?,?)",
                    (file_sha, root, len(chunks), a.chunk_size, ts))
        con.commit()

        with open(MANIFEST, "a", encoding="utf-8") as m:
            m.write(json.dumps({
                "ts": ts, "path": str(p), "file_sha256": file_sha,
                "root_sha256": root, "size": size, "chunk_size": a.chunk_size,
                "chunks": [c[0] for c in chunks],
            }, sort_keys=True) + "\n")
        new += 1

    con.close()
    print(f"[banked] chunker_v1: new={new} already_chunked={dup} unreadable={held}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
