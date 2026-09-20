#!/usr/bin/env python3
HEAD
"""Write RMH comparison next to this repo. Works on OptiPlex and A15 mesh."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.openroot_optimizer.rmh_labyrinth_model import compare_current_vs_rmh_lab

OUT = ROOT / "reports" / "RMH_LABYRINTH_COMPARISON.md"
BOX = ROOT / "reports" / "RMH_LABYRINTH_COMPARISON_BOX.md"
JSON_OUT = ROOT / "reports" / "rmh_compare.json"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = compare_current_vs_rmh_lab()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = [
        "# RMH + labyrinth comparison",
        "generated: " + now,
        "root: " + str(ROOT),
        "N14: model output, not pad measurement.",
        "CSV trial.A1.sample is a 3-row fixture. Do not publish as a hang.",
        "",
        "```json",
        json.dumps(data, indent=2, default=str),
        "```",
        "",
    ]
    text = "\n".join(body)
    OUT.write_text(text, encoding="utf-8")
    BOX.write_text(text, encoding="utf-8")
    JSON_OUT.write_text(json.dumps({"generated": now, "root": str(ROOT), "n14": "model", "data": data}, indent=2, default=str) + "\n", encoding="utf-8")
    print("wrote", OUT)
    print("wrote", BOX)
    print("wrote", JSON_OUT)


if __name__ == "__main__":
    main()
=======
import sys, os
from pathlib import Path
from datetime import datetime, timezone
HOME = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
sys.path.insert(0, str(HOME / "aerocement"))
from aerocement_calc import calc_solar, compare_current_vs_rmh_lab
def main(area_m2=10.0):
    out = HOME / "openroot" / "output" / f"rmh_lab_report_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    solar = calc_solar(area_m2, 931.0, 5.0)
    scenarios = compare_current_vs_rmh_lab(floor_area_m2=area_m2*10)
    lines = ["# OpenRoot RMH + Cooling Labyrinth Report",
             f"Generated: {datetime.now(timezone.utc).isoformat()}",
             "Location: Sikeston, Missouri", "",
             "## H-003 Solar Capture",
             f"- Area: {solar.area_m2} m²",
             f"- Irradiance: {solar.irradiance_w_m2} W/m²",
             f"- Daily energy: **{solar.daily_energy_kwh:.2f} kWh**", "",
             "## Scenario Comparison (CodeRabbit required)"]
    for key in ("current", "proposed", "electrical_fallback"):
        s = scenarios[key]
        lines += [f"### {s['name']}", f"- Thermal: {s['thermal_kwh_day']} kWh/day",
                  f"- Electrical: {s['electrical_kwh_day']} kWh/day", f"- Cost: ${s['cost_usd_day']}/day",
                  f"- η: {s['eta']}", f"- Notes: {s['notes']}", ""]
    lines += ["## Savings",
              f"- Electricity: **{scenarios['electricity_savings_kwh_day']} kWh/day**",
              f"- Cost: **${scenarios['cost_savings_usd_day']}/day**",
              f"- Annual: **{scenarios['annual_elec_savings_kwh']} kWh**", "",
              f"Nightly capture target: {scenarios['nightly_capture_kwh_m2']} kWh/m²",
              "η = useful_joules / human_joules | R=1.0 | forks absorbed"]
    text = "\n".join(lines)
    out.write_text(text)
    print(text)
    print(f"\n[written] {out}")
if __name__ == "__main__":
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 10.0)
 cb5c3dd (auto: 20260826T134225Z)
