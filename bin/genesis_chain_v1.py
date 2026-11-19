#!/usr/bin/env python3
"""OpenRoot Genesis Chain v1 - compresses cache states and anchors a second genesis block."""
import argparse, hashlib, json, os, sqlite3, sys, time
from pathlib import Path

REPO = Path(os.environ.get("OPENROOT_REPO", "/home/jesse/openroot"))
CACHE_DB = REPO / "data" / "receipt_cache.db"
GENESIS_LEDGER = REPO / "data" / "genesis_chain.jsonl"

def get_latest_merkle_root(conn):
    """Compute a Merkle root over all current receipt cache entries."""
    cur = conn.execute("SELECT cache_key, dossier_sha256, ai_output FROM receipt_cache ORDER BY created_at ASC")
    h = hashlib.sha256()
    count = 0
    for row in cur.fetchall():
        h.update(row[0].encode())
        h.update(row[1].encode())
        h.update(hashlib.sha256(row[2].encode()).digest())
        count += 1
    return h.hexdigest(), count

def anchor_second_genesis():
    if not CACHE_DB.exists():
        print(f"[held] Cache DB not found at {CACHE_DB}")
        sys.exit(1)
        
    conn = sqlite3.connect(str(CACHE_DB))
    merkle_root, total_receipts = get_latest_merkle_root(conn)
    conn.close()

    # Read previous genesis if exists to form the chain
    prev_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    if GENESIS_LEDGER.exists():
        lines = GENESIS_LEDGER.read_text().strip().splitlines()
        if lines:
            last_block = json.loads(lines[-1])
            prev_hash = last_block.get("block_hash", prev_hash)

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    block_payload = {
        "block_index": 2, # Second Genesis Block chaining cached paths
        "previous_block_hash": prev_hash,
        "timestamp": timestamp,
        "receipts_count": total_receipts,
        "cache_merkle_root": merkle_root,
        "node_anchor": "optiplex3060-node-alpha-01"
    }
    
    block_string = json.dumps(block_payload, sort_keys=True)
    block_hash = hashlib.sha256(block_string.encode()).hexdigest()
    block_payload["block_hash"] = block_hash

    with open(GENESIS_LEDGER, "a") as f:
        f.write(json.dumps(block_payload) + "\n")

    print(json.dumps(block_payload, indent=2))
    print(f"[banked] Second Genesis Block successfully chained and anchored: {block_hash}")

if __name__ == "__main__":
    anchor_second_genesis()
