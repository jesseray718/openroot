#!/usr/bin/env python3
"""Newton-chain pathway ledger v2 — Merkle lineage.
Proven pathways (input_hash -> output) are cached and never recomputed.
v2: parents + merkle_root columns. compose() builds theorem rows referencing
parent seals (A + B -> T). Seal formula for base rows is UNCHANGED from v1
so existing rows verify untouched; parents/merkle verified independently.

Usage:
  pathway_ledger_v1.py append  --input-hash H --kind K [--tool T] [--report-path P] [--verdict V]
  pathway_ledger_v1.py lookup  --input-hash H
  pathway_ledger_v1.py compose --parents SHA1,SHA2,... --label "theorem name" [--kind theorem]
  pathway_ledger_v1.py descend --row-sha S        # list children recursively
  pathway_ledger_v1.py verify                     # chain walk + lineage check
"""
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
  created_utc TEXT NOT NULL,
  parents TEXT,
  merkle_root TEXT
);
CREATE INDEX IF NOT EXISTS idx_input ON pathways(input_hash);
"""

def conn():
    c = sqlite3.connect(DB)
    c.executescript(SCHEMA)
    return c

def migrate(c):
    cols = [r[1] for r in c.execute("PRAGMA table_info(pathways)").fetchall()]
    if "parents" not in cols:
        c.execute("ALTER TABLE pathways ADD COLUMN parents TEXT")
    if "merkle_root" not in cols:
        c.execute("ALTER TABLE pathways ADD COLUMN merkle_root TEXT")
    c.commit()

def merkle_of(parent_shas, row_sha):
    leaves = sorted(list(parent_shas) + [row_sha])
    return hashlib.sha256("".join(leaves).encode()).hexdigest()

def last_row(c):
    r = c.execute("SELECT row_sha FROM pathways ORDER BY id DESC LIMIT 1").fetchone()
    return r[0] if r else "GENESIS"

def lookup(input_hash):
    c = conn(); migrate(c)
    r = c.execute("SELECT id, report_path, verdict, created_utc FROM pathways WHERE input_hash=? AND verdict='verified' ORDER BY id DESC LIMIT 1", (input_hash,)).fetchone()
    c.close()
    return r

def append(input_hash, kind, tool, report_path, verdict, parents=None):
    c = conn(); migrate(c)
    prev = last_row(c)
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    # v1 seal formula preserved EXACTLY for base rows
    payload = json.dumps([str(input_hash), kind, tool, str(report_path), verdict, prev, ts], sort_keys=True)
    row_sha = hashlib.sha256(payload.encode()).hexdigest()
    parents = parents or []
    root = merkle_of(parents, row_sha) if parents else None
    c.execute("INSERT INTO pathways(input_hash,kind,tool,report_path,verdict,prev_hash,row_sha,created_utc,parents,merkle_root) VALUES(?,?,?,?,?,?,?,?,?,?)",
              (input_hash, kind, tool, report_path, verdict, prev, row_sha, ts, json.dumps(parents) if parents else None, root))
    c.commit(); c.close()
    return row_sha

def compose(parent_list, label, kind="theorem"):
    c = conn(); migrate(c)
    for p in parent_list:
        r = c.execute("SELECT id FROM pathways WHERE row_sha=?", (p,)).fetchone()
        if not r:
            print(f"[held] parent not found: {p[:12]}"); c.close(); sys.exit(1)
    input_hash = hashlib.sha256(("THEOREM|" + label + "|" + "|".join(sorted(parent_list))).encode()).hexdigest()
    existing = c.execute("SELECT row_sha FROM pathways WHERE input_hash=?", (input_hash,)).fetchone()
    if existing:
        print(f"[banked] THEOREM ALREADY SEALED row_sha={existing[0]}")
        c.close(); return existing[0]
    c.close()
    row_sha = append(input_hash, kind, "merkle_composer", f"(composed: {label})", "verified", parents=parent_list)
    print(f"[banked] THEOREM SEALED row_sha={row_sha} parents={len(parent_list)} label={label}")
    return row_sha

def descend(row_sha, depth=0, seen=None):
    seen = seen or set()
    c = conn(); migrate(c)
    rows = c.execute("SELECT row_sha, kind, parents, report_path FROM pathways WHERE parents LIKE ?", (f"%{row_sha}%",)).fetchall()
    c.close()
    for rs, kind, pj, rp in rows:
        if rs in seen:
            continue
        parents = json.loads(pj) if pj else []
        if row_sha not in parents:
            continue
        seen.add(rs)
        print(f"{'  '*depth}[child] {rs[:12]} kind={kind} {(rp or '')[:60]}")
        descend(rs, depth+1, seen)

def verify():
    c = conn(); migrate(c)
    rows = c.execute("SELECT id,input_hash,kind,tool,report_path,verdict,prev_hash,row_sha,created_utc,parents,merkle_root FROM pathways ORDER BY id").fetchall()
    c.close()
    prev = "GENESIS"; broken = 0; theorem_count = 0; lineage_errors = 0
    all_shas = {r[7] for r in rows}
    for (rid, ih, kind, tool, rp, verdict, ph, rs, ts, pj, mr) in rows:
        # Stage 1: v1 chain walk (formula unchanged)
        payload = json.dumps([str(ih), kind, tool, str(rp), verdict, ph, ts], sort_keys=True)
        calc = hashlib.sha256(payload.encode()).hexdigest()
        if calc != rs or ph != prev:
            broken += 1
            print(f"[held] BROKEN at row {rid}")
        prev = rs
        # Stage 2: lineage verification
        if pj:
            theorem_count += 1
            parents = json.loads(pj)
            ok = all(p in all_shas for p in parents)
            expected_root = merkle_of(parents, rs)
            if not ok or mr != expected_root:
                lineage_errors += 1
                print(f"[held] LINEAGE ERROR at row {rid} (missing parents or bad merkle root)")
    status = "GREEN" if broken == 0 and lineage_errors == 0 else "RED"
    print(f"[banked] pathway chain: {len(rows)} rows ({theorem_count} theorems), {broken} broken, {lineage_errors} lineage errors, status={status}")
    return 0 if status == "GREEN" else 1

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["append", "lookup", "verify", "compose", "descend"])
    p.add_argument("--input-hash"); p.add_argument("--kind", default="audit")
    p.add_argument("--tool", default="ollama"); p.add_argument("--report-path")
    p.add_argument("--verdict", default="verified")
    p.add_argument("--parents"); p.add_argument("--label"); p.add_argument("--row-sha")
    a = p.parse_args()
    if a.cmd == "verify":
        sys.exit(verify())
    if a.cmd == "descend":
        if not a.row_sha: sys.exit("--row-sha required")
        descend(a.row_sha); sys.exit(0)
    if a.cmd == "compose":
        if not a.parents or not a.label: sys.exit("--parents and --label required")
        sys.exit(0 if compose([x.strip() for x in a.parents.split(",") if x.strip()], a.label) else 1)
    if not a.input_hash:
        sys.exit("--input-hash required")
    if a.cmd == "lookup":
        r = lookup(a.input_hash)
        print(json.dumps(r) if r else "MISS")
    else:
        parents = [x.strip() for x in a.parents.split(",")] if a.parents else None
        print(append(a.input_hash, a.kind, a.tool, a.report_path, a.verdict, parents=parents))
