#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""professionalize_repo_v2.py - CANARY:OPENROOT-PROFESSIONALIZE-V2
Part 2 is appended separately (paste-size doctrine). Default dry-run;
CONFIRM=1 env var executes.
"""
import os
import subprocess
from pathlib import Path

ROOT = Path("/home/jesse/openroot")
LIVE = os.environ.get("CONFIRM") == "1"

DOCS = {}

DOCS["CONTRIBUTING.md"] = """# Contributing to OpenRoot

OpenRoot is a locally-sovereign automation organism: a dispatcher (bin/rootkit.py)
coordinating deterministic renderers, a SHA-256 Newton Chain of verified work,
and a POPW (Proof of Physical Work) energy ledger.

## Setup

- Linux, Python 3.10+, no cloud dependencies
- Fork, clone, branch: feat/your-topic, fix/..., docs/...

## Hard gates (PR will not merge without these)

1. python3 -m py_compile bin/<script>.py passes
2. Every Python file carries SPDX-License-Identifier: GPL-3.0-only
3. Conventions: set -eu, absolute paths, [banked]/[held]/[gate] tags
4. bin/ changes: rootkit doctor shows all wired organs OK

## Doctrine

- Never report BANKED for work that did not run.
- Energy claims are estimate or measured - never inferred.
- No >100% thermodynamic claims, no hype.
- Licenses: GPL-3.0-only code, CC BY-SA 4.0 docs.

## History note

Repo was force-pushed (large blobs stripped). Old forks will not merge
cleanly; re-clone.
"""

DOCS["SECURITY.md"] = """# Security Policy

## Note on the name

OpenRoot refers to open, auditable root-systems thinking (permaculture,
decentralized compute, verifiable work ledgers). It is NOT a
root-privilege escalation tool.

## Reporting a Vulnerability

Do NOT open a public issue. Use GitHub private vulnerability reporting.
Include: description, reproduction steps, affected script, suggested fix.

## Hardening posture

- No cloud dependency; models run locally.
- SHA-256 receipts; destructive ops gated behind CONFIRM=1.
- Human is the only commit gate.
"""

DOCS["CHANGELOG.md"] = """# Changelog

Chain-verified (not semantic) release philosophy.

## [Unreleased]

### Added
- bin/rootkit.py: unified dispatcher
- bin/newton_chain_v1.py: SHA-256 chained work ledger
- bin/popw_ledger_v1.py: POPW attestations
- bin/bom_from_source_v1.py: deterministic BOM renderer
- bin/relay_loop_v1.py: guarded publish relay

### Changed
- BOM outputs deterministic; timestamps quarantined to manifest.json
- Generated BOM report dirs gitignored

### Fixed
- Literal-newline bug in BOM JSON output
- bin/ tracking blindness via git add -N guard
"""

EDITORCONFIG = """root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 4

[*.md]
trim_trailing_whitespace = false

[*.yml]
indent_size = 2
"""

DOCS[".github/ISSUE_TEMPLATE/bug_report.md"] = """---
name: Bug report
about: Something in the organism behaved incorrectly
labels: bug
---

## Description

## Steps to Reproduce
1.
2.

## Evidence
Paste [banked]/[held]/[gate] output and exit code.

## Environment
- OS / Python / rootkit subcommand:
"""

DOCS[".github/ISSUE_TEMPLATE/feature_request.md"] = """---
name: Feature request
labels: enhancement
---

## Problem

## Proposed Solution
Which dispatcher verb does it map to?

## Acceptance Criteria
Falsifiable, grep-able, chain-recordable.
"""

DOCS[".github/PULL_REQUEST_TEMPLATE.md"] = """## Summary

## Gates Passed
- [ ] py_compile on touched Python files
- [ ] SPDX headers present
- [ ] rootkit doctor: wired organs OK

## Verification Evidence
Paste output proving the work ran.
"""

DOCS[".github/workflows/ci.yml"] = """name: CI
on:
  push:
    branches: [main]
  pull_request:
