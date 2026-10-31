#!/usr/bin/env python3
import argparse
import codecs
import csv
import hashlib
import json
import os
import socket
import sqlite3
import stat
import sys
import tempfile
from datetime import datetime, timezone

from blake3 import blake3

VIRTUAL_ROOTS = ("/proc", "/sys", "/dev")
SCHEMA = """
CREATE TABLE IF NOT EXISTS cells (
    id INTEGER PRIMARY KEY,
    sha256 TEXT NOT NULL UNIQUE,
    cell_json TEXT NOT NULL
);
CREATE VIRTUAL TABLE IF NOT EXISTS content_fts USING fts5(
    body,
    tokenize='unicode61'
);
CREATE TABLE IF NOT EXISTS errors (
    observed_at TEXT NOT NULL,
    path TEXT NOT NULL,
    error TEXT NOT NULL
);
"""


def now():
    return datetime.now(timezone.utc).isoformat()


def connect(path):
    db = sqlite3.connect(path)
    db.execute("PRAGMA journal_mode=WAL")
    db.executescript(SCHEMA)
    db.commit()
    return db


def within(path, root):
    return path == root or path.startswith(root + os.sep)


def fingerprint(s):
    return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def decode_text(snapshot, max_bytes):
    snapshot.seek(0, os.SEEK_END)
    size = snapshot.tell()
    if size > max_bytes:
        return None, "text_size_limit"
    snapshot.seek(0)
    data = snapshot.read()

    if data.startswith((codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE)):
        encoding = "utf-32"
    elif data.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
        encoding = "utf-16"
    else:
        encoding = "utf-8-sig"

    try:
        text = data.decode(encoding, errors="strict")
    except UnicodeError:
        return None, "needs_extractor"

    if any(ord(c) < 32 and c not in "\t\n\r\f" for c in text):
        return None, "needs_extractor"
    return text, "indexed_text"


