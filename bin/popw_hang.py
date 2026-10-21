#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations
import argparse, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--work", required=True)
ap.add_argument("--joules", type=float, default=None)
ap.add_argument("--photo", default=None)
ap.add_argument("--mass-kg", type=float, default=None)
args = ap.parse_args()

out = Path(args.out)
if not out.is_absolute():
    raise SystemExit("REFUSE: --out must be absolute")
if args.photo is None and args.mass_kg is None:
    raise SystemExit("REFUSE: N09 hang needs --photo or --mass-kg")

photo_hash = None
if args.photo:
    pp = Path(args.photo)
    if not pp.is_absolute() or not pp.is_file():
        raise SystemExit("REFUSE: --photo must be an existing absolute file")
    photo_hash = sha256_file(pp)

row = {
    "ts": datetime.now(timezone.utc).isoformat(),
    "schema": "POPW-HANG-1",
    "n": ["N08", "N09"],
    "work": args.work,
    "human_joules": args.joules,
    "photo": args.photo,
    "photo_sha256": photo_hash,
    "mass_kg": args.mass_kg,
    "acre": "REFUSED_UNTIL_HANG_CONFIRMED",
    "chain": "local-jsonl-cas",
    "not": "solana",
}
out.parent.mkdir(parents=True, exist_ok=True)
with out.open("a", encoding="utf-8") as f:
    f.write(json.dumps(row, separators=(",", ":")) + "\n")
print(json.dumps({"wrote": str(out), "photo_sha256": photo_hash}))
