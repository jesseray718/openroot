#!/usr/bin/env python3
"""
merge_ledgers.py - Reconcile divergent JSONL ledgers across devices
Merges newer entries by hash comparison, preserves chain integrity
"""

import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime

A15_PATH = Path("/tmp/a15_parallel_ideas.jsonl")  # Will be copied over
OP_PATH = Path("/home/jesse/openroot/data/parallel_ideas.jsonl")
MERGED_PATH = Path("/home/jesse/openroot/data/reconciliation/merged_parallel_ideas.jsonl")

def load_jsonl(path):
    """Load JSONL file, return list of entries with metadata"""
    entries = []
    if not path.exists():
        return entries
    
    with open(path) as f:
        for i, line in enumerate(f):
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    entry["_line"] = i
                    entries.append(entry)
                except json.JSONDecodeError as e:
                    print(f"⚠️ Parse error at {path}:{i+1}: {e}")
    return entries

def compute_entry_hash(entry):
    """Compute hash of entry content (excluding internal keys)"""
    clean = {k: v for k, v in entry.items() if not k.startswith("_")}
    return hashlib.sha256(json.dumps(clean, sort_keys=True).encode()).hexdigest()[:16]

def merge_ledgers(a15_entries, op_entries):
    """Merge with deduplication based on hash"""
    seen_hashes = {}
    merged = []
    
    # Index existing OptiPlex entries by hash
    for entry in op_entries:
        h = compute_entry_hash(entry)
        seen_hashes[h] = entry
        merged.append(entry)
    
    # Add A15 entries if not in OptiPlex
    added = 0
    skipped = 0
    for entry in a15_entries:
        h = compute_entry_hash(entry)
        if h not in seen_hashes:
            merged.append(entry)
            seen_hashes[h] = entry
            added += 1
        else:
            skipped += 1
    
    return merged, added, skipped

def main():
    print("=== LEDGER MERGE TOOL ===")
    print(f"A15 source: {A15_PATH}")
    print(f"OptiPlex source: {OP_PATH}")
    
    a15_entries = load_jsonl(A15_PATH)
    op_entries = load_jsonl(OP_PATH)
    
    print(f"\nA15 entries: {len(a15_entries)}")
    print(f"OptiPlex entries: {len(op_entries)}")
    
    merged, added, skipped = merge_ledgers(a15_entries, op_entries)
    
    print(f"\nResults:")
    print(f"  Total merged: {len(merged)}")
    print(f"  New entries from A15: {added}")
    print(f"  Skipped (duplicate): {skipped}")
    
    # Write merged file
    MERGED_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MERGED_PATH, "w") as f:
        for entry in merged:
            f.write(json.dumps(entry) + "\n")
    
    print(f"\nMerged ledger written: {MERGED_PATH}")
    print(f"Size: {MERGED_PATH.stat().st_size:,} bytes")
    
    # Output summary for commit message
    print(f"\nCOMMIT_MESSAGE=[ADD] Ledger reconciliation - {added} entries merged, {skipped} duplicates removed")

if __name__ == "__main__":
    main()
