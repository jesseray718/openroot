#!/usr/bin/env python3
"""Build a read-only catalog of all OpenLoom database pods."""

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inspect_database(path: Path) -> dict:
    uri = path.resolve().as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row

    try:
        tables = [
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
                "ORDER BY name"
            )
        ]

        fts_tables = [
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name LIKE '%_fts' "
                "ORDER BY name"
            )
        ]

        return {
            "database": str(path.resolve()),
            "sha256": sha256(path),
            "integrity": conn.execute("PRAGMA integrity_check").fetchone()[0],
            "tables": tables,
            "fts_tables": fts_tables,
        }
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path,
                        default=Path("pods/model-access/model_access_catalog.json"))
    args = parser.parse_args()

    root = args.root.resolve()
    databases = sorted(root.rglob("*.sqlite3")) + sorted(root.rglob("*.db"))
    databases = [
        path for path in databases
        if not any(part in {".venv", ".git", "node_modules"} for part in path.parts)
        and not path.name.endswith(("-wal", "-shm"))
    ]

    records = []
    for path in databases:
        try:
            record = inspect_database(path)
            record["status"] = "READ_ONLY_OK"
            records.append(record)
            print(f"[catalog] {path.relative_to(root)}: {record['integrity']}")
        except sqlite3.Error as error:
            records.append({
                "database": str(path.resolve()),
                "status": "UNREADABLE",
                "error": str(error),
            })
            print(f"[catalog] {path.relative_to(root)}: UNREADABLE")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(records, indent=2) + "\n")

    print(json.dumps({
        "catalog": str(args.out.resolve()),
        "catalog_sha256": sha256(args.out),
        "databases": len(records),
        "readable": sum(1 for r in records if r["status"] == "READ_ONLY_OK"),
    }, indent=2))


if __name__ == "__main__":
    main()
