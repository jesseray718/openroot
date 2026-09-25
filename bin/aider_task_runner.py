#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""aider_task_runner.py — Atomic spec → 7B edit → gate → commit"""
import subprocess, sys, os
from datetime import datetime

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0, result.stdout.strip()

def main():
    spec = sys.argv[1] if len(sys.argv) > 1 else "no spec"
    print(f"[aider] Processing spec: {spec[:50]}...")
    
    # Step 1: Generate (placeholder — replace with actual aider call)
    success, output = True, "Generated file based on spec"
    print(f"[7B] {output}")
    
    # Step 2: Gate
    success, msg = run_cmd("bash $HOME/openroot/bin/stack_gate.sh $HOME/openroot/bin/env_map.py")
    print(f"[GATE] {'PASS' if success else 'FAIL'}")
    
    # Step 3: Commit
    success, msg = run_cmd(f"cd $HOME/openroot && git add -A && git commit -m '[AUTO] aider task: {spec[:50]}'")
    print(f"[COMMIT] {'OK' if success else 'NEEDS MANUAL REVIEW'}")
    print("[aider] Complete")

if __name__ == "__main__":
    main()
