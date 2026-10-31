#!/usr/bin/env python3
"""
INSPECT ALL PODS & MERKLE SEALS
==============================
Scans ~/pods/ for all pod databases, checks their document counts, 
chunks, and Merkle root seals.
"""

import sqlite3
from pathlib import Path

def inspect():
    pods_dir = Path("~/pods").expanduser()
    if not pods_dir.exists():
        print(f"[error] Pods directory not found at {pods_dir}")
        return

    pod_dbs = list(pods_dir.glob("*/pod.db"))
    print(f"Discovered {len(pod_dbs)} pod databases under {pods_dir}:\n" + "-"*65)

    for pod_db in pod_dbs:
        pod_name = pod_db.parent.name
        try:
            conn = sqlite3.connect(f"file:{pod_db}?mode=ro", uri=True)
            
            # Check tables
            tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            
            docs = conn.execute("SELECT count(*) FROM ledger").fetchone()[0] if "ledger" in tables else 0
            chunks = conn.execute("SELECT count(*) FROM chunks").fetchone()[0] if "chunks" in tables else 0
            
            seal = conn.execute("SELECT merkle_root, timestamp FROM seals ORDER BY seal_id DESC LIMIT 1").fetchone() if "seals" in tables else None
            merkle_root = seal[0] if seal else "UNSEALED"
            seal_time = seal[1] if seal else "N/A"
            
            conn.close()
            
            print(f"📦 Pod: {pod_name}")
            print(f"   Documents (Ledger): {docs:,}")
            print(f"   Chunks:             {chunks:,}")
            print(f"   Merkle Seal:        {merkle_root[:24]}... ({seal_time})")
            print("-" * 65)
        except Exception as e:
            print(f"❌ Pod: {pod_name} [Error reading DB: {e}]")

if __name__ == "__main__":
    inspect()
