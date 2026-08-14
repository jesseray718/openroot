#!/usr/bin/env python3
"""
ACRE Validator v0.2 — Proof of Innovation mint flow (ACRE_SPECIFICATION.md)
Two-validator | PoPW only (no repetition) | UNE claim types | demo mode
"""

import argparse
import json
import sys
import datetime
from dataclasses import dataclass, asdict
from typing import List

@dataclass
class Claim:
    claim_id: str
    claim_type: str
    description: str
    evidence: List[str]
    submitter: str
    timestamp: str
    status: str = "pending"
    validators: List[str] = None
    notes: str = ""

    def __post_init__(self):
        if self.validators is None:
            self.validators = []

VALID_CATEGORIES = {
    "HW.VAL.NODE.ZERO": "First Node new climate zone (15k-20k ACRE) — e.g. Sikeston Node Zero thermal data",
    "HW.FIX.BUG": "Hardware bug fix/optimization (5k-50k)",
    "SW.TOOL.NEW": "New tool/script (5k-50k)",
    "SW.FIX.BUG": "Software bug fix (1k-20k)",
    "SW.OPT": "Optimization/refactor (2k-30k)",
    "DOC.SKILL.NEW": "New skill document (5k-20k)",
    "VAL.INSP": "Validator inspection (100 ACRE)",
}

def is_innovation(claim_type: str, description: str) -> bool:
    if any(x in claim_type for x in ["REP.", "MONITOR.", "COPY."]):
        return False
    if "replicate" in description.lower() and "exact" in description.lower():
        return False
    return True

def submit_claim(claim_type: str, description: str, evidence: List[str], submitter: str) -> Claim:
    if claim_type not in VALID_CATEGORIES:
        raise ValueError(f"Invalid claim_type. Allowed: {list(VALID_CATEGORIES.keys())}")
    if not is_innovation(claim_type, description):
        raise ValueError("PoPW gate: repetition or monitoring only — earns 0 ACRE.")
    cid = f"ACRE-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{claim_type.split('.')[0]}"
    return Claim(cid, claim_type, description, evidence, submitter,
                 datetime.datetime.utcnow().isoformat() + "Z")

def approve_claim(claim: Claim, validator: str, note: str = "") -> Claim:
    if validator in claim.validators:
        return claim
    claim.validators.append(validator)
    if note:
        claim.notes += f" | {validator}: {note}"
    if len(claim.validators) >= 2:
        claim.status = "approved"
    return claim

def finalize_mint_ready(claim: Claim) -> dict:
    if claim.status != "approved":
        raise ValueError("Needs exactly 2 independent validator approvals.")
    claim.status = "mint_ready"
    return {
        "claim": asdict(claim),
        "acre_potential": VALID_CATEGORIES.get(claim.claim_type, "TBD per spec"),
        "mint_ready_for": "Solana + IPFS memo (after 3 validated nodes + legal)",
        "governance_note": "Quadratic voting. No entity >2%. Community supreme. No pre-mine.",
        "philosophy": "Proof of Innovation only. Builders advancing the commons get paid. Repetition earns zero."
    }

def run_demo():
    print("=== ACRE v0.2 DEMO: H-003 Node Zero thermal data claim (matches spec A1) ===")
    claim = submit_claim(
        "HW.VAL.NODE.ZERO",
        "First thermal data log for H-003 v0.6 at Sikeston Node Zero — 12.91 kWh nightly, 82.98 kWh/7 nights, desiccant placement debugged upstream, published to commons",
        [
            "ipfs://QmcMjnAVN9FbQ77VwMPMCteb93U7W4REdZmZbPqoMBE4F",
            "https://zenodo.org/records/21210931",
            "https://github.com/jesseray718/aerocement",
            "https://github.com/jesseray718/openroot"
        ],
        "Jesse"
    )
    print("SUBMITTED:", json.dumps(asdict(claim), indent=2))

    claim = approve_claim(claim, "Validator-Alpha", "Data validates multi-night radiative cooling + actionable humid-climate fix")
    print("\nAPPROVED (1/2):", json.dumps(asdict(claim), indent=2))

    claim = approve_claim(claim, "Validator-Beta", "Cross-checked vs Zenodo v0.4 dataset + SPEC-H003. Ready for v0.6 PR.")
    print("\nAPPROVED (2/2):", json.dumps(asdict(claim), indent=2))

    record = finalize_mint_ready(claim)
    print("\n=== MINT_READY RECORD (publish this to IPFS + Zenodo + openroot PR) ===")
    print(json.dumps(record, indent=2))
    print("\nNext real step: run aerocement/scripts/data_logger.py on A15 → replace evidence links → re-submit for actual claim.")

def main():
    parser = argparse.ArgumentParser(
        description="ACRE Validator — Proof of Innovation (pre-launch prototype)",
        epilog="See ACRE_SPECIFICATION.md for payout tables and rules. No tokens exist yet."
    )
    sub = parser.add_subparsers(dest="action", required=True)

    p_sub = sub.add_parser("submit", help="Submit new innovation claim")
    p_sub.add_argument("claim_type", choices=list(VALID_CATEGORIES.keys()))
    p_sub.add_argument("description")
    p_sub.add_argument("evidence_csv", help="Comma-separated IPFS/Zenodo/GitHub links")
    p_sub.add_argument("submitter")

    p_app = sub.add_parser("approve", help="Validator approves a claim JSON")
    p_app.add_argument("claim_json")
    p_app.add_argument("validator")
    p_app.add_argument("note", nargs="?", default="")

    p_fin = sub.add_parser("finalize", help="Finalize approved claim to mint_ready record")
    p_fin.add_argument("claim_json")

    sub.add_parser("demo", help="Run full H-003 / Node Zero example end-to-end")

    args = parser.parse_args()

    if args.action == "submit":
        ev = [e.strip() for e in args.evidence_csv.split(",") if e.strip()]
        claim = submit_claim(args.claim_type, args.description, ev, args.submitter)
        print(json.dumps(asdict(claim), indent=2))
    elif args.action == "approve":
        with open(args.claim_json) as f:
            data = json.load(f)
        claim = Claim(**data)
        claim = approve_claim(claim, args.validator, args.note)
        print(json.dumps(asdict(claim), indent=2))
    elif args.action == "finalize":
        with open(args.claim_json) as f:
            data = json.load(f)
        claim = Claim(**data)
        record = finalize_mint_ready(claim)
        print(json.dumps(record, indent=2))
    elif args.action == "demo":
        run_demo()

if __name__ == "__main__":
    main()
