#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0
"""
stack_tuner.py - Benchmark local models per role, write optimal routing weights
CANARY: STACK_TUNER_V1_20260924
Doctrine: eta = J_useful/J_human measured, not claimed. w_i = 1/(f_i + eps).

Default = DRY RUN (benchmarks only, no downloads).
CONFIRM=1 pulls missing models first, then benches.
Writes data/model_weights.json (runtime state, untracked).
"""
import sys, os, json, subprocess, time, shutil, socket
from pathlib import Path
from datetime import datetime

BASE = Path("/home/jesse/openroot")
WEIGHTS = BASE / "data" / "model_weights.json"
CONFIRM = os.environ.get("CONFIRM") == "1"
EPS = 0.01

# role -> candidate models (small-first, per CPU-bound doctrine)
ROSTER = {
    "route":  ["llama3.2:1b", "qwen3:1.7b", "qwen2.5:3b"],
    "grade":  ["phi4-mini", "smollm3:3b", "qwen2.5:3b"],
    "draft":  ["phi4-mini", "smollm3:3b", "qwen2.5:3b"],
    "build":  ["qwen2.5-coder:7b"],
}

# canonical micro-benchmarks per role (fixed prompts = reproducible)
BENCH = {
    "route":  "Classify in exactly one word (code, grade, draft, or search): 'Write a python function to parse JSONL logs'",
    "grade":  "Rate 1-10 in one sentence: A script that greps a ledger for a canary string and exits nonzero on miss.",
    "draft":  "In 2 sentences: why cache-first routing saves energy in local AI stacks.",
    "build":  "Write a python function sha16(s) returning the first 16 hex chars of the sha256 of s.",
}

def ollama_post(path, payload, timeout=600):
    payload = json.dumps(payload)
    r = subprocess.run(["curl", "-s", "-X", "POST", f"http://localhost:11434/api/{path}",
                         "-H", "Content-Type: application/json", "-d", payload],
                        capture_output=True, text=True, timeout=timeout)
    return json.loads(r.stdout) if r.stdout.strip() else {}

def ollama_get_tags(timeout=30):
    r = subprocess.run(["curl", "-s", "http://localhost:11434/api/tags"],
                       capture_output=True, text=True, timeout=timeout)
    return json.loads(r.stdout) if r.stdout.strip() else {}

def models_installed():
    r = ollama_get_tags()
    return {m["name"] for m in r.get("models", [])}

def bench(model, prompt):
    """Returns (tok_per_s, wall_s, chars). Bare /api/generate for micro-tasks."""
    t0 = time.time()
    resp = ollama_post("generate", {"model": model, "prompt": prompt, "stream": False,
                                    "options": {"num_predict": 150}})
    wall = time.time() - t0
    n = resp.get("eval_count", 0); d = resp.get("eval_duration", 1)
    tps = n / (d / 1e9) if d else 0.0
    return tps, wall, len(resp.get("response", ""))

def main():
    installed = models_installed()
    if not installed:
        print("[held] Ollama not responding on :11434"); return 1
    disk_gb = shutil.disk_usage(BASE).free / 1e9
    print(f"=== STACK TUNER === ts={datetime.now().isoformat()}")
    print(f"disk free: {disk_gb:.1f} GB | installed: {sorted(installed)}")

    to_pull = sorted({m for ms in ROSTER.values() for m in ms} - installed)
    if to_pull:
        if not CONFIRM:
            print(f"[held] not installed, pull with CONFIRM=1: {to_pull}")
        else:
            for m in to_pull:
                print(f"[pulling] {m} ...")
                rc = subprocess.run(["ollama", "pull", m]).returncode
                print(f"  -> {'[banked]' if rc == 0 else '[held] FAILED'} {m}")
            installed = models_installed()

    results = {}
    for role, models in ROSTER.items():
        prompt = BENCH[role]
        for m in models:
            if m not in installed:
                continue
            tps, wall, chars = bench(m, prompt)
            # effort proxy for CPU-only: wall time (joules ~ watts x wall; watts constant)
            w = 1.0 / (wall + EPS)
            results.setdefault(role, []).append(
                {"model": m, "tok_per_s": round(tps, 1), "wall_s": round(wall, 1),
                 "out_chars": chars, "weight": round(w, 4)})
            print(f"  {role:6s} {m:22s} {tps:6.1f} tok/s  {wall:5.1f}s  {chars:4d} chars")

    # winners per role = max weight (min wall). non-regression floor: keep 7B for build.
    best = {role: max(v, key=lambda x: x["weight"])["model"] for role, v in results.items() if v}
    WEIGHTS.write_text(json.dumps({"generated": datetime.now().isoformat(),
                                   "results": results, "recommended_stack": best}, indent=2))
    print(f"\n[banked] {WEIGHTS}")
    print("RECOMMENDED STACK:")
    for role, m in best.items():
        print(f"  {role:6s} -> {m}")
    print("\nMigration commands (human-gated):")
    print("  ollama rm qwen2.5-coder:7b   # NO - keep for build tier, just stop warming")
    print("  edit bin/warm_models.sh     # warm only: nomic-embed-text + " + best.get("route", "?"))
    print("[exit=0] stack_tuner complete")

if __name__ == "__main__":
    sys.exit(main())
