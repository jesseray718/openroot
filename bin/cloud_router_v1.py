# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""OpenRoot Cloud Router v1 - cascade free-tier APIs with token bucket rotation."""
import argparse, json, os, sqlite3, sys, time
from pathlib import Path

REPO = Path(os.environ.get("OPENROOT_REPO", "/home/jesse/openroot"))
LEDGER = REPO / "data" / "cloud_token_ledger.db"
KEYS_FILE = REPO / "data" / "cloud_keys.json"

# Provider chain in priority order. Add/remove as you acquire keys.
# Each provider has: name, base_url, free_models, daily_token_cap, daily_request_cap
DEFAULT_CHAIN = [
    {"name":"openrouter", "base_url":"https://openrouter.ai/api/v1",
     "free_models":["meta-llama/llama-3.3-70b-instruct","google/gemini-2.0-flash-exp:free","qwen/qwen-2.5-72b-instruct:free"],
     "daily_token_cap":200000, "daily_request_cap":1000},
    {"name":"groq", "base_url":"https://api.groq.com/openai/v1",
     "free_models":["llama-3.3-70b-versatile","qwen-2.5-32b"],
     "daily_token_cap":30000, "daily_request_cap":14400},
    {"name":"gemini", "base_url":"https://generativelanguage.googleapis.com/v1beta",
     "free_models":["gemini-2.0-flash","gemini-1.5-flash"],
     "daily_token_cap":1000000, "daily_request_cap":1500},
    {"name":"cerebras", "base_url":"https://api.cerebras.ai/v1",
     "free_models":["llama-3.3-70b"],
     "daily_token_cap":30000, "daily_request_cap":14400},
    {"name":"cloudflare", "base_url":"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai",
     "free_models":["@cf/meta/llama-3.3-70b-instruct-fp8-fast"],
     "daily_token_cap":10000, "daily_request_cap":1000},
]

def init_ledger():
    conn = sqlite3.connect(str(LEDGER))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS token_usage (
            date TEXT, provider TEXT,
            requests_used INTEGER DEFAULT 0,
            prompt_tokens_used INTEGER DEFAULT 0,
            completion_tokens_used INTEGER DEFAULT 0,
            PRIMARY KEY (date, provider));
        CREATE TABLE IF NOT EXISTS call_log (
            ts TEXT, provider TEXT, model TEXT,
            prompt_tokens INTEGER, completion_tokens INTEGER,
            latency_ms INTEGER, success INTEGER, error TEXT,
            receipt_id TEXT);
    """)
    return conn

def load_keys():
    if not KEYS_FILE.exists():
        print(f"[held] {KEYS_FILE} missing - create it with provider:apikey pairs", file=sys.stderr)
        sys.exit(1)
    return json.loads(KEYS_FILE.read_text())

def get_remaining(conn, provider, cap_tokens, cap_requests):
    today = time.strftime("%Y-%m-%d", time.gmtime())
    cur = conn.execute("SELECT requests_used, prompt_tokens_used, completion_tokens_used FROM token_usage WHERE date=? AND provider=?", (today, provider))
    row = cur.fetchone()
    if not row:
        return cap_tokens, cap_requests
    req_used, pt_used, ct_used = row
    tokens_used = pt_used + ct_used
    return max(0, cap_tokens - tokens_used), max(0, cap_requests - req_used)

def consume(conn, provider, prompt_tokens, completion_tokens):
    today = time.strftime("%Y-%m-%d", time.gmtime())
    conn.execute("""INSERT INTO token_usage (date, provider, requests_used, prompt_tokens_used, completion_tokens_used)
        VALUES (?, ?, 1, ?, ?)
        ON CONFLICT(date, provider) DO UPDATE SET
            requests_used = requests_used + 1,
            prompt_tokens_used = prompt_tokens_used + ?,
            completion_tokens_used = completion_tokens_used + ?""",
        (today, provider, prompt_tokens, completion_tokens, prompt_tokens, completion_tokens))
    conn.commit()

def log_call(conn, provider, model, pt, ct, latency_ms, success, error, receipt_id):
    conn.execute("""INSERT INTO call_log VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
         provider, model, pt, ct, latency_ms, success, error, receipt_id))
    conn.commit()

