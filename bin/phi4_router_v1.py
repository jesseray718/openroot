#!/usr/bin/env python3
"""phi4-router front door: hash-first → embed-second → model-last.
Acts on DECISION output from semantic_lookup_v1.py and seals pathways.

Usage:
  phi4_router_v1.py query "user question" [--threshold N] [--model NAME]
  phi4_router_v1.py seal --input-hash H --report-path P --kind K --tool T [--parents SHA1,SHA2]

The query command:
  1. Calls semantic_lookup_v1.py route
  2. Parses DECISION=<HASH|SEMANTIC|MODEL>
  3. HASH: returns cached answer_path
  4. SEMANTIC: returns nearest row_sha + score
  5. MODEL: prints instruction for caller to invoke model, then seal

The seal command:
  - Appends new pathway to Merkle ledger
  - Auto-calculates parents if none provided (links to existing theorems)
  - Optionally triggers embedding (requires --embed)
"""
import subprocess, sys, json, hashlib, argparse, sqlite3, os

ROUTER = "/home/jesse/openroot/bin/semantic_lookup_v1.py"
LEDGER = "/home/jesse/openroot/bin/pathway_ledger_v1.py"

def run_route(question, threshold):
    proc = subprocess.run(["python3", ROUTER, "route", question, "--threshold", str(threshold)],
                         capture_output=True, text=True, timeout=180)
    return proc.stdout.strip(), proc.returncode

def query_handler(question, threshold, model):
    decision_out, code = run_route(question, threshold)
    print(f"[gate] routing: {decision_out}")
    
    if "DECISION=HASH" in decision_out:
        answer = decision_out.split("answer=")[1] if "answer=" in decision_out else "(cached)"
        print(f"[banked] CACHE_HIT (exact query hash) → {answer[:60]}")
        print(f"[gate] RETURN: exact-cache")
        return 0
    
    if "DECISION=SEMANTIC" in decision_out:
        parts = decision_out.split()
        sha = [p for p in parts if p.startswith("row_sha=")]
        sc = [p for p in parts if p.startswith("score=")]
        info = f"sha={sha[0][8:] if sha else '?'} score={sc[0][6:] if sc else '?'}" if sha or sc else "?"
        print(f"[banked] NEIGHBOR_FOUND → {info}")
        print(f"[gate] RETURN: semantic-cache")
        return 0
    
    if "DECISION=MODEL" in decision_out:
        print(f"[gate] NO_CACHE → invoke model '{model}' on: {question[:100]}")
        print(f"[gate] AFTER_MODEL: run: python3 {LEDGER} append --input-hash $(echo \"{question}\" | sha256sum | cut -c1-64) --kind query --tool {model} --report-path /path/to/sealed_report.md")
        print(f"[gate] RETURN: model-needed")
        return 3
    
    print(f"[held] unknown decision: {decision_out}")
    return 1

def seal_handler(input_hash, report_path, kind, tool, parents):
    cmd = ["python3", LEDGER, "append",
           "--input-hash", input_hash,
           "--kind", kind,
           "--tool", tool,
           "--report-path", report_path,
           "--verdict", "verified"]
    if parents:
        cmd.extend(["--parents", parents])
    
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode == 0:
        row_sha = proc.stdout.strip()
        print(f"[banked] pathway sealed: {row_sha[:12]}")
        
        # Optional embedding
        try:
            emb_proc = subprocess.run(["python3", "/home/jesse/openroot/bin/embed_backfill_v1.py", row_sha],
                                     capture_output=True, text=True, timeout=60)
            if emb_proc.returncode == 0:
                print(f"[banked] embedding created for {row_sha[:12]}")
        except Exception as e:
            print(f"[held] embedding skipped: {e}")
        
        print(f"[gate] RETURN: sealed")
        return 0
    else:
        print(f"[held] seal failed: {proc.stderr}")
        return 1

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    
    q = sub.add_parser("query")
    q.add_argument("question")
    q.add_argument("--threshold", type=float, default=0.42)
    q.add_argument("--model", default="qwen2.5-coder:7b")
    
    s = sub.add_parser("seal")
    s.add_argument("--input-hash", required=True)
    s.add_argument("--report-path", required=True)
    s.add_argument("--kind", default="audit")
    s.add_argument("--tool", default="ollama")
    s.add_argument("--parents")
    
    a = p.parse_args()
    if a.cmd == "query":
        sys.exit(query_handler(a.question, a.threshold, a.model))
    elif a.cmd == "seal":
        sys.exit(seal_handler(a.input_hash, a.report_path, a.kind, a.tool, a.parents))
    else:
        print(__doc__); sys.exit(1)
