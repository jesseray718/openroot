#!/usr/bin/env python3
"""
core_atomic.py — order-0 atoms only
f1 measure, f2 axiom score, f3 merkle, Landauer, η, ARM energy, E=mc² residual
Every function returns joules or a hash. No side effects beyond the return value.
"""

import hashlib
import time
from typing import Dict, Tuple

LANDAUER = 2.85e-21          # J/bit @ 300 K
ARM_J_PER_CYCLE = 1.2e-10   # rough Helio G99 scale

def f1_capture(data: bytes) -> Tuple[str, float]:
    """Capture + hash. Returns (sha256, human_joules)."""
    h = hashlib.sha256(data).hexdigest()
    bits = len(data) * 8
    human_j = bits * LANDAUER * 1e9   # scaled for visibility
    return h, human_j

def f2_landauer(bits_erased: int) -> float:
    """Irreversible bit cost."""
    return bits_erased * LANDAUER * 1e9

def f3_merkle(leaves: list) -> str:
    """Binary merkle root. Returns hex."""
    if not leaves:
        return hashlib.sha256(b"empty").hexdigest()
    layer = [hashlib.sha256(x.encode() if isinstance(x, str) else x).hexdigest() for x in leaves]
    while len(layer) > 1:
        nxt = []
        for i in range(0, len(layer), 2):
            left = layer[i]
            right = layer[i+1] if i+1 < len(layer) else left
            nxt.append(hashlib.sha256((left + right).encode()).hexdigest())
        layer = nxt
    return layer[0]

def f4_eta(useful_j: float, human_j: float) -> float:
    """η = useful / human. Never divide by zero."""
    return useful_j / human_j if human_j > 0 else 0.0

def f5_arm_energy(cycles: int, freq_mhz: float = 650.0) -> float:
    """Measured-style ARM energy at given frequency."""
    # lower frequency → higher η on this silicon
    scale = 2000.0 / max(freq_mhz, 100.0)
    return cycles * ARM_J_PER_CYCLE * scale

def f6_emc2_residual(mass_kg: float = 1e-12) -> float:
    """Symbolic residual energy from mass (E=mc²). Used only as upper bound."""
    c = 299792458.0
    return mass_kg * c * c

def f7_commit(trace: Dict) -> str:
    """Immutable commit of any dict → merkle leaf."""
    blob = str(sorted(trace.items())).encode()
    return hashlib.sha256(blob).hexdigest()

def f8_raise_order(node_id: str, order: int) -> str:
    """Sparse raise. Returns new node id only."""
    return f"{node_id}_o{order+1}"

def f9_bottleneck(etas: Dict[str, float]) -> str:
    """Return id of lowest η node."""
    if not etas:
        return "none"
    return min(etas, key=etas.get)

def f10_acre_seed(merkle_root: str) -> str:
    """Mint the claim string."""
    return f"PoCW:{merkle_root[:16]}"

def f11_sensor_condition(sensor: Dict, threshold: float = 0.85) -> str:
    """Sensor → condition → possibility. Returns action string."""
    η = sensor.get("η", 0.0)
    if η >= threshold:
        return "HOLD"
    if η < 0.40:
        return "RAISE_ORDER"
    return "APPLY_AXIOM"

if __name__ == "__main__":
    # self-test: produce one real ACRE seed
    data = b"openroot-core-atomic"
    h, hj = f1_capture(data)
    leaves = [h, f7_commit({"t": time.time(), "η_law": "useful/human"})]
    root = f3_merkle(leaves)
    claim = f10_acre_seed(root)
    print({"hash": h, "human_j": hj, "merkle": root, "claim": claim})
