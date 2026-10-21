#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-or-later
# OpenRoot — jesseray718
# PANE: SSH — discover last-7-day scripts, reconcile vs git, then 7B/3B team review of profile/landing/consolidation
# eta = useful_joules / human_joules
import os, sys, json, subprocess, datetime, urllib.request, time

STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
CANARY = "WEEKTEAM1"
REPO = "/home/jesse/openroot"
EXTRA_DIRS = ["/home/jesse/aerocement-panel-v0"]
OLLAMA = "http://localhost:11434/api/generate"
REGISTRY = "/home/jesse/openroot/data/model_registry.json"

def log(tag, status, msg):
    line = "[%s] [%s] %s" % (tag, status, msg)
    print(line, flush=True)

print("[%s] START %s" % (CANARY, STAMP))

# ============================================================
# STAGE 1 — FILESYSTEM TRUTH: scripts created/modified in past 7 days
# ============================================================
cutoff = time.time() - 7 * 86400
found = []
scan_dirs = [REPO] + EXTRA_DIRS
for base in scan_dirs:
    if not os.path.isdir(base):
        log("sweep", "status", "%s not present — skip" % base)
        continue
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in
                   (".git", "__pycache__", "venv", "node_modules", "attic", "archive", "local_archive")]
        for fn in files:
            if not (fn.endswith(".py") or fn.endswith(".sh")):
                continue
            p = os.path.join(root, fn)
            try:
                st = os.stat(p)
            except OSError:
                continue
            if st.st_mtime >= cutoff:
                found.append(p)
log("sweep", "status", "scripts touched in last 7 days: %d" % len(found))
for p in sorted(found):
    rel = os.path.relpath(p, REPO) if p.startswith(REPO) else p
    print("    %s" % rel)

# ============================================================
# STAGE 2 — GIT TRUTH: which recent files are untracked (slipped through)?
# ============================================================
os.chdir(REPO)
ls_files = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.splitlines()
tracked = set(ls_files)
untracked_recent = [p for p in found if p.startswith(REPO) and os.path.relpath(p, REPO) not in tracked]
if untracked_recent:
    log("sweep", "held", "UNTRACKED recent scripts (%d) — review, then git add:" % len(untracked_recent))
    for p in sorted(untracked_recent):
        print("    UNTRACKED: %s" % os.path.relpath(p, REPO))
else:
    log("sweep", "banked", "all recent scripts are git-tracked — nothing slipped")

# junk files from heredoc collisions (observed in repo root: EOF, PYEOF)
junk = [f for f in ("EOF", "PYEOF", "_EOF_SCRIPT_", "_EOF_CMT_", "_EOF_FIX", "_EOF_THX_", "_EOF_CONTRIB_")
        if os.path.isfile(os.path.join(REPO, f))]
if junk:
    log("sweep", "held", "heredoc junk files in repo root: %s — safe to delete, NOT scripts" % ", ".join(junk))
else:
    log("sweep", "status", "no heredoc junk files")

# dangling backups (README bak storm from 2026-09-23/24)
baks = []
for f in os.listdir(REPO):
    if f.startswith("README.md.bak.") and os.path.isfile(os.path.join(REPO, f)):
        baks.append(f)
if len(baks) > 3:
    log("sweep", "held", "%d README backups in repo root — keep newest 2, delete rest" % len(baks))
    for b in sorted(baks):
        print("    BAK: %s" % b)

# ============================================================
# STAGE 3 — TEAM REVIEW (7B authors, 3B grades; registry-weighted)
# ============================================================
def ollama(model, prompt, timeout=240):
    try:
        req = urllib.request.Request(
            OLLAMA,
            data=json.dumps({"model": model, "prompt": prompt,
                             "stream": False, "options": {"num_predict": 700}}).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read()).get("response", "").strip()
    except Exception as e:
        return None

