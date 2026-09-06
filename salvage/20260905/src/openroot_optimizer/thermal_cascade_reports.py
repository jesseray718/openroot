import csv
from pathlib import Path

def main():
    root = Path(__file__).resolve().parents[2]
    inp = root / "data" / "thermal_cascade_ledger.csv"
    out1 = root / "reports" / "THERMAL_CASCADE_LEDGER.md"
    out2 = root / "reports" / "CASCADE_STAGE_TABLE.md"

    rows = []
    with inp.open("r", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    if not rows:
        raise RuntimeError("empty ledger")

    n = len(rows)
    sum_in = sum(float(r["J_input_total"]) for r in rows)
    sum_use = sum(float(r["J_delivered_total"]) for r in rows)
    sum_loss = sum(float(r["J_storage_loss"]) for r in rows)
    sum_dump = sum(float(r["J_dump"]) for r in rows)
    eta = (sum_use / sum_in) if sum_in > 0 else 0.0
    soc_min = min(float(r["SOC"]) for r in rows)
    soc_max = max(float(r["SOC"]) for r in rows)
    soc_avg = sum(float(r["SOC"]) for r in rows)/n

    out1.parent.mkdir(parents=True, exist_ok=True)
    with out1.open("w", encoding="utf-8") as f:
        f.write("# THERMAL_CASCADE_LEDGER\n\n")
        f.write(f"- samples: {n}\n")
        f.write(f"- input_total_J: {sum_in}\n")
        f.write(f"- delivered_total_J: {sum_use}\n")
        f.write(f"- storage_loss_J: {sum_loss}\n")
        f.write(f"- dumped_J: {sum_dump}\n")
        f.write(f"- eta_whole: {eta}\n")
        f.write(f"- soc_min: {soc_min}\n")
        f.write(f"- soc_max: {soc_max}\n")
        f.write(f"- soc_avg: {soc_avg}\n")

    stage_keys = [
        "J_delivered_high_temp","J_delivered_dhw","J_delivered_drying","J_delivered_space_heat","J_delivered_low_temp"
    ]
    sums = {k: sum(float(r[k]) for r in rows) for k in stage_keys}
    with out2.open("w", encoding="utf-8") as f:
        f.write("# CASCADE_STAGE_TABLE\n\n")
        for k in stage_keys:
            f.write(f"- {k}: {sums[k]} J\n")

    print(f"ok: wrote {out1}")
    print(f"ok: wrote {out2}")

if __name__ == "__main__":
    main()
