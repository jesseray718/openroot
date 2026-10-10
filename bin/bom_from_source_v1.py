#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
bom_from_source_v1.py

Deterministic BOM render from a source document.

Rules:
  - bom.json is canonical and stable
  - generated_at_utc lives only in manifest.json
  - output files are hash-registered
  - energy is recorded as an estimate when no physical meter exists
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
        raise ValueError(f"JSON source file {path} did not contain a BOM list")
    raise ValueError(f"Unsupported JSON structure in {path}")

def parse_text_source(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = [ln.rstrip() for ln in text.splitlines()]
    rows = []
    current = {}
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("- "):
            if current:
                rows.append(current)
            current = {}
            s = s[2:].strip()
        if ":" not in s:
            continue
        key, val = s.split(":", 1)
        key = key.strip().lower()
        val = val.strip()
        if key in {"name", "item", "part", "component", "quantity", "qty", "count",
                   "unit", "units", "uom", "material", "mat", "source", "ref",
                   "notes", "note", "category", "class"}:
            current[key] = val
    if current:
        rows.append(current)

    cleaned = []
    for row in rows:
        if row:
            try:
                cleaned.append(normalize_row(row))
            except Exception:
                pass
    if not cleaned:
        raise ValueError(f"No BOM rows could be parsed from text source: {path}")
    return cleaned

def parse_source(path: Path):
    if path.suffix.lower() == ".json":
        return parse_json_source(path)
    return parse_text_source(path)

def build_bom(rows):
    norm = [normalize_row(r) for r in rows]
    norm.sort(key=lambda r: (
        str(r["name"]).lower(),
        str(r["material"]).lower(),
        str(r["source"]).lower(),
        str(r["category"]).lower(),
    ))
    for r in norm:
        try:
            r["quantity"] = float(r["quantity"])
        except Exception:
            r["quantity"] = 1.0
    return norm

def write_outputs(bom_rows, source_path: Path, out_dir: Path):
    bom_path = out_dir / "bom.json"
    csv_path = out_dir / "bom.csv"
    meta_path = out_dir / "bom_meta.json"
    manifest_path = out_dir / "manifest.json"

    bom = {
        "source": str(source_path),
        "schema_version": "bom_from_source_v1",
        "rows": bom_rows,
    }
    bom_path.write_text(stable_dump(bom) + "\\n", encoding="utf-8")

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "quantity", "unit", "material", "source", "notes", "category"])
        for r in bom_rows:
            writer.writerow([r["name"], r["quantity"], r["unit"], r["material"], r["source"], r["notes"], r["category"]])

    meta = {
        "source_sha256": sha256_file(source_path),
        "row_count": len(bom_rows),
        "sum_quantity": sum(float(r["quantity"]) for r in bom_rows),
        "popw_estimate": {
            "meter_kind": "estimate",
            "joules_human": 0.0,
            "joules_useful": 0.0,
            "k_delta": 0.0,
            "verifier": "rootkit_bom_v1",
            "note": "estimated; actual energy use requires RAPL or measured meter"
        }
    }
    meta_path.write_text(stable_dump(meta) + "\\n", encoding="utf-8")

    manifest = {
        "source": str(source_path),
        "source_sha256": meta["source_sha256"],
        "generated_at_utc": now_iso(),
        "schema_version": "bom_from_source_v1",
        "row_count": len(bom_rows),
        "output_hashes": {
            "bom.json": sha256_file(bom_path),
            "bom.csv": sha256_file(csv_path),
            "bom_meta.json": sha256_file(meta_path),
        },
        "popw_estimate": meta["popw_estimate"]
    }
    manifest_path.write_text(stable_dump(manifest) + "\\n", encoding="utf-8")

    return {
        "bom.json": sha256_file(bom_path),
        "bom.csv": sha256_file(csv_path),
        "bom_meta.json": sha256_file(meta_path),
        "manifest.json": sha256_file(manifest_path),
    }

def ledger_touch(rootkit_db: Path, out_hashes, src_hash):
    if not rootkit_db.exists():
        return
    con = sqlite3.connect(rootkit_db)
    con.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
      job_id TEXT PRIMARY KEY,
      input_sha256 TEXT,
      output_sha256 TEXT,
      spec_sha256 TEXT,
      status TEXT NOT NULL DEFAULT 'pending',
      started_ts TEXT,
      ended_ts TEXT,
      notes TEXT
    )
    """)
    con.execute("""
    CREATE TABLE IF NOT EXISTS attestations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      job_id TEXT NOT NULL,
      meter_kind TEXT NOT NULL,
      joules_human REAL,
      joules_useful REAL,
      k_delta REAL,
      measured_ts TEXT NOT NULL,
      verifier TEXT,
      note TEXT
    )
    """)
    con.execute("""
    INSERT OR IGNORE INTO jobs(job_id, input_sha256, output_sha256, spec_sha256, status, started_ts, ended_ts, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "bom_render_" + sha256_file(rootkit_db)[:12],
        src_hash,
        out_hashes["bom.json"],
        src_hash,
        "recorded",
        now_iso(),
        now_iso(),
        "deterministic BOM render"
    ))
    con.execute("""
    INSERT OR IGNORE INTO attestations(job_id, meter_kind, joules_human, joules_useful, k_delta, measured_ts, verifier, note)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "bom_render_" + sha256_file(rootkit_db)[:12],
        "estimate",
        0.0,
        0.0,
        0.0,
        now_iso(),
        "rootkit_bom_v1",
        "BOM render: estimate only"
    ))
    con.commit()
    con.close()

def main():
    parser = argparse.ArgumentParser(description="Deterministic BOM render from source document")
    parser.add_argument("--source", required=True, help="path to BOM source file")
    parser.add_argument("--out-dir", default=None, help="output dir override")
    parser.add_argument("--no-ledger", action="store_true")
    args = parser.parse_args()

    ensure_dirs()
    src = Path(args.source).resolve()
    if not src.exists():
        print(f"[held] source missing: {src}", file=sys.stderr)
        return 1

    try:
        rows = build_bom(parse_source(src))
    except Exception as e:
        print(f"[ERROR] failed to parse BOM source: {e}", file=sys.stderr)
        return 2

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(args.out_dir).resolve() if args.out_dir else REPORTS / f"bom_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    hashes = write_outputs(rows, src, out_dir)

    if not args.no_ledger:
        ledger_touch(ROOTKIT_DB, hashes, sha256_file(src))

    print(f"[banked] bom generated: {out_dir}")
    print(f"[banked] source_sha256={sha256_file(src)}")
    print(f"[banked] output_hashes={stable_dump(hashes)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
