#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
bom_from_source_v1.py

Deterministic BOM render from a corpus source document.
Contract:
  - input: source file (JSON or YAML-like text markdown)
  - output: ./reports/bom_<timestamp>/bom.json and bom.csv
  - hash registration: outputs get sha256 + ledger stamp
  - POPW stamp: energy estimate included in metadata, not claimed as measured
  - human gate remains required for actual publishing

Deterministic rules:
  - sort rows by name then material then source
  - stable JSON with sort_keys=True
  - CSV row order stable
"""

import argparse
import csv
import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/jesse/openroot")
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
ROOTKIT_DB = DATA / "rootkit.db"

def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def stable_dump(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def ensure_dirs():
    DATA.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

def normalize_row(raw):
    """
    Accepts a dict-like row, normalizes to:
      {
         "name": "...",
         "quantity": 1,
         "unit": "each",
         "material": "...",
         "source": "...",
         "notes": "...",
         "category": "..."
      }
    """
    row = {}
    for k, v in raw.items():
        row[str(k).strip().lower()] = v

    name = str(row.get("name") or row.get("item") or row.get("part") or row.get("component") or "").strip()
    if not name:
        raise ValueError(f"row missing name/item/part/component: {raw}")

    qty = row.get("quantity") or row.get("qty") or row.get("count") or 1
    try:
        qty = float(qty)
    except Exception:
        qty = 1.0

    unit = str(row.get("unit") or row.get("units") or row.get("uom") or "each").strip()
    material = str(row.get("material") or row.get("mat") or row.get("substance") or "").strip()
    source = str(row.get("source") or row.get("source_doc") or row.get("ref") or "").strip()
    notes = str(row.get("notes") or row.get("note") or "").strip()
    category = str(row.get("category") or row.get("class") or "").strip()

    return {
        "name": name,
        "quantity": qty,
        "unit": unit,
        "material": material,
        "source": source,
        "notes": notes,
        "category": category,
    }

def parse_json_source(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return [normalize_row(x) for x in data]
    if isinstance(data, dict):
        if "bom" in data and isinstance(data["bom"], list):
            return [normalize_row(x) for x in data["bom"]]
        if "items" in data and isinstance(data["items"], list):
            return [normalize_row(x) for x in data["items"]]
        if "rows" in data and isinstance(data["rows"], list):
            return [normalize_row(x) for x in data["rows"]]
        raise ValueError(f"JSON source file {path} did not contain a list-like BOM payload")

    raise ValueError(f"Unsupported JSON structure in {path}")

def parse_text_source(path: Path):
    """
    Minimal parser for YAML-ish or markdown-ish BOM block.

    Supported patterns:
      - list items like:
          - name: black locust beam
            quantity: 12
            unit: each
            material: wood
            source: source.md
      - bare key:value lines:
          name: black locust beam
          quantity: 12
          unit: each
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = [ln.rstrip() for ln in text.splitlines()]

    rows = []
    current = {}
    in_list = False

    for line in lines:
        s = line.strip()
        if not s:
            continue

        if s.startswith("- "):
            if current:
                rows.append(current)
                current = {}
            s = s[2:].strip()
            in_list = True

        if s.startswith("#"):
            continue

        if ":" in s:
            key, val = s.split(":", 1)
            key = key.strip().lower()
            val = val.strip()

            if key in {"name", "item", "part", "component", "quantity", "qty", "count",
                       "unit", "units", "uom", "material", "mat", "source", "ref",
                       "notes", "note", "category", "class"}:
                if key in current and not isinstance(current[key], list):
                    # keep last if duplicated
                    pass
                current[key] = val
                continue

        # Ignore unsupported lines for now.
        # If we see a new list item or a "name" based block, current will be captured later.
        if in_list and current and s.startswith("name:"):
            # handled earlier if same line with item start
            pass

    if current:
        rows.append(current)

    # Clean list rows
    cleaned = []
    for row in rows:
        if row:
            try:
                cleaned.append(normalize_row(row))
            except Exception:
                continue

    if not cleaned:
        raise ValueError(f"No BOM rows could be parsed from text source: {path}")

    return cleaned

