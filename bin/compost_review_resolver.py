# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""compost_review_resolver.py - group the REVIEW bucket by cause and propose fix strings.

Input : /tmp/compost_review.tsv        (key, occurrences, exits, shape, last_cmd)
Output: /tmp/compost_review_fixes.tsv  (key, family, proposed fix)   <- edit before applying

  python3 bin/compost_review_resolver.py             # propose + summarise (banks nothing)
  python3 bin/compost_review_resolver.py --show 40   # print more sample rows per family
  python3 bin/compost_review_resolver.py --apply     # bank the edited proposals

--apply banks whatever is in the output TSV, so edit it first. Any row whose fix
column still begins with 'TODO' is skipped, so unclassified keys stay open.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import os
import sqlite3
import sys
from collections import defaultdict

ROOT = "/home/jesse/openroot"
DB = os.path.join(ROOT, "data", "mistakes.db")
BIN = os.path.join(ROOT, "bin")
IN_TSV = "/tmp/compost_review.tsv"
OUT_TSV = "/tmp/compost_review_fixes.tsv"

NET_HEADS = {"ssh", "scp", "sftp", "rsync"}
READ_HEADS = {"head", "tail", "cat", "sed", "grep", "ls", "less", "stat"}


def dom_exit(exits: str) -> int:
    vals = [
        int(t) for t in str(exits or "").replace(",", " ").split()
        if t.lstrip("-").isdigit()
    ]
    return max(set(vals), key=vals.count) if vals else 0


def head_of(shape: str) -> str:
    s = (shape or "").strip()
    return s.split()[0] if s else ""


def propose(shape: str, last_cmd: str, exits: str):
    """Return (family, fix_string) for one review key."""
    s = (shape or "").strip()
    lc = (last_cmd or "").strip()
    d = dom_exit(exits)
    h = head_of(s)

    if d in (254, 255) and h in NET_HEADS:
        return "ssh_transport", (
            f"SSH/SCP transport failure (exit {d}): the connection was refused, reset or "
            "dropped before the remote command ran. Environmental, not a usage error - add "
            "ServerAliveInterval 30 and ServerAliveCountMax 6 to that host's block in "
            "~/.ssh/config, then retry."
        )
    if "not found, did you mean" in s or "not found, did you mean" in lc:
        return "typo_command", (
            "command name mistyped - the shell suggested a near match; a stray character "
            "before the command name is the usual cause. Check spelling or use the suggestion."
        )
    if h == "cd" and d == 1:
        return "cd_missing", (
            "cd target does not exist (exit 1): typo, wrong cwd, or the directory was never "
            "created. Verify with ls before cd, and quote paths containing spaces."
        )
    if h in {"apt", "apt-get", "dpkg"} and d in (100, 1):
        return "apt_failed", (
            f"apt/dpkg returned an error (exit {d}): usually a missing sudo, an unmet "
            "dependency, or a lock held by another process. Re-run with sudo and read the "
            "dpkg error text."
        )
    if h == "git" and d == 128:
        return "git_fatal", (
            "git fatal error (exit 128): check branch divergence, a missing upstream, or a "
            "dirty tree. Run git status, then git pull --rebase before pushing."
        )
    if h == "git" and d == 1:
        return "git_signal", (
            "git returned 1: for diff --cached --check and grep this is the normal "
            "'found something' signal, not a failure; for push/pull it means the operation "
            "was rejected - read the message."
        )
    if d == 126:
        return "not_executable", (
            "command found but not executable (exit 126): chmod +x the script, or invoke it "
            "through bash/interpreter explicitly."
        )
    if d == 130:
        return "interrupted", (
            "interrupted by Ctrl-C (exit 130): intentional abort of a running command; "
            "no corrective action."
        )
    if h in {"python", "python3"} and d == 2:
        return "script_usage", (
            "script exited 2: argparse/usage error or a bad argument passed to it. Check the "
            "script's own stderr and its argument contract."
        )
    if h in {"python", "python3"} and d == 1:
        return "script_error", (
            "script exited 1: the script itself failed (missing module, missing file, "
            "assertion or unhandled exception). Read its traceback before re-running."
        )
    if h == "gh" and ("GraphQL" in lc or "failed" in lc.lower()):
        return "gh_api", (
            "gh API call failed: for 'branch has no history in common with main' the branch "
            "was created from an unrelated root - recreate it from main, or push with "
            "--force-with-lease."
        )
    if h in READ_HEADS and d == 1:
        return "path_missing", (
            "file or path argument not found (exit 1): check the path for typos and confirm "
            "the file exists before piping it."
        )
    if h in {"install", "cp", "mv"} and d == 1:
        return "copy_failed", (
            "copy/install failed (exit 1): source missing, destination not writable, or "
            "wrong permissions. Verify both paths with ls -l."
        )
    return "unclassified", (
        f"TODO: command exited {d} - inspect the recorded last_cmd and write the real lesson."
    )


