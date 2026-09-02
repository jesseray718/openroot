#!/usr/bin/env python3
"""
data_logger_v0.3 — Termux/A15 ready for H-003 Node Zero validation
Simulated sensors (easy to swap for real DS18B20 + DHT22)
Logs to /storage/emulated/0/Documents/openroot-data/
Produces .jsonl + summary.csv usable as ACRE evidence
"""

import datetime
import json
import os
import csv
import time
import random

LOG_DIR = "/storage/emulated/0/Documents/openroot-data"
os.makedirs(LOG_DIR, exist_ok=True)

DATE = datetime.date.today().isoformat()
JSONL = f"{LOG_DIR}/{DATE}_H003_NodeZero.jsonl"
CSV   = f"{LOG_DIR}/{DATE}_H003_NodeZero_summary.csv"

def read_t_in():
    """Replace with real DS18B20 (1-wire) read when hardware ready"""
    return round(48.5 + random.uniform(-1.5, 1.5), 2)   # solar chimney outlet \~47-50°C

def read_t_out():
    """Replace with real DS18B20 read"""
    return round(12.3 + random.uniform(-0.8, 0.8), 2)   # labyrinth outlet \~11.5-13°C

def read_hum():
    """Replace with real DHT22 read"""
    return round(68.0 + random.uniform(-3, 3), 1)       # typical humid-climate

def log_reading(t_in, t_out, hum):
    ts = datetime.datetime.now().isoformat()
    delta_t = round(t_in - t_out, 2)
    record = {"ts": ts, "t_in": t_in, "t_out": t_out, "delta_t": delta_t, "hum": hum}
    
    with open(JSONL, "a") as f:
        f.write(json.dumps(record) + "\n")
    
    return record

def run_test_burst(minutes=2, interval=6):
    print(f"=== H-003 TEST BURST START ({minutes} min, {interval}s interval) ===")
    print(f"Logging to: {JSONL}")
    print(f"Summary CSV:  {CSV}")
    
    readings = []
    for i in range(int(minutes * 60 / interval)):
        t_in  = read_t_in()
        t_out = read_t_out()
        hum   = read_hum()
        rec = log_reading(t_in, t_out, hum)
        readings.append(rec)
        print(f"[{i+1:02d}] ΔT={rec['delta_t']:5.2f}°C  t_in={t_in:5.1f}  t_out={t_out:5.1f}  hum={hum:4.1f}%")
        time.sleep(interval)
    
    # write summary CSV
    with open(CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ts", "t_in", "t_out", "delta_t", "hum"])
        writer.writeheader()
        writer.writerows(readings)
    
    avg_delta = sum(r["delta_t"] for r in readings) / len(readings)
    print(f"\n=== BURST COMPLETE ===")
    print(f"Readings: {len(readings)}")
    print(f"Avg ΔT: {avg_delta:.2f}°C")
    print(f"Files ready for ACRE evidence: {JSONL}  +  {CSV}")

if __name__ == "__main__":
    run_test_burst(minutes=2, interval=6)
