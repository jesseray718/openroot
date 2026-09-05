#!/usr/bin/env python3
"""palm.py — pocket Find+Memo over logs you already have. Stdlib only."""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

HELP = "python3 palm.py where|logs|latest|grep PAT|memo TEXT|digest|todo|said"

TODO = """(A) python3 /home/jesse/openroot/bin/palm.py digest
(A) python3 /home/jesse/wisdom-scaffold/bin/operator-memory import --label markor-48h /home/jesse/phone-terminal-logs/auto_20260902_122444.log
(B) A15: python3 /storage/emulated/0/openroot/bin/palm.py said
(C) do not git add -A
"""

REDACT = re.compile(
    r"(?i)((?:sk-|Bearer |AIza|api[_-]?key=)[A-Za-z0-9_\-./+]{8,})"
    r"|((?:password|token|secret)\s*[:=]\s*\S+)"
)
NOISE = re.compile(
    r"(No command |command not found|did you mean:|Command .+ in package |"
    r"syntax error near|Standard output is not a terminal|rgb:0000)"
)


def pane() -> str:
    cwd = str(Path.cwd())
    host = os.uname().nodename.lower()
    if cwd.startswith("/home/jesse") or "optiplex" in host:
        return "SSH"
    if Path("/data/data/com.termux").exists() and not Path("/home/jesse").exists():
        return "A15"
    if cwd.startswith("/data/data/com.termux") or cwd.startswith("/storage/emulated/0"):
        return "A15"
    return "UNKNOWN"


def roots() -> dict[str, Path]:
    if pane() == "SSH":
        return {
            "openroot": Path("/home/jesse/openroot"),
            "outbox": Path("/home/jesse/openroot/outbox"),
            "logs": Path("/home/jesse/phone-terminal-logs"),
        }
    return {
        "openroot": Path("/storage/emulated/0/openroot"),
        "outbox": Path("/storage/emulated/0/openroot/outbox"),
        "logs": Path("/storage/emulated/0/Documents/terminal-logs"),
    }


def redact(s: str) -> str:
    return REDACT.sub("REDACTED", s)


def log_files(d: Path) -> list[Path]:
    if not d.is_dir():
        return []
    xs = [p for p in d.iterdir() if p.is_file() and p.suffix == ".log"]
    xs.sort(key=lambda p: p.stat().st_mtime)
    return xs


def said_lines(text: str) -> list[str]:
    out = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if NOISE.search(line):
            continue
        if " $ " in line[:48]:
            cmd = line.split(" $ ", 1)[-1].strip()
            if cmd:
                out.append(cmd)
            continue
        if line.startswith("> ") and not line.startswith("> ```"):
            out.append(line[2:])
    return out


def cmd_where() -> int:
    r = roots()
    print(json.dumps({"pane": pane(), "paths": {k: str(v) for k, v in r.items()}}, indent=2))
    for k, v in r.items():
        print(f"{k}\t{v}\t{'YES' if v.exists() else 'NO'}")
    return 0


def cmd_logs() -> int:
    files = log_files(roots()["logs"])
    print(f"n={len(files)} dir={roots()['logs']}")
    for p in files[-20:]:
        st = p.stat()
        print(f"{int(st.st_mtime)}\t{st.st_size}\t{p.name}")
    return 0


def cmd_latest() -> int:
    files = log_files(roots()["logs"])
    if not files:
        print(json.dumps({"ok": False, "err": "no logs", "dir": str(roots()["logs"])}))
        return 2
    p = files[-1]
    text = redact(p.read_text(errors="replace"))
    print(f"FILE {p} BYTES {p.stat().st_size}")
    print("---")
    print(text[-8000:] if len(text) > 8000 else text)
    return 0


def cmd_said() -> int:
    files = log_files(roots()["logs"])
    target = files[-1] if files else None
    if len(sys.argv) >= 3:
        cand = roots()["logs"] / sys.argv[2]
        if cand.exists():
            target = cand
    if target is None:
        print(json.dumps({"ok": False, "err": "no logs"}))
        return 2
    text = redact(target.read_text(errors="replace"))
    lines = said_lines(text)
    print(f"FILE {target} SAID {len(lines)}")
    for ln in lines[-80:]:
        print(ln)
    return 0


def cmd_grep(pat: str) -> int:
    rx = re.compile(pat, re.I)
    hits = 0
    for p in log_files(roots()["logs"])[-30:]:
        try:
            text = redact(p.read_text(errors="replace"))
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if NOISE.search(line):
                continue
            if rx.search(line):
                print(f"{p.name}:{i}:{line[:240]}")
                hits += 1
                if hits >= 80:
                    print("TRUNCATED")
                    return 0
    print(f"hits={hits}")
    return 0 if hits else 1


def cmd_memo(text: str) -> int:
    ob = roots()["outbox"]
    ob.mkdir(parents=True, exist_ok=True)
    fp = ob / "PALM_MEMO.md"
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    with fp.open("a") as f:
        f.write(f"\n## {stamp} pane={pane()}\n{redact(text).strip()}\n")
    print(json.dumps({"ok": True, "path": str(fp)}))
    return 0


def cmd_digest() -> int:
    files = log_files(roots()["logs"])
    ob = roots()["outbox"]
    ob.mkdir(parents=True, exist_ok=True)
    fp = ob / "LOG_DIGEST.md"
    lines = [
        f"# LOG_DIGEST {time.strftime('%Y-%m-%dT%H:%M:%S')} pane={pane()}",
        f"dir={roots()['logs']} n={len(files)}",
        "rule=said-lines. not full FTS.",
        "",
    ]
    for p in files[-12:]:
        st = p.stat()
        body = redact(p.read_text(errors="replace")) if st.st_size < 400000 else ""
        said = said_lines(body)[-8:] if body else ["(skip large)"]
        lines.append(f"## {p.name} bytes={st.st_size}")
        lines.extend(f"- {s}" for s in said or ["(none)"])
        lines.append("")
    fp.write_text("\n".join(lines) + "\n")
    print(json.dumps({"ok": True, "path": str(fp), "n": len(files)}))
    return 0


def cmd_todo() -> int:
    print(TODO)
    ob = roots()["outbox"]
    ob.mkdir(parents=True, exist_ok=True)
    (ob / "PALM_TODO.txt").write_text(TODO)
    print("wrote", ob / "PALM_TODO.txt")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in {"help", "-h"}:
        print(HELP)
        return 0
    c = argv[1]
    if c == "where":
        return cmd_where()
    if c == "logs":
        return cmd_logs()
    if c == "latest":
        return cmd_latest()
    if c == "said":
        return cmd_said()
    if c == "grep":
        return cmd_grep(" ".join(argv[2:])) if len(argv) >= 3 else 1
    if c == "memo":
        return cmd_memo(" ".join(argv[2:]) or "empty")
    if c == "digest":
        return cmd_digest()
    if c == "todo":
        return cmd_todo()
    print(HELP)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