def read_review(path: str):
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line:
                continue
            # split(maxsplit=4): last_cmd may itself contain tabs
            parts = line.split("\t", 4)
            if len(parts) < 5:
                continue
            key, occ, exits, shape, last_cmd = parts
            rows.append((key, occ, exits, shape, last_cmd))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", type=int, default=6,
                    help="sample rows printed per family (default 6)")
    ap.add_argument("--apply", action="store_true",
                    help="bank the edited proposals from the output TSV")
    args = ap.parse_args()

    if args.apply:
        if not os.path.exists(OUT_TSV):
            print(f"nothing to apply: {OUT_TSV} not found")
            return
        sys.path.insert(0, BIN)
        import mistake_engine_v1 as me  # noqa: E402

        con = sqlite3.connect(DB)
        before = con.execute("SELECT COUNT(*) FROM mistakes WHERE solved=1").fetchone()[0]
        con.close()

        banked = skipped = failed = 0
        with open(OUT_TSV) as fh:
            for line in fh:
                parts = line.rstrip("\n").split("\t", 2)
                if len(parts) < 3:
                    continue
                key, _family, fix = parts
                if not key or fix.startswith("TODO"):
                    skipped += 1
                    continue
                try:
                    with contextlib.redirect_stdout(io.StringIO()):
                        me.solve(key, fix)
                    banked += 1
                except SystemExit:
                    failed += 1
                except Exception as exc:  # noqa: BLE001
                    print(f"  ! {key}: {exc}")
                    failed += 1

        con = sqlite3.connect(DB)
        after = con.execute("SELECT COUNT(*) FROM mistakes WHERE solved=1").fetchone()[0]
        con.close()
        print(f"banked {banked}, skipped TODO/already-solved {skipped}, failed {failed}")
        print(f"solved keys {before} -> {after}")
        print("re-run: python3 bin/mistake_engine_v1.py compost")
        return

    if not os.path.exists(IN_TSV):
        print(f"input not found: {IN_TSV} - run compost_triage_v2.py first")
        return

    rows = read_review(IN_TSV)
    families: dict[str, list] = defaultdict(list)
    with open(OUT_TSV, "w") as fh:
        for key, occ, exits, shape, last_cmd in rows:
            fam, fix = propose(shape, last_cmd, exits)
            families[fam].append((key, occ, exits, shape, last_cmd))
            fh.write(f"{key}\t{fam}\t{fix}\n")

    print(f"review keys read: {len(rows)}")
    for fam in sorted(families, key=lambda f: -len(families[f])):
        items = families[fam]
        print(f"\n[{fam}] {len(items)} keys")
        for key, occ, exits, shape, _ in items[: args.show]:
            print(f"    {key} x{occ:<3} exit {exits[:18]:<18} {shape[:56]}")

    unclassified = len(families.get("unclassified", []))
    print(f"\nproposals -> {OUT_TSV}")
    print(f"unclassified (marked TODO): {unclassified}")
    print("edit the fix column, then: python3 bin/compost_review_resolver.py --apply")


if __name__ == "__main__":
    main()