jobs:
  gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Syntax gate
        run: |
          set -eu
          rc=0
          for f in bin/*.py; do
            python3 -m py_compile "$f" || { echo "SYNTAX FAIL: $f"; rc=1; }
          done
          exit $rc
      - name: SPDX gate
        run: |
          set -eu
          missing=""
          for f in bin/*.py; do
            grep -q 'SPDX-License-Identifier' "$f" || missing="$missing $f"
          done
          [ -z "$missing" ] || { echo "SPDX MISSING:$missing"; exit 1; }
          echo "SPDX gate: pass"
"""

DOCS["docs/architecture.md"] = """# Architecture

Flat bin/ layout: dispatcher + independently runnable organ scripts.

## Dispatcher: bin/rootkit.py
Verbs: ingest, index, chunk, ask, task, popw, chain, publish, migrate,
doctor, organism, mint, audit. Exit: 0 BANKED, 1 HELD, 2 ERROR.

## Wired organs
- bom_from_source_v1.py - deterministic BOM renderer
- popw_ledger_v1.py - POPW attestations
- newton_chain_v1.py - SHA-256 chained ledger
- relay_loop_v1.py - guarded publish relay
- a1_core_v1.py, ask_router_v1.py, chunker_v1.py, lumo_ingest.py,
  rootkit_migrate_v1.py - corpus indexing and routing

## Data Flow

task spec -> dispatcher (spec_sha256) -> organ (deterministic hashes)
-> POPW record -> Newton Chain append -> human-gated publish

## Principles

- SHA-256 content addressing is the spine
- Falsifiable claims only
- Human is the only commit gate
- Local sovereignty, no cloud dependency
"""

DOCS["docs/getting-started.md"] = """# Getting Started

Linux, Python 3.10+, no cloud accounts.

    git clone https://github.com/jesseray718/openroot.git
    cd openroot
    python3 bin/rootkit.py doctor
    python3 bin/newton_chain_v1.py verify   # expect green

Run a render:

    python3 bin/rootkit.py task --spec '{"type":"bom","source":"/path/src.json"}'

Code: GPL-3.0-only. Docs: CC BY-SA 4.0.
"""

COMMIT_GROUPS = [
    ("docs: CONTRIBUTING, SECURITY, CHANGELOG",
     ["CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md"]),
    ("chore: editorconfig", [".editorconfig"]),
    ("chore: GitHub templates",
     [".github/ISSUE_TEMPLATE/bug_report.md",
      ".github/ISSUE_TEMPLATE/feature_request.md",
      ".github/PULL_REQUEST_TEMPLATE.md"]),
    ("ci: py_compile + SPDX gates", [".github/workflows/ci.yml"]),
    ("docs: architecture and getting-started",
     ["docs/architecture.md", "docs/getting-started.md"]),
]

def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args],
                           capture_output=True, text=True)

def main():
    print("CANARY:OPENROOT-PROFESSIONALIZE-V2")
    print("[gate] " + ("LIVE (CONFIRM=1)" if LIVE else "DRY RUN"))

    lic = ROOT / "LICENSE"
    if lic.exists():
        print("[banked] LICENSE present, skip")
    else:
        import urllib.request
        try:
            txt = urllib.request.urlopen(
                "https://www.gnu.org/licenses/gpl-3.0.txt", timeout=30).read().decode()
            assert "GNU GENERAL PUBLIC LICENSE" in txt and "VERSION 3" in txt
            if LIVE:
                lic.write_text(txt + "\n\nCopyright (C) 2026 Jesse Ray / OpenRoot LLC\n")
                print("[banked] LICENSE written (fetched+verified)")
            else:
                print("[gate] (dry) would write verified LICENSE")
        except Exception as e:
            print("[held] LICENSE fetch failed: %s" % e)
            return 1

    if LIVE:
        (ROOT / ".editorconfig").write_text(EDITORCONFIG)
    for rel in DOCS:
        tgt = ROOT / rel
        if LIVE:
            tgt.parent.mkdir(parents=True, exist_ok=True)
            tgt.write_text(DOCS[rel])
        print("[{}] wrote {}".format("banked" if LIVE else "gate", rel))

    if not LIVE:
        print("[gate] DRY RUN COMPLETE - rerun with CONFIRM=1")
        return 0

    for msg, paths in COMMIT_GROUPS:
        existing = [p for p in paths if (ROOT / p).exists()]
        if not existing:
            continue
        git("add", *existing)
        r = git("commit", "-m", msg + "; CANARY:OPENROOT-PROFESSIONALIZE-V2")
        if r.returncode == 0:
            print("[banked] " + msg)
        elif "nothing to commit" in (r.stdout + r.stderr).lower():
            print("[banked] " + msg + " (idempotent skip)")
        else:
            print("[held] commit failed: " + msg)
            print(r.stderr)
            return 1
    print("[banked] professionalize v2 complete")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
