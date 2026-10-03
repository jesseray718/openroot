#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print(
        json.dumps(
            {
                "check_id": "public-boundary",
                "status": "failed",
                "failures": [
                    "PyYAML is required to load .github/public-docs-policy.yaml. "
                    "Install it with: python3 -m pip install --user pyyaml"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    raise SystemExit(1)


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        text=True,
        stderr=subprocess.STDOUT,
    ).strip()


def load_policy(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"Policy file not found: {path}")
    except yaml.YAMLError as exc:
        raise ValueError(f"Policy YAML is invalid: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("Policy top level must be a mapping.")

    classes = data.get("promotion_classes")
    if not isinstance(classes, dict) or not classes:
        raise ValueError("Policy must contain a nonempty promotion_classes mapping.")

    forbidden = data.get("forbidden_path_patterns")
    if not isinstance(forbidden, list):
        raise ValueError("Policy forbidden_path_patterns must be a list.")

    return data


def compile_patterns(values: list[Any], label: str) -> list[re.Pattern[str]]:
    compiled: list[re.Pattern[str]] = []
    for value in values:
        if not isinstance(value, str) or not value:
            raise ValueError(f"{label} contains an invalid pattern: {value!r}")
        try:
            compiled.append(re.compile(value))
        except re.error as exc:
            raise ValueError(f"{label} has invalid regex {value!r}: {exc}") from exc
    return compiled


def changed_paths(base: str, head: str) -> list[str]:
    output = git(
        "diff",
        "--name-only",
        "--diff-filter=ACMR",
        base,
        head,
    )
    return [line for line in output.splitlines() if line]


def manifest_expected_paths(path: Path) -> list[str] | None:
    if not path.exists():
        return None

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Manifest is not valid JSON: {exc}") from exc

    expected = data.get("expected_paths")
    if not isinstance(expected, list) or not expected:
        raise ValueError("Manifest expected_paths must be a nonempty list.")

    if not all(isinstance(item, str) and item for item in expected):
        raise ValueError("Manifest expected_paths must contain nonempty strings only.")

    return sorted(set(expected))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Git diff against Openroot promotion policy."
    )
    parser.add_argument("--base", required=True, help="Base commit SHA or ref.")
    parser.add_argument("--head", required=True, help="Head commit SHA or ref.")
    parser.add_argument(
        "--promotion-class",
        required=True,
        help="Policy promotion class, for example automation_bootstrap or technical_docs.",
    )
    parser.add_argument(
        "--policy",
        default=".github/public-docs-policy.yaml",
        help="Repository policy path.",
    )
    parser.add_argument(
        "--manifest",
        default="docs-promotion-manifest.json",
        help="Optional promotion manifest path.",
    )
    parser.add_argument(
        "--require-manifest",
        action="store_true",
        help="Fail if the manifest file is absent.",
    )
    args = parser.parse_args()

    failures: list[str] = []
    report: dict[str, Any] = {
        "check_id": "public-boundary",
        "base": args.base,
        "head": args.head,
        "promotion_class": args.promotion_class,
        "policy_path": args.policy,
        "manifest_path": args.manifest,
        "changed_paths": [],
        "failures": failures,
    }

    try:
        policy = load_policy(Path(args.policy))
        promotion_classes = policy["promotion_classes"]

        selected = promotion_classes.get(args.promotion_class)
        if not isinstance(selected, dict):
            available = ", ".join(sorted(promotion_classes))
            raise ValueError(
                f"Unknown promotion class {args.promotion_class!r}. "
                f"Available classes: {available}"
            )

        allowed_raw = selected.get("allowed_path_patterns")
        if not isinstance(allowed_raw, list) or not allowed_raw:
            raise ValueError(
                f"Promotion class {args.promotion_class!r} must contain "
                "a nonempty allowed_path_patterns list."
            )

        allowed = compile_patterns(
            allowed_raw,
            f"promotion class {args.promotion_class} allowed_path_patterns",
        )
        forbidden = compile_patterns(
            policy["forbidden_path_patterns"],
            "forbidden_path_patterns",
        )

        paths = changed_paths(args.base, args.head)
        report["changed_paths"] = paths

        if not paths:
            failures.append("No added, copied, modified, or renamed paths were found.")

        for path in paths:
            if not any(pattern.search(path) for pattern in allowed):
                failures.append(
                    f"Path is outside the allowed boundary for "
                    f"{args.promotion_class}: {path}"
                )

            for pattern in forbidden:
                if pattern.search(path):
                    failures.append(f"Forbidden or private-looking path: {path}")
                    break

        expected = manifest_expected_paths(Path(args.manifest))
        if expected is None:
            if args.require_manifest:
                failures.append(f"Required manifest not found: {args.manifest}")
        else:
            report["manifest_expected_paths"] = expected

            excluded_control_paths = {
                ".github/public-docs-policy.yaml",
                "automation/checks/public_boundary.py",
                "automation/checks/newton_chain_validate.py",
                "automation/checks/claim_boundary.py",
                "automation/checks/provenance.py",
                "automation/schemas/docs-promotion-manifest.schema.json",
                "docs-promotion-manifest.json",
            }

            manifest_subject_paths = sorted(
                path for path in paths if path not in excluded_control_paths
            )

            if expected != manifest_subject_paths:
                failures.append(
                    "Manifest expected_paths does not match changed subject paths. "
                    f"Expected: {expected}; actual: {manifest_subject_paths}"
                )

    except (ValueError, subprocess.CalledProcessError) as exc:
        failures.append(str(exc))

    report["status"] = "passed" if not failures else "failed"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
