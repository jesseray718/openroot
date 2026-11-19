#!/usr/bin/env python3
import os
import sys

# Ensure local bin is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../bin")))

import flint_hybrid_client

def main():
    # Force offline mode to hit the local Ollama instance
    os.environ["OPENROOT_MODE"] = "offline"
    os.environ["OPENROOT_OFFLINE_ENDPOINT"] = "http://127.0.0.1:11434/v1"
    os.environ["OPENROOT_OFFLINE_MODEL"] = "local/qwen2.5-coder:7b"

    messages = [
        {"role": "system", "content": "You are a concise offline reasoning assistant."},
        {"role": "user", "content": "Output a JSON object with key 'status' set to 'ok' and key 'engine' set to 'ollama'."}
    ]

    print("[*] Sending test prompt to local Ollama instance...")
    try:
        response = flint_hybrid_client.ask_flint(messages)
        print("\n[+] Response received from local model:")
        print(response)
    except Exception as e:
        print(f"\n[-] Error connecting to local Ollama instance: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
