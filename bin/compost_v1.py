#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
[COMPOSTV1] OpenRoot waste-stream transmutation ledger.

Registers candidates without deleting anything, extracts conservative keypoints,
indexes records with SQLite FTS5 when available, and ranks release candidates.
No delete operation exists in this utility.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path("/home/jesse/openroot")
DATA = REPO / "data"
DB = DATA / "compost_v1.db"
TAG = "[COMPOSTV1]"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def connect() -> sqlite3.Connection:
    DATA.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS candidates (
            candidate_id TEXT PRIMARY KEY,
            path TEXT NOT NULL,
            reason TEXT NOT NULL,
            visibility REAL NOT NULL DEFAULT 1.0,
            reach REAL NOT NULL DEFAULT 1.0,
            sysfit REAL NOT NULL DEFAULT 1.0,
            floor_weight REAL NOT NULL DEFAULT 1.0,
            effort REAL NOT NULL DEFAULT 1.0,
            score REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'registered_no_delete',
            keypoints TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    con.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS compost_fts
        USING fts5(candidate_id UNINDEXED, path, reason, keypoints)
        """
    )
    con.commit()
    return con


def keypoints(path: Path, limit: int = 12) -> str:
    if not path.is_file():
        return "path unavailable; metadata-only registration"
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return f"unreadable: {exc}"
    found = []
    for line in raw.splitlines():
        clean = line.strip()
        if re.match(r"^(#{1,6}\s+|[A-Z][A-Z0-9 _:-]{5,}$)", clean):
            found.append(clean[:240])
        if len(found) >= limit:
            break
    if found:
        return "\n".join(found)
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]{2,}", raw[:12000])
    return " ".join(words[:80]) if words else "no extractable text"


def score(v: float, r: float, s: float, f: float, e: float) -> float:
    if e <= 0:
        raise ValueError("effort must be greater than zero")
    return (v * r * s * f) / math.pow(e, 1.5)


def register(args: argparse.Namespace) -> int:
    con = connect()
    candidate_path = Path(args.path)
    resolved = str(candidate_path.resolve(strict=False))
    points = keypoints(candidate_path)
    value = score(args.visibility, args.reach, args.sysfit, args.floor_weight, args.effort)
    cid = sha256_text(f"{resolved}\0{args.reason}")[:32]
    timestamp = now()
    con.execute(
        """
        INSERT INTO candidates(
            candidate_id,path,reason,visibility,reach,sysfit,floor_weight,
            effort,score,status,keypoints,created_at,updated_at
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(candidate_id) DO UPDATE SET
            visibility=excluded.visibility,
            reach=excluded.reach,
            sysfit=excluded.sysfit,
            floor_weight=excluded.floor_weight,
            effort=excluded.effort,
            score=excluded.score,
            keypoints=excluded.keypoints,
            updated_at=excluded.updated_at
        """,
        (
            cid, resolved, args.reason, args.visibility, args.reach, args.sysfit,
            args.floor_weight, args.effort, value, "registered_no_delete",
            points, timestamp, timestamp,
        ),
    )
    con.execute("DELETE FROM compost_fts WHERE candidate_id=?", (cid,))
    con.execute(
        "INSERT INTO compost_fts(candidate_id,path,reason,keypoints) VALUES(?,?,?,?)",
        (cid, resolved, args.reason, points),
    )
    con.commit()
    print(f"[banked] candidate_id={cid}")
    print(f"[banked] score={value:.6f}")
    print("[held] registered_no_delete; human review required before any external cleanup")
    return 0


def listing(_: argparse.Namespace) -> int:
    con = connect()
    rows = con.execute(
        """
        SELECT candidate_id,path,reason,round(score,6),status,updated_at
        FROM candidates ORDER BY score DESC, updated_at DESC
        """
    ).fetchall()
    for row in rows:
        print("\t".join(str(value) for value in row))
    print(f"[banked] candidates={len(rows)}")
    return 0


def search(args: argparse.Namespace) -> int:
    con = connect()
    rows = con.execute(
        """
        SELECT candidate_id,path,reason,keypoints
        FROM compost_fts
        WHERE compost_fts MATCH ?
        LIMIT ?
        """,
        (args.query, args.limit),
    ).fetchall()
    for row in rows:
        print(json.dumps({"id": row[0], "path": row[1], "reason": row[2], "keypoints": row[3]}, ensure_ascii=False))
    print(f"[banked] matches={len(rows)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="compost_v1.py")
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("register")
    add.add_argument("path")
    add.add_argument("reason")
    add.add_argument("--visibility", type=float, default=1.0)
    add.add_argument("--reach", type=float, default=1.0)
    add.add_argument("--sysfit", type=float, default=1.0)
    add.add_argument("--floor-weight", type=float, default=1.0)
    add.add_argument("--effort", type=float, default=1.0)
    add.set_defaults(func=register)
    ls = sub.add_parser("list")
    ls.set_defaults(func=listing)
    find = sub.add_parser("search")
    find.add_argument("query")
    find.add_argument("--limit", type=int, default=20)
    find.set_defaults(func=search)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
