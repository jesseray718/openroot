#!/usr/bin/env python3
# ecosystem_v2.py — corpus-wide compile gates + optional 7B repair, keyed on ledger sha256
# SPDX-License-Identifier: GPL-3.0-only
# Usage:
#   python3 bin/ecosystem_v2.py              # full corpus sweep (gate only, no code writes)
#   python3 bin/ecosystem_v2.py openroot/    # scope to relpaths containing substring
#   CONFIRM=1 python3 bin/ecosystem_v2.py --repair   # repair failures (writes code, backups kept)
import os, sys, sqlite3, subprocess, shutil, time, json, hashlib
import urllib.request, urllib.error

ROOT = "/home/jesse/openroot"
LEDGER = os.path.join(ROOT, "data/file_ledger.db")
ENG = os.path.join(ROOT, "data/ecosystem_v2.db")
OLLAMA_URL = "http://localhost:11434/api/generate"
REPAIR_MODEL = "qwen2.5-coder:7b"
MAX_ATTEMPTS = 3
REPAIR_LIMIT = 5
EXCLUDE_PARTS = {"venv", ".venv", "node_modules", ".git", "__pycache__", ".cache",
                 "salvage", ".next", "local_archive", "quarantine_handoff_corrupt", "attic"}

ns = {}
exec(open(os.path.join(ROOT, "bin/file_ledger_v2.py")).read().split("def ")[0], ns)
DOMAINS = ns["DOMAINS"]

eng = sqlite3.connect(ENG, timeout=120)
eng.execute("PRAGMA busy_timeout=120000")
try:
    eng.execute("PRAGMA journal_mode=WAL")
except sqlite3.OperationalError:
    pass
eng.execute("""CREATE TABLE IF NOT EXISTS gates (
    sha TEXT PRIMARY KEY, path TEXT, ftype TEXT, success INTEGER, logs TEXT, checked_ts REAL)""")
eng.execute("CREATE TABLE IF NOT EXISTS repairs (sha TEXT, path TEXT, result TEXT, ts REAL)")
eng.commit()

HAS_OPENSCAD = shutil.which("openscad") is not None
SCAD_TMP = "/tmp/ecosystem_scad"
os.makedirs(SCAD_TMP, exist_ok=True)


def compile_py(path):
    r = subprocess.run([sys.executable, "-m", "py_compile", path],
                       capture_output=True, text=True, timeout=60)
    return (1 if r.returncode == 0 else 0), (r.stdout + r.stderr)[:1500]


def compile_scad(path, sha):
    stl = os.path.join(SCAD_TMP, sha[:16] + ".stl")
    r = subprocess.run(["openscad", "-o", stl, path],
                       capture_output=True, text=True, timeout=300)
    return (1 if r.returncode == 0 else 0), (r.stdout + r.stderr)[:1500]


def sweep(scope):
    led = sqlite3.connect("file:%s?mode=ro" % LEDGER, uri=True, timeout=120)
    rows = led.execute("""SELECT domain, relpath, sha256 FROM files
        WHERE sha256 IS NOT NULL AND sha256 != '-unreadable-'
        AND (relpath LIKE '%.py' OR relpath LIKE '%.scad')""").fetchall()
    led.close()
    cached = {r[0] for r in eng.execute("SELECT sha FROM gates WHERE success=1")}
    todo, skipped_missing = [], 0
    for dom, rel, sha in rows:
        if any(p in EXCLUDE_PARTS for p in rel.split("/")):
            continue
        if scope and scope not in rel:
            continue
        if sha in cached:
            continue
        p = os.path.join(DOMAINS.get(dom, ""), rel)
        if not os.path.isfile(p):
            skipped_missing += 1
            continue
        todo.append((sha, p, os.path.splitext(rel)[1].lower()))
    print("[gate] candidates=%d (cached-skipped=%d, missing=%d) scope=%r"
          % (len(todo), len(cached), skipped_missing, scope), flush=True)
    buf, done, passed, failed, t0 = [], 0, 0, 0, time.time()
    for sha, p, ft in todo:
        try:
            if ft == ".py":
                ok, logs = compile_py(p)
            elif ft == ".scad":
                if not HAS_OPENSCAD:
                    ok, logs = -1, "no-openscad-skip"
                else:
                    ok, logs = compile_scad(p, sha)
            else:
                ok, logs = -1, "no-gate-type"
        except (subprocess.TimeoutExpired, OSError) as e:
            ok, logs = 0, str(e)[:1500]
        buf.append((sha, p, ft, ok, logs, time.time()))
        done += 1
        passed += (ok == 1)
        failed += (ok == 0)
        if len(buf) >= 500:
            eng.executemany("INSERT OR REPLACE INTO gates VALUES (?,?,?,?,?,?)", buf)
            eng.commit()
            buf = []
        if done % 500 == 0:
            print("  %d/%d (%.0f%%) %.0fs, %.1f files/s, failed=%d"
                  % (done, len(todo), 100*done/len(todo), time.time()-t0,
                     done/(time.time()-t0), failed), flush=True)
    if buf:
        eng.executemany("INSERT OR REPLACE INTO gates VALUES (?,?,?,?,?,?)", buf)
        eng.commit()
    print("[banked] sweep: checked=%d passed=%d failed=%d in %.0fs"
          % (done, passed, failed, time.time()-t0), flush=True)


