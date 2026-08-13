#!/usr/bin/env python3
"""
OPENROOT RAISE_FLOOR PROTOCOL v4 — REAL MULTI-SOURCE TELEMETRY
Galaxy A15 / Termux native. Lowest node dictates pace.
η = useful_joules / human_joules
(Max Good / Min Effort)^6
"""
import os, sys, json, math, subprocess
from pathlib import Path
from datetime import datetime

PHI = (1 + math.sqrt(5)) / 2
REPO_ROOT = Path(__file__).resolve().parent.parent

def safe_float(path, default=None, col=0):
    try:
        with open(path) as f:
            parts = f.read().split()
            if parts:
                return float(parts[col])
    except Exception:
        pass
    return default

def safe_meminfo():
    mem = {}
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if ":" in line:
                    k, v = line.split(":", 1)
                    parts = v.strip().split()
                    if parts:
                        mem[k.strip()] = int(parts[0])
    except Exception:
        pass
    total = mem.get("MemTotal", 3645440)          # A15 \~3.5 GiB typical
    avail = mem.get("MemAvailable", mem.get("MemFree", total // 4))
    return total, avail

def read_battery_ua_uv():
    """µA / µV from power_supply ABI. Sign must be calibrated on this exact A15."""
    cur = safe_float("/sys/class/power_supply/battery/current_now")
    volt = safe_float("/sys/class/power_supply/battery/voltage_now")
    return cur, volt

def read_real_termux_stats():
    stats = {
        "efficiency": 0.3,
        "cpu_load": 0.0,
        "ram_mb": 0,
        "ram_total_mb": 0,
        "uptime_h": 0.0,
        "battery_ua": None,
        "battery_uv": None,
        "source": "fallback"
    }
    # CPU load (1-min)
    cpu = safe_float("/proc/loadavg", 0.0, 0)
    stats["cpu_load"] = cpu if cpu is not None else 0.0

    # RAM
    total_kb, avail_kb = safe_meminfo()
    used_kb = max(0, total_kb - avail_kb)
    stats["ram_total_mb"] = int(total_kb / 1024)
    stats["ram_mb"] = int(used_kb / 1024)

    # Uptime — direct, no helper indirection
    try:
        with open("/proc/uptime") as f:
            stats["uptime_h"] = float(f.read().split()[0]) / 3600.0
    except Exception:
        stats["uptime_h"] = 0.0

    # Battery (optional, non-fatal)
    cur, volt = read_battery_ua_uv()
    stats["battery_ua"] = cur
    stats["battery_uv"] = volt

    # Efficiency: 60 % inverse CPU + 40 % free-RAM ratio (clamped)
    cpu_eff = max(0.0, 1.0 - min(stats["cpu_load"], 2.0) / 2.0)
    ram_ratio = avail_kb / max(total_kb, 1)
    stats["efficiency"] = round(cpu_eff * 0.60 + ram_ratio * 0.40, 4)
    stats["source"] = "proc+sys"
    return stats

def load_node_stats(node_name):
    if node_name == "termux_android":
        return read_real_termux_stats()
    # Offline / higher nodes stay simulated until live SSH bridge reports
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
            "action": "Immediate offload: kill heavy python / llama processes, push work to Alpine via existing id_ed25519_rmh",
            "effort": "Low",
            "impact": "High",
            "reason": f"CPU load {load:.2f} exceeds sustainable phone floor"
        }
    if surplus > 0.25:
        return {
            "action": "Migrate background tasks + context absorption to higher node (Alpine or OptiPlex once online)",
            "effort": "Low",
            "impact": "High",
            "reason": "Spare capacity detected on higher nodes"
        }
    if surplus > 0.10:
        return {
            "action": "Optimize local caching + drop unused Ollama models; keep only nomic-embed + one generative if RAM allows",
            "effort": "Very Low",
            "impact": "Medium",
            "reason": "Minor inefficiency — free RAM ratio still recoverable"
        }
    return {
        "action": "Hardware floor raise: passive ΔT node + Black Locust RMH first measured joules",
        "effort": "Medium",
        "impact": "Critical",
        "reason": "Node at physical limit — software surplus exhausted"
    }

def main():
    print("=" * 62)
    print("OPENROOT: RAISE FLOOR PROTOCOL v4 — REAL MULTI-SOURCE")
    print("(Max Good / Min Effort)^6   η language only")
    print("=" * 62)

    nodes = ["termux_android", "raspberry_pi", "alpine_linux"]
    stats = {n: load_node_stats(n) for n in nodes}

    lowest = min(stats, key=lambda k: stats[k]["efficiency"])
    highest = max(stats, key=lambda k: stats[k]["efficiency"])
    real = stats["termux_android"]

    print()
    print("[SCAN] REAL DEVICE TELEMETRY (this node = termux_android)")
    print(f"  CPU Load 1m : {real.get('cpu_load', 0):.3f}")
    print(f"  RAM Used    : {real.get('ram_mb', 0)} MB / {real.get('ram_total_mb', 0)} MB")
    print(f"  Uptime      : {real.get('uptime_h', 0):.2f} h")
    print(f"  Efficiency  : {real.get('efficiency', 0):.4f}  (source={real.get('source')})")
    if real.get("battery_ua") is not None:
        print(f"  Battery     : {real['battery_ua']} µA  {real.get('battery_uv')} µV")

    print()
    print(f"[SCAN] Lowest  : {lowest:16s}  Eff={stats[lowest]['efficiency']:.4f}")
    print(f"[SCAN] Highest : {highest:16s}  Eff={stats[highest]['efficiency']:.4f}")

    surplus = calculate_surplus(stats[highest], stats[lowest])
    proposal = propose_opt(lowest, surplus, stats[lowest])

    print()
    print(f"[SURPLUS] {surplus:.4f} Φ-units available")
    print(f"[ACTION]  {proposal['action']}")
    print(f"  Effort={proposal['effort']}  Impact={proposal['impact']}")
    print(f"  Reason: {proposal.get('reason', 'N/A')}")

    # Append-only ledger
    ledger = REPO_ROOT / "04_DATA" / "floor_raise_log.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    cycle = 1
    if ledger.exists():
        with open(ledger) as f:
            cycle = sum(1 for _ in f) + 1
    entry = {
        "ts": datetime.now().isoformat(),
        "cycle": cycle,
        "lowest": lowest,
        "highest": highest,
        "surplus": round(surplus, 6),
        "real_telemetry": {k: v for k, v in real.items() if v is not None},
        "proposal": proposal,
        "version": "v4"
    }
    with open(ledger, "a") as f:
        f.write(json.dumps(entry, default=str) + "\n")

    print()
    print(f"[LOGGED] Cycle {cycle} → {ledger}")
    print("=" * 62)
    print("NEXT PHYSICAL (ordered by η):")
    print("  1. Implement the ACTION above (software offload or cache clean)")
    print("  2. Instrument first passive ΔT (chicken-wire + thermometer + mass)")
    print("  3. Measure real joules → write thermo_ledger → mint first ACRE")
    print("  4. git add . && git commit -m \"raise-floor cycle N\" && git push")
    print("=" * 62)

if __name__ == "__main__":
    main()
