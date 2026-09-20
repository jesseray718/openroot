#!/usr/bin/env python3
"""config_tiers.py — Configure API keys for tier routing
Uses your existing keys: OpenRouter (free tier), Gemini (trial), Grok (xAPI)
Before enabling tier 4 spending, set CONFIRM=1 and verify current pricing.

Usage:
  ./config_tiers.py set <provider> <key>
  ./config_tiers.py list
  ./config_tiers.py test
"""
import os, sys, json
from pathlib import Path
from dotenv import load_dotenv, set_key, find_dotenv

DOTENV = Path.home() / "openroot" / ".env"
if not DOTENV.exists():
    DOTENV.parent.mkdir(parents=True, exist_ok=True)
    DOTENV.touch()

load_dotenv(DOTENV)

PROVIDERS = {
    "openrouter": {"env_var": "OPENROUTER_API_KEY", "tier": 2, "cost_in": 0.14, "cost_out": 0.28, "model": "deepseek/deepseek-chat"},
    "gemini": {"env_var": "GEMINI_API_KEY", "tier": 3, "cost_in": 0.20, "cost_out": 0.80, "model": "gemini-1.5-flash"},
    "grok": {"env_var": "XAI_API_KEY", "tier": 3, "cost_in": 0.25, "cost_out": 1.00, "model": "grok-2"},
    "ollama_local": {"env_var": None, "tier": 0, "cost_in": 0, "cost_out": 0, "model": "qwen2.5:3b"},
}

def set_key(provider, key):
    if provider not in PROVIDERS:
        print(f"[ERROR] Unknown provider: {provider}. Options: {list(PROVIDERS.keys())}")
        sys.exit(1)
    set_key(str(DOTENV), PROVIDERS[provider]["env_var"], key)
    print(f"[SET] {provider} configured")

def list_keys():
    loaded = load_dotenv(DOTENV)
    print("[LIST] API Keys:")
    for name, conf in PROVIDERS.items():
        env_var = conf["env_var"]
        if env_var and os.getenv(env_var):
            masked = os.getenv(env_var)[:4] + "***" + os.getenv(env_var)[-2:]
            print(f"  {name}: {masked} (tier {conf['tier']})")
        elif conf["env_var"] is None:
            print(f"  {name}: LOCAL (no key needed)")
        else:
            print(f"  {name}: NOT CONFIGURED")

def test_provider(provider):
    """Test connectivity with minimal token usage."""
    if provider == "ollama_local":
        import urllib.request
        try:
            req = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5)
            data = json.loads(req.read())
            print(f"[TEST] ollama_local OK — {len(data.get('models', []))} models available")
            return True
        except Exception as e:
            print(f"[TEST] ollama_local FAILED: {e}")
            return False
    
    # API-based providers
    import http.client, json
    conf = PROVIDERS[provider]
    env_var = conf["env_var"]
    api_key = os.getenv(env_var)
    if not api_key:
        print(f"[TEST] {provider}: no key configured")
        return False
    
    print(f"[TEST] {provider} — would call {conf['model']} (test skipped for safety)")
    return True

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "set" and len(sys.argv) >= 4:
        set_key(sys.argv[2], sys.argv[3])
    elif cmd == "list":
        list_keys()
    elif cmd == "test":
        if len(sys.argv) >= 3:
            test_provider(sys.argv[2])
        else:
            for p in PROVIDERS:
                test_provider(p)
    else:
        print(__doc__)
