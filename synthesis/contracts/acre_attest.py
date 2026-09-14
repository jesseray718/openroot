#!/usr/bin/env python3
"""acre_attest.py — off-chain claim signer; on-chain mint is gated to MEASURED rows."""
from dataclasses import dataclass, asdict
import hashlib, json, time

@dataclass
class Attestation:
    source: str; joules: float; grade: str; ts: str
    def digest(self):
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True).encode()).hexdigest()

def attest(source, joules, grade="MODEL"):
    assert grade in ("MEASURED", "MODEL")
    return Attestation(source, joules, grade, time.strftime("%Y-%m-%dT%H:%M:%SZ"))
