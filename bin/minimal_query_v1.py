#!/usr/bin/env python3
"""Minimal query: per-pod routing + slim dossier + clarifying loop.
Outputs a fully-accounted OpenRoot receipt."""
import argparse, hashlib, json, os, subprocess, sys, time
from pathlib import Path

REPO = Path(os.environ.get("OPENROOT_REPO", "/home/jesse/openroot"))
DOSSIER = REPO / "bin" / "dossier_engine_v1.py"
ROUTER = REPO / "bin" / "cloud_router_v2.py"
POD_ROUTER = REPO / "bin" / "pod_router_v1.py"

def blake3_hex(b):
    try:
        import blake3; return blake3.blake3(b).hexdigest()
    except: return hashlib.sha256(b).hexdigest()

def run_pod_router(question):
    r = subprocess.run(["python3", str(POD_ROUTER), "--question", question, "--json"],
        capture_output=True, text=True, timeout=10, cwd=str(REPO), stdin=subprocess.DEVNULL)
    return json.loads(r.stdout)

def assemble_dossier(question, pods, budget=4000):
    r = subprocess.run(
        ["python3", str(DOSSIER), "--pods", *pods, "--query", question,
         "--top-k", "12", "--budget", str(budget)],
        capture_output=True, text=True, timeout=20, cwd=str(REPO), stdin=subprocess.DEVNULL)
    return r.stdout.strip() if r.returncode == 0 else ""

def is_clarifying(text):
    head = text.lstrip()[:200].lower()
    markers = ["clarif", "do you mean", "which ", "could you specify", "i need more",
              "ambiguous", "before i answer", "can you confirm", "do you want",
              "are you asking", "would you like", "please provide", "to give you",
              "question:", "need more context", "not sure", "unsure"]
    return any(m in head for m in markers)

def call_cloud(prompt, max_tokens=256):
    r = subprocess.run(
        ["python3", str(ROUTER), "--prompt", prompt, "--max-tokens", str(max_tokens)],
        capture_output=True, text=True, timeout=180, cwd=str(REPO), stdin=subprocess.DEVNULL)
    decoder = json.JSONDecoder()
    for i, c in enumerate(r.stdout):
        if c == "{":
            try:
                cand, _ = decoder.raw_decode(r.stdout[i:])
                if isinstance(cand, dict) and ("response" in cand or "providers_tried" in cand):
                    return cand
            except: pass
    return {"response": r.stdout, "success": False}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--question", required=True)
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--max-rounds", type=int, default=3)
    args = ap.parse_args()

    route = run_pod_router(args.question)
    pods = route["pods"]
    kws = route["keywords"]
    
    print(f"[router] pods: {pods}", file=sys.stderr)
    print(f"[router] keywords: {kws}", file=sys.stderr)
    
    question = args.question
    rounds = []
    
    for round_idx in range(args.max_rounds):
        dossier_text = assemble_dossier(question, pods, budget=4000)
        prompt = f"CONTEXT (minimal, from {pods}):\n{dossier_text}\n---\nQUESTION:\n{question}\n"
        packet_hash = blake3_hex(prompt.encode())
        
        print(f"[round {round_idx}] packet={packet_hash[:16]}... dossier={len(dossier_text)}chars", file=sys.stderr)
        
        t_start = time.time()
        result = call_cloud(prompt, args.max_tokens)
        latency_ms = int((time.time() - t_start) * 1000)
        
        response = result.get("response", "")
        tokens = result.get("tokens", 0)
        
        # Basic cost estimation (OpenRouter Llama-3.3-70b is ~$0.23/M input, ~$0.40/M output)
        # We'll estimate 50/50 split for simplicity in the receipt
        cost_usd = (tokens / 2 / 1_000_000) * 0.23 + (tokens / 2 / 1_000_000) * 0.40
        
        # Basic energy estimation (local fallback ~150W for 5s = 0.2J, cloud is attested)
        # If local, measure 150W * latency. If cloud, mark as attested.
        if result.get("provider") == "local":
            energy_joules = (150 * (latency_ms / 1000.0))
            energy_class = "measured"
        else:
            energy_joules = None
            energy_class = "attested_external"
            
        round_log = {
            "round": round_idx,
            "pods": pods,
            "keywords": kws,
            "packet_blake3": packet_hash,
            "dossier_chars": len(dossier_text),
            "provider": result.get("provider"),
            "model": result.get("model"),
            "tokens": tokens,
            "latency_ms": latency_ms,
            "cost_usd_estimated": round(cost_usd, 6),
            "energy_joules": round(energy_joules, 2) if energy_joules else None,
            "energy_class": energy_class,
            "clarifying": is_clarifying(response),
        }
        rounds.append(round_log)
        
        if is_clarifying(response) and round_idx < args.max_rounds - 1:
            print(f"\n[CLARIFYING QUESTION from AI]:\n{response.strip()}\n")
            print("Your answer (or empty to skip): ", end="", flush=True)
            try:
                ans = input().strip()
                if ans:
                    question += f"\n\n[ANSWER_{round_idx+1}]: {ans}"
            except (EOFError, KeyboardInterrupt):
                pass
            continue
        
        # Final Answer - construct the full receipt
        receipt = {
            "receipt_type": "minimal_query_v1",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "question": args.question,
            "final_response": response,
            "success": result.get("success", False),
            "rounds_completed": round_idx + 1,
            "rounds_log": rounds,
            "total_tokens": sum(r["tokens"] for r in rounds),
            "total_cost_usd_estimated": round(sum(r["cost_usd_estimated"] for r in rounds), 6),
            "total_energy_joules": round(sum(r["energy_joules"] for r in rounds if r["energy_joules"]), 2) if any(r["energy_joules"] for r in rounds) else None,
            "pods_routed": pods,
            "keywords_routed": kws,
            "dossier_budget": 1500,
            "subject_bound": True,
        }
        print(json.dumps(receipt, indent=2))
        sys.exit(0 if result.get("success") else 1)

    print(json.dumps({"response": response, "rounds": rounds, "exhausted": True}, indent=2))
    sys.exit(1)

if __name__ == "__main__":
    main()
