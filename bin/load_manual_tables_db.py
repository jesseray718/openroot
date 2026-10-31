# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""Load OpenLoom-extracted manual tables into a SHA-256 evidence database."""

from __future__ import annotations

import argparse
import csv
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    args = parser.parse_args()

    manifest_path = args.manifest.resolve()
    db_path = args.db.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    conn.executescript("""
    CREATE TABLE IF NOT EXISTS manual_sources (
        source_id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        manifest_path TEXT NOT NULL,
        manifest_sha256 TEXT NOT NULL,
        loaded_at_utc TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS manual_tables (
        table_id TEXT PRIMARY KEY,
        source_id INTEGER NOT NULL REFERENCES manual_sources(source_id),
        pdf_page INTEGER NOT NULL,
        row_count INTEGER NOT NULL,
        column_count INTEGER NOT NULL,
        csv_path TEXT NOT NULL,
        jsonl_path TEXT NOT NULL,
        csv_sha256 TEXT NOT NULL,
        jsonl_sha256 TEXT NOT NULL,
        loaded_at_utc TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS manual_table_rows (
        row_id INTEGER PRIMARY KEY,
        table_id TEXT NOT NULL REFERENCES manual_tables(table_id),
        pdf_page INTEGER NOT NULL,
        row_index INTEGER NOT NULL,
        row_json TEXT NOT NULL,
        row_sha256 TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_manual_tables_source
        ON manual_tables(source_id);

    CREATE INDEX IF NOT EXISTS idx_manual_table_rows_table
        ON manual_table_rows(table_id);

    CREATE VIRTUAL TABLE IF NOT EXISTS manual_tables_fts USING fts5(
        table_id UNINDEXED,
        pdf_page UNINDEXED,
        content
    );
    """)

    manifest_sha = sha256(manifest_path)

    conn.execute(
        "INSERT INTO manual_sources (title, manifest_path, manifest_sha256) VALUES (?, ?, ?)",
        ("Lubuntu 24.04 Manual", str(manifest_path), manifest_sha),
    )
    source_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    loaded_tables = 0
    loaded_rows = 0

    for item in manifest:
        table_id = item["table_id"]
        csv_path = Path(item["csv"])
        jsonl_path = Path(item["jsonl"])

        csv_hash = sha256(csv_path)
        jsonl_hash = sha256(jsonl_path)

        if csv_hash != item["csv_sha256"]:
            raise ValueError(f"CSV hash mismatch: {table_id}")
        if jsonl_hash != item["jsonl_sha256"]:
            raise ValueError(f"JSONL hash mismatch: {table_id}")

        conn.execute(
            """
            INSERT INTO manual_tables (
                table_id, source_id, pdf_page, row_count, column_count,
                csv_path, jsonl_path, csv_sha256, jsonl_sha256
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                table_id, source_id, item["pdf_page"], item["rows"],
                item["columns"], str(csv_path), str(jsonl_path),
                csv_hash, jsonl_hash,
            ),
        )

        searchable_lines = []

        with csv_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            header = next(reader)
            searchable_lines.append(" | ".join(header))

            for row_index, row in enumerate(reader):
                row_json = json.dumps(
                    dict(zip(header, row)),
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                row_hash = sha256_text(row_json)

                conn.execute(
                    """
                    INSERT INTO manual_table_rows (
                        table_id, pdf_page, row_index, row_json, row_sha256
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (table_id, item["pdf_page"], row_index, row_json, row_hash),
                )
                searchable_lines.append(" | ".join(row))
                loaded_rows += 1

        conn.execute(
            "INSERT INTO manual_tables_fts (table_id, pdf_page, content) VALUES (?, ?, ?)",
            (table_id, item["pdf_page"], "\n".join(searchable_lines)),
        )
        loaded_tables += 1

    conn.commit()

    counts = {
        "sources": conn.execute("SELECT COUNT(*) FROM manual_sources").fetchone()[0],
        "tables": conn.execute("SELECT COUNT(*) FROM manual_tables").fetchone()[0],
        "rows": conn.execute("SELECT COUNT(*) FROM manual_table_rows").fetchone()[0],
        "fts_rows": conn.execute("SELECT COUNT(*) FROM manual_tables_fts").fetchone()[0],
        "integrity": conn.execute("PRAGMA integrity_check").fetchone()[0],
    }

    print(json.dumps({
        "status": "LOADED",
        "database": str(db_path),
        "manifest": str(manifest_path),
        "manifest_sha256": manifest_sha,
        "loaded_tables": loaded_tables,
        "loaded_rows": loaded_rows,
        "counts": counts,
    }, indent=2))

    conn.close()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    main()
