#!/usr/bin/env python3
# [canary] paste intact
"""queue_directive.py — write TASK.md from one model_findings row. Does not execute."""

import sqlite3
import sys

LEDGER = "/home/jesse/.local/share/openroot/ledger.db"
TASK = "/home/jesse/openroot/TASK.md"


def main() -> int:
    if len(sys.argv) != 2:
        sys.stderr.write("usage: queue_directive.py FINDING_ID\n")
        return 2
    try:
        finding_id = int(sys.argv[1])
    except ValueError:
        sys.stderr.write("usage: queue_directive.py FINDING_ID\n")
        return 2

    con = sqlite3.connect(LEDGER)
    con.row_factory = sqlite3.Row
    row = con.execute(
        "SELECT id, snapshot_id, directive, status FROM model_findings WHERE id = ?",
        (finding_id,),
    ).fetchone()
    con.close()
    if row is None:
        sys.stderr.write(f"finding {finding_id} not found\n")
        return 3

    raw = row["directive"] if row["directive"] is not None else ""
    parts = raw.split("|")
    # DIRECTIVE|absolute-path-or-command|action-description
    target = parts[1].strip() if len(parts) > 1 else ""
    action = "|".join(parts[2:]).strip() if len(parts) > 2 else ""

    body = (
        f"# Task {finding_id}\n"
        f"## Goal\n"
        f"{action}\n"
        f"## Target\n"
        f"{target}\n"
        f"## Constraints: Change only what this directive specifies. Nothing else.\n"
    )
    with open(TASK, "w", encoding="utf-8") as fh:
        fh.write(body)
    print(f"[queued] TASK.md <- finding {finding_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
