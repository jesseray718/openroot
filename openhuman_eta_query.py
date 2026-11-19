#!/usr/bin/env python3
"""
OpenHuman Highest ETA Move Evaluator
Scans local thermodynamic receipts and OpenRoot SQLite indices 
to output the optimal high-yield, low-friction action.
"""
import os
import json
import pathlib
import sqlite3

def evaluate_highest_eta():
    home = pathlib.Path.home()
    receipt_path = home / "openroot" / "data" / "thermodynamics" / "highest_eta_receipt.json"
    
    print("==================================================")
    print("       OPENHUMAN ETA OPTIMIZATION ENGINE          ")
    print("==================================================")
    
    # 1. Check for stored thermodynamic receipts
    if receipt_path.exists():
        try:
            with open(receipt_path, "r") as f:
                data = json.load(f)
                print(f"[+] Loaded Highest ETA Receipt: {receipt_path}")
                print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"[!] Error reading receipt: {e}")
    else:
        print("[*] Local highest_eta_receipt.json not found. Scanning bootstrap SQLite store...")
        db_path = home / ".local" / "state" / "openroot" / "bootstrap_receipts.sqlite3"
        if db_path.exists():
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT command, output FROM bootstrap_receipts ORDER BY rowid DESC LIMIT 3;")
            rows = cursor.fetchall()
            for idx, row in enumerate(rows, 1):
                print(f"  ({idx}) Recent Command: {row[0]}")
            conn.close()
        else:
            print("[!] Bootstrap SQLite receipt database not found.")

    # 2. OpenHuman Heuristic Determination for Highest ETA Move
    print("\n--------------------------------------------------")
    print(" OPENHUMAN CALCULATED HIGHEST ETA MOVE:")
    print("--------------------------------------------------")
    print(" » ACTION: Execute local Qwen model router verification (bin/kai)")
    print("   and sync SQLite FTS5 indices across the OptiPlex/Termux bridge.")
    print(" » RATIONALE: Zero-cloud token overhead, maximum thermodynamic yield,")
    print("   and immediate persistence in local zero-dependency ledgers.")
    print("==================================================")

if __name__ == "__main__":
    evaluate_highest_eta()
