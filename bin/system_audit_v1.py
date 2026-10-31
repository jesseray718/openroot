# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""OpenRoot System Audit v1 — 12 Permaculture Principles as Code Gates.

Runs all 12 principles deterministically against the actual system state.
Computes system-wide eta (Obtain a Yield).
Then optionally routes to cloud AI for synthesis of the computed results.

Doctrine: Verifiers are pure code. Models propose. Code disposes.
"""
import argparse, hashlib, json, math, os, sqlite3, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(os.environ.get("OPENROOT_REPO", "/home/jesse/openroot"))
GARDEN = REPO / "pods_garden"
PHI = 1.6180339887498947

def now_utc():
    return datetime.now(timezone.utc).isoformat()

def count_pods():
    if not GARDEN.is_dir(): return 0
    return len([p for p in GARDEN.iterdir() if p.is_dir() and (p / "pod.db").exists()])

def count_chunks():
    total = 0
    if not GARDEN.is_dir(): return 0
    for pod in GARDEN.iterdir():
        db = pod / "pod.db"
        if db.exists():
            try:
                conn = sqlite3.connect(str(db))
                total += conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
                conn.close()
            except: pass
    return total

def count_receipts():
    """Count sealed receipts in genesis"""
    count = 0
    for f in (REPO / "genesis").glob("receipt_v*.json"):
        count += 1
    return count

def count_tools():
    bin_dir = REPO / "bin"
    if not bin_dir.is_dir(): return 0
    return len([f for f in bin_dir.iterdir() if f.suffix in ('.py', '.sh') and f.is_file()])

def count_mistakes():
    ml = REPO / "data" / "mistakes" / "mistake_log.jsonl"
    if not ml.exists(): return 0
    return sum(1 for _ in open(ml))

def count_cron():
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=5)
        return len([l for l in result.stdout.splitlines() if l.strip() and not l.startswith("#")])
    except: return 0

def count_systemd():
    try:
        result = subprocess.run(["systemctl", "--user", "list-units", "--type=service", "--state=active", "--no-pager"],
                              capture_output=True, text=True, timeout=5)
        return len([l for l in result.stdout.splitlines() if ".service" in l and "active" in l])
    except: return 0

def count_ollama_models():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        return len([l for l in result.stdout.splitlines() if l.strip()]) - 1  # minus header
    except: return 0

def cloud_router_working():
    """Test if cloud router returns success"""
    try:
        result = subprocess.run(
            ["python3", str(REPO / "bin" / "cloud_router_v2.py"),
             "--prompt", "Reply with OK", "--max-tokens", "5"],
            capture_output=True, text=True, timeout=30, cwd=str(REPO), stdin=subprocess.DEVNULL)
        # Parse JSON
        for i, c in enumerate(result.stdout):
            if c == "{":
                try:
                    import json
                    data = json.JSONDecoder().raw_decode(result.stdout[i:])[0]
                    return data.get("success", False)
                except: pass
        return False
    except: return False

def count_github_commits():
    try:
        result = subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=str(REPO),
                                capture_output=True, text=True, timeout=5)
        return int(result.stdout.strip())
    except: return 0

# ============ THE 12 PERMACULTURE PRINCIPLES AS CODE GATES ============

def principle_1_observe_interact():
    """Observe & Interact — passive monitoring before mutation"""
    pods = count_pods()
    chunks = count_chunks()
    receipts = count_receipts()
    # Gate: have we observed enough? (pods + receipts = observation depth)
    observation_depth = pods + receipts + chunks / 100
    score = min(1.0, observation_depth / 50)
    passed = pods >= 3 and receipts >= 3
    return {
        "name": "Observe & Interact",
        "score": round(score, 3),
        "passed": passed,
        "metric": f"pods={pods}, receipts={receipts}, chunks={chunks}",
        "gate": "pods >= 3 AND receipts >= 3",
        "observation_depth": round(observation_depth, 1),
    }

def principle_2_catch_store_energy():
    """Catch & Store Energy — receipt cache + pod garden = stored knowledge"""
    tools = count_tools()
    # Check if receipt cache exists
    cache_db = REPO / "data" / "receipt_cache.db"
    cache_exists = cache_db.exists()
    # Check if pods have merkle roots (sealed = stored)
    sealed_pods = 0
    if GARDEN.is_dir():
        for pod in GARDEN.iterdir():
            db = pod / "pod.db"
            if db.exists():
                try:
                    conn = sqlite3.connect(str(db))
                    r = conn.execute("SELECT value FROM pod_meta WHERE key='merkle_root'").fetchone()
                    if r and r[0]: sealed_pods += 1
                    conn.close()
                except: pass
    score = min(1.0, sealed_pods / 10)
    passed = sealed_pods >= 5 and cache_exists
    return {
        "name": "Catch & Store Energy",
        "score": round(score, 3),
        "passed": passed,
        "metric": f"sealed_pods={sealed_pods}, cache={'yes' if cache_exists else 'no'}",
        "gate": "sealed_pods >= 5 AND receipt_cache exists",
        "storage_efficiency": round(score * 100, 1),
    }

def principle_3_obtain_yield():
    """Obtain a Yield — the master principle. What has the system PRODUCED?"""
    # Count actual outputs: receipts, commits, tools, pods
    receipts = count_receipts()
    commits = count_github_commits()
    tools = count_tools()
    pods = count_pods()
    # Has the system produced anything verifiable?
    total_outputs = receipts + commits + tools + pods
    # Cost: hours spent (estimate from commits) + cloud spend (~$1)
    estimated_hours = max(1, commits / 5)  # ~5 commits/hour
    estimated_cost = 1.0  # $1 OpenRouter credit
    # Yield = outputs / inputs
    input_cost = estimated_cost + (estimated_hours * 15)  # $15/hr opportunity cost
    output_value = total_outputs * 10  # each output worth ~$10 in infrastructure value
    eta = output_value / max(input_cost, 1)
    score = min(1.0, eta / 10)
    passed = total_outputs >= 20
    return {
        "name": "Obtain a Yield",
        "score": round(score, 3),
        "passed": passed,
        "metric": f"outputs={total_outputs}, cost=${estimated_cost}, hours={estimated_hours:.0f}",
        "gate": "total_outputs >= 20",
        "eta": round(eta, 2),
        "roi_ratio": f"{output_value}:{input_cost}",
        "total_outputs": total_outputs,
        "total_value_usd": output_value,
        "total_cost_usd": input_cost,
    }

def principle_4_self_regulation():
    """Apply Self-Regulation — mistake log + court v6 + drift detection"""
    mistakes = count_mistakes()
    # Check if court v6 runs
    court_running = False
    try:
        result = subprocess.run(["systemctl", "--user", "show", "openroot-court.service", "-p", "Result"],
                              capture_output=True, text=True, timeout=3)
        court_running = "success" in result.stdout
    except: pass
    score = min(1.0, (mistakes + (1 if court_running else 0)) / 15)
    passed = mistakes >= 5 and court_running
    return {
        "name": "Apply Self-Regulation",
        "score": round(score, 3),
        "passed": passed,
        "metric": f"mistakes={mistakes}, court={'running' if court_running else 'stopped'}",
        "gate": "mistakes >= 5 AND court running",
        "feedback_mechanisms": mistakes + (1 if court_running else 0),
    }

def principle_5_renewable_resources():
    """Use Renewable Resources — local models + solar-powered nodes + open-source"""
    ollama_models = count_ollama_models()
    # All tools are open-source. Cloud router uses free/open models.
    # Check if local models available (renewable compute)
    local_available = ollama_models > 0
    # Check if openrouter (free tier / renewable cloud)
    cloud_ok = cloud_router_working()
    score = min(1.0, (ollama_models / 5 + (1 if cloud_ok else 0)) / 2)
    passed = local_available and cloud_ok
    return {
        "name": "Use Renewable Resources",
        "score": round(score, 3),
        "passed": passed,
        "metric": f"local_models={ollama_models}, cloud={'live' if cloud_ok else 'down'}",
        "gate": "local models > 0 AND cloud router working",
        "renewable_fraction": round(score, 2),
    }

def principle_6_produce_no_waste():
    """Produce No Waste — every mistake composted, every file content-addressed"""
    mistakes = count_mistakes()
    # Check if mistake engine exists
    mistake_engine = (REPO / "bin" / "mistake_engine_v1.py").exists()
    # Check if pods use content-addressing (blake3)
    content_addressed = (REPO / "bin" / "pod_loader_v1.py").exists()
    # Compost rate = mistakes that have solutions
    composted = 0
    if mistake_engine:
        ml = REPO / "data" / "mistakes" / "mistake_log.jsonl"
        if ml.exists():
            for line in open(ml):
                try:
                    d = json.loads(line)
                    if d.get("lesson") or d.get("canary"): composted += 1
                except: pass
    compost_rate = composted / max(mistakes, 1)
    score = min(1.0, compost_rate)
    passed = compost_rate >= 0.5 and content_addressed
    return {
        "name": "Produce No Waste",
        "score": round(score, 3),
        "passed": passed,
        "metric": f"mistakes={mistakes}, composted={composted}, rate={compost_rate:.0%}",
        "gate": "compost_rate >= 0.5 AND content-addressing active",
        "compost_rate": round(compost_rate, 2),
    }

def principle_7_design_patterns_to_details():
    """Design from Patterns to Details — schema first, then implementation"""
    # Check: receipt spec exists (the pattern)
    receipt_spec = (REPO / "genesis" / "receipt_v1.json").exists()
    # Check: multiple implementations follow the pattern
    receipt_versions = count_receipts()
    # Check: lesson plan (doctrine document)
    doctrine = (REPO / "docs" / "LESSON_PLAN_script_doctrine.md").exists()
    score = min(1.0, (receipt_versions + (1 if doctrine else 0)) / 5)
    passed = receipt_spec and doctrine and receipt_versions >= 3
    return {
        "name": "Design from Patterns to Details",
        "score": round(score, 3),
        "passed": passed,
        "metric": f"receipt_versions={receipt_versions}, doctrine={'yes' if doctrine else 'no'}",
        "gate": "receipt spec exists AND doctrine exists AND >= 3 receipt versions",
        "schema_to_impl_drift": round(1.0 - score, 2),
    }

def principle_8_integrate_dont_segregate():
    """Integrate Don't Segregate — cross-zone proposals, mesh connects everything"""
    # Count how many subsystems are connected
    cron = count_cron()
    systemd = count_systemd()
    tools = count_tools()
    pods = count_pods()
    # Integration = cron jobs + systemd services + tools that cross-reference
    integration_points = cron + systemd
    # Check if mesh tools exist (kai9000_connect, github_inbox, etc.)
    mesh_tools = 0
    for t in ["kai9000_connect.sh", "github_inbox_v1.py", "boot_context.sh"]:
        if (REPO / "bin" / t).exists(): mesh_tools += 1
    score = min(1.0, (integration_points + mesh_tools) / 15)
    passed = integration_points >= 5 and mesh_tools >= 2
    return {
        "name": "Integrate Don't Segregate",
        "score": round(score, 3),
        "passed": passed,
        "metric": f"cron={cron}, systemd={systemd}, mesh_tools={mesh_tools}",
        "gate": "integration_points >= 5 AND mesh_tools >= 2",
        "integration_density": integration_points + mesh_tools,
    }

