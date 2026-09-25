#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
compute_marketplace.py v2 - Fixed version with proper Ollama handling
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

BASE = Path("/home/jesse/openroot")
COST_LEDGER = BASE / "data" / "cost_ledger.jsonl"
ORCHESTRATOR_LOG = BASE / "data" / "orchestrator_decisions.jsonl"

PROVIDERS = {
    "local_7b": {
        "provider": "ollama",
        "endpoint": "http://localhost:11434/api/generate",
        "model": "qwen2.5-coder:7b",
        "cost_per_k": 0.00,
        "capabilities": ["coding", "theorems", "debugging", "scripts", "generation"]
    },
    "local_3b": {
        "provider": "ollama",
        "endpoint": "http://localhost:11434/api/generate",
        "model": "qwen2.5:3b",
        "cost_per_k": 0.00,
        "capabilities": ["grading", "evaluation", "validation", "checks", "ranking"]
    }
}

def classify_task(query):
    """Route query to optimal provider"""
    query_lower = query.lower()
    
    if any(kw in query_lower for kw in ["code", "python", "theorem", "prove", "debug", "script", "write", "generate", "design"]):
        return ["local_7b", "local_3b"]
    
    if any(kw in query_lower for kw in ["grade", "eval", "check", "review", "audit", "validate", "rate"]):
        return ["local_3b", "local_7b"]
    
    return ["local_7b", "local_3b"]

def invoke_local(provider_key, query, max_tokens=500):
    """Call Ollama provider"""
    provider = PROVIDERS[provider_key]
    import time
    start = time.time()
    
    payload = {
        "model": provider["model"],
        "prompt": query,
        "stream": False,
        "options": {"num_predict": max_tokens, "temperature": 0.7}
    }
    
    result = subprocess.run(
        ["curl", "-s", "-X", "POST", provider["endpoint"], "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
        capture_output=True, text=True
    )
    
    duration = time.time() - start
    
    try:
        resp = json.loads(result.stdout)
        response = resp.get("response", "No response")
        return response, 0.00, duration * 1000
    except:
        return f"Error: {result.stderr}", 0.00, duration * 1000

def loop_until_complete(task_query, max_iterations=5):
    """Iterate through providers until we get usable output"""
    results = []
    preferred_providers = classify_task(task_query)
    
    print(f"\nTask classification: Routing to {preferred_providers}")
    print(f"Query: {task_query[:150]}...\n")
    
    for iteration in range(max_iterations):
        print(f"=== ITERATION {iteration + 1} ===")
        
        for provider_key in preferred_providers:
            response, cost, latency = invoke_local(provider_key, task_query)
            
            result = {
                "iteration": iteration + 1,
                "provider": provider_key,
                "query": task_query,
                "response": response,
                "cost": cost,
                "latency_ms": round(latency, 2),
                "timestamp": datetime.now().isoformat()
            }
            results.append(result)
            
            print(f"  {provider_key}: {latency:.0f}ms, cost ${cost:.4f}")
            
            # Save to ledger
            with open(COST_LEDGER, "a") as f:
                f.write(json.dumps(result) + "\n")
    
    return results

def main():
    print("=" * 60)
    print("COMPUTE MARKETPLACE ORCHESTRATOR v2")
    print("=" * 60)
    
    if len(__import__('sys').argv) < 2:
        print("Usage: compute_marketplace_v2.py '<query>'")
        print("Examples:")
        print("  compute_marketplace_v2.py 'Write Python script to parse JSONL files'")
        print("  compute_marketplace_v2.py 'Design GitHub profile landing page HTML/CSS'")
        print("  compute_marketplace_v2.py 'Audit my OpenRoot repository structure'")
        return
    
    query = " ".join(__import__('sys').argv[1:])
    
    results = loop_until_complete(query)
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    for i, r in enumerate(results, 1):
        print(f"\n--- Result {i} ({r['provider']}) ---")
        print(f"Latency: {r['latency_ms']:.0f}ms")
        print(f"Output ({len(r['response'])} chars):")
        print(r['response'][:500])
        if len(r['response']) > 500:
            print("... [truncated]")
    
    # Save full results
    result_file = BASE / f"data/orchestrator/results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    result_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(result_file, "w") as f:
        json.dump({"query": query, "results": results}, f, indent=2)
    
    print(f"\nFull results saved: {result_file}")
    print(f"Cost ledger updated: {COST_LEDGER}")

if __name__ == "__main__":
    main()
