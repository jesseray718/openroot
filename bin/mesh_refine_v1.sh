#!/usr/bin/env bash
# mesh_refine_v1.sh — FTS5 retrieval → 7B drafts → 3B grades → sealed drafts
# Specialty routing: SQLite/FTS5 (recall), qwen2.5-coder:7b (synthesis),
#                    qwen2.5:3b (rubric grading). Local models only.
# Canopy rule: each model gets chunks sized to its attention budget.
# Drafts are UNCOMMITTED — human is the only commit gate.
set -eu
export GIT_PAGER=cat
REPO=/home/jesse/openroot
TS=$(date +%Y%m%d_%H%M%S)
DB=$REPO/data/mesh_refine_v1.db
LLM=http://localhost:11434/api/generate
CANARY="[canary] paste intact marker"
grep -qF "$CANARY" "$0" || { echo "[held] canary missing — abort"; echo "[exit=0]"; exit 0; }
curl -sf --max-time 5 http://localhost:11434/api/tags >/dev/null \
  || { echo "[held] ollama down at :11434 — start it and rerun"; echo "[exit=0]"; exit 0; }
mkdir -p "$REPO/data" "$REPO/context_bridge"

tag () { echo "[$1] $2" | tee -a "$REPO/context_bridge/seed_master-$TS.log"; }

tag gate "ollama UP · db=$DB · ts=$TS"

# ---------- [stage:index] FTS5 — recall specialist ----------
python3 - "$REPO" "$DB" <<'PYEOF'
import os, re, sqlite3, sys, glob, hashlib
repo, db = sys.argv[1], sys.argv[2]
con = sqlite3.connect(db)
con.executescript("""
DROP TABLE IF EXISTS docs; DROP TABLE IF EXISTS iters;
CREATE VIRTUAL TABLE docs USING fts5(path, chunk_id, body);
CREATE TABLE iters(id INTEGER PRIMARY KEY, stage TEXT, model TEXT,
                  verdict TEXT, sha16 TEXT, ts DATETIME DEFAULT CURRENT_TIMESTAMP);
""")
CHUNK = 1500
seen = 0
sources = (glob.glob(f"{repo}/context_bridge/session-*.md") +
           glob.glob(f"{repo}/*.md") + glob.glob(f"{repo}/data/*.md"))
for path in sources:
    text = open(path, errors="replace").read()
    for i in range(0, len(text), CHUNK):
        con.execute("INSERT INTO docs VALUES (?,?,?)",
                     (path, i // CHUNK, text[i:i + CHUNK]))
        seen += 1
con.commit()
print(f"[gate] indexed {len(sources)} file(s) → {seen} chunks into FTS5")
PYEOF

# ---------- [stage:retrieve+draft] FTS5 recall → 7B synthesis, per-chunk ----------
python3 - "$REPO" "$DB" "$TS" "$LLM" <<'PYEOF'
import json, re, sqlite3, sys, urllib.request, hashlib, datetime
repo, db, ts, llm = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
con = sqlite3.connect(db)

def call(model, prompt, expect_json=False):
    body = json.dumps({"model": model, "prompt": prompt,
                       "stream": False,
                       "format": "json" if expect_json else None,
                       "options": {"temperature": 0.2, "num_predict": 512}}).encode()
    req = urllib.request.Request(llm, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())["response"]

# FTS5 specialty: recall candidate task-bearing chunks
rows = con.execute("""
    SELECT path, chunk_id, snippet(docs, 2, '', '', ' … ', 24)
    FROM docs WHERE docs MATCH 'goal OR todo OR queue OR priority OR "next action"'
    ORDER BY rank LIMIT 12
""").fetchall()
print(f"[gate] FTS5 recalled {len(rows)} candidate chunk(s)")

# 7B specialty: per-chunk extraction (small context = high fidelity, 5-for-5 precedent)
harvest = set()
for path, cid, snip in rows:
    p = (f"The following is a fragment of a project recovery session from {path}.\n"
         f"Fragment: {snip}\n\n"
         "Extract ONLY concrete actionable task/goal statements as a JSON array of strings. "
         "If none, return []. No commentary.")
    try:
        arr = json.loads(call("qwen2.5-coder:7b", p, expect_json=True))
        for t in arr:
            if isinstance(t, str) and 4 < len(t) < 200:
                harvest.add(t.strip())
    except Exception as e:
        print(f"[held] chunk {cid}@{path} skipped ({e})")
print(f"[gate] 7B harvested {len(harvest)} unique task statement(s)")

# 7B specialty: merge into structured draft
draft = call("qwen2.5-coder:7b",
    "Merge and deduplicate these recovered task statements into a numbered master TODO, "
    "grouped under headings: Infrastructure, Documentation, Community, Physics/Hardware. "
    "Preserve original wording where possible.\n\nStatements:\n" +
    "\n".join(f"- {t}" for t in sorted(harvest)))

# 3B specialty: cheap strict rubric grade (fast verdict, no drafting)
grade = call("qwen2.5:3b",
    "Grade this draft TODO document against the rubric. Rubric: (1) every item is actionable, "
    "(2) no duplicated items, (3) grouped logically, (4) nothing invented beyond the statements. "
    'Reply as JSON: {"verdict": "PASS" or "HOLD", "reasons": ["..."]}\n\nDraft:\n' + draft,
    expect_json=True)
try:
    v = json.loads(grade); verdict, reasons = v.get("verdict", "HOLD"), "; ".join(v.get("reasons", []))
except Exception:
    verdict, reasons = "HOLD", "grader output unparsable"

sha16 = hashlib.sha256(draft.encode()).hexdigest()[:16]
con.execute("INSERT INTO iters(stage, model, verdict, sha16) VALUES (?,?,?,?)",
            ("draft+grade", "7B-draft/3B-grade", verdict, sha16))
con.commit()

out = f"{repo}/context_bridge/MASTER_TODO.meshdraft.{ts}.md"
open(out, "w").write(
    f"# MASTER_TODO.md mesh rebuild draft\n"
    f"# 7B drafted · 3B graded · verdict={verdict} · sha16:{sha16}\n"
    f"# sources: {len(rows)} chunks · {len(harvest)} statements\n\n{draft}\n")
print(f"[{'banked' if verdict=='PASS' else 'held'}] verdict={verdict} ({reasons})")
print(f"[held] draft uncommitted, human gate: {out}")
print(f"[gate] {sha16} logged to iters table")
PYEOF

echo "$(sha256sum "$REPO/context_bridge/MASTER_TODO.meshdraft.$TS.md" 2>/dev/null | cut -c1-16) meshdraft $TS" \
  >> "$REPO/seed_master.log"
tag banked "sealed → context_bridge/MASTER_TODO.meshdraft.$TS.md + seed_master-$TS.log"
echo "[exit=0]"
