#!/usr/bin/env python3
"""Coder node register. Does not touch Syncthing, SSH keys, or git."""
from __future__ import annotations
import json, os, shutil, socket, subprocess, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROLE = os.environ.get("ROLE", "")
HOST = os.environ.get("CODE_NODE_HOST", "192.168.1.193")
PORT = int(os.environ.get("CODE_NODE_PORT", "11434"))
MODEL = os.environ.get("CODER_MODEL", "qwen2.5-coder:7b")

def mesh_root() -> Path:
    if Path("/home/jesse/openroot").is_dir():
        return Path("/home/jesse/openroot")
    if Path("/storage/emulated/0/openroot").is_dir():
        return Path("/storage/emulated/0/openroot")
    raise SystemExit("no live openroot mesh path")

def ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(msg: str) -> None:
    print(msg)
    p = mesh_root() / "outbox" / "CODER.log"
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(p.read_text(encoding="utf-8") + msg + "\n" if p.exists() else msg + "\n", encoding="utf-8")
    except OSError:
        pass

def local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return HOST
    finally:
        s.close()

def detect_role() -> str:
    if ROLE in ("optiplex", "phone"):
        return ROLE
    hn = socket.gethostname()
    if "optiplex" in hn or Path("/home/jesse/openroot").is_dir() and not Path("/data/data/com.termux").exists():
        return "optiplex"
    return "phone"

def api(path: str, host: str = None, timeout: int = 8):
    url = "http://%s:%s%s" % (host or HOST, PORT, path)
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read().decode())

def reachable(host: str = None) -> bool:
    try:
        api("/api/tags", host=host or HOST, timeout=5)
        return True
    except Exception:
        return False

def load_json(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_json(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

def upsert(nodes: list, entry: dict) -> list:
    key = (entry.get("host"), entry.get("port"))
    out = [n for n in nodes if (n.get("host"), n.get("port")) != key]
    out.append(entry)
    return out

def setup_optiplex() -> None:
    root = mesh_root()
    ip = local_ip()
    log("role optiplex ip %s" % ip)
    if not shutil.which("ollama"):
        log("ollama missing. install then rerun:")
        log("curl -fsSL https://ollama.com/install.sh | sh")
        log("do not sudo this script. bind after install:")
        log("mkdir -p /home/jesse/.config/ollama")
        log("export OLLAMA_HOST=0.0.0.0:11434")
        log("systemctl --user enable --now ollama || ollama serve")
    else:
        log("ollama present")
        if reachable("127.0.0.1"):
            tags = api("/api/tags", host="127.0.0.1")
            names = [m.get("name", "") for m in tags.get("models", [])]
            log("models %s" % names)
            if not any(MODEL.split(":")[0] in n for n in names):
                log("pull %s" % MODEL)
                subprocess.run(["ollama", "pull", MODEL], check=False)
        else:
            log("ollama not listening on 127.0.0.1:11434. start: OLLAMA_HOST=0.0.0.0:11434 ollama serve")
    man_p = root / ".coder_node.json"
    man = load_json(man_p)
    man["nodes"] = upsert(man.get("nodes", []), {
        "host": ip, "port": PORT, "model": MODEL, "role": "server",
        "device": "OptiPlex", "registered": ts(),
        "status": "online" if reachable("127.0.0.1") else "offline",
    })
    man["last_sync"] = ts()
    man["n14"] = "coder node is LAN inference, not a pad hang"
    save_json(man_p, man)
    st_p = root / ".session_state.json"
    st = load_json(st_p)
    st["coder_nodes"] = man["nodes"]
    st["coder_node_initialized"] = True
    st["last_updated"] = ts()
    if st.get("next_action") in (None, "idle", "setup_coder_node"):
        st["next_action"] = "idle"
    save_json(st_p, st)
    log("wrote %s" % man_p)

def setup_phone() -> None:
    root = mesh_root()
    home = Path("/data/data/com.termux/files/home")
    bindir = home / "bin"
    bindir.mkdir(parents=True, exist_ok=True)
    src = Path("/home/jesse/knowledge/or_coder.py")
    if not src.exists():
        src = root / "bin" / "or_coder.py"
    dest = bindir / "or-coder"
    if src.exists():
        dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        dest.chmod(0o755)
        log("deployed %s" % dest)
    man_p = root / ".coder_node.json"
    man = load_json(man_p)
    man["nodes"] = upsert(man.get("nodes", []), {
        "host": HOST, "port": PORT, "model": MODEL, "role": "server",
        "device": "OptiPlex", "registered": ts(),
        "status": "online" if reachable(HOST) else "pending",
    })
    man["last_sync"] = ts()
    save_json(man_p, man)
    log("phone reachable %s" % reachable(HOST))

def main() -> int:
    role = detect_role()
    log("ROLE %s HOST %s:%s MODEL %s" % (role, HOST, PORT, MODEL))
    if role == "optiplex":
        setup_optiplex()
    else:
        setup_phone()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
