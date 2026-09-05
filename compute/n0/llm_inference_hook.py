#!/data/data/com.termux/files/usr/bin/env python3
"""
llm_inference_hook.py — OpenRoot n0 unit
CONTRACT
  Single responsibility: one inference call to local llama-server + structured output.
  Input : prompt (via --prompt or stdin)
  Output: JSON with completion + token counts + timings
"""
import argparse
import json
import sys
import time
import urllib.request
from datetime import datetime

def call_llama(prompt: str, host: str = "127.0.0.1", port: int = 8080,
               n_predict: int = 64, temperature: float = 0.2, seed: int = -1) -> dict:
    url = f"http://{host}:{port}/completion"
    payload = {
        "prompt": prompt,
        "n_predict": n_predict,
        "temperature": temperature,
        "seed": seed,
        "stream": False,
        "stop": ["\n\n", "User:", "###"]
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    t0 = time.monotonic()
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    t1 = time.monotonic()

    content = result.get("content") or result.get("generation") or ""
    return {
        "timestamp": datetime.now().isoformat(),
        "host": f"{host}:{port}",
        "prompt": prompt[:200] + ("..." if len(prompt) > 200 else ""),
        "content": content.strip(),
        "tokens_predicted": result.get("tokens_predicted") or result.get("eval_count") or n_predict,
        "tokens_evaluated": result.get("tokens_evaluated") or result.get("prompt_eval_count"),
        "wall_ms": round((t1 - t0) * 1000, 1),
        "node": "N0_llm_inference_hook"
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", type=str, default=None)
    p.add_argument("--host", type=str, default="127.0.0.1")
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--n_predict", type=int, default=64)
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--seed", type=int, default=-1)
    args = p.parse_args()

    prompt = args.prompt
    if prompt is None:
        prompt = sys.stdin.read().strip()
    if not prompt:
        print(json.dumps({"error": "no prompt provided"}))
        sys.exit(1)

    try:
        result = call_llama(
            prompt=prompt,
            host=args.host,
            port=args.port,
            n_predict=args.n_predict,
            temperature=args.temperature,
            seed=args.seed
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "node": "N0_llm_inference_hook"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
