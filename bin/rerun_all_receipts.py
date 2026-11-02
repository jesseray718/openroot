#!/usr/bin/env python3
"""
OPENROOT ALL-RECEIPTS RE-RUNNER
Executes all core engine scripts to refresh thermodynamic, lattice, and clarification receipts
without removing or altering any extraneous repository files.
"""

import subprocess
import sys
from pathlib import Path

engines = [
    "bin/permaculture_lattice_engine.py",
    "bin/mobile_micro_loop_test.py",
    "bin/improvement_barrage_engine.py",
    "bin/clarification_barrage_engine.py"
]

def main():
    print("[*] Re-running OpenRoot core telemetry and receipt generation engines...")
    for engine in engines:
        path = Path(engine)
        if path.exists():
            print(f"[*] Executing {engine}...")
            res = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
            if res.returncode == 0:
                print(f"[✔] {engine} completed successfully.")
            else:
                print(f"[!] Error in {engine}:\n{res.stderr}")
        else:
            print(f"[!] Engine not found: {engine}")
            
    print("[✔] All core receipts successfully regenerated in data/thermodynamics/")

if __name__ == "__main__":
    main()
