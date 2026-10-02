#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# [FRONTV2WATER] Delivered WATER heat (50C sink) per config, physical-temp filter
import json
from datetime import datetime

src = open("thermal_balance_v63.py").read()
ns = {}
exec(src.split("TARGET_TEMP, MIN_STEAM")[0], ns)
compute_flow = ns["compute_flow"]

T_SINK = 50.0        # tilapia/microgreens water target
EFF = 0.75           # conservative HX effectiveness
PHYS_CAP_C = 350.0   # radiative-equilibrium ceiling (341C) + margin — filters overshoot

rows = []
for n_ch in range(4, 41, 4):
    for n_p in range(8, 25):
        for ch_d_cm in [5, 8, 10, 15, 20, 25, 30]:
            ch_d = ch_d_cm / 100
            for chimney in [6, 8, 10, 12, 15]:
                flow, temp, solar_cap, resid = compute_flow(n_ch, n_p, ch_d, chimney)
                if not flow or not temp or temp <= T_SINK or temp > PHYS_CAP_C:
                    continue
                q_water = EFF * flow * 1005 * (temp - T_SINK)  # watts delivered to water
                if q_water <= 0:
                    continue
                rows.append({"n_ch": n_ch, "n_p": n_p, "ch_d_cm": ch_d_cm,
                             "chimney_m": chimney, "temp_C": round(float(temp), 1),
                             "flow_kgs": round(float(flow), 4),
                             "q_water_W": round(float(q_water)),
                             "aperture_m2": n_p * 5,
                             "kwh_day_5sun": round(q_water * 5 / 1000, 1)})

rows.sort(key=lambda r: -r["q_water_W"])
print(f"  Physical configs (50C sink, temp<={PHYS_CAP_C:.0f}C): {len(rows)}")
print(f"\n  TOP 10 BY DELIVERED WATER HEAT")
print(f"  {'kW':>6} {'kWh/d':>7} {'T_C':>6} {'flow':>7} {'Ch':>3} {'Pan':>4} {'Dcm':>4} {'Chim':>4}")
for r in rows[:10]:
    print(f"  {r['q_water_W']/1000:>6.2f} {r['kwh_day_5sun']:>7.1f} {r['temp_C']:>6.0f} "
          f"{r['flow_kgs']:>7.3f} {r['n_ch']:>3} {r['n_p']:>4} {r['ch_d_cm']:>4} {r['chimney_m']:>4}")

best = rows[0] if rows else {}
with open("data/thermal_frontier_v2_water.json", "w") as fh:
    json.dump({"version": "FRONTV2WATER", "timestamp": datetime.now().isoformat(),
               "sink_C": T_SINK, "eff": EFF, "physical_cap_C": PHYS_CAP_C,
               "top10": rows[:10],
               "note": "Note: compute_flow overshoots above ~341C radiative equilibrium; filtered"}, fh, indent=2)
print(f"\n[banked] water frontier -> data/thermal_frontier_v2_water.json")
print("[exit=0] FRONTV2WATER")
