#!/usr/bin/env python3
"""
SAFE INSPECT ALL PODS v2
========================
Inspects all SQLite pod databases safely, using read-only URI connections
to prevent any write lock attempts.
"""

import sqlite3
from pathlib import Path

def inspect():
    pods_dir = Path("~/pods").expanduser()
    if not pods_dir.exists():
        print(f"[error] Pods directory not found at {pods_dir}")
        return

    all_dbs = list(pods_dir.rglob("pod.db"))
    print(f"Discovered {len(all_dbs)} pod databases under {pods_dir}:\n" + "-"*65)

    for pod_db in all_dbs:
        pod_name = pod_db.parent.name
        try:
            # Force read-only URI connection mode to bypass locks
            conn = sqlite3.connect(f"file:{pod_db}?mode=ro", uri=True)
            
            tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            
            docs = 0
            if "ledger" in tables:
                docs = conn.execute("SELECT count(*) FROM ledger").fetchone()[0]

            chunks = 0
            if "chunks" in tables:
                chunks = conn.execute("SELECT count(*) FROM chunks").fetchone()[0]

            merkle_info = "UNSEALED"
            if "seals" in tables:
                seal_cols = [r[1] for r in conn.execute("PRAGMA table_info(seals)").fetchall()]
                root_col = next((c for c in seal_cols if "merkle" in c or "root" in c), None)
                if root_col:
                    seal = conn.execute(f"SELECT {root_col} FROM seals ORDER BY rowid DESC LIMIT 1").fetchone()
                    if seal and seal[0]:
                        merkle_info = seal[0][:24] + "..."

            conn.close()
            
            print(f"📦 Pod: {pod_name}")
            print(f"   Tables:           {', '.join(tables)}")
            print(f"   Documents/Ledger: {docs:,}")
            print(f"   Chunks:           {chunks:,}")
            print(f"   Merkle Seal:      {merkle_info}")
            print("-" * 65)
        except Exception as e:
            print(f"❌ Pod: {pod_name} [Error: {e}]")

if __name__ == "__main__":
    inspect()
