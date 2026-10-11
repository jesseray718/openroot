#!/usr/bin/env python3
"""
Test 6^6 hierarchy with phone's OpenRoot task data
"""

import json
import os
import glob
import time

# ============================================================
# THE 6 STEPS (atomic functions)
# ============================================================

def step_observe(data):
    return {"observed": data}

def step_collect(data):
    if isinstance(data, dict) and "observed" in data:
        obs = data["observed"]
        collected = {}
        for key, val in obs.items():
            collected[key] = val
        return {"collected": collected}
    return {"collected": data}

def step_apply(data):
    collected = data.get("collected", {})
    candidates = []
    
    # Look for tasks array or single task object
    tasks = collected.get("tasks", [])
    if not tasks and isinstance(collected, dict) and "result" in collected:
        tasks = [{"name": collected.get("name", "single_task"), "result": collected.get("result", 100), "human_input": collected.get("human_input", 1)}]
    
    if not tasks:
        tasks = [{"name": "default_task", "result": 100, "human_input": 1}]
    
    for item in tasks:
        if isinstance(item, dict):
            result = item.get("result", 100)
            human_input = item.get("human_input", 1)
            efficiency = result / human_input if human_input > 0 else 0
            candidates.append({"task": item.get("name", "unnamed"), "result": result, "human_input": human_input, "efficiency": efficiency})
    
    return {"applied": candidates}

def step_evaluate(data):
    candidates = data.get("applied", [])
    ranked = sorted(candidates, key=lambda x: x["efficiency"], reverse=True)
    return {"evaluated": ranked, "count": len(ranked)}

def step_calculate(data):
    evaluated = data.get("evaluated", [])
    winner = evaluated[0] if evaluated else {"task": None, "efficiency": 0, "result": 0, "human_input": 0}
    return {"calculated": {"best_efficiency": winner["efficiency"], "winner": winner["task"], "result": winner.get("result", 0), "human_input": winner.get("human_input", 0), "total": len(evaluated)}}

def step_respond(data):
    calc = data.get("calculated", {})
    return {"response": {"highest_efficiency_task": calc.get("winner"), "efficiency_per_human_unit": calc.get("best_efficiency", 0), "result_generated": calc.get("result", 0), "human_joules_spent": calc.get("human_input", 0), "recommendation": f"Task '{calc.get('winner')}' gives {calc.get('best_efficiency', 0):.2f}x return per human input"}}

STEPS = [step_observe, step_collect, step_apply, step_evaluate, step_calculate, step_respond]

# ============================================================
# HIERARCHY EXECUTION
# ============================================================

def run_tier(inp, team_size, tier_num):
    data = inp
    for step_func in STEPS:
        data = step_func(data)
    if team_size > 1 and "response" in data:
        data["response"]["team_bonus"] = team_size
        data["response"]["efficiency_scaled"] = data["response"].get("efficiency_per_human_unit", 0) * team_size
        data["response"]["atoms_used"] = team_size * 6
    return data

def main():
    print("="*70)
    print("AGAPE UNE: Phone Task Data Test -> 6^6 = 46,656 atoms")
    print("="*70)
    
    # Load task data from phone
    task_dir = "/data/data/com.termux/files/home/.projects/openroot/computational_flow/tasks"
    json_files = glob.glob(f"{task_dir}/*.json")
    
    if not json_files:
        print(f"\nNo JSON files found in {task_dir}")
        print("Creating sample tasks...")
        inp = {"tasks": [
            {"name": "data_analysis", "result": 500, "human_input": 10},
            {"name": "code_generation", "result": 800, "human_input": 20},
            {"name": "network_routing", "result": 1200, "human_input": 5},
            {"name": "encryption_verify", "result": 400, "human_input": 2}
        ]}
    else:
        print(f"\nLoading {len(json_files)} task files from {task_dir}")
        all_tasks = []
        
        for fpath in json_files[:10]:  # Load first 10 files
            try:
                with open(fpath, 'r') as f:
                    content = json.load(f)
                    if isinstance(content, dict):
                        if "tasks" in content:
                            all_tasks.extend(content["tasks"])
                        else:
                            all_tasks.append(content)
            except Exception as e:
                print(f"Warning: Could not read {fpath}: {e}")
        
        inp = {"tasks": all_tasks[:20]}  # Use up to 20 tasks
    
    print(f"\nLoaded {len(inp.get('tasks', []))} tasks")
    for t in inp["tasks"][:5]:
        print(f"  - {t.get('name', 'unnamed')}: result={t.get('result', 0)}, input={t.get('human_input', 0)}")
    if len(inp["tasks"]) > 5:
        print(f"  ... and {len(inp['tasks'])-5} more")
    
    tiers = [(0, 1, "6^1=6"), (1, 6, "6^2=36"), (2, 36, "6^3=216"), (3, 216, "6^4=1,296"), (4, 1296, "6^5=7,776"), (5, 7776, "6^6=46,656")]
    
    results = {}
    for tier_num, team_size, formula in tiers:
        start = time.time()
        data = run_tier(inp, team_size, tier_num)
        elapsed = time.time() - start
        
        resp = data.get("response", data.get("calculated", {}))
        eff = resp.get("efficiency_scaled") or resp.get("efficiency_per_human_unit", 0) * team_size
        
        winner = resp.get("highest_efficiency_task") or resp.get("winner", "None")
        print(f"Tier {tier_num}: {formula:<14} | Atoms: {6*team_size:>7,} | Time: {elapsed:.4f}s | Eff: {eff:.2f} | Best: {winner}")
        results[tier_num] = data
    
    print("\n" + "="*70)
    final = results[5].get("response", results[5].get("calculated", {}))
    print(f"🏆 HIGHEST EFFICIENCY TASK: {final.get('highest_efficiency_task', final.get('winner', 'None'))}")
    print(f"⚡ EFFICIENCY PER HUMAN UNIT: {final.get('efficiency_scaled', final.get('best_efficiency', 0)):.2f}")
    print(f"📊 RESULT GENERATED: {final.get('result_generated', final.get('result', 'None'))}")
    print(f"💪 HUMAN JOULES SPENT: {final.get('human_joules_spent', final.get('human_input', 'None'))}")
    print(f"🔢 ATOMS ACTING AS ONE: 46,656")
    print(f"💬 RECOMMENDATION: {final.get('recommendation', 'See above')}")
    print("="*70)

if __name__ == "__main__":
    main()
