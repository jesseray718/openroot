#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGNS = ROOT / "designs"

REQUIRED = [
    "README.md",
    "STATUS.md",
    "metadata.yaml",
    "LICENSE.md",
    "bom/BOM.csv",
    "bom/BOM.md",
    "docs/problem.md",
    "docs/safety.md",
    "docs/build-instructions.md",
    "docs/test-protocol.md",
    "docs/results.md",
    "docs/replication-notes.md",
    "calculations/assumptions.md",
    "calculations/formulas.md",
    "release/REPRODUCE.md",
]

BOM_COLUMNS = {
    "reference",
    "part_name",
    "description",
    "quantity",
    "unit",
    "specification",
    "material_or_grade",
    "manufacturer_part_number",
    "source_or_make",
    "cost_estimate_usd",
    "currency",
    "alternatives",
    "design_file",
    "criticality",
    "notes",
}

def fail(message):
    print(f"ERROR: {message}", file=sys.stderr)

def main():
    if not DESIGNS.exists():
        print("No designs directory; template-only state is valid.")
        return 0

    packets = sorted(
        item for item in DESIGNS.iterdir()
        if item.is_dir() and (item / "metadata.yaml").is_file()
    )

    if not packets:
        print("No design packets yet; template-only state is valid.")
        return 0

    errors = []

    for packet in packets:
        for relative in REQUIRED:
            if not (packet / relative).is_file():
                errors.append(f"{packet.relative_to(ROOT)} missing {relative}")

        bom = packet / "bom" / "BOM.csv"
        if bom.is_file():
            with bom.open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                missing = BOM_COLUMNS - set(reader.fieldnames or [])
                if missing:
                    errors.append(
                        f"{bom.relative_to(ROOT)} missing columns: {', '.join(sorted(missing))}"
                    )

    if errors:
        for item in errors:
            fail(item)
        return 1

    print(f"Validated {len(packets)} design packet(s).")
    return 0

raise SystemExit(main())
