#!/usr/bin/env python3
import json
from pathlib import Path

STORE = Path("/home/jesse/openroot/axiom_engine/store")

def load_from_file(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

def append_to_jsonl(filepath, records):
    with filepath.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=True, separators=(",",":")) + "\n")

if __name__ == "__main__":
    defs = load_from_file(STORE / "euclid_defs_import.txt")
    axioms = load_from_file(STORE / "euclid_axioms_import.txt")
    
    append_to_jsonl(STORE / "definitions.jsonl", defs)
    append_to_jsonl(STORE / "axioms.jsonl", axioms)
    
    print(f"Imported {len(defs)} definitions")
    print(f"Imported {len(axioms)} axioms")
    print("Done — run theorems_extend.py audit to verify")
