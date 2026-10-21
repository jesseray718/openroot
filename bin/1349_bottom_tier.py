#!/data/data/com.termux/files/usr/bin/env python3
"""
bottom_tier.py — OpenRoot fractal n0 mold (nanobot runner + DAG leaf)
CONTRACT (max systemic benefit / human effort):
  - Zero external deps
  - Exponential backoff + full jitter + config-driven rate limit
  - Self-similar: every task is a micro-DAG leaf that can escalate
  - Reads $HOME/.governor/swarm-config.json
  - Local fallback via openroot/compute/n0/llm_inference_hook.py
  - Emits only structured JSON. Tokens = joules. Confidence gates park/done.
"""
import json, os, sys, time, random, urllib.request, urllib.error, subprocess
from datetime import datetime
from pathlib import Path

GOV = Path(os.environ.get("GOVERNOR_HOME", str(Path.home() / ".governor")))
CFG_PATH = GOV / "swarm-config.json"
QUEUE, WORK, PARKED, DONE, STATE, OUT, DAGS = [
    GOV / d for d in ("queue", "work", "parked", "done", "state", "output", "dags")
]

def load_cfg():
    with open(CFG_PATH) as f:
        return json.load(f)

def exponential_backoff(attempt: int, base: float = 2.0, cap: float = 45.0) -> float:
    """Full-jitter exponential backoff. attempt starts at 0."""
    return min(cap, random.uniform(0, base ** attempt))

def call_provider(provider: str, model: str, prompt: str, max_tokens: int = 96, temp: float = 0.1):
    cfg = load_cfg()
    p = cfg["providers"].get(provider, {})
    key = p.get("api_key") or os.environ.get(p.get("env_key", ""))
    if not key and provider != "local":
        return None, 0, f"missing key for {provider}"

    if provider == "local":
        hook = Path.home() / "openroot" / "compute" / "n0" / "llm_inference_hook.py"
        if not hook.exists():
            return None, 0, "local hook missing"
        r = subprocess.run(
            [sys.executable, str(hook), "--prompt", prompt, "--n_predict", str(max_tokens)],
            capture_output=True, text=True, timeout=90
        )
        try:
            j = json.loads(r.stdout)
            return j.get("content", "").strip(), j.get("tokens_predicted", 0), j.get("error")
        except Exception:
            return r.stdout.strip(), 0, r.stderr.strip() or "parse fail"

    url = p.get("base_url", "https://api.groq.com/openai/v1/chat/completions")
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    body = {
        "model": model or p.get("default_model"),
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temp,
        "stream": False
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            j = json.loads(resp.read())
        content = j["choices"][0]["message"]["content"].strip()
        tokens = j.get("usage", {}).get("total_tokens", max_tokens)
        return content, tokens, None
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        return None, 0, f"HTTP {e.code}: {body}"
    except Exception as e:
        return None, 0, str(e)

def process_leaf(task: dict) -> dict:
    """Fractal leaf: one prompt → one inference → confidence gate."""
    tid = task.get("id", "anon")
    prompt = task["prompt"]
    max_tokens = task.get("max_tokens", 96)
    providers = load_cfg().get("provider_order", ["groq", "cerebras", "mistral", "local"])
    models = load_cfg().get("models", {})
    rate = load_cfg().get("rate_limit", {})
    base = rate.get("backoff_base", 2.0)
    cap = rate.get("backoff_cap", 45.0)

    for attempt, prov in enumerate(providers):
        model = models.get(prov) or load_cfg()["providers"].get(prov, {}).get("default_model")
        content, tokens, err = call_provider(prov, model, prompt, max_tokens)
        if err:
            sleep = exponential_backoff(attempt, base, cap)
            print(json.dumps({"tid": tid, "provider": prov, "err": err, "sleep": round(sleep, 2), "attempt": attempt}), flush=True)
            time.sleep(sleep)
            continue

        conf = 0.92 if (len(content) > 12 and "ESCALATE" not in content.upper()) else 0.28
        result = {
            "tid": tid,
            "provider": prov,
            "model": model,
            "content": content,
            "tokens": tokens,
            "confidence": conf,
            "ts": datetime.now().isoformat(),
            "node": "N0_bottom_tier_leaf"
        }
        (OUT / f"{tid}.json").write_text(json.dumps(result, indent=2))
        if conf < 0.5:
            (PARKED / f"{tid}.json").write_text(json.dumps(task))
            status = "parked"
        else:
            (DONE / f"{tid}.json").write_text(json.dumps(result))
            status = "done"
        print(json.dumps({"tid": tid, "status": status, "tokens": tokens, "provider": prov, "conf": conf}), flush=True)
        return result

    (PARKED / f"{tid}.json").write_text(json.dumps(task))
    return {"tid": tid, "status": "parked", "reason": "all_providers_failed"}

def main():
    print(json.dumps({"node": "N0_bottom_tier", "status": "alive", "mold": "fractal-leaf"}), flush=True)
    while True:
        tasks = sorted(QUEUE.glob("*.json"))
        if not tasks:
            time.sleep(1.2)
            continue
        for tpath in tasks[:4]:  # fractal batch
            try:
                task = json.loads(tpath.read_text())
                tpath.unlink(missing_ok=True)
                process_leaf(task)
            except Exception as e:
                print(json.dumps({"err": str(e), "file": tpath.name}), flush=True)
                time.sleep(1.5)

if __name__ == "__main__":
    main()
