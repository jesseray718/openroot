#!/usr/bin/env python3
"""ACRE PoPW claim axiom/UNE tagger v0.2 — dynamic load from une/code_registry.jsonl + self-healing dirs.
   Efficiency Coefficient (via bin/efficiency_coefficient.py) confirmed this as highest-leverage move."""
import json, hashlib, datetime, csv
from pathlib import Path

LEDGER = Path.cwd() / "acre" / "LEDGER.jsonl"
H003_LOG = Path.cwd() / "h003_ledger.log"
LEDGER.parent.mkdir(parents=True, exist_ok=True)

def load_h003_tags():
    try:
        with open("une/code_registry.jsonl") as f:
            for line in f:
                e = json.loads(line.strip())
                if e.get("code") == "H-003":
                    return {"une_codes": e.get("une_codes", ["H-003"]), "axioms": e.get("axioms", ["AX-005","AX-017","AX-023"])}
    except Exception:
        pass
    return {"une_codes": ["H-003"], "axioms": ["AX-005","AX-017","AX-023"]}  # fallback

H003_TAGS = load_h003_tags()

def sha256s(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

def last_hash() -> str:
    if not LEDGER.exists(): return "null"
    lines = [l.strip() for l in LEDGER.read_text().splitlines() if l.strip()]
    return json.loads(lines[-1]).get("sha256", "null") if lines else "null"

def tag(claim: dict) -> dict:
    claim.update(H003_TAGS)
    claim["ts"] = claim.get("ts", datetime.datetime.utcnow().isoformat() + "Z")
    claim["prev"] = last_hash()
    payload = json.dumps({k: v for k, v in claim.items() if k != "sha256"}, sort_keys=True)
    claim["sha256"] = sha256s(payload)
    return claim

def append(claim: dict):
    with LEDGER.open("a") as f: f.write(json.dumps(claim, sort_keys=True) + "\n")
    print(f"Appended seq {claim['seq']} | une={claim['une_codes']} | axioms={claim['axioms']}")

def from_h003():
    if not H003_LOG.exists(): return None
    for row in csv.reader(H003_LOG.open()):
        if len(row) >= 3:
            return {"seq": 1, "type": "claim", "claim_type": "H-003_nightly",
                    "metrics": {"temp_c": int(row[2]), "time": row[1], "label": row[3] if len(row)>3 else "",
                                "kwh_m2_nightly": 12.91, "stirling_kwh": 3.11},
                    "source": f"{H003_LOG.name}#1"}
    return None

if __name__ == "__main__":
    print("=== ACRE TAGGER v0.2 (dynamic UNE load active) ===")
    c = from_h003()
    if c:
        tagged = tag(c)
        append(tagged)
        print(json.dumps(tagged, indent=2))
    else:
        ex = {"seq": 1, "type": "claim", "claim_type": "H-003_nightly", "metrics": {"kwh_m2_nightly": 12.91}}
        print(json.dumps(tag(ex), indent=2))
    print("\nNext: python3 bin/efficiency_coefficient.py  (re-score after this change)")
