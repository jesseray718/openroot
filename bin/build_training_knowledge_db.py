# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""Build an FTS-searchable knowledge database for tiny-model training."""

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    args = parser.parse_args()

    docs = sorted(args.docs.resolve().glob("*.md"))
    if not docs:
        raise SystemExit(f"No Markdown documents found in {args.docs}")

    if args.db.exists():
        args.db.unlink()

    conn = sqlite3.connect(args.db)
    conn.executescript("""
    CREATE TABLE documents (
        document_id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        path TEXT NOT NULL UNIQUE,
        sha256 TEXT NOT NULL,
        content TEXT NOT NULL,
        ingested_at_utc TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE VIRTUAL TABLE documents_fts USING fts5(
        title,
        content,
        content='documents',
        content_rowid='document_id'
    );

    CREATE TRIGGER documents_ai AFTER INSERT ON documents BEGIN
      INSERT INTO documents_fts(rowid, title, content)
      VALUES (new.document_id, new.title, new.content);
    END;

    CREATE TRIGGER documents_ad AFTER DELETE ON documents BEGIN
      INSERT INTO documents_fts(documents_fts, rowid, title, content)
      VALUES ('delete', old.document_id, old.title, old.content);
    END;

    CREATE TRIGGER documents_au AFTER UPDATE ON documents BEGIN
      INSERT INTO documents_fts(documents_fts, rowid, title, content)
      VALUES ('delete', old.document_id, old.title, old.content);
      INSERT INTO documents_fts(rowid, title, content)
      VALUES (new.document_id, new.title, new.content);
    END;
    """)

    for path in docs:
        content = path.read_text(encoding="utf-8")
        conn.execute(
            "INSERT INTO documents (title, path, sha256, content) VALUES (?, ?, ?, ?)",
            (path.stem, str(path), sha256(path), content),
        )

    conn.commit()

    report = {
        "status": "LOADED",
        "database": str(args.db.resolve()),
        "database_sha256": sha256(args.db),
        "documents": len(docs),
        "fts_rows": conn.execute(
            "SELECT COUNT(*) FROM documents_fts"
        ).fetchone()[0],
        "integrity": conn.execute("PRAGMA integrity_check").fetchone()[0],
    }

    print(json.dumps(report, indent=2))
    conn.close()


if __name__ == "__main__":
    main()
