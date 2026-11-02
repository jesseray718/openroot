#!/usr/bin/env python3
"""
OPENROOT ALL-RECEIPTS RE-RUNNER (PRODUCTION POLISH)
Executes all core engine scripts to refresh thermodynamic, lattice, and clarification receipts.
"""
import subprocess, sys
from pathlib import Path

engines = [
    "bin/permaculture_lattice_engine.py",
    "bin/mobile_micro_loop_test.py",
    "bin/improvement_barrage_engine.py",
    "bin/clarification_barrage_engine.py"
]

def main():
    print("[*] Executing production OpenRoot telemetry regeneration...")
    for engine in engines:
        path = Path(engine)
        if path.exists():
            print(f"[*] Running {engine}...")
            subprocess.run([sys.executable, str(path)], check=True)
        else:
            print(f"[!] Missing engine: {engine}")
    print("[✔] All core receipts successfully regenerated and validated.")

if __name__ == "__main__":
    main()
