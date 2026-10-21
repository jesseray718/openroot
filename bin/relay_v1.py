#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# relay_v1.py — Template Relay: capability-masked multi-actor fill loop.
# SPDX-License-Identifier: GPL-3.0
# Node-agnostic DB path: OPENROOT_DIR env, Termux, or OptiPlex.
import argparse, hashlib, json, os, sqlite3, subprocess, sys, tempfile
import urllib.request

if os.environ.get("OPENROOT_DIR"):
    DB_PATH = os.path.join(os.environ["OPENROOT_DIR"], "data", "relay.db")
elif os.path.isdir("/data/data/com.termux/files/home/openroot"):
    DB_PATH = ("/data/data/com.termux/files/home/openroot"
               "/data/relay.db")
else:
    DB_PATH = "/home/jesse/openroot/data/relay.db"
OLLAMA = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")

SCHEMA = """
CREATE TABLE IF NOT EXISTS artifact(
  id INTEGER PRIMARY KEY, kind TEXT, title TEXT, status TEXT DEFAULT 'open',
  created TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS slot(
  id INTEGER PRIMARY KEY, artifact_id INT REFERENCES artifact(id),
  name TEXT, capability TEXT, difficulty INT, checks TEXT,
  body TEXT DEFAULT '', status TEXT DEFAULT 'empty',
  attempts INT DEFAULT 0, filled_by TEXT, verdict TEXT, ord INT);
CREATE TABLE IF NOT EXISTS actor(
  id INTEGER PRIMARY KEY, name TEXT UNIQUE, endpoint TEXT, model TEXT,
  tier TEXT, capabilities TEXT, max_difficulty INT);
CREATE TABLE IF NOT EXISTS solution(
  sid INTEGER PRIMARY KEY, slot_name TEXT, problem_hash TEXT, prompt_digest TEXT,
  body TEXT, verdict TEXT, actor TEXT, ts TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE VIRTUAL TABLE IF NOT EXISTS solution_fts USING fts5(body, slot_name);
CREATE TABLE IF NOT EXISTS solution_vec(
  sid INTEGER PRIMARY KEY REFERENCES solution(sid), dim INT, vec TEXT);
CREATE TABLE IF NOT EXISTS relay_log(
  id INTEGER PRIMARY KEY, slot_id INT, actor TEXT, outcome TEXT, note TEXT,
  ts TEXT DEFAULT CURRENT_TIMESTAMP);
"""

TEMPLATE = {"kind": "research_dossier", "title": "OpenRoot Dossier v1", "slots": [
 {"name":"abstract",     "capability":"synthesize","difficulty":4,
  "checks":[{"type":"min_words","value":80},{"type":"contains","value":"falsifiable"}]},
 {"name":"background",   "capability":"prose","difficulty":2,
  "checks":[{"type":"min_words","value":200}]},
 {"name":"method",       "capability":"prose","difficulty":3,
  "checks":[{"type":"min_words","value":150}]},
 {"name":"analysis_code","capability":"code","difficulty":3,
  "checks":[{"type":"py_compile"},{"type":"contains","value":"def "}]},
 {"name":"theorem_block","capability":"theorem","difficulty":4,
  "checks":[{"type":"contains","value":"QED"}]},
 {"name":"conclusion",   "capability":"synthesize","difficulty":3,
  "checks":[{"type":"min_words","value":100}]},
]}

ACTORS = [
 {"name":"qwen7b-builder","endpoint":OLLAMA+"/api/generate",
  "model":"qwen2.5-coder:7b","tier":"local7b",
  "capabilities":"code,prose","max_difficulty":3},
 {"name":"qwen3b-grader","endpoint":OLLAMA+"/api/generate",
  "model":"qwen2.5:3b","tier":"local3b",
  "capabilities":"grade","max_difficulty":2},
 {"name":"api-bigbrain","endpoint":"https://openrouter.ai/api/v1/chat/completions",
  "model":"meta-llama/llama-3.3-70b-instruct:free","tier":"api",
  "capabilities":"synthesize,theorem,prose,code","max_difficulty":5},
]

def db():
    con = sqlite3.connect(DB_PATH); con.row_factory = sqlite3.Row; return con

def log(con, sid, actor, outcome, note=""):
    con.execute("INSERT INTO relay_log(slot_id,actor,outcome,note) VALUES(?,?,?,?)",
                (sid, actor, outcome, note)); con.commit()

def embed(text):
    try:
        req = urllib.request.Request(OLLAMA+"/api/embeddings",
            data=json.dumps({"model":"nomic-embed-text","prompt":text}).encode(),
            headers={"Content-Type":"application/json"})
        return json.loads(urllib.request.urlopen(req, timeout=60).read())["embedding"]
    except Exception:
        return None