try:
    reg = json.load(open(REGISTRY))
    author = [m for m in reg["routing_table"]["AUTHOR"]
              if reg["models"][m]["grade"] == "PASS"][0]
    grader = [m for m in reg["routing_table"]["GRADE"]
              if reg["models"][m]["grade"] == "PASS"][0]
    log("team", "banked", "registry routing: author=%s grader=%s" % (author, grader))
except Exception:
    author, grader = "qwen2.5-coder:7b", "qwen2.5:3b"
    log("team", "status", "registry unreadable — falling back to known-good pair")

inventory_lines = "\n".join("- " + (os.path.relpath(p, REPO) if p.startswith(REPO) else p)
                            for p in sorted(found)[:80])

prompt = (
"You are reviewing the OpenRoot project (github.com/jesseray718, ~41 public repos). "
"Owner wants: (1) GitHub profile README improvements, (2) landing page updates, "
"(3) GitHub-wide mass consolidation and cleanup. "
"CURRENT WEEK ACTIVITY (recent scripts):\n%s\n\n"
"FACTS: flagship=openroot; other live repos include openroot-canon, wisdom-scaffold, "
"black-locust-rmh, une, axiom-library, openroot-ecosystem, jesseray718-archive (firmware); "
"recently created: aerocement-panel-v0 (build evidence). Legacy scattered repos: agapenet, "
"une, canonical, renaissance-protocol, openroot-thesis, fractallattice, oscillation-mesh, "
"agaperesonance, aerocement-calc, OpenCell-Thermal-System, agape-coordination, "
"openroot-spoke-template, sync-from-kai, kai-memory, kai9000, etaledger, "
"jesseray718.github.io. Archived AeroCement_Ecosystem is NOT live. "
"N14: never claim efficiency above 100 percent; thermal numbers stay MODEL until instrumented. "
"Output three sections with concrete recommendations, max 8 bullets each: "
"PROFILE / LANDING / CONSOLIDATION. For consolidation: classify each repo group as "
"KEEP, MERGE-INTO (target), or ARCHIVE, and name the exact target. Be decisive." % inventory_lines)

draft = ollama(author, prompt)
if not draft:
    log("team", "gate", "7B unavailable — warm it (ollama run %s) and rerun; sweep results above are still valid" % author)
    sys.exit(0)

grade_prompt = ("Grade this recommendation set 0-10 on: decisiveness, correctness given the facts, "
"N14 compliance (no efficiency overclaims), and effort-efficiency. First line: 'SCORE: n/10'. "
"Then 3 bullets max of critique.\n\nRECOMMENDATIONS:\n%s" % draft)
grade = ollama(grader, grade_prompt, timeout=120)

N14_BAD = ["over 100 percent", ">100%", "134% eff", "2197 W", "free energy", "over unity"]
n14_hits = [p for p in N14_BAD if p.lower() in draft.lower()]

out = "/home/jesse/openroot/context_bridge/team_review_%s.md" % STAMP
with open(out, "w") as f:
    f.write("# Team Review — Profile / Landing / Consolidation\n")
    f.write("STAMP: %s\nAUTHOR: %s (7B)  GRADE: %s (3B)\n" % (STAMP, author, grader))
    f.write("N14: %s\nSTATUS: DRAFT — HUMAN GATE REQUIRED\n\n" %
            ("PASS" if not n14_hits else "REJECT " + str(n14_hits)))
    f.write("## Recommendations\n\n%s\n\n## Grader verdict\n\n%s\n" % (draft, grade or "(grader unavailable)"))
    f.write("\n## Sweep appendix\nRecent scripts: %d, untracked: %d, junk files: %s\n" %
            (len(found), len(untracked_recent), junk or "none"))
log("team", "held", "team review written: %s (N14 %s)" % (out, "PASS" if not n14_hits else "FAIL"))
if grade:
    print("    %s" % grade.splitlines()[0])

print("[%s] END %s [exit=0]" % (CANARY, STAMP))
