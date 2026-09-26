#!/usr/bin/env python3
"""
OpenRoot Permaculture CI.

Read-only CI coordinator for:
- Router context validation
- Router report generation
- Design packet validation when present
- Python compilation
- Git whitespace validation
- Protected local-runtime staging boundary checks

This tool does not commit, push, tag, release, edit registry state,
operate devices, or promote evidence levels.

Usage:
  python3 scripts/permaculture_ci.py
  python3 scripts/permaculture_ci.py --strict
  python3 scripts/permaculture_ci.py --report-dir .ci/permaculture
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

PROTECTED_LOCAL_PATHS = (
    "data/model_registry.json",
    "data/superloop_chains.json",
    "context_bridge/superloop_DASHBOARD.md",
    "bin/quarantine_pyfails_final_v2/",
)

CHECKS: list[tuple[str, list[str]]] = [
    (
        "Python syntax compilation",
        [sys.executable, "-m", "compileall", "-q", "scripts", "tests"],
    ),
    (
        "Permaculture context validation",
        [sys.executable, "scripts/validate_permaculture_context.py", "data/router_examples"],
    ),
]


def run(command: list[str]) -> tuple[int, str]:
    process = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return process.returncode, process.stdout


def git_available() -> bool:
    code, _ = run(["git", "--version"])
    return code == 0


def staged_files() -> list[str]:
    code, output = run(["git", "diff", "--cached", "--name-only"])
    if code != 0:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def protected_staged(paths: list[str]) -> list[str]:
    hits: list[str] = []

    for path in paths:
        for protected in PROTECTED_LOCAL_PATHS:
            if protected.endswith("/"):
                if path.startswith(protected):
                    hits.append(path)
            elif path == protected:
                hits.append(path)

    return sorted(set(hits))


def generate_router_reports(report_dir: Path) -> list[dict[str, Any]]:
    report_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []

    contexts = sorted(Path("data/router_examples").glob("*.json"))
    design_contexts = sorted(Path("designs").glob("*/router_context.json"))
    contexts.extend(design_contexts)

    for context in contexts:
        safe_name = context.as_posix().replace("/", "__").replace(".json", "")
        output = report_dir / f"{safe_name}.report.json"
        command = [
            sys.executable,
            "scripts/permaculture_router.py",
            str(context),
            "--output",
            str(output),
        ]
        code, text = run(command)
        results.append({
            "context": str(context),
            "report": str(output),
            "exit_code": code,
            "output": text.strip(),
        })

    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run OpenRoot Permaculture CI.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat router HOLD decisions as CI failures.",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=Path(".ci/permaculture"),
        help="Directory for generated CI reports.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results: list[dict[str, Any]] = []
    failures = 0

    for label, command in CHECKS:
        code, output = run(command)
        results.append({
            "check": label,
            "command": command,
            "exit_code": code,
            "output": output.strip(),
        })
        if code != 0:
            failures += 1

    if (ROOT / "scripts" / "validate_design_packets.py").is_file():
        command = [sys.executable, "scripts/validate_design_packets.py"]
        code, output = run(command)
        results.append({
            "check": "Design packet validation",
            "command": command,
            "exit_code": code,
            "output": output.strip(),
        })
        if code != 0:
            failures += 1

    if git_available():
        command = ["git", "diff", "--check"]
        code, output = run(command)
        results.append({
            "check": "Git whitespace validation",
            "command": command,
            "exit_code": code,
            "output": output.strip(),
        })
        if code != 0:
            failures += 1

        staged = staged_files()
        protected = protected_staged(staged)
        boundary_code = 1 if protected else 0
        results.append({
            "check": "Protected local-runtime staging boundary",
            "command": ["git", "diff", "--cached", "--name-only"],
            "exit_code": boundary_code,
            "output": (
                "Protected local/runtime files staged: " + ", ".join(protected)
                if protected
                else "No protected local/runtime files are staged."
            ),
        })
        if boundary_code != 0:
            failures += 1

    router_results = generate_router_reports(args.report_dir)
    for item in router_results:
        if item["exit_code"] != 0:
            failures += 1

        report_path = ROOT / item["report"]
        if args.strict and report_path.is_file():
            try:
                report = json.loads(report_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                failures += 1
                continue
            if report.get("decision") == "HOLD_FOR_HUMAN_REVIEW":
                failures += 1
                item["strict_failure"] = True

    summary = {
        "ci_version": 1,
        "generated_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "repository_root": str(ROOT),
        "mode": "read-only",
        "strict": args.strict,
        "failures": failures,
        "checks": results,
        "router_reports": router_results,
        "protected_local_paths": list(PROTECTED_LOCAL_PATHS),
        "invariants": [
            "This CI does not mutate Git state.",
            "This CI does not promote evidence levels.",
            "This CI does not turn an L0/L1 design into a validated physical claim.",
            "This CI blocks staging of designated local runtime paths.",
        ],
    }

    args.report_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.report_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    for result in results:
        mark = "PASS" if result["exit_code"] == 0 else "FAIL"
        print(f"[{mark}] {result['check']}")
        if result["output"]:
            print(result["output"])

    for item in router_results:
        mark = "PASS" if item["exit_code"] == 0 else "FAIL"
        print(f"[{mark}] Router report: {item['context']} → {item['report']}")
        if item["output"]:
            print(item["output"])

    print(f"Summary report: {summary_path}")

    if failures:
        print(f"OpenRoot Permaculture CI failed with {failures} failure(s).", file=sys.stderr)
        return 1

    print("OpenRoot Permaculture CI passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
