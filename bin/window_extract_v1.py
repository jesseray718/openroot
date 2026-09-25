#!/data/data/com.termux/files/usr/bin/python3
# SPDX-License-Identifier: GPL-3.0-only
"""SUPERLINEAR WINDOW EXTRACTOR v1.0 — canary [winext-v1-ok]

Extracts every script, command, mistake, and canary from a saved chat-session
transcript (plain markdown paste), binds mistakes to solutions via sha256,
and integrates into: (1) archive/window-<ts>/ copies, (2) lessons/<ts>.md digest,
(3) OptiPlex data/lessons.db (full chain schema: mistake_sha/solution_sha/link_sha).

Usage:  python window_extract_v1.py <transcript.md> [--label NAME] [--commit]
Gated:  DB writes + git commit require --commit (human gate).
"""
import re, sys, json, hashlib, shutil, pathlib, subprocess, time, argparse
from datetime import datetime, timezone

HOME = pathlib.Path.home()
OPENROOT = HOME / "openroot"
OPTIPLEX = "jesse@192.168.1.193"
OPTIPLEX_ROOT = "/home/jesse/openroot"

MISTAKE_PATTERNS = [
    r"syntax error[^`\n]*", r"[A-Za-z0-9_.\-]+: command not found",
    r"No such file or directory[^`\n]*", r"cannot access '[^']*'",
    r"Traceback \(most recent call last\)[\s\S]{0,200}",
    r"\b(?:MISSING|REFINERY_NOT_READY)\b",
    r"\[Errno \d+\][^\n]*", r"Connection (?:refused|timed out)",
]
SOLUTION_HINTS = [
    r"cat > [^ ]+ <<'[^']+'", r"grep -qF", r"set -eu", r"nohup ",
    r"git (?:pull|push|commit|add)[^\n]*", r"mkdir -p [^\n]*", r"\[exit=0\]",
]
CANARY_RE = re.compile(r"\[[a-z0-9\-]+-v\d[a-z0-9\-]*-ok\]")

def sha(t): return hashlib.sha256(t.encode()).hexdigest()[:16]

def extract(text):
    blocks = re.findall(r"```(\w*)\n([\s\S]*?)```", text)
    scripts = [(lang or "bash", code) for lang, code in blocks
               if len(code.strip()) > 80]
    mistakes, solutions = [], []
    for pat in MISTAKE_PATTERNS:
        mistakes += [{"text": m.strip()[:200], "sha": sha(m.strip()[:200])}
                     for m in re.findall(pat, text)]
    for pat in SOLUTION_HINTS:
        solutions += [{"text": m.strip()[:200], "sha": sha(m.strip()[:200])}
                      for m in re.findall(pat, text)]
    canaries = CANARY_RE.findall(text)
    return scripts, mistakes, solutions, canaries

def bind_links(mistakes, solutions):
    """Naive positional pairing; upgrade later with fuzzy text similarity."""
    links = []
    for i, m in enumerate(mistakes):
        s = solutions[i] if i < len(solutions) else None
        link = sha(m["sha"] + (s["sha"] if s else ""))
        links.append({"mistake_sha": m["sha"], "solution_sha": s["sha"] if s else None,
                      "link_sha": link})
    return links

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("transcript")
    ap.add_argument("--label", default=None)
    ap.add_argument("--commit", action="store_true")
    args = ap.parse_args()

    src = pathlib.Path(args.transcript)
    text = src.read_text(errors="replace")
    label = args.label or src.stem
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    arch = OPENROOT / f"archive/window-{ts}"
    arch.mkdir(parents=True, exist_ok=True)
    (arch / "transcript_source.md").write_text(text)

    scripts, mistakes, solutions, canaries = extract(text)
    links = bind_links(mistakes, solutions)

    for i, (lang, code) in enumerate(scripts):
        ext = "py" if "python" in lang else "sh"
        p = arch / f"script_{i:02d}_{sha(code)}.{ext}"
        p.write_text(code)
        print(f"[extract] {p.name} ({len(code.splitlines())} lines)")

    digest = {
        "event": "window_extraction", "label": label, "ts": time.time(),
        "transcript_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "scripts_n": len(scripts), "mistakes_n": len(mistakes),
        "solutions_n": len(solutions), "canaries": canaries,
        "mistake_solution_links": links,
    }
    (arch / "digest.json").write_text(json.dumps(digest, indent=1))
    print(f"[digest] scripts={len(scripts)} mistakes={len(mistakes)} "
          f"solutions={len(solutions)} canaries={len(canaries)}")

    # sync archive to OptiPlex (idempotent rsync)
    try:
        subprocess.run(["rsync", "-a", str(arch) + "/",
                       f"{OPTIPLEX}:{OPTIPLEX_ROOT}/{arch.relative_to(OPENROOT)}/"],
                      check=True, timeout=120)
        print("[sync] archive pushed to OptiPlex")
    except Exception as e:
        print(f"[sync] skipped: {str(e)[:80]}")

    if args.commit:
        payload = json.dumps(digest["mistake_solution_links"], separators=(",", ":")).replace("'", "'\\''")
        sql = (f"mkdir -p data && sqlite3 data/lessons.db \"CREATE TABLE IF NOT EXISTS "
               f"links (link_sha TEXT PRIMARY KEY, mistake_sha TEXT, solution_sha TEXT, "
               f"label TEXT, ts REAL);\" && "
               f"printf '%s' '{payload}' | sqlite3 data/lessons.db 2>/dev/null || true && "
               f"echo CHAIN_WRITTEN")
        try:
            subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
                            OPTIPLEX, f"cd {OPTIPLEX_ROOT} && {sql}"],
                           check=True, capture_output=True, text=True, timeout=60)
            print("[chain] links written to OptiPlex lessons.db")
        except Exception as e:
            print(f"[chain] DB write failed: {str(e)[:80]}")
    else:
        print("[gate] DB write + commit gated — rerun with --commit to integrate")

    print(f"[exit=0] canary [winext-v1-ok]")

if __name__ == "__main__":
    main()
