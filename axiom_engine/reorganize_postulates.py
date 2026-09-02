#!/usr/bin/env python3
"""reorganize_postulates.py - Move Euclid postulates from axioms to postulates file."""
import json
from pathlib import Path

STORE = Path("/home/jesse/openroot/axiom_engine/store")

# Read axioms
axioms_file = STORE / "axioms.jsonl"
postulates_file = STORE / "postulates.jsonl"

axioms_lines = axioms_file.read_text(encoding="utf-8").splitlines()
postulates_lines = postulates_file.read_text(encoding="utf-8").splitlines() if postulates_file.exists() else []

# Euclid postulate IDs (already in axioms)
euclid_postulate_ids = [
    "AX-POSTULATE-1", "AX-POSTULATE-2", "AX-POSTULATE-3",
    "AX-POSTULATE-4", "AX-POSTULATE-5"
]

kept_axioms = []
moved_postulates = []

for line in axioms_lines:
    if not line.strip():
        continue
    rec = json.loads(line)
    if rec.get("id") in euclid_postulate_ids:
        # Convert to postulate format
        rec["kind"] = "postulate"
        moved_postulates.append(rec)
    else:
        kept_axioms.append(rec)

# Write remaining axioms back
with axioms_file.open("w", encoding="utf-8") as f:
    for r in kept_axioms:
        f.write(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n")

# Write postulates
with postulates_file.open("w", encoding="utf-8") as f:
    # Keep any existing postulates not being replaced
    for line in postulates_lines:
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("id") not in euclid_postulate_ids:
            f.write(line + "\n")
    # Add Euclid postulates
    for p in moved_postulates:
        f.write(json.dumps(p, sort_keys=True, separators=(",", ":")) + "\n")

print(f"Moved {len(moved_postulates)} postulates to postulates.jsonl")
print(f"Kept {len(kept_axioms)} axioms in axioms.jsonl")
print("Run theorems_extend.py audit to verify counts")
