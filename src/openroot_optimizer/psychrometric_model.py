import math
import csv
from pathlib import Path
from typing import Dict, Any, List

# Conservative engineering approximations
# P_atm fixed at sea-level unless provided
P_ATM_KPA = 101.325
CP_DRY_AIR_KJ_KG_K = 1.006
CP_VAPOR_KJ_KG_K = 1.86

def saturation_vapor_pressure_kpa(T_c: float) -> float:
    # Tetens approximation (0-50 C practical band)
    return 0.61078 * math.exp((17.2694 * T_c) / (T_c + 237.29))

def humidity_ratio_kg_per_kg_da(T_c: float, RH_pct: float, p_kpa: float = P_ATM_KPA) -> float:
    RH = max(0.0, min(100.0, RH_pct)) / 100.0
    p_ws = saturation_vapor_pressure_kpa(T_c)
    p_w = RH * p_ws
    return 0.62198 * p_w / max(1e-9, (p_kpa - p_w))

def moist_air_enthalpy_kj_per_kg_da(T_c: float, w: float) -> float:
    # h = 1.006T + w(2501 + 1.86T)
    return CP_DRY_AIR_KJ_KG_K * T_c + w * (2501.0 + CP_VAPOR_KJ_KG_K * T_c)

def dry_air_mass_flow_kg_s(airflow_m3_s: float, rho_air_kg_m3: float = 1.2) -> float:
    # approximation for total moist flow to dry-air equivalent
    return max(0.0, airflow_m3_s) * rho_air_kg_m3

def cooling_power_w(T_in, RH_in, T_out, RH_out, airflow_m3_s) -> float:
    w_in = humidity_ratio_kg_per_kg_da(T_in, RH_in)
    w_out = humidity_ratio_kg_per_kg_da(T_out, RH_out)
    h_in = moist_air_enthalpy_kj_per_kg_da(T_in, w_in)
    h_out = moist_air_enthalpy_kj_per_kg_da(T_out, w_out)
    mdot_da = dry_air_mass_flow_kg_s(airflow_m3_s)
    delta_h_kj_kg = h_in - h_out
    return max(0.0, mdot_da * delta_h_kj_kg * 1000.0)

def parse_float(x, default=None):
    try:
        if x is None or x == "":
            return default
        return float(x)
    except:
        return default

def run_from_csv(input_csv: Path, output_csv: Path):
    rows_out: List[Dict[str, Any]] = []
    with input_csv.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            mode = row.get("mode","").strip().lower()
            T_in = parse_float(row.get("T_in_C"))
            RH_in = parse_float(row.get("RH_in_pct"))
            T_out = parse_float(row.get("T_out_C"))
            RH_out = parse_float(row.get("RH_out_pct"))
            flow = parse_float(row.get("airflow_m3_s"), 0.0)
            fan_w = parse_float(row.get("fan_power_W"), 0.0) or 0.0
            pump_w = parse_float(row.get("pump_power_W"), 0.0) or 0.0
            p_elec = fan_w + pump_w

            cool_w = None
            cop_like = None

            if mode == "cooling" and None not in (T_in, RH_in, T_out, RH_out):
                cool_w = cooling_power_w(T_in, RH_in, T_out, RH_out, flow)
                cop_like = (cool_w / p_elec) if p_elec > 0 else None

            rows_out.append({
                "trial_id": row.get("trial_id"),
                "timestamp_utc": row.get("timestamp_utc"),
                "mode": mode,
                "cooling_power_W": cool_w,
                "electric_input_W": p_elec,
                "cop_like": cop_like,
                "confidence": row.get("confidence","unknown"),
                "evidence_reference": row.get("evidence_reference","")
            })

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()) if rows_out else [
            "trial_id","timestamp_utc","mode","cooling_power_W","electric_input_W","cop_like","confidence","evidence_reference"
        ])
        w.writeheader()
        for x in rows_out:
            w.writerow(x)

if __name__ == "__main__":
    inp = Path("/sdcard/openroot/data/rmh_labyrinth_inputs.csv")
    out = Path("/sdcard/openroot/data/rmh_labyrinth_results.csv")
    run_from_csv(inp, out)
    print(f"ok: wrote {out}")
