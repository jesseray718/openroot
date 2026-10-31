#!/usr/bin/env python3
"""
Observe and Interact - Raised to 6^6

Tier 0: 6 atoms, each does 1 step         = 6 total
Tier 1: 6 atoms do each of 6 steps         = 36 total
Tier 2: 36 atoms do each of 6 steps        = 216 total
Tier 3: 216 atoms do each of 6 steps       = 1,296 total
Tier 4: 1,296 atoms do each of 6 steps      = 7,776 total
Tier 5: 7,776 atoms do each of 6 steps      = 46,656 total = 6^6
"""

import time

# ============================================================
# THE 6 STEPS (atomic functions)
# ============================================================

def step_observe(data):
    """Step 1: Observe/Analyze"""
    return {"observed": data}

def step_collect(data):
    """Step 2: Collect pertinent info"""
    if isinstance(data, dict):
        return {"collected": list(data.values())}
    return {"collected": [data]}

def step_apply(data):
    """Step 3: Apply"""
    vals = data.get("collected", [data]) if isinstance(data, dict) else [data]
    return {"applied": [str(v).upper() for v in vals]}

def step_evaluate(data):
    """Step 4: Evaluate"""
    vals = data.get("applied", [data]) if isinstance(data, dict) else [data]
    return {"evaluated": len(vals), "items": vals}

def step_calculate(data):
    """Step 5: Calculate"""
    count = data.get("evaluated", 1) if isinstance(data, dict) else 1
    return {"calculated": count * 2, "items": data.get("items", [])}

def step_respond(data):
    """Step 6: Respond"""
    calc = data.get("calculated", 0) if isinstance(data, dict) else 0
    items = data.get("items", []) if isinstance(data, dict) else [data]
    return {"response": " ".join(items), "score": calc}

STEPS = [step_observe, step_collect, step_apply, step_evaluate, step_calculate, step_respond]
STEP_NAMES = ["Observe", "Collect", "Apply", "Evaluate", "Calculate", "Respond"]

# ============================================================
# EXECUTE ONE PRINCIPLE (6 steps)
# ============================================================

def execute_principle(inp):
    """Run all 6 steps once, return final output"""
    data = inp
    for step_func in STEPS:
        data = step_func(data)
    return data

# ============================================================
# RAISE TO N^N
# ============================================================

def raise_tier(team_size, inp):
    """
    Each of the 6 steps is executed by the whole team.
    Team collects all outputs, passes combined result to next step.
    """
    data = inp
    
    for step_num, step_func in enumerate(STEPS):
        # Every atom in the team executes this step
        team_outputs = []
        for atom in range(team_size):
            result = step_func(data)
            team_outputs.append(result)
        
        # Combine all team outputs into one
        combined = {
            "team_size": team_size,
            "step": STEP_NAMES[step_num],
            "outputs": team_outputs,
            "combined": team_outputs[0]  # First output represents the team
        }
        data = combined
    
    return data

def run_full_hierarchy(inp):
    """Run all tiers from 6 to 6^6"""
    
    tiers = [
        (0, 1,      "6^1 = 6"),
        (1, 6,      "6^2 = 36"),
        (2, 36,     "6^3 = 216"),
        (3, 216,    "6^4 = 1,296"),
        (4, 1296,   "6^5 = 7,776"),
        (5, 7776,   "6^6 = 46,656"),
    ]
    
    print("INPUT:", inp)
    print("=" * 60)
    
    data = inp
    
    for tier_num, team_size, formula in tiers:
        start = time.time()
        
        if tier_num == 0:
            # Tier 0: just 6 atoms, 1 per step
            data = execute_principle(inp)
            atoms = 6
        else:
            # Each step executed by entire previous team
            data = raise_tier(team_size, data)
            atoms = 6 * team_size
        
        elapsed = time.time() - start
        
        print(f"Tier {tier_num}: {formula:<16} | "
              f"Atoms: {atoms:>7,} | "
              f"Time: {elapsed:.4f}s | "
              f"Output: {str(data)[:60]}...")
    
    print("=" * 60)
    print(f"FINAL: 6^6 = 46,656 atoms acted as ONE unit")
    print(f"Result: {data}")

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    run_full_hierarchy("what is the temperature")