def call_provider(provider_cfg, keys, model, prompt, max_tokens=500):
    import urllib.request, urllib.error
    name = provider_cfg["name"]
    if name not in keys:
        return None, "no_api_key"
    api_key = keys[name]
    url = provider_cfg["base_url"] + "/chat/completions"
    body = json.dumps({
        "model": model,
        "messages": [{"role":"user","content":prompt}],
        "max_tokens": max_tokens,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type":"application/json"
    })
    try:
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=60) as resp:
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
        return None, f"http_{e.code}: {e.read()[:200].decode('utf-8', errors='replace')}"
    except Exception as e:
        return None, str(e)

def route(prompt, preferred_model=None, max_tokens=500, fallback_to_local=True):
    """Try providers in priority order. Fall to next if rate-limited. Return receipt."""
    conn = init_ledger()
    keys = load_keys()
    receipt = {
        "prompt_sha256": __import__("hashlib").sha256(prompt.encode()).hexdigest(),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "providers_tried": [],
        "success": False,
    }
    for provider_cfg in DEFAULT_CHAIN:
        name = provider_cfg["name"]
        model = preferred_model or provider_cfg["free_models"][0]
        tokens_left, reqs_left = get_remaining(conn, name,
            provider_cfg["daily_token_cap"], provider_cfg["daily_request_cap"])
        if tokens_left < max_tokens or reqs_left < 1:
            receipt["providers_tried"].append({"provider":name, "status":"exhausted",
                "tokens_remaining":tokens_left})
            continue
        result, err = call_provider(provider_cfg, keys, model, prompt, max_tokens)
        if result:
            consume(conn, name, result["prompt_tokens"], result["completion_tokens"])
            log_call(conn, name, model, result["prompt_tokens"],
                result["completion_tokens"], result["latency_ms"], 1, None, receipt["prompt_sha256"])
            receipt["providers_tried"].append({"provider":name, "status":"success",
                "model":model, "latency_ms":result["latency_ms"]})
            receipt["response"] = result["content"]
            receipt["provider"] = name
            receipt["model"] = model
            receipt["tokens"] = result["prompt_tokens"] + result["completion_tokens"]
            receipt["success"] = True
            conn.close()
            return receipt
        else:
            receipt["providers_tried"].append({"provider":name, "status":"failed", "error":err})
            log_call(conn, name, model, 0, 0, 0, 0, err, receipt["prompt_sha256"])
            if "rate_limit" in err or "429" in err:
                continue
            else:
                continue
    if fallback_to_local:
        receipt["providers_tried"].append({"provider":"local", "status":"fallback"})
        try:
            import subprocess
            r = subprocess.run(["ollama","run","qwen2.5:3b",prompt],
                capture_output=True, text=True, timeout=120)
            receipt["response"] = r.stdout
            receipt["provider"] = "local"
            receipt["model"] = "qwen2.5:3b"
            receipt["success"] = True
        except Exception as e:
            receipt["error"] = f"local_fallback_failed: {e}"
    conn.close()
    return receipt

def main():
    p = argparse.ArgumentParser(description="OpenRoot Cloud Router v1")
    p.add_argument("--prompt", required=True)
    p.add_argument("--model", default=None)
    p.add_argument("--max-tokens", type=int, default=500)
    p.add_argument("--no-local-fallback", action="store_true")
    args = p.parse_args()
    print(f"[gate] CANARY:OPENROOT-CLOUD-ROUTER-V1 {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}", file=sys.stderr)
    r = route(args.prompt, args.model, args.max_tokens, fallback_to_local=not args.no_local_fallback)
    print(json.dumps(r, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
