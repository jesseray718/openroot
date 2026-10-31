# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""Living ride-along state v2: travels between every AI instance/window/session.
Usage:
  state_ride_along_v1.py snapshot          # regenerate CURRENT STATE from live system
  state_ride_along_v1.py log "<message>"   # append timestamped event
  state_ride_along_v1.py read              # print current state
v2 fix: QUEUE moved to plain constant string — braces in {CLIDdy,ReGen} no longer
parsed as f-string placeholders. Structural fix, not brace-escaping.
"""
import subprocess, sqlite3, hashlib, datetime, sys, os

STATE = "/home/jesse/openroot/context_bridge/RIDE_ALONG_STATE.md"

# Plain strings. NO f-strings here, so braces in text are inert.
VISION = """## MISSION (immutable)
Superlinear permaculture: maximize eta = J_useful / J_human. Cache every proven pathway.
A pathway proven once (SHA256-sealed in the Newton chain) is NEVER recomputed.
Compound modular Turing tidbits upward: input -> hash -> sealed pathway -> bigger modules.
Route everything: hash-first, embed-second, model-last. Proof (CLIDdy/ReGen style):
if a theorem stands, the whole system inherits it as flag and skips recompute.
The endgame: an interconnected organism where the least among us is lifted by the
accumulated proven pathways of everything that came before."""

QUEUE = """- [ ] SOLUTION 1 — commit-state hashing: input basis = git rev-parse HEAD (+ dirty bit), NOT working-tree diff. Daemon ledger churn stops invalidating pathways. Audit validates what will be PUSHED.
- [ ] SOLUTION 2 — parent-child lineage: ALTER pathways table ADD COLUMN parents TEXT (JSON list of row_shas). A->B->C composes into theorem T instead of 3 isolated seals. Bookshelf becomes spine.
- [ ] SOLUTION 3 — thresholded semantic routing: wire cosine similarity into lookup. Semantic hit needs confidence score (start 0.75, calibrate). Hash = binary truth, embed = scored neighbor, model = last resort.
- [ ] phi4-router front door: query -> hash lookup -> embed neighbor (scored) -> model call -> seal. NEXT ORGAN.
- [ ] tighten audit system prompt: 7B echoes scripts back instead of enumerating per-file risks.
- [ ] verify --embed flag fires on every audit (auto-embed new seals).
- [ ] theorem flags: CLIDdy/ReGen proven theorem = permanent ledger flag, never recompute.
- [ ] weekly onepass_v3.sh absorbs this snapshot."""

def now():
    return datetime.datetime.now(datetime.timezone.utc)

def sh(cmd):
    try:
        return subprocess.run(cmd, shell=False, capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:
        return "(unavailable)"

def snapshot():
    head = sh("cd /home/jesse/openroot && git rev-parse --short HEAD")
    branch = sh("cd /home/jesse/openroot && git rev-parse --abbrev-ref HEAD")
    dirty = sh("cd /home/jesse/openroot && git status --short | wc -l")
    try:
        c = sqlite3.connect("/home/jesse/openroot/data/pathways.db")
        rows = c.execute("SELECT COUNT(*) FROM pathways").fetchone()[0]
        emb = c.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0] if c.execute("SELECT name FROM sqlite_master WHERE name='embeddings'").fetchone() else 0
        last = c.execute("SELECT row_sha, created_utc FROM pathways ORDER BY id DESC LIMIT 1").fetchone()
        c.close()
        ledger = f"{rows} rows, {emb} embeddings, latest seal {str(last[0])[:12]} ({last[1][:19]})"
    except Exception:
        ledger = "(ledger unreadable)"
    reports = sh("ls -t /home/jesse/openroot/reports/audit-*.md 2>/dev/null | head -3")
    loglines = ""
    if os.path.isfile(STATE):
        txt = open(STATE).read()
        if "## EVENT LOG" in txt:
            loglines = txt.split("## EVENT LOG", 1)[1]

    banner = "# OPENROOT RIDE-ALONG STATE\n"
    banner += "<!-- Single source of truth for every AI instance. Read FIRST. Update after acting. -->\n"
    banner += "<!-- snapshot regenerates CURRENT STATE; event log is append-only history -->\n\n"
    banner += VISION + "\n\n"
    banner += f"## CURRENT STATE (regenerated {now().isoformat()})\n"
    banner += f"- Git: {branch} @ {head} ({dirty} dirty entries)\n"
    banner += f"- Pathway ledger: {ledger}\n"
    banner += f"- Latest reports: {reports or '(none)'}\n\n"
    banner += "## ACTIVE QUEUE (delete when done, never leave stale)\n"
    banner += QUEUE + "\n\n"
    banner += "## EVENT LOG\n"
    banner += (loglines.rstrip() + "\n") if loglines.strip() else "(empty — history starts now)\n"

    with open(STATE, "w") as f:
        f.write(banner)

def log(msg):
    ts = now().strftime("%Y-%m-%dT%H:%M:%SZ")
    h = hashlib.sha256(f"{ts}{msg}".encode()).hexdigest()[:16]
    if not os.path.isfile(STATE):
        snapshot()
    with open(STATE, "a") as f:
        f.write(f"- [{ts}] [{h}] {msg}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("snapshot", "log", "read"):
        print(__doc__); sys.exit(1)
    if sys.argv[1] == "snapshot":
        snapshot()
        print(f"[banked] snapshot written {STATE}")
    elif sys.argv[1] == "log":
        log(" ".join(sys.argv[2:]) or "(empty)")
        print("[banked] event logged")
    else:
        print(open(STATE).read() if os.path.isfile(STATE) else "(no state yet — run snapshot)")
