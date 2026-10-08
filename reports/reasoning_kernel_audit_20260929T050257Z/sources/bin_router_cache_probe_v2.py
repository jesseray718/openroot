#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
OpenRoot route-cache probe v2.

Read-only behavior:
- exact lookup through route_cache.query;
- checks whether existing route_cache_fts is actually searchable;
- never creates, rebuilds, updates, deletes, or inserts SQLite data;
- never dispatches a model;
- never changes Git state.
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

CANARY = "[ROUTER-CACHE-PROBE-V2]"
DEFAULT_ROOT = Path(os.environ.get("ROOT", str(Path.home() / "openroot"))).expanduser()
DEFAULT_DB = DEFAULT_ROOT / "data" / "route_cache.db"

REQUIRED_ROUTE_COLUMNS = {
    "key",
    "query",
    "route",
    "model",
    "response",
    "hits",
    "provenance",
    "ts",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def emit(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def end(code: int) -> int:
    print(f"{CANARY} [exit={code}]", file=sys.stderr)
    return code


def held(status: str, detail: str, query: str = "") -> int:
    emit(
        {
            "canary": CANARY,
            "detail": detail,
            "query": query,
            "status": status,
            "timestamp": now(),
        }
    )
    return end(1)


def normalize(value: str) -> str:
    return " ".join(value.strip().split())


def readonly_connection(db_path: Path) -> sqlite3.Connection:
    if not db_path.is_file():
        raise FileNotFoundError(str(db_path))

    uri = f"file:{quote(str(db_path))}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def route_columns(conn: sqlite3.Connection) -> set[str]:
    return {
        str(row[1])
        for row in conn.execute("PRAGMA table_info(route_cache)").fetchall()
    }


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

    fields = (
        "key",
        "query",
        "route",
        "model",
        "response",
        "hits",
        "provenance",
        "ts",
    )

    return dict(zip(fields, row, strict=True))


def token_literals(query: str) -> list[str]:
    raw = query.replace('"', " ").split()
    output: list[str] = []

    for token in raw:
        cleaned = "".join(
            character
            for character in token
            if character.isalnum() or character in {"_", "-"}
        )

        if cleaned:
            output.append(cleaned)

    return output[:12]


def fts_is_searchable(
    conn: sqlite3.Connection,
    expected_key: str,
    query: str,
) -> tuple[bool, str]:
    tables = {
        str(row[0])
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
        ).fetchall()
    }

    if "route_cache_fts" not in tables:
        return False, "UNKNOWN_FTS_INTERFACE"

    for token in token_literals(query):
        match = f'"{token.replace(chr(34), "")}"'

        row = conn.execute(
            """
            SELECT rc.key
            FROM route_cache_fts
            JOIN route_cache AS rc
              ON rc.rowid = route_cache_fts.rowid
            WHERE route_cache_fts MATCH ?
            ORDER BY bm25(route_cache_fts)
            LIMIT 1
            """,
            (match,),
        ).fetchone()

        if row is not None and str(row[0]) == expected_key:
            return True, "FTS_SEARCHABLE"

    return False, "HELD_UNSYNCED_FTS_INDEX"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only OpenRoot exact-cache probe with FTS health reporting."
    )
    parser.add_argument("query")
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help="Existing route_cache.db; opened read-only only.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    query = normalize(args.query)
    db_path = args.db.expanduser().resolve()

    if not query:
        return held("HELD_EMPTY_QUERY", "normalized query is empty")

    try:
        conn = readonly_connection(db_path)
    except (OSError, sqlite3.Error) as exc:
        return held("UNKNOWN_ROUTE_CACHE_INTERFACE", str(exc), query)

    try:
        tables = {
            str(row[0])
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
            ).fetchall()
        }

        if "route_cache" not in tables:
            return held(
                "UNKNOWN_ROUTE_CACHE_INTERFACE",
                "route_cache table absent",
                query,
            )

        columns = route_columns(conn)
        missing = sorted(REQUIRED_ROUTE_COLUMNS - columns)

        if missing:
            return held(
                "UNKNOWN_ROUTE_CACHE_INTERFACE",
                "route_cache missing columns: " + ",".join(missing),
                query,
            )

        exact = exact_lookup(conn, query)

        if exact is not None:
            fts_ok, fts_state = fts_is_searchable(conn, exact["key"], query)

            emit(
                {
                    "canary": CANARY,
                    "cache_disposition": "EXACT_REUSE",
                    "db": str(db_path),
                    "fts_state": fts_state,
                    "next_state": (
                        "RETURN_EXACT_RESULT"
                        if fts_ok
                        else "RETURN_EXACT_RESULT_AND_HOLD_FTS_REPAIR"
                    ),
                    "query": query,
                    "record": exact,
                    "status": "READ_ONLY_HIT",
                    "timestamp": now(),
                }
            )

            return end(0)

        emit(
            {
                "canary": CANARY,
                "cache_disposition": "CACHE_MISS",
                "db": str(db_path),
                "next_state": "HUMAN_GATE_REQUIRED",
                "query": query,
                "reason": "exact cache miss; dispatch remains intentionally disabled",
                "status": "READ_ONLY_MISS",
                "timestamp": now(),
            }
        )

        return end(0)

    except sqlite3.Error as exc:
        return held(
            "UNKNOWN_ROUTE_CACHE_INTERFACE",
            f"{type(exc).__name__}: {exc}",
            query,
        )
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
