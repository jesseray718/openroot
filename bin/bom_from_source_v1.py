#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
bom_from_source_v1.py - deterministic BOM render.

bom.json, bom.csv, bom_meta.json depend only on the source content.
Timestamps live only in manifest.json. Ledger/chain recording is done
by the rootkit dispatcher, not here.
Exit: 0 banked, 1 held (source missing), 2 error.
"""
import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/jesse/openroot")
REPORTS = ROOT / "reports"
NL = chr(10)

KEYS = {"name", "item", "part", "component", "quantity", "qty", "count",
        "unit", "units", "uom", "material", "mat", "source", "ref",
        "notes", "note", "category", "class"}


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def stable_dump(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def normalize_row(raw):
    row = {str(k).strip().lower(): v for k, v in raw.items()}
    name = str(row.get("name") or row.get("item") or row.get("part")
               or row.get("component") or "").strip()
    if not name:
        raise ValueError("row missing name/item/part/component: %r" % (raw,))
    try:
        qty = float(row.get("quantity") or row.get("qty") or row.get("count") or 1)
    except (TypeError, ValueError):
        qty = 1.0
    return {
        "name": name,
        "quantity": qty,
        "unit": str(row.get("unit") or row.get("units") or row.get("uom") or "each").strip(),
        "material": str(row.get("material") or row.get("mat") or "").strip(),
        "source": str(row.get("source") or row.get("ref") or "").strip(),
        "notes": str(row.get("notes") or row.get("note") or "").strip(),
        "category": str(row.get("category") or row.get("class") or "").strip(),
    }


def parse_json_source(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        for k in ("bom", "items", "rows"):
            if isinstance(data.get(k), list):
                data = data[k]
                break
        else:
            raise ValueError("JSON has no bom/items/rows list")
    if not isinstance(data, list):
        raise ValueError("unsupported JSON structure")
    return [normalize_row(x) for x in data]


def parse_text_source(path):
    rows, cur = [], {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("- "):
            if cur:
                rows.append(cur)
            cur = {}
            s = s[2:].strip()
        if ":" not in s:
            continue
        k, v = s.split(":", 1)
        k = k.strip().lower()
        if k in KEYS:
            cur[k] = v.strip()
    if cur:
        rows.append(cur)
    out = []
    for r in rows:
        try:
            out.append(normalize_row(r))
        except ValueError:
            pass
    if not out:
        raise ValueError("no BOM rows parsed from text source")
    return out


def build_bom(rows):
    return sorted(rows, key=lambda r: (r["name"].lower(), r["material"].lower(),
                                       r["source"].lower(), r["category"].lower()))


def write_outputs(rows, src, out_dir):
    src_sha = sha256_file(src)
    bom_path = out_dir / "bom.json"
    csv_path = out_dir / "bom.csv"
    meta_path = out_dir / "bom_meta.json"
    man_path = out_dir / "manifest.json"

    bom = {"schema_version": "bom_from_source_v1", "source_sha256": src_sha, "rows": rows}
    bom_path.write_text(stable_dump(bom) + NL, encoding="utf-8")

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", "quantity", "unit", "material", "source", "notes", "category"])
        for r in rows:
            w.writerow([r["name"], r["quantity"], r["unit"], r["material"],
                        r["source"], r["notes"], r["category"]])

    meta = {
        "source_sha256": src_sha,
        "row_count": len(rows),
        "sum_quantity": sum(r["quantity"] for r in rows),
        "popw_estimate": {"meter_kind": "estimate", "joules_human": 0.0,
                          "joules_useful": 0.0, "k_delta": 0.0,
                          "note": "estimate only; no physical meter"},
    }
    meta_path.write_text(stable_dump(meta) + NL, encoding="utf-8")

    hashes = {"bom.json": sha256_file(bom_path),
              "bom.csv": sha256_file(csv_path),
              "bom_meta.json": sha256_file(meta_path)}
    manifest = {"source": str(src), "source_sha256": src_sha,
                "generated_at_utc": now_iso(), "output_hashes": hashes}
    man_path.write_text(stable_dump(manifest) + NL, encoding="utf-8")
    return src_sha, hashes


def main():
    ap = argparse.ArgumentParser(description="deterministic BOM render")
    ap.add_argument("--source", required=True)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--no-ledger", action="store_true", help="accepted, no-op")
    a = ap.parse_args()

    src = Path(a.source).resolve()
    if not src.exists():
        print("[held] source missing: %s" % src, file=sys.stderr)
        return 1
    try:
        src_path = src
        rows = build_bom(parse_json_source(src_path) if src.suffix.lower() == ".json"
                         else parse_text_source(src_path))
    except Exception as e:
        print("[ERROR] failed to parse BOM source: %s" % e, file=sys.stderr)
        return 2

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(a.out_dir).resolve() if a.out_dir else REPORTS / ("bom_" + stamp)
    out_dir.mkdir(parents=True, exist_ok=True)

    src_sha, hashes = write_outputs(rows, src, out_dir)
    print("[banked] bom generated: %s" % out_dir)
    print("[banked] source_sha256=%s" % src_sha)
    print("[banked] output_hashes=%s" % stable_dump(hashes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
