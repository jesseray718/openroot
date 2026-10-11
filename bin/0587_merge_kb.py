#!/data/data/com.termux/files/usr/bin/python3
"""Merge postulate fragment into live postulates.json by id.
Existing ids win unless FORCE_OVERWRITE=1.
Always writes synergy_mult into engine_state.
"""
from __future__ import annotations

import json
import os
import shutil
import time
from pathlib import Path

HOME = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
OPENROOT = Path(os.environ.get("OPENROOT", "/sdcard/openroot"))
KB = OPENROOT / "agape_kb"
LIVE = KB / "postulates.json"
FRAG = KB / "postulates.merge.json"
STATE = KB / "engine_state.json"
BRIDGE = OPENROOT / "context_bridge" / "axiom_merge_context.json"
FORCE = os.environ.get("FORCE_OVERWRITE", "0") == "1"


def load(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(data):
    if isinstance(data, list):
        return {"version": "unknown", "postulates": data}
    if isinstance(data, dict):
        if "postulates" not in data:
            data = dict(data)
            data["postulates"] = []
        return data
    return {"version": "unknown", "postulates": []}


def main() -> int:
    KB.mkdir(parents=True, exist_ok=True)
    live = normalize(load(LIVE, {"version": "init", "postulates": []}))
    frag = normalize(load(FRAG, {"postulates": []}))
    by_id = {}
    order = []
    for p in live.get("postulates", []):
        if not isinstance(p, dict) or "id" not in p:
            continue
        by_id[p["id"]] = p
        order.append(p["id"])
    added, skipped, replaced = [], [], []
    for p in frag.get("postulates", []):
        if not isinstance(p, dict) or "id" not in p:
            continue
        i = p["id"]
        if i in by_id:
            if FORCE:
                by_id[i] = p
                replaced.append(i)
            else:
                skipped.append(i)
        else:
            by_id[i] = p
            order.append(i)
            added.append(i)
    out = {
        "version": "2026-08-26-merge",
        "updated_unix": time.time(),
        "postulates": [by_id[i] for i in order],
    }
    if LIVE.exists():
        bak = LIVE.with_suffix(".json.bak-" + time.strftime("%Y%m%d-%H%M%S"))
        shutil.copy2(LIVE, bak)
        bak_name = str(bak)
    else:
        bak_name = None
    LIVE.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    state = load(STATE, {})
    if not isinstance(state, dict):
        state = {}
    state["last_axiom_merge_unix"] = time.time()
    state["postulate_count"] = len(out["postulates"])
    state["synergy_mult"] = 1.0
    state["R"] = 1.0
    STATE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    BRIDGE.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "event": "axiom_merge",
        "unix": time.time(),
        "live": str(LIVE),
        "backup": bak_name,
        "added": added,
        "skipped_existing": skipped,
        "replaced": replaced,
        "count": len(out["postulates"]),
        "R": 1.0,
        "N": max(len(out["postulates"]), 1),
        "synergy_mult": 1.0,
        "note": "Existing ids kept. FORCE_OVERWRITE=1 to replace.",
    }
    BRIDGE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
