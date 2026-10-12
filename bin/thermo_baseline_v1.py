#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""thermo_baseline_v1.py — RAPL energy sampling, TDP estimate fallback.
Usage: thermo_baseline_v1.py --seconds N --label idle|load"""
import argparse, glob, json, os, time
OUT = "/home/jesse/openroot/data/thermo_baselines.jsonl"
TDP_W = 65.0

def read_rapl():
    vals = {}
    for d in glob.glob("/sys/class/powercap/intel-rapl*/"):
        f, n = os.path.join(d, "energy_uj"), os.path.join(d, "name")
        if os.path.exists(f):
            try:
                key = open(n).read().strip() if os.path.exists(n) else os.path.basename(d.rstrip("/"))
                vals[key] = int(open(f).read().strip())
            except Exception:
                pass
    return vals

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=10)
    ap.add_argument("--label", default="idle")
    a = ap.parse_args()
    a1 = read_rapl()
    time.sleep(a.seconds)
    a2 = read_rapl()
    domains, measured = {}, False
    for k, v2 in a2.items():
        v1 = a1.get(k)
        if v1 is not None and v2 >= v1:
            j = (v2 - v1) / 1e6
            domains[k] = {"joules": round(j, 3), "watts_avg": round(j / a.seconds, 3)}
            measured = True
    rec = {"label": a.label, "seconds": a.seconds,
           "source": "rapl" if measured else "estimate",
           "domains": domains,
           "estimate_joules": None if measured else round(TDP_W * a.seconds * 0.35, 3)}
    with open(OUT, "a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    detail = "; ".join("%s=%.2fW" % (k, v["watts_avg"]) for k, v in domains.items())
    print("[banked] %s %ds source=%s %s" % (a.label, a.seconds, rec["source"],
        detail or ("estimate=%.1fJ" % (rec["estimate_joules"] or 0))))

if __name__ == "__main__":
    main()
