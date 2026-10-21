#!/data/data/com.termux/files/usr/bin/python3
"""
deepdive.py — offline deep audit of every local git repo.
stdlib only. READ-ONLY: never commits, never pushes (Firewall F1).
Outputs: ranked actions (impact*urgency/effort heuristic),
JSON report, paste-ready payload for any external AI.
Status: in-progress until first on-device run.
"""
import json, os, re, subprocess, time
from pathlib import Path

HOME = Path.home()
OUT_DIR = Path("/sdcard/openroot/context_bridge")
REPORT = OUT_DIR / "deepdive_report.json"
PAYLOAD = OUT_DIR / "last_deepdive_payload.json"
LEDGER = OUT_DIR / "thermo_ledger.jsonl"

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv",
             "models", ".cache", "dist", "build"}
TEXT_EXT = {".py", ".md", ".json", ".jsonl", ".txt", ".sh", ".yml",
            ".yaml", ".toml", ".html", ".js", ".css", ".csv"}
MAX_FILE_BYTES = 262_144
MAX_FILES_PER_REPO = 4000

SECRET_PATTERNS = [
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("github_pat",   re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("sk_style_key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")),
    ("groq_key",     re.compile(r"\bgsk_[A-Za-z0-9]{20,}")),
    ("aws_key",      re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack_token",  re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("private_key",  re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]
RETRACTED_PATTERNS = [
    ("stirling_dt_vehicle", re.compile(r"stirling", re.I)),
    ("h003_12_91",          re.compile(r"12\.91")),
    ("cop_8544",            re.compile(r"8,?544")),
]
TODO_RE = re.compile(r"\b(TODO|FIXME|XXX)\b")
WEIRD_NAME_RE = re.compile(r'^["\s\\~]|\\~')

def git(repo, *args):
    try:
        r = subprocess.run(["git", "-C", str(repo)] + list(args),
                           capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception:
        return ""

def find_repos(root, max_depth=4):
    repos = []
    root = Path(root)
    for dirpath, dirnames, _ in os.walk(root):
        p = Path(dirpath)
        try:
            depth = len(p.relative_to(root).parts)
        except ValueError:
            depth = 0
        if depth > max_depth:
            dirnames[:] = []
            continue
        if ".git" in dirnames:
            repos.append(p)
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and not d.startswith(".")]
    return repos

def repo_status(repo):
    info = {"path": str(repo), "name": repo.name}
    info["branch"] = git(repo, "rev-parse", "--abbrev-ref", "HEAD") or "?"
    info["remote"] = git(repo, "remote", "get-url", "origin")
    info["behind"], info["ahead"] = 0, 0
    ab = git(repo, "rev-list", "--left-right", "--count", "@{u}...HEAD")
    parts = ab.split()
    if len(parts) == 2 and all(x.isdigit() for x in parts):
        info["behind"], info["ahead"] = int(parts[0]), int(parts[1])
    staged = modified = untracked = 0
    weird = []
    for line in git(repo, "status", "--porcelain").splitlines():
        if len(line) < 4:
            continue
        code, name = line[:2], line[3:]
        if code == "??":
            untracked += 1
            if WEIRD_NAME_RE.search(name):
                weird.append(name)
        else:
            if code[0] not in " ?":
                staged += 1
            if code[1] not in " ?":
                modified += 1
    info.update(staged=staged, modified=modified,
                untracked=untracked, weird_names=weird)
    last = git(repo, "log", "-1", "--format=%ct|%s")
    if "|" in last:
        ct, msg = last.split("|", 1)
        try:
            info["last_commit_days"] = round((time.time() - int(ct)) / 86400, 1)
        except ValueError:
            pass
        info["last_commit_msg"] = msg[:80]
    return info

def scan_repo_files(repo):
    secrets, retracted, todos, scanned = [], {}, 0, 0
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if scanned >= MAX_FILES_PER_REPO:
                dirnames[:] = []
                break
            p = Path(dirpath) / fn
            if p.suffix.lower() not in TEXT_EXT:
                continue
            try:
                if p.stat().st_size > MAX_FILE_BYTES:
                    continue
                text = p.read_text(errors="replace")
            except Exception:
                continue
            scanned += 1
            todos += len(TODO_RE.findall(text))
            rel = str(p.relative_to(repo))
            for label, rx in SECRET_PATTERNS:
                for m in rx.finditer(text):
                    tok = m.group(0)
                    secrets.append({"file": rel, "type": label,
                                    "masked": tok[:6] + "..." + tok[-4:]})
            for label, rx in RETRACTED_PATTERNS:
                if rx.search(text):
                    retracted.setdefault(label, []).append(rel)
    return {"secrets": secrets, "retracted": retracted,
            "todos": todos, "files_scanned": scanned}

def check_ledger():
    flags = []
    if not LEDGER.exists():
        return flags
    for i, line in enumerate(LEDGER.read_text().strip().splitlines()):
        try:
            e = json.loads(line)
        except Exception:
            flags.append({"line": i, "issue": "unparseable ledger line"})
            continue
        if e.get("type") == "measurement" and float(e.get("joules", 0) or 0) > 0:
            basis = [k for k in ("mass_flow_kg_s", "m_dot", "cp",
                                 "duration_s", "sensor", "meter_kWh") if k in e]
            if not basis:
                flags.append({"line": i, "joules": e.get("joules"),
                    "issue": "joules recorded with no measurement basis "
                             "(violates genesis rule: no estimates)"})
    return flags

def main():
    t0 = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    repos = find_repos(HOME)
    findings, repo_reports = [], []
    for repo in repos:
        st = repo_status(repo)
        sc = scan_repo_files(repo)
        st.update(sc)
        repo_reports.append(st)
        for s in sc["secrets"]:
            findings.append({"priority": 100, "status": "verify-then-rotate",
                "action": f"ROTATE key + purge history: {st['name']}/{s['file']} ({s['type']} {s['masked']})"})
        for n in st["weird_names"]:
            findings.append({"priority": 64, "status": "tested",
                "action": f"stray escaped filename {n!r} in {st['name']} — run cleanup block"})
        if st.get("ahead"):
            findings.append({"priority": 30 + 2 * st["ahead"], "status": "tested",
                "action": f"{st['name']}: {st['ahead']} unpushed commit(s) — review, then: git -C {st['path']} push"})
        if st["staged"]:
            findings.append({"priority": 28, "status": "tested",
                "action": f"{st['name']}: {st['staged']} staged file(s) awaiting commit"})
        if st["untracked"]:
            findings.append({"priority": 12, "status": "tested",
                "action": f"{st['name']}: {st['untracked']} untracked file(s) — add or ignore"})
        for label, files in sc["retracted"].items():
            findings.append({"priority": 21, "status": "contradicted-claim-refs",
                "action": f"{st['name']}: {len(files)} file(s) reference retracted claim [{label}] — align with CORRECTIONS.md: " + ", ".join(files[:3])})
    for f in check_ledger():
        findings.append({"priority": 70, "status": "contradicted",
            "action": f"thermo_ledger line {f['line']}: {f['issue']}"})
    findings.sort(key=lambda x: -x["priority"])
    report = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
              "elapsed_s": round(time.time() - t0, 2),
              "repos": repo_reports, "findings": findings,
              "note": "priority = impact*urgency/effort heuristic; "
                      "ability/time^3 is not a derivable physical metric"}
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    payload = {"ts": report["ts"],
               "deepdive_top_actions": findings[:10],
               "repos": [{k: r.get(k) for k in
                          ("name", "branch", "ahead", "behind", "staged",
                           "modified", "untracked", "files_scanned")}
                         for r in repo_reports]}
    PAYLOAD.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"DEEPDIVE  repos={len(repos)}  elapsed={report['elapsed_s']}s")
    print(f"report : {REPORT}")
    print(f"payload: {PAYLOAD}")
    print("TOP ACTIONS (impact*urgency/effort):")
    for i, f in enumerate(findings[:10], 1):
        print(f"{i:2}. [{f['priority']:>3}] {f['action']}")
    if not findings:
        print("  clean — no findings")

if __name__ == "__main__":
    main()
