#!/usr/bin/env python3
"""OpenRoot self-observing inventory + circuit registry.
η = useful_joules / human_joules. This script maximises the denominator reduction.
"""
import os, json, hashlib, time, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

HOME = Path("/data/data/com.termux/files/home")
SD = Path("/sdcard/openroot")
ROOTS = [
    HOME / "openroot",
    HOME / "une",
    HOME / "black-locust-rmh",
    HOME / "agape-une",
    HOME / "computational_flow",
    SD,
    HOME / "wiki",
]
CIRCUITS_DIR = SD / "circuits"
INDEX_JSON = SD / "context_bridge" / "circuits_index.json"
INDEX_MD = SD / "INDEX.md"
STATUS_JSON = SD / "context_bridge" / "status.json"
LEDGER = SD / "ledger" / "eta_log.jsonl"

def sha(p: Path) -> str:
    try:
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()[:16]
    except Exception:
        return "ERR"

def walk():
    nodes = []
    for root in ROOTS:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            # skip noise
            dirnames[:] = [d for d in dirnames if d not in {".git", "__pycache__", "node_modules", ".cache", "tmp", "temp"}]
            for fn in filenames:
                p = Path(dirpath) / fn
                rel = str(p.relative_to(root)) if root in p.parents else str(p)
                try:
                    st = p.stat()
                    size = st.st_size
                    mtime = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat()
                except Exception:
                    size, mtime = 0, ""
                nodes.append({
                    "path": str(p),
                    "rel": rel,
                    "root": str(root),
                    "size": size,
                    "mtime": mtime,
                    "sha16": sha(p) if size < 8_000_000 else "large",
                    "ext": p.suffix.lower(),
                    "is_script": p.suffix in {".py", ".sh", ".bash"} or (p.is_file() and os.access(p, os.X_OK)),
                })
    return nodes

def load_circuits():
    CIRCUITS_DIR.mkdir(parents=True, exist_ok=True)
    circuits = {}
    for f in CIRCUITS_DIR.glob("*.json"):
        try:
            circuits[f.stem] = json.loads(f.read_text())
        except Exception:
            pass
    return circuits

def write_index(nodes, circuits):
    INDEX_JSON.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "node_count": len(nodes),
        "circuit_count": len(circuits),
        "nodes": nodes,
        "circuits": circuits,
    }
    INDEX_JSON.write_text(json.dumps(data, indent=2))
    # human readable
    lines = [
        f"# OpenRoot INDEX — {data['generated']}",
        f"nodes: {len(nodes)} | circuits: {len(circuits)}",
        "",
        "## Circuits (runnable)",
    ]
    for name, c in sorted(circuits.items()):
        lines.append(f"- `{name}` → {c.get('cmd','?')}  | η-note: {c.get('eta_note','')}")
    lines.append("")
    lines.append("## High-value scripts (auto-detected)")
    scripts = [n for n in nodes if n["is_script"] and n["size"] > 50]
    for n in sorted(scripts, key=lambda x: x["mtime"], reverse=True)[:40]:
        lines.append(f"- `{n['path']}` ({n['size']} B)")
    INDEX_MD.write_text("\n".join(lines))
    return data

def write_status(data):
    st = {
        "ts": data["generated"],
        "nodes": data["node_count"],
        "circuits": data["circuit_count"],
        "index": str(INDEX_JSON),
        "index_md": str(INDEX_MD),
    }
    STATUS_JSON.write_text(json.dumps(st, indent=2))
    print(json.dumps(st, indent=2))

def main():
    print("=== OpenRoot self-inventory ===")
    nodes = walk()
    circuits = load_circuits()
    data = write_index(nodes, circuits)
    write_status(data)
    print(f"INDEX written → {INDEX_MD}")
    print(f"JSON index  → {INDEX_JSON}")
    print("Done. Run any registered circuit with: openroot-run <name>")

if __name__ == "__main__":
    main()
