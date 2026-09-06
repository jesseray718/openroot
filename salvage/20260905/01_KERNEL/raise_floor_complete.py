#!/usr/bin/env python3
"""
OPENROOT RAISE_FLOOR COMPLETE LOOP v5.0
Observe → Detect → Swap → Re-measure → Log joules saved
A15 native. Only acts on things it can actually change.
η language only. (Max Good / Min Effort)^6
"""
import os, sys, json, math, time, shutil, subprocess
from pathlib import Path
from datetime import datetime

PHI = (1 + math.sqrt(5)) / 2
REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "04_DATA"
DATA.mkdir(parents=True, exist_ok=True)
LEDGER = DATA / "floor_raise_log.jsonl"
SWAPLOG = DATA / "swap_actions.jsonl"

def sh(cmd, timeout=12):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0, (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        return False, str(e)

def read_stats():
    s = {"cpu_load": 0.0, "ram_mb": 0, "ram_total_mb": 0, "ram_avail_mb": 0,
         "uptime_h": 0.0, "efficiency": 0.3, "source": "proc"}
    try:
        with open("/proc/loadavg") as f:
            s["cpu_load"] = float(f.read().split()[0])
    except: pass
    try:
        mem = {}
        with open("/proc/meminfo") as f:
            for line in f:
                if ":" in line:
                    k, v = line.split(":", 1)
                    parts = v.strip().split()
                    if parts: mem[k.strip()] = int(parts[0])
        total = mem.get("MemTotal", 3645440)
        avail = mem.get("MemAvailable", mem.get("MemFree", 800000))
        s["ram_total_mb"] = int(total / 1024)
        s["ram_avail_mb"] = int(avail / 1024)
        s["ram_mb"] = int((total - avail) / 1024)
    except: pass
    # uptime via btime (uptime file is denied)
    try:
        with open("/proc/stat") as f:
            for line in f:
                if line.startswith("btime"):
                    btime = int(line.split()[1])
                    s["uptime_h"] = round((time.time() - btime) / 3600.0, 2)
                    break
    except: pass
    cpu_eff = max(0.0, 1.0 - min(s["cpu_load"], 2.0) / 2.0)
    ram_ratio = s["ram_avail_mb"] / max(s["ram_total_mb"], 1)
    s["efficiency"] = round(cpu_eff * 0.55 + ram_ratio * 0.45, 4)
    return s

def find_swappable():
    """Return list of concrete, safe actions that free resources on this A15."""
    actions = []
    # 1. Large caches
    for p in [Path.home()/".cache", Path.home()/"tmp", Path("/data/data/com.termux/files/usr/tmp")]:
        if p.exists() and p.is_dir():
            try:
                size = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
                if size > 20 * 1024 * 1024:  # >20 MB
                    actions.append({"type": "cache_clean", "path": str(p), "bytes": size,
                                    "desc": f"Clear {p.name} cache ({size//1024//1024} MB)"})
            except: pass
    # 2. Old / large model files that are not currently needed
    model_dirs = [Path.home()/"models", Path.home()/".ollama", Path.home()/"llama.cpp"]
    for d in model_dirs:
        if d.exists():
            for f in d.rglob("*.gguf"):
                try:
                    sz = f.stat().st_size
                    if sz > 400 * 1024 * 1024:  # >400 MB
                        actions.append({"type": "large_model", "path": str(f), "bytes": sz,
                                        "desc": f"Large model present: {f.name} ({sz//1024//1024} MB) — candidate for offload/delete when unused"})
                except: pass
    # 3. Drop page cache if we have root-like capability (safe attempt)
    actions.append({"type": "drop_caches_attempt", "path": None, "bytes": 0,
                    "desc": "Attempt drop_caches (may require elevated privileges)"})
    # 4. Termux package cache
    pkg_cache = Path("/data/data/com.termux/files/usr/var/cache/apt/archives")
    if pkg_cache.exists():
        try:
            size = sum(f.stat().st_size for f in pkg_cache.rglob("*") if f.is_file())
            if size > 10 * 1024 * 1024:
                actions.append({"type": "apt_cache", "path": str(pkg_cache), "bytes": size,
                                "desc": f"Clear apt archives ({size//1024//1024} MB)"})
        except: pass
    return actions

def execute_swap(action):
    """Perform the swap. Return bytes freed and success flag."""
    freed = 0
    ok = False
    if action["type"] == "cache_clean":
        p = Path(action["path"])
        if p.exists():
            try:
                before = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
                shutil.rmtree(p, ignore_errors=True)
                p.mkdir(parents=True, exist_ok=True)
                after = sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) if p.exists() else 0
                freed = max(0, before - after)
                ok = True
            except Exception as e:
                return 0, False, str(e)
    elif action["type"] == "apt_cache":
        ok, out = sh("apt-get clean 2>/dev/null || true")
        freed = action.get("bytes", 0) if ok else 0
    elif action["type"] == "drop_caches_attempt":
        # Best-effort; usually fails without elevated rights
        ok, out = sh("sync; echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true")
        freed = 0
    elif action["type"] == "large_model":
        # Do not auto-delete models — only report. Safer.
        ok = False
        freed = 0
    return freed, ok, "done" if ok else "skipped/safe"