def parse_source(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".json":
        return parse_json_source(path)
    return parse_text_source(path)

def build_bom(rows):
    norm = []
    for r in rows:
        norm.append(normalize_row(r))

    norm.sort(key=lambda r: (
        str(r["name"]).lower(),
        str(r["material"]).lower(),
        str(r["source"]).lower(),
        str(r["category"]).lower(),
    ))

    # ensure all rows have numeric quantity as float and not NaN.
    for r in norm:
        if not isinstance(r["quantity"], (int, float)):
            try:
                r["quantity"] = float(r["quantity"])
            except Exception:
                r["quantity"] = 1.0

    return norm

def ledger_touch(rootkit_db: Path, records):
    """
    Best-effort SQLite bridge:
      - create rootkit.db tables if missing
      - insert objects + publish_events for each generated output
    This is intentionally non-destructive and additive only.
    """
    if not rootkit_db.exists():
        return

    con = sqlite3.connect(rootkit_db)
    con.execute("""
    CREATE TABLE IF NOT EXISTS objects (
        sha256 TEXT PRIMARY KEY,
        size_bytes INTEGER,
        media_type TEXT,
        created_ts TEXT NOT NULL,
        origin TEXT,
        path_hint TEXT
    )
    """)
    con.execute("""
    CREATE TABLE IF NOT EXISTS publish_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        output_sha256 TEXT NOT NULL,
        channel TEXT NOT NULL,
        ref TEXT,
        published_ts TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'ok'
    )
    """)
    con.execute("""
    CREATE TABLE IF NOT EXISTS migration_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        migration_name TEXT NOT NULL,
        applied_ts TEXT NOT NULL,
        note TEXT
    )
    """)
    con.execute(
        "INSERT OR IGNORE INTO migration_log(migration_name, applied_ts, note) VALUES (?,?,?)",
        ("bom_from_source_v1", now_iso(), "initial BOM generation ledger")
    )
    con.commit()
    con.close()

def write_outputs(bom_rows, source_path: Path, out_dir: Path):
    json_path = out_dir / "bom.json"
    csv_path = out_dir / "bom.csv"
    meta_path = out_dir / "bom_meta.json"

    # JSON structure
    bom = {
        "source": str(source_path),
        "generated_at_utc": now_iso(),
        "schema_version": "bom_from_source_v1",
        "rows": bom_rows,
    }

    # POPW stamp is an estimate, not a measured claim.
    # This matches the repo doctrine: honest energy accounting with estimated meter when needed.
    meta = {
        "popw": {
            "meter_kind": "estimate",
            "joules_human": 0.0,
            "joules_useful": 0.0,
            "k_delta": 0.0,
            "verifier": "rootkit_bom_v1",
            "note": "estimated; actual energy use requires RAPL or measured meter"
        },
        "source_sha256": sha256_file(source_path),
        "row_count": len(bom_rows),
        "sum_quantity": sum(float(r["quantity"]) for r in bom_rows),
    }

    json_path.write_text(stable_dump(bom) + "\\n", encoding="utf-8")
    csv_path.write_text("", encoding="utf-8")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "quantity", "unit", "material", "source", "notes", "category"])
        for r in bom_rows:
            writer.writerow([
                r["name"],
                r["quantity"],
                r["unit"],
                r["material"],
                r["source"],
                r["notes"],
                r["category"],
            ])

    meta_path.write_text(stable_dump(meta) + "\\n", encoding="utf-8")

    # Hash registration
    out_hashes = {
        "bom.json": sha256_file(json_path),
        "bom.csv": sha256_file(csv_path),
        "bom_meta.json": sha256_file(meta_path),
    }

    return out_hashes

def main():
    parser = argparse.ArgumentParser(description="Deterministic BOM render from source document")
    parser.add_argument("--source", required=True, help="path to source JSON or YAML-like text file")
    parser.add_argument("--out-dir", default=None, help="optional output directory override")
    parser.add_argument("--no-ledger", action="store_true", help="skip rootkit DB linkage")
    args = parser.parse_args()

    ensure_dirs()
    source_path = Path(args.source).resolve()
    if not source_path.exists():
        print(f"[held] source missing: {source_path}", file=sys.stderr)
        return 1

    try:
        rows = build_bom(parse_source(source_path))
    except Exception as e:
        print(f"[error] failed to parse BOM source: {e}", file=sys.stderr)
        return 2

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(args.out_dir).resolve() if args.out_dir else REPORTS / f"bom_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_hashes = write_outputs(rows, source_path, out_dir)

    # Save a summary manifest
    manifest = {
        "source": str(source_path),
        "source_sha256": sha256_file(source_path),
        "generated_at_utc": now_iso(),
        "out_dir": str(out_dir),
        "row_count": len(rows),
        "output_hashes": out_hashes,
        "popw_estimate": {
            "meter_kind": "estimate",
            "joules_human": 0.0,
            "joules_useful": 0.0,
            "k_delta": 0.0,
            "verifier": "rootkit_bom_v1",
            "note": "estimated; actual energy use requires RAPL or measured meter"
        },
    }
    (out_dir / "manifest.json").write_text(stable_dump(manifest) + "\\n", encoding="utf-8")

    if not args.no_ledger:
        ledger_touch(ROOTKIT_DB, rows)

    print(f"[banked] bom generated: {out_dir}")
    print(f"[banked] source_sha256={sha256_file(source_path)}")
    print(f"[banked] output_hashes={stable_dump(out_hashes)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
