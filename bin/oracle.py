#!/usr/bin/env python3
"""OpenRoot UNE Oracle — offline joule-native engine"""
import json, os, sys, time, shutil, subprocess, re
from pathlib import Path
from datetime import datetime

HOME = Path("/data/data/com.termux/files/home")
REPO = HOME / "openroot"
LEDGER = REPO / "04_DATA" / "floor_raise_log.jsonl"
DATA = REPO / "04_DATA"

for p in [REPO, DATA, REPO/"bin"]:
    p.mkdir(parents=True, exist_ok=True)

KNOWLEDGE = {
    "η": "η = useful_joules / human_joules. Only performance language allowed. Write only measured joules into the ledger.",
    "hierarchy": "1. A15 + Kai9000 + Termux = GOVERNOR-01. 2. OptiPlex 3060 = heavy spoke. 3. Cloud burst. 4. Thin nodes later.",
    "aerocement": "Volumetric open-cell aerated cement + activated carbon. Triple utility: mechanical work (Stirling), heat/cool transport, energy capture target approximately 93 percent. Passive solar-thermal. PoPW. RWA/DePIN. Open-source.",
    "control_loop": "Sensor → condition → ranked possibility. Observe → Interact → Measure → Regulate. Same loop on phone and on thermal mass.",
    "raise_floor": "Measure → detect → safe act → re-measure → log. When deltas go to zero, software surplus is exhausted. Pivot to physical.",
    "physical_map": "Software efficiency ↔ useful thermal work. RAM available ↔ usable delta-T. Cache clean ↔ seal leaks / remove dead mass. Large models (manual) ↔ oversized mass that stores but never delivers. Observation cost ↔ heat lost by probing.",
    "rules": "Absolute paths only. Never auto-delete models. Privilege degrades (rish → termux → stdlib). One-hot RAM. Measured numbers only in ledger.",
    "pending": "Instrument prototype (airflow, delta-T hot/cold, shaft work). Write measured joules. Finish black-locust-rmh. OptiPlex llama-server. Syncthing.",
    "device": "Samsung Galaxy A15 Helio G99, approximately 3.5 GB usable. Higher η at lower frequency.",
    "oracle": "This offline tool. Sensors + ledger + knowledge + query + physical advisor + floor engine."
}

def rish(cmd, timeout=5):
    try:
        r = subprocess.run(["rish", "-c", cmd], capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None

def read_stats():
    s = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "cpu_load": 0.0, "ram_total_mb": 0, "ram_avail_mb": 0,
        "temp_c": None, "battery_pct": None, "battery_ua": None, "battery_uv": None,
        "uptime_h": None, "privilege": "termux", "power_mw": None, "efficiency": 0.0
    }
    try:
        with open("/proc/loadavg") as f:
            s["cpu_load"] = float(f.read().split()[0])
    except: pass
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    s["ram_total_mb"] = int(line.split()[1]) // 1024
                elif line.startswith("MemAvailable:"):
                    s["ram_avail_mb"] = int(line.split()[1]) // 1024
    except: pass
    try:
        with open("/proc/stat") as f:
            for line in f:
                if line.startswith("btime"):
                    s["uptime_h"] = round((time.time() - int(line.split()[1])) / 3600.0, 2)
                    break
    except: pass

    # Thermal
    for z in range(15):
        try:
            with open(f"/sys/class/thermal/thermal_zone{z}/temp") as f:
                t = int(f.read().strip()) / 1000.0
                if 15 < t < 95:
                    s["temp_c"] = round(t, 1)
                    break
        except: pass
    if s["temp_c"] is None:
        out = rish("cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null")
        if out and out.isdigit():
            s["temp_c"] = round(int(out)/1000.0, 1)
            s["privilege"] = "rish"

    # Battery — prefer rish
    out = rish("cat /sys/class/power_supply/battery/capacity 2>/dev/null")
    if out and out.isdigit():
        s["battery_pct"] = int(out)
        s["privilege"] = "rish"
    else:
        try:
            with open("/sys/class/power_supply/battery/capacity") as f:
                s["battery_pct"] = int(f.read().strip())
        except: pass

    out = rish("cat /sys/class/power_supply/battery/current_now 2>/dev/null")
    if out and out.lstrip("-").isdigit():
        s["battery_ua"] = int(out)
        s["privilege"] = "rish"

    out = rish("cat /sys/class/power_supply/battery/voltage_now 2>/dev/null")
    if out and out.isdigit():
        s["battery_uv"] = int(out)
        s["privilege"] = "rish"

    if s["battery_ua"] is not None and s["battery_uv"] is not None:
        s["power_mw"] = round(abs(s["battery_ua"]) * s["battery_uv"] / 1e9, 1)

    cpu_eff = max(0.0, 1.0 - min(s["cpu_load"], 2.0) / 2.0)
    ram_ratio = s["ram_avail_mb"] / max(s["ram_total_mb"], 1)
    s["efficiency"] = round(cpu_eff * 0.40 + ram_ratio * 0.60, 4)
    return s

