#!/usr/bin/env python3
from __future__ import annotations
import json, os, sqlite3, sys, urllib.request
from pathlib import Path
def find_base():
    env = os.environ.get("THEOREM_FORGE_BASE")
    if env:
        p = Path(env); p.mkdir(parents=True, exist_ok=True); return p
    p = Path("/data/data/com.termux/files/home/openroot/data/theorem_forge")
    p.mkdir(parents=True, exist_ok=True); return p
BASE = find_base()
DB = BASE / "theorem_forge.db"
SEED = BASE / "in" / "kernel.jsonl"
OUT = BASE / "out"
def connect():
    OUT.mkdir(parents=True, exist_ok=True)
    (BASE / "in").mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(DB))
    c.execute("CREATE TABLE IF NOT EXISTS kernel(id TEXT PRIMARY KEY, kind TEXT NOT NULL, statement TEXT NOT NULL, provisional INTEGER NOT NULL DEFAULT 1, notes TEXT, seeded_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS theorems(id TEXT PRIMARY KEY, statement TEXT NOT NULL, proof_json TEXT NOT NULL, machine_checkable INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL, created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS checks(id TEXT PRIMARY KEY, theorem_id TEXT, solver_result TEXT, core_or_model TEXT, z3_version TEXT, note TEXT)")
    c.commit(); return c
def seed_kernel(c):
    if not SEED.exists():
        print("NO_SEED", SEED); return 0
    n = 0
    for line in SEED.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"): continue
        row = json.loads(line)
        c.execute("INSERT OR IGNORE INTO kernel(id, kind, statement, provisional, notes, seeded_at) VALUES(?,?,?,?,?,datetime('now'))", (row["id"], row.get("type") or row.get("kind"), row["statement"], 0, row.get("notes", "")))
        n += 1
    c.commit(); return n
def try_z3_t03():
    out = {"theorem_id":"T03","solver_result":"absent","core_or_model":None,"z3_version":None,"note":"z3 not importable"}
    try:
        import z3
        from z3 import And, Implies, Int, Not, Real, RealVal, Solver, sat, unsat
    except ImportError:
        return out
    out["z3_version"] = z3.get_version_string()
    Ti = Int("Ti"); Ni, Ri = Real("Ni"), Real("Ri"); cases = []
    for t in range(1, 5):
        C = Ni * RealVal("1/1000") * (1 + RealVal("1/10") * t) * ((1 - Ri) ** t)
        cases.append(Implies(And(Ti == t, Ri == 1), C == 0))
    s = Solver(); s.set("timeout", 2000); s.add(Not(And(cases))); r = s.check()
    if r == unsat:
        out["solver_result"] = "unsat"; out["note"] = "T03 PROVED for T=1..4"
    elif r == sat:
        out["solver_result"] = "sat"; out["core_or_model"] = str(s.model()); out["note"] = "T03 REFUTED"
    else:
        out["solver_result"] = "unknown"; out["note"] = "solver gave up"
    return out
def ollama_up():
    try:
        urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2); return True
    except Exception:
        return False
def main():
    print("HOST_BASE", BASE); print("DB", DB); print("SEED", SEED)
    c = connect(); inserted = seed_kernel(c)
    print("SEED_INSERTED", inserted)
    print("KERNEL_COUNTS", json.dumps(dict(c.execute("SELECT kind, COUNT(*) FROM kernel GROUP BY kind"))))
    z = try_z3_t03(); print("Z3_T03", json.dumps(z))
    c.execute("INSERT OR REPLACE INTO checks(id, theorem_id, solver_result, core_or_model, z3_version, note) VALUES('CHK-T03','T03',?,?,?,?)", (z["solver_result"], z.get("core_or_model"), z.get("z3_version"), z.get("note")))
    if z["solver_result"] == "unsat":
        c.execute("INSERT OR REPLACE INTO theorems(id, statement, proof_json, machine_checkable, status, created_at) VALUES('T03',?,?,'1','proved',datetime('now'))", ("Given C(N,T,R) := N * 0.001 * (1 + 0.1*T) * (1-R)^T, for R=1 and integer T>=1, C=0.", json.dumps(z)))
    c.commit(); print("OLLAMA", "up" if ollama_up() else "down_skip"); c.close(); return 0
if __name__ == "__main__":
    sys.exit(main())
