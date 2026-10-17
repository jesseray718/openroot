#!/usr/bin/env python3
"""Convert the three-line lesson format into TSV; refuse output overwrite."""
import argparse
import csv
import io
import re
from pathlib import Path

def transform(text):
    rows = []
    seen = set()
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.splitlines()
        if len(lines) != 3:
            raise ValueError("Each lesson must contain exactly three lines.")
        match = re.fullmatch(r"(L[0-9]{2,})\. (.+)", lines[0])
        if not match:
            raise ValueError("Invalid lesson heading.")
        ident, lesson = match.groups()
        if ident in seen:
            raise ValueError("Duplicate lesson ID.")
        if not lines[1].startswith("Evidence: "):
            raise ValueError("Missing Evidence field.")
        if not lines[2].startswith("Rule: "):
            raise ValueError("Missing Rule field.")
        evidence = lines[1][10:]
        rule = lines[2][6:]
        if not evidence.strip() or not rule.strip():
            raise ValueError("Empty evidence or rule.")
        seen.add(ident)
        rows.append((ident, lesson, evidence, rule))
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
    writer.writerow(("id", "lesson", "evidence", "rule"))
    writer.writerows(rows)
    return stream.getvalue()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = transform(args.input.read_text(encoding="utf-8"))
    with args.output.open("x", encoding="utf-8", newline="") as handle:
        handle.write(result)

if __name__ == "__main__":
    main()
