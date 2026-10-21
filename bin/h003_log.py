#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--t-in", type=float, required=True)
ap.add_argument("--t-out", type=float, required=True)
ap.add_argument("--t-core", type=float, default=None)
ap.add_argument("--t-amb", type=float, default=None)
ap.add_argument("--irr", type=float, default=None)
ap.add_argument("--flow", type=float, default=None)
ap.add_argument("--pump-w", type=float, default=None)
ap.add_argument("--photo", default=None)
ap.add_argument("--mass-kg", type=float, default=None)
ap.add_argument("--note", default="")
args = ap.parse_args()
out = Path(args.out)
if not out.is_absolute():
    raise SystemExit("REFUSE: --out must be absolute")
out.parent.mkdir(parents=True, exist_ok=True)
row = {
    "ts": datetime.now(timezone.utc).isoformat(),
    "schema": "H003-LOG-1",
    "grade": "OPEN",
    "area_m2": 1.0,
    "t_in_c": args.t_in,
    "t_out_c": args.t_out,
    "t_core_c": args.t_core,
    "t_amb_c": args.t_amb,
    "dT_c": args.t_out - args.t_in,
    "irr_w_m2": args.irr,
    "irradiance_lock_w_m2": 931.0,
    "flow_l_min": args.flow,
    "pump_w": args.pump_w,
    "service_ratio_1_34": "MODEL",
    "photo": args.photo,
    "mass_kg": args.mass_kg,
    "note": args.note,
}
with out.open("a", encoding="utf-8") as f:
    f.write(json.dumps(row, separators=(",", ":")) + "\n")
print(json.dumps({"wrote": str(out), "dT_c": row["dT_c"], "grade": "OPEN"}))
