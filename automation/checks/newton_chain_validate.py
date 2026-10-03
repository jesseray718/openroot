#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print(json.dumps({
        "check_id": "newton-chain-validate",
        "status": "failed",
        "failures": ["PyYAML is not installed. Install with: python3 -m pip install --user pyyaml"]
    }, indent=2))
    raise SystemExit(1)

ROOT = Path(".")
YAML_PATHS = sorted(
    p for p in list(ROOT.glob("docs/newton_chain/**/*.yaml")) + list(ROOT.glob("docs/newton_chain/**/*.yml"))
    if p.is_file()
)

REQUIRED_EXAMPLE_KEYS = {
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

def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []

    schema = ROOT / "docs/newton_chain/SCHEMA.yaml"
    if not schema.exists():
        warnings.append("docs/newton_chain/SCHEMA.yaml is absent; schema-presence check skipped.")
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

        if "EXAMPLES" in path.parts:
            missing = sorted(REQUIRED_EXAMPLE_KEYS - set(data))
            if missing:
                failures.append(f"{path}: missing required example keys: {', '.join(missing)}")

            evidence_level = data.get("evidence_level")
            if not isinstance(evidence_level, str) or not evidence_level.strip():
                failures.append(f"{path}: evidence_level must be a nonempty string.")

            assumptions = data.get("assumptions")
            if not isinstance(assumptions, (list, str)) or not assumptions:
                failures.append(f"{path}: assumptions must be a nonempty list or string.")

            non_claims = data.get("non_claims")
            if not isinstance(non_claims, (list, str)) or not non_claims:
                failures.append(f"{path}: non_claims must be a nonempty list or string.")

            variables = data.get("variables")
            if not isinstance(variables, (dict, list)) or not variables:
                failures.append(f"{path}: variables must be a nonempty mapping or list.")

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
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            candidate = (doc.parent / target.split("#", 1)[0]).resolve()
            if target and not candidate.exists():
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
