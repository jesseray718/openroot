#!/usr/bin/env python3
"""compost_triage_v2.py - classify unsolved COMPOST keys, propose dispositions, optionally bank them.

Dry-run by default: nothing is written to the ledger unless --solve is given.

  python3 bin/compost_triage_v2.py            # classify, write TSVs to /tmp, print summary
  python3 bin/compost_triage_v2.py --solve    # also bank dispositions for the auto buckets
  python3 bin/compost_triage_v2.py --top 15   # more samples printed per bucket

Auto buckets (provably not mistakes - safe to bank):
  paste_output    terminal output / annotation captured as if it were a command
  paste_python    Python source pasted at the bash prompt (exit 127/2)
  stray_char      one- or two-character line (stray keystroke / broken paste)
  benign_nonzero  known-good command whose nonzero exit is its normal signal

Review bucket (NEVER auto-banked - needs human judgement):
  real_mistake    everything else
"""
from __future__ import annotations

import argparse
import contextlib
import io
import os
import re
import sqlite3
import sys

ROOT = "/home/jesse/openroot"
DB = os.path.join(ROOT, "data", "mistakes.db")
BIN = os.path.join(ROOT, "bin")

DISPOSITIONS = {
    "paste_output": (
        "terminal output or program annotation captured as a command by the hook "
        "(paste noise); not a mistake and not actionable; no corrective action"
    ),
    "paste_python": (
        "Python source line pasted at the bash prompt (exit 127/2 = not a command); "
        "write code to a file or feed it through a python3 heredoc instead of pasting "
        "at the shell prompt; not a mistake; no corrective action"
    ),
    "stray_char": (
        "one- or two-character line executed as a command (stray keystroke or broken "
        "paste); confirm the intended command before pressing enter"
    ),
    "benign_nonzero": (
        "legitimate command whose nonzero exit is its normal signal (no match, nothing "
        "staged, push rejected, checks failing); not a mistake; no corrective action"
    ),
}

AUTO_BUCKETS = tuple(DISPOSITIONS)

BENIGN_HEADS = {
    "grep", "egrep", "fgrep", "rg", "git", "gh", "diff", "cmp", "test", "[",
    "curl", "wget", "scp", "rsync", "ssh", "ps", "pgrep", "cat", "sed", "awk",
    "ls", "find", "make", "pytest", "python", "python3", "pip", "pip3", "npm",
    "cargo", "systemctl", "journalctl", "docker", "tar", "unzip", "sha256sum",
}

# exits a healthy command may legitimately return
BENIGN_EXITS = {1, 2, 130, 141}

PY_STRONG = re.compile(
    r"(^|\s)(def |class |lambda |elif |except|try:|return |yield |import |from |"
    r"assert |self\.|print\(|raise )|->\s*\w|\]\s*:\s*$|\)\s*:\s*$|^\s*@\w+"
)

OUTPUT_MARKERS = re.compile(
    r"^(-rw|drw|lrw|crw|total\s)|"
    r"^(\[|\(|>|\|)+\s*|"
    r"^(Warning:|error:|remote:|Enumerating|Counting|Compressing|Writing|Creating|"
    r"Already |Branch |Switched |Your branch|Nothing to commit|On branch|HEAD |"
    r"\[tablemaker\]|\[gate\]|\[exit=|\[PASS\]|\[COMPOST\])|"
    r"^\s*#|"
    r"^\d+\s+(files?|objects?|insertions?)"
)

ASSIGN_ONLY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=\S*(\s+[A-Za-z_][A-Za-z0-9_]*=\S*)*$")


def dominant_exit(exits: str) -> int:
    vals = []
    for tok in str(exits or "").replace(",", " ").split():
        if tok.lstrip("-").isdigit():
            vals.append(int(tok))
    if not vals:
        return 0
    return max(set(vals), key=vals.count)


