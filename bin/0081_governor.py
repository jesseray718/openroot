#!/usr/bin/env python3
"""GOVERNOR-01 — Bounded LLM Swarm Orchestrator. Pure stdlib, no pip deps."""
import os, sys, json, subprocess, re
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen

HOME = Path(os.environ.get("HOME", ""))
G = HOME / ".governor"
PROJ = HOME / "projects" / "openroot"
PARKED, DONE, DEAD = G / "parked", G / "done", G / "dead"
PARKED_CAP = 10
os.environ["GOVERNOR"] = "1"

def now(): return datetime.now(timezone.utc).isoformat()
def parked_n(): return len(list(PARKED.glob("*")))

def parse_queue():
    qf = G / "tasks.queue"
    if not qf.exists(): return []
    tasks, cur = [], {}
    for line in qf.read_text().splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("[TASK-"):
            if cur:
                tasks.append(cur)
            bracket_end = s.index("]")
            cur = {"id": s[1:bracket_end]}
            rest = s[bracket_end+1:].strip()
            if ":" in rest:
                k, _, v = rest.partition(":")
                cur[k.strip().lower()] = v.strip()
        elif ":" in s and cur:
            k, _, v = s.partition(":")
            cur[k.strip().lower()] = v.strip()
    if cur:
        tasks.append(cur)
    return tasks

def log(tid, dest, reason=""):
    (G / "audit.log").open("a").write(f"{now()} | {tid} -> {dest} | {reason}\n")

def get_groq_key():
    env_key = os.environ.get("GROQ_API_KEY", "").strip()
    if env_key and not env_key.startswith("nano"):
        return env_key.split()[0]
    cfg = HOME / ".config" / "aiq" / "config.sh"
    if not cfg.exists(): return None
    for line in cfg.read_text().splitlines():
        if "GROQ_API_KEY" in line and "=" in line and not line.strip().startswith("#"):
            v = line.split("=", 1)[1].strip().strip('"').strip("'")
            if v and not v.startswith("nano"):
                return v.split()[0]
    return None

def record_health(provider, ok, headers=None):
    pf = G / "providers.json"
    data = json.loads(pf.read_text()) if pf.exists() else {}
    e = data.get(provider, {})
    e["last_success" if ok else "last_failure"] = now()
    if headers and ok:
        for h in ["x-ratelimit-limit-requests", "x-ratelimit-remaining-requests",
                   "x-ratelimit-reset-requests"]:
            if h in headers: e[h] = headers[h]
    data[provider] = e
    pf.write_text(json.dumps(data, indent=2))

def groq_chat(prompt, model="llama-3.3-70b-versatile", max_tokens=4096):
    key = get_groq_key()
    if not key: return False, "No Groq key found", {}
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }).encode()
    req = Request(url, data=payload, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "User-Agent": "OpenRoot-Governor/1.0"
    })
    try:
        with urlopen(req, timeout=120) as r:
            d = json.loads(r.read())
            return True, d["choices"][0]["message"]["content"], dict(r.headers)
    except Exception as e:
        return False, f"{type(e).__name__}: {e}", {}

def w_extractor(task):
    results = []
    raw_input = task.get("input", "")
    for inp in raw_input.split(","):
        inp = inp.strip()
        if not inp: continue
        fp = PROJ / inp
        if not fp.exists():
            results.append(f"SKIP {inp} not found")
            continue
        if fp.is_dir():
            results.append(f"SKIP {inp} is a directory")
            continue
        txt = fp.read_text()
        if "[THEORETICAL]" in txt:
            results.append(f"SKIP {inp} already tagged")
            continue
        lines = txt.splitlines()
        idx = 0
        for i, l in enumerate(lines):
            if l.startswith("#"):
                idx = i + 1
                break
        hdr = "\n> **[THEORETICAL]** — All performance metrics herein are unvalidated simulations. No physical bench test conducted. See VERIFY-01.\n"
        lines.insert(idx, hdr)
        fp.write_text("\n".join(lines))
        results.append(f"OK {inp} header inserted")
    return True, "\n".join(results), "deterministic"