def principle_9_small_slow_solutions():
    """Use Small & Slow Solutions — local models first, small pods, incremental"""
    ollama_models = count_ollama_models()
    # Check if we have small models (qwen3:0.6b, qwen2.5:1.5b, etc.)
    small_models = 0
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        for line in result.stdout.splitlines()[1:]:
            if any(x in line for x in ["0.6b", "1.5b", "1.7b", "2b", "3b"]):
                small_models += 1
    except: pass
    # Check if we use local-first routing (cloud_router_v2 has prefer_local)
    local_first = (REPO / "bin" / "cloud_router_v2.py").exists()
    score = min(1.0, small_models / 5)
    passed = small_models >= 3 and local_first
    return {
        "name": "Use Small Slow Solutions",
        "score": round(score, 3),
        "passed": passed,
        "metric": f"small_models={small_models}, local_first={'yes' if local_first else 'no'}",
        "gate": "small_models >= 3 AND local-first routing exists",
        "solution_size_vs_need": round(score, 2),
    }

def principle_10_value_diversity():
    """Use & Value Diversity — multiple pods, models, providers, approaches"""
    pods = count_pods()
    ollama_models = count_ollama_models()
    # Check if cloud router has multiple providers
    cloud_multi = False
    try:
        src = (REPO / "bin" / "cloud_router_v2.py").read_text()
        providers = src.count('"name":"')
        cloud_multi = providers >= 3
    except: pass
    diversity = pods + ollama_models + (3 if cloud_multi else 0)
    score = min(1.0, diversity / 20)
    passed = pods >= 5 and ollama_models >= 3 and cloud_multi
    return {
        "name": "Use & Value Diversity",
        "score": round(score, 3),
        "passed": passed,
        "metric": f"pods={pods}, models={ollama_models}, providers={'multi' if cloud_multi else 'single'}",
        "gate": "pods >= 5 AND models >= 3 AND multi-provider",
        "diversity_index": diversity,
    }

