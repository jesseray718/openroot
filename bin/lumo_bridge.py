#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
lumo_bridge.py - Connect local bot_loop to Lumo inbox
Sends queries via webhook/API, receives responses into ledger
"""

import json
import hashlib
import time
from pathlib import Path
from datetime import datetime

BASE = Path("/home/jesse/openroot")
INBOX = BASE / "lumo_inbox"
INBOX.mkdir(parents=True, exist_ok=True)

LEDGER = BASE / "data" / "lumo_exchange.jsonl"

CANARY = "LUMO_BRIDGE_V1"

def compute_hash(content):
    return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()[:16]

def send_to_lumo(topic, query, context=None):
    """Prepare query for Lumo inbox"""
    entry = {
        "ts": datetime.now().isoformat(),
        "topic": topic,
        "query": query,
        "context": context or {},
        "status": "pending",
        "canary": CANARY
    }
    entry["hash"] = compute_hash(entry)
    
    # Write to inbox for pickup
    inbox_file = INBOX / f"inbox_{entry['hash']}.json"
    with open(inbox_file, "w") as f:
        json.dump(entry, f, indent=2)
    
    # Also log to exchange ledger
    with open(LEDGER, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    return entry["hash"]

def receive_from_lumo(response_hash):
    """Check for Lumo response"""
    response_file = INBOX / f"outbox_{response_hash}.json"
    
    if response_file.exists():
        with open(response_file) as f:
            response = json.load(f)
        response["received_ts"] = datetime.now().isoformat()
        response["status"] = "processed"
        
        # Log to ledger
        with open(LEDGER, "a") as f:
            f.write(json.dumps(response) + "\n")
        
        return response
    
    return None

def scan_pending():
    """Scan inbox for pending queries"""
    pending = []
    for f in INBOX.glob("inbox_*.json"):
        if "outbox_" + f.name.replace("inbox_", "") not in [ff.name for ff in INBOX.glob("outbox_*.json")]:
            with open(f) as fh:
                pending.append(json.load(fh))
    return pending

def main():
    print("=== LUMO BRIDGE STATUS ===")
    print(f"Inbox: {INBOX}")
    print(f"Exchange ledger: {LEDGER}")
    print(f"Ledger entries: {sum(1 for _ in open(LEDGER)) if LEDGER.exists() else 0}")
    
    pending = scan_pending()
    print(f"Pending queries: {len(pending)}")
    
    for p in pending[:5]:
        print(f"  - {p['topic']}: {p['query'][:60]}...")
    
    print("\nTo add query:")
    print("  lumo_bridge.py send <topic> <query>")
    print("To check responses:")
    print("  lumo_bridge.py check")

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 3:
        send_to_lumo(sys.argv[1], " ".join(sys.argv[2:]))
        print(f"Queued: {CANARY}")
    elif len(sys.argv) >= 2 and sys.argv[1] == "check":
        responses = []
        for p in scan_pending():
            r = receive_from_lumo(p["hash"])
            if r:
                responses.append(r)
        print(f"Responses found: {len(responses)}")
    else:
        main()
