#!/usr/bin/env python3
"""
solve.py v1 - Cache-first task router (OpenRoot superlinear engine)
CANARY: SOLVE_V1_20260924

Three pillars:
  1. Cached pathways: task hash -> prior verified result (no recompute)
  2. Chain: lessons.jsonl append-only, human-gated graduation
  3. Routing: 7B builds / 3B grades, only on cache miss

Doctrine: proposals default UNVERIFIED. Writes only with CONFIRM=1.
Human is the only commit gate. This script never commits or pushes.

Usage:
  python3 bin/solve.py <task text>              # lookup + route (reads free)
  python3 bin/solve.py lessons                   # list lesson chain
  python3 bin/solve.py lesson-add <file.json>   # validate + propose ingest
  CONFIRM=1 python3 bin/solve.py ...            # allow ledger writes
"""
import sys, os, json, hashlib, subprocess, time
from pathlib import Path
from datetime import datetime

BASE = Path("/home/jesse/openroot")
CACHE = BASE / "data" / "solve_cache.jsonl"
LESSONS = BASE / "data" / "lessons.jsonl"
SCHEMA_DOC = BASE / "docs" / "LESSON_RECORD_SCHEMA.md"
OLLAMA = "http://localhost:11434/api/generate"
CONFIRM = os.environ.get("CONFIRM") == "1"

def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:16]

def task_key(task: str) -> str:
    """Normalized task fingerprint (strip whitespace variance)."""
    norm = " ".join(task.lower().split())
    return sha(norm)

# ---------- Pillar 1: cached pathways ----------
def cache_lookup(task: str):
    key = task_key(task)
    if CACHE.exists():
        for line in CACHE.read_text().splitlines():
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("key") == key:
                return rec
    return None

def cache_store(task, result, provider, status="proposed"):
    if not CONFIRM:
        print(f"[held] cache write suppressed (CONFIRM=1 to record, key={task_key(task)})")
        return None
    rec = {"key": task_key(task), "task": task[:200], "result": result[:2000],
           "provider": provider, "status": status,
           "provenance": {"commit": git_head(), "ts": datetime.now().isoformat()},
           "ts": datetime.now().isoformat()}
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    with CACHE.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"[banked] cache {rec['key']} ({status})")
    return rec["key"]

