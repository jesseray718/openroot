#!/usr/bin/env python3
"""
Groq cascading fallback client - 2026 safe
Primary: openai/gpt-oss-120b → qwen/qwen3.6-27b → openai/gpt-oss-20b
Deprecation-safe: avoids llama-* models after 08/16/26
"""

import os
import sys
from groq import Groq, APIError, RateLimitError, APIStatusError

PREFERRED_MODELS = [
    "openai/gpt-oss-120b",
    "qwen/qwen3.6-27b",
    "openai/gpt-oss-20b",
]

def get_active_models(client):
    """Query /v1/models endpoint for ground-truth active list."""
    try:
        models = client.models.list()
        return {m.id for m in models.data}
    except Exception:
        return set(PREFERRED_MODELS)

def chat_with_fallback(prompt, api_key, max_tokens=1024, temperature=0.7):
    if not api_key:
        raise ValueError("GROQ_API_KEY is required")

    client = Groq(api_key=api_key)
    active = get_active_models(client)
    
    # Filter preferred models to only those currently active
    usable = [m for m in PREFERRED_MODELS if m in active]
    
    if not usable:
        usable = PREFERRED_MODELS  # Fallback to hardcoded if query fails
    
    for model in usable:
        try:
            print(f"[INFO] Using model: {model}", file=sys.stderr)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except RateLimitError as e:
            retry_after = getattr(e, 'retry_after', 5)
            print(f"[WARN] Rate limited on {model}, waiting {retry_after}s...", file=sys.stderr)
            import time
            time.sleep(retry_after)
            continue
        except APIStatusError as e:
            error_body = str(e.body) if hasattr(e, 'body') else str(e)
            if 'decommissioned' in error_body.lower():
                print(f"[WARN] Model {model} decommissioned, skipping...", file=sys.stderr)
                continue
            print(f"[ERR] Status error on {model}: {e.status_code}", file=sys.stderr)
            continue
        except Exception as e:
            print(f"[ERR] Error with {model}: {type(e).__name__}: {e}", file=sys.stderr)
            continue

    raise RuntimeError("All fallback models failed")

if __name__ == "__main__":
    # API KEY CONFIGURATION OPTIONS:
    # Option 1: Export before running: export GROQ_API_KEY="gsk_..."
    # Option 2: Pass directly: GROQ_API_KEY=gsk_... python3 groq_fallback.py ...
    # Get key from: https://console.groq.com/keys

    api_key = os.getenv("GROQ_API_KEY")
    
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "Hello from Termux"
        print("[WARN] No args provided, using default:", prompt, file=sys.stderr)

    try:
        result = chat_with_fallback(prompt, api_key or "")
        print("\n=== Response ===\n")
        print(result)
    except Exception as e:
        print(f"\n[FAILED]: {e}\n")
        sys.exit(1)
