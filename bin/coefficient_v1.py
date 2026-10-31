# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""OpenRoot Coefficient Calculator v1 - verified_performance / cost_of_interaction."""
import argparse, json, sys, time

def coefficient(verified_quality_score, task_value_usd, cloud_cost_usd, latency_s, local_cost_per_s=0.001):
    """Returns the coefficient and breakdown."""
    opportunity_cost_usd = latency_s * local_cost_per_s
    total_cost = cloud_cost_usd + opportunity_cost_usd
    if total_cost == 0:
        return {"coefficient": float("inf") if verified_quality_score * task_value_usd > 0 else 0,
                "breakdown": {"verified_quality_score": verified_quality_score,
                              "task_value_usd": task_value_usd,
                              "cloud_cost_usd": cloud_cost_usd,
                              "opportunity_cost_usd": 0,
                              "total_cost": 0}}
    coeff = (verified_quality_score * task_value_usd) / total_cost
    return {"coefficient": coeff,
            "breakdown": {"verified_quality_score": verified_quality_score,
                          "task_value_usd": task_value_usd,
                          "cloud_cost_usd": cloud_cost_usd,
                          "opportunity_cost_usd": opportunity_cost_usd,
                          "total_cost": total_cost}}

def main():
    p = argparse.ArgumentParser(description="OpenRoot Coefficient Calculator v1")
    p.add_argument("--quality", type=float, required=True, help="verified_quality_score 0.0-1.0")
    p.add_argument("--value", type=float, required=True, help="task_value_usd")
    p.add_argument("--cost", type=float, required=True, help="cloud_cost_usd")
    p.add_argument("--latency", type=float, required=True, help="latency in seconds")
    args = p.parse_args()
    r = coefficient(args.quality, args.value, args.cost, args.latency)
    print(json.dumps(r, indent=2))

if __name__ == "__main__":
    main()
