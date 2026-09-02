#!/usr/bin/env python3
"""Observer -> Inference -> Ledger loop. Reads existing history then watches for new."""
import json, hashlib, subprocess, sys, urllib.request, time
from datetime import datetime, timezone
from pathlib import Path

LEDGER = Path.home() / "openroot/closed-loop/ledger/eta-ledger.jsonl"
API = "http://localhost:8080/v1/chat/completions"
MODEL = "qwen2.5-coder-7b"

def f1_capture(line, source):
    return {"type": "capture", "raw": line.strip()[:200], "source": source,
            "ts": datetime.now(timezone.utc).isoformat()}

def f3_aggregate(c):
    line = c["raw"].lower()
    patterns = []
    for kw, pat in [("agape","agape_key"),("proof","proof_key"),
                    ("theorem","proof_key"),("fractal","fractal_sys"),
                    ("inference","inference"),("llama","inference")]:
        if kw in line: patterns.append(pat)
    return {"type": "aggregate", "patterns": patterns}

def f10_yield(insight):
    priority = min(sum(1 for k in ["agape","proof","theorem","sacred","etymology"]
                       if k in str(insight).lower()), 5)
    return {"type": "yield", "insight": insight, "priority": priority}

def call_llm(prompt):
    body = json.dumps({"model": MODEL, "messages": [
        {"role": "user", "content": prompt}], "max_tokens": 200,
        "temperature": 0.0}).encode()
    req = urllib.request.Request(API, data=body,
        headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read())
    return resp, time.time() - t0

def measure_joules(seconds):
    out = subprocess.check_output(
        ["sudo", "perf", "stat", "-e", "power/energy-pkg/", "sleep", str(seconds)],
        stderr=subprocess.STDOUT, text=True)
    for line in out.splitlines():
        if "Joules power/energy-pkg" in line:
            return float(line.strip().split()[0].replace(",", ""))
    return 0.0

def commit_inference(entry):
    entry["sha256"] = hashlib.sha256(
        json.dumps(entry, sort_keys=True, separators=(",",":")).encode()).hexdigest()
    with LEDGER.open("a") as f:
        f.write(json.dumps(entry) + "\n")

def loop(filepath):
    prev_pat = None
    ops = 0
    inferences = 0
    pos = 0
    print(f"Starting loop on {filepath}", flush=True)
    
    # Pass 1: read existing file
    try:
        with open(filepath, "r", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                ops += 1
                cap = f1_capture(line, filepath)
                agg = f3_aggregate(cap)
                y = f10_yield({"line": cap["raw"][:100], "patterns": agg["patterns"]})
                if y["priority"] >= 2 and inferences < 3:
                    prompt = f"Observed: {cap['raw'][:150]}\nPatterns: {agg['patterns']}\nBriefly: meaning for OpenRoot?"
                    print(f"\n>>> INFERENCE (pri={y['priority']})", flush=True)
                    try:
                        base_j = measure_joules(0.3)
                        resp, wall = call_llm(prompt)
                        post_j = measure_joules(0.3)
                        infer_j = (post_j / 0.3) * wall
                        usage = resp.get("usage", {})
                        entry = {
                            "ts": datetime.now(timezone.utc).isoformat(),
                            "event": "inference", "trigger": "observer",
                            "model": MODEL, "input_patterns": agg["patterns"],
                            "total_tokens": usage.get("total_tokens", 0),
                            "wall_s": round(wall, 3),
                            "infer_j": round(infer_j, 4),
                            "method": "PoPW_inference_v1",
                        }
                        commit_inference(entry)
                        inferences += 1
                        print(f"  infer_j={infer_j:.3f}J tokens={usage.get('total_tokens',0)}", flush=True)
                        print(f"  {resp['choices'][0]['message']['content'][:200]}", flush=True)
                    except Exception as e:
                        print(f"  failed: {e}", flush=True)
                if ops % 100 == 0:
                    print(f"  pass1 ops={ops} inferences={inferences}", flush=True)
            pos = f.tell()
    except Exception as e:
        print(f"File error: {e}", flush=True)
    
    print(f"\nPass 1 done. ops={ops} inferences={inferences}. Now watching for new lines...", flush=True)
    
    # Pass 2: watch for new lines
    while True:
        try:
            with open(filepath, "r", errors="ignore") as f:
                f.seek(pos)
                while True:
                    line = f.readline()
                    if not line:
                        time.sleep(0.5)
                        continue
                    line = line.strip()
                    if not line: continue
                    ops += 1
                    cap = f1_capture(line, filepath)
                    agg = f3_aggregate(cap)
                    y = f10_yield({"line": cap["raw"][:100], "patterns": agg["patterns"]})
                    if y["priority"] >= 2 and inferences < 5:
                        prompt = f"Observed: {cap['raw'][:150]}\nPatterns: {agg['patterns']}\nBriefly: meaning for OpenRoot?"
                        print(f"\n>>> INFERENCE (pri={y['priority']})", flush=True)
                        try:
                            base_j = measure_joules(0.3)
                            resp, wall = call_llm(prompt)
                            post_j = measure_joules(0.3)
                            infer_j = (post_j / 0.3) * wall
                            usage = resp.get("usage", {})
                            entry = {
                                "ts": datetime.now(timezone.utc).isoformat(),
                                "event": "inference", "trigger": "observer",
                                "model": MODEL, "input_patterns": agg["patterns"],
                                "total_tokens": usage.get("total_tokens", 0),
                                "wall_s": round(wall, 3),
                                "infer_j": round(infer_j, 4),
                                "method": "PoPW_inference_v1",
                            }
                            commit_inference(entry)
                            inferences += 1
                            print(f"  infer_j={infer_j:.3f}J tokens={usage.get('total_tokens',0)}", flush=True)
                            print(f"  {resp['choices'][0]['message']['content'][:200]}", flush=True)
                        except Exception as e:
                            print(f"  failed: {e}", flush=True)
                    pos = f.tell()
        except KeyboardInterrupt:
            print(f"\nStopped. ops={ops} inferences={inferences}", flush=True)
            return
        except Exception as e:
            print(f"Error: {e}", flush=True)
            time.sleep(1)

if __name__ == "__main__":
    fp = sys.argv[1] if len(sys.argv) > 1 else "/home/jesse/.bash_history"
    loop(fp)
