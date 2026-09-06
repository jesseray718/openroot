#!/usr/bin/env python3
import json, os, datetime, sys

LEDGER = "/data/data/com.termux/files/home/openroot/ledger/thermo_ledger.json"

def load():
    if os.path.exists(LEDGER):
        with open(LEDGER) as f: return json.load(f)
    return {"entries": [], "totals": {"heat_kwh": 0.0, "cold_kwh": 0.0, "mech_kwh": 0.0, "elec_kwh": 0.0}}

def save(data):
    with open(LEDGER, "w") as f: json.dump(data, f, indent=2)

def record(work_type, kwh, note=""):
    data = load()
    entry = {
        "ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "type": work_type,
        "kwh": float(kwh),
        "note": note
    }
    data["entries"].append(entry)
    key = work_type + "_kwh"
    data["totals"][key] = data["totals"].get(key, 0.0) + float(kwh)
    save(data)
    print(f"Recorded {kwh} kWh {work_type}. Total {work_type}: {data['totals'][key]:.3f}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 thermo_ledger.py <heat|cold|mech|elec> <kwh> [note]")
        sys.exit(1)
    note = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
    record(sys.argv[1], sys.argv[2], note)
