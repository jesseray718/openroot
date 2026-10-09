#!/usr/bin/env python3
"""lumo_ingest.py v2 — rebuilt from scar 2026-10-09 (original unrecoverable).

Known contract (hard facts from cron + tap log):
  - runs every 10 min via cron: /usr/bin/python3 bin/lumo_ingest.py >> logs/lumo_ingest.log
  - role: ingest directives from context_bridge/lumo_inbox, consume lumo_outbox
INFERENCE (rebuild author): dedupe by sha256 in sqlite, append receipts as JSONL.
If original differed, mistake-engine the delta on first live run.
"""
import os, sys, json, hashlib, sqlite3, time

ROOT = "/home/jesse/openroot"
INBOX = os.path.join(ROOT, "context_bridge", "lumo_inbox")
OUTBOX = os.path.join(ROOT, "context_bridge", "lumo_outbox")
DB = os.path.join(ROOT, "data", "lumo_ingest.db")
RECEIPTS = os.path.join(ROOT, "logs", "lumo_ingest_receipts.jsonl")

BUF = 1024 * 1024

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(BUF), b""):
            h.update(chunk)
    return h.hexdigest()

def db():
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS ingested (
        sha256 TEXT PRIMARY KEY, path TEXT, ts_utc TEXT)""")
    return conn

def main():
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    conn = db()
    now_new, now_dup = 0, 0
    for d in (INBOX, OUTBOX):
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            p = os.path.join(d, name)
            if not os.path.isfile(p):
                continue
            s = sha256_file(p)
            try:
                conn.execute("INSERT INTO ingested VALUES (?,?,?)",
                             (s, os.path.relpath(p, ROOT), ts))
                now_new += 1
                status = "new"
            except sqlite3.IntegrityError:
                now_dup += 1
                status = "dup"
            rec = {"ts_utc": ts, "path": os.path.relpath(p, ROOT),
                   "sha256": s, "status": status}
            os.makedirs(os.path.dirname(RECEIPTS), exist_ok=True)
            with open(RECEIPTS, "a") as f:
                f.write(json.dumps(rec) + "\n")
    conn.commit()
    print(f"[lumo_ingest v2] new={now_new} dup={now_dup} db={DB}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
