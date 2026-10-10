#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
newton_chain_v1.py - append-only JOB provenance chain (rootkit).

NOT the Newton daemon's thermodynamic chain (data/newton_chain.jsonl,
ledger/newton_chain*.jsonl). This writes only data/rootkit_chain.jsonl.

block = index, timestamp_utc, job_id, input_sha256, output_sha256,
        attestation_sha256, prev_hash, nonce, note, hash
hash  = sha256 of the canonical JSON of the block without "hash".
Genesis prev_hash = 64 zeros. PoW: hash starts with "00".
Exit: 0 ok, 2 error. verify exits 1 when red.
"""
import argparse
import hashlib
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/jesse/openroot")
DATA = ROOT / "data"
CHAIN_FILE = DATA / "rootkit_chain.jsonl"
DB = DATA / "rootkit.db"
GENESIS_PREV = "0" * 64
HEX64 = re.compile(r"^[0-9a-f]{64}$")
REQUIRED = {"index", "timestamp_utc", "job_id", "input_sha256", "output_sha256",
            "attestation_sha256", "prev_hash", "nonce", "note", "hash"}


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def block_hash(block):
    payload = json.dumps(block, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def load_chain():
    if not CHAIN_FILE.exists():
        return []
    rows = []
    with open(CHAIN_FILE, "r", encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as e:
                    raise ValueError(f"{CHAIN_FILE} line {n}: {e}")
    return rows


def check_schema(blocks):
    for b in blocks:
        if not REQUIRED.issubset(b):
            raise ValueError("chain file has foreign schema; refusing to touch it")


def append_block(job_id, inp, out, att, note):
    DATA.mkdir(parents=True, exist_ok=True)
    blocks = load_chain()
    check_schema(blocks)
    prev = blocks[-1]["hash"] if blocks else GENESIS_PREV
    b = {
        "index": len(blocks), "timestamp_utc": now_iso(), "job_id": job_id,
        "input_sha256": inp, "output_sha256": out, "attestation_sha256": att,
        "prev_hash": prev, "nonce": 0, "note": note or "",
    }
    while True:
        h = block_hash(b)
        if h.startswith("00"):
            b["hash"] = h
            break
        b["nonce"] += 1

    with open(CHAIN_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(b, sort_keys=True, separators=(",", ":")) + "\n")

    con = sqlite3.connect(DB, timeout=60)
    con.execute("""CREATE TABLE IF NOT EXISTS chain_blocks (
        idx INTEGER PRIMARY KEY, job_id TEXT NOT NULL, input_sha256 TEXT NOT NULL,
        output_sha256 TEXT NOT NULL, attestation_sha256 TEXT NOT NULL,
        prev_hash TEXT NOT NULL, hash TEXT NOT NULL, note TEXT, created_ts TEXT NOT NULL)""")
    con.execute("INSERT OR IGNORE INTO chain_blocks VALUES (?,?,?,?,?,?,?,?,?)",
                (b["index"], job_id, inp, out, att, prev, b["hash"], b["note"], b["timestamp_utc"]))
    con.commit()
    con.close()
    return b


def cmd_append(a):
    for name in ("input_hash", "output_hash", "attestation_hash"):
        v = getattr(a, name)
        if not HEX64.match(v or ""):
            print(f"[ERROR] --{name.replace('_', '-')} must be 64 lowercase hex chars "
                  f"(got {len(v or '')})", file=sys.stderr)
            return 2
    try:
        b = append_block(a.job_id, a.input_hash, a.output_hash, a.attestation_hash, a.note)
    except ValueError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2
    print(json.dumps(b, sort_keys=True))
    return 0


def cmd_show(a):
    try:
        blocks = load_chain()
    except ValueError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2
    print(json.dumps({"count": len(blocks), "blocks": blocks}, sort_keys=True))
    return 0


def cmd_verify(a):
    try:
        blocks = load_chain()
        check_schema(blocks)
    except ValueError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2
    prev = GENESIS_PREV
    for i, b in enumerate(blocks):
        body = {k: v for k, v in b.items() if k != "hash"}
        if b["index"] != i or b["prev_hash"] != prev or block_hash(body) != b["hash"] \
                or not b["hash"].startswith("00"):
            print(json.dumps({"blocks": len(blocks), "status": "red", "first_bad_index": i}))
            return 1
        prev = b["hash"]
    print(json.dumps({"blocks": len(blocks), "status": "green"}))
    return 0


def main():
    ap = argparse.ArgumentParser(description="rootkit job provenance chain")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("append")
    s.add_argument("--job-id", required=True)
    s.add_argument("--input-hash", required=True)
    s.add_argument("--output-hash", required=True)
    s.add_argument("--attestation-hash", required=True)
    s.add_argument("--note", default="")
    s.set_defaults(func=cmd_append)
    sub.add_parser("show").set_defaults(func=cmd_show)
    sub.add_parser("verify").set_defaults(func=cmd_verify)
    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
