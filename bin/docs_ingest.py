#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
"""
docs_ingest.py - Build/rebuild FTS5 knowledge corpus for local retrieval
CANARY: DOCS_INGEST_V1_20260924
Feeds: context_bridge/, docs/, data/lessons.jsonl, analysis/, README, axiom JSONLs.
Idempotent: content sha256 dedup means re-runs skip unchanged files.
DB: data/knowledge.db (runtime state, untracked).
Usage: python3 bin/docs_ingest.py [search "query"] (no args = full ingest)
"""
import sys, os, json, hashlib, sqlite3, re
from pathlib import Path
from datetime import datetime

BASE = Path("/home/jesse/openroot")
DB = BASE / "data" / "knowledge.db"

SOURCES = [
    ("session", BASE / "context_bridge", "*.md"),
    ("session_seed", BASE / "context_bridge" / "session_seeds", "*"),
    ("doc", BASE / "docs", "*.md"),
    ("lesson", BASE / "data", "lessons.jsonl"),      # special-cased below
    ("analysis", BASE / "analysis", "*.md"),
    ("repo", BASE, "README.md"),
    ("repo", BASE, "FOUNDATION_ROOT.md"),
    ("goal", BASE, "GOALS.md"),
    ("axiom", BASE / "data", "*.jsonl"),
]

def schema(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS docs (
        id INTEGER PRIMARY KEY, path TEXT UNIQUE, source TEXT,
        title TEXT, content TEXT, sha TEXT, ingested TEXT);
    CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(
        title, content, content='docs', content_rowid='id');
    CREATE TRIGGER IF NOT EXISTS docs_ai AFTER INSERT ON docs BEGIN
        INSERT INTO docs_fts(rowid, title, content) VALUES (new.id, new.title, new.content);
    END;
    CREATE TRIGGER IF NOT EXISTS docs_ad AFTER DELETE ON docs BEGIN
        INSERT INTO docs_fts(docs_fts, rowid, title, content)
        VALUES('delete', old.id, old.title, old.content);
    END;
    """)
    conn.commit()

def sha(t): return hashlib.sha256(t.encode()).hexdigest()

def iter_units():
    """Yield (path, source, title, content). Chunks jsonl line-wise, md whole-file."""
    for source, root, pattern in SOURCES:
        if isinstance(pattern, str) and pattern.endswith(".jsonl") and (root / pattern).exists():
            f = root / pattern
            for i, line in enumerate(f.read_text(errors="replace").splitlines()):
                if not line.strip(): continue
                try:
                    rec = json.loads(line)
                    title = rec.get("lesson_id") or rec.get("id") or f"line{i}"
                    body = " ".join(str(v) for v in rec.values() if isinstance(v, (str, int, float)))
                except json.JSONDecodeError:
                    continue
                yield str(f) + f"#{i}", source, str(title), body
        elif hasattr(root, "glob"):
            for f in sorted(root.glob(pattern)):
                if not f.is_file() or f.stat().st_size > 500_000: continue
                text = f.read_text(errors="replace")
                yield str(f), source, f.stem, text

def ingest():
    conn = sqlite3.connect(DB); schema(conn)
    seen, added, skipped = 0, 0, 0
    for path, source, title, content in iter_units():
        seen += 1
        h = sha(content)
        row = conn.execute("SELECT sha FROM docs WHERE path=?", (path,)).fetchone()
        if row:
            if row[0] == h: skipped += 1; continue
            conn.execute("DELETE FROM docs WHERE path=?", (path,))
        conn.execute("INSERT INTO docs (path, source, title, content, sha, ingested) VALUES (?,?,?,?,?,?)",
                     (path, source, title, content[:100000], h, datetime.now().isoformat()))
        added += 1
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM docs").fetchone()[0]
    conn.close()
    print(f"[banked] scanned {seen} units | added {added} | unchanged {skipped} | corpus total {total}")
    print(f"[banked] {DB}")

def search(q):
    conn = sqlite3.connect(DB); schema(conn)
    rows = conn.execute(
        "SELECT d.source, d.title, snippet(docs_fts, 1, '>>>', '<<<', '...', 20) "
        "FROM docs_fts JOIN docs d ON d.id = docs_fts.rowid "
        "WHERE docs_fts MATCH ? ORDER BY rank LIMIT 10", (q,)).fetchall()
    conn.close()
    if not rows:
        print(f"[held] no matches for {q!r}"); return
    for src, title, snip in rows:
        print(f"[{src}] {title}\n    {snip}\n")

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "search":
        search(" ".join(sys.argv[2:]))
    else:
        ingest()
