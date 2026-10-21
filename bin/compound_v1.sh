#!/usr/bin/env bash
# compound_v1.sh — THE COMPOUNDING ENGINE (v1.1)
# One command, end of session: lessons → lessons.db (idempotent by content-hash),
# fresh boot-seed for next session from LIVE repo state (staleness-proof).
# Usage: bin/compound_v1.sh   (dry-run default; CONFIRM=1 writes)
set -u
CONFIRM="${CONFIRM:-0}"
export GIT_PAGER=cat
REPO=/home/jesse/openroot
TS=$(date +%Y%m%d_%H%M%S)
SRC="compound-v1.1-${TS}"

python3 - "$REPO" "$SRC" "$CONFIRM" <<'PYEOF'
import sqlite3, sys, hashlib, datetime, os, glob
repo, src = sys.argv[1], sys.argv[2]
confirm = os.getenv("CONFIRM", "0") == "1"
con = sqlite3.connect(f"{repo}/data/lessons.db")

# ---- [gate] staleness probe FIRST ----
head = os.popen(f"git -C {repo} rev-parse --short HEAD").read().strip()
mt_lines = sum(1 for _ in open(f"{repo}/MASTER_TODO.md")) if os.path.exists(f"{repo}/MASTER_TODO.md") else 0
q_open = "SELECT COUNT(*) FROM tasks WHERE outcome IS NULL OR outcome=''"
tasks_open = con.execute(q_open).fetchone()[0]
print(f"[gate] HEAD={head} MASTER_TODO={mt_lines} lines tasks_open={tasks_open}")

# ---- [stage:lessons] scan recent lb logs, ingest failures/holds idempotently ----
logfiles = sorted(glob.glob("/home/jesse/lumo/logs/run-*.log"), key=os.path.getmtime, reverse=True)[:5]
print(f"[gate] scanning {len(logfiles)} recent lb log(s)")
new = []
for lf in logfiles:
    try:
        text = open(lf, errors="replace").read()
    except OSError:
        continue
    base = os.path.basename(lf)
    if "Traceback" in text or "FAILED" in text:
        new.append(("instrument-audit", f"Script failure in {base}",
                    "see log corpse", "triage log before reingest", "1 round", "recovered"))
    if "[held]" in text:
        new.append(("process", f"Gate fired (held op) in {base}",
                    "gate held a mutating/remote pattern or run failed", "review held gate fires", "manual check", "recovered"))

have = {r[0] for r in con.execute("SELECT recurrence_of FROM lessons") if r[0]}
added = 0
for row in new:
    sha = "hh:" + hashlib.sha256((row[1] + row[3]).encode()).hexdigest()[:8]
    if sha in have:
        continue
    if confirm:
        con.execute(
            "INSERT INTO lessons(ts,domain,mistake,root_cause,correction,cost,verified,recurrence_of,source) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (datetime.datetime.now(datetime.UTC).isoformat(), *row, sha, src))
        added += 1
    else:
        print(f"[held] would ingest: {row[1][:60]}")
if confirm:
    con.commit()
state = "banked" if confirm else "held"
print(f"[{state}] {added} auto-lessons ingested (dry_run={not confirm})")

# ---- [stage:seed] emit next-session boot seed from LIVE state ----
if confirm:
    open_tasks = [r[0] for r in con.execute(
        "SELECT description FROM tasks WHERE outcome IS NULL OR outcome='' ORDER BY rowid DESC LIMIT 10")]
    recent = [r[0] for r in con.execute("SELECT correction FROM lessons ORDER BY rowid DESC LIMIT 5")]
    seed = "# BOOT SEED - AUTO-COMPILED " + src + "\n" \
         + f"HEAD={head} MASTER_TODO={mt_lines} lines (CHECK git log -- MASTER_TODO.md BEFORE rebuild-work)\n" \
         + "## Immediate queue (from tasks table, open items)\n" \
         + "\n".join("- " + t for t in (open_tasks or ["(tasks table empty - curate)"])) + "\n" \
         + "## Fresh corrections (most recent lessons)\n" \
         + "\n".join("- " + r for r in recent) + "\n"
    sp = f"{repo}/context_bridge/seed_next-{src}.md"
    open(sp, "w").write(seed)
    print(f"[banked] next-session seed: {sp} sha16:{hashlib.sha256(seed.encode()).hexdigest()[:16]}")
PYEOF
echo "[exit=0]"
