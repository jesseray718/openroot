#!/usr/bin/env python3
"""env_map.py — Map environment state to data/env_map.json"""
import os, sys, json, socket
from datetime import datetime, timezone
from pathlib import Path

OUTPUT = os.getenv("ENV_MAP_OUTPUT", "/home/jesse/openroot/data/env_map.json")
if "/data/data/com.termux" in os.path.expanduser("~"):
    OUTPUT = str(Path.home() / "openroot" / "data" / "env_map.json")

def main():
    env_map = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "machine": socket.gethostname(),
        "user": os.environ.get("USER", "unknown"),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "ollama_url": os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
        "agent_model": os.environ.get("AGENT_MODEL", "qwen2.5-coder:7b"),
        "grader_model": os.environ.get("GRADER_MODEL", "qwen2.5:3b"),
        "embed_model": os.environ.get("EMBED_MODEL", "nomic-embed-text"),
        "home": str(Path.home()),
        "git_user": os.environ.get("GIT_AUTHOR_NAME", ""),
        "git_email": os.environ.get("GIT_AUTHOR_EMAIL", "")
    }
    with open(OUTPUT, "w") as f:
        json.dump(env_map, f, indent=2)
    print(f"[BANKED] {OUTPUT}")

if __name__ == "__main__":
    main()
