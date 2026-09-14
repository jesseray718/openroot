#!/usr/bin/env python3
"""circuit_forge.py v0.1 — AST-introspect all repo python organs into a capability
registry, SHA256-hash every file, report candidate circuits (A outputs -> B inputs).
No execution of discovered code — v0.2 will gate that behind CONFIRM + 3B grading."""
import ast, hashlib, os, sqlite3, datetime

R = os.path.expanduser("~/src/openroot")
SCAN_DIRS = [R + "/bin", R + "/lever", R + "/synthesis", R + "/scripts"]
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def organs_of(path):
    try:
        tree = ast.parse(open(path, errors="replace").read())
    except SyntaxError:
        return []
    out = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            params = [a.arg for a in node.args.args]
            returns = []
            for n in ast.walk(node):
                if isinstance(n, ast.Return) and isinstance(n.value, ast.Name):
                    returns.append(n.value.id)
            out.append((node.name, params, returns or ["?"]))
    return out

c = sqlite3.connect(R + "/lever/db/lever.db")
c.executescript("""CREATE TABLE IF NOT EXISTS capability_registry(
  organ TEXT, file TEXT, params TEXT, outputs TEXT, file_sha TEXT, ts TEXT,
  PRIMARY KEY(organ, file));
CREATE TABLE IF NOT EXISTS file_hashes(file TEXT PRIMARY KEY, sha TEXT, ts TEXT);""")

n_files, n_organs = 0, 0
for d in SCAN_DIRS:
    for root, _, files in os.walk(d):
        if ".git" in root or "attic" in root:
            continue
        for fn in files:
            if not fn.endswith(".py"):
                continue
            p = os.path.join(root, fn); n_files += 1
            sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
            c.execute("INSERT OR REPLACE INTO file_hashes VALUES(?,?,?)", (p, sha, NOW))
            for name, params, outs in organs_of(p):
                c.execute("INSERT OR REPLACE INTO capability_registry VALUES(?,?,?,?,?,?)",
                          (name, p, ",".join(params), ",".join(outs), sha, NOW))
                n_organs += 1
c.commit()

regs = c.execute("SELECT organ, params, outputs FROM capability_registry").fetchall()
print("[forge] %d files hashed, %d organs registered" % (n_files, n_organs))
edges = 0
for a, ap, ao in regs:
    for b, bp, bo in regs:
        if a == b:
            continue
        for o in ao:
            if o in bp.split(",") and o != "?":
                print("   %s --%s--> %s" % (a, o, b)); edges += 1
print("[forge] %d candidate circuit edges" % edges if edges else "[forge] 0 edges yet — v0.2 widens matching")
print("[forge] execution wiring arrives v0.2 (CONFIRM=1 gated, 3B-graded)")
