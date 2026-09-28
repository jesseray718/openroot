#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# openroot_superlinear_v1.py — CANARY SLV1
# Canonical entry point: pre-route gauntlet (cache->mistake chain->FTS5->gap-route),
# RAPL joule ledger, log compost harvest (tombstone protocol, no deletion),
# thermal export (low-grade pre-heat grade ONLY), cache_hit_rate metric.
import json, os, re, sqlite3, subprocess, sys, time, hashlib, glob
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/home/jesse/openroot")
DB = BASE / "data" / "superlinear" / "superlinear.db"
REG = BASE / "data" / "model_registry.json"
CANARY = "SLV1"

def now(): return datetime.now(timezone.utc).isoformat()

DEFAULT_REGISTRY = {
  "version": "v1-slv",
  "generated_at": now(),
  "models": {
    "qwen2.5-coder:7b":       {"role": "AUTHOR", "grade": "PASS"},
    "qwen2.5:3b":             {"role": "GRADER", "grade": "PASS", "latency_s": 0.4},
    "deepseek-r1:1.5b":       {"role": "THINK",  "grade": "OPEN"},
    "llama3.2:1b":            {"role": "TINY",   "grade": "OPEN"},
    "nomic-embed-text:latest":{"role": "EMBED",  "grade": "PASS"}
  },
  "routing_table": {
    "AUTHOR": ["qwen2.5-coder:7b"],
    "GRADE":   ["qwen2.5:3b"],
    "THINK":   ["deepseek-r1:1.5b"],
    "TINY":    ["llama3.2:1b"],
    "EMBED":   ["nomic-embed-text:latest"]
  }
}

def repair_registry():
    ok = False
    if REG.exists():
        try:
            json.loads(REG.read_text()); ok = True
        except Exception:
            pass
    if ok:
        print("[banked] registry OK — not touched"); return
    tmp = str(REG) + ".tmp"
    REG.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp, "w") as f: json.dump(DEFAULT_REGISTRY, f, indent=2)
    os.replace(tmp, REG)
    print(f"[FIXED] regenerated corrupted registry -> {REG}")

STOP = set("the a an of for to in on is are be with and or how what calculate compute design build make i my me".split())
def canonicalize(task: str) -> tuple:
    words = sorted(w for w in re.findall(r"[a-z0-9.]+", task.lower()) if w not in STOP)
    nums = sorted(re.findall(r"\d+(?:\.\d+)?", task))
    canon = " ".join(words + ["|"] + nums)
    return canon, hashlib.sha256(canon.encode()).hexdigest()

SCHEMA = """
CREATE TABLE IF NOT EXISTS pathways(
  task_hash TEXT PRIMARY KEY, canonical TEXT, verdict TEXT,
  artifact_path TEXT, model TEXT, joules REAL, ts TEXT);
CREATE TABLE IF NOT EXISTS gauntlet_log(
  id INTEGER PRIMARY KEY, ts TEXT, task_hash TEXT, gate TEXT,
  hit INTEGER, model TEXT, joules REAL, task_head TEXT);
CREATE TABLE IF NOT EXISTS telemetry(
  ts TEXT, pkg_uj INTEGER, dram_uj INTEGER, watts_est REAL, source TEXT);
CREATE TABLE IF NOT EXISTS harvest(
  id INTEGER PRIMARY KEY, ts TEXT, source TEXT, bytes_in INTEGER,
  lines_total INTEGER, lines_new INTEGER, distill_path TEXT, tombstone TEXT);
CREATE INDEX IF NOT EXISTS ix_gl ON gauntlet_log(ts);
"""

def db():
    c = sqlite3.connect(DB); c.executescript(SCHEMA); c.commit(); return c

RAPL_GLOB = "/sys/class/powercap/intel-rapl:*/energy_uj"
_last = {}
def read_rapl():
    uj_pkg = 0; sources = []
    for f in sorted(glob.glob(RAPL_GLOB)):
        try:
            v = int(Path(f).read_text().strip()); uj_pkg += v; sources.append(f)
        except Exception:
            pass
    if sources:
        uj, src = uj_pkg, "rapl"
    else:
        uj, src = int(65 * 1e6), "estimate"
    prev = _last.get(src)
    _last[src] = (uj, time.monotonic())
    return uj, src, prev

LOG_ROOTS = [BASE / "logs", BASE / "context_bridge"]

