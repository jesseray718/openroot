#!/usr/bin/env python3
"""Merge A15 and OptiPlex ideas ledgers"""
import json
import hashlib
from pathlib import Path

A15 = Path("/tmp/a15_ideas.jsonl")
OP = Path("/home/jesse/openroot/data/parallel_ideas.jsonl")
MERGED = Path("/home/jesse/openroot/data/reconciliation/merged.jsonl")

def load(p):
    if not p.exists(): return []
    entries = []
    with open(p) as f:
        for line in f:
            if line.strip():
                try: entries.append(json.loads(line))
                except: pass
    return entries

def entry_hash(e):
    clean = {k: v for k, v in e.items() if not k.startswith('_')}
    return hashlib.sha256(json.dumps(clean, sort_keys=True).encode()).hexdigest()[:16]

a15_entries = load(A15)
op_entries = load(OP)

print(f"A15: {len(a15_entries)}, OptiPlex: {len(op_entries)}")

seen = {}
merged = []
for e in op_entries:
    h = entry_hash(e)
    seen[h] = True
    merged.append(e)

added = 0
for e in a15_entries:
    h = entry_hash(e)
    if h not in seen:
        merged.append(e)
        seen[h] = True
        added += 1

MERGED.parent.mkdir(parents=True, exist_ok=True)
with open(MERGED, 'w') as f:
    for e in merged:
        f.write(json.dumps(e) + '\n')

print(f"Merged: {len(merged)} total, +{added} from A15")
print(f"Output: {MERGED}")
print(f"Size: {MERGED.stat().st_size:,} bytes")
