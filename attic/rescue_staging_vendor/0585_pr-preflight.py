#!/usr/bin/env python3
"""Scan the current git diff the way CodeRabbit + caveman99 would.

Exit codes:
  0  clear to draft
  2  warnings only (draft allowed, publish should wait)
  3  hard reject (do not draft upstream)
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

JARGON = [
    "OpenRoot",
    "Node-001",
    "Agape",
    "Landauer",
    "ACRE",
    "R = 1.0",
    "R=1.0",
    "UNE",
    "AeroCement",
    "Black Locust",
    "joule-native",
    "coordination cost",
    "OpenRoot Auto",
    "permaculture",
]

ENERGY = [
    r"supplies energy",
    r"provides power",
    r"powers the node",
    r"free energy",
    r"harvests from the structure",
    r"passive (thermal|unit|structure).{0,40}(energy|power)",
]


def run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return (p.stdout or "") + (p.stderr or "")


def origin() -> str:
    return run(["git", "remote", "get-url", "origin"]).strip()


def parse_owner_repo(url: str) -> tuple[str, str]:
    # git@github.com:org/repo.git  or https://github.com/org/repo.git
    m = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)", url)
    if not m:
        return ("", "")
    return m.group("owner"), m.group("repo")


def changed_files() -> list[str]:
    out = run(["git", "diff", "--name-only", "HEAD"])
    staged = run(["git", "diff", "--cached", "--name-only"])
    untracked = run(["git", "ls-files", "--others", "--exclude-standard"])
    files = []
    for block in (out, staged, untracked):
        files.extend([ln.strip() for ln in block.splitlines() if ln.strip()])
    # unique preserve order
    seen = set()
    ordered = []
    for f in files:
        if f not in seen:
            seen.add(f)
            ordered.append(f)
    return ordered


def diff_text() -> str:
    return run(["git", "diff", "HEAD"]) + run(["git", "diff", "--cached"])


def main() -> int:
    if run(["git", "rev-parse", "--is-inside-work-tree"]).strip() != "true":
        print("FAIL: not a git repo")
        return 3

    url = origin()
    owner, repo = parse_owner_repo(url)
    files = changed_files()
    diff = diff_text()
    print(f"origin     {url or '(none)'}")
    print(f"owner/repo {owner}/{repo}")
    print(f"files      {len(files)}")
    for f in files:
        print(f"  - {f}")

    warnings = []
    rejects = []

    lattice = owner.lower() == "jesseray718"
    meshtastic = owner.lower() == "meshtastic"
    firmware_tree = repo.lower() in {"firmware", "meshtastic-device", "meshtastic-esp32"}

    docs_touch = any(f.startswith("docs/") or f.endswith(".md") for f in files)
    src_touch = any(f.startswith("src/") or f.startswith("variants/") for f in files)

    if meshtastic and firmware_tree and docs_touch and not src_touch:
        rejects.append(
            "11424-class: markdown-only change against meshtastic/firmware. "
            "Target meshtastic/meshtastic instead, or keep it in jesseray718/openroot."
        )

    if meshtastic:
        blob = diff + "\n" + "\n".join(files)
        for word in JARGON:
            if word.lower() in blob.lower():
                rejects.append(
                    f"upstream jargon '{word}' — strip it or move the file to the lattice."
                )

        for pat in ENERGY:
            if re.search(pat, diff, re.I):
                rejects.append(
                    f"energy-claim pattern /{pat}/ — co-location is not a power source."
                )

    if any("OpenRoot Auto" in diff for _ in [0]):
        rejects.append("diff still contains OpenRoot Auto")

    # weak success definitions
    if re.search(r"appear on a local mesh", diff, re.I):
        warnings.append(
            "success defined as 'appear on a local mesh' — require bidirectional + persistence."
        )

    if meshtastic and re.search(r"chicken[- ]wire", diff, re.I) and not re.search(
        r"keep-?out|faraday|clear of metal", diff, re.I
    ):
        warnings.append("chicken-wire mentioned without antenna keep-out / range-test.")

    if not files:
        warnings.append("no changed files. nothing to PR.")

    print("---")
    if lattice:
        print("LANE     LATTICE (your repo)")
    elif meshtastic:
        print("LANE     UPSTREAM meshtastic")
    else:
        print(f"LANE     OTHER {owner}/{repo}")

    for w in warnings:
        print(f"WARN     {w}")
    for r in rejects:
        print(f"REJECT   {r}")

    if rejects and not lattice:
        print("VERDICT  DO NOT DRAFT UPSTREAM")
        print("WRITE    keep the text in openroot; open a Meshtastic-native rewrite later.")
        return 3
    if rejects and lattice:
        print("VERDICT  LATTICE draft allowed, but clean the listed issues if this will be copied upstream later.")
        return 2
    if warnings:
        print("VERDICT  DRAFT OK, do not PUBLISH until warnings die")
        return 2
    print("VERDICT  CLEAR")
    return 0


if __name__ == "__main__":
    sys.exit(main())