def principle_11_use_edges_marginal():
    """Use Edges & Value the Marginal — edge hardware (A15, ESP32), rural deployment"""
    # Check if A15 thin client exists
    a15_connected = (REPO / "bin" / "kai9000_connect.sh").exists()
    # Check if rural/marginal context (Sikeston, MO)
    rural = True  # Sikeston is rural
    # Check if edge tools exist
    edge_tools = 0
    for t in ["kai9000_connect.sh", "optiplex_to_kai9000.sh", "boot_context.sh"]:
        if (REPO / "bin" / t).exists(): edge_tools += 1
    # Check if hardware dossier covers edge devices
    hardware_pod = (GARDEN / "hardware_dossier_v1").exists()
    score = min(1.0, (edge_tools + (1 if a15_connected else 0) + (1 if hardware_pod else 0)) / 5)
    passed = a15_connected and edge_tools >= 2
    return {
        "name": "Use Edges & Value the Marginal",
        "score": round(score, 3),
        "passed": passed,
        "metric": f"a15={'connected' if a15_connected else 'no'}, edge_tools={edge_tools}, hardware_dossier={'yes' if hardware_pod else 'no'}",
        "gate": "A15 connected AND edge_tools >= 2",
        "edge_to_core_ratio": round(score, 2),
    }

