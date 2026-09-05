#!/usr/bin/env python3
"""
eta_agape.py — Computable η¹ η² η³ + Landauer floor + Agape root scoring
OpenRoot / UNE
"""

from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Optional

# -------------------------------------------------
# Root axiom
# -------------------------------------------------
AGAPE_ROOT = "A"
AGAPE_MEANING = (
    "Agape — unconditional, self-giving, ordered love "
    "that raises useful complexity and η for the lowest node"
)

# Boltzmann constant
K_BOLTZMANN = 1.380649e-23  # J/K
LN2 = 0.693147


# -------------------------------------------------
# Core η functions
# -------------------------------------------------
def eta1(useful_joules: float,
         people_reached: float,
         lasting_good: float,
         human_joules: float,
         time_seconds: float) -> float:
    """
    η¹ — Forward progress
    (useful_joules × people_reached × lasting_good) / (human_joules × time)
    """
    if human_joules <= 0 or time_seconds <= 0:
        return 0.0
    return (useful_joules * people_reached * lasting_good) / (human_joules * time_seconds)


def eta2(eta1_current: float, eta1_previous: float, dt: float) -> float:
    """η² — Acceleration of progress (dη¹/dt)"""
    if dt <= 0:
        return 0.0
    return (eta1_current - eta1_previous) / dt


def eta3(eta2_current: float, eta2_previous: float, dt: float) -> float:
    """η³ — Jerk (dη²/dt)"""
    if dt <= 0:
        return 0.0
    return (eta2_current - eta2_previous) / dt


# -------------------------------------------------
# Landauer floor
# -------------------------------------------------
def landauer_floor(bits: float, temperature_K: float = 300.0) -> float:
    """
    Minimum energy (joules) required to irreversibly erase the given number of bits
    at the stated temperature. Landauer's principle.
    """
    if bits <= 0 or temperature_K <= 0:
        return 0.0
    return bits * K_BOLTZMANN * temperature_K * LN2


def landauer_ratio(actual_joules: float, bits: float, temperature_K: float = 300.0) -> float:
    """
    How many times above the Landauer floor a real process is operating.
    Returns actual_joules / landauer_floor. Values >> 1 are normal for current technology.
    """
    floor = landauer_floor(bits, temperature_K)
    if floor <= 0:
        return float("inf")
    return actual_joules / floor


# -------------------------------------------------
# Agape + combined scoring
# -------------------------------------------------
def agape_score(eta1_value: float,
                raises_lowest_node: bool = True,
                verified: bool = False,
                bits_erased: float = 0.0,
                actual_joules_for_erasure: float = 0.0,
                temperature_K: float = 300.0) -> dict:
    """
    Combined scorer.
    - Always anchors to Agape root.
    - Optionally reports distance from Landauer floor when erasure data is supplied.
    """
    result = {
        "root": AGAPE_ROOT,
        "root_meaning": AGAPE_MEANING,
        "eta1": eta1_value,
        "raises_lowest_node": raises_lowest_node,
        "verified": verified,
        "aligned": bool(eta1_value > 0 and raises_lowest_node),
        "ts": time.time()
    }

    if bits_erased > 0 and actual_joules_for_erasure > 0:
        floor = landauer_floor(bits_erased, temperature_K)
        ratio = landauer_ratio(actual_joules_for_erasure, bits_erased, temperature_K)
        result["landauer"] = {
            "bits": bits_erased,
            "floor_joules": floor,
            "actual_joules": actual_joules_for_erasure,
            "times_above_floor": ratio
        }

    return result


# -------------------------------------------------
# Seed absorption
# -------------------------------------------------
def absorb_seed(json_path: str | Path) -> dict:
    """Load a context-bridge or mutual-understanding JSON seed."""
    path = Path(json_path)
    if not path.exists():
        return {"error": f"seed not found: {path}"}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "type": "context_bridge_seed",
        "source": str(path),
        "absorbed_at": time.time(),
        "payload": data
    }


# -------------------------------------------------
# Self-test
# -------------------------------------------------
if __name__ == "__main__":
    print("=== η + Agape + Landauer self-test ===")

    e1 = eta1(
        useful_joules=1200,
        people_reached=3,
        lasting_good=2.5,
        human_joules=400,
        time_seconds=3600
    )
    print(f"η¹ example: {e1:.6f}")

    floor = landauer_floor(bits=1e9, temperature_K=300)  # 1 Gbit
    print(f"Landauer floor for 1 Gbit @ 300 K: {floor:.6e} J")

    score = agape_score(
        eta1_value=e1,
        raises_lowest_node=True,
        verified=False,
        bits_erased=1e9,
        actual_joules_for_erasure=0.05,  # example real cost
        temperature_K=300
    )
    print("Combined score:")
    print(json.dumps(score, indent=2))
