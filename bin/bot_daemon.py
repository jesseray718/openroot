#!/usr/bin/env python3
"""
bot_daemon.py - Actually runs forever, restarting bot_loop after each cycle
"""

import subprocess
import time
import sys
import signal
from pathlib import Path
from datetime import datetime

BIN = Path("/home/jesse/openroot/bin")
LOGDIR = Path("/home/jesse/openroot/logs")

BOT_SCRIPT = BIN / "bot_loop_v1.py"
LOGFILE = LOGDIR / f"bot_daemon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

RUNNING = True
CYCLE_COUNT = 0

def signal_handler(sig, frame):
    global RUNNING
    RUNNING = False
    print("\nShutdown requested...")

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    global CYCLE_COUNT
    
    print("=== BOT DAEMON ===")
    print(f"Starting at: {datetime.now().isoformat()}")
    print(f"Logging to: {LOGFILE}")
    
    while RUNNING:
        CYCLE_COUNT += 1
        print(f"\n--- Cycle {CYCLE_COUNT} ---")
        
        start_time = time.time()
        
        try:
            proc = subprocess.run(
                [sys.executable, str(BOT_SCRIPT)],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour max per cycle
            )
            
            duration = time.time() - start_time
            
            # Log output
            with open(LOGFILE, "a") as log:
                log.write(f"--- Cycle {CYCLE_COUNT} ({duration:.1f}s) ---\n")
                if proc.stdout:
                    log.write(proc.stdout)
                if proc.stderr:
                    log.write(proc.stderr)
                log.write("\n")
            
            print(f"Cycle {CYCLE_COUNT} completed in {duration:.1f}s (exit code {proc.returncode})")
            
            # If exit code 0 = successful completion, wait before next cycle
            if proc.returncode == 0:
                print("Waiting 60 seconds before next cycle...")
                time.sleep(60)
            else:
                print(f"⚠️ Non-zero exit code {proc.returncode}, waiting 5 seconds...")
                time.sleep(5)
                
        except subprocess.TimeoutExpired:
            print(f"⚠️ Cycle {CYCLE_COUNT} timed out (1h limit)")
            time.sleep(10)
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(10)
    
    print(f"\nDaemon stopped after {CYCLE_COUNT} cycles")

if __name__ == "__main__":
    main()
