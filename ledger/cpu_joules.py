#!/usr/bin/env python3
"""Estimate CPU energy from wall time and a measured or assumed power draw."""
import time, json, os, datetime

STATE = "/data/data/com.termux/files/home/openroot/ledger/cpu_energy.json"

def record_cpu(seconds, watts=2.5, note=""):
    """Default 2.5 W is a realistic average for a phone CPU under load."""
    joules = seconds * watts
    kwh = joules / 3_600_000
    data = {"ts": datetime.datetime.now().isoformat(timespec="seconds"),
            "seconds": seconds, "watts": watts, "joules": joules, "kwh": kwh, "note": note}
    history = []
    if os.path.exists(STATE):
        with open(STATE) as f: history = json.load(f)
    history.append(data)
    with open(STATE, "w") as f: json.dump(history, f, indent=2)
    print(f"CPU: {joules:.1f} J ({kwh:.6f} kWh) — {note}")
    return joules

if __name__ == "__main__":
    import sys
    sec = float(sys.argv[1]) if len(sys.argv) > 1 else 10
    note = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "manual"
    record_cpu(sec, note=note)
