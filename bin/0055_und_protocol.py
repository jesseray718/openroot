#!/usr/bin/env python3
"""
und_protocol.py — Universal Native Descriptor (und) Protocol
Zero-dependency encoder / decoder + Newton Chain validator
R_EQUILIBRIUM = 0.8158
"""

import json
import re
import time
from dataclasses import dataclass
from typing import Dict, List, Any, Tuple, Optional

R_EQUILIBRIUM: float = 0.8158


class NewtonChainValidator:
    @staticmethod
    def validate(delta_e_kw: float, delta_r: float, max_r: float = R_EQUILIBRIUM) -> Tuple[str, bool]:
        is_valid = (delta_r <= max_r) and (delta_e_kw >= 0.0 or abs(delta_e_kw) <= 100.0)
        status = "VERIFIED" if is_valid else "REJECTED"
        sign = "+" if delta_e_kw >= 0 else ""
        proof_str = f"#NC[dE={sign}{delta_e_kw:.1f}kW,dR={delta_r:.4f},status={status}]"
        return proof_str, is_valid


@dataclass
class UNDClause:
    opcode: str
    domain: str
    attributes: Dict[str, Any]

    def to_und(self) -> str:
        attrs_str = ",".join(f"{k}:{v}" for k, v in self.attributes.items())
        return f"{self.opcode}{self.domain}{{{attrs_str}}}"


class UNDEncoder:
    def __init__(self, node_id: str = "NZ-01", r_limit: float = R_EQUILIBRIUM):
        self.node_id = node_id
        self.r_limit = r_limit

    def encode(self, telemetry: Dict[str, Any], delta_e_kw: float = 0.0, delta_r: float = 0.0) -> str:
        timestamp = telemetry.get("timestamp", int(time.time()))
        header = f"[{self.node_id}|{timestamp}|R={self.r_limit:.4f}]"
        clauses = []
        for raw_c in telemetry.get("clauses", []):
            clause = UNDClause(
                opcode=raw_c["opcode"],
                domain=raw_c["domain"],
                attributes=raw_c["attributes"]
            )
            clauses.append(clause.to_und())
        clause_sequence = ";".join(clauses)
        proof_block, _ = NewtonChainValidator.validate(delta_e_kw, delta_r, self.r_limit)
        return f"{header}::{clause_sequence}::{proof_block}"


class UNDDecoder:
    FRAME_REGEX = re.compile(
        r"^\[(?P<node>[^|]+)\|(?P<ts>\d+)\|R=(?P<r>[\d\.]+)\]::(?P<clauses>.*?)::(?P<proof>#NC\[.*?\])$"
    )
    PROOF_REGEX = re.compile(
        r"#NC\[dE=(?P<de>[^,]+),dR=(?P<dr>[\d\.]+),status=(?P<status>VERIFIED|REJECTED)\]"
    )
    CLAUSE_REGEX = re.compile(r"([!?\~=%])(@[A-Z]+)\{([^}]+)\}")

    @classmethod
    def decode(cls, und_frame: str) -> Dict[str, Any]:
        match = cls.FRAME_REGEX.match(und_frame.strip())
        if not match:
            raise ValueError("Malformed UND frame structure.")
        groups = match.groupdict()
        parsed_clauses = []
        if groups["clauses"]:
            for raw_c in groups["clauses"].split(";"):
                c_match = cls.CLAUSE_REGEX.match(raw_c)
                if c_match:
                    opcode, domain, raw_attrs = c_match.groups()
                    attrs = {}
                    for item in raw_attrs.split(","):
                        if ":" in item:
                            k, v = item.split(":", 1)
                            attrs[k.strip()] = v.strip()
                    parsed_clauses.append({
                        "opcode": opcode,
                        "domain": domain,
                        "attributes": attrs
                    })
        p_match = cls.PROOF_REGEX.match(groups["proof"])
        if not p_match:
            raise ValueError("Invalid Newton Chain proof block.")
        p_groups = p_match.groupdict()
        return {
            "node_id": groups["node"],
            "timestamp": int(groups["ts"]),
            "r_equilibrium": float(groups["r"]),
            "clauses": parsed_clauses,
            "newton_chain": {
                "delta_e": p_groups["de"],
                "delta_r": float(p_groups["dr"]),
                "status": p_groups["status"],
                "verified": p_groups["status"] == "VERIFIED"
            }
        }


if __name__ == "__main__":
    json_telemetry = {
        "timestamp": 1723284299,
        "clauses": [
            {"opcode": "?", "domain": "@THM", "attributes": {"T_sol": "330.15K"}},
            {"opcode": "?", "domain": "@PWR", "attributes": {"V_bat": "23.4V"}},
            {"opcode": "!", "domain": "@THM", "attributes": {"relay_1": "ON", "tgt": "bench_mass"}}
        ]
    }
    encoder = UNDEncoder(node_id="NZ-01")
    und_frame = encoder.encode(json_telemetry, delta_e_kw=1.2, delta_r=0.7410)
    print("--- ENCODED ---")
    print(und_frame)
    decoder = UNDDecoder()
    decoded = decoder.decode(und_frame)
    print("\n--- DECODED ---")
    print(json.dumps(decoded, indent=2))
