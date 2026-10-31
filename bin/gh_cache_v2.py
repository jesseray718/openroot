# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""Cached-pathway wrapper for arbitrary commands with RAPL measurement.
Usage: gh_cache_v2.py [--ttl=3600] -- <command...>
Hit: replay stdout, record skip-joules (0.000J honest floor).
Miss: execute, measure RAPL (or TDP estimate), store output, stamp receipt."""
import hashlib, json, subprocess, sys, time, datetime, os
from pathlib import Path

REPO = "/home/jesse/openroot"
CACHE = Path(REPO + "/data/cmd_cache.jsonl")
RECEIPTS = Path(REPO + "/ledger/unified/run_receipts.jsonl")
RAPL_PATH = "/sys/class/powercap/intel-rapl/intel-rapl:0/energy_uj"
TDP_WATTS = 65.0  # OptiPlex 3060 TDP — falsifiable, never claimed measured

def sha(s): return hashlib.sha256(s.encode()).hexdigest()
def ts(): return datetime.datetime.now(datetime.timezone.utc).isoformat()

def rapl_read():
    try:
        with open(RAPL_PATH) as f:
            return int(f.read().strip())
    except Exception:
        return None

def load_cache():
    if not CACHE.exists(): return {}
    return {json.loads(line)["key"]: json.loads(line) for line in CACHE.read_text().splitlines() if line.strip()}

def save_entry(entry):
    cache = load_cache(); cache[entry["key"]] = entry
    CACHE.write_text("\n".join(json.dumps(v, separators=(",", ":")) for v in cache.values()) + "\n")

def write_receipt(rec):
    RECEIPTS.parent.mkdir(parents=True, exist_ok=True)
    with open(RECEIPTS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, separators=(",", ":")) + "\n")

def measure_joules(start_uj, t_start):
    end_uj = rapl_read()
    wall = time.time() - t_start
    if start_uj is not None and end_uj is not None and end_uj >= start_uj:
        return {"source": "rapl", "joules": (end_uj - start_uj) / 1e6, "wall_s": round(wall, 4)}
    return {"source": "estimate", "joules": TDP_WATTS * wall, "wall_s": round(wall, 4),
            "note": "RAPL unavailable — TDP x wall estimate"}

def main():
    args = sys.argv[1:]
    ttl = 3600
    while args and args[0].startswith("--ttl="):
        ttl = int(args[0].split("=")[1]); args = args[1:]
    if not args or args[0] != "--":
        print("usage: gh_cache_v2.py [--ttl=3600] -- <command...>", file=sys.stderr); sys.exit(2)
    cmd = args[1:]
    key = sha(" ".join(cmd) + "|" + os.getcwd())
    cache = load_cache()
    entry = cache.get(key)
    now = time.time()

    if entry and (ttl == 0 or now - entry["ts"] < ttl):
        print(entry["out"], end="")
        rec = {"ts": ts(), "input_fingerprint": key, "cache_hit": True, "entries": 0,
               "joules": 0.0, "source": "skipped", "wall_s": 0.0, "cmd": cmd[0]}
        write_receipt(rec)
        print(f"\n[cache] HIT {key[:12]} — replayed, {(now - entry['ts']):.0f}s old, 0.000J")
        return

    t0 = time.time()
    start_uj = rapl_read()
    r = subprocess.run(cmd, capture_output=True, text=True)
    energy = measure_joules(start_uj, t0)
    out = r.stdout
    if r.returncode != 0:
        print(out, end=""); print(r.stderr, end="", file=sys.stderr); sys.exit(r.returncode)
    print(out, end="")
    save_entry({"key": key, "out": out, "sha": sha(out), "ts": now, "cmd": " ".join(cmd)[:200]})
    rec = {"ts": ts(), "input_fingerprint": key, "cache_hit": False, "entries": 0,
           "joules": round(energy["joules"], 6), "source": energy["source"],
           "wall_s": energy["wall_s"], "cmd": cmd[0]}
    write_receipt(rec)
    src = energy.get("source", "unknown")
    jval = f"{energy['joules']:.3f}J"
    print(f"\n[cache] MISS {key[:12]} — executed fresh in {energy['wall_s']:.2f}s, {jval} ({src})")

if __name__ == "__main__":
    main()
    print("[exit=0]")
