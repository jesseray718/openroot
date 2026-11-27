#!/usr/bin/env python3
"""Check tracked JSONL hash chains without changing them."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def check_records(records):
    if not records:
        return "empty chain"
    first = records[0]
    key = "previous_hash" if "previous_hash" in first else "prev" if "prev" in first else None
    if key is None:
        return "missing link field"
    previous = first[key]
    if previous not in (None, "GENESIS", "0" * 64):
        return "unsupported genesis marker"
    spaced = previous == "GENESIS"
    if spaced and "block_id" not in first:
        return "unsupported GENESIS format"
    for index, record in enumerate(records):
        if key not in record or record[key] != previous:
            return f"broken link at row {index + 1}"
        if "seq" in record and record["seq"] != index + 1:
            return f"sequence mismatch at row {index + 1}"
        if "block_id" in record and record["block_id"] != index:
            return f"block ID mismatch at row {index + 1}"
        core = {name: value for name, value in record.items() if name != "hash"}
        options = {"sort_keys": True}
        if not spaced:
            options["separators"] = (",", ":")
        digest = hashlib.sha256(json.dumps(core, **options).encode()).hexdigest()
        if record.get("hash") != digest:
            return f"hash mismatch at row {index + 1}"
        previous = digest
    return None


def main():
    paths = subprocess.check_output(
        ["git", "ls-files", "-z", "--", "*.jsonl"], cwd=ROOT
    ).split(b"\0")
    failures = 0
    checked = 0
    for raw_path in filter(None, paths):
        path = ROOT / Path(raw_path.decode("utf-8", errors="surrogateescape"))
        if path.is_symlink():
            print(f"[error] JSONL symlink requires review: {path.relative_to(ROOT)}", file=sys.stderr)
            failures += 1
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as exc:
            print(f"[error] cannot read {path.relative_to(ROOT)}: {exc}", file=sys.stderr)
            failures += 1
            continue
        records = []
        bad = None
        for index, line in enumerate(lines, 1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                bad = index
                break
            if not isinstance(record, dict):
                bad = index
                break
            records.append(record)
        if bad:
            print(f"[error] cannot classify {path.relative_to(ROOT)}: invalid row {bad}", file=sys.stderr)
            failures += 1
            continue
        if not any("previous_hash" in record or "prev" in record for record in records):
            continue
        error = check_records(records)
        if error:
            print(f"[error] {path.relative_to(ROOT)}: {error}", file=sys.stderr)
            failures += 1
        else:
            checked += 1
            print(f"[ok] {path.relative_to(ROOT)}: {len(records)} entries")
    if not checked:
        print("[error] no supported tracked JSONL chains checked", file=sys.stderr)
        failures += 1
    print(f"Checked {checked} tracked JSONL chains")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
