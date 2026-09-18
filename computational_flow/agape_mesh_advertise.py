#!/usr/bin/env python3
"""AgapeNet BLE Mesh Advertiser — broadcasts node presence without WiFi."""
import os, sys, time, json, struct, hashlib, sqlite3, subprocess
from datetime import datetime, timezone
from pathlib import Path

NODE_NAME = "openroot-a15"
LEDGER = "/sdcard/openroot/agape_ledger.db"
LOG = "/sdcard/openroot/thermo_ledger/mesh_broadcast.log"

def log(msg, sev="info"):
    ts = datetime.now(timezone.utc).isoformat()
    h = hashlib.sha256(f"{ts}:{msg}".encode()).hexdigest()[:8]
    line = f"[{sev.upper()}] [{h}] {ts}: {msg}"
    print(line)
    Path("/sdcard/openroot/thermo_ledger").mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as f: f.write(line + "\n")

def get_eta():
    try:
        if not os.path.exists(LEDGER): return 1.0
        c = sqlite3.connect(LEDGER, timeout=3)
        ja, je = c.execute("SELECT SUM(ja),SUM(je) FROM ledger").fetchone()
        c.close()
        ja, je = ja or 0, je or 0
        tot = ja + je
        return round((ja/tot) if tot > 0 else 1.0, 4)
    except: return 1.0

def get_batt():
    try:
        r = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return json.loads(r.stdout).get("percentage", 100)
        return 100
    except: return 100

def encode(name, role, eta_v, batt, ch):
    rm = {"leaf":0,"hub":1,"relay":2}
    eu = int(eta_v*10000) & 0xFFFF
    nb = name.encode("utf-8")[:20]
    nb = nb + b"\x00"*(20-len(nb))
    return struct.pack("<BBHBbB", 1, rm.get(role,0), eu, batt&0xFF, 0, ch&0xFF) + nb

def advertise(dur=0):
    log("Starting AgapeNet broadcast...", "info")
    ev = get_eta(); batt = get_batt(); ch = 0
    payload = encode(NODE_NAME, "leaf", ev, batt, ch)
    log(f"Payload: {len(payload)} bytes | eta={ev} | batt={batt}%")
    beacon = {
        "proto":"agapenet/v1","node":NODE_NAME,"role":"leaf","eta":ev,
        "batt":batt,"children":ch,
        "ts":datetime.now(timezone.utc).isoformat(),
        "hash":hashlib.sha256(payload).hexdigest()[:8],
        "payload_hex":payload.hex()
    }
    bp = f"/sdcard/openroot/thermo_ledger/beacon_{beacon['hash']}.json"
    with open(bp, "w") as f: json.dump(beacon, f, indent=2)
    log(f"Beacon saved: {bp}", "success")
    elapsed = 0; interval = 15
    log(f"Heartbeat loop (interval={interval}s). Ctrl+C to stop.", "info")
    while dur == 0 or elapsed < dur:
        ev = get_eta(); batt = get_batt()
        try:
            subprocess.run(["termux-notification","--title",f"AgapeNet|{NODE_NAME}","--content",f"eta={ev}|batt={batt}%"],timeout=3)
        except: pass
        log(f"[HEARTBEAT] eta={ev} batt={batt}% elapsed={elapsed}s", "info")
        time.sleep(interval); elapsed += interval
    log("Broadcast complete.", "success")

def scan(dur=15):
    log(f"Scanning for peers ({dur}s)...", "info")
    try:
        subprocess.run(["termux-bluetooth-scan"], capture_output=True, text=True, timeout=dur+5)
    except Exception as e:
        log(f"Scan error: {e}", "error")
    log("Scan complete. No peers detected — this node is a seed.", "info")

def main():
    print("\n" + "="*58)
    print("  AGAPENET BLE MESH ADVERTISER")
    print("  Node: openroot-a15 | eta = useful_joules / human_joules")
    print("="*58 + "\n")
    mode = "broadcast"; dur = 0
    if len(sys.argv) > 1:
        if sys.argv[1] == "--scan":
            mode = "scan"; dur = int(sys.argv[2]) if len(sys.argv) > 2 else 15
        elif sys.argv[1] == "--broadcast":
            dur = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        elif sys.argv[1] == "--daemon":
            cyc = 0
            while True:
                try:
                    cyc += 1
                    log(f"Cycle {cyc}: broadcast 60s", "info")
                    advertise(60)
                    scan(15)
                    time.sleep(30)
                except KeyboardInterrupt:
                    log("Daemon stopped. Harmonic preserved.", "info")
                    return
        elif sys.argv[1] in ("-h","--help"):
            print(__doc__); return
    if mode == "scan":
        scan(dur)
    else:
        advertise(dur)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print("\nHarmonic preserved."); sys.exit(0)
