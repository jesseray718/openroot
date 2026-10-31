#!/data/data/com.termux/files/usr/bin/python3
import json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path
OPENROOT = Path("/sdcard/openroot")
JOULE_LOG = OPENROOT / "context_bridge" / "seed_oracle_joules.jsonl"
def ensure():
    JOULE_LOG.parent.mkdir(parents=True, exist_ok=True)
def rish(cmd, timeout=6):
    try:
        r = subprocess.run(["rish", "-c", cmd], capture_output=True, text=True, timeout=timeout, env={**os.environ, "RISH_PRESERVE_ENV": "0"})
        if r.returncode == 0: return r.stdout.strip()
    except: pass
    return None
def termux_battery():
    try:
        r = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0: return json.loads(r.stdout)
    except: pass
    return None
def sysfs_sample():
    v = rish("cat /sys/class/power_supply/battery/voltage_now")
    i = rish("cat /sys/class/power_supply/battery/current_now")
    c = rish("cat /sys/class/power_supply/battery/charge_counter")
    def to_int(s):
        try: return int(s)
        except: return None
    return {"voltage_uV": to_int(v), "current_uA": to_int(i), "charge_uAh": to_int(c)}
def sample(tag="point"):
    ensure()
    rec = {"ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "tag": tag, "sysfs": sysfs_sample(), "termux": termux_battery()}
    with open(JOULE_LOG, "a") as f: f.write(json.dumps(rec) + "\n")
    return rec
if __name__ == "__main__":
    import sys
    print(json.dumps(sample(sys.argv[1] if len(sys.argv)>1 else "manual"), indent=2))
