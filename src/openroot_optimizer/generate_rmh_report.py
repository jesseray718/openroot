import csv
from pathlib import Path

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
        if cp not in ("", None):
            cop_vals.append(float(cp))

    avg_cooling_w = (total_cooling_w / n_cooling) if n_cooling else 0.0
    avg_elec_w = (total_elec_w / n_cooling) if n_cooling else 0.0
    avg_cop = (sum(cop_vals)/len(cop_vals)) if cop_vals else 0.0

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
        f.write("## Notes\n")
        f.write("- This is a measured/estimated scaffold, not a universal claim.\n")
        f.write("- Replace assumptions with calibrated sensor data for decision-grade output.\n")

    print(f"ok: wrote {OUT}")

if __name__ == "__main__":
    main()
