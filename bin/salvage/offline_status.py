#!/usr/bin/env python3
"""
OpenRoot Offline Workflow Status — OptiPlex heavy spoke
η = useful_joules / human_joules
No network required. Stdlib only.
"""

import os, sys, json, time, subprocess, socket, shutil
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
LOG_DIR = HOME / "openroot" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
LOG_FILE = LOG_DIR / f"offline_status_{STAMP}.json"

def run(cmd, timeout=8):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def section(title):
    print(f"\n{'='*64}\n  {title}\n{'='*64}")

def kv(k, v, ok=None):
    mark = "✅" if ok is True else ("❌" if ok is False else "•")
    print(f"  {mark} {k:<28} {v}")

# ─── collect ───────────────────────────────────────────────────
data = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "host": socket.gethostname(),
    "η_notes": [],
    "next_actions": [],
}

section("HOST + RESOURCES")
code, out, _ = run("uptime")
data["uptime"] = out
kv("uptime", out)

code, out, _ = run("free -h | awk '/Mem:/{print $2,$3,$7}'")
parts = out.split()
if len(parts) >= 3:
    data["ram"] = {"total": parts[0], "used": parts[1], "available": parts[2]}
    kv("RAM total/used/avail", f"{parts[0]} / {parts[1]} / {parts[2]}")
    try:
        avail_gi = float(parts[2].replace("Gi","").replace("G",""))
        if avail_gi < 4:
            data["η_notes"].append("RAM pressure — avoid loading larger models")
            data["next_actions"].append("Free RAM or stay on 7B class")
    except: pass

code, out, _ = run("df -h / | awk 'NR==2{print $2,$3,$4,$5}'")
parts = out.split()
if len(parts) >= 4:
    data["disk"] = {"size": parts[0], "used": parts[1], "avail": parts[2], "pct": parts[3]}
    kv("disk / size/used/avail/%", f"{parts[0]} / {parts[1]} / {parts[2]} / {parts[3]}")

section("LLAMA-SERVER")
code, out, _ = run("ss -tlnp | grep ':8080'")
data["llama_port_8080"] = bool(out)
kv("port 8080 listening", "yes" if out else "no", ok=bool(out))

code, out, _ = run("pgrep -a llama-server || true")
data["llama_process"] = out
kv("process", out[:90] if out else "not running", ok=bool(out))

code, out, _ = run("curl -s --max-time 2 http://127.0.0.1:8080/health || true")
data["llama_health"] = out
kv("health endpoint", out if out else "no response", ok=("ok" in out.lower() if out else False))

code, out, _ = run("curl -s --max-time 2 http://127.0.0.1:8080/v1/models 2>/dev/null | head -c 200 || true")
data["llama_models"] = out
if out:
    kv("models snippet", out[:80] + "...")

section("SYNCTHING")
code, out, _ = run("systemctl --user is-active syncthing 2>/dev/null || echo inactive")
data["syncthing_active"] = out.strip()
kv("systemd active", out.strip(), ok=(out.strip()=="active"))

code, out, _ = run("syncthing cli show system 2>/dev/null | grep -o '\"myID\": \"[^\"]*\"' || true")
data["syncthing_myID"] = out
kv("myID", out.replace('"myID": ', '') if out else "unavailable")

code, out, _ = run("syncthing cli config devices list 2>/dev/null || true")
data["syncthing_devices"] = out.splitlines() if out else []
kv("known devices", str(len(data["syncthing_devices"])))
for d in data["syncthing_devices"]:
    print(f"      {d}")

code, out, _ = run("syncthing cli config folders list 2>/dev/null || true")
data["syncthing_folders"] = out.splitlines() if out else []
kv("folders", ", ".join(data["syncthing_folders"]) if data["syncthing_folders"] else "none")

section("OPENROOT TREE")
for name in ["openroot", "une", "black-locust-rmh"]:
    p = HOME / name
    exists = p.exists()
    data[f"dir_{name}"] = str(p) if exists else None
    if exists:
        code, size, _ = run(f"du -sh {p} 2>/dev/null | cut -f1")
        kv(name, f"{p}  ({size})", ok=True)
    else:
        kv(name, "missing", ok=False)
        data["next_actions"].append(f"Restore or re-clone {name}")

section("NETWORK (local only)")
code, out, _ = run("ip -4 addr show wlx1869454c6de2 2>/dev/null | awk '/inet /{print $2}' || true")
data["wifi_ip"] = out
kv("wlx... IP", out if out else "down or missing", ok=bool(out))

code, out, _ = run("ip -4 addr show | awk '/inet / && $2 !\~ /^127/ {print $2}' | head -5")
data["all_ips"] = out.splitlines() if out else []
for ip in data["all_ips"]:
    print(f"      {ip}")

section("η SUMMARY + NEXT ACTIONS")
print(f"  Timestamp     : {data['timestamp']}")
print(f"  Host          : {data['host']}")
if data["η_notes"]:
    print("  η notes:")
    for n in data["η_notes"]:
        print(f"    - {n}")
if data["next_actions"]:
    print("  Next actions:")
    for a in data["next_actions"]:
        print(f"    → {a}")
else:
    print("  Next actions  : none critical — stack is coherent offline")

# persist
with open(LOG_FILE, "w") as f:
    json.dump(data, f, indent=2)
print(f"\n📋 Log written: {LOG_FILE}")
print("="*64)
