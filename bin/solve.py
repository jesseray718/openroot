#!/usr/bin/env python3
"""
solve.py v2 - Cache-first task router (OpenRoot superlinear engine)
CANARY: SOLVE_V3_20260924

v2 upgrades over v1:
  - verify <key-prefix>: human-gated graduation proposed -> verified (CONFIRM=1)
  - semantic cache: nomic-embed cosine over cache tasks + lesson texts (paraphrase-safe)
  - grounding injection: data/grounding.md prepended to all builds (anti-hallucination)

Doctrine: proposals default UNVERIFIED. Writes only with CONFIRM=1.
Human is the only commit gate. This script never commits or pushes.

Usage:
  python3 bin/solve.py <task text>              # exact -> semantic -> route
  python3 bin/solve.py lessons                   # list lesson chain
  python3 bin/solve.py cache                     # list cache entries
  python3 bin/solve.py verify <key-prefix>       # propose graduation (CONFIRM=1 to apply)
  CONFIRM=1 python3 bin/solve.py ...             # allow ledger writes
"""
import sys, os, json, hashlib, subprocess, time, math
from pathlib import Path
from datetime import datetime

BASE = Path("/home/jesse/openroot")
CACHE = BASE / "data" / "solve_cache.jsonl"
LESSONS = BASE / "data" / "lessons.jsonl"
GROUNDING = BASE / "data" / "grounding.md"
OLLAMA = "http://localhost:11434/api/generate"
EMBED_URL = "http://localhost:11434/api/embeddings"
SEM_THRESHOLD = float(os.environ.get("SEM_THRESHOLD", "0.78"))
CONFIRM = os.environ.get("CONFIRM") == "1"

def sha(s): return hashlib.sha256(s.encode()).hexdigest()[:16]
def task_key(task): return sha(" ".join(task.lower().split()))
def now(): return datetime.now().isoformat()

