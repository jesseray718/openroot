#!/usr/bin/env python3
import os
import shutil
import sqlite3
import subprocess
from datetime import datetime, timezone

OPENROOT_HOME = os.getenv("OPENROOT_HOME", os.path.expanduser("~/openroot"))
DB_FILE = os.path.join(OPENROOT_HOME, "data", "knowledge.db")
LEDGER_SCRIPT = os.path.join(OPENROOT_HOME, "scripts", "ledger.py")

def check_disk_space():
    total, used, free = shutil.disk_usage(OPENROOT_HOME)
    free_gb = free / (2**30)
    percent_free = (free / total) * 100
    status = f"Disk Space: {free_gb:.2f} GB free ({percent_free:.1f}% available)"
    return status, percent_free > 5.0  # Alert if under 5%

def check_db_integrity():
    if not os.path.exists(DB_FILE):
        return "Database not initialized yet.", True
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()
        conn.close()
        is_ok = result and result[0] == "ok"
        return f"SQLite Integrity Check: {result[0]}", is_ok
    except Exception as e:
        return f"Database integrity error: {e}", False

def run_health_check():
    print(f"=== Running Agape Edge Health Check @ {datetime.now(timezone.utc).isoformat()} ===")
    
    disk_msg, disk_ok = check_disk_space()
    print(f"  - {disk_msg}")
    
    db_msg, db_ok = check_db_integrity()
    print(f"  - {db_msg}")
    
    overall_status = "HEALTHY" if (disk_ok and db_ok) else "DEGRADED"
    print(f"=== System Status: {overall_status} ===")
    
    # Log telemetry entry via ledger script if healthy/degraded
    if os.path.exists(LEDGER_SCRIPT):
        log_content = f"Health Check Status: {overall_status} | {disk_msg} | {db_msg}"
        subprocess.run(["python3", LEDGER_SCRIPT, "append", log_content, "telemetry,health"])

if __name__ == "__main__":
    run_health_check()
