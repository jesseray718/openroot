#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""
OpenRoot Permaculture Router v0.1.0

A deterministic decision-support engine for the 12 permaculture principles.

Safety model:
- Read-only by design.
- Never writes source files unless --output is explicitly provided.
- Never stages, commits, pushes, tags, releases, opens/closes issues,
  changes external state, controls equipment, or promotes evidence levels.
- Produces an auditable report for human review.

Usage:
  python3 scripts/permaculture_router.py data/router_examples/thermal-cascade-l0.json
  python3 scripts/permaculture_router.py designs/thermal-cascade/router_context.json --output reports/thermal-cascade-router.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PRINCIPLES: dict[str, dict[str, str]] = {
    "P01": {
        "name": "Observe and interact",
        "purpose": "Reduce uncertainty before intervention."
    },
    "P02": {
        "name": "Catch and store energy",
        "purpose": "Retain useful surplus flows before they dissipate."
    },
    "P03": {
        "name": "Obtain a yield",
        "purpose": "Define and measure durable useful output."
    },
    "P04": {
        "name": "Apply self-regulation and accept feedback",
        "purpose": "Keep the system within safe and intended bounds."
    },
    "P05": {
        "name": "Use and value renewable resources and services",
        "purpose": "Prefer renewable, local, repairable, regenerative inputs where justified."
    },
    "P06": {
        "name": "Produce no waste",
        "purpose": "Treat avoidable losses and byproducts as candidate inputs."
    },
    "P07": {
        "name": "Design from patterns to details",
        "purpose": "Establish system boundary, flows, dependencies, and constraints before detail expansion."
    },
    "P08": {
        "name": "Integrate rather than segregate",
        "purpose": "Connect compatible nodes when transfer value exceeds total connection burden."
    },
    "P09": {
        "name": "Use small and slow solutions",
        "purpose": "Match intervention scale to evidence, reversibility, and risk."
    },
    "P10": {
        "name": "Use and value diversity",
        "purpose": "Reduce single points of failure and increase adaptive capacity."
    },
    "P11": {
        "name": "Use edges and value the marginal",
        "purpose": "Inspect interfaces, overlooked users, boundary losses, and low-resource opportunities."
    },
    "P12": {
        "name": "Creatively use and respond to change",
        "purpose": "Adapt assumptions and plans to meaningful changes in conditions."
    }
}

ROUTE_EDGES = [
    ("P01", "P04"),
    ("P01", "P07"),
    ("P01", "P09"),
    ("P01", "P12"),
    ("P02", "P03"),
    ("P02", "P06"),
    ("P02", "P08"),
    ("P03", "P04"),
    ("P04", "P01"),
    ("P04", "P09"),
    ("P04", "P12"),
    ("P05", "P02"),
    ("P05", "P06"),
    ("P05", "P10"),
    ("P06", "P02"),
    ("P06", "P08"),
    ("P07", "P08"),
    ("P07", "P10"),
    ("P07", "P11"),
    ("P08", "P03"),
    ("P08", "P06"),
    ("P08", "P10"),
    ("P09", "P01"),
    ("P09", "P04"),
    ("P10", "P04"),
    ("P10", "P12"),
    ("P11", "P02"),
    ("P11", "P06"),
    ("P11", "P08"),
    ("P12", "P01"),
    ("P12", "P04"),
    ("P12", "P09"),
]

EVIDENCE_LABELS = {
    0: "L0 — concept or unverified idea",
    1: "L1 — documented source, calculation, simulation, or design rationale",
    2: "L2 — documented controlled physical measurement",
    3: "L3 — replicated physical measurement",
    4: "L4 — documented field validation",
    5: "L5 — independent replication or mature validation"
}


@dataclass(frozen=True)
class Context:
    schema_version: int
    name: str
    description: str
    context_kind: str
    evidence_level: int
    risk_level: int
    uncertainty: float
    missing_measurements: bool
    system_map_exists: bool
    feedback_exists: bool
    metric_out_of_bounds: bool
    stop_conditions_defined: bool
    surplus_flow: float
    storage_capacity: float
    expected_yield: float
    minimum_yield: float
    renewable_option_viable: bool
    lifecycle_benefit: float
    waste_stream_detected: bool
    reuse_path_exists: bool
    compatible_nodes: int
    connection_value: float
    connection_cost: float
    intervention_scale: int
    reversibility: float
    concentration_risk: float
    edge_opportunity_score: float
    change_detected: bool
    adaptation_option_exists: bool
    safety_review_complete: bool
    claimed_outputs: tuple[str, ...]
    evidence_artifacts: tuple[str, ...]
    tags: tuple[str, ...]


