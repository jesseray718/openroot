#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# openroot_rapl_sampler_v1.py — CANARY RLSP1
# Always-on RAPL counter sampler. Reads /sys/class/powercap/intel-rapl:0/energy_uj
# every INTERVAL seconds, banks {ts, energy_uj, delta_j, watts} to JSONL.
# Counter wraps at max_energy_range_uj — handled via modulo-wrap detection.
# MUST run as root (systemd unit openroot-rapl-sampler) — RAPL is root-readable.
import json, time, argparse
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/home/jesse/openroot")
OUT = BASE / "data" / "superlinear" / "rapl_samples.jsonl"
SYS_UJ = "/sys/class/powercap/intel-rapl:0/energy_uj"
SYS_MAX = "/sys/class/powercap/intel-rapl:0/max_energy_range_uj"
CANARY = "RLSP1"

def read_uj():
    with open(SYS_UJ) as f:
        return int(f.read().strip())

def read_max():
    try:
        with open(SYS_MAX) as f:
            return int(f.read().strip())
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser(prog=CANARY)
    ap.add_argument("--interval", type=float, default=5.0)
    args = ap.parse_args()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    mx = read_max()
    prev = read_uj()
    print(f"[{CANARY}] sampling every {args.interval}s | max_range_uj={mx}", flush=True)
    while True:
        time.sleep(args.interval)
        cur = read_uj()
        delta = cur - prev
        if delta < 0:  # counter wrap
            delta += (mx or 262143328850)
        with open(OUT, "a") as f:
            f.write(json.dumps({
                "ts": datetime.now(timezone.utc).isoformat(),
                "energy_uj": cur,
                "delta_j": round(delta / 1e6, 4),
                "watts": round(delta / 1e6 / args.interval, 3),
                "source": "rapl"
            }) + "\n")
        prev = cur

if __name__ == "__main__":
    main()
