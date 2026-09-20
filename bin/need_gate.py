#!/usr/bin/env python3
from __future__ import annotations
import json, platform, socket, sys
from datetime import datetime, timezone
from pathlib import Path

NOW = [
    "DONE: canon.py printed 0.0",
    "A15: NightHawk 1:2 cubes + 21-day wet tent",
    "A15/field: H-003 1m2 dT log",
    "field: one paid patch + photo hang",
    "SSH: FTS5 probe — no nomic until FTS5 hits",
]
REJECT = [
    "7B on A15",
    "nomic on A15",
    "syncthing serve on Termux",
    "ACRE without hang",
    "1.34 as MEASURED",
    "2500-4000 psi",
    "xanthan/Dawn as NightHawk gel",
]

def pane():
    home = str(Path.home())
    if home.startswith("/data/data/com.termux"):
        return "A15"
    if home == "/home/jesse":
        return "SSH"
    return "OTHER"

def probe(paths):
    out = []
    for p in paths:
        pp = Path(p)
        out.append({"path": p, "exists": pp.exists()})
    return out

p = pane()
rep = {
    "ts": datetime.now(timezone.utc).isoformat(),
    "pane": p,
    "uid_hint": "expect u0_a357 on this A15",
    "home": str(Path.home()),
    "host": socket.gethostname(),
    "canon_0_0": "CONFIRMED_BY_OPERATOR",
    "service_ratio_1_34": "MODEL",
    "h1_mpa": "OPEN",
    "now": NOW,
    "n14_reject": REJECT,
}
if p == "A15":
    rep["probe"] = probe([
        "/data/data/com.termux/files/home/openroot/canon/src/canon.py",
        "/data/data/com.termux/files/home/openroot/bin/need_gate.py",
        "/data/data/com.termux/files/home/openroot/bin/h003_log.py",
        "/data/data/com.termux/files/home/openroot/bin/popw_hang.py",
        "/data/data/com.termux/files/home/aerocement/aerocement_calc",
        "/storage/emulated/0/openroot/.stfolder",
        "/storage/emulated/0/openroot/outbox",
        "/storage/emulated/0/openroot/outbox/PHONE.md",
        "/storage/emulated/0/openroot/inbox/VALVE.md",
        "/storage/emulated/0/openroot/outbox/cube_day0.jpg",
        "/storage/emulated/0/openroot/outbox/h003.jsonl",
        "/storage/emulated/0/openroot/outbox/popw.jsonl",
    ])
print(json.dumps(rep, indent=2))
print("PANE", p, file=sys.stderr)
print("1.34 MODEL. H1 OPEN. Do not hang a missing photo.", file=sys.stderr)
