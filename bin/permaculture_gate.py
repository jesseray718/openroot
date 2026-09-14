#!/usr/bin/env python3
"""permaculture_gate.py — computational translation of Holmgren's 12 permaculture
principles. Each principle = a measurable predicate over on-disk ledgers. FAILED
predicates auto-enter lever.db leverage_items as fireable work. Idempotent."""
import datetime, glob, os, sqlite3, subprocess, time, urllib.request

R = "/home/jesse/src/openroot"
LD, SD, TM = R + "/lever/db/lever.db", R + "/synthesis/db/synthesis.db", R + "/data/terminal_mining.db"
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def one(db, sql, d=0):
    try:
        if os.path.exists(db):
            v = sqlite3.connect("file:" + db + "?mode=ro", uri=True).execute(sql).fetchone()
            if v and v[0] is not None: return v[0]
    except Exception: pass
    return d

def ollama_up():
    try:
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3); return True
    except Exception: return False

def commits24():
    r = subprocess.run("cd " + R + " && git log --oneline --since=24.hours 2>/dev/null | wc -l",
                       shell=True, capture_output=True, text=True)
    try: return int(r.stdout.strip())
    except ValueError: return 0

sm = int((time.time() - os.path.getmtime(R + "/STATE.md")) / 60) if os.path.exists(R + "/STATE.md") else 99999
jn  = one(LD, "SELECT COUNT(*) FROM joule_events")
jj  = one(LD, "SELECT COALESCE(ROUND(SUM(joules),1),0) FROM joule_events")
mea = one(SD, "SELECT COUNT(*) FROM capabilities WHERE grade='MEASURED'")
don = one(LD, "SELECT COUNT(*) FROM leverage_items WHERE status='DONE'")
grd = one(LD, "SELECT COUNT(*) FROM ai_grades")
qmv = one(LD, "SELECT COUNT(*) FROM quarantine WHERE moved IS NOT NULL")
cmd = one(TM, "SELECT COUNT(*) FROM cmds")
lgm = one(TM, "SELECT COUNT(*) FROM digests")
gist = ""
try: gist = open(R + "/data/state_pulse/gist_id.txt").read().strip()
except Exception: pass
shallow = bool(glob.glob(os.path.dirname(R) + "/*/.git/shallow"))
mn  = one(LD, "SELECT COUNT(*) FROM models")
edge = os.access("/mnt/sdb1/openroot", os.W_OK)
c24 = commits24()

CHECKS = [
 ("P01 Observe & Interact",            sm <= 15,       "STATE.md age " + str(sm) + " min (target <15)"),
 ("P02 Catch & Store Energy",          jn > 0,         str(jn) + " joule events, " + str(jj) + " J banked"),
 ("P03 Obtain a Yield",                mea > 0 or don > 0, "MEASURED capabilities " + str(mea) + ", DONE items " + str(don)),
 ("P04 Self-Regulation & Accept Feedback", grd > 0,    str(grd) + " ai-graded tasks recorded"),
 ("P05 Use & Value Renewables",        ollama_up(),    "local ollama serving (offline-first compute)"),
 ("P06 Produce No Waste",              qmv > 0,        str(qmv) + " clutter items quarantined to attic"),
 ("P07 Design From Patterns to Details", lgm > 0 and cmd > 100, str(cmd) + " commands mined from " + str(lgm) + " logs"),
 ("P08 Integrate Rather Than Segregate", bool(gist) and mn > 0, "shared living-state gist + unified fleet db"),
 ("P09 Small & Slow Solutions",        shallow,        "shallow depth-1 clones in use"),
 ("P10 Use & Value Diversity",         mn >= 2,        str(mn) + " distinct local models registered"),
 ("P11 Use Edges & Value the Marginal", edge,          "/mnt/sdb1 115G edge node writable"),
 ("P12 Creatively Use & Respond to Change", c24 >= 1,  str(c24) + " commits in last 24h"),
]

con = sqlite3.connect(LD)
con.executescript("CREATE TABLE IF NOT EXISTS permaculture_runs("
                  "ts TEXT, principle TEXT, passed INTEGER, evidence TEXT);")
L = ["# PERMACULTURE GATE — " + NOW,
     "> Holmgren's 12 principles as computable predicates over the OpenRoot ledgers.",
     "> FAIL rows are auto-queued in the lever ledger (category: permaculture).", ""]
npass = 0
for name, ok, ev in CHECKS:
    con.execute("INSERT INTO permaculture_runs(ts,principle,passed,evidence) VALUES(?,?,?,?)",
                (NOW, name, int(ok), ev))
    L.append("- " + ("PASS" if ok else "FAIL") + " **" + name + "** — " + ev)
    if ok: npass += 1
    else:
        con.execute("INSERT OR IGNORE INTO leverage_items(category,title,detail,priority) "
                    "VALUES('permaculture',?,?,1.55)",
                    (name, "gate failing: " + ev + " — fix the underlying check"))
con.commit()
pct = round(npass / 12 * 100)
L += ["", "## Adherence: " + str(npass) + "/12 (" + str(pct) + "%)",
      "", "Failures above are fireable items in `python3 lever/lever.py ledger`.", ""]
open(R + "/PERMACULTURE.md", "w").write("\n".join(L) + "\n")
print("[permaculture] " + str(npass) + "/12 (" + str(pct) + "%) — report: " + R + "/PERMACULTURE.md")
for name, ok, ev in CHECKS:
    if not ok: print("  FAIL " + name + ": " + ev)