def read_verified(path, max_bytes):
    flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)

    with os.fdopen(fd, "rb") as source, tempfile.TemporaryFile() as snapshot:
        before = os.fstat(source.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise ValueError("not a regular file")

        sha = hashlib.sha256()
        b3 = blake3()
        total = 0
        for block in iter(lambda: source.read(1024 * 1024), b""):
            sha.update(block)
            b3.update(block)
            snapshot.write(block)
            total += len(block)

        after = os.fstat(source.fileno())
        current = os.stat(path, follow_symlinks=False)
        if (
            fingerprint(before) != fingerprint(after)
            or fingerprint(after) != fingerprint(current)
            or total != after.st_size
        ):
            raise ValueError("file changed during reading; retry later")

        text, status = decode_text(snapshot, max_bytes)
        return sha.hexdigest(), b3.hexdigest(), after, text, status


def save_cell(db, path, device, result):
    sha, b3, s, text, status = result
    observed = now()
    location = {
        "device": device,
        "filepath": path,
        "mtime_ns": s.st_mtime_ns,
        "metadata": {
            "mode": s.st_mode,
            "uid": s.st_uid,
            "gid": s.st_gid,
            "inode": s.st_ino,
            "filesystem_device": s.st_dev,
        },
        "last_verified_at": observed,
    }

    with db:
        # Remove this location from any previously observed content identity.
        previous = db.execute(
            """SELECT DISTINCT c.id, c.cell_json
               FROM cells AS c, json_each(c.cell_json, '$.locations') AS loc
               WHERE json_extract(loc.value, '$.device') = ?
                 AND json_extract(loc.value, '$.filepath') = ?
                 AND c.sha256 <> ?""",
            (device, path, sha),
        ).fetchall()
        for row_id, payload in previous:
            old = json.loads(payload)
            old["locations"] = [
                item for item in old["locations"]
                if (item["device"], item["filepath"]) != (device, path)
            ]
            db.execute(
                "UPDATE cells SET cell_json=? WHERE id=?",
                (json.dumps(old, ensure_ascii=True), row_id),
            )

        row = db.execute(
            "SELECT id, cell_json FROM cells WHERE sha256=?", (sha,)
        ).fetchone()

        if row:
            row_id, payload = row
            cell = json.loads(payload)
            if cell["blake3"] != b3:
                raise ValueError("hash identity conflict; no update committed")
        else:
            cell = {
                "sha256": sha,
                "blake3": b3,
                "size_bytes": s.st_size,
                "metadata": {},
                "locations": [],
            }
            row_id = db.execute(
                "INSERT INTO cells(sha256, cell_json) VALUES (?, '{}')",
                (sha,),
            ).lastrowid

        cell["locations"] = [
            item for item in cell["locations"]
            if (item["device"], item["filepath"]) != (device, path)
        ]
        cell["locations"].append(location)
        cell["content_verified_at"] = observed
        cell["text_extraction"] = {"status": status, "extractor": "builtin-text-v1"}

        db.execute(
            "UPDATE cells SET cell_json=? WHERE id=?",
            (json.dumps(cell, ensure_ascii=True), row_id),
        )
        db.execute("DELETE FROM content_fts WHERE rowid=?", (row_id,))
        if text is not None:
            db.execute(
                "INSERT INTO content_fts(rowid, body) VALUES (?, ?)",
                (row_id, text),
            )


def scan(db, args):
    db_path = os.path.realpath(args.db)
    excluded = {db_path, db_path + "-wal", db_path + "-shm"}
    excluded.update(os.path.realpath(p) for p in args.exclude)
    count = 0

    def blocked(path):
        return (
            any(within(path, root) for root in VIRTUAL_ROOTS)
            or any(within(path, root) for root in excluded)
        )

    def log_error(path, error):
        with db:
            db.execute(
                "INSERT INTO errors VALUES (?, ?, ?)",
                (now(), path, str(error)),
            )
        print(f"ERROR {path}: {error}", file=sys.stderr)

    for root_arg in args.roots:
        root = os.path.abspath(root_arg)
        if os.path.islink(root) or blocked(root):
            raise ValueError(f"excluded or symlink root: {root}")
        if not os.path.exists(root):
            raise ValueError(f"missing root: {root}")

        if os.path.isfile(root):
            walks = [(os.path.dirname(root), [], [os.path.basename(root)])]
        else:
            walks = os.walk(
                root, followlinks=False,
                onerror=lambda error: log_error(error.filename or root, error),
            )

        for directory, dirs, files in walks:
            dirs[:] = [
                name for name in dirs
                if not blocked(os.path.join(directory, name))
                and not os.path.islink(os.path.join(directory, name))
            ]
            for name in files:
                path = os.path.join(directory, name)
                if blocked(path) or os.path.islink(path):
                    continue
                try:
                    if not stat.S_ISREG(os.lstat(path).st_mode):
                        continue
                    result = read_verified(path, args.max_text_mib * 1024**2)
                    save_cell(db, path, args.device, result)
                    count += 1
                    if count % 100 == 0:
                        print(f"{count} files processed", file=sys.stderr)
                except (OSError, ValueError) as error:
                    log_error(path, error)

    print(f"{count} files processed", file=sys.stderr)


def search(db, args):
    if args.fts:
        expression = args.query
    else:
        words = args.query.split()
        if not words:
            raise ValueError("empty search")
        expression = " AND ".join(
            '"' + word.replace('"', '""') + '"' for word in words
        )

    rows = db.execute(
        """SELECT c.cell_json, bm25(content_fts) AS score
           FROM content_fts
           JOIN cells AS c ON c.id = content_fts.rowid
           WHERE content_fts MATCH ?
             AND json_array_length(c.cell_json, '$.locations') > 0
           ORDER BY score
           LIMIT ?""",
        (expression, args.limit),
    )
    for payload, score in rows:
        print(json.dumps(
            {"bm25": score, "cell": json.loads(payload)},
            ensure_ascii=True,
        ))


def export_matrix(db, args):
    # Exclusive creation prevents accidental replacement of an existing export.
    with open(args.output, "x", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            row[0] for row in db.execute(
                "SELECT sha256 FROM cells ORDER BY sha256"
            )
        )
        writer.writerow(
            row[0] for row in db.execute(
                "SELECT cell_json FROM cells ORDER BY sha256"
            )
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    commands = parser.add_subparsers(dest="command", required=True)

    scan_parser = commands.add_parser("scan")
    scan_parser.add_argument("roots", nargs="+")
    scan_parser.add_argument("--device", default=socket.gethostname())
    scan_parser.add_argument("--exclude", action="append", default=[])
    scan_parser.add_argument("--max-text-mib", type=int, default=64)

    search_parser = commands.add_parser("search")
    search_parser.add_argument("query")
    search_parser.add_argument("--limit", type=int, default=50)
    search_parser.add_argument("--fts", action="store_true")

    export_parser = commands.add_parser("export-matrix")
    export_parser.add_argument("output")

    args = parser.parse_args()
    db = connect(args.db)
    try:
        if args.command == "scan":
            scan(db, args)
        elif args.command == "search":
            search(db, args)
        else:
            export_matrix(db, args)
    finally:
        db.close()


if __name__ == "__main__":
    main()
