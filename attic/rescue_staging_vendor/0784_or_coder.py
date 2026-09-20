#!/usr/bin/env python3
"""or-coder — query LAN Ollama. No cloud."""
from __future__ import annotations
import json, os, sys, urllib.request
from pathlib import Path

HOST = os.environ.get("CODE_NODE_HOST", "192.168.1.193")
PORT = int(os.environ.get("CODE_NODE_PORT", "11434"))
MODEL = os.environ.get("CODER_MODEL", "qwen2.5-coder:7b")
TIMEOUT = int(os.environ.get("CODER_TIMEOUT", "600"))

def mesh() -> Path:
    for p in (Path("/home/jesse/openroot"), Path("/storage/emulated/0/openroot")):
        if p.is_dir():
            return p
    return Path("/home/jesse/openroot")

def server() -> dict:
    man = mesh() / ".coder_node.json"
    try:
        data = json.loads(man.read_text(encoding="utf-8"))
        for n in data.get("nodes", []):
            if n.get("role") == "server":
                return n
    except Exception:
        pass
    return {"host": HOST, "port": PORT, "model": MODEL}

def api(path: str, method: str = "GET", data=None, timeout: int = 10):
    srv = server()
    url = "http://%s:%s%s" % (srv.get("host", HOST), srv.get("port", PORT), path)
    req = urllib.request.Request(url, method=method)
    if data is not None:
        req.data = json.dumps(data).encode()
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

def gen(prompt: str) -> str:
    srv = server()
    body = {"model": srv.get("model", MODEL), "prompt": prompt, "stream": False, "options": {"temperature": 0.2}}
    return api("/api/generate", method="POST", data=body, timeout=TIMEOUT)["response"]

def health() -> None:
    try:
        srv = server()
        tags = api("/api/tags")
        names = [m["name"] for m in tags.get("models", [])]
        print("ONLINE", "%s:%s" % (srv.get("host"), srv.get("port")))
        print("models", ",".join(names) if names else "none")
        print("active", srv.get("model", MODEL))
    except Exception as e:
        print("OFFLINE", e)

def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("help", "-h", "--help"):
        print("or-coder health|models|ask|review|fix|gen|diff")
        return 0
    cmd, rest = args[0], args[1:]
    if cmd == "health":
        health(); return 0
    if cmd == "models":
        for m in api("/api/tags").get("models", []):
            print(m.get("name"), m.get("size"))
        return 0
    if cmd == "ask":
        print(gen(" ".join(rest))); return 0
    if cmd in ("review", "fix", "diff"):
        text = Path(rest[0]).read_text(encoding="utf-8", errors="replace")
        if cmd == "review":
            print(gen("Review for bugs. Terse bullets.\n\n```\n%s\n```" % text))
        elif cmd == "fix":
            print(gen("Fix bugs. Return full file only.\n\n```\n%s\n```" % text))
        else:
            print(gen("Unified diff of correctness fixes.\n\n```\n%s\n```" % text))
        return 0
    if cmd == "gen":
        print(gen("Write Python with types. Request: " + " ".join(rest)))
        return 0
    print("unknown", cmd)
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
