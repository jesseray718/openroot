# SPDX-License-Identifier: Apache-2.0
"""Deterministic proposal evaluator and cache; not a deployment controller."""
import argparse
import hashlib
import json
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

VERSION = "need-outcome/0.1"


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False,
    )


def sha(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def number(value):
    return (
        type(value) in (int, float)
        and math.isfinite(value)
    )


def require(condition, message):
    if not condition:
        raise ValueError(message)


def evaluate(request):
    require(isinstance(request, dict), "request must be an object")
    for key in ("need_id", "context_id", "policy_id", "access_scope"):
        require(
            isinstance(request.get(key), str) and bool(request[key]),
            f"{key} must be a nonempty string",
        )
    require(
        isinstance(request.get("freshness"), dict)
        and bool(request["freshness"]),
        "freshness must identify the input/corpus/policy generations",
    )
    policy = request.get("policy")
    require(isinstance(policy, dict), "policy must be an object")
    gates = policy.get("required_gates")
    criteria = policy.get("criteria")
    require(
        isinstance(gates, list) and bool(gates)
        and all(isinstance(g, str) and g for g in gates)
        and len(set(gates)) == len(gates),
        "required_gates must contain unique names",
    )
    require(
        isinstance(criteria, dict) and bool(criteria)
        and all(isinstance(k, str) and k for k in criteria)
        and all(v in ("min", "max") for v in criteria.values()),
        "criteria maps names to min or max",
    )
    pathways = request.get("pathways")
    require(
        isinstance(pathways, list) and bool(pathways),
        "pathways must be a nonempty list",
    )

    results = []
    ids = set()
    for pathway in pathways:
        require(isinstance(pathway, dict), "pathway must be an object")
        identity = pathway.get("id")
        require(
            isinstance(identity, str) and identity and identity not in ids,
            "pathway IDs must be nonempty and unique",
        )
        ids.add(identity)
        checks = pathway.get("gates", {})
        measures = pathway.get("measures", {})
        require(
            isinstance(checks, dict) and isinstance(measures, dict),
            "gates and measures must be objects",
        )
        failures, missing = [], []
        for name in gates:
            value = checks.get(name)
            require(
                value is None or type(value) is bool,
                f"gate {name} must be true, false, or null",
            )
            if value is False:
                failures.append(name)
            elif value is None:
                missing.append("gate:" + name)

        values = {}
        for name in criteria:
            measurement = measures.get(name)
            if measurement is None:
                missing.append("measure:" + name)
                continue
            require(
                isinstance(measurement, dict),
                f"measurement {name} must be an object",
            )
            value = measurement.get("value")
            refs = measurement.get("evidence_refs")
            comparable = measurement.get("comparison_basis")
            if (
                not number(value)
                or not isinstance(refs, list)
                or not refs
                or not all(isinstance(ref, str) and ref for ref in refs)
                or not isinstance(comparable, str)
                or not comparable
            ):
                missing.append("measure:" + name)
                continue
            values[name] = {
                "value": value,
                "comparison_basis": comparable,
                "evidence_refs": sorted(set(refs)),
            }

        state = "EXCLUDE" if failures else "HOLD" if missing else "PASS"
        results.append({
            "id": identity, "state": state,
            "failed_gates": failures, "missing": missing,
            "measures": values,
            "route": (
                "requirement-review" if failures else
                "evidence-or-authorization-needed" if missing else
                "eligible-for-comparison"
            ),
        })

    eligible = [p for p in results if p["state"] == "PASS"]
    bases = {
        name: {p["measures"][name]["comparison_basis"] for p in eligible}
        for name in criteria
    }
    comparable = all(len(b) <= 1 for b in bases.values())

    def dominates(a, b):
        differences = [
            (a["measures"][k]["value"] - b["measures"][k]["value"])
            * (1 if direction == "max" else -1)
            for k, direction in criteria.items()
        ]
        return all(d >= 0 for d in differences) and any(
            d > 0 for d in differences
        )

    frontier = (
        [
            p["id"] for p in eligible
            if not any(dominates(other, p) for other in eligible)
        ]
        if comparable else []
    )
    return {
        "engine": VERSION,
        "request_sha256": sha(request),
        "need_id": request["need_id"],
        "context_id": request["context_id"],
        "policy_id": request["policy_id"],
        "assessments": results,
        "comparison_state": (
            "NO_ELIGIBLE_OPTIONS" if not eligible else
            "COMPARABLE" if comparable else "HOLD"
        ),
        "frontier": frontier,
        "interventions": (
            ["resolve-incompatible-measurement-bases"] if not comparable else []
        ),
        "limits": [
            "Gate decisions and evidence validity are supplied, not independently verified.",
            "Comparison covers supplied alternatives and point estimates only.",
            "A PASS is eligibility under supplied policy, not deployment authorization.",
            "No pathway is automatically executed.",
        ],
    }


def plan_chain(nodes):
    require(isinstance(nodes, list) and bool(nodes), "nodes must be nonempty")
    mapping = {}
    for node in nodes:
        require(isinstance(node, dict), "node must be an object")
        identity = node.get("id")
        require(
            isinstance(identity, str) and identity and identity not in mapping,
            "node IDs must be unique",
        )
        require(
            isinstance(node.get("worker"), str) and bool(node["worker"]),
            "worker name required",
        )
        deps = node.get("depends_on", [])
        require(
            isinstance(deps, list)
            and all(isinstance(d, str) for d in deps)
            and len(set(deps)) == len(deps),
            "depends_on must be a list of unique IDs",
        )
        require(
            type(node.get("approval_required", False)) is bool,
            "approval_required must be boolean",
        )
        mapping[identity] = node

    for node in nodes:
        require(
            all(d in mapping for d in node.get("depends_on", [])),
            "unknown dependency",
        )
    pending = set(mapping)
    completed, order, routes = set(), [], {}
    while pending:
        ready = sorted(
            key for key in pending
            if set(mapping[key].get("depends_on", [])) <= completed
        )
        require(bool(ready), "dependency cycle detected")
        for key in ready:
            node = mapping[key]
            route = (
                "approval-required" if node.get("approval_required", False)
                else "blocked-by-intervention"
                if any(
                    routes[d] != "ready-after-dependencies"
                    for d in node.get("depends_on", [])
                )
                else "ready-after-dependencies"
            )
            routes[key] = route
            order.append({
                "id": key, "worker": node["worker"], "route": route,
                "depends_on": node.get("depends_on", []),
            })
            completed.add(key)
            pending.remove(key)
    return {"chain_sha256": sha(nodes), "plan": order, "executed": False}


def cached_evaluate(db_path, request):
    implementation = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    key = sha({
        "implementation": implementation,
        "version": VERSION,
        "request": request,
    })
    db = sqlite3.connect(db_path, timeout=30)
    try:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS results(
            cache_key TEXT PRIMARY KEY,
            result_json TEXT NOT NULL,
            result_sha256 TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS receipts(
            sequence INTEGER PRIMARY KEY AUTOINCREMENT,
            cell_json TEXT NOT NULL
        );
        """)
        with db:
            row = db.execute(
                "SELECT result_json, result_sha256 FROM results WHERE cache_key=?",
                (key,),
            ).fetchone()
            if row:
                result = json.loads(row[0])
                require(sha(result) == row[1], "cached result integrity failure")
            else:
                result = evaluate(request)
                db.execute(
                    "INSERT OR IGNORE INTO results VALUES (?, ?, ?)",
                    (key, canonical(result), sha(result)),
                )
            receipt = {
                "engine": VERSION,
                "at": datetime.now(timezone.utc).isoformat(),
                "cache_key": key,
                "cache_hit": row is not None,
                "request_sha256": sha(request),
                "result_sha256": sha(result),
                "implementation_sha256": implementation,
                "freshness": request["freshness"],
                "freshness_verified": False,
            }
            db.execute(
                "INSERT INTO receipts(cell_json) VALUES (?)",
                (canonical(receipt),),
            )
        return {"receipt": receipt, "result": result}
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("evaluate", "plan"))
    parser.add_argument("input", type=Path)
    parser.add_argument("--db", type=Path)
    args = parser.parse_args()
    value = json.loads(args.input.read_text(encoding="utf-8"))
    if args.operation == "plan":
        output = plan_chain(value)
    elif args.db:
        output = cached_evaluate(args.db, value)
    else:
        output = evaluate(value)
    print(json.dumps(output, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
