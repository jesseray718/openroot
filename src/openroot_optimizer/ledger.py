import json
from pathlib import Path
import csv

DATA_DIR = Path("/sdcard/openroot/data")
REPORTS_DIR = Path("/sdcard/openroot/reports")
EVENTS = DATA_DIR / "events.jsonl"

def load_events():
    if not EVENTS.exists():
        return []
    out = []
    with EVENTS.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out

def build_energy_time_ledger(tolerance=1e-6):
    events = load_events()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    total_in = total_useful = total_loss = total_store = 0.0
    for e in events:
        jin = float(e.get("input_energy_J", 0.0))
        juse = float(e.get("useful_output_J", 0.0))
        jloss = float(e.get("loss_energy_J", 0.0))
        jstore = float(e.get("stored_energy_delta_J", 0.0))
        c = jin - juse - jloss - jstore
        rows.append({
            "event_id": e.get("event_id"),
            "timestamp_utc": e.get("timestamp_utc"),
            "node_id": e.get("node_id"),
            "actor_id": e.get("actor_id"),
            "input_energy_J": jin,
            "useful_output_J": juse,
            "loss_energy_J": jloss,
            "stored_energy_delta_J": jstore,
            "residual_C_J": c,
            "confidence": e.get("confidence"),
            "evidence_reference": e.get("evidence_reference"),
        })
        total_in += jin
        total_useful += juse
        total_loss += jloss
        total_store += jstore

    out_csv = DATA_DIR / "energy_by_actor.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [
            "event_id","timestamp_utc","node_id","actor_id","input_energy_J","useful_output_J",
            "loss_energy_J","stored_energy_delta_J","residual_C_J","confidence","evidence_reference"
        ])
        w.writeheader()
        for r in rows:
            w.writerow(r)

    c_total = total_in - total_useful - total_loss - total_store
    eta = (total_useful / total_in) if total_in > 0 else 0.0

    md = REPORTS_DIR / "ENERGY_TIME_LEDGER.md"
    with md.open("w", encoding="utf-8") as f:
        f.write("# ENERGY_TIME_LEDGER\n\n")
        f.write(f"- events: {len(events)}\n")
        f.write(f"- total_input_J: {total_in}\n")
        f.write(f"- total_useful_J: {total_useful}\n")
        f.write(f"- total_loss_J: {total_loss}\n")
        f.write(f"- total_stored_delta_J: {total_store}\n")
        f.write(f"- conservation_residual_C_J: {c_total}\n")
        f.write(f"- eta_total: {eta}\n")
        f.write(f"- within_tolerance: {abs(c_total) <= tolerance}\n")
