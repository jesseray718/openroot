#!/usr/bin/env python3
"""In/out translators. Model stays stock qwen2.5-coder via llama-server."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

FENCE = re.compile(r"```(?:[\w.+-]*)\n(.*?)```", re.S)

def read_in(kind: str, src: str) -> str:
    if kind == "raw":
        return src
    if kind == "stdin":
        return sys.stdin.read()
    p = Path(src)
    if kind == "file":
        return p.read_text(encoding="utf-8", errors="replace")
    if kind == "ledger-tail":
        lines = [ln for ln in p.read_text(encoding="utf-8", errors="replace").splitlines() if ln.strip()]
        return "\n".join(lines[-20:])
    if kind == "git-diff":
        return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else src
    raise SystemExit("unknown in kind: " + kind)

def wrap_prompt(user: str, mode: str) -> list[dict]:
    # stock coder. no new personality. only task envelope.
    sysmsg = {
        "code": "You are Qwen2.5-Coder. Return one solution. Prefer a single fenced code block. No preamble.",
        "explain": "You are Qwen2.5-Coder. Explain the given code or error. Be direct. No marketing.",
        "json": "You are Qwen2.5-Coder. Return one JSON object only. No fences. No prose.",
        "review": "You are Qwen2.5-Coder. Review the diff. List bugs, then a patch hunk. No cheerleading.",
        "raw": "",
    }[mode]
    msgs = []
    if sysmsg:
        msgs.append({"role": "system", "content": sysmsg})
    msgs.append({"role": "user", "content": user})
    return msgs

def write_out(kind: str, text: str, dest: str | None) -> str:
    if kind == "raw":
        out = text
    elif kind == "code":
        m = FENCE.search(text)
        out = m.group(1) if m else text
    elif kind == "json":
        m = FENCE.search(text)
        body = m.group(1) if m else text
        s, e = body.find("{"), body.rfind("}")
        if s >= 0 and e > s:
            json.loads(body[s : e + 1])
            out = body[s : e + 1]
        else:
            out = body
    else:
        raise SystemExit("unknown out kind: " + kind)
    if dest and dest != "-":
        Path(dest).write_text(out if out.endswith("\n") else out + "\n", encoding="utf-8")
    return out
