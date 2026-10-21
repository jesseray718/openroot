#!/usr/bin/env python3
# asset_preclassify.py — deterministic keyword routing of the inventory manifest
# classifies the obvious, isolates the ambiguous for 7B batches | read-only
import json, glob, os, hashlib, sys

INV = "/home/jesse/openroot/data/asset_inventory"
newest = max(glob.glob(f"{INV}/inventory_manifest_*.json"), key=os.path.getmtime)
print("[canary] paste intact | manifest:", newest)

inv = json.load(open(newest))
RULES = [
    ("dome/geometry",     ["dome_bom","geodesic","icosahedron","strut","chord","dome"]),
    ("dome/cutlist-bom",  ["cutlist","cut_list","bom","bill_of_material","cardboard_dome"]),
    ("aerocement/",       ["aerocement","aero_cement","opencell","open_cell","absorber","cement_mix"]),
    ("thermal/",          ["thermal","cascade","rmh","rocket_mass","labyrinth","psychrometric","stirling","uplift","cooling"]),
    ("rag-agents/",       ["rag","embedding","nomic","ollama","agent","aider","vector","retrieval"]),
    ("logic-engine/",     ["axiom","theorem","postulate","chain_verify","proof","canon","merkle"]),
    ("ledger-grants/",    ["ledger","grant","synthesis","acre","popw","attest","scribe","seed"]),
    ("docs/",             ["readme","handbook","guide","playbook","template","contribut","hando"]),
]

def route(path):
    p = path.lower()
    hits = [(b, len(k)) for b, kws in RULES for k in kws if k in p]
    if not hits: return None
    hits.sort(key=lambda x: -x[1])          # longest keyword match wins
    counts = {}
    for b, _ in hits: counts[b] = counts.get(b, 0) + 1
    return max(counts, key=counts.get)      # most-frequent bucket wins

assigned, residue = [], []
for r in inv:
    b = route(r["path"])
    (assigned if b else residue).append({**r, "bucket": b})

with open(f"{INV}/preclassified.json", "w") as f:
    json.dump(assigned, f, indent=1)
with open(f"{INV}/residue_for_coder.json", "w") as f:
    json.dump(residue, f, indent=1)

from collections import Counter
print(f"[observe] total={len(inv)} routed={len(assigned)} residue={len(residue)}")
for b, n in Counter(a["bucket"] for a in assigned).most_common():
    print(f"  {b:<20} {n}")
print(f"[banked] preclassified.json + residue_for_coder.json -> {INV}")
print("[next] if residue <= ~1200, batch the 7B over residue in chunks of 150;")
print("       if residue is huge, add rules and re-run (cheap) before spending model time")
