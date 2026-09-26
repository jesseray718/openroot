#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Render a router JSON report as Markdown.

Usage:
  python3 scripts/render_permaculture_report.py .ci/permaculture/data__router_examples__thermal-cascade-l0.report.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python3 scripts/render_permaculture_report.py <router-report.json>", file=sys.stderr)
        return 2

    path = Path(argv[1])

    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"Cannot read {path}: {exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON in {path}: {exc}", file=sys.stderr)
        return 2

    context = report.get("context", {})
    print("# OpenRoot Permaculture Router Report")
    print()
    print(f"- Generated: {report.get('generated_at_utc', 'unknown')}")
    print(f"- Context: {context.get('name', 'unknown')}")
    print(f"- Evidence: {context.get('evidence_label', 'unknown')}")
    print(f"- Decision: `{report.get('decision', 'unknown')}`")
    print()

    print("## Active principles")
    print()
    print("| ID | Principle | Active | Reasons |")
    print("|---|---|---|---|")

    for code, item in report.get("active_principles", {}).items():
        reasons = "; ".join(item.get("reasons", []))
        print(
            f"| {cell(code)} | {cell(item.get('name', ''))} | "
            f"{cell(item.get('active', False))} | {cell(reasons)} |"
        )

    print()
    print("## Gates")
    print()

    gates = report.get("gates", [])
    if not gates:
        print("No gates triggered.")
    else:
        for gate in gates:
            print(f"- `{gate.get('severity', 'unknown')}` `{gate.get('gate', 'unknown')}`: {gate.get('message', '')}")

    print()
    print("## Recommended actions")
    print()
    print("| Priority | Principles | Action | Expected artifact |")
    print("|---|---|---|---|")

    for action in report.get("recommended_actions", []):
        print(
            f"| {cell(action.get('priority', ''))} | "
            f"{cell(action.get('principles', ''))} | "
            f"{cell(action.get('action', ''))} | "
            f"{cell(action.get('artifact', ''))} |"
        )

    print()
    print("## Scores")
    print()

    for key, value in report.get("scores", {}).items():
        print(f"- `{key}`: {value}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