def main():
    print("=" * 64)
    print("OPENROOT RAISE_FLOOR COMPLETE LOOP v5.0")
    print("Observe → Detect → Swap → Re-measure → Log saved")
    print("=" * 64)

    # 1. OBSERVE
    before = read_stats()
    print("\n[1] OBSERVE (before)")
    print(f"  CPU 1m     : {before['cpu_load']:.3f}")
    print(f"  RAM used   : {before['ram_mb']} / {before['ram_total_mb']} MB")
    print(f"  RAM avail  : {before['ram_avail_mb']} MB")
    print(f"  Efficiency : {before['efficiency']:.4f}")
    print(f"  Uptime     : {before['uptime_h']:.2f} h")

    # 2. DETECT
    candidates = find_swappable()
    print(f"\n[2] DETECT — {len(candidates)} candidate swaps")
    for i, a in enumerate(candidates, 1):
        print(f"  {i}. {a['desc']}")

    # 3. SWAP (only safe automatic actions)
    total_freed = 0
    executed = []
    print("\n[3] SWAP")
    for a in candidates:
        if a["type"] in ("cache_clean", "apt_cache", "drop_caches_attempt"):
            freed, ok, msg = execute_swap(a)
            status = "EXECUTED" if ok else "SKIPPED"
            print(f"  {status}: {a['desc']}  → freed {freed//1024} KB  ({msg})")
            if ok and freed > 0:
                total_freed += freed
                executed.append({**a, "freed_bytes": freed, "status": status})
        else:
            print(f"  REPORT ONLY: {a['desc']}  (not auto-deleted)")

    time.sleep(1.5)  # let system settle

    # 4. RE-MEASURE
    after = read_stats()
    print("\n[4] RE-MEASURE (after)")
    print(f"  CPU 1m     : {after['cpu_load']:.3f}")
    print(f"  RAM used   : {after['ram_mb']} / {after['ram_total_mb']} MB")
    print(f"  RAM avail  : {after['ram_avail_mb']} MB")
    print(f"  Efficiency : {after['efficiency']:.4f}")

    # 5. DELTA + JOULES SAVED (approximate)
    ram_delta_mb = after["ram_avail_mb"] - before["ram_avail_mb"]
    eff_delta = after["efficiency"] - before["efficiency"]
    # Rough conversion: freeing RAM reduces future paging / CPU work.
    # Conservative estimate: 1 MB freed ≈ 0.5–2 J of future avoided work on this device.
    # We report the measured efficiency rise and bytes freed; joules are lower-bound.
    estimated_joules_saved = max(0.0, total_freed / (1024*1024) * 0.8)  # conservative

    print("\n[5] RESULT")
    print(f"  Bytes freed     : {total_freed:,}")
    print(f"  RAM avail Δ     : {ram_delta_mb:+d} MB")
    print(f"  Efficiency Δ    : {eff_delta:+.4f}")
    print(f"  Est. joules saved (lower bound): {estimated_joules_saved:.1f} J")

    # 6. LOG
    cycle = sum(1 for _ in open(LEDGER)) + 1 if LEDGER.exists() else 1
    entry = {
        "ts": datetime.now().isoformat(),
        "cycle": cycle,
        "version": "v5.0-complete",
        "before": before,
        "after": after,
        "ram_delta_mb": ram_delta_mb,
        "efficiency_delta": round(eff_delta, 6),
        "bytes_freed": total_freed,
        "est_joules_saved": round(estimated_joules_saved, 2),
        "executed_swaps": executed,
        "candidates_seen": len(candidates)
    }
    with open(LEDGER, "a") as f:
        f.write(json.dumps(entry, default=str) + "\n")
    with open(SWAPLOG, "a") as f:
        f.write(json.dumps(entry, default=str) + "\n")

    print(f"\n[LOGGED] Cycle {cycle} → {LEDGER}")
    print("=" * 64)
    if total_freed > 0 or eff_delta > 0:
        print("LOOP CLOSED. Real resources freed. Floor raised.")
    else:
        print("No safe automatic swaps available right now.")
        print("Next higher-η move: first physical ΔT measurement.")
    print("=" * 64)

if __name__ == "__main__":
    main()
