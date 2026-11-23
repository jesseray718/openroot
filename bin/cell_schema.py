#!/usr/bin/env python3
# cell_schema.py v1 — unified self-similar cell store. Constitution 1.1 steps 1-2.
import sqlite3, sys, hashlib, json, os

CMD = sys.argv[1] if len(sys.argv) > 1 else ""
DB = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("CELL_DB", "/home/jesse/openroot/pods/cells.pod.sqlite3")

DDL = """
CREATE TABLE IF NOT EXISTS cell (
    tid          TEXT PRIMARY KEY,
    level        INTEGER NOT NULL,
    parent_tid   TEXT REFERENCES cell(tid),
    blake3       TEXT NOT NULL,
    sha256       TEXT NOT NULL,
    bytes        INTEGER NOT NULL,
    mtime        INTEGER NOT NULL,
    prev         TEXT,
    kind         TEXT NOT NULL,
    payload_ref  TEXT
);
CREATE TABLE IF NOT EXISTS taxon (
    rank        TEXT NOT NULL,
    name        TEXT NOT NULL,
    tid         TEXT PRIMARY KEY REFERENCES cell(tid),
    fts_table   TEXT NOT NULL
);
CREATE VIRTUAL TABLE IF NOT EXISTS cell_fts USING fts5(
    tid UNINDEXED, body, tokenize='unicode61 remove_diacritics 2'
);
"""

def sha256(s): return hashlib.sha256(s.encode()).hexdigest()

def open_db(db=DB):
    con = sqlite3.connect(db)
    con.executescript(DDL)
    return con


def insert_fts(con, tid, body):
    """Insert once per TID; reject a different body without committing caller work."""
    if not isinstance(tid, str) or not tid:
        raise ValueError("invalid FTS TID")
    if not isinstance(body, str):
        raise ValueError("non-text FTS body")
    con.execute("SAVEPOINT openroot_fts_guard")
    try:
        inserted = con.execute(
            "INSERT INTO cell_fts (tid, body) "
            "SELECT ?, ? WHERE NOT EXISTS "
            "(SELECT 1 FROM cell_fts WHERE tid=?)",
            (tid, body, tid),
        ).rowcount
        rows = con.execute(
            "SELECT DISTINCT body COLLATE BINARY "
            "FROM cell_fts WHERE tid=? LIMIT 2",
            (tid,),
        ).fetchall()
        if len(rows) != 1 or rows[0][0] != body:
            raise ValueError("conflicting FTS body for existing TID")
    except BaseException:
        con.execute("ROLLBACK TO openroot_fts_guard")
        con.execute("RELEASE openroot_fts_guard")
        raise
    con.execute("RELEASE openroot_fts_guard")
    return inserted == 1

def insert_cell(con, level, kind, parent_tid, body, payload_ref=None, prev=None, tid_salt=""):
    b3 = hashlib.blake2b((tid_salt + body).encode(), digest_size=32).hexdigest()
    tid = hashlib.blake2b((str(level) + kind + str(parent_tid) + b3).encode(), digest_size=32).hexdigest()
    ts = int(os.environ.get("CELL_MTIME", __import__("time").time()))
    con.execute("INSERT OR IGNORE INTO cell VALUES (?,?,?,?,?,?,?,?,?,?)",
                (tid, level, parent_tid, b3, sha256(body), len(body.encode()), ts, prev, kind, payload_ref))
    insert_fts(con, tid, body)
    return tid

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "init":
        con = open_db()
        print("[ok] cell store at", DB)
        con.close()
    elif cmd == "ingest-ledger":
        con = open_db()
        LEDGER = os.environ.get("CELL_LEDGER", "/home/jesse/openroot/ledger/popw_thermal.jsonl")
        kingdom = insert_cell(con, 4, "taxon", None, "Ledger: metered thermal and energy receipts, hash-chained, OTS-notarized.")
        con.execute("INSERT OR IGNORE INTO taxon VALUES (?,?,?,?)", ("kingdom", "Ledger", kingdom, "cell_fts"))
        prev = None
        n = 0
        for line in open(LEDGER):
            line = line.strip()
            if not line: continue
            b = json.loads(line)
            prev_link = b.get("prev")
            tid = insert_cell(con, 3, "ledger_block", kingdom, json.dumps(b, sort_keys=True),
                              payload_ref="ledger/popw_thermal.jsonl", prev=prev_link)
            prev = b.get("hash")
            n += 1
        con.commit()
        print("[ok] ingested", n, "ledger blocks under kingdom", kingdom[:16])
        print("[ok] last sibling hash (chain tip):", prev)
    elif cmd == "verify":
        con = open_db()
        bad = 0
        for tid, level, parent, b3, prev in con.execute("SELECT tid, level, parent_tid, blake3, prev FROM cell WHERE kind = ?", ("ledger_block",)):
            # positional identity check: tid must derive from level+kind+parent+b3
            expect = hashlib.blake2b((str(level) + "ledger_block" + str(parent) + b3).encode(), digest_size=32).hexdigest()
            if expect != tid:
                bad += 1
                print("BROKEN cell identity:", tid[:16])
        # sibling chain walk: each block prev must equal prior block sha-hash-of-body (popw hash field)
        rows = list(con.execute("SELECT cell.prev, cell.blake3, cell_fts.body FROM cell JOIN cell_fts ON cell.tid = cell_fts.tid WHERE cell.kind = ? ORDER BY cell.rowid", ("ledger_block",)))
        prev_expect = None
        for r in rows:
            body = json.loads(r[2])
            if prev_expect is not None and body.get("prev") != prev_expect:
                bad += 1
                print("BROKEN prev link at", body.get("id"))
            prev_expect = body.get("hash")
        print("cells:", len(rows), "broken:", bad)
        sys.exit(1 if bad else 0)
    elif cmd == "fts-probe":
        # Stage 1 smoke test: autodossier primitive against the unified store
        con = open_db()
        WORD = os.environ.get("CELL_WORD", "energy")
        hits = con.execute("SELECT cell.tid, substr(cell_fts.body,1,60) FROM cell_fts JOIN cell ON cell.tid = cell_fts.tid WHERE cell_fts MATCH ? ORDER BY rank", (WORD,)).fetchall()
        for h in hits: print("[hit]", h[0][:16], h[1])
        print("[ok] autodossier probe: word =", WORD, "| incidences:", len(hits))
    else:
        print("usage: init | ingest-ledger | verify | fts-probe")
        sys.exit(2)
