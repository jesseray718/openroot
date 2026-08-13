#!/usr/bin/env python3
"""
OPENROOT RAISE_FLOOR PROTOCOL v4.2
A15 reality: /proc/uptime is Permission denied under Termux UID.
Uptime from /proc/stat btime. η language only.
(Max Good / Min Effort)^6
"""
import os, sys, json, math
from pathlib import Path
from datetime import datetime

PHI = (1 + math.sqrt(5)) / 2
REPO_ROOT = Path(__file__).resolve().parent.parent

def read_real_termux_stats():
    stats = {
        "efficiency": 0.3,
        "cpu_load": 0.0,
        "ram_mb": 0,
        "ram_total_mb": 0,
        "uptime_h": 0.0,
        "battery_ua": None,
        "battery_uv": None,
        "source": "proc+sys"
    }

    # CPU load
    try:
        with open("/proc/loadavg") as f:
            stats["cpu_load"] = float(f.read().split()[0])
    except Exception:
        pass

    # RAM
    total_kb = 3645440
    avail_kb = 800000
    try:
        mem = {}
        with open("/proc/meminfo") as f:
            for line in f:
                if ":" in line:
                    k, v = line.split(":", 1)
                    parts = v.strip().split()
                    if parts:
                        mem[k.strip()] = int(parts[0])
        total_kb = mem.get("MemTotal", total_kb)
        avail_kb = mem.get("MemAvailable", mem.get("MemFree", avail_kb))
    except Exception:
        pass
    used_kb = max(0, total_kb - avail_kb)
    stats["ram_total_mb"] = int(total_kb / 1024)
    stats["ram_mb"] = int(used_kb / 1024)

    # UPTIME — never touch /proc/uptime (Permission denied on this device)
    # Primary: /proc/stat btime
    up = None
    try:
        with open("/proc/stat") as f:
            for line in f:
                if line.startswith("btime"):
                    btime = int(line.split()[1])
                    up = max(0.0, datetime.now().timestamp() - btime)
                    break
    except Exception:
        pass
    if up is None:
        up = 0.0
    stats["uptime_h"] = round(up / 3600.0, 2)

    # Battery (optional, non-fatal)
    for key, path in [
        ("battery_ua", "/sys/class/power_supply/battery/current_now"),
        ("battery_uv", "/sys/class/power_supply/battery/voltage_now")
    ]:
        try:
            with open(path) as f:
                stats[key] = int(f.read().strip())
        except Exception:
            pass

    # Efficiency
    cpu_eff = max(0.0, 1.0 - min(stats["cpu_load"], 2.0) / 2.0)
    ram_ratio = avail_kb / max(total_kb, 1)
    stats["efficiency"] = round(cpu_eff * 0.60 + ram_ratio * 0.40, 4)
    return stats

def load_node_stats(node_name):
    if node_name == "termux_android":
        return read_real_termux_stats()
    simulated = {
        "raspberry_pi": {"cpu_load": 0.25, "ram_mb": 650, "efficiency": 0.78, "source": "sim"},
        "alpine_linux": {"cpu_load": 0.08, "ram_mb": 180, "efficiency": 0.94, "source": "sim"}
    }
    return simulated.get(node_name, {"efficiency": 0.0, "source": "none"})

def calculate_surplus(high, low):
    return (high.get("efficiency", 0) - low.get("efficiency", 0)) * PHI

def propose_opt(low_name, surplus, low_stats):
    load = low_stats.get("cpu_load", 0)
    if load > 1.2:
        return {
            "action": "Immediate offload heavy processes to Alpine/OptiPlex",
            "effort": "Low", "impact": "High",
            "reason": f"CPU load {load:.2f} exceeds phone floor"
        }
    if surplus > 0.25:
        return {
            "action": "Migrate background tasks + context absorption to higher node",
            "effort": "Low", "impact": "High",
            "reason": "Spare capacity detected on higher nodes"
        }
    if surplus > 0.10:
        return {
            "action": "Optimize local caching + drop unused models",
            "effort": "Very Low", "impact": "Medium",
            "reason": "Minor inefficiency"
        }
    return {
        "action": "Hardware floor raise: first passive ΔT + measured joules",
        "effort": "Medium", "impact": "Critical",
        "reason": "Software surplus exhausted"
    }

def main():
    print("=" * 62)
    print("OPENROOT: RAISE FLOOR PROTOCOL v4.2")
    print("A15: /proc/uptime blocked → using /proc/stat btime")
    print("(Max Good / Min Effort)^6")
    print("=" * 62)

    nodes = ["termux_android", "raspberry_pi", "alpine_linux"]
    stats = {n: load_node_stats(n) for n in nodes}
    lowest = min(stats, key=lambda k: stats[k]["efficiency"])
    highest = max(stats, key=lambda k: stats[k]["efficiency"])
    real = stats["termux_android"]

    print()
    print("[SCAN] REAL DEVICE TELEMETRY (termux_android)")
    print(f"  CPU Load 1m : {real.get('cpu_load', 0):.3f}")
    print(f"  RAM Used    : {real.get('ram_mb', 0)} MB / {real.get('ram_total_mb', 0)} MB")
    print(f"  Uptime      : {real.get('uptime_h', 0):.2f} h")
    print(f"  Efficiency  : {real.get('efficiency', 0):.4f}")
    if real.get("battery_ua") is not None:
        print(f"  Battery     : {real['battery_ua']} µA  {real.get('battery_uv')} µV")

    print()
    print(f"[SCAN] Lowest  : {lowest:16s}  Eff={stats[lowest]['efficiency']:.4f}")
    print(f"[SCAN] Highest : {highest:16s}  Eff={stats[highest]['efficiency']:.4f}")

    surplus = calculate_surplus(stats[highest], stats[lowest])
    proposal = propose_opt(lowest, surplus, stats[lowest])

    print()
    print(f"[SURPLUS] {surplus:.4f} Φ-units")
    print(f"[ACTION]  {proposal['action']}")
    print(f"  Effort={proposal['effort']}  Impact={proposal['impact']}")
    print(f"  Reason: {proposal.get('reason')}")

    ledger = REPO_ROOT / "04_DATA" / "floor_raise_log.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    cycle = sum(1 for _ in open(ledger)) + 1 if ledger.exists() else 1
    entry = {
        "ts": datetime.now().isoformat(),
        "cycle": cycle,
        "lowest": lowest,
        "highest": highest,
        "surplus": round(surplus, 6),
        "real_telemetry": {k: v for k, v in real.items() if v is not None},
        "proposal": proposal,
        "version": "v4.2"
    }
    with open(ledger, "a") as f:
        f.write(json.dumps(entry, default=str) + "\n")

    print()
    print(f"[LOGGED] Cycle {cycle} → {ledger}")
    print("=" * 62)
    print("NEXT: Act on the ACTION or instrument first passive ΔT.")
    print("=" * 62)

if __name__ == "__main__":
    main()
