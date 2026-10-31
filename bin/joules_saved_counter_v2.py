# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""CANARY:OPENROOT-JOULES-SAVED-V2 — Running tally of joules saved by cached pathways."""
import sqlite3, json, time, os, sys

LEDGER = "/home/jesse/openroot/data/joules_saved.jsonl"
# TDP estimate for OptiPlex 3060 under mixed load (watts); RAPL read if available
TDP_W = 65
def read_rapl():
    try:
        j = sum(float(open(f"/sys/class/powercap/intel-rapl:{i}/energy_uj").read())
                for i in range(2) if os.path.exists(f"/sys/class/powercap/intel-rapl:{i}/energy_uj"))
        return j
    except Exception:
        return None

def estimate_joules(duration_s, source="estimate"):
    return (TDP_W * duration_s), source

def log_hit(label, avoided_seconds, source=None):
    j, src = (avoided_seconds * read_rapl_watts() if False else estimate_joules(avoided_seconds))
    entry = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
             "pathway": label, "avoided_seconds": avoided_seconds,
             "joules_saved": round(j, 3), "source": src}
    with open(LEDGER, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry

def total():
    tot = 0.0
    n = 0
    if os.path.exists(LEDGER):
        for line in open(LEDGER):
            try:
                tot += json.loads(line)["joules_saved"]; n += 1
            except Exception: pass
    return tot, n

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        e = log_hit(sys.argv[1], float(sys.argv[2]))
        print(f"[banked] {e['pathway']}: {e['joules_saved']:.1f} J saved ({e['source']})")
    tot, n = total()
    print(f"TOTAL: {tot:.1f} J ({tot/3600000:.6f} kWh) across {n} cached-pathway hits")
