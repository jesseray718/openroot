import json
from pathlib import Path
import csv
import hashlib

DATA_DIR = Path("/sdcard/openroot/data")
REPORTS_DIR = Path("/sdcard/openroot/reports")
EVENTS = DATA_DIR / "events.jsonl"

def load_events():
    if not EVENTS.exists():
        return []
    out = []
    prev_hash = None
    with EVENTS.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            event = json.loads(line)

            # Validate hash chain
            hash_previous = event.get("hash_previous_event")
            hash_current = event.get("hash_current_event")

            # Check that previous hash matches the chain
            if prev_hash is not None and hash_previous != prev_hash:
                raise ValueError(f"Hash chain broken: expected hash_previous_event={prev_hash}, got {hash_previous}")

            # Recompute current hash to verify integrity
            tmp = dict(event)
            tmp["hash_current_event"] = ""
            payload = json.dumps(tmp, sort_keys=True, separators=(",", ":")).encode("utf-8")
            computed_hash = hashlib.sha256(payload).hexdigest()

            if computed_hash != hash_current:
                raise ValueError(f"Event hash mismatch: expected {hash_current}, computed {computed_hash}")

            out.append(event)
            prev_hash = hash_current
    return out

def build_energy_time_ledger(tolerance=1e-6):
    events = load_events()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Aggregate by actor_id
    actor_data = {}
    total_in = total_useful = total_loss = total_store = 0.0
    for e in events:
        jin = float(e.get("input_energy_J", 0.0))
        juse = float(e.get("useful_output_J", 0.0))
        jloss = float(e.get("loss_energy_J", 0.0))
        jstore = float(e.get("stored_energy_delta_J", 0.0))

        actor_id = e.get("actor_id")
        if actor_id not in actor_data:
            actor_data[actor_id] = {
                "actor_id": actor_id,
                "node_id": e.get("node_id"),
                "input_energy_J": 0.0,
                "useful_output_J": 0.0,
                "loss_energy_J": 0.0,
                "stored_energy_delta_J": 0.0,
                "confidence": e.get("confidence"),
                "evidence_reference": e.get("evidence_reference"),
            }

        actor_data[actor_id]["input_energy_J"] += jin
        actor_data[actor_id]["useful_output_J"] += juse
        actor_data[actor_id]["loss_energy_J"] += jloss
        actor_data[actor_id]["stored_energy_delta_J"] += jstore

        total_in += jin
        total_useful += juse
        total_loss += jloss
        total_store += jstore

    rows = []
    for actor_id, data in actor_data.items():
        c = data["input_energy_J"] - data["useful_output_J"] - data["loss_energy_J"] - data["stored_energy_delta_J"]
        rows.append({
            "actor_id": data["actor_id"],
            "node_id": data["node_id"],
            "input_energy_J": data["input_energy_J"],
            "useful_output_J": data["useful_output_J"],
            "loss_energy_J": data["loss_energy_J"],
            "stored_energy_delta_J": data["stored_energy_delta_J"],
            "residual_C_J": c,
            "confidence": data["confidence"],
            "evidence_reference": data["evidence_reference"],
        })

    out_csv = DATA_DIR / "energy_by_actor.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "actor_id","node_id","input_energy_J","useful_output_J",
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