def bool_value(data: dict[str, Any], key: str, default: bool = False) -> bool:
    value = data.get(key, default)
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be boolean")
    return value


def number_value(data: dict[str, Any], key: str, default: float = 0.0) -> float:
    value = data.get(key, default)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{key} must be numeric")
    return float(value)


def int_value(data: dict[str, Any], key: str, default: int = 0) -> int:
    value = data.get(key, default)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{key} must be an integer")
    return value


def string_value(data: dict[str, Any], key: str, default: str = "") -> str:
    value = data.get(key, default)
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string")
    return value


def string_list(data: dict[str, Any], key: str) -> tuple[str, ...]:
    value = data.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{key} must be a list of strings")
    return tuple(value)


def load_context(path: Path) -> Context:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Context file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValueError("Context root must be a JSON object")

    context = Context(
        schema_version=int_value(raw, "schema_version"),
        name=string_value(raw, "name"),
        description=string_value(raw, "description", ""),
        context_kind=string_value(raw, "context_kind", "intake").strip().lower(),
        evidence_level=int_value(raw, "evidence_level"),
        risk_level=int_value(raw, "risk_level"),
        uncertainty=number_value(raw, "uncertainty"),
        missing_measurements=bool_value(raw, "missing_measurements", True),
        system_map_exists=bool_value(raw, "system_map_exists", False),
        feedback_exists=bool_value(raw, "feedback_exists", False),
        metric_out_of_bounds=bool_value(raw, "metric_out_of_bounds", False),
        stop_conditions_defined=bool_value(raw, "stop_conditions_defined", False),
        surplus_flow=number_value(raw, "surplus_flow", 0.0),
        storage_capacity=number_value(raw, "storage_capacity", 0.0),
        expected_yield=number_value(raw, "expected_yield", 0.0),
        minimum_yield=number_value(raw, "minimum_yield", 1.0),
        renewable_option_viable=bool_value(raw, "renewable_option_viable", False),
        lifecycle_benefit=number_value(raw, "lifecycle_benefit", 0.0),
        waste_stream_detected=bool_value(raw, "waste_stream_detected", False),
        reuse_path_exists=bool_value(raw, "reuse_path_exists", False),
        compatible_nodes=int_value(raw, "compatible_nodes", 0),
        connection_value=number_value(raw, "connection_value", 0.0),
        connection_cost=number_value(raw, "connection_cost", 1.0),
        intervention_scale=int_value(raw, "intervention_scale"),
        reversibility=number_value(raw, "reversibility"),
        concentration_risk=number_value(raw, "concentration_risk", 0.0),
        edge_opportunity_score=number_value(raw, "edge_opportunity_score", 0.0),
        change_detected=bool_value(raw, "change_detected", False),
        adaptation_option_exists=bool_value(raw, "adaptation_option_exists", False),
        safety_review_complete=bool_value(raw, "safety_review_complete"),
        claimed_outputs=string_list(raw, "claimed_outputs"),
        evidence_artifacts=string_list(raw, "evidence_artifacts"),
        tags=string_list(raw, "tags"),
    )

    validate_context(context)
    return context


