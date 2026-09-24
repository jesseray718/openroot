#!/usr/bin/env python3
"""A15 document census + optional 7B labels via tunnel.

Pane: Termux on SM-A156U only. Refuses jesse@optiplex3060.
No mv, no rm, no GGUF, no Termux syncthing serve.

  python3 /data/data/com.termux/files/home/wisdom-recovery/organize_docs_a15.py doctor
  python3 /data/data/com.termux/files/home/wisdom-recovery/organize_docs_a15.py census
  python3 /data/data/com.termux/files/home/wisdom-recovery/organize_docs_a15.py plan --limit 20
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
TEXT_SUFFIX = {".md", ".txt", ".rst", ".org", ".json", ".csv"}
SKIP_DIRS = {
    ".git", ".venv", "__pycache__", "node_modules", ".cache",
    ".stversions", "Android", "DCIM", "Movies", "Music", "Notifications",
    "Ringtones", "Alarms", "Audiobooks", "Podcasts", ".thumbnails",
    "obb", "data",
}
ROOTS = [
    TERMUX_HOME,
    MESH,
    Path("/storage/emulated/0/Download"),
    Path("/storage/emulated/0/Documents"),
    Path("/storage/emulated/0/Markor"),
    Path("/storage/emulated/0/markor"),
    Path("/storage/emulated/0/Download/Markor"),
    Path("/storage/emulated/0/Documents/Markor"),
]
MAX_CHARS = 1800
MAX_TOKENS = 200
MAX_FILE = 250_000

SYSTEM = """You classify Jesse McMillen A15 (SM-A156U Termux) documents.
Return ONE JSON object. No markdown.
Schema:
{"class":"active_source|markor_note|download_inbox|mesh_share|handoff_clone|generated_log|duplicate_twin|archive_candidate|junk","action":"keep|rename|merge_review|archive_copy|move_to_mesh_outbox","dest":"same_or_relative","title":"short","reason":"one sentence","n14_risk":false}
Rules:
- Phone HOME is /data/data/com.termux/files/home
- Mesh share is /storage/emulated/0/openroot
- Downloads are inbox, not source of truth
- Do not invent /home/jesse paths
- Do not delete
- handoff_clone = repeated continuity memos
"""


def die(msg: str, code: int = 2) -> None:
    print("FAIL", msg, file=sys.stderr)
    raise SystemExit(code)


def assert_a15() -> None:
    cwd = os.getcwd()
    host = os.uname().nodename
    if cwd.startswith("/home/jesse") or "optiplex" in host.lower():
        die("wrong pane: this script is A15-only. Run on Termux. Box uses organize_docs_7b.py")
    if not TERMUX_HOME.is_dir():
        die("Termux HOME missing: /data/data/com.termux/files/home")


def doctor() -> int:
    assert_a15()
    print("pane", "A15")
    print("host", os.uname().nodename)
    print("uid", os.getuid())
    print("cwd", os.getcwd())
    print("termux_home", TERMUX_HOME.exists())
    print("mesh", MESH.exists(), "outbox", MESH_OUT.exists())
    for r in ROOTS:
        print("root", str(r), "exists", r.is_dir())
    HOME_OUT.mkdir(parents=True, exist_ok=True)
    print("home_out", HOME_OUT)
    try:
        with urllib.request.urlopen("http://127.0.0.1:8080/v1/models", timeout=3) as resp:
            print("tunnel_8080", "UP", resp.read()[:120].decode("utf-8", "replace"))
    except Exception as e:
        print("tunnel_8080", "DOWN", str(e)[:160])
        print("HINT ssh -N -L 8080:127.0.0.1:8080 jesse@192.168.1.193")
    print("DOCTOR_OK")
    return 0


def iter_docs(limit: int):
    seen = set()
    n = 0
    for root in ROOTS:
        if not root.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            for name in filenames:
                p = Path(dirpath) / name
                if p.suffix.lower() not in TEXT_SUFFIX:
                    continue
                key = str(p)
                if key in seen:
                    continue
                seen.add(key)
                try:
                    st = p.stat()
                except OSError:
                    continue
                if st.st_size > MAX_FILE or st.st_size == 0:
                    continue
                yield p, st
                n += 1
                if limit and n >= limit:
                    return


def census(limit: int) -> Path:
    assert_a15()
    HOME_OUT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    tsv = HOME_OUT / ("a15-census-" + stamp + ".tsv")
    n = 0
    with tsv.open("w") as f:
        f.write("path\tbytes\tmtime\tsuffix\n")
        for p, st in iter_docs(limit):
            f.write("%s\t%s\t%s\t%s\n" % (p, st.st_size, int(st.st_mtime), p.suffix.lower()))
            n += 1
    print("WROTE", tsv)
    print("N", n)
    if MESH_OUT.is_dir():
        dest = MESH_OUT / tsv.name
        shutil.copy2(tsv, dest)
        print("MESH_COPY", dest)
    else:
        print("MESH_COPY skipped — /storage/emulated/0/openroot/outbox missing")
    return tsv


def ask_7b(path: Path, text: str) -> dict:
    payload = {
        "model": MODEL,
        "temperature": 0,
        "max_tokens": MAX_TOKENS,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {
                "role": "user",
                "content": "PATH: %s\nBYTES: %s\n---\n%s" % (path, len(text.encode()), text[:MAX_CHARS]),
            },
        ],
    }
    req = urllib.request.Request(
        CODER,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = json.loads(resp.read().decode())
    content = raw["choices"][0]["message"]["content"].strip()
    if content.startswith("```"):
        content = content.strip("`")
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()
    try:
        obj = json.loads(content)
    except json.JSONDecodeError:
        obj = {
            "class": "generated_log",
            "action": "keep",
            "dest": "same",
            "title": path.name,
            "reason": "7B did not return JSON",
            "n14_risk": False,
            "raw": content[:300],
        }
    obj["path"] = str(path)
    obj["bytes"] = path.stat().st_size
    return obj


def plan(limit: int) -> int:
    doctor()
    try:
        urllib.request.urlopen("http://127.0.0.1:8080/v1/models", timeout=3).read()
    except Exception:
        die("no tunnel to box 7B. census still works. bring tunnel up then rerun plan")
    stamp = time.strftime("%Y%m%d-%H%M%S")
    tsv = HOME_OUT / ("a15-plan-" + stamp + ".tsv")
    jsonl = HOME_OUT / ("a15-plan-" + stamp + ".jsonl")
    rows = []
    with tsv.open("w") as tf, jsonl.open("w") as jf:
        tf.write("path\tclass\taction\tdest\tn14_risk\ttitle\treason\n")
        for p, st in iter_docs(limit):
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                print("SKIP", p, e)
                continue
            print("ASK", p)
            obj = ask_7b(p, text)
            rows.append(obj)
            jf.write(json.dumps(obj, ensure_ascii=False) + "\n")
            tf.write(
                "\t".join(
                    [
                        obj.get("path", ""),
                        str(obj.get("class", "")),
                        str(obj.get("action", "")),
                        str(obj.get("dest", "")),
                        str(obj.get("n14_risk", "")),
                        str(obj.get("title", "")).replace("\t", " "),
                        str(obj.get("reason", "")).replace("\t", " ").replace("\n", " "),
                    ]
                )
                + "\n"
            )
            tf.flush()
            jf.flush()
    print("WROTE", tsv)
    print("WROTE", jsonl)
    print("N", len(rows))
    if MESH_OUT.is_dir():
        shutil.copy2(tsv, MESH_OUT / tsv.name)
        print("MESH_COPY", MESH_OUT / tsv.name)
    by = {}
    for r in rows:
        by[r.get("class", "?")] = by.get(r.get("class", "?"), 0) + 1
    print("CLASSES", json.dumps(by, sort_keys=True))
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["doctor", "census", "plan", "help"])
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args(argv[1:])
    if args.cmd == "help":
        print(__doc__)
        return 0
    if args.cmd == "doctor":
        return doctor()
    if args.cmd == "census":
        assert_a15()
        census(args.limit)
        return 0
    return plan(args.limit)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
