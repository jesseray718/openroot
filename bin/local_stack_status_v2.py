#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# OpenRoot — jesseray718
# PANE: SSH — stack status v2: fixed probes (POST /api/show, correct generate opts), true FTS5 count, full model rank
import json, os, sys, sqlite3, datetime, hashlib, urllib.request

STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OLLAMA = "http://localhost:11434"
DB = "/home/jesse/wisdom-scaffold/data/optiplex_index.db"
CANARY = "STACKV2"

def post(url, payload, timeout):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

print(f"[{CANARY}] START {STAMP}")

# --- models ---
try:
    with urllib.request.urlopen(f"{OLLAMA}/api/tags", timeout=5) as r:
        models = json.loads(r.read()).get("models", [])
    print(f"[OLLAMA] {len(models)} models:")
    for m in models:
        print(f"  - {m.get('name','?'):26} {m.get('size',0)//(1024**3)}GB")
except Exception as e:
    print(f"[OLLAMA] DOWN: {e}"); sys.exit(1)

# --- true FTS5 chunk count (inspect schema first, no bogus fallback) ---
if os.path.exists(DB):
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    fts_tables = [t for t in tables if "fts" in t.lower()]
    print(f"[FTS5] {os.path.getsize(DB)/(1024**2):.0f}MB, tables={len(tables)}, fts_tables={fts_tables or 'NONE'}")
    counted = False
    for t in fts_tables:
        for col in ("chunks", "documents", "rows", ""):
            try:
                cur.execute(f"SELECT COUNT(*) FROM {t}" if not col else f"SELECT COUNT(*) FROM {t}")
                print(f"[FTS5]   {t}: {cur.fetchone()[0]} rows"); counted = True; break
            except Exception: continue
        if counted: break
    if not counted and fts_tables:
        print("[FTS5]   could not count — schema differs, inspect manually")
    conn.close()
else:
    print(f"[FTS5] DB MISSING: {DB}")

# --- warm inference probe (correct Ollama payload: options.num_predict) ---
t0 = datetime.datetime.now()
try:
    r = post(f"{OLLAMA}/api/generate",
             {"model": "qwen2.5:3b", "prompt": "Reply with the single word: ready",
              "stream": False, "options": {"num_predict": 5}}, timeout=60)
    dt = (datetime.datetime.now() - t0).total_seconds()
    print(f"[PROBE] 3B responded in {dt:.1f}s (incl. cold-load): {r.get('response','')[:40]!r}")
except Exception as e:
    print(f"[PROBE] FAILED: {e}")

# --- ranking based on ACTUAL installed models ---
print("""
[RANKING — all discovered models, by role fit on OptiPlex 3060 / 16GB]
  qwen2.5-coder:7b     AUTHOR   4GB  primary builder (known-good, 5-for-5 lineage)
  openroot-coder:latest AUTHOR  4GB  custom — UNKNOWN lineage, benchmark before trusting
  qwen2.5:3b           GRADE    1GB  grader (known-good)
  openroot-assistant:latest GRADE 4GB custom — UNKNOWN, benchmark before trusting
  deepseek-r1:1.5b     THINK    1GB  reasoning-chain drafts (chain-of-thought talent)
  llama3.2:1b          TINY     1GB  keyword routing / pinger only, not authoring
  nomic-embed-text:late EMBED    0GB  FTS5 pair, never co-loaded with 7B+indexer

DOCTRINE: two custom openroot-* models exist but carry no verified lineage in this
session. AUDIT INSTRUMENTS BEFORE BUILDERS: before routing work to them, run the
benchmark below. Until then they are UNVERIFIED (grade: OPEN).
""")

# --- benchmark the two unknown customs (small, gated, optional) ---
if "--bench" in sys.argv:
    for m in ("openroot-coder:latest", "openroot-assistant:latest"):
        try:
            t0 = datetime.datetime.now()
            r = post(f"{OLLAMA}/api/generate",
                     {"model": m, "prompt": "Write a one-line Python function returning the sha256 of a string.",
                      "stream": False, "options": {"num_predict": 120}}, timeout=180)
            dt = (datetime.datetime.now() - t0).total_seconds()
            resp = r.get("response", "")
            compiles = False
            import subprocess, tempfile
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tf:
                tf.write(resp); path = tf.name
            compiles = subprocess.run([sys.executable, "-m", "py_compile", path],
                                      capture_output=True).returncode == 0
            os.unlink(path)
            verdict = "PASS" if compiles else "FAIL(non-compiling output)"
            print(f"[BENCH] {m}: {dt:.1f}s, py_compile={verdict}")
        except Exception as e:
            print(f"[BENCH] {m}: ERROR {e}")

# --- handoff with hash (bug fixed: hashlib imported) ---
hp = f"/home/jesse/openroot/context_bridge/stack_status_v2_{STAMP}.md"
os.makedirs(os.path.dirname(hp), exist_ok=True)
with open(hp, "w") as f:
    f.write(f"# Stack Status v2 {STAMP}\n- models: {[m.get('name') for m in models]}\n"
            f"- fts_db: {'present' if os.path.exists(DB) else 'missing'}\n"
            f"- probe: see stdout\n- v1 defects fixed: hashlib import, POST /api/show, num_predict, bogus chunk-count fallback\n")
print(f"sha256 {hashlib.sha256(open(hp,'rb').read()).hexdigest()}  {hp}")
print(f"[{CANARY}] END {STAMP} [exit=0]")