def cosine(a, b):
    dot=sum(x*y for x,y in zip(a,b))
    na=sum(x*x for x in a)**.5; nb=sum(x*x for x in b)**.5
    return dot/(na*nb) if na and nb else 0.0

def retrieve(con, query, k=3):
    scored = {}
    try:
        rows = con.execute(
            "SELECT sid FROM solution_fts WHERE solution_fts MATCH ? LIMIT 20",
            (query.replace('"','""'),)).fetchall()
        for r, row in enumerate(rows):
            scored[row[0]] = scored.get(row[0], 0) + 1/(60+r)
    except sqlite3.OperationalError:
        pass
    q = embed(query)
    if q:
        for row in con.execute(
            "SELECT sv.sid, sv.vec FROM solution_vec sv "
            "JOIN solution s ON s.sid=sv.sid WHERE s.verdict='PASS'").fetchall():
            try:
                scored[row[0]] = scored.get(row[0],0) + cosine(q, json.loads(row[1]))
            except Exception:
                pass
    top = sorted(scored.items(), key=lambda kv:-kv[1])[:k]
    out = []
    for sid, _ in top:
        r = con.execute("SELECT slot_name,body FROM solution_fts WHERE rowid=?",
                        (sid,)).fetchone()
        if r: out.append("[prior:%s]\n%s" % (r["slot_name"], r["body"][:600]))
    return out

def call_actor(actor, prompt):
    try:
        if actor["tier"].startswith("local"):
            payload = {"model":actor["model"],"prompt":prompt,"stream":False,
                       "options":{"num_predict":2048}}
            req = urllib.request.Request(actor["endpoint"],
                data=json.dumps(payload).encode(),
                headers={"Content-Type":"application/json"})
            return json.loads(urllib.request.urlopen(req, timeout=600).read())["response"]
        if actor["tier"]=="api" and OPENROUTER_KEY:
            payload = {"model":actor["model"],
                       "messages":[{"role":"user","content":prompt}],
                       "max_tokens":2048}
            req = urllib.request.Request(actor["endpoint"],
                data=json.dumps(payload).encode(),
                headers={"Content-Type":"application/json",
                         "Authorization":"Bearer "+OPENROUTER_KEY,
                         "HTTP-Referer":"https://github.com/jesseray718/openroot",
                         "X-Title":"openroot-relay"})
            return json.loads(urllib.request.urlopen(req, timeout=300).read())\
                      ["choices"][0]["message"]["content"]
    except Exception as e:
        print("[actor-error] %s: %s" % (actor["name"], str(e)[:200]), flush=True)
        return None
    return None

def gate(checks, body):
    for c in checks:
        t, v = c["type"], c.get("value")
        if t=="min_words" and len(body.split())<v: return False, "words<%s"%v
        if t=="contains" and v.lower() not in body.lower(): return False, "missing '%s'"%v
        if t=="py_compile":
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
                f.write(body); p = f.name
            r = subprocess.run([sys.executable,"-m","py_compile",p],
                               capture_output=True)
            if r.returncode!=0: return False, "py_compile failed"
    return True, "ok"

def route(slot, registry):
    out = []
    for a in registry:
        if a["tier"] == "api" and not OPENROUTER_KEY:
            continue  # unauthenticated actor is not eligible
        if (slot["capability"] in a["capabilities"].split(",")
                and slot["difficulty"] <= a["max_difficulty"]):
            out.append(a)
    return out

def grade(registry, slot, body):
    gs = [a for a in registry if "grade" in a["capabilities"].split(",")]
    if not gs: return "NOTSURE"
    out = call_actor(gs[0],
        "Grade strictly. Reply exactly PASS, FAIL, or NOTSURE, then one "
        "sentence why.\n---\n%s" % body)
    if not out: return "NOTSURE"
    u = out.strip().upper()
    return "PASS" if u.startswith("PASS") else ("FAIL" if u.startswith("FAIL") else "NOTSURE")

