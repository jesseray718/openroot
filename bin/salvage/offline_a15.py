#!/usr/bin/env python3
"""
OpenRoot Offline A15 Workflow — GOVERNOR-01 only
No network. No OptiPlex. No assumptions.
η = useful_joules / human_joules
Stdlib only. Absolute paths.
"""

import os, sys, json, time, subprocess, socket, hashlib
from datetime import datetime, timezone
from pathlib import Path

HOME = Path("/data/data/com.termux/files/home")
SDCARD = Path("/sdcard/openroot")
LOG_DIR = HOME / "openroot" / "logs"
SEED_DIR = SDCARD / "session_seeds"
LOG_DIR.mkdir(parents=True, exist_ok=True)
SEED_DIR.mkdir(parents=True, exist_ok=True)

STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
LOG_FILE = LOG_DIR / f"offline_a15_{STAMP}.json"
SEED_FILE = SEED_DIR / "current_seed.json"

def run(cmd, timeout=6):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or "").strip(), (r.stderr or "").strip()
    except Exception as e:
        return 1, "", str(e)

def section(t):
    print(f"\n{'='*62}\n  {t}\n{'='*62}")

def kv(k, v, ok=None):
    mark = "✅" if ok is True else ("❌" if ok is False else "•")
    print(f"  {mark} {k:<26} {v}")

data = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "host": "a15-governor",
    "mode": "offline-house-absent",
    "η_notes": [],
    "next": [],
    "dirs": {},
    "joules": {},
}

section("IDENTITY + MODE")
kv("mode", "OFFLINE — house left, OptiPlex unreachable")
kv("host", data["host"])
kv("stamp", STAMP)

section("CORE DIRECTORIES")
for name, path in [
    ("openroot", HOME / "openroot"),
    ("une", HOME / "une"),
    ("computational_flow", HOME / "une" / "computational_flow"),
    ("agape_kb", SDCARD / "agape_kb"),
    ("session_seeds", SEED_DIR),
]:
    exists = path.exists()
    data["dirs"][name] = str(path) if exists else None
    if exists:
        code, size, _ = run(f"du -sh '{path}' 2>/dev/null | cut -f1")
        kv(name, f"{path} ({size})", ok=True)
    else:
        kv(name, "MISSING", ok=False)
        data["next"].append(f"Create or restore {name}")

section("BATTERY + THERMAL (local sensors)")
# Prefer rish when available, degrade cleanly
code, out, _ = run("rish -c 'cat /sys/class/power_supply/battery/voltage_now 2>/dev/null' || cat /sys/class/power_supply/battery/voltage_now 2>/dev/null || true")
v = out.strip()
code, out, _ = run("rish -c 'cat /sys/class/power_supply/battery/current_now 2>/dev/null' || cat /sys/class/power_supply/battery/current_now 2>/dev/null || true")
c = out.strip()
code, out, _ = run("rish -c 'cat /sys/class/power_supply/battery/capacity 2>/dev/null' || cat /sys/class/power_supply/battery/capacity 2>/dev/null || true")
cap = out.strip()

data["joules"]["voltage_uV"] = v
data["joules"]["current_uA"] = c
data["joules"]["capacity_pct"] = cap

kv("capacity %", cap or "unreadable")
kv("voltage_now", v or "unreadable")
kv("current_now", c or "unreadable")

if v and c:
    try:
        watts = (int(v) / 1e6) * (int(c) / 1e6)
        data["joules"]["instant_W"] = round(watts, 3)
        kv("instant power (W)", f"{watts:.3f}")
        if abs(watts) > 4.5:
            data["η_notes"].append("High discharge — reduce background load")
    except: pass

section("LOCAL AI / PROCESS STATE")
code, out, _ = run("pgrep -a -f 'llama|ollama|kai|python.*computational' || true")
if out:
    for line in out.splitlines()[:6]:
        print(f"  • {line[:90]}")
    data["local_ai_procs"] = out.splitlines()
else:
    kv("local AI processes", "none running")
    data["next"].append("Optional: start small local model if RAM allows")

section("SYNCTHING (local only)")
code, out, _ = run("pgrep -a syncthing || true")
if out:
    kv("syncthing process", "running", ok=True)
    data["syncthing"] = "running"
else:
    kv("syncthing process", "stopped (expected offline)", ok=True)
    data["syncthing"] = "stopped"

section("SEED + BRIDGE (offline write)")
seed = {
    "timestamp": data["timestamp"],
    "mode": "offline-house-absent",
    "host": "a15",
    "capacity_pct": cap,
    "dirs_present": [k for k,v in data["dirs"].items() if v],
    "η_notes": data["η_notes"],
    "next": data["next"],
}
# simple content hash for integrity
blob = json.dumps(seed, sort_keys=True).encode()
seed["sha256"] = hashlib.sha256(blob).hexdigest()[:16]

with open(SEED_FILE, "w") as f:
    json.dump(seed, f, indent=2)
kv("seed written", str(SEED_FILE), ok=True)

section("η SUMMARY — OFFLINE MODE")
print(f"  Timestamp     : {data['timestamp']}")
print(f"  Mode          : house absent — pure A15")
if data["η_notes"]:
    print("  η notes:")
    for n in data["η_notes"]:
        print(f"    - {n}")
print("  Next (local only):")
if data["next"]:
    for a in data["next"]:
        print(f"    → {a}")
else:
    print("    → Maintain seed cadence + observe battery")
    print("    → When home: re-join OptiPlex via SSH 192.168.1.193")

with open(LOG_FILE, "w") as f:
    json.dump(data, f, indent=2)
print(f"\n📋 Log : {LOG_FILE}")
print(f"🌱 Seed: {SEED_FILE}")
print("="*62)
print("Offline workflow ready. You can leave the house.")
print("Re-run this script any time for a new seed + status.")
