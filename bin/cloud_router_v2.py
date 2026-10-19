#!/usr/bin/env python3
"""OpenRoot Cloud Router v2 - rolling window tokens + OpenRouter + local models."""
import argparse, hashlib, json, os, sqlite3, sys, time, urllib.request, urllib.error
from pathlib import Path

REPO = Path(os.environ.get("OPENROOT_REPO", "/home/jesse/openroot"))
LEDGER = REPO / "data" / "cloud_token_ledger.db"

# Rolling window per provider (in seconds)
ROLLING_WINDOWS = {
    "openrouter": {"short_window": 60, "short_cap": 20, "long_window": 86400, "long_cap": 1000, "token_cap": 100000},
    "groq": {"short_window": 60, "short_cap": 30, "long_window": 86400, "long_cap": 14400, "token_cap": 30000},
    "gemini": {"short_window": 60, "short_cap": 15, "long_window": 86400, "long_cap": 1500, "token_cap": 1000000},
    "cerebras": {"short_window": 60, "short_cap": 30, "long_window": 86400, "long_cap": 14400, "token_cap": 30000},
    "cloudflare": {"short_window": 86400, "short_cap": 1000, "long_window": 86400, "long_cap": 1000, "token_cap": 10000},
}

MIN_TOKENS_TO_REENTER = 2000

# Local models in priority order
LOCAL_CHAIN = [
    {"name":"local", "model":"qwen2.5-coder:14b-instruct-q4_k_m", "role":"coder", "token_cap":999999, "rolling":False},
    {"name":"local", "model":"qwen2.5-coder:7b-instruct", "role":"coder", "token_cap":999999, "rolling":False},
    {"name":"local", "model":"qwen3:1.7b", "role":"router", "token_cap":999999, "rolling":False},
    {"name":"local", "model":"qwen2.5:3b", "role":"general", "token_cap":999999, "rolling":False},
]

# Cloud provider chain
DEFAULT_CHAIN = [
    {"name":"openrouter", "base_url":"https://openrouter.ai/api/v1",
     "free_models":["meta-llama/llama-3.3-70b-instruct:free","google/gemini-2.0-flash-exp:free","qwen/qwen-2.5-72b-instruct:free","deepseek/deepseek-r1:free"]},
    {"name":"groq", "base_url":"https://api.groq.com/openai/v1",
     "free_models":["meta-llama/llama-3.3-70b-instruct:free","google/gemini-2.0-flash-exp:free","qwen/qwen-2.5-72b-instruct:free","deepseek/deepseek-r1:free"]},
    {"name":"gemini", "base_url":"https://generativelanguage.googleapis.com/v1beta",
     "free_models":["meta-llama/llama-3.3-70b-instruct:free","google/gemini-2.0-flash-exp:free","qwen/qwen-2.5-72b-instruct:free","deepseek/deepseek-r1:free"]},
    {"name":"cerebras", "base_url":"https://api.cerebras.ai/v1",
     "free_models":["meta-llama/llama-3.3-70b-instruct:free","google/gemini-2.0-flash-exp:free","qwen/qwen-2.5-72b-instruct:free","deepseek/deepseek-r1:free"]},
    {"name":"cloudflare", "base_url":"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai",
     "free_models":["meta-llama/llama-3.3-70b-instruct:free","google/gemini-2.0-flash-exp:free","qwen/qwen-2.5-72b-instruct:free","deepseek/deepseek-r1:free"]},
]

