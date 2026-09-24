#!/usr/bin/env python3
"""
smart_router.py - FIXED VERSION
Assign tasks to optimal model (7B, 3B, or Lumo)
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

BASE = Path("/home/jesse/openroot")
ROUTE_LOG = BASE / "data" / "router_decisions.jsonl"

MODELS = {
    "local_7b": {"provider": "ollama", "endpoint": "http://localhost:11434/api/generate", "model": "qwen2.5-coder:7b"},
    "local_3b": {"provider": "ollama", "endpoint": "http://localhost:11434/api/generate", "model": "qwen2.5:3b"},
    "lumo": {"provider": "lumo_inbox", "endpoint": "/lumo_inbox", "model": "external"}
}

def classify_query(query):
    """Route decision heuristic"""
    query_lower = query.lower()
    
    if any(kw in query_lower for kw in ["code", "python", "theorem", "prove", "debug", "script"]):
        return "local_7b", "Complex reasoning/coding"
    
    if any(kw in query_lower for kw in ["grade", "eval", "check", "review", "validate"]):
        return "local_3b", "Fast evaluation"
    
    if any(kw in query_lower for kw in ["analyze", "design", "create", "plan", "strategy", "ethics"]):
        return "lumo", "Human-expert judgment"
    
    return "local_3b", "Default quick response"

def route_query(query, context=None):
    model, reason = classify_query(query)
    
    decision = {
        "ts": datetime.now().isoformat(),
        "query": query[:200],
        "model": model,
        "reason": reason,
        "context": context or {}
    }
    
    with open(ROUTE_LOG, "a") as f:
        f.write(json.dumps(decision) + "\n")
    
    return decision

def invoke_model(model_key, query, context=None, max_tokens=500):
    """FIXED: Added context parameter"""
    model = MODELS[model_key]
    
    if model["provider"] == "ollama":
        payload = {
            "model": model["model"],
            "prompt": query,
            "stream": False,
            "options": {"num_predict": max_tokens}
        }
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", model["endpoint"], "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
            capture_output=True, text=True
        )
        try:
            resp = json.loads(result.stdout)
            return resp.get("response", "No response")
        except:
            return f"Error: {result.stderr}"
    
    elif model["provider"] == "lumo_inbox":
        # FIXED: Pass context properly
        from lumo_bridge import send_to_lumo
        hash_id = send_to_lumo("routing", query, context or {})
        return f"Queued to Lumo (ID: {hash_id})"
    
    return "Unknown model provider"

def main():
    print("=== SMART ROUTER ===")
    print(f"Models: {list(MODELS.keys())}")
    
    if len(__import__('sys').argv) < 2:
        print("Usage: smart_router.py '<query>'")
        return
    
    query = " ".join(__import__('sys').argv[1:])
    
    print(f"\nQuery: {query[:100]}...")
    decision = route_query(query)
    
    print(f"Route to: {decision['model']} ({decision['reason']})")
    
    result = invoke_model(decision['model'], query, decision.get('context'))
    
    print(f"\nResult: {result[:300]}..." if len(result) > 300 else f"\nResult: {result}")

if __name__ == "__main__":
    main()
