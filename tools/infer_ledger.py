#!/usr/bin/env python3
import json, hashlib, subprocess, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

LEDGER = Path.home() / "openroot/closed-loop/ledger/eta-ledger.jsonl"
API = "http://localhost:8080/v1/chat/completions"
MODEL = "qwen2.5-coder-7b"

def read_pkg_joules_over(seconds):
    out = subprocess.check_output(
        ["sudo", "perf", "stat", "-e", "power/energy-pkg/",
         "sleep", str(seconds)],
        stderr=subprocess.STDOUT, text=True
    )
    for line in out.splitlines():
        if "Joules power/energy-pkg" in line:
            return float(line.strip().split()[0].replace(",", ""))
    raise RuntimeError("could not parse perf output")

def chat(prompt):
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 256,
        "temperature": 0.0,
    }).encode()
    req = urllib.request.Request(API, data=body,
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=180) as r:
        resp = json.loads(r.read())
    wall_s = time.time() - t0
    return resp, wall_s

def canonical_hash(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

def main():
    if len(sys.argv) > 1 and sys.argv[1] in {"-h", "--help"}:
        print(
            "Usage: infer_ledger.py PROMPT\n"
            "   or: printf '%s\\n' 'PROMPT' | python3 infer_ledger.py\n\n"
            "Runs one local LLM inference, estimates energy using perf, "
            "and appends a JSONL event to closed-loop/ledger/eta-ledger.jsonl."
        )
        return

    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = sys.stdin.read().strip()

    if not prompt:
        print("error: provide a prompt as arguments or standard input", file=sys.stderr)
        raise SystemExit(2)
    base_j = read_pkg_joules_over(0.5)
    t0 = time.time()
    resp, wall_s = chat(prompt)
    post_j = read_pkg_joules_over(0.5)
    post_power = post_j / 0.5
    infer_j = max(post_power * wall_s, 0.0)
    usage = resp.get("usage", {})
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": "inference",
        "domain": "computational",
        "model": MODEL,
        "total_tokens": usage.get("total_tokens", 0),
        "idle_sample_j": round(base_j, 4),
        "post_sample_j": round(post_j, 4),
        "estimated_infer_j": round(infer_j, 4),
        "method": "PoPW_inference_v1_post_sample_estimate",
    }
    entry["sha256"] = canonical_hash(entry)
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a") as f: f.write(json.dumps(entry) + "\n")
    print(json.dumps(entry, indent=2))

if __name__ == "__main__": main()