def validate_context(ctx: Context) -> None:
    if ctx.schema_version != 1:
        raise ValueError("schema_version must be 1")
    if ctx.context_kind not in {"intake", "analysis", "simulation", "pilot", "physical_test", "field_operation"}:
        raise ValueError("context_kind is invalid")
    if len(ctx.name.strip()) < 3:
        raise ValueError("name must contain at least 3 non-space characters")
    if not 0 <= ctx.evidence_level <= 5:
        raise ValueError("evidence_level must be between 0 and 5")
    if not 0 <= ctx.risk_level <= 5:
        raise ValueError("risk_level must be between 0 and 5")
    if not 0 <= ctx.uncertainty <= 1:
        raise ValueError("uncertainty must be between 0 and 1")
    if not 0 <= ctx.reversibility <= 1:
        raise ValueError("reversibility must be between 0 and 1")
    if not 0 <= ctx.concentration_risk <= 1:
        raise ValueError("concentration_risk must be between 0 and 1")
    if not 0 <= ctx.edge_opportunity_score <= 1:
        raise ValueError("edge_opportunity_score must be between 0 and 1")
    if not 0 <= ctx.intervention_scale <= 5:
        raise ValueError("intervention_scale must be between 0 and 5")
    if ctx.minimum_yield < 0:
        raise ValueError("minimum_yield must not be negative")
    if ctx.connection_cost < 0:
        raise ValueError("connection_cost must not be negative")
    if ctx.surplus_flow < 0 or ctx.storage_capacity < 0:
        raise ValueError("surplus_flow and storage_capacity must not be negative")


def activate_principles(ctx: Context) -> dict[str, dict[str, Any]]:
    scale_exceeds_evidence = ctx.intervention_scale > max(1, ctx.evidence_level)
    low_reversibility = ctx.reversibility < 0.70
    elevated_risk = ctx.risk_level > ctx.evidence_level

    active: dict[str, dict[str, Any]] = {
        "P01": {
            "active": ctx.missing_measurements or ctx.uncertainty > 0.35 or ctx.change_detected,
            "reasons": []
        },
        "P02": {
            "active": ctx.surplus_flow > 0 and ctx.storage_capacity > 0,
            "reasons": []
        },
        "P03": {
            "active": ctx.expected_yield >= ctx.minimum_yield and ctx.minimum_yield > 0,
            "reasons": []
        },
        "P04": {
            "active": (not ctx.feedback_exists) or ctx.metric_out_of_bounds or (not ctx.stop_conditions_defined),
            "reasons": []
        },
        "P05": {
            "active": ctx.renewable_option_viable and ctx.lifecycle_benefit > 0,
            "reasons": []
        },
        "P06": {
            "active": ctx.waste_stream_detected and ctx.reuse_path_exists,
            "reasons": []
        },
        "P07": {
            "active": (not ctx.system_map_exists) or ctx.intervention_scale > 1,
            "reasons": []
        },
        "P08": {
            "active": ctx.compatible_nodes >= 2 and ctx.connection_value > ctx.connection_cost,
            "reasons": []
        },
        "P09": {
            "active": scale_exceeds_evidence or low_reversibility or elevated_risk,
            "reasons": []
        },
        "P10": {
            "active": ctx.concentration_risk > 0.50,
            "reasons": []
        },
        "P11": {
            "active": ctx.edge_opportunity_score > 0.50,
            "reasons": []
        },
        "P12": {
            "active": ctx.change_detected and ctx.adaptation_option_exists,
            "reasons": []
        },
    }

    if active["P01"]["active"]:
        active["P01"]["reasons"] = [
            f"missing_measurements={ctx.missing_measurements}",
            f"uncertainty={ctx.uncertainty:.2f}",
            f"change_detected={ctx.change_detected}",
        ]

    if active["P02"]["active"]:
        active["P02"]["reasons"] = [
            f"surplus_flow={ctx.surplus_flow:.3f}",
            f"storage_capacity={ctx.storage_capacity:.3f}",
        ]

    if active["P03"]["active"]:
        active["P03"]["reasons"] = [
            f"expected_yield={ctx.expected_yield:.3f}",
            f"minimum_yield={ctx.minimum_yield:.3f}",
        ]

    if active["P04"]["active"]:
        active["P04"]["reasons"] = [
            f"feedback_exists={ctx.feedback_exists}",
            f"metric_out_of_bounds={ctx.metric_out_of_bounds}",
            f"stop_conditions_defined={ctx.stop_conditions_defined}",
        ]

    if active["P05"]["active"]:
        active["P05"]["reasons"] = [
            f"renewable_option_viable={ctx.renewable_option_viable}",
            f"lifecycle_benefit={ctx.lifecycle_benefit:.3f}",
        ]

    if active["P06"]["active"]:
        active["P06"]["reasons"] = [
            f"waste_stream_detected={ctx.waste_stream_detected}",
            f"reuse_path_exists={ctx.reuse_path_exists}",
        ]

    if active["P07"]["active"]:
        active["P07"]["reasons"] = [
            f"system_map_exists={ctx.system_map_exists}",
            f"intervention_scale={ctx.intervention_scale}",
        ]

    if active["P08"]["active"]:
        active["P08"]["reasons"] = [
            f"compatible_nodes={ctx.compatible_nodes}",
            f"connection_value={ctx.connection_value:.3f}",
            f"connection_cost={ctx.connection_cost:.3f}",
        ]

    if active["P09"]["active"]:
        active["P09"]["reasons"] = [
            f"intervention_scale={ctx.intervention_scale}",
            f"evidence_level={ctx.evidence_level}",
            f"reversibility={ctx.reversibility:.2f}",
            f"risk_level={ctx.risk_level}",
        ]

    if active["P10"]["active"]:
        active["P10"]["reasons"] = [
            f"concentration_risk={ctx.concentration_risk:.2f}",
        ]

    if active["P11"]["active"]:
        active["P11"]["reasons"] = [
            f"edge_opportunity_score={ctx.edge_opportunity_score:.2f}",
        ]

    if active["P12"]["active"]:
        active["P12"]["reasons"] = [
            f"change_detected={ctx.change_detected}",
            f"adaptation_option_exists={ctx.adaptation_option_exists}",
        ]

    for code, payload in active.items():
        payload["name"] = PRINCIPLES[code]["name"]
        payload["purpose"] = PRINCIPLES[code]["purpose"]

    return active


