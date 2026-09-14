#!/usr/bin/env python3
"""exec_log.py — capture every executed script into Markor + sha256 index + SQLite chain.
Modes:
  wrap <interp> <args...>   — reads script from stdin, logs, executes, seals result
  x <file> [args...]        — logs + executes a script file
  list                      — recent executions
  verify                    — chain walk"""
import datetime, hashlib, json, os, sqlite3, subprocess, sys

ROOT = os.environ.get("SYN_ROOT", os.path.expanduser("~/src/openroot"))
DB   = os.path.join(ROOT, "data", "exec_log.db")

def markor_dir():
    for cand in (os.environ.get("MARKOR_DIR"),
                 "/storage/emulated/0/Documents/openroot-scripts"):
        if cand:
            try:
                os.makedirs(cand, exist_ok=True)
                probe = os.path.join(cand, ".probe"); open(probe, "w").write("x"); os.remove(probe)
                return cand
            except OSError:
                continue
    return os.path.join(ROOT, "markor-mirror")  # fallback: Syncthing carries it to phone later

SCHEMA = """
CREATE TABLE IF NOT EXISTS chain (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, kind TEXT NOT NULL,
  payload TEXT NOT NULL, prev_hash TEXT NOT NULL, hash TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS execs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, interpreter TEXT, source TEXT,
  sha256 TEXT, lines INTEGER, exit_code INTEGER, duration_s REAL,
  markor_path TEXT, output_tail TEXT, block_hash TEXT);
CREATE INDEX IF NOT EXISTS idx_execs_sha ON execs(sha256);
"""

def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def conn():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    c = sqlite3.connect(DB); c.executescript(SCHEMA); return c
def head(c):
    r = c.execute("SELECT hash FROM chain ORDER BY id DESC LIMIT 1").fetchone()
    return r[0] if r else "0" * 64
def bhash(prev, payload):
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256((prev + "|" + blob).encode()).hexdigest()
def append_block(c, payload):
    h = bhash(head(c), payload)
    c.execute("INSERT INTO chain(ts,kind,payload,prev_hash,hash) VALUES(?,?,?,?,?)",
              (now(), "exec", json.dumps(payload, sort_keys=True, separators=(",", ":")),
               head(c), h))
    c.commit(); return h

def md_doc(interp, source, sha, lines, ts):
    return (
        "---\nid: EXEC-" + sha[:12] + "\n"
        "timestamp: " + ts + "\n"
        "type: script-execution\n"
        "interpreter: " + interp + "\n"
        "sha256: " + sha + "\n"
        "status: RUNNING\n---\n\n"
        "# Script Execution — " + ts + "\n\n"
        "**Interpreter:** " + interp + "  \n"
        "**Lines:** " + str(lines) + "  \n"
        "**Source:** " + source + "\n\n"
        "## Script Body\n\n```bash\n" + "{BODY}" + "\n```\n\n"
        "## Result\n\n_PENDING_\n"
    )

def finish_doc(path, exit_code, dur, tail):
    txt = open(path, encoding="utf-8").read()
    res = ("## Result\n\n**Exit code:** {ec}  \n**Duration:** {d:.3f}s\n\n"
           "### Output tail\n\n```\n{t}\n```\n").format(ec=exit_code, d=dur, t=tail)
    txt = txt.replace("status: RUNNING", "status: DONE-EXIT" + str(exit_code))
    txt = txt.replace("## Result\n\n_PENDING_\n", res)
    open(path, "w", encoding="utf-8").write(txt)

def rebuild_index(md, rows):
    lines = ["# Execution sha256 Index", "",
             "| timestamp | sha256 | exit | lines |", "|---|---|---|---|"]
    for ts, sha, ec, ln in rows:
        lines.append("| {} | `{}` | {} | {} |".format(ts, sha, ec, ln))
    open(os.path.join(md, "sha256-index.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")

def run_logged(argv, stdin_text):
    interp = argv[0]
    source = stdin_text if stdin_text is not None else (argv[1] if len(argv) > 1 else "?")
    body = stdin_text if stdin_text is not None else (
        open(source, encoding="utf-8", errors="replace").read() if os.path.isfile(source) else "")
    sha = hashlib.sha256(body.encode()).hexdigest()
    ts = now()
    lines = body.count("\n") + 1 if body else 0
    md = markor_dir(); os.makedirs(md, exist_ok=True)
    fname = ts.replace(":", "").replace("-", "") + "-" + sha[:10] + ".md"
    mpath = os.path.join(md, fname)
    open(mpath, "w", encoding="utf-8").write(md_doc(interp, source, sha, lines, ts).replace("{BODY}", body))

    t0 = datetime.datetime.now()
    p = subprocess.run(argv, input=(stdin_text.encode() if stdin_text is not None else None),
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    dur = (datetime.datetime.now() - t0).total_seconds()
    tail = p.stdout.decode(errors="replace")[-2000:]
    sys.stdout.write(p.stdout.decode(errors="replace"))

    c = conn()
    bh = append_block(c, dict(script_sha256=sha, interpreter=interp, source=str(source),
                               exit_code=p.returncode, duration_s=round(dur, 4)))
    c.execute("""INSERT INTO execs(ts,interpreter,source,sha256,lines,exit_code,duration_s,
                 markor_path,output_tail,block_hash) VALUES(?,?,?,?,?,?,?,?,?,?)""",
              (ts, interp, str(source), sha, lines, p.returncode, round(dur, 4),
               mpath, tail, bh)); c.commit()
    finish_doc(mpath, p.returncode, dur, tail)
    rebuild_index(md, c.execute(
        "SELECT ts,sha256,exit_code,lines FROM execs ORDER BY id DESC LIMIT 200").fetchall())
    print("[logged] {}  sha={}  exit={}  doc={}".format(ts, sha[:16] + "...", p.returncode, mpath))
    return p.returncode

def wrap_mode(args):
    stdin_text = sys.stdin.read()
    return run_logged([args[0]], stdin_text) if False else run_logged(args, stdin_text)

def x_mode(args):
    if not args: print("usage: x <script> [args...]"); return 2
    return run_logged(args, None)

def list_mode():
    c = conn()
    for r in c.execute("SELECT id,ts,interpreter,exit_code,duration_s,sha256 FROM execs ORDER BY id DESC LIMIT 15"):
        print("  #{:<4} {} {:<10} exit={:<3} {:.2f}s  {}".format(*r[:5], r[5][:12] + "..."))

def verify_mode():
    c, ok, n, prev = conn(), True, 0, "0" * 64
    for bid, ph, h, pl in c.execute("SELECT id,prev_hash,hash,payload FROM chain ORDER BY id"):
        n += 1
        if ph != prev or bhash(ph, json.loads(pl)) != h:
            ok = False; print("[verify] RED at block {}".format(bid)); break
        prev = h
    print("[verify] {} — {} blocks, head {}...".format("GREEN" if ok else "RED", n, prev[:16]))

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    a = sys.argv[2:]
    sys.exit({"wrap": lambda: wrap_mode(a) or 0, "x": lambda: x_mode(a),
              "list": lambda: (list_mode(), 0)[1], "verify": verify_mode}.get(mode, verify_mode)())
