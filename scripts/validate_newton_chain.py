#!/usr/bin/env python3
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
        "failures": ["PyYAML is not installed. Install with: python3 -m pip install --user pyyaml"],
    }, indent=2))
    raise SystemExit(1)

ROOT = Path(".")
NEWTON = ROOT / "docs" / "newton_chain"
SCHEMA = NEWTON / "SCHEMA.yaml"

PROOF_REQUIRED = {
    "id", "title", "kind", "status", "statement",
    "definitions", "common_notions", "assumptions", "postulates",
    "evidence_inputs", "inference_rules", "proof_steps", "scope",
    "dependencies", "cache", "provenance", "review",
}
STEP_REQUIRED = {"step_id", "premises", "rule", "conclusion"}
SCOPE_REQUIRED = {"applies_when", "does_not_establish", "uncertainty"}
REVIEW_REQUIRED = {
    "supporting_arguments", "counterarguments",
    "unresolved_questions", "reviewer_notes",
}


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def missing(data, required):
    return sorted(required - set(data))


def main() -> int:
    failures = []
    warnings = []
    checked = []

    if not SCHEMA.exists():
        failures.append(f"{SCHEMA}: required schema file is absent.")
        schema_data = {}
    else:
        try:
            schema_data = load_yaml(SCHEMA)
            checked.append(str(SCHEMA))
        except Exception as exc:
            failures.append(f"{SCHEMA}: invalid YAML: {exc}")
            schema_data = {}

    if not isinstance(schema_data, dict):
        failures.append(f"{SCHEMA}: top-level YAML value must be a mapping.")
        schema_data = {}

    proof_schema = schema_data.get("proof_object", {})
    allowed_kinds = set(proof_schema.get("kind", {}).get("allowed", []))
    allowed_statuses = set(proof_schema.get("status", {}).get("allowed", []))

    records = sorted({
        path
        for pattern in ("**/*.yaml", "**/*.yml")
        for path in NEWTON.glob(pattern)
        if path.is_file() and path != SCHEMA
    })

    if not records:
        warnings.append(f"{NEWTON}: no Newton Chain YAML records found.")

    for path in records:
        try:
            data = load_yaml(path)
            checked.append(str(path))
        except Exception as exc:
            failures.append(f"{path}: invalid YAML: {exc}")
            continue

        if not isinstance(data, dict):
            failures.append(f"{path}: top-level YAML value must be a mapping.")
            continue

        proof = data.get("proof_object", data)
        if not isinstance(proof, dict):
            failures.append(f"{path}: proof object must be a mapping.")
            continue

        absent = missing(proof, PROOF_REQUIRED)
        if absent:
            failures.append(f"{path}: proof_object missing keys: {', '.join(absent)}")

        if allowed_kinds and proof.get("kind") not in allowed_kinds:
            failures.append(
                f"{path}: unsupported proof_object.kind: {proof.get('kind')!r}"
            )
        if allowed_statuses and proof.get("status") not in allowed_statuses:
            failures.append(
                f"{path}: unsupported proof_object.status: {proof.get('status')!r}"
            )

        for field in (
            "definitions", "common_notions", "assumptions", "postulates",
            "evidence_inputs", "inference_rules",
        ):
            if field in proof and not isinstance(proof[field], list):
                failures.append(f"{path}: proof_object.{field} must be a list.")

        steps = proof.get("proof_steps")
        if not isinstance(steps, list) or not steps:
            failures.append(f"{path}: proof_object.proof_steps must be a nonempty list.")
        else:
            for number, step in enumerate(steps, start=1):
                if not isinstance(step, dict):
                    failures.append(f"{path}: proof step {number} must be a mapping.")
                    continue
                absent = missing(step, STEP_REQUIRED)
                if absent:
                    failures.append(
                        f"{path}: proof step {number} missing keys: {', '.join(absent)}"
                    )
                if "premises" in step and not isinstance(step["premises"], list):
                    failures.append(
                        f"{path}: proof step {number} premises must be a list."
                    )

        scope = proof.get("scope")
        if not isinstance(scope, dict):
            failures.append(f"{path}: proof_object.scope must be a mapping.")
        else:
            absent = missing(scope, SCOPE_REQUIRED)
            if absent:
                failures.append(f"{path}: scope missing keys: {', '.join(absent)}")

        for field in ("dependencies", "cache", "provenance", "review"):
            if field in proof and not isinstance(proof[field], dict):
                failures.append(f"{path}: proof_object.{field} must be a mapping.")

        review = proof.get("review")
        if isinstance(review, dict):
            absent = missing(review, REVIEW_REQUIRED)
            if absent:
                failures.append(f"{path}: review missing keys: {', '.join(absent)}")

    docs = [
        ROOT / "docs" / "NEWTON_CHAIN.md",
        NEWTON / "README.md",
        NEWTON / "INFERENCE_RULES.md",
        NEWTON / "ELEMENTS.md",
    ]
    for doc in docs:
        if not doc.exists():
            continue
        checked.append(str(doc))
        for target in re.findall(r"\]\(([^)]+)\)", doc.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#", "mailto:", "/")):
                continue
            relative = target.split("#", 1)[0]
            if relative and not (doc.parent / relative).resolve().exists():
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
