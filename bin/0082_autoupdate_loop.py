import os, json, time, sqlite3, hashlib, subprocess, urllib.request
LOOP_SECS = 1800
ROOTS = ["/storage/emulated/0/openroot"]
DB = "/storage/emulated/0/openroot/logs/autoupdate.db"
SKIP = {".git","__pycache__","node_modules","salvage","attic","build","venv",".cache",".sync-conflict"}

def sh(*c, cwd=None):
    try: return subprocess.check_output(c, cwd=cwd, stderr=subprocess.DEVNULL, text=True).strip()
    except Exception: return ""

def llm(prompt):
    try:
        req = urllib.request.Request("http://localhost:11434/api/generate",
            data=json.dumps({"model":"qwen2.5-coder:7b","stream":False,
                             "prompt":prompt}).encode(),
            headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)["response"].strip().split("\n")[0][:70]
    except Exception: return "openroot autoupdate: periodic drift commit"

def log(con, repo, action, detail):
    con.execute("""INSERT INTO events(ts,repo,action,detail,fp) VALUES(?,?,?,?,?)""",
        (time.time(), repo, action, detail,
         hashlib.sha256((repo+action+detail).encode()).hexdigest()[:16]))
    con.commit(); print(f"[{action}] {repo}: {detail[:90]}")

def find_repos():
    out = []
    for root in ROOTS:
        for dp, dns, _ in os.walk(root):
            dns[:] = [d for d in dns if d not in SKIP]
            if ".git" in dns and dp != root:
                out.append(dp); dns.remove(".git")
    return out

con = sqlite3.connect(DB)
con.execute("""CREATE TABLE IF NOT EXISTS events(
    ts REAL, repo TEXT, action TEXT, detail TEXT, fp TEXT PRIMARY KEY)""")

while True:
    for repo in find_repos():
        if not sh("git","-C",repo,"rev-parse","HEAD"): continue
        upstream = sh("git","-C",repo,"rev-parse","--abbrev-ref","@{u}")
        sh("git","-C",repo,"fetch","origin")
        if upstream and sh("git","-C",repo,"rev-parse","HEAD") != sh("git","-C",repo,"rev-parse",upstream):
            if sh("git","-C",repo,"pull","--ff-only"):
                log(con, repo, "pull", f"fast-forwarded to {sh('git','-C',repo,'log','--oneline','-1')}")
            else:
                log(con, repo, "held", "pull blocked, dirty tree — inspect manually"); continue
        dirty = sh("git","-C",repo,"status","--porcelain")
        if not dirty: continue
        names = [l[3:] for l in dirty.split("\n") if l.strip()][:10]
        msg = llm(f"Write ONE conventional git commit line (max 70 chars, no quotes) for these changed files in repo {os.path.basename(repo)}: {names}")
        if sh("git","-C",repo,"add","-A") is None and sh("git","-C",repo,"commit","-m",msg):
            log(con, repo, "commit", f"{msg} ({len(names)} files)")
            if not sh("git","-C",repo,"status","--porcelain") and sh("git","-C",repo,"push"):
                log(con, repo, "push", f"shipped '{msg}'")
            else:
                log(con, repo, "held", "push failed or tree dirty after commit")
        else:
            log(con, repo, "held", "nothing staged or commit refused")
    time.sleep(LOOP_SECS)
