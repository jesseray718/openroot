#!/usr/bin/env python3
"""Talk to the already-running llama-server. Do not launch a second model."""
from __future__ import annotations
import argparse, json, os, socket, sys, time, urllib.error, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("OPENROOT_ROOT", "/home/jesse/openroot"))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
from openroot_optimizer.coder_translate import read_in, wrap_prompt, write_out

API = os.environ.get("OPENROOT_LLAMA_API", "http://127.0.0.1:8080/v1/chat/completions")
MODEL = os.environ.get("OPENROOT_MODEL", "qwen2.5-coder-7b")
LEDGER = Path(os.environ.get("OPENROOT_LEDGER", str(ROOT / "closed-loop" / "ledger" / "eta-ledger.jsonl")))

def chat(messages, max_tokens, temperature):
    body = json.dumps({
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }).encode()
    req = urllib.request.Request(API, data=body, headers={"Content-Type": "application/json"})
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=300) as r:
        resp = json.loads(r.read())
    return resp, time.perf_counter() - t0

def hang(entry: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.open("a", encoding="utf-8").write(json.dumps(entry, separators=(",", ":")) + "\n")

def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="coder")
    p.add_argument("text", nargs="*", help="prompt words, or empty for --in")
    p.add_argument("--in", dest="inkind", default="raw", choices=["raw", "stdin", "file", "ledger-tail", "git-diff"])
    p.add_argument("--src", default="")
    p.add_argument("--mode", default="code", choices=["code", "explain", "json", "review", "raw"])
    p.add_argument("--out", dest="outkind", default="code", choices=["raw", "code", "json"])
    p.add_argument("--dest", default="-")
    p.add_argument("--max-tokens", type=int, default=1024)
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--no-ledger", action="store_true")
    args = p.parse_args(argv)

    if args.inkind in {"stdin", "file", "ledger-tail", "git-diff"}:
        user = read_in(args.inkind, args.src)
    else:
        user = " ".join(args.text).strip() or read_in("stdin", "")
    if not user.strip():
        print("empty prompt", file=sys.stderr)
        return 2

    try:
        resp, wall = chat(wrap_prompt(user, args.mode), args.max_tokens, args.temperature)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print("llama down at", API, ":", e, file=sys.stderr)
        print("start the server you already use. do not spawn a second 7B.", file=sys.stderr)
        return 3

    choice = (resp.get("choices") or [{}])[0]
    text = ((choice.get("message") or {}).get("content")) or choice.get("text") or ""
    usage = resp.get("usage") or {}
    out = write_out(args.outkind, text, None if args.dest == "-" else args.dest)
    if args.dest == "-":
        sys.stdout.write(out if out.endswith("\n") else out + "\n")

    if not args.no_ledger:
        hang({
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": "coder_infer",
            "hostname": socket.gethostname(),
            "model": MODEL,
            "backend": API,
            "mode": args.mode,
            "outkind": args.outkind,
            "prompt_chars": len(user),
            "out_chars": len(out),
            "wall_s": round(wall, 4),
            "total_tokens": usage.get("total_tokens", 0),
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "energy_grade": "UNAVAILABLE",
        })
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
