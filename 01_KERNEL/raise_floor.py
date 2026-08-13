#!/usr/bin/env python3
"""
OPENROOT RAISE_FLOOR PROTOCOL
Goal: (Max Good / Min Effort)^6
Logic: Identify lowest node -> Apply surplus -> Raise floor -> Repeat.
"""
import os, sys, json, math, time
from pathlib import Path
from datetime import datetime

PHI = (1 + math.sqrt(5)) / 2
REPO_ROOT = Path(__file__).parent.parent

def load_node_stats(node_name):
    stats = {
        "termux_android": {"cpu_load": 0.8, "ram_mb": 1200, "efficiency": 0.4},
        "raspberry_pi": {"cpu_load": 0.3, "ram_mb": 800, "efficiency": 0.7},
        "alpine_linux": {"cpu_load": 0.1, "ram_mb": 200, "efficiency": 0.95}
    }
    return stats.get(node_name, {"efficiency": 0.0})

def calculate_surplus(high, low):
    return (high.get("efficiency", 0) - low.get("efficiency", 0)) * PHI

def propose_opt(low_name, surplus):
    if surplus > 0.2:
        return {"action": "Migrate heavy compute to cloud/server", "effort": "Low", "impact": "High"}
    elif surplus > 0.1:
        return {"action": "Optimize local caching", "effort": "Very Low", "impact": "Medium"}
    else:
        return {"action": "Hardware upgrade (Solar/Battery)", "effort": "Medium", "impact": "Critical"}

def main():
    print("=" * 60)
    print("OPENROOT: RAISE FLOOR PROTOCOL")
    print("(Max Good / Min Effort)^6")
    print("=" * 60)

    nodes = ["termux_android", "raspberry_pi", "alpine_linux"]
    stats = {n: load_node_stats(n) for n in nodes}

    lowest = min(stats, key=lambda k: stats[k]["efficiency"])
    highest = max(stats, key=lambda k: stats[k]["efficiency"])

    print(f"\n[SCAN] Lowest Node: {lowest} (Eff: {stats[lowest]['efficiency']:.2f})")
    print(f"[SCAN] Highest Node: {highest} (Eff: {stats[highest]['efficiency']:.2f})")

    surplus = calculate_surplus(stats[highest], stats[lowest])
    proposal = propose_opt(lowest, surplus)

    print(f"\n[SURPLUS] Available: {surplus:.2f} units")
    print(f"[ACTION] {proposal['action']} (Effort: {proposal['effort']}, Impact: {proposal['impact']})")

    ledger = REPO_ROOT / "04_DATA" / "floor_raise_log.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(),
        "lowest": lowest,
        "surplus": surplus,
        "proposal": proposal
    }
    with open(ledger, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"\n[LOGGED] Entry saved to {ledger}")
    print("=" * 60)
    print("NEXT: Implement proposal. Measure new floor. Repeat.")
    print("=" * 60)

if __name__ == "__main__":
    main()
