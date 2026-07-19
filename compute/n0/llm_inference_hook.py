#!/data/data/com.termux/files/usr/bin/env python3
"""
llm_inference_hook.py — OpenRoot n0 unit
CONTRACT
  Single responsibility: one inference call to local llama-server + structured output.
  Input : prompt (via --prompt or stdin)
  Output: JSON with completion + token counts + timings (for measure_llm_efficiency.py)
"""
import argparse
import json
import sys
import time
import urllib.request
from datetime import datetime

def call_llama(prompt: str, model: str = "default", n_predict: int = 256,
               temperature: float = 0.0, seed: int = -1) -> dict:
    url = "http://127.0.0.1:8080/completion"
    payload = {
        "prompt": prompt,
        "n_predict": n_predict,
        "temperature": temperature,
        "seed": seed,
        "stream": False
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    t0 = time.monotonic()
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    t1 = time.monotonic()

    # llama.cpp returns these fields
    return {
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt,
        "content": result.get("content", ""),
        "prompt_eval_count": result.get("prompt_eval_count"),
        "eval_count": result.get("tokens_predicted") or result.get("eval_count"),
        "prompt_eval_duration": result.get("prompt_eval_duration"),  # in µs
        "eval_duration": result.get("eval_duration"),                # in µs
        "wall_ms": round((t1 - t0) * 1000, 2),
        "node": "N0_llm_inference_hook"
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", help="Prompt text")
    ap.add_argument("--model", default="local")
    ap.add_argument("--n-predict", type=int, default=256)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=-1)
    args = ap.parse_args()

    if args.prompt:
        prompt = args.prompt
    else:
        prompt = sys.stdin.read().strip()

    if not prompt:
        print(json.dumps({"error": "No prompt provided"}))
        sys.exit(1)

    result = call_llama(
        prompt=prompt,
        model=args.model,
        n_predict=args.n_predict,
        temperature=args.temperature,
        seed=args.seed
    )
    print(json.dumps(result))


if __name__ == "__main__":
    main()
