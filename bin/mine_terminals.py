#!/usr/bin/env python3
"""mine_terminals.py — scan months of terminal logs; extract bespoke workflows + dossier."""
import collections, datetime, glob, hashlib, os, re, sqlite3, subprocess
LOGS = "/storage/emulated/0/Documents/terminal-logs"
DB = os.path.expanduser("~/src/openroot/data/terminal_mining.db")
PAT = re.compile(r"^\S*\s*\$\s+(.*)$")  # prompt-anchored
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
os.makedirs(os.path.dirname(DB), exist_ok=True)
c = sqlite3.connect(DB)
c.executescript("""CREATE TABLE IF NOT EXISTS cmds(id INTEGER PRIMARY KEY AUTOINCREMENT,
  log TEXT, cmd TEXT, sha TEXT); CREATE INDEX IF NOT EXISTS ix ON cmds(sha);
CREATE TABLE IF NOT EXISTS digests(log TEXT PRIMARY KEY, sha TEXT);""")
have = {r[0] for r in c.execute("SELECT log FROM digests")}
new = 0
for f in sorted(glob.glob(os.path.join(LOGS, "**", "*"), recursive=True)):
    if not os.path.isfile(f) or os.path.getsize(f) > 8_000_000: continue
    h = hashlib.sha256(open(f, "rb").read()).hexdigest()
    if h in have: continue
    have.add(h)
    for line in open(f, errors="replace"):
        m = PAT.match(line.strip())
        if m and (m.group(1) or m.group(2)):
            cmd = (m.group(1) or m.group(2)).strip()[:500]
            if cmd and not cmd.startswith("#"):
                c.execute("INSERT INTO cmds(log,cmd,sha) VALUES(?,?,?)",
                         (f, cmd, hashlib.sha256(cmd.encode()).hexdigest())); new += 1
    c.execute("INSERT OR REPLACE INTO digests VALUES(?,?)", (f, h))
c.commit()
rows = c.execute("SELECT cmd, COUNT(*) n FROM cmds GROUP BY sha ORDER BY n DESC LIMIT 30").fetchall()
seqs = c.execute("SELECT log, cmd FROM cmds ORDER BY id").fetchall()
pair = collections.Counter()
for (log, cmd), (log2, cmd2) in zip(seqs, seqs[1:]):
    if log == log2 and cmd != cmd2:
        pair[(cmd.split()[0], cmd2.split()[0])] += 1
L = ["# TERMINAL-MINED DOSSIER — " + datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%MZ"),
     f"_{new} new commands ingested; corpus {len(have)} logs_", "",
     "## Most-used commands (your real bespoke toolkit)", ""]
for cmd, n in rows: L.append(f"- ({n}x) `{cmd[:110]}`")
L += ["", "## Recurring command pipelines (candidate one-shot workflows)", ""]
for (a, b), n in pair.most_common(15): L.append(f"- ({n}x) `{a} -> {b}`")
L += ["", "## Next move", "- cluster top pipelines into named workflows; push to bin/ as one-shots"]
fp = os.path.expanduser("~/src/openroot/lever/audits/terminal_dossier.md")
open(fp, "w").write("\n".join(L) + "\n")
print(f"[mine] {new} commands ingested, {len(pair)} pipeline patterns")
print(f"[dossier] {fp}")
g = sh(f"gh gist create {fp} --public --desc 'OpenRoot terminal-mined bespoke workflow dossier'")
print("[gist]", g or "publish failed — file is local")
