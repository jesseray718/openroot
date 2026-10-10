#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
popw_ledger_v1.py

Proof-of-Physical-Work ledger for openroot.

Doctrine:
  - Energy is recorded as a ledger, not a claim.
  - If no measured instrument exists, meter_kind MUST be "estimate".
  - A job must have input/output SHA-256 references.
  - Human gate remains necessary for any high-value publication.

Commands:
  record  --job-id JOB --input-hash X --output-hash Y --meter-kind estimate
          --joules-human JH --joules-useful JU --k-delta KD --note TEXT
  stats
  list   [--job-id JOB]
"""

import argparse
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/jesse/openroot")
DATA = ROOT / "data"
DB = DATA / "rootkit.db"

def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def ensure_db():
    DATA.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
      job_id TEXT PRIMARY KEY,
      input_sha256 TEXT,
      output_sha256 TEXT,
      spec_sha256 TEXT,
      status TEXT NOT NULL DEFAULT 'pending',
      started_ts TEXT,
      ended_ts TEXT,
      notes TEXT
    )
    """)
    con.execute("""
    CREATE TABLE IF NOT EXISTS attestations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      job_id TEXT NOT NULL,
      meter_kind TEXT NOT NULL,
      joules_human REAL,
      joules_useful REAL,
      k_delta REAL,
      measured_ts TEXT NOT NULL,
      verifier TEXT,
      note TEXT
    )
    """)
    con.execute("""
    CREATE TABLE IF NOT EXISTS migration_log (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      migration_name TEXT NOT NULL,
      applied_ts TEXT NOT NULL,
      note TEXT
    )
    """)
    con.execute(
      "INSERT OR IGNORE INTO migration_log(migration_name, applied_ts, note) VALUES (?,?,?)",
      ("popw_ledger_v1", now_iso(), "initial energy ledger")
    )
    con.commit()
    con.close()

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def cmd_record(args):
    if not args.job_id:
        print("[ERROR] --job-id required", file=sys.stderr)
        return 2
    if not args.input_hash and not args.output_hash:
        print("[ERROR] at least one of --input-hash/--output-hash is required", file=sys.stderr)
        return 2

    meter_kind = (args.meter_kind or "estimate").lower()
    if meter_kind not in {"estimate", "measured"}:
        print(f"[ERROR] unsupported meter_kind: {meter_kind}", file=sys.stderr)
        return 2

    con = sqlite3.connect(DB)
    con.execute("""
    INSERT OR IGNORE INTO jobs(job_id, input_sha256, output_sha256, spec_sha256, status, started_ts, ended_ts, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        args.job_id,
        args.input_hash,
        args.output_hash,
        args.spec_hash,
        "recorded",
        args.started_ts or now_iso(),
        args.ended_ts or now_iso(),
        args.note or ""
    ))

    con.execute("""
    INSERT INTO attestations
      (job_id, meter_kind, joules_human, joules_useful, k_delta, measured_ts, verifier, note)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        args.job_id,
        meter_kind,
        args.joules_human,
        args.joules_useful,
        args.k_delta,
        now_iso(),
        args.verifier or "rootkit_popw_v1",
        args.note or ""
    ))
    con.commit()
    con.close()

    print(f"[banked] recorded POPW attestation: job={args.job_id} meter={meter_kind}")
    return 0

def cmd_stats(args):
    con = sqlite3.connect(DB)
    jobs = con.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    ats  = con.execute("SELECT COUNT(*) FROM attestations").fetchone()[0]
    total_jh = con.execute("SELECT COALESCE(SUM(joules_human),0) FROM attestations").fetchone()[0]
    total_ju = con.execute("SELECT COALESCE(SUM(joules_useful),0) FROM attestations").fetchone()[0]
    total_k  = con.execute("SELECT COALESCE(SUM(k_delta),0) FROM attestations").fetchone()[0]
    con.close()

    print(json.dumps({
        "jobs": jobs,
        "attestations": ats,
        "joules_human_total": total_jh,
        "joules_useful_total": total_ju,
        "k_delta_total": total_k,
        "meter_kind_note": "estimate values are explicit; never inferred as measured"
    }, sort_keys=True))
    return 0

def cmd_list(args):
    con = sqlite3.connect(DB)
    if args.job_id:
        rows = con.execute("""
          SELECT a.id, a.job_id, a.meter_kind, a.joules_human, a.joules_useful, a.k_delta,
                 a.measured_ts, a.verifier, a.note
          FROM attestations a
          WHERE a.job_id = ?
          ORDER BY a.measured_ts DESC
        """, (args.job_id,)).fetchall()
    else:
        rows = con.execute("""
          SELECT a.id, a.job_id, a.meter_kind, a.joules_human, a.joules_useful, a.k_delta,
                 a.measured_ts, a.verifier, a.note
          FROM attestations a
          ORDER BY a.measured_ts DESC
        """).fetchall()

    if not rows:
        print(json.dumps({"job_id": args.job_id, "attestations": []}, sort_keys=True))
        return 0

    out = []
    for r in rows:
        out.append({
            "id": r[0],
            "job_id": r[1],
            "meter_kind": r[2],
            "joules_human": r[3],
            "joules_useful": r[4],
            "k_delta": r[5],
            "measured_ts": r[6],
            "verifier": r[7],
            "note": r[8],
        })
    print(json.dumps({"attestations": out}, sort_keys=True))
    return 0

def cmd_hash(args):
    if not args.path:
        print("[ERROR] --path required", file=sys.stderr)
        return 2
    p = Path(args.path).resolve()
    if not p.exists():
        print(f"[ERROR] missing file: {p}", file=sys.stderr)
        return 2
    print(json.dumps({"path": str(p), "sha256": sha256_file(p)}, sort_keys=True))
    return 0

def main():
    ap = argparse.ArgumentParser(description="POPW ledger")
    sub = ap.add_subparsers(dest="cmd", required=True)

    rec = sub.add_parser("record", help="record energy attestation")
    rec.add_argument("--job-id", required=True)
    rec.add_argument("--input-hash", default=None)
    rec.add_argument("--output-hash", default=None)
    rec.add_argument("--spec-hash", default=None)
    rec.add_argument("--meter-kind", default="estimate", choices=["estimate", "measured"])
    rec.add_argument("--joules-human", type=float, default=0.0)
    rec.add_argument("--joules-useful", type=float, default=0.0)
    rec.add_argument("--k-delta", type=float, default=0.0)
    rec.add_argument("--note", default="")
    rec.add_argument("--verifier", default="rootkit_popw_v1")
    rec.add_argument("--started-ts", default=None)
    rec.add_argument("--ended-ts", default=None)
    rec.set_defaults(func=cmd_record)

    st = sub.add_parser("stats", help="show ledger totals")
    st.set_defaults(func=cmd_stats)

    lst = sub.add_parser("list", help="list attestations")
    lst.add_argument("--job-id", default=None)
    lst.set_defaults(func=cmd_list)

    hs = sub.add_parser("hash", help="hash a file")
    hs.add_argument("--path", required=True)
    hs.set_defaults(func=cmd_hash)

    args = ap.parse_args()
    ensure_db()
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
