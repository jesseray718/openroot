# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import socket
import sqlite3
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = "content-provenance-v1"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def open_db(path):
    db = sqlite3.connect(path, timeout=30)
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.executescript("""
    CREATE TABLE IF NOT EXISTS events(
        epoch INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id TEXT NOT NULL UNIQUE,
        cell_json TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS artifacts(
        record_id TEXT PRIMARY KEY,
        cell_json TEXT NOT NULL,
        stale INTEGER NOT NULL DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS dependencies(
        parent TEXT NOT NULL REFERENCES artifacts(record_id),
        child TEXT NOT NULL REFERENCES artifacts(record_id),
        PRIMARY KEY(parent, child)
    );
    CREATE TABLE IF NOT EXISTS heads(
        device TEXT NOT NULL,
        path TEXT NOT NULL,
        sha256 TEXT NOT NULL,
        artifact_id TEXT NOT NULL REFERENCES artifacts(record_id),
        PRIMARY KEY(device, path)
    );
    CREATE VIEW IF NOT EXISTS event_cells AS
        SELECT record_id, cell_json FROM events;
    CREATE VIEW IF NOT EXISTS artifact_cells AS
        SELECT record_id, cell_json FROM artifacts;
    """)
    db.commit()
    return db


def event(db, kind, payload):
    record = {
        "schema": VERSION,
        "kind": kind,
        "at": timestamp(),
        "agent": {"host": socket.gethostname(), "pid": os.getpid()},
        "payload": payload,
    }
    previous = db.execute(
        "SELECT record_id FROM events ORDER BY epoch DESC LIMIT 1"
    ).fetchone()
    record["previous_event"] = previous[0] if previous else None
    record_id = hashlib.sha256(canonical(record).encode()).hexdigest()
    cursor = db.execute(
        "INSERT INTO events(record_id, cell_json) VALUES (?, ?)",
        (record_id, canonical(record)),
    )
    return {"epoch": cursor.lastrowid, "event_id": record_id}


def put_artifact(db, kind, identity, parents):
    parents = sorted(set(parents))
    for parent in parents:
        row = db.execute(
            "SELECT stale FROM artifacts WHERE record_id=?", (parent,)
        ).fetchone()
        if row is None or row[0]:
            raise ValueError(f"missing or stale dependency: {parent}")

    record = {
        "schema": VERSION,
        "kind": kind,
        "identity": identity,
        "parents": parents,
    }
    record_id = hashlib.sha256(canonical(record).encode()).hexdigest()
    db.execute(
        "INSERT OR IGNORE INTO artifacts(record_id, cell_json) VALUES (?, ?)",
        (record_id, canonical(record)),
    )
    db.executemany(
        "INSERT OR IGNORE INTO dependencies(parent, child) VALUES (?, ?)",
        [(parent, record_id) for parent in parents],
    )
    return record_id


def invalidate_descendants(db, parent):
    db.execute("""
        WITH RECURSIVE affected(id) AS (
            SELECT child FROM dependencies WHERE parent=?
            UNION
            SELECT d.child
            FROM dependencies d JOIN affected a ON d.parent=a.id
        )
        UPDATE artifacts SET stale=1
        WHERE record_id IN (SELECT id FROM affected)
    """, (parent,))


def signature(s):
    return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def observe(db, filename, device):
    path = os.path.abspath(filename)
    flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
    with os.fdopen(os.open(path, flags), "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise ValueError("only regular files may be observed")
        hasher = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
        after = os.fstat(stream.fileno())
        current = os.stat(path, follow_symlinks=False)
        if signature(before) != signature(after) or signature(after) != signature(current):
            raise ValueError("file changed while being observed")
    sha = hasher.hexdigest()

    db.execute("BEGIN IMMEDIATE")
    try:
        source = put_artifact(
            db, "source-bytes",
            {"sha256": sha, "size_bytes": after.st_size}, []
        )
        old = db.execute(
            "SELECT sha256, artifact_id FROM heads WHERE device=? AND path=?",
            (device, path),
        ).fetchone()
        changed = old is not None and old[0] != sha
        if changed:
            invalidate_descendants(db, old[1])
        db.execute("""
            INSERT INTO heads(device, path, sha256, artifact_id)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(device, path) DO UPDATE SET
                sha256=excluded.sha256, artifact_id=excluded.artifact_id
        """, (device, path, sha, source))
        receipt = event(db, "file-observed", {
            "device": device,
            "path": path,
            "sha256": sha,
            "artifact_id": source,
            "previous_sha256": old[0] if old else None,
            "content_changed": changed,
            "mtime_ns": after.st_mtime_ns,
        })
        db.commit()
    except BaseException:
        db.rollback()
        raise
    return {**receipt, "artifact_id": source, "sha256": sha, "changed": changed}


def derive(db, kind, identity, parents):
    db.execute("BEGIN IMMEDIATE")
    try:
        artifact = put_artifact(db, kind, identity, parents)
        receipt = event(db, "artifact-registered", {"artifact_id": artifact})
        db.commit()
    except BaseException:
        db.rollback()
        raise
    return {**receipt, "artifact_id": artifact}


def run_command(db, argv):
    if not argv:
        raise ValueError("a command is required after --")
    db.execute("BEGIN IMMEDIATE")
    start = event(db, "command-started", {
        "argv": argv,
        "cwd": os.getcwd(),
        "executable_resolved": False,
        "capture_policy": "argv-only; no environment or output capture",
    })
    db.commit()
    try:
        result = subprocess.run(argv, shell=False)
        code, error = result.returncode, None
    except OSError as exc:
        code, error = 127, str(exc)
    db.execute("BEGIN IMMEDIATE")
    finish = event(db, "command-finished", {
        "start_event": start["event_id"],
        "returncode": code,
        "error": error,
    })
    db.commit()
    print(canonical(finish), file=sys.stderr)
    return code if code >= 0 else 128 - code


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init")
    obs = commands.add_parser("observe")
    obs.add_argument("path")
    obs.add_argument("--device", default=socket.gethostname())
    derived = commands.add_parser("derive")
    derived.add_argument("kind")
    derived.add_argument("--identity-json", required=True)
    derived.add_argument("--parent", action="append", default=[])
    commands.add_parser("stale")
    runner = commands.add_parser("run")
    runner.add_argument("argv", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    db = open_db(args.db)
    try:
        if args.command == "init":
            print(canonical({"status": "initialized", "schema": VERSION}))
        elif args.command == "observe":
            print(canonical(observe(db, args.path, args.device)))
        elif args.command == "derive":
            print(canonical(derive(
                db, args.kind, json.loads(args.identity_json), args.parent
            )))
        elif args.command == "stale":
            for record_id, payload in db.execute(
                "SELECT record_id, cell_json FROM artifacts WHERE stale=1"
            ):
                print(canonical({
                    "artifact_id": record_id,
                    "stale": True,
                    "artifact": json.loads(payload),
                }))
        else:
            argv = args.argv
            if argv[:1] == ["--"]:
                argv = argv[1:]
            return run_command(db, argv)
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