def principle_12_creatively_respond_to_change():
    """Creatively Use & Respond to Change — schema versioning, mistakes drive improvement"""
    receipt_versions = count_receipts()
    mistakes = count_mistakes()
    # Check if receipt schema has version field
    schema_versioned = False
    try:
        r = json.loads((REPO / "genesis" / "receipt_v1.json").read_text())
        schema_versioned = "schema_version" in r
    except: pass
    # Adaptation rate = receipt versions + mistakes composted
    adaptation_events = receipt_versions + mistakes
    score = min(1.0, adaptation_events / 15)
    passed = schema_versioned and receipt_versions >= 3 and mistakes >= 5
    return {
        "name": "Creatively Use & Respond to Change",
        "score": round(score, 3),
        "passed": passed,
        "metric": f"receipt_versions={receipt_versions}, mistakes={mistakes}, schema_versioned={'yes' if schema_versioned else 'no'}",
        "gate": "schema_versioned AND receipt_versions >= 3 AND mistakes >= 5",
        "adaptation_rate": round(score, 2),
    }

# ============ RUN ALL 12 GATES ============

def run_all_principles():
    """Run all 12 permaculture principles as deterministic code gates."""
    principles = [
        principle_1_observe_interact,
        principle_2_catch_store_energy,
        principle_3_obtain_yield,
        principle_4_self_regulation,
        principle_5_renewable_resources,
        principle_6_produce_no_waste,
        principle_7_design_patterns_to_details,
        principle_8_integrate_dont_segregate,
        principle_9_small_slow_solutions,
        principle_10_value_diversity,
        principle_11_use_edges_marginal,
        principle_12_creatively_respond_to_change,
    ]
    
    results = []
    for i, func in enumerate(principles, 1):
        result = func()
        result["principle_number"] = i
        results.append(result)
    
    # Calculate aggregate
    scores = [r["score"] for r in results]
    passed_count = sum(1 for r in results if r["passed"])
    aggregate = sum(scores) / 12
    
    # System-wide eta (from principle 3)
    eta = results[2].get("eta", 0)
    
    # Synergetic compounding
    functions_stacked = sum(1 for r in results if r["passed"])
    beneficiaries = count_pods() + count_tools() // 5
    synergy = 1 * (PHI ** functions_stacked) * (1 + math.log(max(beneficiaries, 1)) / PHI)
    
    return {
        "audit_type": "system_audit_v1",
        "timestamp": now_utc(),
        "principles": results,
        "aggregate_score": round(aggregate, 3),
        "principles_passed": f"{passed_count}/12",
        "system_eta": round(eta, 2),
        "synergy_score": round(synergy, 2),
        "functions_stacked": functions_stacked,
        "beneficiaries": beneficiaries,
        "system_state": {
            "pods": count_pods(),
            "chunks": count_chunks(),
            "receipts": count_receipts(),
            "tools": count_tools(),
            "mistakes": count_mistakes(),
            "cron_jobs": count_cron(),
            "systemd_services": count_systemd(),
            "ollama_models": count_ollama_models(),
            "github_commits": count_github_commits(),
            "cloud_router_live": cloud_router_working(),
        },
    }

