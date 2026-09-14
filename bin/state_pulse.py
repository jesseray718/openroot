#!/usr/bin/env python3
"""state_pulse.py — regenerate STATE.md from ledgers, republish fixed gist."""
import datetime, os, sqlite3, subprocess
R = "/home/jesse/src/openroot"
STATE, IDF = f"{R}/STATE.md", f"{R}/data/state_pulse/gist_id.txt"
def now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def q(db, sql):
    try:
        if os.path.exists(db):
            return sqlite3.connect(f"file:{db}?mode=ro", uri=True).execute(sql).fetchall()
    except Exception: pass
    return []
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
SD, LD = f"{R}/synthesis/db/synthesis.db", f"{R}/lever/db/lever.db"
nb, hd = (q(SD, "SELECT COUNT(*), MAX(hash) FROM chain") or [(0, "none")])[0]
L = [f"# OPENROOT LIVING STATE — {now()}", "> auto-regenerated; do not hand-edit.",
     "## Resume: chain " + str(hd)[:16] + f" ({nb} blocks, verify: synthesis/synthesis.py verify)",
     "## ACRE mint gate: 0 J MEASURED — thermal instrumentation is the standing blocker", "",
     "## Least-resistance queue (fire first)"]
for cat, t, p in (q(LD, "SELECT category,title,priority FROM leverage_items "
                        "WHERE status='OPEN' ORDER BY priority ASC LIMIT 8") or []):
    L.append(f"- [{cat}] **{t}** (resistance {p})")
b = (q(SD, "SELECT COUNT(*) FROM bounties WHERE status='OPEN'") or [(0,)])[0][0]
j = (q(LD, "SELECT COALESCE(ROUND(SUM(joules),1),0) FROM joule_events") or [(0,)])[0][0]
L += ["", f"Bounties open: {b} | compute joules logged: {j}",
      "## Recent commits", sh(f"cd {R} && git log --oneline -3") or "(none)",
      "## Dirty tree", sh(f"cd {R} && git status --porcelain | head -5") or "(clean)",
      "", f"Writer node: OptiPlex {R} | A15 read-only verify",
      "Concepts: synthesis/SYNTHESIS_CARD.md + docs/concepts/CONCEPTS_INDEX.md"]
open(STATE, "w").write("\n".join(L) + "\n")
gid = open(IDF).read().strip() if os.path.exists(IDF) else ""
r = (subprocess.run(["gh", "gist", "edit", gid, STATE], capture_output=True, text=True) if gid
     else subprocess.run(["gh", "gist", "create", STATE, "--public",
     "--desc", "OpenRoot LIVING STATE (auto-refreshed)"], capture_output=True, text=True))
if r.returncode == 0 and not gid:
    os.makedirs(os.path.dirname(IDF), exist_ok=True)
    open(IDF, "w").write(r.stdout.strip().split("/")[-1])
    print("[pulse] gist created:", r.stdout.strip())
elif r.returncode != 0:
    print("[pulse] gist publish failed — local STATE.md still refreshed")
sh(f"cd {R} && git add STATE.md && git -c user.name=pulse -c user.email=p@o "
   "commit -m 'pulse: state refresh' --no-verify --quiet || true")
print(f"[pulse] {now()} — {nb} blocks, refreshed STATE.md")