def classify(shape: str, exits: str) -> str:
    s = (shape or "").strip()
    dom = dominant_exit(exits)
    if not s:
        return "paste_output"
    if len(s) <= 2:
        return "stray_char"
    if PY_STRONG.search(s):
        return "paste_python"
    if ASSIGN_ONLY.match(s):
        return "paste_output"
    if OUTPUT_MARKERS.match(s):
        return "paste_output"
    head = s.split()[0]
    if head in BENIGN_HEADS and dom in BENIGN_EXITS:
        return "benign_nonzero"
    if dom == 127:
        return "paste_python"
    return "real_mistake"


def fetch_unsolved():
    con = sqlite3.connect(DB)
    try:
        return con.execute(
            "SELECT key, shape, last_cmd, occurrences, exits, first_seen "
            "FROM mistakes WHERE solved=0 ORDER BY occurrences DESC"
        ).fetchall()
    finally:
        con.close()


def solved_count() -> int:
    con = sqlite3.connect(DB)
    try:
        return con.execute("SELECT COUNT(*) FROM mistakes WHERE solved=1").fetchone()[0]
    finally:
        con.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--solve", action="store_true",
                    help="bank dispositions (default: dry run)")
    ap.add_argument("--top", type=int, default=8,
                    help="samples printed per bucket (default 8)")
    args = ap.parse_args()

    rows = fetch_unsolved()
    buckets: dict[str, list] = {}
    for key, shape, last_cmd, occ, exits, first in rows:
        buckets.setdefault(classify(shape, exits), []).append(
            (key, shape, occ, exits, last_cmd)
        )

    print(f"unsolved keys: {len(rows)}")
    for name in sorted(buckets, key=lambda b: -sum(r[2] for r in buckets[b])):
        items = buckets[name]
        total = sum(r[2] for r in items)
        tag = "auto" if name in AUTO_BUCKETS else "REVIEW"
        print(f"\n[{tag}] {name}: {len(items)} keys, {total} occurrences")
        for key, shape, occ, exits, _ in sorted(items, key=lambda r: -r[2])[: args.top]:
            print(f"    {key} x{occ:<4} {shape[:70]}")

    fixes = [(k, DISPOSITIONS[b])
             for b in AUTO_BUCKETS
             for k, _, _, _, _ in buckets.get(b, [])]
    review = list(buckets.get("real_mistake", []))

    with open("/tmp/compost_fixes.tsv", "w") as fh:
        for k, fix in fixes:
            fh.write(f"{k}\t{fix}\n")
    with open("/tmp/compost_review.tsv", "w") as fh:
        for k, s, o, e, lc in review:
            fh.write(f"{k}\t{o}\t{e}\t{s}\t{lc}\n")
    with open("/tmp/compost_triage.tsv", "w") as fh:
        for b in sorted(buckets):
            for k, s, o, e, lc in buckets[b]:
                fh.write(f"{b}\t{k}\t{o}\t{s}\t{lc}\n")

    print(f"\nauto-solvable: {len(fixes)} keys -> /tmp/compost_fixes.tsv")
    print(f"needs review:  {len(review)} keys -> /tmp/compost_review.tsv")
    print("full triage:               -> /tmp/compost_triage.tsv")

    if not args.solve:
        print("\ndry run - nothing banked. re-run with --solve to apply.")
        return

    sys.path.insert(0, BIN)
    import mistake_engine_v1 as me  # noqa: E402

    before = solved_count()
    banked = failed = 0
    for key, fix in fixes:
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                me.solve(key, fix)
            banked += 1
        except SystemExit:
            failed += 1
        except Exception as exc:  # noqa: BLE001
            print(f"  ! {key}: {exc}")
            failed += 1

    after = solved_count()
    print(f"\nbanked {banked} ({failed} failed); solved keys {before} -> {after}")
    print("re-run: python3 bin/mistake_engine_v1.py compost")


if __name__ == "__main__":
    main()