def git_head():
    try:
        return subprocess.run(["git", "-C", str(BASE), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        return "unknown"

def load_jsonl(path):
    if not path.exists(): return []
    out = []
    for line in path.read_text().splitlines():
        try: out.append(json.loads(line))
        except json.JSONDecodeError: continue
    return out

def save_jsonl(path, records):
    with path.open("w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

# ---------- embeddings (pillar: semantic retrieval) ----------
def embed(text):
    """EMBEDCACHEV1: persistent vector cache — cache hits cost zero Ollama calls."""
    import sys as _sys, os as _os
    _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
    from embed_cache import embed_cached
    return embed_cached([text])[0]

def cosine(v1, v2):
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = math.sqrt(sum(a * a for a in v1)); n2 = math.sqrt(sum(b * b for b in v2))
    return dot / (n1 * n2) if n1 and n2 else 0.0

# ---------- pillar 1: cached pathways (exact + semantic) ----------
def cache_lookup(task):
    key = task_key(task)
    for rec in load_jsonl(CACHE):
        if rec.get("key") == key:
            return rec, "exact"
    return None, None

def semantic_lookup(task):
    """Paraphrase-resistant: cosine match over cache tasks and lesson problems+root_causes."""
    q = embed(task)
    if not q:
        return None, None, 0.0
    best, best_kind, best_sim = None, None, 0.0
    for rec in load_jsonl(CACHE):
        if "task" not in rec: continue
        v = embed(rec["task"])
        if v:
            s = cosine(q, v)
            if s > best_sim: best, best_kind, best_sim = rec, "cache", s
    for l in load_jsonl(LESSONS):
        if l.get("status") == "superseded": continue
        text = l.get("problem", "") + " " + l.get("solution", "")
        v = embed(text)
        if v:
            s = cosine(q, v)
            if s > best_sim: best, best_kind, best_sim = l, "lesson", s
    return best, best_kind, best_sim

def cache_store(task, result, provider, status="proposed"):
    if not CONFIRM:
        print(f"[held] cache write suppressed (CONFIRM=1 to record, key={task_key(task)})")
        return None
    rec = {"key": task_key(task), "task": task[:200], "result": result[:2000],
           "provider": provider, "status": status,
           "provenance": {"commit": git_head(), "ts": now()}, "ts": now()}
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    with CACHE.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"[banked] cache {rec['key']} ({status})")
    return rec["key"]

# ---------- pillar 2: lesson chain ----------
LESSON_FIELDS = ["lesson_id", "created_at", "status", "domain", "problem",
                 "root_cause", "solution", "verification", "evidence", "safety_notes"]

def lesson_valid(rec):
    missing = [f for f in LESSON_FIELDS if f not in rec]
    if missing: return False, f"missing fields: {missing}"
    if rec["status"] not in ("draft", "verified", "superseded"): return False, f"bad status: {rec['status']}"
    if not rec["lesson_id"].startswith("LRN-"): return False, "lesson_id must start LRN-"
    return True, ""

def lesson_add(path):
    rec = json.loads(Path(path).read_text())
    ok, err = lesson_valid(rec)
    if not ok: print(f"[held] INVALID: {err}"); return 1
    if any(l["lesson_id"] == rec["lesson_id"] for l in load_jsonl(LESSONS)):
        print(f"[held] duplicate lesson_id {rec['lesson_id']}"); return 1
    if not CONFIRM:
        print(f"[held] lesson validated but NOT ingested: {rec['lesson_id']} (CONFIRM=1 to record)"); return 0
    with LESSONS.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"[banked] lesson {rec['lesson_id']} appended"); return 0

def seed_two_lessons():
    existing = {l["lesson_id"] for l in load_jsonl(LESSONS)}
    seeds = [
        {"lesson_id": "LRN-20260924-json-shell-quoting", "created_at": "2026-09-24T05:40:00",
         "status": "draft", "domain": "python",
         "problem": "JSON round-trip failed: double quotes stripped when payload passed through echo | pipe | $(cat)",
         "root_cause": "Nested shell parsing plus shell=True treated JSON data as shell syntax",
         "solution": "json.dumps then subprocess.run argument list; no shell=True, no echo, no pipe, no $(cat)",
         "verification": "Round-trip preserves embedded double quotes; witness hash 586dd81cd5d8d71a (commit 34b3e046)",
         "evidence": [{"type": "git_commit", "reference": "34b3e046"},
                      {"type": "test", "reference": "test_workflow key, shared_context.db"}],
         "safety_notes": "Applies wherever structured data crosses a shell boundary"},
        {"lesson_id": "LRN-20260924-marker-paste-artifacts", "created_at": "2026-09-24T05:40:00",
         "status": "draft", "domain": "shell",
         "problem": "Pasting [exit=0] markers and pager text into Bash created artifact files (0,, 1,, etc)",
         "root_cause": "Status-display metadata mistaken for terminal input",
         "solution": "Markers emitted inside script stdout only; never paste prompt markers/pager text/commentary",
         "verification": "Artifacts removed in 34b3e046; verify_openroot.sh passes clean",
         "evidence": [{"type": "git_commit", "reference": "34b3e046"}],
         "safety_notes": "Operator rule, permanent"},
    ]
    for s in seeds:
        if s["lesson_id"] in existing: continue
        if not CONFIRM:
            print(f"[held] seed lesson {s['lesson_id']} validated (CONFIRM=1 to ingest)"); continue
        with LESSONS.open("a") as f:
            f.write(json.dumps(s) + "\n")
        print(f"[banked] seeded lesson {s['lesson_id']}")

# ---------- pillar 3: grounded bounded routing ----------
def ollama_call(model, prompt, max_tokens=600):
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False,
                          "options": {"num_predict": max_tokens}})
    r = subprocess.run(["curl", "-s", "-X", "POST", OLLAMA,
                        "-H", "Content-Type: application/json", "-d", payload],
                       capture_output=True, text=True, timeout=300)
    try:
        return json.loads(r.stdout).get("response", "[no response]")
    except Exception:
        return f"[error: {r.stdout[:100]}]"

def grounding_text():
    if GROUNDING.exists():
        return GROUNDING.read_text()
    return ""

def retrieve_context(task, limit=4):
    """FTS5 retrieval over knowledge corpus (docs_ingest.py). Returns context text."""
    import sqlite3
    db = BASE / "data" / "knowledge.db"
    if not db.exists():
        return ""
    try:
        conn = sqlite3.connect(db)
        words = [w for w in task.lower().split() if len(w) > 3][:8]
        q = " OR ".join(words)
        rows = conn.execute(
            "SELECT d.source, d.title, snippet(docs_fts, 1, '[', ']', '...', 16) "
            "FROM docs_fts JOIN docs d ON d.id = docs_fts.rowid "
            "WHERE docs_fts MATCH ? ORDER BY rank LIMIT ?", (q, limit)).fetchall()
        conn.close()
        if not rows:
            return ""
        return "\n".join(f"- [{src}] {title}: {snip}" for src, title, snip in rows)
    except Exception:
        return ""