def fts5_lookup(canon_words: str) -> list:
    hits = []
    for dbf in (BASE / "data").glob("**/*.db"):
        try:
            fc = sqlite3.connect(f"file:{dbf}?mode=ro", uri=True)
            tables = [r[0] for r in fc.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")]
            fts = [t for t in tables if "fts" in t.lower() or t == "documents"]
            for t in fts:
                try:
                    q = " ".join(w for w in canon_words.split() if w != "|" and len(w) > 2)[:3]
                    rows = fc.execute(
                        f"SELECT rowid FROM {t} WHERE {t} MATCH ? LIMIT 5", (q,)).fetchall()
                    if rows: hits.append((str(dbf), t, len(rows)))
                except Exception: pass
            fc.close()
        except Exception: pass
    return hits

def gauntlet(task: str, c):
    canon, th = canonicalize(task)
    row = c.execute("SELECT verdict, artifact_path, model FROM pathways WHERE task_hash=?",
                    (th,)).fetchone()
    if row:
        log(c, th, "cache", 1, row[2], 0.0, task)
        return {"hit": "CACHE", "verdict": row[0], "artifact": row[1]}
    me_db = BASE / "data" / "mistake_engine.db"
    if me_db.exists():
        try:
            mc = sqlite3.connect(f"file:{me_db}?mode=ro", uri=True)
            tabs = [r[0] for r in mc.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")]
            for t in tabs:
                cols = [r[1] for r in mc.execute(f"PRAGMA table_info({t})")]
                if "key" in cols and ("fix" in cols or "solution" in cols):
                    fixcol = "fix" if "fix" in cols else "solution"
                    r = mc.execute(f"SELECT {fixcol} FROM {t} WHERE key=?",
                                   (th[:16],)).fetchone()
                    if r:
                        log(c, th, "mistake_chain", 1, "chain", 0.0, task)
                        return {"hit": "MISTAKE_CHAIN", "correction": r[0]}
        except Exception: pass
    fhits = fts5_lookup(canon)
    if fhits:
        log(c, th, "fts5", 1, "-", 0.0, task)
        return {"hit": "FTS5", "sources": fhits, "gap": "join + verify only"}
    log(c, th, "miss", 0, "-", 0.0, task)
    reg = json.loads(REG.read_text())
    role = "GRADE" if re.search(r"grade|check|validate", task, re.I) else "AUTHOR"
    model = reg["routing_table"][role][0]
    return {"hit": "MISS", "route_to": model, "role": role,
            "instruction": "route ONLY the gap; retrieve context first"}

def log(c, th, gate, hit, model, joules, task):
    c.execute("INSERT INTO gauntlet_log(ts, task_hash, gate, hit, model, joules, task_head)"
              " VALUES (?,?,?,?,?,?,?)", (now(), th, gate, hit, model, joules, task[:120]))
    c.commit()

def bank(task: str, verdict: str, artifact: str, model: str, joules: float, c):
    canon, th = canonicalize(task)
    c.execute("INSERT INTO pathways(task_hash, canonical, verdict, artifact_path, model, joules, ts)"
              " VALUES (?,?,?,?,?,?,?) ON CONFLICT(task_hash) DO UPDATE"
              " SET verdict=excluded.verdict, artifact_path=excluded.artifact_path,"
              " model=excluded.model, joules=excluded.joules",
              (th, canon, verdict, artifact, model, joules, now()))
    c.commit()
    return th

DISTILL_PATTERNS = [
    (r"COMPOST\] key=(\w+).*occurrence #(\d+)", "mistake_recurrence"),
    (r"SyntaxError[: ].*", "syntax_failure"),
    (r"command not found[: ](\S+)", "cmd_not_found"),
    (r"Traceback \(most recent call last\)", "python_traceback"),
]
def harvest():
    c = db()
    last_file = BASE / "data" / "superlinear" / "harvest_last.json"
    state = json.loads(last_file.read_text()) if last_file.exists() else {}
    total_in = total_new = 0; distills = []
    for root in LOG_ROOTS:
        if not root.exists(): continue
        for lf in root.rglob("*.log"):
            mtime = str(lf.stat().st_mtime)
            if state.get(str(lf)) == mtime: continue
            try: lines = lf.read_text(errors="ignore").splitlines()
            except Exception: continue
            state[str(lf)] = mtime
            total_in += sum(len(l) for l in lines)
            seen = set()
            for ln in lines:
                for pat, kind in DISTILL_PATTERNS:
                    m = re.search(pat, ln)
                    if m:
                        h = hashlib.sha256(ln.strip().encode()).hexdigest()[:16]
                        if h in seen: continue
                        seen.add(h); total_new += 1
                        distills.append({"kind": kind, "sha": h, "line": ln.strip()[:200]})
    dp = BASE / "data" / "superlinear" / "harvest" / f"distill_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    dp.write_text(json.dumps(distills, indent=2))
    c.execute("INSERT INTO harvest(ts, source, bytes_in, lines_total, lines_new, distill_path, tombstone)"
              " VALUES (?,?,?,?,?,?,?)",
              (now(), "logs+context_bridge", total_in, len(distills), total_new, str(dp),
               "tombstone: originals RETAINED pending human reclaim confirmation"))
    c.commit()
    tmp = last_file.with_suffix(".tmp"); tmp.write_text(json.dumps(state)); os.replace(tmp, last_file)
    print(f"[banked] harvest: bytes_in={total_in} distilled_new={total_new} -> {dp.name}")
    print("[held] reclaim candidates logged, NOTHING deleted (tombstone protocol)")

def thermal():
    c = db()
    rows = c.execute("SELECT COUNT(*), COALESCE(AVG(watts_est),0), "
                     "COUNT(DISTINCT date(ts)) FROM telemetry").fetchone()
    n, avg_w, days = rows
    hours = max(days, 1) * 24
    kwh = avg_w * hours / 1000
    hits = c.execute("SELECT COUNT(*) FROM gauntlet_log WHERE hit=1 AND gate!='miss'").fetchone()[0]
    joules_saved = hits * 65 * 60
    print(f"[SLV1][thermal] samples={n} avg_system_w={avg_w:.1f}W est_low_grade_heat={kwh:.2f} kWh")
    print("[SLV1][thermal] grade=LOW (pre-heat/labyrinth/greenhouse ONLY — NOT Stirling; COP-boundary language)")
    print(f"[SLV1][superlinear] cache/chain/fts5_hits={hits} joules_saved_estimate={joules_saved/1e6:.2f} MJ")

def metrics():
    c = db()
    tot = c.execute("SELECT COUNT(*) FROM gauntlet_log").fetchone()[0]
    hit = c.execute("SELECT COUNT(*) FROM gauntlet_log WHERE hit=1 AND gate!='miss'").fetchone()[0]
    rate = (hit / tot * 100) if tot else 0.0
    by_gate = c.execute("SELECT gate, COUNT(*), SUM(hit) FROM gauntlet_log GROUP BY gate").fetchall()
    print(f"[SLV1][metrics] cache_hit_rate={rate:.1f}% ({hit}/{tot})")
    for g, n, h in by_gate: print(f"  {g:14s} n={n} hits={h}")
    return rate

def route_sample(task: str):
    uj, src, _ = read_rapl()
    c = db(); r = gauntlet(task, c)
    print(json.dumps(r, indent=2)); print(f"[SLV1][telemetry] energy_counter={uj} uJ source={src}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "verify"
    if cmd == "repair-registry": repair_registry()
    elif cmd == "init": db(); repair_registry(); print(f"[banked] {DB}")
    elif cmd == "route": route_sample(" ".join(sys.argv[2:]))
    elif cmd == "sample":
        c = db(); interval = float(os.environ.get("SLV_INTERVAL", "10"))
        print(f"[SLV1][sample] RAPL loop every {interval}s — run under nohup")
        while True:
            uj, src, prev = read_rapl()
            watts = 65.0
            if prev and src == "rapl":
                du, dt = uj - prev[0], time.monotonic() - prev[1]
                if dt > 0 and du >= 0: watts = du / dt / 1e6
            c.execute("INSERT INTO telemetry VALUES (?,?,?,?,?)",
                      (now(), uj, 0, watts, src)); c.commit()
            time.sleep(interval)
    elif cmd == "harvest": harvest()
    elif cmd == "thermal": thermal()
    elif cmd == "metrics": metrics()
    elif cmd == "verify":
        db(); repair_registry(); metrics(); print(f"[{CANARY}] END [exit=0]")
    else:
        print(__doc__)
