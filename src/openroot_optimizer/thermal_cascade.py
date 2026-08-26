import csv
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Tuple

J_PER_KWH = 3_600_000.0

@dataclass
class Row:
    timestamp_utc: str
    dt_s: float
    ambient_C: float
    source_solar_W: float
    source_fuel_W: float
    source_electric_W: float
    source_human_W: float
    source_pumping_W: float
    source_controls_W: float
    source_maintenance_W: float
    eta_capture: float
    eta_transfer: float
    store_mass_kg: float
    store_cp_J_per_kgK: float
    store_T_min_C: float
    store_T_max_C: float
    store_T_C: float
    U_W_per_m2K: float
    A_m2: float
    load_high_temp_W: float
    load_dhw_W: float
    load_drying_W: float
    load_space_heat_W: float
    load_low_temp_W: float
    Tmin_high_temp_C: float
    Tmin_dhw_C: float
    Tmin_drying_C: float
    Tmin_space_heat_C: float
    Tmin_low_temp_C: float
    reliability_R: float
    confidence: str
    evidence_reference: str

def f(x): return float(x)

def parse_rows(path: Path) -> List[Row]:
    out = []
    with path.open("r", encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        for d in r:
            out.append(Row(
                timestamp_utc=d["timestamp_utc"],
                dt_s=f(d["dt_s"]),
                ambient_C=f(d["ambient_C"]),
                source_solar_W=f(d["source_solar_W"]),
                source_fuel_W=f(d["source_fuel_W"]),
                source_electric_W=f(d["source_electric_W"]),
                source_human_W=f(d["source_human_W"]),
                source_pumping_W=f(d["source_pumping_W"]),
                source_controls_W=f(d["source_controls_W"]),
                source_maintenance_W=f(d["source_maintenance_W"]),
                eta_capture=f(d["eta_capture"]),
                eta_transfer=f(d["eta_transfer"]),
                store_mass_kg=f(d["store_mass_kg"]),
                store_cp_J_per_kgK=f(d["store_cp_J_per_kgK"]),
                store_T_min_C=f(d["store_T_min_C"]),
                store_T_max_C=f(d["store_T_max_C"]),
                store_T_C=f(d["store_T_C"]),
                U_W_per_m2K=f(d["U_W_per_m2K"]),
                A_m2=f(d["A_m2"]),
                load_high_temp_W=f(d["load_high_temp_W"]),
                load_dhw_W=f(d["load_dhw_W"]),
                load_drying_W=f(d["load_drying_W"]),
                load_space_heat_W=f(d["load_space_heat_W"]),
                load_low_temp_W=f(d["load_low_temp_W"]),
                Tmin_high_temp_C=f(d["Tmin_high_temp_C"]),
                Tmin_dhw_C=f(d["Tmin_dhw_C"]),
                Tmin_drying_C=f(d["Tmin_drying_C"]),
                Tmin_space_heat_C=f(d["Tmin_space_heat_C"]),
                Tmin_low_temp_C=f(d["Tmin_low_temp_C"]),
                reliability_R=f(d["reliability_R"]),
                confidence=d["confidence"],
                evidence_reference=d["evidence_reference"],
            ))
    return out

def capacity_j(r: Row) -> float:
    return r.store_mass_kg * r.store_cp_J_per_kgK * (r.store_T_max_C - r.store_T_min_C)

def t_from_e(e: float, r: Row) -> float:
    denom = r.store_mass_kg * r.store_cp_J_per_kgK
    if denom <= 0:
        return r.store_T_min_C
    return r.store_T_min_C + (e / denom)

def loss_j(e_store: float, r: Row) -> float:
    t_store = t_from_e(e_store, r)
    dT = t_store - r.ambient_C
    if dT <= 0:
        return 0.0
    return r.U_W_per_m2K * r.A_m2 * dT * r.dt_s

def allocate_cascade(q_avail: float, r: Row, t_store_c: float) -> Tuple[Dict[str, float], Dict[str, float], float]:
    loads = [
        ("high_temp", r.load_high_temp_W * r.dt_s, r.Tmin_high_temp_C),
        ("dhw", r.load_dhw_W * r.dt_s, r.Tmin_dhw_C),
        ("drying", r.load_drying_W * r.dt_s, r.Tmin_drying_C),
        ("space_heat", r.load_space_heat_W * r.dt_s, r.Tmin_space_heat_C),
        ("low_temp", r.load_low_temp_W * r.dt_s, r.Tmin_low_temp_C),
    ]
    delivered = {k: 0.0 for k,_,_ in loads}
    unmet = {k: 0.0 for k,_,_ in loads}
    for k, q_req, tmin in loads:
        if t_store_c < tmin:
            unmet[k] = q_req
            continue
        q_del = min(q_avail, q_req)
        delivered[k] = q_del
        unmet[k] = q_req - q_del
        q_avail -= q_del
    return delivered, unmet, q_avail

def run(input_csv: Path, output_csv: Path, tol: float = 1e-6):
    rows = parse_rows(input_csv)
    if not rows:
        raise RuntimeError("no rows")
    r0 = rows[0]
    e_cap = capacity_j(r0)
    e_store = max(0.0, min(e_cap, r0.store_mass_kg * r0.store_cp_J_per_kgK * (r0.store_T_C - r0.store_T_min_C)))

    out = []
    cum_in = cum_use = cum_loss = cum_dump = 0.0

    for r in rows:
        e_cap = capacity_j(r)
        t_store = t_from_e(e_store, r)

        j_source = (r.source_solar_W + r.source_fuel_W) * r.dt_s
        j_ops = (r.source_electric_W + r.source_human_W + r.source_pumping_W + r.source_controls_W + r.source_maintenance_W) * r.dt_s
        j_in_total = j_source + j_ops

        q_captured = j_source * r.eta_capture
        q_charge = q_captured * r.eta_transfer * r.reliability_R

        q_loss = loss_j(e_store, r)

        q_avail_for_delivery = max(0.0, e_store + q_charge - q_loss)
        delivered, unmet, q_left = allocate_cascade(q_avail_for_delivery, r, t_store)

        q_deliver = sum(delivered.values())

        e_next_raw = e_store + q_charge - q_deliver - q_loss
        q_dump = 0.0
        if e_next_raw > e_cap:
            q_dump = e_next_raw - e_cap
            e_next = e_cap
        elif e_next_raw < 0:
            e_next = 0.0
        else:
            e_next = e_next_raw

        dE = e_next - e_store
        c_residual = dE - (q_charge - q_deliver - q_loss - q_dump)

        cum_in += j_in_total
        cum_use += q_deliver
        cum_loss += q_loss
        cum_dump += q_dump

        eta_capture = (q_captured / j_source) if j_source > 0 else 0.0
        eta_transfer = (q_charge / q_captured) if q_captured > 0 else 0.0
        eta_storage = (q_deliver / q_charge) if q_charge > 0 else 0.0
        eta_whole_inst = (q_deliver / j_in_total) if j_in_total > 0 else 0.0
        eta_whole_cum = (cum_use / cum_in) if cum_in > 0 else 0.0

        out.append({
            "timestamp_utc": r.timestamp_utc,
            "dt_s": r.dt_s,
            "J_input_total": j_in_total,
            "J_source_available": j_source,
            "J_captured": q_captured,
            "J_charge_to_store": q_charge,
            "J_storage_loss": q_loss,
            "J_dump": q_dump,
            "J_delivered_total": q_deliver,
            "J_delivered_high_temp": delivered["high_temp"],
            "J_delivered_dhw": delivered["dhw"],
            "J_delivered_drying": delivered["drying"],
            "J_delivered_space_heat": delivered["space_heat"],
            "J_delivered_low_temp": delivered["low_temp"],
            "J_unmet_high_temp": unmet["high_temp"],
            "J_unmet_dhw": unmet["dhw"],
            "J_unmet_drying": unmet["drying"],
            "J_unmet_space_heat": unmet["space_heat"],
            "J_unmet_low_temp": unmet["low_temp"],
            "E_store_J_start": e_store,
            "E_store_J_end": e_next,
            "SOC": (e_next / e_cap) if e_cap > 0 else 0.0,
            "T_store_C_start": t_store,
            "T_store_C_end": t_from_e(e_next, r),
            "eta_capture": eta_capture,
            "eta_transfer": eta_transfer,
            "eta_storage": eta_storage,
            "eta_whole_inst": eta_whole_inst,
            "eta_whole_cum": eta_whole_cum,
            "C_residual_J": c_residual,
            "C_within_tolerance": abs(c_residual) <= tol,
            "confidence": r.confidence,
            "evidence_reference": r.evidence_reference
        })
        e_store = e_next

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        for row in out:
            w.writerow(row)

def main():
    root = Path(__file__).resolve().parents[2]
    inp = root / "data" / "thermal_cascade_inputs.csv"
    out = root / "data" / "thermal_cascade_ledger.csv"
    run(inp, out)
    print(f"ok: wrote {out}")

if __name__ == "__main__":
    main()