def find_models():
    found = []
    for d in [HOME/"models", HOME/".ollama", HOME/"llama.cpp", REPO/"models", Path("/sdcard")]:
        if not d.exists(): continue
        try:
            for f in d.rglob("*.gguf"):
                try:
                    sz = f.stat().st_size
                    if sz > 40 * 1024 * 1024:
                        found.append({"path": str(f), "name": f.name, "mb": round(sz/1024/1024, 1)})
                except: pass
        except: pass
    found.sort(key=lambda x: -x["mb"])
    return found

def status():
    st = read_stats()
    models = find_models()
    print("=" * 58)
    print("  OPENROOT UNE ORACLE — STATUS")
    print("=" * 58)
    print(f"  Time        {st['ts']}")
    print(f"  Efficiency  {st['efficiency']:.4f}")
    print(f"  RAM         {st['ram_avail_mb']} / {st['ram_total_mb']} MB")
    print(f"  CPU 1m      {st['cpu_load']:.3f}")
    print(f"  Temp        {st.get('temp_c')} C")
    print(f"  Battery     {st.get('battery_pct')} %    power={st.get('power_mw')} mW")
    print(f"  Uptime      {st.get('uptime_h')} h")
    print(f"  Privilege   {st['privilege']}")
    print(f"  Models      {len(models)} large GGUF")
    for m in models[:6]:
        print(f"              {m['mb']:7.1f} MB  {m['name']}")
    print("=" * 58)

def query(q):
    q = q.strip().lower()
    if not q:
        return "Empty query"
    results = []
    st = read_stats()
    live = f"Live efficiency {st['efficiency']:.4f} | RAM {st['ram_avail_mb']}/{st['ram_total_mb']} MB | temp {st.get('temp_c')} | battery {st.get('battery_pct')}% | priv {st['privilege']}"
    results.append((0.9, "LIVE", live))
    for k, v in KNOWLEDGE.items():
        if any(tok in (k+" "+v).lower() for tok in q.split()):
            results.append((0.7, k.upper(), v))
    if "model" in q or "gguf" in q:
        models = find_models()
        results.append((0.8, "MODELS", " | ".join(f"{m['name']} ({m['mb']}MB)" for m in models[:5])))
    if "physical" in q or "thermal" in q or "delta" in q:
        results.append((0.85, "PHYSICAL", KNOWLEDGE["physical_map"]))
    if not results:
        return "No match. Try: status | models | physical | eta | aerocement | hierarchy"
    out = []
    for sc, title, body in results[:6]:
        out.append(f"[{sc:.2f}] {title}\n{body}")
    return "\n\n".join(out)

def main():
    args = sys.argv[1:]
    if not args or args[0] in ("help", "manual"):
        print("Commands: status | models | query <text> | physical | eta | log")
        return
    cmd = args[0].lower()
    if cmd == "status":
        status()
    elif cmd == "models":
        for m in find_models():
            print(f"{m['mb']:8.1f}  {m['path']}")
    elif cmd == "query":
        print(query(" ".join(args[1:])))
    elif cmd == "physical":
        print(KNOWLEDGE["physical_map"])
        print("\nNext physical: measure baseline delta-T with thermometer. One change only. Re-measure. Log only measured numbers.")
    elif cmd in ("η", "eta"):
        st = read_stats()
        print(f"eta {st['efficiency']:.4f} | RAM free {st['ram_avail_mb']} MB | priv {st['privilege']}")
        print("1. Decide large GGUF files\n2. Physical thermometer baseline\n3. Keep phone one-hot")
    elif cmd == "log":
        if LEDGER.exists():
            lines = LEDGER.read_text().strip().splitlines()[-5:]
            for line in lines:
                print(line[:220])
        else:
            print("No ledger yet")
    else:
        print(query(" ".join(args)))

if __name__ == "__main__":
    main()
