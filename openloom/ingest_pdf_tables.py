#!/usr/bin/env python3
"""Extract normalized tables from a PDF for OpenLoom ingestion."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import pdfplumber


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_cell(value):
    if value is None:
        return ""
    return " ".join(str(value).split())


def extract_tables(pdf_path: Path, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            for table_number, raw_table in enumerate(page.extract_tables(), start=1):
                if not raw_table or len(raw_table) < 2:
                    continue

                rows = [[normalize_cell(cell) for cell in row] for row in raw_table]
                header = rows[0]
                body = rows[1:]

                if not any(header) or not body:
                    continue

                table_id = f"lubuntu_manual_p{page_number:03d}_t{table_number:02d}"
                csv_path = out_dir / f"{table_id}.csv"
                jsonl_path = out_dir / f"{table_id}.jsonl"

                with csv_path.open("w", newline="", encoding="utf-8") as handle:
                    writer = csv.writer(handle)
                    writer.writerow(header)
                    writer.writerows(body)

                with jsonl_path.open("w", encoding="utf-8") as handle:
                    for row in body:
                        record = dict(zip(header, row))
                        record["_table_id"] = table_id
                        record["_pdf_page"] = page_number
                        handle.write(json.dumps(record, ensure_ascii=False) + "\n")

                manifest.append({
                    "table_id": table_id,
                    "pdf_page": page_number,
                    "rows": len(body),
                    "columns": len(header),
                    "csv": str(csv_path),
                    "jsonl": str(jsonl_path),
                    "csv_sha256": sha256(csv_path),
                    "jsonl_sha256": sha256(jsonl_path),
                })

    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    manifest = extract_tables(args.pdf.resolve(), args.out.resolve())
    manifest_path = args.out / "tables_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "status": "EXTRACTED",
        "pdf": str(args.pdf.resolve()),
        "pdf_sha256": sha256(args.pdf.resolve()),
        "tables": len(manifest),
        "manifest": str(manifest_path),
    }, indent=2))


if __name__ == "__main__":
    main()
