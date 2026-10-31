#!/usr/bin/env python3
"""Idempotent local booking for the OpenRoot e-waste pickup pipeline."""

import argparse
import fcntl
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SLOTS = ROOT / "data" / "ewaste" / "slots.json"
GENESIS_HASH = "0" * 64

def _read_receipts(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid receipt at {path}:{line_number}") from exc
    return records

def _write_slots(path: Path, slots: dict[str, list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(slots, stream, indent=4)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)

def _append_receipt(path: Path, records: list[dict[str, Any]], event_id: str,
                   pickup_date: str, pickup_time: str) -> None:
    previous_hash = records[-1]["hash"] if records else GENESIS_HASH
    record = {
        "block_id": len(records),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "EWASTE_PICKUP_BOOKED",
        "event_id": event_id,
        "pickup_date": pickup_date,
        "pickup_time": pickup_time,
        "previous_hash": previous_hash,
    }
    record["hash"] = hashlib.sha256(
        json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())

def book_slot(
    pickup_date: str,
    pickup_time: str,
    slots_path: Path | str = DEFAULT_SLOTS,
    ledger_path: Path | str | None = None,
) -> bool:
    """Book a slot once; return False when it is unavailable."""
    try:
        if date.fromisoformat(pickup_date).isoformat() != pickup_date:
            raise ValueError
        if datetime.strptime(pickup_time, "%H:%M").time().strftime("%H:%M") != pickup_time:
            raise ValueError
    except ValueError as exc:
        raise ValueError("Use a valid YYYY-MM-DD date and HH:MM time") from exc

    slots_file = Path(slots_path)
    receipts_file = Path(ledger_path) if ledger_path else slots_file.with_name("newton_chain.jsonl")
    lock_file = slots_file.with_name(f".{slots_file.name}.lock")
    event_id = hashlib.sha256(
        f"EWASTE_PICKUP_BOOKED\n{pickup_date}\n{pickup_time}".encode("utf-8")
    ).hexdigest()

    slots_file.parent.mkdir(parents=True, exist_ok=True)
    with lock_file.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        with slots_file.open(encoding="utf-8") as stream:
            slots = json.load(stream)
            if not isinstance(slots, dict):
                raise ValueError("Pickup slots must be a date-to-times JSON object")
            records = _read_receipts(receipts_file)
            already_booked = any(record.get("event_id") == event_id for record in records)

            available = slots.get(pickup_date, [])
            if not already_booked and pickup_time not in available:
                return False
            if not already_booked:
                _append_receipt(receipts_file, records, event_id, pickup_date, pickup_time)

            if pickup_time in available:
                slots[pickup_date] = [slot for slot in available if slot != pickup_time]
                _write_slots(slots_file, slots)
            return True

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("date", help="Pickup date (YYYY-MM-DD)")
    parser.add_argument("time", help="Pickup time (HH:MM)")
    parser.add_argument("--slots", type=Path, default=DEFAULT_SLOTS)
    parser.add_argument("--ledger", type=Path)
    args = parser.parse_args()

    try:
        booked = book_slot(args.date, args.time, args.slots, args.ledger)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"[error] {exc}\n")
    
    if not booked:
        print("[alert] Slot unavailable.")
        return 1
    
    print(f"[logistics] Slot {args.date} {args.time} booked; receipt sealed.")
    
    # THERMODYNAMIC MINT: Record as a 'step' contribution
    try:
        subprocess.run(["python3", "bin/thermo_mint.py", "step", "jesse", "pickup", args.date], check=True)
    except Exception as e:
        print(f"[warning] Thermodynamic mint failed: {e}")
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