def strip_fences(text):
    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 2:
            code = parts[1]
            if code.startswith(("python", "scad")):
                code = code.split("\n", 1)[1]
            return code.strip()
    return text.strip()


def repair():
    if os.environ.get("CONFIRM") != "1":
        print("[held] repair requires CONFIRM=1 — this writes code across the corpus. Halting.")
        return
    led_fail = eng.execute("""SELECT g.sha, g.path, g.ftype, g.logs FROM gates g
        WHERE g.success=0
        AND (SELECT COUNT(*) FROM repairs r WHERE r.sha=g.sha) < ?
        ORDER BY g.path LIMIT ?""", (MAX_ATTEMPTS, REPAIR_LIMIT)).fetchall()
    if not led_fail:
        print("[banked] no repairable failures (or all at attempt cap). Ecosystem healthy.")
        return
    print("[gate] repairing %d failures (max %d attempts each)" % (len(led_fail), MAX_ATTEMPTS))
    for sha, p, ft, logs in led_fail:
        if not os.path.isfile(p):
            print("  skip %s — missing" % p)
            continue
        code = open(p, encoding="utf-8", errors="ignore").read()
        fence = chr(96) * 3
        prompt = ("You are a code repair agent. The file failed compilation. "
                  "Return ONLY the corrected full file, no commentary.\n"
                  "File: %s\nType: %s\nError log: %.1500s\n%s\n%s\n%s"
                  % (p, ft, logs, fence, code, fence))
        payload = {"model": REPAIR_MODEL, "prompt": prompt, "stream": False,
                   "options": {"temperature": 0.1, "seed": 42}}
        req = urllib.request.Request(OLLAMA_URL, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                fixed = strip_fences(json.loads(resp.read()).get("response", ""))
        except (urllib.error.URLError, OSError) as e:
            print("  ollama error on %s: %s" % (p, e))
            continue
        if not fixed or len(fixed) < 20:
            print("  empty/short repair for %s — skipped" % p)
            continue
        bak = p + ".bak." + time.strftime("%Y%m%dT%H%M%S")
        shutil.copy2(p, bak)
        with open(p, "w", encoding="utf-8") as f:
            f.write(fixed)
        # re-verify: the gate only passes if the repaired file actually compiles
        ok, rlogs = 0, "unverified"
        try:
            if ft == ".py":
                ok, rlogs = compile_py(p)
            elif ft == ".scad" and HAS_OPENSCAD:
                ok, rlogs = compile_scad(p, sha)
        except (subprocess.TimeoutExpired, OSError) as e:
            rlogs = str(e)[:1500]
        new_sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
        eng.execute("INSERT OR REPLACE INTO gates VALUES (?,?,?,?,?,?)",
                    (new_sha, p, ft, ok, rlogs[:1500], time.time()))
        eng.execute("INSERT INTO repairs (sha, path, result, ts) VALUES (?,?,?,?)",
                    (sha, p, "pass" if ok else "still-failing", time.time()))
        eng.commit()
        print("  %s %s (%s) backup=%s"
              % ("[banked]" if ok else "[held]", p,
                 "repaired" if ok else "still-failing", bak), flush=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    scope = args[0] if args else ""
    do_repair = "--repair" in sys.argv
    sweep(scope)
    if do_repair:
        repair()
    else:
        n = eng.execute("SELECT COUNT(*) FROM gates WHERE success=0").fetchone()[0]
        print("[held] %d failures recorded. Repairs: CONFIRM=1 python3 bin/ecosystem_v2.py --repair" % n)
    print("[exit=0]")
