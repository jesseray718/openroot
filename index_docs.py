#!/usr/bin/env python3
import hashlib
import os
import sqlite3
import sys
from pathlib import Path

HOME = Path.home()
DB = HOME / "docs_index.db"
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HOME
TEST_TERM = sys.argv[2] if len(sys.argv) > 2 else "test"

TEXT_SUFFIXES = {
    ".txt", ".md", ".markdown", ".rst", ".log", ".csv", ".tsv", ".json",
    ".jsonl", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".py",
    ".sh", ".bash", ".zsh", ".sql", ".c", ".h", ".cpp", ".hpp", ".java",
    ".js", ".ts", ".html", ".css", ".xml", ".svg", ".tex", ".org"
}

SKIP_DIRS = {
    ".git", ".cache", ".cargo", ".npm", ".pnpm-store",
    "node_modules", "__pycache__", ".venv", "venv",
    ".android", ".gradle", "Trash"
}

MAX_BYTES = 100 * 1024 * 1024


def init_db(con):
    con.executescript("""
    PRAGMA journal_mode=WAL;
    PRAGMA synchronous=NORMAL;

    CREATE TABLE IF NOT EXISTS files (
        rowid INTEGER PRIMARY KEY,
        id TEXT UNIQUE NOT NULL,
        path TEXT UNIQUE NOT NULL,
        mtime INTEGER NOT NULL,
        size INTEGER NOT NULL,
        hash TEXT NOT NULL,
        content TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS files_hash_idx ON files(hash);
    CREATE INDEX IF NOT EXISTS files_path_idx ON files(path);

    CREATE VIRTUAL TABLE IF NOT EXISTS files_fts USING fts5(
        content,
        content='files',
        content_rowid='rowid',
        tokenize='unicode61 remove_diacritics 2'
    );

    CREATE TRIGGER IF NOT EXISTS files_ai
    AFTER INSERT ON files BEGIN
        INSERT INTO files_fts(rowid, content)
        VALUES (new.rowid, new.content);
    END;

    CREATE TRIGGER IF NOT EXISTS files_ad
    AFTER DELETE ON files BEGIN
        INSERT INTO files_fts(files_fts, rowid, content)
        VALUES ('delete', old.rowid, old.content);
    END;

    CREATE TRIGGER IF NOT EXISTS files_au
    AFTER UPDATE ON files BEGIN
        INSERT INTO files_fts(files_fts, rowid, content)
        VALUES ('delete', old.rowid, old.content);
        INSERT INTO files_fts(rowid, content)
        VALUES (new.rowid, new.content);
    END;

    CREATE TABLE IF NOT EXISTS corrections (
        file_id TEXT,
        wrong TEXT,
        fixed TEXT,
        hash TEXT
    );

    CREATE TABLE IF NOT EXISTS search_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_utc TEXT NOT NULL DEFAULT (datetime('now')),
        query TEXT NOT NULL,
        result_count INTEGER NOT NULL,
        success INTEGER NOT NULL,
        top_path TEXT,
        top_rank REAL
    );
    """)


