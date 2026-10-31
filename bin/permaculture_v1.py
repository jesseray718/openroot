# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""OpenRoot Permaculture Encoder v1 - 12 principles as algorithmic fitness functions."""
import argparse, json, sys

PERMACULTURE_PRINCIPLES = {
    1: {"name": "Observe and interact",
        "algorithmic_form": "passive_monitoring_days >= 30 before any mutation",
        "metric": "observation_to_action_ratio",
        "applies_to": ["system_design","pod_creation","mesh_deployment"]},
    2: {"name": "Catch and store energy",
        "algorithmic_form": "stored_joules >= captured_joules * 0.5",
        "metric": "storage_efficiency",
        "applies_to": ["thermal_cascade","mesh_nodes","batteries"]},
    3: {"name": "Obtain a yield",
        "algorithmic_form": "output_value >= input_cost * 1.5",
        "metric": "roi_ratio",
        "applies_to": ["every_receipt","every_worker_action"]},
    4: {"name": "Apply self-regulation and accept feedback",
        "algorithmic_form": "if scar_count >= 3 for class X, auto_disable(X)",
        "metric": "scar_density_per_class",
        "applies_to": ["court_v6","mistake_compost","worker_layer"]},
    5: {"name": "Use and value renewable resources and services",
        "algorithmic_form": "renewable_joules / total_joules >= 0.8",
        "metric": "renewable_fraction",
        "applies_to": ["energy_receipts","hardware_sourcing"]},
    6: {"name": "Produce no waste",
        "algorithmic_form": "compost_rate >= 0.95",
        "metric": "compost_efficiency",
        "applies_to": ["mistake_log","e_scrap_recycling","food_waste"]},
    7: {"name": "Design from patterns to details",
        "algorithmic_form": "schema_first, then implementation",
        "metric": "schema_to_impl_drift",
        "applies_to": ["receipt_spec","pod_schema","mesh_protocol"]},
    8: {"name": "Integrate rather than segregate",
        "algorithmic_form": "cross_zone_proposals_per_beat >= 1",
        "metric": "integration_density",
        "applies_to": ["expert_mesh","worker_layer","federation"]},
    9: {"name": "Use small and slow solutions",
        "algorithmic_form": "if small_model_works, never_use_large_model",
        "metric": "model_size_vs_task_complexity",
        "applies_to": ["model_routing","worker_autonomy_levels"]},
    10: {"name": "Use and value diversity",
         "algorithmic_form": "unique_pods >= 5, unique_models >= 3, unique_providers >= 2",
         "metric": "diversity_index",
         "applies_to": ["pod_garden","model_fleet","cloud_router"]},
    11: {"name": "Use edges and value the marginal",
         "algorithmic_form": "edge_nodes_count >= core_nodes_count",
         "metric": "edge_to_core_ratio",
         "applies_to": ["mesh_topology","hardware_sourcing","rural_access"]},
    12: {"name": "Creatively use and respond to change",
         "algorithmic_form": "schema_version_supports_migrations AND scars_drive_improvements",
         "metric": "adaptation_rate",
         "applies_to": ["receipt_schema","pod_schema","mesh_protocol"]},
}

def evaluate(system_state):
    """Evaluate system state against all 12 principles. Returns scores 0.0-1.0."""
    results = {}
    for pid, p in PERMACULTURE_PRINCIPLES.items():
        metric = p["metric"]
        score = system_state.get(metric, 0.0)
        if not isinstance(score, (int, float)):
            score = 0.0
        score = max(0.0, min(1.0, float(score)))
        results[pid] = {"name": p["name"], "metric": metric, "score": score}
    aggregate = sum(r["score"] for r in results.values()) / 12
    return {"principles": results, "aggregate_score": aggregate}

def main():
    p = argparse.ArgumentParser(description="OpenRoot Permaculture Encoder v1")
    p.add_argument("--state", help="JSON file with system state metrics")
    args = p.parse_args()
    
    if args.state:
        state = json.loads(open(args.state).read())
    else:
        # Example state for demo
        state = {
            "observation_to_action_ratio": 0.8,
            "storage_efficiency": 0.6,
            "roi_ratio": 1.8,
            "scar_density_per_class": 0.7,
            "renewable_fraction": 0.9,
            "compost_efficiency": 0.95,
            "schema_to_impl_drift": 0.9,
            "integration_density": 0.6,
            "model_size_vs_task_complexity": 0.8,
            "diversity_index": 0.7,
            "edge_to_core_ratio": 0.5,
            "adaptation_rate": 0.85,
        }
    
    r = evaluate(state)
    print(json.dumps(r, indent=2))

if __name__ == "__main__":
    main()