def route(task):
    # tier 0: exact
    hit, kind = cache_lookup(task)
    if hit:
        print(f"[EXACT HIT] key={hit['key']} status={hit['status']} provider={hit['provider']}")
        print(f"  prior result: {hit['result'][:300]}")
        print("  -> VERIFIED: reuse (no recompute)" if hit["status"] == "verified"
              else "  -> PROPOSED: run 'verify' to graduate after review")
        return 0
    # tier 1: semantic
    best, best_kind, sim = semantic_lookup(task)
    if best and sim >= SEM_THRESHOLD:
        print(f"[SEMANTIC HIT] {best_kind} cos={sim:.3f} (threshold {SEM_THRESHOLD})")
        if best_kind == "cache":
            print(f"  task: {best['task'][:100]}")
            print(f"  prior result: {best['result'][:300]}")
            print("  -> reuse if applicable, or re-run with adjusted wording")
        else:
            print(f"  lesson: {best['lesson_id']} [{best['status']}]")
            print(f"  problem: {best['problem'][:120]}")
            print(f"  solution: {best['solution'][:200]}")
            print("  -> lesson applies to this task; adapt, do not recompute blindly")
        return 0
    # tier 2: grounded build
    print("[MISS] routing: 7B build (grounded) -> 3B grade")
    g = grounding_text()
    ctx = retrieve_context(task)
    build_prompt = (f"Use ONLY the following grounding facts and retrieved context plus the task. "
                    f"Do NOT invent projects, employers, skills, or links not present here.\n\n"
                    f"--- GROUNDING ---\n{g}\n--- END GROUNDING ---\n\n"
                    f"--- RETRIEVED CONTEXT (prior project records) ---\n{ctx}\n--- END CONTEXT ---\n\n"
                    f"TASK: {task}")
    t0 = time.time()
    draft = ollama_call("qwen2.5-coder:7b", build_prompt)
    t1 = time.time()
    print(f"\n--- DRAFT (7B, {t1-t0:.0f}s) ---\n{draft[:1500]}\n")
    import sys as _sg, os as _og
    _sg.path.insert(0, _og.path.dirname(_og.path.abspath(__file__)))
    from grade_guard import grade_guarded
    grade_verdict, grade = grade_guarded(
        lambda p: ollama_call("qwen2.5:3b", p, 250), task, draft)
    if grade_verdict == "ERROR":
        print("[held] grader contract failed — draft NOT proposed, escalate")
        return
    print(f"--- GRADE (3B, {time.time()-t1:.0f}s) ---\nverdict={grade_verdict}\n{grade[:600]}\n")
    cache_store(task, f"DRAFT:\n{draft}\n\nGRADE:\n{grade}", "7B+3B-grounded", "proposed")
    print("[held] PROPOSED — review, then: CONFIRM=1 python3 bin/solve.py verify "
          f"<{task_key(task)[:8]}>")
    return 0

def verify_cmd(prefix):
    recs = load_jsonl(CACHE)
    matches = [r for r in recs if r["key"].startswith(prefix)]
    if not matches:
        print(f"[held] no cache entry with key prefix {prefix!r}")
        return 1
    if len(matches) > 1:
        print(f"[held] ambiguous prefix {prefix!r}: {[m['key'] for m in matches]}")
        return 1
    rec = matches[0]
    print(f"target: {rec['key']} status={rec['status']} provider={rec.get('provider')}")
    print(f"result: {rec['result'][:400]}")
    if not CONFIRM:
        print("[held] graduation proposed — review above, then re-run with CONFIRM=1")
        return 0
    rec["status"] = "verified"
    rec["verified_by"] = "human"; rec["verified_at"] = now()
    save_jsonl(CACHE, recs)
    print(f"[banked] {rec['key']} -> VERIFIED (future identical tasks skip models)")
    return 0

def main():
    if len(sys.argv) < 2:
        print(__doc__); return 1
    cmd = sys.argv[1]
    if cmd == "lessons":
        for l in load_jsonl(LESSONS):
            print(f"{l['lesson_id']} [{l['status']}] {l['problem'][:70]}")
        return 0
    if cmd == "cache":
        for r in load_jsonl(CACHE):
            print(f"{r['key']} [{r['status']}] {r.get('task', '')[:60]}")
        return 0
    if cmd == "lesson-add" and len(sys.argv) >= 3:
        return lesson_add(sys.argv[2])
    if cmd == "seed":
        seed_two_lessons(); return 0
    if cmd == "verify" and len(sys.argv) >= 3:
        return verify_cmd(sys.argv[2])
    task = " ".join(sys.argv[1:])
    return route(task)

if __name__ == "__main__":
    sys.exit(main())