def init_ledger():
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(LEDGER))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS call_log (
            ts TEXT, provider TEXT, model TEXT,
            prompt_tokens INTEGER, completion_tokens INTEGER,
            latency_ms INTEGER, success INTEGER, error TEXT,
            receipt_id TEXT);
        CREATE INDEX IF NOT EXISTS idx_ts_provider ON call_log(ts, provider);
    """)
    return conn

def load_keys():
    """Load keys: checks data/cloud_keys.json first, falls back to cloud_keys.json"""
    candidates = [
        REPO / "data" / "cloud_keys.json",
        REPO / "cloud_keys.json"
    ]
    for p in candidates:
        if p.exists():
            try:
                return json.loads(p.read_text())
            except Exception as e:
                print(f"[held] Error parsing {p}: {e}", file=sys.stderr)
    return {}

def get_rolling_remaining(conn, provider):
    cfg = ROLLING_WINDOWS.get(provider)
    if not cfg:
        return 999999, 999999
    now = time.time()
    short_cutoff = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - cfg["short_window"]))
    long_cutoff = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - cfg["long_window"]))
    
    cur = conn.execute("""SELECT COALESCE(SUM(prompt_tokens + completion_tokens), 0), COUNT(*)
                          FROM call_log WHERE provider=? AND ts >= ?""",
                       (provider, long_cutoff))
    long_tokens, long_requests = cur.fetchone()
    
    cur = conn.execute("""SELECT COUNT(*) FROM call_log WHERE provider=? AND ts >= ?""",
                       (provider, short_cutoff))
    short_requests = cur.fetchone()[0]
    
    tokens_remaining = max(0, cfg["token_cap"] - long_tokens)
    long_req_remaining = max(0, cfg["long_cap"] - long_requests)
    short_req_remaining = max(0, cfg["short_cap"] - short_requests)
    
    return tokens_remaining, min(long_req_remaining, short_req_remaining)

def is_eligible_to_reenter(conn, provider, min_tokens=MIN_TOKENS_TO_REENTER):
    tokens_remaining, req_remaining = get_rolling_remaining(conn, provider)
    return tokens_remaining >= min_tokens and req_remaining >= 1

def call_local(model, prompt, max_tokens=500):
    import subprocess
    try:
        t0 = time.time()
        r = subprocess.run(["ollama", "run", model, prompt],
            capture_output=True, text=True, timeout=180,
            stdin=subprocess.DEVNULL)
        latency = int((time.time() - t0) * 1000)
        if r.returncode != 0:
            return None, f"ollama_error: {r.stderr[:200]}"
        est_tokens = len(r.stdout) // 4
        return {
            "content": r.stdout,
            "prompt_tokens": len(prompt) // 4,
            "completion_tokens": est_tokens,
            "latency_ms": latency,
            "model": model,
            "provider": "local",
        }, None
    except Exception as e:
        return None, str(e)

def call_cloud_provider(provider_cfg, keys, model, prompt, max_tokens=500):
    name = provider_cfg["name"]
    if name not in keys or str(keys[name]).startswith("REPLACE"):
        return None, "no_api_key"
    api_key = keys[name]
    url = provider_cfg["base_url"] + "/chat/completions"
    body = json.dumps({
        "model": model,
        "messages": [{"role":"user","content":prompt}],
        "max_tokens": max_tokens,
    }).encode("utf-8")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    # OpenRouter specific headers
    if name == "openrouter":
        headers["HTTP-Referer"] = "https://github.com/jesseray718/openroot"
        headers["X-Title"] = "OpenRoot Autonomous Pod Engine"

    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read())
        latency = int((time.time() - t0) * 1000)
        usage = data.get("usage", {})
        return {
            "content": data["choices"][0]["message"]["content"],
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "latency_ms": latency,
            "model": model,
            "provider": name,
        }, None
    except urllib.error.HTTPError as e:
        body = e.read()[:200].decode('utf-8', errors='replace')
        return None, f"http_{e.code}: {body}"
    except Exception as e:
        return None, str(e)

def log_call(conn, provider, model, pt, ct, latency_ms, success, error, receipt_id):
    conn.execute("""INSERT INTO call_log VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
         provider, model, pt, ct, latency_ms, success, error, receipt_id))
    conn.commit()

def route(prompt, preferred_model=None, max_tokens=500, prefer_local=False, role=None):
    conn = init_ledger()
    keys = load_keys()
    receipt = {
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "providers_tried": [],
        "success": False,
        "role": role,
    }
    
    cascade = []
    
    # 1. Local models first if explicitly requested or role specified
    if prefer_local or role:
        for local_cfg in LOCAL_CHAIN:
            if role and local_cfg["role"] != role:
                continue
            cascade.append(("local", local_cfg))
    
    # 2. Cloud cascade in priority order
    for provider_cfg in DEFAULT_CHAIN:
        name = provider_cfg["name"]
        if name in keys and not str(keys[name]).startswith("REPLACE"):
            if is_eligible_to_reenter(conn, name):
                cascade.append(("cloud", provider_cfg))
            else:
                receipt["providers_tried"].append({"provider":name, "status":"exhausted_wait_replenish"})
    
    # 3. Fallback to local if not already attempted
    if not prefer_local and not role:
        for local_cfg in LOCAL_CHAIN:
            if local_cfg["role"] == "general":
                cascade.append(("local", local_cfg))
                break
    
    for kind, cfg in cascade:
        if kind == "local":
            model = preferred_model or cfg["model"]
            result, err = call_local(model, prompt, max_tokens)
            provider_name = "local"
        else:
            model = preferred_model or cfg["free_models"][0]
            result, err = call_cloud_provider(cfg, keys, model, prompt, max_tokens)
            provider_name = cfg["name"]
        
        if result:
            log_call(conn, provider_name, model,
                result["prompt_tokens"], result["completion_tokens"],
                result["latency_ms"], 1, None, receipt["prompt_sha256"])
            receipt["providers_tried"].append({
                "provider": provider_name, "status": "success",
                "model": model, "latency_ms": result["latency_ms"]
            })
            receipt["response"] = result["content"]
            receipt["provider"] = provider_name
            receipt["model"] = model
            receipt["tokens"] = result["prompt_tokens"] + result["completion_tokens"]
            receipt["success"] = True
            conn.close()
            return receipt
        else:
            receipt["providers_tried"].append({
                "provider": provider_name, "status": "failed", "error": err
            })
            log_call(conn, provider_name, model, 0, 0, 0, 0, err, receipt["prompt_sha256"])
    
    conn.close()
    return receipt

def main():
    p = argparse.ArgumentParser(description="OpenRoot Cloud Router v2")
    p.add_argument("--prompt", required=True)
    p.add_argument("--model", default=None)
    p.add_argument("--max-tokens", type=int, default=500)
    p.add_argument("--prefer-local", action="store_true")
    p.add_argument("--role", choices=["coder","router","general"], default=None)
    args = p.parse_args()
    print(f"[gate] CANARY:OPENROOT-CLOUD-ROUTER-V2 {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}", file=sys.stderr)
    r = route(args.prompt, args.model, args.max_tokens, args.prefer_local, args.role)
    print(json.dumps(r, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
