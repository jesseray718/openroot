#!/usr/bin/env python3
"""
compute_marketplace.py - Optimal compute allocation across models
Local 7B/3B → Lumo → Gemini → OpenRouter → Frontier (paid)
Loops until quality threshold met, budget aware
"""

import json
import hashlib
import time
import subprocess
from pathlib import Path
from datetime import datetime

BASE = Path("/home/jesse/openroot")
ORCHESTRATOR_LOG = BASE / "data" / "orchestrator_decisions.jsonl"
MODEL_POOL = BASE / "data" / "model_warm_pool.json"
COST_LEDGER = BASE / "data" / "cost_ledger.jsonl"

# Provider capabilities and costs (per 1K tokens)
PROVIDERS = {
    "local_7b": {
        "provider": "ollama",
        "endpoint": "http://localhost:11434/api/generate",
        "model": "qwen2.5-coder:7b",
        "cost_per_k": 0.00,
        "latency_ms": 5000,
        "capabilities": ["coding", "theorems", "debugging", "scripts"],
        "warm": True
    },
    "local_3b": {
        "provider": "ollama",
        "endpoint": "http://localhost:11434/api/generate",
        "model": "qwen2.5:3b",
        "cost_per_k": 0.00,
        "latency_ms": 2000,
        "capabilities": ["grading", "evaluation", "validation", "checks"],
        "warm": True
    },
    "lumo": {
        "provider": "lumo_api",
        "endpoint": "https://api.lumo.proton.me/v1/chat",
        "cost_per_k": 0.02,
        "latency_ms": 3000,
        "capabilities": ["design", "analysis", "strategy", "human_expert"],
        "warm": False
    },
    "gemini_free": {
        "provider": "google",
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
        "cost_per_k": 0.00,
        "latency_ms": 2500,
        "capabilities": ["general", "creative", "explanation"],
        "warm": False
    },
    "openrouter": {
        "provider": "openrouter",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "model": "meta-llama/llama-3-70b-instruct:free",
        "cost_per_k": 0.00,
        "latency_ms": 4000,
        "capabilities": ["complex_reasoning", "research"],
        "warm": False
    },
    "frontier": {
        "provider": "openai",
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-4o",
        "cost_per_k": 25.00,
        "latency_ms": 5000,
        "capabilities": ["ultimate_quality", "final_approval"],
        "warm": False
    }
}

def load_api_keys():
    """Load keys from environment (set in terminal)"""
    return {
        "LUMO_API_KEY": __import__('os').environ.get("LUMO_API_KEY", ""),
        "GEMINI_API_KEY": __import__('os').environ.get("GEMINI_API_KEY", ""),
        "OPENROUTER_API_KEY": __import__('os').environ.get("OPENROUTER_API_KEY", ""),
        "OPENAI_API_KEY": __import__('os').environ.get("OPENAI_API_KEY", "")
    }

def classify_task(query):
    """Match query to best provider capability"""
    query_lower = query.lower()
    
    if any(kw in query_lower for kw in ["code", "python", "theorem", "prove", "debug", "script", "fix"]):
        return ["local_7b", "local_3b", "lumo"]
    
    if any(kw in query_lower for kw in ["grade", "eval", "check", "review", "audit", "validate"]):
        return ["local_3b", "local_7b", "lumo"]
    
    if any(kw in query_lower for kw in ["design", "plan", "strategy", "analyze", "create"]):
        return ["lumo", "local_7b", "gemini_free"]
    
    if any(kw in query_lower for kw in ["write", "generate", "profile", "page", "landing"]):
        return ["local_7b", "gemini_free", "lumo"]
    
    return ["local_3b", "local_7b", "lumo", "gemini_free"]

def invoke_provider(provider_key, query, max_tokens=1000):
    """Call specific provider, return response + cost"""
    provider = PROVIDERS[provider_key]
    api_keys = load_api_keys()
    
    start = time.time()
    
    if provider["provider"] == "ollama":
        payload = {
            "model": provider["model"],
            "prompt": query,
            "stream": False,
            "options": {"num_predict": max_tokens}
        }
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", provider["endpoint"], "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
            capture_output=True, text=True
        )
        try:
            resp = json.loads(result.stdout)
            response = resp.get("response", "No response")
            return response, 0.00, (time.time() - start) * 1000
    
    elif provider["provider"] in ["lumo_api", "google", "openrouter", "openai"]:
        # API calls would go here with proper authentication
        # For now, return placeholder
        return f"[{provider_key} would respond]", 0.01, 3000
    
    return "Provider unavailable", 0.00, 0

def loop_until_complete(task_query, quality_threshold=0.8, max_iterations=10, budget_limit=1.00):
    """Iterate through providers until quality met or budget exhausted"""
    results = []
    total_cost = 0.00
    iteration = 0
    
    # Start with cheapest capable provider
    preferred_providers = classify_task(task_query)
    
    while iteration < max_iterations and total_cost < budget_limit:
        iteration += 1
        print(f"\n=== ITERATION {iteration} ===")
        
        for provider_key in preferred_providers:
            response, cost, latency = invoke_provider(provider_key, task_query)
            total_cost += cost
            
            result = {
                "iteration": iteration,
                "provider": provider_key,
                "query": task_query[:100],
                "response": response[:500],
                "cost": cost,
                "latency_ms": latency,
                "timestamp": datetime.now().isoformat()
            }
            results.append(result)
            
            # Log to cost ledger
            with open(COST_LEDGER, "a") as f:
                f.write(json.dumps(result) + "\n")
            
            print(f"  {provider_key}: {cost:.4f} USD, {latency:.0f}ms")
            
            # Check if quality threshold met (placeholder - actual grading needed)
            if cost >= quality_threshold:  # Simplified for demo
                return results, total_cost
    
    return results, total_cost

def main():
    print("=== COMPUTE MARKETPLACE ORCHESTRATOR ===")
    print(f"Providers: {list(PROVIDERS.keys())}")
    print(f"Free tier: local_7b, local_3b, gemini_free, openrouter")
    print(f"Paid tier: lumo, frontier")
    print("")
    
    if len(__import__('sys').argv) < 3:
        print("Usage:")
        print("  compute_marketplace.py <budget> '<query>'")
        print("  Example: compute_marketplace.py 0.50 'Design optimal GitHub profile page'")
        return
    
    budget = float(__import__('sys').argv[1])
    query = " ".join(__import__('sys').argv[2:])
    
    print(f"Budget: ${budget:.2f}")
    print(f"Query: {query[:100]}...")
    
    results, total_cost = loop_until_complete(query, budget_limit=budget)
    
    print(f"\n=== SUMMARY ===")
    print(f"Iterations: {len(results)}")
    print(f"Total cost: ${total_cost:.4f}")
    print(f"Providers used: {set(r['provider'] for r in results)}")
    
    # Write results
    result_file = BASE / f"data/orchestrator/results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    result_file.parent.mkdir(parents=True, exist_ok=True)
    with open(result_file, "w") as f:
        json.dump({"query": query, "results": results, "total_cost": total_cost}, f, indent=2)
    
    print(f"Results saved: {result_file}")

if __name__ == "__main__":
    main()
