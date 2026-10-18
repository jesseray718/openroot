#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Mistake composter v1 — real-time terminal mistake ingestion.
sha256(shape)-keyed solution cache; recurrence = instant non-recompute restore."""
import sys, os, re, sqlite3, hashlib, datetime

ROOT = "/home/jesse/openroot"
DB = ROOT + "/data/mistakes.db"
SOLDIR = ROOT + "/context_bridge/mistake_solutions"

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def norm(cmd):
    c = re.sub(r"\s+", " ", cmd.strip())
    for _ in range(4):
        c = re.sub(r"^(sudo |[A-Za-z_][A-Za-z0-9_]*=\S+) ?", "", c)
    return c

def shape_of(cmd):
    c = norm(cmd)
    c = re.sub(r"([^\s]*/[^\s]*|\./[^\s]*|~[^\s]*)", "PATH", c)
    c = re.sub(r"\S+\.\w{1,4}(\s|$)", "FILE\\1", c)
    c = re.sub(r"\d+", "#", c)
    c = re.sub(r"'[^']*'", "'X'", c)
    c = re.sub(r'"[^"]*"', '"X"', c)
    return c

def key_of(s):
    return hashlib.sha256(s.encode()).hexdigest()[:16]

SCHEMA = """
CREATE TABLE IF NOT EXISTS mistakes(
  key TEXT PRIMARY KEY, shape TEXT, last_cmd TEXT,
  occurrences INTEGER DEFAULT 1, exits TEXT,
  first_seen TEXT, last_seen TEXT,
  solved INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS solutions(
  key TEXT PRIMARY KEY, solution TEXT, path TEXT,
  solved_by TEXT, solved_at TEXT);
CREATE VIRTUAL TABLE IF NOT EXISTS solution_fts USING fts5(
  key UNINDEXED, shape, solution);
"""

def db():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    c = sqlite3.connect(DB)
    c.executescript(SCHEMA)
    return c

def link(path, text):
    return "\x1b]8;;file://%s\x07\x1b[1;36m%s\x1b[0m\x1b]8;;\x07" % (path, text)

STOP = {"the","and","for","with","etc","tmp","home","root","bin"}

def hook(ec, cmd):
    sh = shape_of(cmd)
    k = key_of(sh)
    c = db()
    row = c.execute(
        "SELECT occurrences,solved FROM mistakes WHERE key=?", (k,)
    ).fetchone()
    if row:
        occ, solved = row
        occ += 1
        c.execute(
            "UPDATE mistakes SET occurrences=?,last_cmd=?,last_seen=?,"
            "exits=exits||? WHERE key=?",
            (occ, cmd, now(), "," + str(ec), k))
    else:
        occ, solved = 1, 0
        c.execute(
            "INSERT INTO mistakes(key,shape,last_cmd,occurrences,"
            "exits,first_seen,last_seen) VALUES(?,?,?,?,?,?,?)",
            (k, sh, cmd, 1, str(ec), now(), now()))
    c.commit()
    if solved:
        s = c.execute(
            "SELECT solution,path,solved_at FROM solutions WHERE key=?",
            (k,)).fetchone()
        if s:
            sol, p, when = s
            print("[COMPOST] [PASS] non-recompute: mistake "
                  "shape seen %d times, solved since %s" % (occ, when))
            print("[COMPOST] known fix: %s" % sol[:200])
            print("[COMPOST] full record: %s" % link(p, p))
            c.close()
            return
    print("[COMPOST] key=%s — unsolved, occurrence #%d" % (k, occ))
    toks = [t for t in re.findall(r"[a-z_]{3,}", sh)
            if t not in STOP][:6]
    if toks:
        q = " ".join(toks)
        try:
            near = c.execute(
                "SELECT key FROM solution_fts WHERE solution_fts "
                "MATCH ? LIMIT 3", (q,)).fetchall()
            for n in near:
                print("[COMPOST] near-match solved variant: "
                      "python3 bin/mistake_engine_v1.py show %s" % n[0])
        except Exception:
            pass
    print("[COMPOST] solve it: python3 bin/mistake_engine_v1.py "
          "solve %s '<the fix>'" % k)
    c.close()

def solve(k, sol):
    if len(k) < 8 or not re.match(r"^[0-9a-f]+$", k):
        print("[held] key must be >=8 hex chars"); sys.exit(1)
    c = db()
    row = c.execute(
        "SELECT key FROM mistakes WHERE key LIKE ?", (k + "%",)
    ).fetchone()
    if not row:
        print("[held] no mistake matches that key"); sys.exit(1)
    k = row[0]
    os.makedirs(SOLDIR, exist_ok=True)
    p = SOLDIR + "/" + k + ".md"
    with open(p, "w") as f:
        f.write("---\nid: %s\nts: %s\ntype: mistake-solution\n"
                "status: solved\nagape_score: high\n---\n" % (k, now()))
        f.write("# Mistake %s\n\nSHA256-shape key: %s\n\n"
                "## Solution\n%s\n" % (k, k, sol))
    c.execute(
        "INSERT OR REPLACE INTO solutions(key,solution,path,"
        "solved_by,solved_at) VALUES(?,?,?,?,?)",
        (k, sol, p, "jesse", now()))
    c.execute("UPDATE mistakes SET solved=1 WHERE key=?", (k,))
    c.execute("DELETE FROM solution_fts WHERE key=?", (k,))
    c.execute("INSERT INTO solution_fts(key,shape,solution) "
              "SELECT key,shape,? FROM mistakes WHERE key=?", (sol, k))
    c.commit()
    print("[banked] solution sealed: %s" % p)
    c.close()

def show(k):
    c = db()
    row = c.execute(
        "SELECT shape,last_cmd,occurrences,exits,first_seen,"
        "solved FROM mistakes WHERE key LIKE ?",
        (k + "%",)).fetchone()
    if not row:
        print("[held] no match"); sys.exit(1)
    print("shape:    %s" % row[0])
    print("last_cmd: %s" % row[1])
    print("occurred: %d times (exits %s)" % (row[2], row[3]))
    print("first:    %s" % row[4])
    print("solved:   %s" % bool(row[5]))
    s = c.execute("SELECT solution,path FROM solutions "
                  "WHERE key LIKE ?", (k + "%",)).fetchone()
    if s:
        print("solution: %s" % s[0])
        print("record:   %s" % link(s[1], s[1]))
    c.close()

def compost():
    c = db()
    tot = c.execute("SELECT COUNT(*) FROM mistakes").fetchone()[0]
    solved = c.execute("SELECT COUNT(*) FROM solutions").fetchone()[0]
    occ = c.execute("SELECT COALESCE(SUM(occurrences),0) "
                    "FROM mistakes").fetchone()[0]
    top = c.execute(
        "SELECT key,shape,occurrences,last_cmd FROM mistakes "
        "WHERE solved=0 ORDER BY occurrences DESC LIMIT 10").fetchall()
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    rpt = ROOT + "/context_bridge/compost-%s.md" % stamp
    with open(rpt, "w") as f:
        f.write("# Compost Report — %s\n\n" % now())
        f.write("- distinct mistakes: %d | solved: %d | "
                "total occurrences: %d\n" % (tot, solved, occ))
        f.write("- non-recompute rate: %.1f%%\n"
                % (100.0 * solved / max(tot, 1)))
        f.write("\n## Top unsolved (compost the hot ones first)\n\n")
        for k, sh, oc, lc in top:
            f.write("- `%s` x%d — %s\n" % (k, oc, lc[:120]))
    print("[COMPOST] distinct=%d solved=%d occurrences=%d "
          "recycle=%.1f%%" % (tot, solved, occ,
                              100.0 * solved / max(tot, 1)))
    print("[COMPOST] [banked] report: %s" % rpt)
    c.close()

def main():
    a = sys.argv[1:]
    if len(a) >= 3 and a[0] == "hook":
        hook(int(a[1]), " ".join(a[2:]))
    elif len(a) >= 3 and a[0] == "solve":
        solve(a[1], " ".join(a[2:]))
    elif len(a) == 2 and a[0] == "show":
        show(a[1])
    elif a[:1] == ["compost"]:
        compost()
    else:
        print("usage: hook EC CMD | solve KEY FIX | show KEY | compost")
        sys.exit(1)

if __name__ == "__main__":
    main()
