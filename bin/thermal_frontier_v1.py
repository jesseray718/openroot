#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# [FRONTV1] Pareto scan of v6.3 audited physics — max steam delivery per temp band
# Sweeps the SAME solver functions as thermal_balance_v63.py, no targets imposed.
import json
from datetime import datetime

src = open("thermal_balance_v63.py").read()
head = src.split("TARGET_TEMP, MIN_STEAM")[0]  # defs + constants, stops before the sweep
ns = {}
exec(head, ns)
compute_flow = ns["compute_flow"]
steam_hx = ns["steam_hx_performance"]

results = []
for n_ch in range(4, 41, 4):
    for n_p in range(8, 25):
        for ch_d_cm in [5, 8, 10, 15, 20, 25, 30]:
            ch_d = ch_d_cm / 100
            for chimney in [6, 8, 10, 12, 15]:
                flow, temp, solar_cap, resid = compute_flow(n_ch, n_p, ch_d, chimney)
                if flow is None or temp is None:
                    continue
                q_steam, T_out, UA, A_HX = steam_hx(temp, flow)
                if q_steam is None or q_steam <= 0:
                    continue
                complexity = n_ch * n_p * (ch_d_cm ** 2)
                results.append({
                    "n_ch": n_ch, "n_p": n_p, "ch_d_cm": ch_d_cm, "chimney_m": chimney,
                    "temp_C": round(float(temp), 1), "q_steam_W": round(float(q_steam)),
                    "electric_W": round(float(q_steam) * 0.232),
                    "complexity": complexity})

print(f"Configs evaluated: {len(results)}")
best_by_temp = {}
for r in results:
    t = int(r["temp_C"] // 10 * 10)
    cur = best_by_temp.get(t)
    if cur is None or r["q_steam_W"] > cur["q_steam_W"]:
        best_by_temp[t] = r

print(f"\n  {'AirC':>5} {'MaxSteam_W':>11} {'Elec_W':>8} {'Ch':>3} {'Pan':>4} {'Dcm':>4} {'Chim':>4}")
for t in sorted(best_by_temp, reverse=True):
    r = best_by_temp[t]
    print(f"  {t:>5} {r['q_steam_W']:>11,} {r['electric_W']:>8,} {r['n_ch']:>3} {r['n_p']:>4} {r['ch_d_cm']:>4} {r['chimney_m']:>4}")

payload = {"version": "FRONTV1", "timestamp": datetime.now().isoformat(),
           "region_basis": "SE Missouri ~4.5-5 equiv sun-hours (capacity basis applied downstream)",
           "note": "Best steam delivery per 10C band, v6.3 audited physics, no target imposed",
           "frontier": [best_by_temp[t] for t in sorted(best_by_temp, reverse=True)]}
out = "data/thermal_frontier_v1.json"
with open(out, "w") as fh:
    json.dump(payload, fh, indent=2)
print(f"\n[banked] frontier saved -> {out}")
print("[exit=0] FRONTV1")