def should_index(path):
    if not path.is_file():
        return False

    try:
        rel = path.relative_to(SRC)
    except ValueError:
        return False

    if any(part in SKIP_DIRS for part in rel.parts):
        return False

    if path.suffix.lower() not in TEXT_SUFFIXES:
        return False

    try:
        if path.stat().st_size > MAX_BYTES:
            return False

        with path.open("rb") as f:
            sample = f.read(8192)

        if b"\x00" in sample:
            return False

        sample.decode("utf-8")
        return True
    except (UnicodeDecodeError, OSError):
        return False


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def index_files(con):
    indexed = 0
    updated = 0
    skipped = 0
    errors = 0

    for root, dirs, filenames in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for name in filenames:
            path = Path(root) / name

            try:
                if not should_index(path):
                    skipped += 1
                    continue

                stat = path.stat()
                file_hash = sha256(path)
                content = path.read_text(encoding="utf-8", errors="replace")

                old = con.execute(
                    "SELECT rowid, hash, mtime, size FROM files WHERE path=?",
                    (str(path),)
                ).fetchone()

                if old:
                    rowid, old_hash, old_mtime, old_size = old

                    if (
                        old_hash == file_hash
                        and old_mtime == int(stat.st_mtime)
                        and old_size == stat.st_size
                    ):
                        continue

                    con.execute(
                        """UPDATE files
                           SET id=?, mtime=?, size=?, hash=?, content=?
                           WHERE rowid=?""",
                        (
                            file_hash,
                            int(stat.st_mtime),
                            stat.st_size,
                            file_hash,
                            content,
                            rowid,
                        ),
                    )
                    updated += 1
                else:
                    con.execute(
                        """INSERT INTO files
                           (id, path, mtime, size, hash, content)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (
                            file_hash,
                            str(path),
                            int(stat.st_mtime),
                            stat.st_size,
                            file_hash,
                            content,
                        ),
                    )
                    indexed += 1

                if indexed % 100 == 0:
                    con.commit()
                    print(f"progress: {indexed} new, {updated} updated", flush=True)

            except Exception as e:
                errors += 1
                print(f"ERROR: {path}: {e}", file=sys.stderr)

    con.commit()
    return indexed, updated, skipped, errors


def rebuild_fts_if_needed(con):
    fts_count = con.execute("SELECT count(*) FROM files_fts").fetchone()[0]
    files_count = con.execute("SELECT count(*) FROM files").fetchone()[0]

    if fts_count == files_count:
        return False

    print(f"Rebuilding FTS: files={files_count}, fts rows={fts_count}")

    con.executescript("""
    DROP TRIGGER IF EXISTS files_ai;
    DROP TRIGGER IF EXISTS files_ad;
    DROP TRIGGER IF EXISTS files_au;
    DROP TABLE IF EXISTS files_fts;

    CREATE VIRTUAL TABLE files_fts USING fts5(
        content,
        content='files',
        content_rowid='rowid',
        tokenize='unicode61 remove_diacritics 2'
    );

    INSERT INTO files_fts(rowid, content)
    SELECT rowid, content FROM files;

    CREATE TRIGGER files_ai
    AFTER INSERT ON files BEGIN
        INSERT INTO files_fts(rowid, content)
        VALUES (new.rowid, new.content);
    END;

    CREATE TRIGGER files_ad
    AFTER DELETE ON files BEGIN
        INSERT INTO files_fts(files_fts, rowid, content)
        VALUES ('delete', old.rowid, old.content);
    END;

    CREATE TRIGGER files_au
    AFTER UPDATE ON files BEGIN
        INSERT INTO files_fts(files_fts, rowid, content)
        VALUES ('delete', old.rowid, old.content);
        INSERT INTO files_fts(rowid, content)
        VALUES (new.rowid, new.content);
    END;
    """)

    con.commit()
    return True


def search(con, term):
    safe_term = term.replace('"', '""')
    fts_query = f'"{safe_term}"'

    rows = con.execute(
        """
        SELECT
            f.path,
            bm25(files_fts) AS rank,
            snippet(files_fts, 0, '>>>', '<<<', '...', 18) AS excerpt
        FROM files_fts
        JOIN files f ON f.rowid = files_fts.rowid
        WHERE files_fts MATCH ?
        ORDER BY rank
        LIMIT 25
        """,
        (fts_query,),
    ).fetchall()

    count = con.execute(
        "SELECT count(*) FROM files_fts WHERE files_fts MATCH ?",
        (fts_query,),
    ).fetchone()[0]

    top_path = rows[0][0] if rows else None
    top_rank = rows[0][1] if rows else None

    con.execute(
        """INSERT INTO search_log
           (query, result_count, success, top_path, top_rank)
           VALUES (?, ?, ?, ?, ?)""",
        (term, count, 1 if count else 0, top_path, top_rank),
    )
    con.commit()

    return rows, count


def main():
    print(f"Database: {DB}")
    print(f"Source:   {SRC}")

    if not SRC.exists():
        raise SystemExit(f"Source directory does not exist: {SRC}")

    con = sqlite3.connect(DB)
    init_db(con)

    indexed, updated, skipped, errors = index_files(con)
    rebuilt = rebuild_fts_if_needed(con)

    total = con.execute("SELECT count(*) FROM files").fetchone()[0]
    fts_total = con.execute("SELECT count(*) FROM files_fts").fetchone()[0]

    print()
    print("=== INDEX STATUS ===")
    print(f"New files indexed:  {indexed}")
    print(f"Existing updated:   {updated}")
    print(f"Files skipped:      {skipped}")
    print(f"Errors:             {errors}")
    print(f"Total files:        {total}")
    print(f"Total FTS rows:     {fts_total}")
    print(f"FTS rebuilt:        {rebuilt}")

    print()
    print(f"=== SEARCH TEST: {TEST_TERM} ===")

    rows, count = search(con, TEST_TERM)
    print(f"Matches: {count}")

    for path, rank, excerpt in rows:
        print()
        print(path)
        print(f"  rank: {rank:.3f}")
        print("  " + excerpt.replace("\n", " ")[:300])

    if count == 0:
        print()
        print("No matches for test term.")
        print('Try: python3 index_docs.py "$HOME" openroot')
    else:
        print()
        print("PASS: FTS search returned results.")

    con.execute("PRAGMA optimize;")
    con.commit()
    con.close()


if __name__ == "__main__":
    main()