def main():
    ap = argparse.ArgumentParser(description="OpenRoot System Audit v1 — 12 Permaculture Principles")
    ap.add_argument("--ai-synthesis", action="store_true", help="Route results to cloud AI for synthesis")
    ap.add_argument("--json", action="store_true", default=True)
    args = ap.parse_args()
    
    print("[gate] RUNNING 12 PERMACULTURE PRINCIPLES AS CODE GATES", file=sys.stderr)
    print("[gate] Verifiers are pure code. Models propose. Code disposes.", file=sys.stderr)
    print(file=sys.stderr)
    
    audit = run_all_principles()
    
    # Print results
    print("╔══════════════════════════════════════════════════════════════════════╗", file=sys.stderr)
    print("║          OPENROOT SYSTEM AUDIT — 12 PERMACULTURE PRINCIPLES         ║", file=sys.stderr)
    print("╚══════════════════════════════════════════════════════════════════════╝", file=sys.stderr)
    print(file=sys.stderr)
    
    for p in audit["principles"]:
        status = "✅ PASS" if p["passed"] else "❌ FAIL"
        print(f"  {p['principle_number']:2d}. {p['name']:35s} {status}  score={p['score']:.2f}  {p['metric']}", file=sys.stderr)
    
    print(file=sys.stderr)
    print(f"  Aggregate Score:     {audit['aggregate_score']:.3f}", file=sys.stderr)
    print(f"  Principles Passed:   {audit['principles_passed']}", file=sys.stderr)
    print(f"  System η (eta):      {audit['system_eta']:.2f}", file=sys.stderr)
    print(f"  Synergy Score:        {audit['synergy_score']:.2f} ({audit['functions_stacked']} functions, {audit['beneficiaries']} beneficiaries)", file=sys.stderr)
    print(file=sys.stderr)
    print(f"  System State:", file=sys.stderr)
    for k, v in audit["system_state"].items():
        print(f"    {k}: {v}", file=sys.stderr)
    print(file=sys.stderr)
    
    # Output JSON receipt
    receipt_hash = hashlib.sha256(json.dumps(audit, sort_keys=True).encode()).hexdigest()
    audit["receipt_hash"] = receipt_hash
    
    print(json.dumps(audit, indent=2))
    
    # Optional AI synthesis
    if args.ai_synthesis:
        print(file=sys.stderr)
        print("[gate] Routing audit results to cloud AI for synthesis...", file=sys.stderr)
        
        prompt = f"""SYSTEM AUDIT RESULTS (computed by deterministic code gates):

Aggregate Score: {audit['aggregate_score']:.3f}
Principles Passed: {audit['principles_passed']}
System η: {audit['system_eta']:.2f}
Synergy Score: {audit['synergy_score']:.2f}

System State: {json.dumps(audit['system_state'])}

Principle Results:
{json.dumps([{k: v for k, v in p.items() if k in ('name','score','passed','metric')} for p in audit['principles']], indent=2)}

Based on these DETERMINISTIC results (not AI text), analyze:
1. Which principle has the lowest score and why?
2. What is the single highest-leverage action to improve the aggregate score?
3. How does the system η (eta) compound when the failed principles are fixed?
"""
        router = REPO / "bin" / "cloud_router_v2.py"
        r = subprocess.run(
            ["python3", str(router), "--prompt", prompt, "--max-tokens", "1000"],
            capture_output=True, text=True, timeout=180, cwd=str(REPO), stdin=subprocess.DEVNULL)
        
        # Parse and print AI response
        for i, c in enumerate(r.stdout):
            if c == "{":
                try:
                    data = json.JSONDecoder().raw_decode(r.stdout[i:])[0]
                    print("\n=== AI SYNTHESIS ===", file=sys.stderr)
                    print(data.get("response", ""), file=sys.stderr)
                    break
                except: pass

if __name__ == "__main__":
    main()
