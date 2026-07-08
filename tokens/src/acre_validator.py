#!/usr/bin/env python3
"""ACRE Token Validator — Two-Approval Mint Flow"""
import json, hashlib, datetime
from pathlib import Path
from dataclasses import dataclass, asdict, field

STATE_DIR = Path.home() / ".cache" / "acre"
STATE_FILE = STATE_DIR / "claims.json"
STATE_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class Claim:
    id: str
    claimant: str
    description: str
    novelty_score: int
    evidence_links: list
    validators_approved: list
    status: str
    created_at: str
    solana_tx: str = ""
    solana_address: str = ""

    def to_dict(self):
        return asdict(self)

class ACREValidator:
    def __init__(self):
        self.claims = self._load_claims()

    def _load_claims(self):
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                return [Claim(**c) for c in json.load(f)]
        return []

    def _save_claims(self):
        with open(STATE_FILE, "w") as f:
            json.dump([c.to_dict() for c in self.claims], f, indent=2)

    def submit_claim(self, claimant, description, novelty_score, evidence_links, solana_address=""):
        if not 1 <= novelty_score <= 10:
            raise ValueError("Novelty score must be 1-10")
        claim_id = f"CLM-{len(self.claims)+1:04d}-{claimant[:4].upper()}"
        claim = Claim(
            id=claim_id, claimant=claimant, description=description,
            novelty_score=novelty_score, evidence_links=evidence_links,
            validators_approved=[], status="pending",
            created_at=datetime.datetime.now().isoformat(),
            solana_address=solana_address
        )
        self.claims.append(claim)
        self._save_claims()
        print(f"Claim submitted: {claim_id}")
        return claim_id

    def approve_claim(self, claim_id, validator_name):
        for claim in self.claims:
            if claim.id == claim_id:
                if claim.status != "pending":
                    print(f"Claim already {claim.status}")
                    return False
                if validator_name not in claim.validators_approved:
                    claim.validators_approved.append(validator_name)
                if len(claim.validators_approved) >= 2:
                    claim.status = "approved_for_mint"
                    print(f"CLAIM READY FOR MINT! {claim_id}")
                else:
                    remaining = 2 - len(claim.validators_approved)
                    print(f"Approval recorded. {remaining} remaining.")
                self._save_claims()
                return True
        print(f"Claim not found: {claim_id}")
        return False

    def list_claims(self, filter_status=None):
        if not self.claims:
            print("No claims found.")
            return
        for c in self.claims:
            if filter_status and c.status != filter_status:
                continue
            print(f"\n[{c.status}] {c.id}")
            print(f"  Claimant: {c.claimant}")
            print(f"  Novelty: {c.novelty_score}/10")
            print(f"  Validators: {', '.join(c.validators_approved) if c.validators_approved else '(none)'}")
            if c.evidence_links:
                print(f"  Evidence: {c.evidence_links[0][:50]}...")
