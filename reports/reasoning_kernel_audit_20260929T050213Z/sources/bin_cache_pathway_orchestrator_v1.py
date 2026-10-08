#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
SLWF-CACHE-V1 :: cache_pathway_orchestrator_v1.py
Cache-first superlinear orchestrator.
Route: SHA256(task) -> pathway cache (SQLite FTS5) -> HIT = zero compute
       MISS -> warm-pool router (7B author / 3B grade) -> bank pathway
Usage:
  cache_pathway_orchestrator_v1.py run "task text"
  cache_pathway_orchestrator_v1.py battery
  cache_pathway_orchestrator_v1.py stats
"""
import hashlib, json, os, sqlite3, subprocess, sys, time

REPO = "/home/jesse/openroot"
DB_PATH = os.path.join(REPO, "data", "pathway_cache.db")
DECISIONS = os.path.join(REPO, "data", "orchestrator_decisions.jsonl")
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_PS = "http://localhost:11434/api/ps"
MODELS = {
    "author": "qwen2.5-coder:7b",   # 7B-only authoring constraint
    "grader": "qwen2.5:3b",
}
CANARY = "SLWF-CACHE-V1"

COMMON_TASKS = [
    "list all python files in bin/ with py count",
    "check git status for untracked files",
    "fetch current branch and divergence from origin/main",
    "count files in repo excluding .git and venvs",
    "get system load memory and disk usage",
]

def norm(task: str) -> str:
    return " ".join(task.lower().split()).strip()

def task_hash(task: str) -> str:
    return hashlib.sha256(norm(task).encode()).hexdigest()

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS pathways (
        task_hash TEXT PRIMARY KEY,
        task_text TEXT NOT NULL,
        route TEXT NOT NULL,
        solution TEXT NOT NULL,
        verdict TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""")
    conn.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS pathways_fts USING fts5(
        task_text, solution, content='pathways',
        content_rowid='rowid'
    )""")
    conn.execute("""CREATE TRIGGER IF NOT EXISTS pathways_ai AFTER INSERT ON pathways BEGIN
        INSERT INTO pathways_fts(rowid, task_text, solution)
        VALUES (new.rowid, new.task_text, new.solution);
    END""")
    conn.commit()
    return conn

def warm_pool() -> dict:
    """Return set of currently loaded models (warming staging area check)."""
    try:
        out = subprocess.run(["curl", "-s", "--max-time", "3", OLLAMA_PS],
                             capture_output=True, text=True).stdout
        return {m.get("name", "") for m in json.loads(out).get("models", [])}
    except Exception:
        return set()

def ollama(model: str, prompt: str, timeout: int = 240) -> tuple[str, dict]:
    t0 = time.time()
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False,
                          "options": {"num_ctx": 4096}})
    out = subprocess.run(["curl", "-s", "--max-time", str(timeout),
                          OLLAMA_URL, "-d", payload],
                         capture_output=True, text=True).stdout
    resp = json.loads(out)
    text = resp.get("response", "").strip()
    meta = {"latency_ms": int((time.time() - t0) * 1000),
            "tokens": len(text.split()),
            "warm": any(model in m for m in warm_pool())}
    return text, meta

def decide_route(task: str) -> str:
    """3B classifies; falls back to keyword heuristic on failure."""
    q = (f"Classify this task into exactly one route word: AUTHOR (needs new code "
         f"or file written), SHELL (simple git/system inspection command), GRADE "
         f"(evaluating quality). Task: {task}\nRoute:")
    try:
        ans, _ = ollama(MODELS["grader"], q, timeout=120)
        ans = ans.upper()
        for r in ("AUTHOR", "SHELL", "GRADE"):
            if r in ans:
                return r
    except Exception:
        pass
    for kw in ("write", "create", "build", "generate", "fix", "patch"):
        if kw in task.lower():
            return "AUTHOR"
    return "SHELL"

def author_solution(task: str, route: str) -> str:
    if route == "AUTHOR":
        prompt = (f"You are the OpenRoot 7B builder. Produce a single, complete, "
                  f"idempotent solution for this task. Code or commands only.\nTask: {task}")
        sol, _ = ollama(MODELS["author"], prompt)
        return sol if sol else "# 7B empty response; pathway marked DRAFT"
    prompt = (f"You are the OpenRoot helper. Provide a single robust shell/python "
              f"command sequence (one command per line) to accomplish this.\nTask: {task}")
    sol, _ = ollama(MODELS["grader"], prompt, timeout=180)
    return sol if sol else "# 3B empty response; pathway marked DRAFT"

def grade_solution(solution: str) -> str:
    q = ("Judge this solution: complete, syntactically plausible, harmless? "
         "Answer one word GREEN or RED.\nSolution:\n" + solution[:1500])
    try:
        ans, _ = ollama(MODELS["grader"], q, timeout=120)
        return "GREEN" if "GREEN" in ans.upper() else "RED"
    except Exception:
        return "UNVERIFIED"

def log_decision(rec: dict):
    rec["canary"] = CANARY
    with open(DECISIONS, "a") as f:
        f.write(json.dumps(rec) + "\n")

def run_task(task: str) -> dict:
    th = task_hash(task)
    conn = db()
    row = conn.execute("SELECT route, solution, verdict FROM pathways WHERE task_hash=?",
                       (th,)).fetchone()
    t0 = time.time()
    if row and row[2] == "GREEN":
        rec = {"event": "CACHE_HIT", "task": task, "task_hash": th,
               "route": row[0], "solution_chars": len(row[1]),
               "elapsed_ms": int((time.time() - t0) * 1000), "compute": 0}
        log_decision(rec)
        print(f"[cache][HIT] zero-compute replay | route={row[0]} | {rec['elapsed_ms']}ms | {task[:60]}")
        conn.close()
        return rec
    route = decide_route(task)
    solution = author_solution(task, task)
    verdict = grade_solution(solution)
    conn.execute("INSERT OR REPLACE INTO pathways VALUES (?,?,?,?,?,?)",
                 (th, norm(task), route, solution, verdict,
                  time.strftime("%Y-%m-%dT%H:%M:%S")))
    conn.commit(); conn.close()
    rec = {"event": "CACHE_MISS", "task": task, "task_hash": th, "route": route,
           "verdict": verdict, "solution_chars": len(solution),
           "elapsed_ms": int((time.time() - t0) * 1000), "compute": 1}
    log_decision(rec)
    print(f"[cache][MISS->banked] route={route} verdict={verdict} | {task[:60]}")
    return rec

def main():
    if len(sys.argv) < 2:
        sys.exit("usage: run|battery|stats ['task']")
    mode = sys.argv[1]
    if mode == "run":
        task = " ".join(sys.argv[2:]) or sys.exit("no task given")
        run_task(task)
    elif mode == "battery":
        hits = misses = 0
        for t in COMMON_TASKS:
            r = run_task(t)
            hits += (r["event"] == "CACHE_HIT")
            misses += (r["event"] == "CACHE_MISS")
        print(f"[battery] canary={CANARY} tasks={len(COMMON_TASKS)} hits={hits} misses={misses}")
    elif mode == "stats":
        conn = db()
        n = conn.execute("SELECT COUNT(*), SUM(compute_j) FROM (SELECT 1 AS compute_j, verdict FROM pathways WHERE verdict='GREEN')").fetchone()
        print(f"[stats] green_pathways={n[0]} total_rows={conn.execute('SELECT COUNT(*) FROM pathways').fetchone()[0]}")
        conn.close()

if __name__ == "__main__":
    main()
