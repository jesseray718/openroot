#!/usr/bin/env python3
"""Newton-chain pathway ledger: proven pathways (input_hash -> output) are cached and never recomputed."""
import sqlite3, hashlib, json, sys, datetime, argparse

DB = "/home/jesse/openroot/data/pathways.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS pathways(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  input_hash TEXT NOT NULL,
  kind TEXT NOT NULL,
  tool TEXT NOT NULL,
  report_path TEXT,
  verdict TEXT,
  prev_hash TEXT,
  row_sha TEXT NOT NULL,
  created_utc TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_input ON pathways(input_hash);
"""

def conn():
    c = sqlite3.connect(DB)
    c.executescript(SCHEMA)
    return c

def last_row(c):
    r = c.execute("SELECT row_sha FROM pathways ORDER BY id DESC LIMIT 1").fetchone()
    return r[0] if r else "GENESIS"

def lookup(input_hash):
    c = conn()
    r = c.execute("SELECT id, report_path, verdict, created_utc FROM pathways WHERE input_hash=? AND verdict='verified' ORDER BY id DESC LIMIT 1", (input_hash,)).fetchone()
    c.close()
    return r

def append(input_hash, kind, tool, report_path, verdict):
    c = conn()
    prev = last_row(c)
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    payload = json.dumps([str(input_hash), kind, tool, str(report_path), verdict, prev, ts], sort_keys=True)
    row_sha = hashlib.sha256(payload.encode()).hexdigest()
    c.execute("INSERT INTO pathways(input_hash,kind,tool,report_path,verdict,prev_hash,row_sha,created_utc) VALUES(?,?,?,?,?,?,?,?)",
              (input_hash, kind, tool, report_path, verdict, prev, row_sha, ts))
    c.commit(); c.close()
    return row_sha

def verify():
    c = conn()
    rows = c.execute("SELECT id,input_hash,kind,tool,report_path,verdict,prev_hash,row_sha,created_utc FROM pathways ORDER BY id").fetchall()
    c.close()
    prev = "GENESIS"; broken = 0
    for (rid, ih, kind, tool, rp, verdict, ph, rs, ts) in rows:
        payload = json.dumps([str(ih), kind, tool, str(rp), verdict, ph, ts], sort_keys=True)
        calc = hashlib.sha256(payload.encode()).hexdigest()
        if calc != rs or ph != prev:
            broken += 1
            print(f"[held] BROKEN at row {rid}")
        prev = rs
    status = "GREEN" if broken == 0 else "RED"
    print(f"[banked] pathway chain: {len(rows)} rows, {broken} broken, status={status}")
    return 0 if broken == 0 else 1

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["append", "lookup", "verify"])
    p.add_argument("--input-hash"); p.add_argument("--kind", default="audit")
    p.add_argument("--tool", default="ollama"); p.add_argument("--report-path")
    p.add_argument("--verdict", default="verified")
    a = p.parse_args()
    if a.cmd == "verify":
        sys.exit(verify())
    if not a.input_hash:
        sys.exit("--input-hash required")
    if a.cmd == "lookup":
        r = lookup(a.input_hash)
        print(json.dumps(r) if r else "MISS")
    else:
        print(append(a.input_hash, a.kind, a.tool, a.report_path, a.verdict))