def hard_gates(ctx: Context, active: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []

    if ctx.risk_level > ctx.evidence_level:
        blockers.append({
            "gate": "evidence_risk_gate",
            "severity": "block",
            "message": (
                f"Risk level {ctx.risk_level} exceeds evidence level {ctx.evidence_level}. "
                "Reduce scope, gather evidence, or require explicit human review."
            ),
        })

    if ctx.risk_level >= 2 and not ctx.safety_review_complete:
        blockers.append({
            "gate": "safety_review_gate",
            "severity": "block",
            "message": (
                "Safety review is incomplete for a risk level of 2 or greater. "
                "Do not execute or scale a physical intervention."
            ),
        })

    if ctx.missing_measurements and ctx.intervention_scale > 1:
        blockers.append({
            "gate": "observation_gate",
            "severity": "block",
            "message": (
                "Measurements are missing while intervention scale exceeds a minimal pilot. "
                "Observe and measure before expanding."
            ),
        })

    if not ctx.stop_conditions_defined and ctx.risk_level >= 1:
        blockers.append({
            "gate": "stop_condition_gate",
            "severity": "block",
            "message": (
                "Safe stop conditions are not defined for a nonzero risk context. "
                "Define stop conditions before testing."
            ),
        })

    if ctx.reversibility < 0.70 and ctx.intervention_scale > 1:
        blockers.append({
            "gate": "reversibility_gate",
            "severity": "block",
            "message": (
                "The proposed intervention is insufficiently reversible at its current scale. "
                "Use a smaller, bounded, reversible pilot."
            ),
        })

    if ctx.evidence_level <= 1 and len(ctx.claimed_outputs) > 0:
        blockers.append({
            "gate": "claim_boundary_gate",
            "severity": "warning",
            "message": (
                "L0/L1 contexts contain claimed outputs. Treat statements as hypotheses "
                "unless supported by explicit documented evidence artifacts."
            ),
        })

    if active["P04"]["active"] and ctx.risk_level >= 1:
        blockers.append({
            "gate": "feedback_gate",
            "severity": "warning",
            "message": (
                "Feedback, bounds, or stop conditions are incomplete. Add monitoring "
                "before any action beyond observation."
            ),
        })

    return blockers


def route_edges(active: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    routed: list[dict[str, str]] = []

    for source, target in ROUTE_EDGES:
        if active[source]["active"] and active[target]["active"]:
            routed.append({
                "from": source,
                "to": target,
                "from_name": PRINCIPLES[source]["name"],
                "to_name": PRINCIPLES[target]["name"],
            })

    return routed


def recommended_actions(ctx: Context, active: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []

    if active["P01"]["active"]:
        actions.append({
            "priority": "P0",
            "principles": "P01",
            "action": "Collect the smallest set of measurements that removes the highest-impact uncertainty.",
            "artifact": "Dated raw-data record with conditions, instrument, units, and caveats.",
        })

    if active["P07"]["active"]:
        actions.append({
            "priority": "P0",
            "principles": "P07",
            "action": "Draw or update the system boundary: inputs, outputs, nodes, flows, dependencies, hazards, and excluded claims.",
            "artifact": "System map or boundary diagram linked from the design packet.",
        })

    if active["P04"]["active"]:
        actions.append({
            "priority": "P0",
            "principles": "P04",
            "action": "Define measurable operating bounds, feedback metrics, safe stop conditions, and human escalation criteria.",
            "artifact": "Test protocol with explicit stop conditions and review requirements.",
        })

    if active["P09"]["active"]:
        actions.append({
            "priority": "P0",
            "principles": "P09",
            "action": "Reduce the intervention to a reversible, single-node, low-risk pilot that is proportionate to the evidence level.",
            "artifact": "Pilot plan, rollback plan, and expected evidence artifact.",
        })

    if active["P02"]["active"] and active["P06"]["active"]:
        actions.append({
            "priority": "P1",
            "principles": "P02 + P06",
            "action": "Map the surplus or waste stream, quantify it, and test one safe route for capture, storage, or reuse.",
            "artifact": "Flow estimate with source, sink, transfer loss, and storage limits.",
        })

    if active["P06"]["active"] and active["P08"]["active"]:
        actions.append({
            "priority": "P1",
            "principles": "P06 + P08",
            "action": "Evaluate whether one node output can become another node input without increasing maintenance or risk disproportionately.",
            "artifact": "Node-to-node interface specification and compatibility check.",
        })

    if active["P05"]["active"]:
        actions.append({
            "priority": "P1",
            "principles": "P05",
            "action": "Compare renewable, local, repairable, and regenerative alternatives against lifecycle burden and reliability.",
            "artifact": "Option comparison with maintenance, cost, repairability, and dependency notes.",
        })

    if active["P10"]["active"]:
        actions.append({
            "priority": "P1",
            "principles": "P10",
            "action": "Add an alternate path, substitute component, skill path, supplier path, or fallback operating mode.",
            "artifact": "Redundancy and single-point-of-failure register.",
        })

    if active["P11"]["active"]:
        actions.append({
            "priority": "P1",
            "principles": "P11",
            "action": "Inspect interfaces, boundary losses, neglected users, low-resource nodes, and underused surplus streams.",
            "artifact": "Edge-opportunity inventory ranked by benefit, effort, and risk.",
        })

    if active["P12"]["active"]:
        actions.append({
            "priority": "P1",
            "principles": "P12",
            "action": "Record what changed, invalidate stale assumptions, and compare adaptation options before choosing a revised plan.",
            "artifact": "Change log and assumption revision record.",
        })

    if active["P03"]["active"]:
        actions.append({
            "priority": "P2",
            "principles": "P03",
            "action": "Define a useful yield metric and a maintenance horizon so short-term output does not hide lifecycle burden.",
            "artifact": "Yield definition with units, baseline, target, and observation period.",
        })

    if not actions:
        actions.append({
            "priority": "P2",
            "principles": "none",
            "action": "No principle activation crossed current thresholds. Preserve observation and reassess when conditions change.",
            "artifact": "No-op decision record.",
        })

    return actions


def score(ctx: Context, active: dict[str, dict[str, Any]], blockers: list[dict[str, str]]) -> dict[str, float]:
    active_count = sum(1 for value in active.values() if value["active"])
    evidence_confidence = ctx.evidence_level / 5.0
    reversibility_score = ctx.reversibility
    node_score = min(1.0, math.log2(ctx.compatible_nodes + 1) / 3.0)
    integration_score = 0.0
    if ctx.connection_cost > 0:
        integration_score = max(0.0, min(1.0, ctx.connection_value / ctx.connection_cost - 1.0))

    yield_score = 0.0
    if ctx.minimum_yield > 0:
        yield_score = max(0.0, min(1.0, ctx.expected_yield / ctx.minimum_yield))

    resilience_score = max(
        0.0,
        min(
            1.0,
            (
                (1.0 - ctx.concentration_risk)
                + reversibility_score
                + (1.0 if ctx.feedback_exists else 0.0)
                + (1.0 if ctx.stop_conditions_defined else 0.0)
            ) / 4.0,
        ),
    )

    burden = (
        (ctx.intervention_scale / 5.0)
        + (ctx.risk_level / 5.0)
        + (1.0 - ctx.reversibility)
        + ctx.uncertainty
    ) / 4.0

    block_count = sum(1 for item in blockers if item["severity"] == "block")
    warning_count = sum(1 for item in blockers if item["severity"] == "warning")
    governance_penalty = min(1.0, 0.25 * block_count + 0.08 * warning_count)

    durable_benefit = (
        0.20 * evidence_confidence
        + 0.15 * node_score
        + 0.15 * integration_score
        + 0.15 * yield_score
        + 0.25 * resilience_score
        + 0.10 * min(1.0, active_count / 12.0)
    )

    safe_opportunity = max(0.0, durable_benefit * (1.0 - burden) * (1.0 - governance_penalty))

    return {
        "active_principle_fraction": round(active_count / 12.0, 4),
        "evidence_confidence": round(evidence_confidence, 4),
        "node_reach_score": round(node_score, 4),
        "integration_score": round(integration_score, 4),
        "yield_score": round(yield_score, 4),
        "resilience_score": round(resilience_score, 4),
        "lifecycle_burden_score": round(burden, 4),
        "governance_penalty": round(governance_penalty, 4),
        "safe_opportunity_score": round(safe_opportunity, 4),
    }


def decision(blockers: list[dict[str, str]], active: dict[str, dict[str, Any]]) -> str:
    has_block = any(item["severity"] == "block" for item in blockers)

    if has_block:
        return "HOLD_FOR_HUMAN_REVIEW"

    if active["P09"]["active"] or active["P01"]["active"] or active["P04"]["active"]:
        return "RUN_MINIMAL_PILOT_ONLY"

    return "PREPARE_HUMAN_REVIEWABLE_PLAN"


def build_report(ctx: Context, source_path: Path) -> dict[str, Any]:
    active = activate_principles(ctx)
    blockers = hard_gates(ctx, active)
    routes = route_edges(active)
    actions = recommended_actions(ctx, active)
    scores = score(ctx, active, blockers)

    return {
        "report_version": 1,
        "generated_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "engine": "OpenRoot Permaculture Router v0.1.0",
        "mode": "read-only decision support",
        "source_context": str(source_path),
        "context": {
            "name": ctx.name,
            "description": ctx.description,
            "context_kind": ctx.context_kind,
            "evidence_level": ctx.evidence_level,
            "evidence_label": EVIDENCE_LABELS[ctx.evidence_level],
            "risk_level": ctx.risk_level,
            "claimed_outputs": list(ctx.claimed_outputs),
            "evidence_artifacts": list(ctx.evidence_artifacts),
            "tags": list(ctx.tags),
        },
        "decision": decision(blockers, active),
        "governance": {
            "human_approval_required": True,
            "automatic_execution_permitted": False,
            "automatic_evidence_promotion_permitted": False,
            "automatic_git_mutation_permitted": False,
            "automatic_release_permitted": False,
        },
        "active_principles": active,
        "active_routes": routes,
        "gates": blockers,
        "recommended_actions": actions,
        "scores": scores,
        "invariants": [
            "Evidence level may not be promoted by this router.",
            "CI validation does not establish physical performance or safety.",
            "L0/L1 contexts must not be presented as documented physical validation.",
            "High-risk or irreversible actions require explicit human review.",
            "Runtime state must not be automatically committed or released.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate an OpenRoot permaculture routing context."
    )
    parser.add_argument(
        "context",
        type=Path,
        help="Path to a JSON routing context."
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON report path. Parent directories are created."
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Emit compact JSON rather than pretty JSON."
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        ctx = load_context(args.context)
        report = build_report(ctx, args.context)
    except ValueError as exc:
        print(f"permaculture_router: error: {exc}", file=sys.stderr)
        return 2

    rendered = json.dumps(
        report,
        indent=None if args.compact else 2,
        sort_keys=True,
        ensure_ascii=False,
    )
    rendered += "\n"

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote router report: {args.output}")
    else:
        sys.stdout.write(rendered)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
