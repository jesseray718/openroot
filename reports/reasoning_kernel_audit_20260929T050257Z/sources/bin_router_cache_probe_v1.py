#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
Read-only OpenRoot route-cache probe.

Uses only the discovered existing route_cache.db:
  route_cache(key, query, route, model, response, hits, provenance, ts)
  route_cache_fts(query, response)

No database creation.
No schema mutation.
No cache-hit counter update.
No model dispatch.
No network access.
No Git action.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

CANARY = "[ROUTER-CACHE-PROBE-V1]"
DEFAULT_ROOT = Path(os.environ.get("ROOT", str(Path.home() / "openroot"))).expanduser()
DEFAULT_DB = DEFAULT_ROOT / "data" / "route_cache.db"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def emit(event: dict) -> None:
    print(json.dumps(event, sort_keys=True, separators=(",", ":")))


def fail(reason: str, *, query: str = "") -> int:
    emit(
        {
            "canary": CANARY,
            "status": reason,
            "query": query,
            "timestamp": utc_now(),
        }
    )
    print(f"{CANARY} [exit=1]", file=sys.stderr)
    return 1


def open_readonly(db_path: Path) -> sqlite3.Connection:
    if not db_path.is_file():
        raise FileNotFoundError(str(db_path))

    uri = f"file:{quote(str(db_path))}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def normalize_query(value: str) -> str:
    return " ".join(value.strip().split())


def fts_terms(query: str) -> str:
    terms = [
        token
        for token in query.replace('"', " ").split()
        if any(char.isalnum() for char in token)
    ]
    return " OR ".join(f'"{term}"' for term in terms[:12])


def exact_lookup(conn: sqlite3.Connection, query: str) -> dict | None:
    row = conn.execute(
        """
        SELECT key, query, route, model, response, hits, provenance, ts
        FROM route_cache
        WHERE query = ?
        ORDER BY ts DESC
        LIMIT 1
        """,
        (query,),
    ).fetchone()

    if row is None:
        return None

    keys = (
        "key",
        "query",
        "route",
        "model",
        "response",
        "hits",
        "provenance",
        "ts",
    )
    return dict(zip(keys, row, strict=True))


def fts_lookup(conn: sqlite3.Connection, query: str, limit: int) -> list[dict]:
    match = fts_terms(query)

    if not match:
        return []

    rows = conn.execute(
        """
        SELECT
            rc.key,
            rc.query,
            rc.route,
            rc.model,
            rc.response,
            rc.hits,
            rc.provenance,
            rc.ts,
            bm25(route_cache_fts) AS rank
        FROM route_cache_fts
        JOIN route_cache AS rc ON rc.rowid = route_cache_fts.rowid
        WHERE route_cache_fts MATCH ?
        ORDER BY rank
        LIMIT ?
        """,
        (match, limit),
    ).fetchall()

    keys = (
        "key",
        "query",
        "route",
        "model",
        "response",
        "hits",
        "provenance",
        "ts",
        "rank",
    )
    return [dict(zip(keys, row, strict=True)) for row in rows]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only exact and FTS5 lookup against existing OpenRoot route_cache.db."
    )
    parser.add_argument(
        "query",
        help="Task/query text to search. No model dispatch occurs.",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help="Discovered existing route_cache.db path; must already exist.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum FTS5 evidence rows, 1 through 12.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    query = normalize_query(args.query)
    db_path = args.db.expanduser().resolve()

    if not query:
        return fail("HELD_EMPTY_QUERY")

    if not 1 <= args.limit <= 12:
        return fail("HELD_INVALID_LIMIT", query=query)

    if not db_path.is_file():
        return fail("UNKNOWN_ROUTE_CACHE_INTERFACE", query=query)

    try:
        conn = open_readonly(db_path)
    except sqlite3.Error as exc:
        return fail(f"UNKNOWN_ROUTE_CACHE_INTERFACE:{type(exc).__name__}", query=query)

    try:
        schema_rows = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
            )
        }

        required = {"route_cache", "route_cache_fts"}
        if not required.issubset(schema_rows):
            return fail("UNKNOWN_ROUTE_CACHE_INTERFACE", query=query)

        exact = exact_lookup(conn, query)
        if exact is not None:
            emit(
                {
                    "canary": CANARY,
                    "cache_disposition": "EXACT_REUSE",
                    "db": str(db_path),
                    "query": query,
                    "record": exact,
                    "status": "READ_ONLY_HIT",
                    "timestamp": utc_now(),
                }
            )
            print(f"{CANARY} [exit=0]", file=sys.stderr)
            return 0

        evidence = fts_lookup(conn, query, args.limit)
        if evidence:
            emit(
                {
                    "canary": CANARY,
                    "cache_disposition": "FTS_EVIDENCE",
                    "db": str(db_path),
                    "evidence": evidence,
                    "query": query,
                    "status": "READ_ONLY_EVIDENCE",
                    "timestamp": utc_now(),
                }
            )
            print(f"{CANARY} [exit=0]", file=sys.stderr)
            return 0

        emit(
            {
                "canary": CANARY,
                "cache_disposition": "CACHE_MISS",
                "db": str(db_path),
                "next_state": "HUMAN_GATE_REQUIRED",
                "query": query,
                "reason": "route_cache and route_cache_fts contain no usable match; dispatch is intentionally disabled",
                "status": "READ_ONLY_MISS",
                "timestamp": utc_now(),
            }
        )
        print(f"{CANARY} [exit=0]", file=sys.stderr)
        return 0
    except sqlite3.Error as exc:
        return fail(f"UNKNOWN_ROUTE_CACHE_INTERFACE:{type(exc).__name__}", query=query)
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