def cmd_init(con):
    con.executescript(SCHEMA)
    for a in ACTORS:
        con.execute("""INSERT OR REPLACE INTO
            actor(name,endpoint,model,tier,capabilities,max_difficulty)
            VALUES(?,?,?,?,?,?)""",
            (a["name"],a["endpoint"],a["model"],a["tier"],
             a["capabilities"],a["max_difficulty"]))
    if not con.execute("SELECT 1 FROM artifact WHERE title=?",
                       (TEMPLATE["title"],)).fetchone():
        con.execute("INSERT INTO artifact(kind,title) VALUES(?,?)",
                    (TEMPLATE["kind"], TEMPLATE["title"]))
        aid = con.execute("SELECT last_insert_rowid()").fetchone()[0]
        for i, s in enumerate(TEMPLATE["slots"]):
            con.execute("""INSERT INTO
                slot(artifact_id,name,capability,difficulty,checks,ord)
                VALUES(?,?,?,?,?,?)""",
                (aid, s["name"], s["capability"], s["difficulty"],
                 json.dumps(s["checks"]), i))
    con.commit()
    print("[banked] schema + actors + template sealed")

def cmd_status(con):
    for s in con.execute("SELECT * FROM slot ORDER BY ord"):
        print("%9s  %-15s cap=%-10s diff=%d attempts=%d" %
              (s["status"], s["name"], s["capability"],
               s["difficulty"], s["attempts"]))

def cmd_run(con, max_rounds=20):
    registry = [dict(r) for r in con.execute("SELECT * FROM actor")]
    for rnd in range(max_rounds):
        slot = con.execute("""SELECT * FROM slot WHERE status='empty'
                              ORDER BY ord LIMIT 1""").fetchone()
        if slot is None:
            print("[banked] template complete or fully held")
            cmd_status(con); return
        checks = json.loads(slot["checks"])
        cands = route(slot, registry)
        if not cands:
            con.execute("UPDATE slot SET status='held' WHERE id=?", (slot["id"],))
            con.commit()
            log(con, slot["id"], "router", "held", "no actor covers mask")
            continue
        actor = cands[slot["attempts"] % len(cands)]
        priors = retrieve(con, "%s %s openroot" % (slot["name"], slot["capability"]))
        ctx = "\n\n".join(priors) if priors else "(no priors)"
        prompt = ("You are filling ONE slot of a larger template. Do ONLY this "
                  "slot.\nSlot: %s  Type: %s\nOutput ONLY slot content.\n"
                  "Prior verified solutions for grounding:\n%s\n---\n"
                  "Write the %s section now."
                  % (slot["name"], slot["capability"], ctx, slot["name"]))
        print("[relay] round %d slot '%s' -> %s" % (rnd, slot["name"], actor["name"]))
        body = call_actor(actor, prompt)
        if not body:
            con.execute("UPDATE slot SET attempts=attempts+1 WHERE id=?", (slot["id"],))
            con.commit()
            log(con, slot["id"], actor["name"], "skip", "no response")
            if slot["attempts"] + 1 >= 3:
                con.execute("UPDATE slot SET status='held' WHERE id=?",
                            (slot["id"],))
                con.commit()
                print("[held] %s skipped 3x" % slot["name"])
            continue
        ok, why = gate(checks, body)
        verdict = grade(registry, slot, body) if ok else "FAIL"
        ph = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        con.execute("""INSERT INTO
            solution(slot_name,problem_hash,prompt_digest,body,verdict,actor)
            VALUES(?,?,?,?,?,?)""",
            (slot["name"], ph, prompt[:200], body, verdict, actor["name"]))
        sid = con.execute("SELECT last_insert_rowid()").fetchone()[0]
        con.execute("INSERT INTO solution_fts(rowid,body,slot_name) VALUES(?,?,?)",
                    (sid, body, slot["name"]))
        v = embed(body)
        if v:
            con.execute("INSERT INTO solution_vec(sid,dim,vec) VALUES(?,?,?)",
                        (sid, len(v), json.dumps(v)))
        if ok and verdict == "PASS":
            con.execute("""UPDATE slot SET status='verified', body=?, filled_by=?,
                           verdict=? WHERE id=?""",
                        (body, actor["name"], verdict, slot["id"]))
            con.commit()
            log(con, slot["id"], actor["name"], "pass", "verified")
            print("[verified] %s" % slot["name"])
        else:
            con.execute("UPDATE slot SET attempts=attempts+1 WHERE id=?",
                        (slot["id"],))
            con.commit()
            log(con, slot["id"], actor["name"], verdict, "gate:%s" % why)
            if slot["attempts"] + 1 >= 3:
                con.execute("UPDATE slot SET status='held' WHERE id=?",
                            (slot["id"],))
                con.commit()
            print("[held-back] %s %s (%s)" % (slot["name"], verdict, why))
    print("[held] rounds exhausted; rerun or inspect held slots")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["init","run","status"])
    args = ap.parse_args()
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = db()
    {"init":cmd_init,"run":cmd_run,"status":cmd_status}[args.cmd](con)