def git_head():
    try:
        return subprocess.run(["git", "-C", str(BASE), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        return "unknown"

# ---------- Pillar 2: lesson chain ----------
LESSON_FIELDS = ["lesson_id", "created_at", "status", "domain", "problem",
                 "root_cause", "solution", "verification", "evidence", "safety_notes"]

def ensure_schema_doc():
    if SCHEMA_DOC.exists():
        return
    SCHEMA_DOC.parent.mkdir(parents=True, exist_ok=True)
    SCHEMA_DOC.write_text("""# Lesson Record Schema v1
CANARY: LESSON_SCHEMA_V1_20260924

Records: `data/lessons.jsonl` (append-only, JSONL, one record per line)

Fields:
- lesson_id: "LRN-YYYYMMDD-short-slug" (unique)
- created_at: ISO-8601
- status: draft | verified | superseded  (graduation to verified is human-gated)
- domain: shell | python | git | networking | hardware | research
- problem: what failed
- root_cause: why it failed
- solution: what corrected it
- verification: exact check proving the correction
- evidence: list of {type, reference} (commit hash, command, file, test witness)
- safety_notes: conditions and boundaries

License: CC-BY-SA-4.0 (documentation commons)
""")
    print(f"[banked] {SCHEMA_DOC}")

def lesson_valid(rec) -> tuple[bool, str]:
    missing = [f for f in LESSON_FIELDS if f not in rec]
    if missing:
        return False, f"missing fields: {missing}"
    if rec["status"] not in ("draft", "verified", "superseded"):
        return False, f"bad status: {rec['status']}"
    if not rec["lesson_id"].startswith("LRN-"):
        return False, "lesson_id must start LRN-"
    return True, ""

def lessons_load():
    if not LESSONS.exists():
        return []
    out = []
    for line in LESSONS.read_text().splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out

def lesson_add(path: str):
    rec = json.loads(Path(path).read_text())
    ok, err = lesson_valid(rec)
    if not ok:
        print(f"[held] INVALID: {err}")
        return 1
    if any(l["lesson_id"] == rec["lesson_id"] for l in lessons_load()):
        print(f"[held] duplicate lesson_id {rec['lesson_id']}")
        return 1
    if not CONFIRM:
        print(f"[held] lesson validated but NOT ingested: {rec['lesson_id']} (CONFIRM=1 to record)")
        print(json.dumps(rec, indent=2))
        return 0
    LESSONS.parent.mkdir(parents=True, exist_ok=True)
    with LESSONS.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"[banked] lesson {rec['lesson_id']} appended (status={rec['status']})")
    return 0

def seed_two_lessons():
    """Auto-ingest the two witnessed lessons from 2026-09-24 session."""
    ensure_schema_doc()
    existing = {l["lesson_id"] for l in lessons_load()}
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
        if s["lesson_id"] in existing:
            continue
        if not CONFIRM:
            print(f"[held] seed lesson {s['lesson_id']} validated (CONFIRM=1 to ingest)")
            continue
        with LESSONS.open("a") as f:
            f.write(json.dumps(s) + "\n")
        print(f"[banked] seeded lesson {s['lesson_id']}")

# ---------- Pillar 3: bounded routing ----------
def ollama_call(model: str, prompt: str, max_tokens=600) -> str:
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False,
                          "options": {"num_predict": max_tokens}})
    r = subprocess.run(["curl", "-s", "-X", "POST", OLLAMA,
                        "-H", "Content-Type: application/json", "-d", payload],
                       capture_output=True, text=True, timeout=300)
    try:
        return json.loads(r.stdout).get("response", "[no response]")
    except Exception:
        return f"[error: {r.stdout[:100]}]"

def route(task: str):
    """Cache-first dispatch. Miss -> 7B builds, 3B grades, result proposed for review."""
    hit = cache_lookup(task)
    if hit:
        print(f"[CACHE HIT] key={hit['key']} status={hit['status']} provider={hit['provider']}")
        print(f"  prior result: {hit['result'][:300]}")
        print(f"  provenance: {hit.get('provenance', {})}")
        if hit["status"] == "verified":
            print("  -> VERIFIED: reuse recommended (no recompute)")
        else:
            print("  -> PROPOSED: validate before reuse or adapt")
        return 0
    print("[CACHE MISS] routing: 7B build -> 3B grade")
    t0 = time.time()
    draft = ollama_call("qwen2.5-coder:7b", task)
    t1 = time.time()
    print(f"\n--- DRAFT (7B, {t1-t0:.0f}s) ---\n{draft[:1500]}\n")
    grade_prompt = ("Rate 1-10 and justify in 3 sentences. Criteria: correctness, "
                    "completeness, falsifiability. Task was:\n" + task +
                    "\n\nSubmission:\n" + draft[:3000])
    grade = ollama_call("qwen2.5:3b", grade_prompt, 200)
    print(f"--- GRADE (3B, {time.time()-t1:.0f}s) ---\n{grade[:500]}\n")
    cache_store(task, f"DRAFT:\n{draft}\n\nGRADE:\n{grade}", "7B+3B", "proposed")
    print("[held] result is PROPOSED — human review required before it becomes verified")
    return 0

def main():
    if len(sys.argv) < 2:
        print(__doc__); return 1
    cmd = sys.argv[1]
    if cmd == "lessons":
        for l in lessons_load():
            print(f"{l['lesson_id']} [{l['status']}] {l['problem'][:70]}")
        return 0
    if cmd == "lesson-add" and len(sys.argv) >= 3:
        return lesson_add(sys.argv[2])
    if cmd == "seed":
        seed_two_lessons(); return 0
    task = " ".join(sys.argv[1:])
    ensure_schema_doc()
    return route(task)

if __name__ == "__main__":
    sys.exit(main())
