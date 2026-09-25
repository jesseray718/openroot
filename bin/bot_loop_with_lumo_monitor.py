#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
Wrapper: bot_loop + continuous Lumo inbox monitoring
Runs original bot_loop in background, monitors Lumo inbox simultaneously
"""

import subprocess
import time
import sys
from pathlib import Path

BIN = Path("/home/jesse/openroot/bin")
LOGDIR = Path("/home/jesse/openroot/logs")

BOT_SCRIPT = BIN / "bot_loop_v1.py"
LUMO_BRIDGE = BIN / "lumo_bridge.py"

def main():
    print("=== LUMO-INTEGRATED BOT LOOP ===")
    print(f"Starting bot_loop_v1.py...")
    
    # Start bot_loop in background
    bot_proc = subprocess.Popen(
        [sys.executable, str(BOT_SCRIPT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    print(f"Bot PID: {bot_proc.pid}")
    print("Monitoring Lumo inbox every 60 seconds...")
    
    # Main monitoring loop
    while True:
        time.sleep(60)
        
        # Check if bot still running
        if bot_proc.poll() is not None:
            print(f"⚠️ Bot died (return code {bot_proc.returncode})")
            print("Restarting...")
            bot_proc = subprocess.Popen(
                [sys.executable, str(BOT_SCRIPT)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            continue
        
        # Check Lumo inbox
        result = subprocess.run(
            [sys.executable, str(LUMO_BRIDGE), "check"],
            capture_output=True, text=True
        )
        
        if "responses found" in result.stdout:
            count = result.stdout.split("responses found")[0].split(":")[-1].strip()
            print(f"✨ Lumo responses ready: {count}")
            # Could auto-process here if desired
        
        # Print recent bot activity
        stdout_sample = bot_proc.stdout.read(200)
        if stdout_sample:
            print(f"[bot] {stdout_sample[:200]}")

if __name__ == "__main__":
    main()
