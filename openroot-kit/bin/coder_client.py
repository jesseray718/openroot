#!/usr/bin/env python3
"""Offline-first 7B coder client. Phone or box. Never loads a GGUF itself."""
from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit_lib  # noqa: E402

# Box LAN. Do not use localhost from the phone.
ENDPOINT = "http://192.168.1.193:8080/v1/chat/completions"
MODELS = "http://192.168.1.193:8080/v1/models"
LOCAL_ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"
LOCAL_MODELS = "http://127.0.0.1:8080/v1/models"


def get(url: str, timeout: float = 4.0):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.loads(r.read().decode())


def post_chat(url: str, prompt: str, timeout: float = 120.0):
    body = json.dumps(
        {
            "model": "local-7b-coder",
            "messages": [
                {
                    "role": "system",
                    "content": "You are the OptiPlex 7B coder. Absolute paths. No tilde. Small diffs.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 512,
        }
    ).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.loads(r.read().decode())


def main(argv: list[str]) -> int:
    pane = kit_lib.detect_pane()
    action = argv[1] if len(argv) > 1 else "status"
    models_url = LOCAL_MODELS if pane == "SSH" else MODELS
    chat_url = LOCAL_ENDPOINT if pane == "SSH" else ENDPOINT
    report = {"pane": pane, "action": action, "models_url": models_url}
    try:
        code, data = get(models_url)
        report["models_http"] = code
        report["models"] = data
        report["server_up"] = True
    except Exception as e:
        report["server_up"] = False
        report["models_err"] = str(e)
        report["next"] = (
            "SSH: start llama-server against a GGUF in /home/jesse/models then rerun status"
            if pane != "A15"
            else "Box llama-server is down or firewall. Do not start 7B on the phone."
        )
        print(json.dumps(report, indent=2))
        return 2
    if action == "status":
        print(json.dumps(report, indent=2))
        return 0
    if action == "ask":
        prompt = " ".join(argv[2:]) or "Reply with the single word pong."
        try:
            code, data = post_chat(chat_url, prompt)
            text = data["choices"][0]["message"]["content"]
            report["ok"] = True
            report["reply"] = text
            h = hashlib.sha256(prompt.encode()).hexdigest()[:16]
            try:
                con = kit_lib.connect()
                con.execute(
                    """INSERT INTO coder_job(t,model,endpoint,prompt_hash,offline,ok,note)
                       VALUES(?,?,?,?,1,1,?)""",
                    (
                        time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "local-7b-coder",
                        chat_url,
                        h,
                        text[:180],
                    ),
                )
                con.commit()
            except Exception:
                pass
            print(json.dumps(report, indent=2))
            return 0
        except Exception as e:
            report["ok"] = False
            report["ask_err"] = str(e)
            print(json.dumps(report, indent=2))
            return 1
    print("usage: coder_client.py status|ask TEXT")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
