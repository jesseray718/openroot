#!/usr/bin/env python3
"""Consistent state + thermodynamic visualization (text)."""
import json, os, datetime
from collections import defaultdict

STATE = "/data/data/com.termux/files/home/openroot/ledger/system_state.json"
LEDGER = "/data/data/com.termux/files/home/openroot/ledger/thermo_ledger.json"

def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f: return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f: json.dump(data, f, indent=2)

def record_human(joules, task=""):
    """Human metabolic work ≈ 100 W sustained. Record as human_kwh."""
    data = load_json(LEDGER, {"entries": [], "totals": {}})
    entry = {
        "ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "type": "human",
        "kwh": joules / 3_600_000,          # J → kWh
        "note": task
    }
    data["entries"].append(entry)
    data["totals"]["human_kwh"] = data["totals"].get("human_kwh", 0) + entry["kwh"]
    save_json(LEDGER, data)
    print(f"Human work recorded: {entry['kwh']:.4f} kWh ({task})")

def visualize():
    data = load_json(LEDGER, {"entries": [], "totals": {}})
    totals = data.get("totals", {})
    print("\n=== THERMODYNAMIC STATE ===")
    print(f"Heat:     {totals.get('heat_kwh', 0):8.3f} kWh")
    print(f"Cold:     {totals.get('cold_kwh', 0):8.3f} kWh")
    print(f"Mech:     {totals.get('mech_kwh', 0):8.3f} kWh")
    print(f"Elec:     {totals.get('elec_kwh', 0):8.3f} kWh")
    print(f"Human:    {totals.get('human_kwh', 0):8.3f} kWh")
    useful = (totals.get("mech_kwh", 0) + totals.get("elec_kwh", 0) +
              0.3 * totals.get("heat_kwh", 0) + 0.3 * totals.get("cold_kwh", 0))
    human = totals.get("human_kwh", 0) or 1e-9
    eta = useful / human
    print(f"η (useful/human): {eta:.2f}")
    print("===========================\n")

    # simple ASCII bar for the five categories
    cats = ["heat_kwh", "cold_kwh", "mech_kwh", "elec_kwh", "human_kwh"]
    maxv = max((totals.get(c, 0) for c in cats), default=1) or 1
    for c in cats:
        v = totals.get(c, 0)
        bar = "█" * int(40 * v / maxv)
        print(f"{c:12} {v:7.3f} |{bar}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "human":
        j = float(sys.argv[2]) if len(sys.argv) > 2 else 360000   # default 0.1 kWh
        task = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else "manual labor"
        record_human(j, task)
    visualize()