def w_coder(task):
    sp = PROJ / "bin" / "or-linkcheck.py"
    sp.parent.mkdir(parents=True, exist_ok=True)
    sp.write_text(
        '#!/usr/bin/env python3\n'
        '"""Repo link checker — governor/TASK-005. Stdlib only."""\n'
        'import re, sys\n'
        'from pathlib import Path\n'
        'from urllib.request import Request, urlopen\n'
        'repo = Path(sys.argv[1] if len(sys.argv) > 1 else ".")\n'
        'mds = list(repo.rglob("*.md"))\n'
        'urls = set()\n'
        'for md in mds:\n'
        '    for m in re.finditer(r"https?://[^\\s)\\]]+", md.read_text(errors="ignore")):\n'
        '        urls.add(m.group(0).rstrip("."))\n'
        'broken = []\n'
        'for u in sorted(urls):\n'
        '    try:\n'
        '        r = urlopen(Request(u, method="HEAD", headers={"User-Agent": "OpenRoot/1.0"}), timeout=15)\n'
        '        if r.status >= 400: broken.append((u, r.status))\n'
        '    except Exception as e: broken.append((u, str(e)[:60]))\n'
        f'print(f"Checked {{len(urls)}} URLs in {{len(mds)}} files")\n'
        'for u, e in broken:\n'
        '    print(f"  BROKEN {e}: {u}")\n'
        'sys.exit(1 if broken else 0)\n'
    )
    sp.chmod(0o755)
    try:
        r = subprocess.run([sys.executable, str(sp), str(PROJ)],
                           capture_output=True, text=True, timeout=60)
        return r.returncode == 0, f"Written {sp}\n{r.stdout[:300]}", "deterministic"
    except Exception as e:
        return False, f"Written but test failed: {e}", "deterministic"

def w_drafter(task):
    obj = task.get("objective", "")
    prompt = (
        f"Write a complete markdown document for the OpenRoot project:\n\n{obj}\n\n"
        "Rules:\n- Mark all performance claims [THEORETICAL] until physically validated\n"
        "- Include: purpose, materials, methods, measurements, pass/fail criteria, safety\n"
        "- Device: Samsung Galaxy A15, Termux, no root\n"
        "- License: CC-BY-SA-4.0, Copyright: One Human Family\n"
        "- Dense, practical, no fluff"
    )
    ok, text, hdrs = groq_chat(prompt)
    record_health("groq", ok, hdrs)
    return ok, text, "human"

WORKERS = {
    "extractor": w_extractor,
    "coder": w_coder,
    "code": w_coder,
    "drafter": w_drafter,
}

def write_artifact(tid, task, content, vtype):
    ext = ".md" if task.get("class", "").lower() == "drafter" else ".txt"
    dest = DONE if vtype == "deterministic" else PARKED
    hdr = (
        f"<!-- Draft-Origin: governor/{tid} -->\n"
        f"<!-- Generated: {now()} -->\n"
        f"<!-- Verifier: {vtype} -->\n\n"
    )
    (dest / f"{tid}{ext}").write_text(hdr + content)

def route(task):
    tid = task.get("id", "?")
    cls = task.get("class", "").lower()
    ver = task.get("verifier", "human").lower()
    print(f"\n{'='*50}")
    print(f"ROUTING {tid} | class={cls} | verifier={ver}")
    print(f"  Obj: {task.get('objective', '?')[:80]}")
    if ver == "human" and parked_n() >= PARKED_CAP:
        print(f"  HALT — parked at cap {PARKED_CAP}")
        return
    w = WORKERS.get(cls)
    if not w:
        print(f"  SKIP — unknown class '{cls}'")
        log(tid, DEAD.name, f"unknown:{cls}")
        return
    try:
        ok, out, vt = w(task)
    except Exception as e:
        ok, out, vt = False, f"Crash: {e}", "deterministic"
    print(f"  Result: {'PASS' if ok else 'FAIL'}")
    if ok:
        write_artifact(tid, task, out, vt)
        if vt == "deterministic":
            log(tid, DONE.name)
            print("  -> done/ (T0)")
        else:
            log(tid, PARKED.name)
            print("  -> parked/ (T1 await)")
    else:
        log(tid, DEAD.name, out[:200])
        print(f"  -> dead/ ({out[:120]})")

def main():
    if len(sys.argv) < 2:
        print("Usage: governor.py [drain|status]")
        return
    if sys.argv[1] == "status":
        print(f"GOVERNOR-01 STATUS")
        print(f"  Queue: {len(parse_queue())} tasks")
        print(f"  Parked: {parked_n()}/{PARKED_CAP}")
        print(f"  Done: {len(list(DONE.glob('*')))}")
        print(f"  Dead: {len(list(DEAD.glob('*')))}")
        pf = G / "providers.json"
        if pf.exists():
            print(f"  Health: {pf.read_text()[:300]}")
        return
    if sys.argv[1] == "drain":
        # Clear dead/ from previous runs
        for f in DEAD.glob("*"):
            f.unlink()
        tasks = parse_queue()
        if not tasks:
            print("Queue empty.")
            return
        print(f"Draining {len(tasks)} tasks...")
        for t in tasks:
            route(t)
        print(f"\n{'='*50}")
        print(f"DRAIN COMPLETE")
        print(f"  Done: {len(list(DONE.glob('*')))}")
        print(f"  Parked: {parked_n()}/{PARKED_CAP}")
        print(f"  Dead: {len(list(DEAD.glob('*')))}")
        print(f"\nReview parked: ls {PARKED}")

if __name__ == "__main__":
    main()
