#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
OpenRoot route-promotion planner.

Dry-run only:
- reads the existing route_cache.db schema in read-only mode;
- validates a candidate reusable route;
- emits a canonical JSON payload suitable for existing turing_tidbits_v1.py ingest-json;
- never calls the tidbit kernel;
- never writes SQLite;
- never increments cache hits;
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

CANARY = "[ROUTE-PROMOTION-PLAN-V1]"
DEFAULT_ROOT = Path(os.environ.get("ROOT", str(Path.home() / "openroot"))).expanduser()
DEFAULT_DB = DEFAULT_ROOT / "data" / "route_cache.db"
REQUIRED_COLUMNS = {
    "key",
    "query",
    "route",
    "model",
    "response",
    "hits",
    "provenance",
    "ts",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def emit(record: dict) -> None:
    print(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def hold(code: str, detail: str, exit_code: int = 1) -> int:
    emit(
        {
            "canary": CANARY,
            "detail": detail,
            "status": code,
            "timestamp": utc_now(),
        }
    )
    print(f"{CANARY} [exit={exit_code}]", file=sys.stderr)
    return exit_code


def normalize(value: str) -> str:
    return " ".join(value.strip().split())


def validate_text(label: str, value: str, maximum: int) -> str:
    normalized = normalize(value)

    if not normalized:
        raise ValueError(f"{label} is empty")

    if len(normalized) > maximum:
        raise ValueError(f"{label} exceeds {maximum} characters")

    return normalized


def open_readonly(db_path: Path) -> sqlite3.Connection:
    if not db_path.is_file():
        raise FileNotFoundError(str(db_path))

    uri = f"file:{quote(str(db_path))}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def inspect_schema(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute("PRAGMA table_info(route_cache)").fetchall()
    return {str(row[1]) for row in rows}


def exact_exists(conn: sqlite3.Connection, query: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM route_cache WHERE query = ? LIMIT 1",
        (query,),
    ).fetchone()
    return row is not None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a no-write OpenRoot route-promotion candidate."
    )
    parser.add_argument("--query", required=True)
    parser.add_argument("--route", required=True)
    parser.add_argument("--response-file", type=Path, required=True)
    parser.add_argument("--source-uri", default="")
    parser.add_argument("--author", default="")
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--prior-content-sha256", default="")
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help="Existing route_cache.db; read-only inspection only.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Candidate JSON payload output path; may be only within the active run directory.",
    )
    return parser.parse_args()


def ensure_run_local(path: Path) -> Path:
    run_raw = os.environ.get("RUN", "").strip()

    if not run_raw:
        raise ValueError("RUN is required; candidate output must be run-local")

    run = Path(run_raw).expanduser().resolve()
    target = path.expanduser().resolve()

    if not run.is_dir():
        raise ValueError(f"RUN directory absent: {run}")

    if target.parent != run:
        raise ValueError(f"output must be directly inside RUN: {run}")

    return target


def main() -> int:
    args = parse_args()

    try:
        query = validate_text("query", args.query, 4000)
        route = validate_text("route", args.route, 200)
        response_path = args.response_file.expanduser().resolve()
        output_path = ensure_run_local(args.out)
        db_path = args.db.expanduser().resolve()

        if not response_path.is_file():
            return hold("HELD_RESPONSE_FILE_ABSENT", str(response_path))

        response = response_path.read_text(encoding="utf-8", errors="replace").strip()

        if not response:
            return hold("HELD_EMPTY_RESPONSE", str(response_path))

        if len(response) > 200_000:
            return hold("HELD_RESPONSE_TOO_LARGE", str(len(response)))

        if not db_path.is_file():
            return hold("UNKNOWN_ROUTE_CACHE_INTERFACE", str(db_path))

        conn = open_readonly(db_path)

        try:
            columns = inspect_schema(conn)

            if not REQUIRED_COLUMNS.issubset(columns):
                missing = sorted(REQUIRED_COLUMNS - columns)
                return hold(
                    "UNKNOWN_ROUTE_CACHE_INTERFACE",
                    "missing columns: " + ",".join(missing),
                )

            if exact_exists(conn, query):
                return hold(
                    "HELD_EXACT_ROUTE_ALREADY_EXISTS",
                    "promotion refused; existing route_cache query is already present",
                )
        finally:
            conn.close()

        prior = args.prior_content_sha256.strip()

        if prior and (
            len(prior) != 64
            or any(character not in "0123456789abcdefABCDEF" for character in prior)
        ):
            return hold("HELD_INVALID_PRIOR_SHA256", prior)

        relation = []

        if prior:
            relation.append(
                {
                    "relation": "prior_verified_work",
                    "target_sha256": prior.lower(),
                    "note": f"same-channel predecessor for route={route}",
                }
            )

        payload = {
            "schema": "openroot.route_promotion_candidate/v1",
            "created_at": utc_now(),
            "policy": {
                "cache_write_requires_confirm_promote": True,
                "tidbit_ingest_requires_confirm_promote": True,
                "git_action_forbidden": True,
                "model_dispatch_forbidden": True,
                "new_sqlite_schema_forbidden": True,
                "new_identity_implementation_forbidden": True,
            },
            "candidate": {
                "query": query,
                "route": route,
                "model": "",
                "response": response,
                "provenance": "verified_local_candidate",
                "hits": 0,
            },
            "tidbit": {
                "label": f"route-promotion:{route}",
                "type": "openroot.route_promotion_candidate/v1",
                "license": "NOASSERTION",
                "author": args.author,
                "source_uri": args.source_uri,
                "tags": sorted(set(["route-cache", "promotion-candidate", *args.tag])),
                "relations": relation,
            },
            "state": "DRY_RUN_READY_FOR_HUMAN_REVIEW",
        }

        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        emit(
            {
                "canary": CANARY,
                "candidate": str(output_path),
                "cache_disposition": "PROMOTION_CANDIDATE",
                "db": str(db_path),
                "next_state": "HUMAN_GATE_REQUIRED",
                "query": query,
                "route": route,
                "status": "DRY_RUN_READY",
                "timestamp": utc_now(),
            }
        )

        print(f"{CANARY} [exit=0]", file=sys.stderr)
        return 0

    except (OSError, ValueError, sqlite3.Error) as exc:
        return hold("HELD_PROMOTION_PLAN_ERROR", str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
