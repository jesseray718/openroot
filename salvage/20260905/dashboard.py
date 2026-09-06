#!/data/data/com.termux/files/usr/bin/python3
"""
OPENROOT PUSH-BUTTON ENGINE  R=1.0
η = useful_joules / human_joules
Absolute paths only. Zero navigation cost.
"""
import os, sys, subprocess, json
from pathlib import Path

SCRIPTS = {
    "1": {
        "name": "TIEMIT Genesis Hash (VOID root)",
        "path": "/sdcard/openroot/tiemit/genesis/genesis_void.py"
    },
    "2": {
        "name": "Structure Enforcer (joule-native scan)",
        "path": "/data/data/com.termux/files/home/une/computational_flow/structure_enforcer.py"
    },
    "3": {
        "name": "Agape Engine Interactive",
        "path": "/data/data/com.termux/files/home/une/computational_flow/agape_engine.py",
        "args": ["interactive"]
    },
    "4": {
        "name": "Context Bridge Status",
        "path": "/sdcard/openroot/context_bridge/context.json",
        "mode": "read"
    },
    "5": {
        "name": "Syncthing Integrity Probe",
        "path": "/data/data/com.termux/files/home/openroot/core/sync_check.py"
    },
    "6": {
        "name": "Auto-discover all .py under openroot + une",
        "path": "DISCOVER"
    },
}

def discover():
    roots = [
        Path("/sdcard/openroot"),
        Path("/data/data/com.termux/files/home/openroot"),
        Path("/data/data/com.termux/files/home/une"),
        Path("/data/data/com.termux/files/home/kai9000"),
    ]
    found = []
    for root in roots:
        if root.exists():
            for p in root.rglob("*.py"):
                found.append(str(p))
    return sorted(found)

def main():
    while True:
        print("\n" + "="*52)
        print("  OPENROOT PUSH-BUTTON ENGINE   R=1.0   C=0")
        print("  η = useful_joules / human_joules")
        print("="*52)
        for k, v in SCRIPTS.items():
            print(f"  [{k}]  {v['name']}")
        print("  [Q]  Exit")
        print("="*52)
        choice = input("Select: ").strip().lower()
        if choice == "q":
            break
        if choice not in SCRIPTS:
            print("Invalid")
            continue
        entry = SCRIPTS[choice]
        if entry["path"] == "DISCOVER":
            for f in discover():
                print(f)
            continue
        target = entry["path"]
        if entry.get("mode") == "read":
            p = Path(target)
            if p.exists():
                print(p.read_text())
            else:
                print(f"[MISSING] {target}")
            continue
        if not Path(target).exists():
            print(f"[MISSING] {target}")
            continue
        args = [sys.executable, target] + entry.get("args", [])
        print(f"\n[!] EXEC  {' '.join(args)}")
        subprocess.call(args)

if __name__ == "__main__":
    main()
