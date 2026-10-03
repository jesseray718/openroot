#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

SENSITIVE = re.compile(
    r"\b(safe|safety|certified|compliant|approved|field[- ]ready|production[- ]ready|"
    r"guarantee(?:d)?|proven|validated|zero[- ]risk)\b",
    re.IGNORECASE,
)
EVIDENCE_MARKERS = re.compile(
    r"(evidence[_ -]?level|assumption|non[_ -]?claims?|limitations?|known bounds?|"
    r"not a safety|not certified|not validated)",
    re.IGNORECASE,
)

def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True)

def main() -> int:
    if len(sys.argv) != 3:
        print("usage: claim_boundary.py BASE_SHA HEAD_SHA", file=sys.stderr)
        return 2

    base, head = sys.argv[1], sys.argv[2]
    names = [
        p for p in git("diff", "--name-only", "--diff-filter=ACMR", base, head).splitlines()
        if p.startswith(("README.md", "docs/"))
    ]
    failures: list[str] = []
    findings: list[dict[str, str]] = []

    for name in names:
        try:
            text = git("diff", "--unified=0", base, head, "--", name)
        except subprocess.CalledProcessError as exc:
            failures.append(f"Could not inspect changed content for {name}: {exc}")
            continue

        added = "\n".join(
            line[1:] for line in text.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        )
        for match in SENSITIVE.finditer(added):
            context = added[max(0, match.start() - 220):match.end() + 220]
            if not EVIDENCE_MARKERS.search(context):
                findings.append({
                    "path": name,
                    "term": match.group(0),
                    "context": context.replace("\n", " ")[:500],
                })

    if findings:
        failures.append(
            "Sensitive public claim language was added without a nearby evidence, "
            "assumption, limitation, or explicit non-claim marker."
        )

    report = {
        "check_id": "claim-boundary",
        "status": "passed" if not failures else "failed",
        "findings": findings,
        "failures": failures,
        "note": (
            "This is a conservative text gate, not a scientific verifier. "
            "Human technical review remains required for substantive claims."
        ),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not failures else 1

if __name__ == "__main__":
    raise SystemExit(main())
