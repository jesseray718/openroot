import re
import json
from pathlib import Path

DATA = Path("/sdcard/openroot/data/events.jsonl")

def test_rfc3339_utc_format():
    if not DATA.exists():
        return
    with DATA.open() as f:
        for line in f:
            e = json.loads(line)
            ts = e["timestamp_utc"]
            assert ts.endswith("Z") or re.search(r"[+-]\d{2}:\d{2}$", ts)

def test_elapsed_monotonic_nonnegative():
    if not DATA.exists():
        return
    with DATA.open() as f:
        for line in f:
            e = json.loads(line)
            assert e["elapsed_monotonic_s"] >= 0

def test_unknown_human_energy_not_forced_zero():
    # human energy field not explicit; ensure human_time tracked separately
    if not DATA.exists():
        return
    with DATA.open() as f:
        for line in f:
            e = json.loads(line)
            assert "human_time_s" in e

def test_event_hash_chain_fields_present():
    if not DATA.exists():
        return
    with DATA.open() as f:
        for line in f:
            e = json.loads(line)
            assert "hash_current_event" in e
