#!/usr/bin/env python3
"""OpenRoot local ask — OptiPlex llama.cpp OpenAI-compat. stdlib only."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

DEFAULT_BASE = "http://127.0.0.1:8080/v1"
DEFAULT_MODEL = "qwen2.5-coder-7b"
DEFAULT_TIMEOUT = 180


def post_json(url, payload, timeout):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise SystemExit("HTTP %s %s\n%s" % (e.code, url, err))
    except urllib.error.URLError as e:
        raise SystemExit("URL error %s : %s" % (url, e.reason))


def get_json(url, timeout):
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise SystemExit("URL error %s : %s" % (url, e.reason))


def extract_text(obj):
    if "choices" in obj and obj["choices"]:
        c0 = obj["choices"][0]
        msg = c0.get("message") or {}
        if msg.get("content"):
            return msg["content"]
        if c0.get("text"):
            return c0["text"]
    if "content" in obj:
        return str(obj["content"])
    return json.dumps(obj, indent=2)


def main():
    p = argparse.ArgumentParser(description="Ask local llama.cpp on OptiPlex")
    p.add_argument("prompt", nargs="*", help="prompt words")
    p.add_argument("--base", default=os.environ.get("OPENROOT_LLM_BASE", DEFAULT_BASE))
    p.add_argument("--model", default=os.environ.get("OPENROOT_LLM_MODEL", DEFAULT_MODEL))
    p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    p.add_argument("--max-tokens", type=int, default=512)
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--system", default="You are the OpenRoot local spoke. Absolute paths. eta = useful_joules / human_joules. Be exact.")
    p.add_argument("--raw", action="store_true")
    p.add_argument("--models", action="store_true")
    p.add_argument("--out", default="")
    args = p.parse_args()

    if args.models:
        print(json.dumps(get_json(args.base.rstrip("/") + "/models", 8), indent=2))
        return 0

    prompt = " ".join(args.prompt).strip()
    if not prompt and not sys.stdin.isatty():
        prompt = sys.stdin.read().strip()
    if not prompt:
        raise SystemExit("usage: local_ask.py [--models] PROMPT")

    t0 = time.time()
    payload = {
        "model": args.model,
        "messages": [
            {"role": "system", "content": args.system},
            {"role": "user", "content": prompt},
        ],
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }
    obj = post_json(args.base.rstrip("/") + "/chat/completions", payload, args.timeout)
    dt = time.time() - t0
    text = extract_text(obj)
    if args.raw:
        print(json.dumps(obj, indent=2))
    else:
        sys.stdout.write(text if text.endswith("\n") else text + "\n")
        usage = obj.get("usage") or {}
        sys.stderr.write(
            "eta_note model=%s seconds=%.2f prompt_tokens=%s completion_tokens=%s\n"
            % (
                args.model,
                dt,
                usage.get("prompt_tokens", "?"),
                usage.get("completion_tokens", "?"),
            )
        )
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text if text.endswith("\n") else text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
