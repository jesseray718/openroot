#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import json
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    print(json.dumps({
        "check_id": "newton-chain-validate",
        "status": "failed",
        "failures": [
            "PyYAML is not installed. Install with: python3 -m pip install --user pyyaml"
        ],
    }, indent=2))
    raise SystemExit(1)

ROOT = Path(".")
YAML_PATHS = sorted(
    path for path in [
        *ROOT.glob("docs/newton_chain/**/*.yaml"),
        *ROOT.glob("docs/newton_chain/**/*.yml"),
    ]
    if path.is_file()
)

STRICT_SCHEMA_VERSION = "1.0"
STRICT_EXAMPLE_KEYS = {
    "claim_id",
    "title",
    "evidence_level",
    "assumptions",
    "variables",
    "conclusion",
    "non_claims",
}


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def validate_strict_example(path: Path, data: dict, failures: list[str]) -> None:
    missing = sorted(STRICT_EXAMPLE_KEYS - set(data))
    if missing:
        failures.append(
            f"{path}: schema_version {STRICT_SCHEMA_VERSION} is missing "
            f"required example keys: {', '.join(missing)}"
        )

    evidence_level = data.get("evidence_level")
    if not isinstance(evidence_level, str) or not evidence_level.strip():
        failures.append(
            f"{path}: schema_version {STRICT_SCHEMA_VERSION} requires "
            "evidence_level to be a nonempty string."
        )

    assumptions = data.get("assumptions")
    if not isinstance(assumptions, (list, str)) or not assumptions:
        failures.append(
            f"{path}: schema_version {STRICT_SCHEMA_VERSION} requires "
            "assumptions to be a nonempty list or string."
        )

    non_claims = data.get("non_claims")
    if not isinstance(non_claims, (list, str)) or not non_claims:
        failures.append(
            f"{path}: schema_version {STRICT_SCHEMA_VERSION} requires "
            "non_claims to be a nonempty list or string."
        )

    variables = data.get("variables")
    if not isinstance(variables, (dict, list)) or not variables:
        failures.append(
            f"{path}: schema_version {STRICT_SCHEMA_VERSION} requires "
            "variables to be a nonempty mapping or list."
        )


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []

    schema = ROOT / "docs/newton_chain/SCHEMA.yaml"
    if not schema.exists():
        warnings.append(
            "docs/newton_chain/SCHEMA.yaml is absent; schema-presence check skipped."
        )
    else:
        try:
            schema_data = load_yaml(schema)
            checked.append(str(schema))
            if not isinstance(schema_data, dict):
                failures.append(f"{schema}: top-level YAML value must be a mapping.")
        except Exception as exc:
            failures.append(f"{schema}: invalid YAML: {exc}")

    for path in YAML_PATHS:
        try:
            data = load_yaml(path)
            checked.append(str(path))
        except Exception as exc:
            failures.append(f"{path}: invalid YAML: {exc}")
            continue

        if not isinstance(data, dict):
            failures.append(f"{path}: top-level YAML value must be a mapping.")
            continue

        if "EXAMPLES" not in path.parts:
            continue

        schema_version = data.get("schema_version")
        if schema_version == STRICT_SCHEMA_VERSION:
            validate_strict_example(path, data, failures)
        else:
            warnings.append(
                f"{path}: legacy or unspecified schema_version; "
                f"strict {STRICT_SCHEMA_VERSION} example fields not enforced."
            )

    docs = [
        ROOT / "docs/NEWTON_CHAIN.md",
        ROOT / "docs/newton_chain/README.md",
        ROOT / "docs/newton_chain/INFERENCE_RULES.md",
        ROOT / "docs/newton_chain/ELEMENTS.md",
    ]

    for doc in docs:
        if not doc.exists():
            continue

        checked.append(str(doc))
        text = doc.read_text(encoding="utf-8")

        for target in re.findall(r"\]\(([^)]+)\)", text):
            if target.startswith(("http://", "https://", "#", "mailto:", "/")):
                continue

            relative = target.split("#", 1)[0]
            if not relative:
                continue

            candidate = (doc.parent / relative).resolve()
            if not candidate.exists():
                failures.append(f"{doc}: broken local Markdown reference: {target}")

    report = {
        "check_id": "newton-chain-validate",
        "status": "passed" if not failures else "failed",
        "checked": checked,
        "warnings": warnings,
        "failures": failures,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
