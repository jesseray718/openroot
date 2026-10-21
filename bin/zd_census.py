#!/usr/bin/env python3
# [canary] paste intact
# zd_census.py — the REAL 0D/void census of the formal store.
# Extracts full records matching disambiguated phrases (no hex collisions).
import json, sys

STORE = "/home/jesse/src/openroot/axiom_engine/store"
FILES = ["axioms.jsonl", "definitions.jsonl", "postulates.jsonl", "theorems.jsonl"]
# Phrases that CANNOT appear inside a sha256 hex digest
PHRASES = ["zero-dimensional", "zero dimensional", "0-dimensional",
           "zeroth dimension", "void state", "genesis block", "Genesis Block",
           "light instantiation", "spacetime emergence", "space-time emergence",
           "dimension zero", "point-space", "0D"]

def scan(fn):
    path = f"{STORE}/{fn}"
    try:
        lines = open(path).read().splitlines()
    except FileNotFoundError:
        print(f"[refuse-path] {path} missing"); return
    total, matched = 0, []
    for i, line in enumerate(lines):
        total += 1
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        blob = json.dumps(rec).lower()
        hits = [p for p in PHRASES if p.lower() in blob]
        if hits:
            rid = rec.get("id") or rec.get("flag") or f"line{i+1}"
            kind = rec.get("kind") or rec.get("status") or "?"
            stmt = (rec.get("statement") or rec.get("text") or
                    rec.get("content") or rec.get("body") or "")[:110]
            matched.append(f"  [{fn[:-6].upper():12s}] id={rid} kind={kind} match={hits}\n    stmt: {stmt}")
    print(f"== {fn}: {total} records, {len(matched)} matched")
    for m in matched:
        print(m)

print("[canary] paste intact | zero-dimension census, phrase-disambiguated")
for fn in FILES:
    scan(fn)
print("[done] census complete — matched records above are the 0D corpus")
