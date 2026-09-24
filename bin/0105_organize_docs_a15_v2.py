#!/usr/bin/env python3
"""A15 document map v2. Termux only.

Walks Download, Documents/Markor, /Markor, mesh outbox.
Dedupes by inode. HOME only with --include-home.
No mv, no rm, no GGUF.

  python3 /data/data/com.termux/files/home/wisdom-recovery/organize_docs_a15_v2.py doctor
  python3 /data/data/com.termux/files/home/wisdom-recovery/organize_docs_a15_v2.py map
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
import urllib.request
from pathlib import Path

CODER = "http://127.0.0.1:8080/v1/chat/completions"
MODEL = "qwen2.5-coder-7b"
TERMUX_HOME = Path("/data/data/com.termux/files/home")
MESH = Path("/storage/emulated/0/openroot")
HOME_OUT = TERMUX_HOME / "wisdom-recovery" / "doc-plan-20260906"
MESH_OUT = MESH / "outbox"
VERSION = "a15-v2-20260906"

ROOTS_DEFAULT = [
    Path("/storage/emulated/0/Download"),
    Path("/storage/emulated/0/Documents/Markor"),
    Path("/storage/emulated/0/Markor"),
    MESH / "outbox",
]
TEXT_SUFFIX = {".md", ".txt", ".rst", ".org", ".json", ".csv", ".py", ".sh", ".tsv"}
SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules", ".cache", ".stversions", "Android", "DCIM"}
SKIP_NAME_SUB = ("apitoken", "api_token", "id_ed25519", "wireguard")
MAX_CHARS = 1800
MAX_TOKENS = 200
MAX_MAP = 200000
MAX_PLAN = 40000


def die(msg: str, code: int = 2) -> None:
    print("FAIL", msg, file=sys.stderr)
    raise SystemExit(code)


def assert_a15() -> None:
    if os.getcwd().startswith("/home/jesse") or "optiplex" in os.uname().nodename.lower():
        die("wrong pane: A15-only")


def classify_path(path: Path) -> str:
    s = str(path)
    low = path.name.lower()
    if any(x in low for x in SKIP_NAME_SUB):
        return "secret_name"
    if s.startswith("/storage/emulated/0/Download"):
        if low.startswith("continuity") or low.startswith("handoff"):
            return "handoff_clone"
        if low.endswith(".json") and path.stat().st_size > 50000:
            return "chat_export"
        if path.suffix.lower() in {".py", ".sh"}:
            return "tool_script"
        return "download_inbox"
    if "/Documents/Markor" in s or "/Documents/markor" in s:
        return "markor_note"
    if s.startswith("/storage/emulated/0/Markor") or s.startswith("/storage/emulated/0/markor"):
        return "markor_edge"
    if "/openroot/outbox" in s:
        return "mesh_bus"
    if s.startswith(str(TERMUX_HOME)):
        return "home_scratch"
    return "other"


def doctor() -> int:
    assert_a15()
    print("VERSION", VERSION)
    print("pane", "A15")
    for r in ROOTS_DEFAULT + [TERMUX_HOME]:
        print("root", str(r), "exists", r.is_dir())
    HOME_OUT.mkdir(parents=True, exist_ok=True)
    MESH_OUT.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlopen("http://127.0.0.1:8080/v1/models", timeout=3).read()
        print("tunnel_8080", "UP")
    except Exception as e:
        print("tunnel_8080", "DOWN", str(e)[:80])
    print("DOCTOR_OK")
    return 0


def iter_unique(include_home: bool, limit: int, max_bytes: int):
    roots = list(ROOTS_DEFAULT)
    if include_home:
        roots.append(TERMUX_HOME)
    seen = set()
    n = 0
    for root in roots:
        if not root.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in sorted(filenames):
                p = Path(dirpath) / name
                if p.suffix.lower() not in TEXT_SUFFIX:
                    continue
                if any(s in name.lower() for s in SKIP_NAME_SUB):
                    print("SKIP_SECRET_NAME", p)
                    continue
                try:
                    st = p.stat()
                except OSError:
                    continue
                if st.st_size == 0 or st.st_size > max_bytes:
                    continue
                key = (st.st_dev, st.st_ino)
                if key in seen:
                    continue
                seen.add(key)
                yield p, st
                n += 1
                if limit and n >= limit:
                    return


def mesh_copy(src: Path) -> None:
    MESH_OUT.mkdir(parents=True, exist_ok=True)
    dest = MESH_OUT / src.name
    shutil.copy2(src, dest)
    print("MESH_COPY", dest)


def cmd_map(include_home: bool, limit: int) -> int:
    assert_a15()
    HOME_OUT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    tsv = HOME_OUT / ("a15-map-" + stamp + ".tsv")
    classes = {}
    n = 0
    with tsv.open("w") as f:
        f.write("class\tbytes\tino\tpath\n")
        for p, st in iter_unique(include_home, limit, MAX_MAP):
            cls = classify_path(p)
            classes[cls] = classes.get(cls, 0) + 1
            f.write("%s\t%s\t%s\t%s\n" % (cls, st.st_size, st.st_ino, p))
            n += 1
    print("VERSION", VERSION)
    print("WROTE", tsv)
    print("N", n)
    print("CLASSES", json.dumps(classes, sort_keys=True))
    mesh_copy(tsv)
    return 0


def ask_7b(path: Path, text: str) -> dict:
    payload = {
        "model": MODEL,
        "temperature": 0,
        "max_tokens": MAX_TOKENS,
        "messages": [
            {"role": "system", "content": "Return one JSON: class, action, dest, title, reason, n14_risk. No markdown. Download=inbox. Markor=notes. Do not delete."},
            {"role": "user", "content": "PATH: %s\nHINT: %s\n---\n%s" % (path, classify_path(path), text[:MAX_CHARS])},
        ],
    }
    req = urllib.request.Request(CODER, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    raw = json.loads(urllib.request.urlopen(req, timeout=120).read().decode())
    content = raw["choices"][0]["message"]["content"].strip().strip("`")
    if content.startswith("json"):
        content = content[4:].strip()
    try:
        obj = json.loads(content)
    except json.JSONDecodeError:
        obj = {"class": classify_path(path), "action": "keep", "dest": "same", "title": path.name, "reason": "no json", "n14_risk": False}
    obj["path"] = str(path)
    return obj


def cmd_plan(include_home: bool, limit: int) -> int:
    doctor()
    try:
        urllib.request.urlopen("http://127.0.0.1:8080/v1/models", timeout=3).read()
    except Exception:
        die("tunnel down")
    stamp = time.strftime("%Y%m%d-%H%M%S")
    tsv = HOME_OUT / ("a15-plan-" + stamp + ".tsv")
    n = 0
    with tsv.open("w") as tf:
        tf.write("path\tclass\taction\treason\n")
        for p, st in iter_unique(include_home, limit or 15, MAX_PLAN):
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            print("ASK", p)
            obj = ask_7b(p, text)
            tf.write("%s\t%s\t%s\t%s\n" % (obj.get("path"), obj.get("class"), obj.get("action"), str(obj.get("reason", "")).replace("\t", " ")[:200]))
            tf.flush()
            n += 1
    print("VERSION", VERSION)
    print("WROTE", tsv)
    print("N", n)
    mesh_copy(tsv)
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["doctor", "map", "census", "plan", "help"])
    ap.add_argument("--include-home", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv[1:])
    if args.cmd == "help":
        print(__doc__)
        return 0
    if args.cmd == "doctor":
        return doctor()
    if args.cmd in {"map", "census"}:
        return cmd_map(args.include_home, args.limit)
    return cmd_plan(args.include_home, args.limit)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
