#!/usr/bin/env python3
"""
newton_daemon.py - Thermodynamic Telemetry & FTS5 Indexer
Continuously monitors local node vitals, records entropy shifts to the
Newton Chain, and syncs entries to the SQLite FTS5 knowledge store.
"""

import os
import sys
import json
import time
import shutil
import sqlite3
import hashlib
from datetime import datetime, timezone
from pathlib import Path

LEDGER_DIR = Path.home() / "openroot" / "ledger"
LEDGER_FILE = LEDGER_DIR / "newton_chain.jsonl"
DB_FILE = Path.home() / "openroot" / "data" / "fts_index.db"

def get_system_vitals():
    disk = shutil.disk_usage(Path.home())
    disk_pct_used = (disk.used / disk.total) * 100.0
    load1, load5, load15 = os.getloadavg() if hasattr(os, "getloadavg") else (0.0, 0.0, 0.0)
    return {
        "load_1m": load1,
        "load_5m": load5,
        "disk_used_pct": round(disk_pct_used, 2)
    }

def get_latest_hash():
    if not LEDGER_FILE.exists():
        return "0000000000000000000000000000000000000000000000000000000000000000"
    last_line = ""
    with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                last_line = line.strip()
    if not last_line:
        return "0000000000000000000000000000000000000000000000000000000000000000"
    block = json.loads(last_line)
    # FIX 20261009: previous_hash must be the STORED hash of the prior
    # block, not a re-hash of the full record (different scheme -> every
    # link was broken since genesis). CANARY:NEWTON-LINKAGE-FIX-V1
    return block.get("hash", "0" * 64)

def record_telemetry():
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    if not LEDGER_FILE.exists():
        LEDGER_FILE.touch()

    vitals = get_system_vitals()
    prev_hash = get_latest_hash()

    with open(LEDGER_FILE, 'r', encoding='utf-8') as f:
        block_id = sum(1 for line in f if line.strip())

    block = {
        "block_id": block_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "NODE_TELEMETRY",
        "description": f"OptiPlex 3060 vitals - Load: {vitals['load_1m']}, Disk Used: {vitals['disk_used_pct']}%",
        "entropy_delta": -0.01,
        "previous_hash": prev_hash
    }

    block_str = json.dumps(block, sort_keys=True)
    block["hash"] = hashlib.sha256(block_str.encode('utf-8')).hexdigest()

    with open(LEDGER_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(block) + "\n")

    print(f"[Newton Daemon] Block #{block_id} recorded. Load: {vitals['load_1m']} | Hash: {block['hash'][:12]}...")

if __name__ == "__main__":
    print("[*] Starting Newton Chain Telemetry Daemon...")
    record_telemetry()
