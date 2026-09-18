#!/usr/bin/env python3
import hashlib, json, glob
from pathlib import Path

STORE = Path("/home/jesse/openroot/axiom_engine/store")
CHAIN = STORE / "chain.jsonl"

def sha256_hex(b): return hashlib.sha256(b).hexdigest()
def dumps(obj): return json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False)
def content_hash(obj): return sha256_hex(dumps(obj).encode("utf-8"))

# discover all kind-specific jsonl files
index = {}  # id -> full record
files_found = []
for f in sorted(STORE.glob("*.jsonl")):
    if f.name == "chain.jsonl":
        continue
    files_found.append(f.name)
    for line in f.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        rid = rec.get("id")
        if rid:
            index[rid] = rec

print("Store files:", files_found)
print("Indexed records:", len(index))

if not CHAIN.exists():
    print("chain.jsonl missing")
    raise SystemExit(1)

lines = [l for l in CHAIN.read_text(encoding="utf-8").splitlines() if l.strip()]
total, valid, invalid = 0, 0, []

for i, line in enumerate(lines, 1):
    total += 1
    chain_rec = json.loads(line)
    claimed = chain_rec.get("hash")
    rid = chain_rec.get("id")
    kind = chain_rec.get("kind")

    full = index.get(rid)
    if full is None:
        invalid.append({"line": i, "id": rid, "reason": "not found in any store jsonl"})
        continue

    body = {
        "kind": kind,
        "id": full.get("id", rid),
        "statement": full.get("statement", ""),
        "premises": list(full.get("premises") or []),
        "proof": list(full.get("proof") or []),
    }
    computed = content_hash(body)

    if computed == claimed:
        valid += 1
    else:
        invalid.append({
            "line": i, "id": rid, "kind": kind,
            "claimed": claimed, "computed": computed,
            "body_fields": list(body.keys()),
        })

print(json.dumps({
    "total": total,
    "valid": valid,
    "invalid": invalid[:5],
    "status": "GREEN" if not invalid else "RED"
}, indent=2))
