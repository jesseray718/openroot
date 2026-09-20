#!/usr/bin/env python3
"""light_cone_router.py — Route tasks to optimal model by complexity score"""
import sys, json, math
from datetime import datetime

MODELS = {
    "lite": {"threshold": 0.3, "name": "qwen2.5:3b", "cost": 0.01},
    "coder": {"threshold": 0.7, "name": "qwen2.5-coder:7b", "cost": 0.05},
    "max": {"threshold": 1.0, "name": "qwen2.5-coder:7b-max", "cost": 0.10}
}

def estimate_complexity(text: str) -> float:
    tokens = len(text.split())
    keywords = ["theorem", "proof", "cryptographic", "blockchain", "zero-knowledge"]
    kw_score = sum(1 for k in keywords if k in text.lower()) / len(keywords)
    return min(1.0, (tokens / 1000) * 0.5 + kw_score * 0.5)

def route(task: str):
    score = estimate_complexity(task)
    route = next((m["name"] for m in MODELS.values() if score <= m["threshold"]), MODELS["max"]["name"])
    return {"score": round(score, 3), "route": route, "complexity": "high" if score > 0.7 else ("medium" if score > 0.3 else "low")}

if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else "sample task"
    result = route(task)
    print(json.dumps(result, indent=2))
