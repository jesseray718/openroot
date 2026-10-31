import csv
from pathlib import Path
from src.openroot_optimizer.rmh_labyrinth_model import compare_current_vs_rmh_lab

INP = Path("/sdcard/openroot/data/rmh_labyrinth_results.csv")
OUT = Path("/sdcard/openroot/reports/RMH_LABYRINTH_COMPARISON.md")

def main():
    rows = []
    if INP.exists():
        with INP.open("r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

    total_cooling_w = 0.0
    total_elec_w = 0.0
    n_cooling = 0
    n_elec = 0
    cop_vals = []

    for r in rows:
        cw = r.get("cooling_power_W")
        ew = r.get("electric_input_W")
        cp = r.get("cop_like")
        if cw not in ("", None):
            total_cooling_w += float(cw)
            n_cooling += 1
        if ew not in ("", None):
            total_elec_w += float(ew)
            n_elec += 1
        if cp not in ("", None):
            cop_vals.append(float(cp))

    avg_cooling_w = (total_cooling_w / n_cooling) if n_cooling else 0.0
    avg_elec_w = (total_elec_w / n_elec) if n_elec else 0.0
    avg_cop = (sum(cop_vals)/len(cop_vals)) if cop_vals else 0.0

    current_case, proposed_case = compare_current_vs_rmh_lab()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        f.write("# RMH_LABYRINTH_COMPARISON\n\n")
        f.write("## Scope\n")
        f.write("- Conservative trial summary from `data/rmh_labyrinth_results.csv`\n")
        f.write("- Policy: heat for heat, cold for cold\n\n")
        f.write("## Aggregates\n")
        f.write(f"- samples: {len(rows)}\n")
        f.write(f"- avg_cooling_power_W: {avg_cooling_w}\n")
        f.write(f"- avg_electric_input_W: {avg_elec_w}\n")
        f.write(f"- avg_cop_like: {avg_cop}\n\n")
        f.write("## Scenario Comparison\n\n")
        f.write("### Current (All-Electric)\n")
        f.write(f"- heat_demand_J: {current_case['heat_demand_J']}\n")
        f.write(f"- cool_demand_J: {current_case['cool_demand_J']}\n")
        f.write(f"- dhw_demand_J: {current_case['dhw_demand_J']}\n")
        f.write(f"- electric_fallback_kWh: {current_case['electric_fallback_kWh']:.2f}\n")
        f.write(f"- baseline_all_electric_kWh: {current_case['baseline_all_electric_kWh']:.2f}\n\n")
        f.write("### Proposed (RMH + Labyrinth Hybrid)\n")
        f.write(f"- heat_demand_J: {proposed_case['heat_demand_J']}\n")
        f.write(f"- cool_demand_J: {proposed_case['cool_demand_J']}\n")
        f.write(f"- dhw_demand_J: {proposed_case['dhw_demand_J']}\n")
        f.write(f"- heat_served_by_rmh_J: {proposed_case['heat_served_by_rmh_J']}\n")
        f.write(f"- cool_served_by_labyrinth_J: {proposed_case['cool_served_by_labyrinth_J']}\n")
        f.write(f"- dhw_served_by_rmh_J: {proposed_case['dhw_served_by_rmh_J']}\n")
        f.write(f"- electric_fallback_kWh: {proposed_case['electric_fallback_kWh']:.2f}\n")
        f.write(f"- electricity_saved_kWh: {proposed_case['electricity_saved_kWh']:.2f}\n\n")
        f.write("## Notes\n")
        f.write("- This is a measured/estimated scaffold, not a universal claim.\n")
        f.write("- Replace assumptions with calibrated sensor data for decision-grade output.\n")

    print(f"ok: wrote {OUT}")

if __name__ == "__main__":
    main()
