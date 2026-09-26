#!/usr/bin/env python3
"""
Validate OpenRoot permaculture router context files.

Context kinds:
- intake
- analysis
- simulation
- pilot
- physical_test
- field_operation

An empty directory is valid when it contains no router contexts. This allows
design packets to be created before a router context is intentionally added.

The validator is read-only. It never alters repository state.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED = {
    "schema_version": int,
    "name": str,
    "evidence_level": int,
    "risk_level": int,
    "uncertainty": (int, float),
    "intervention_scale": int,
    "reversibility": (int, float),
    "safety_review_complete": bool,
}

BOOL_FIELDS = {
    "missing_measurements",
    "system_map_exists",
    "feedback_exists",
    "metric_out_of_bounds",
    "stop_conditions_defined",
    "renewable_option_viable",
    "waste_stream_detected",
    "reuse_path_exists",
    "change_detected",
    "adaptation_option_exists",
    "safety_review_complete",
}

UNIT_INTERVAL_FIELDS = {
    "uncertainty",
    "reversibility",
    "concentration_risk",
    "edge_opportunity_score",
}

NONNEGATIVE_FIELDS = {
    "surplus_flow",
    "storage_capacity",
    "expected_yield",
    "minimum_yield",
    "connection_value",
    "connection_cost",
}

LIST_OF_STRING_FIELDS = {
    "claimed_outputs",
    "evidence_artifacts",
    "tags",
}

VALID_CONTEXT_KINDS = {
    "intake",
    "analysis",
    "simulation",
    "pilot",
    "physical_test",
    "field_operation",
}


def fail(path: Path, message: str) -> str:
    return f"{path}: {message}"


def context_kind(data: dict[str, Any]) -> str:
    raw_kind = data.get("context_kind", "intake")

    if not isinstance(raw_kind, str):
        raise ValueError("context_kind must be a string")

    kind = raw_kind.strip().lower()

    if kind not in VALID_CONTEXT_KINDS:
        allowed = ", ".join(sorted(VALID_CONTEXT_KINDS))
        raise ValueError(f"context_kind must be one of: {allowed}")

    return kind


def is_physical_or_operational(kind: str) -> bool:
    return kind in {"pilot", "physical_test", "field_operation"}


def validate_type(value: Any, expected_type: type | tuple[type, ...]) -> bool:
    if expected_type is int:
        return isinstance(value, int) and not isinstance(value, bool)

    if expected_type is bool:
        return isinstance(value, bool)

    return isinstance(value, expected_type) and not isinstance(value, bool)


def validate_one(path: Path) -> list[str]:
    errors: list[str] = []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [fail(path, f"invalid JSON: {exc}")]
    except OSError as exc:
        return [fail(path, f"cannot read file: {exc}")]

    if not isinstance(data, dict):
        return [fail(path, "root must be a JSON object")]

    try:
        kind = context_kind(data)
    except ValueError as exc:
        return [fail(path, str(exc))]

    for key, expected_type in REQUIRED.items():
        if key not in data:
            errors.append(fail(path, f"missing required field: {key}"))
            continue

        if not validate_type(data[key], expected_type):
            errors.append(fail(path, f"{key} has wrong type"))

    if data.get("schema_version") != 1:
        errors.append(fail(path, "schema_version must equal 1"))

    if isinstance(data.get("name"), str) and len(data["name"].strip()) < 3:
        errors.append(fail(path, "name must contain at least 3 non-space characters"))

    for key in BOOL_FIELDS:
        if key in data and not isinstance(data[key], bool):
            errors.append(fail(path, f"{key} must be boolean"))

    for key in UNIT_INTERVAL_FIELDS:
        if key not in data:
            continue

        value = data[key]

        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append(fail(path, f"{key} must be numeric"))
        elif not 0 <= value <= 1:
            errors.append(fail(path, f"{key} must be within [0, 1]"))

    for key in NONNEGATIVE_FIELDS:
        if key not in data:
            continue

        value = data[key]

        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append(fail(path, f"{key} must be numeric"))
        elif value < 0:
            errors.append(fail(path, f"{key} must not be negative"))

    for key in ("evidence_level", "risk_level", "intervention_scale"):
        if key not in data:
            continue

        value = data[key]

        if not isinstance(value, int) or isinstance(value, bool):
            errors.append(fail(path, f"{key} must be integer"))
        elif not 0 <= value <= 5:
            errors.append(fail(path, f"{key} must be within [0, 5]"))

    for key in LIST_OF_STRING_FIELDS:
        if key not in data:
            continue

        value = data[key]

        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            errors.append(fail(path, f"{key} must be a list of strings"))

    evidence_level = data.get("evidence_level")
    risk_level = data.get("risk_level")
    intervention_scale = data.get("intervention_scale")
    stop_conditions = data.get("stop_conditions_defined")
    safety_review = data.get("safety_review_complete")
    claimed_outputs = data.get("claimed_outputs", [])
    evidence_artifacts = data.get("evidence_artifacts", [])

    if (
        isinstance(evidence_level, int)
        and evidence_level <= 1
        and isinstance(claimed_outputs, list)
        and len(claimed_outputs) > 0
        and (not isinstance(evidence_artifacts, list) or len(evidence_artifacts) == 0)
    ):
        errors.append(
            fail(
                path,
                "L0/L1 contexts with claimed_outputs require evidence_artifacts or removal of unsupported claims",
            )
        )

    if is_physical_or_operational(kind):
        if isinstance(risk_level, int) and risk_level >= 1 and stop_conditions is not True:
            errors.append(
                fail(
                    path,
                    f"context_kind={kind} with risk_level >= 1 requires stop_conditions_defined: true",
                )
            )

        if isinstance(risk_level, int) and risk_level >= 2 and safety_review is not True:
            errors.append(
                fail(
                    path,
                    f"context_kind={kind} with risk_level >= 2 requires safety_review_complete: true",
                )
            )

        if (
            isinstance(intervention_scale, int)
            and isinstance(evidence_level, int)
            and intervention_scale > max(1, evidence_level)
        ):
            errors.append(
                fail(
                    path,
                    (
                        f"context_kind={kind} intervention_scale={intervention_scale} "
                        f"exceeds evidence_level={evidence_level}; reduce scope or increase evidence"
                    ),
                )
            )

    if kind in {"intake", "analysis", "simulation"}:
        if isinstance(risk_level, int) and risk_level >= 1 and stop_conditions is not False:
            errors.append(
                fail(
                    path,
                    (
                        f"context_kind={kind} should retain stop_conditions_defined: false "
                        "until an actual physical test protocol is documented"
                    ),
                )
            )

        if isinstance(evidence_level, int) and evidence_level <= 1 and safety_review is not False:
            errors.append(
                fail(
                    path,
                    (
                        f"context_kind={kind} at L0/L1 should retain safety_review_complete: false "
                        "until a specific physical intervention is prepared"
                    ),
                )
            )

    return errors


def gather_paths(target: Path) -> list[Path]:
    if target.is_file():
        return [target]

    if not target.is_dir():
        raise ValueError(f"path does not exist or is not a directory: {target}")

    return sorted(
        item
        for item in target.rglob("*.json")
        if item.name == "router_context.json" or "router_examples" in item.as_posix()
    )


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(
            "Usage: python3 scripts/validate_permaculture_context.py <file-or-directory> [...more paths]",
            file=sys.stderr,
        )
        return 2

    candidates: list[Path] = []
    empty_targets: list[Path] = []

    for item in argv[1:]:
        target = Path(item)

        try:
            paths = gather_paths(target)
        except ValueError as exc:
            print(f"Permaculture context validation failed: {exc}", file=sys.stderr)
            return 2

        if not paths:
            empty_targets.append(target)

        candidates.extend(paths)

    errors: list[str] = []

    for path in candidates:
        errors.extend(validate_one(path))

    if errors:
        print("Permaculture context validation failed:", file=sys.stderr)

        for message in errors:
            print(f"- {message}", file=sys.stderr)

        return 1

    print(f"Validated {len(candidates)} permaculture router context file(s).")

    for target in empty_targets:
        print(f"No router contexts found in {target}; treated as valid optional scope.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
