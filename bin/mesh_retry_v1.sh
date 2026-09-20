#!/usr/bin/env bash
# mesh_retry_v1.sh — auto-retry on HOLD verdict (max 2 rounds), fix-specific prompts
# Specialty routing: 7B revisions, 3B grading only. Each round addresses prior reasons.
set -eu
export GIT_PAPER=cat
REPO=/home/jesse/openroot
TS=$(date +%Y%m%d_%H%M%S)
DB=$REPO/data/mesh_refine_v1.db
LLM=http://localhost:11434/api/generate
MAX_ROUNDS=2
CANARY="[canary] paste intact marker"
grep -qF "$CANARY" "$0" || { echo "[held] canary missing — abort"; echo "[exit=0]"; exit 0; }

tag () { echo "[$1] $2" | tee -a "$REPO/context_bridge/seed_master-$TS.log"; }

tag gate "retry loop starting · db=$DB · max_rounds=$MAX_ROUNDS"

python3 - "$REPO" "$DB" "$TS" "$LLM" "$MAX_ROUNDS" <<'PYEOF'
import json, re, sqlite3, sys, urllib.request, hashlib, os, glob

repo, db, ts, llm, max_rounds = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
con = sqlite3.connect(db)

def call(model, prompt, expect_json=False):
    body = json.dumps({"model": model, "prompt": prompt,
                       "stream": False,
                       "format": "json" if expect_json else None,
                       "options": {"temperature": 0.15, "num_predict": 768}}).encode()
    req = urllib.request.Request(llm, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())["response"]

# Find latest draft + verdict
rows = con.execute(
    "SELECT stage, model, verdict, sha16 FROM iters ORDER BY id DESC LIMIT 1"
).fetchone()
if not rows or rows[2] != "HOLD":
    print(f"[gate] no HOLD verdict found (verdict={rows[2] if rows else 'NONE'}) — nothing to retry")
    print("[exit=0]")
    sys.exit(0)

print(f"[gate] FOUND HOLD verdict — initiating retry loop")

draft_path = None
for f in sorted(glob.glob(f"{repo}/context_bridge/MASTER_TODO.meshdraft.*.md"), reverse=True)[:1]:
    draft_path = f
if not draft_path:
    print("[held] draft not found — abort")
    print("[exit=0]")
    sys.exit(0)

draft = open(draft_path).read()
prev_verdict, prev_reasons = rows[2], "initial HOLD"

for round_i in range(max_rounds):
    print(f"[gate] retry round {round_i+1}/{max_rounds}")
    
    # 7B revision: address specific grader reasons
    reason_str = prev_reasons if round_i == 0 else "; ".join(json.loads(prev_reasons).get("reasons", ["logic issues"]))
    revised_draft = call("qwen2.5-coder:7b",
        f"Revise this MASTER_TODO draft addressing these grading feedback points:\n"
        f"FEEDBACK: {reason_str}\n\n"
        f"Requirements: (1) no duplicates across sections, (2) items grouped under correct headings: "
        f"Infrastructure, Documentation, Community, Physics/Hardware. Keep original wording where possible.\n\n"
        f"DRAFT TO REVISE:\n{draft}",
        expect_json=False)
    
    # 3B grading again
    try:
        grade = call("qwen2.5:3b",
            "Grade this MASTER_TODO draft against the rubric. Rubric: (1) every item is actionable, "
            "(2) NO DUPLICATES across sections, (3) grouped under correct headings (Infrastructure, "
            "Documentation, Community, Physics/Hardware), (4) nothing invented beyond original statements. "
            'Reply as JSON: {"verdict": "PASS" or "HOLD", "reasons": ["..."]}\n\nDraft:\n' + revised_draft,
            expect_json=True)
        v = json.loads(grade)
        verdict, reasons = v.get("verdict", "HOLD"), v.get("reasons", [])
        if isinstance(reasons, list):
            reasons = "; ".join(reasons)
    except Exception as e:
        verdict, reasons = "HOLD", f"grader output unparsable ({e})"
    
    sha16 = hashlib.sha256(revised_draft.encode()).hexdigest()[:16]
    con.execute(
        "INSERT INTO iters(stage, model, verdict, sha16) VALUES (?,?,?,?)",
        (f"revise+grade_round{round_i+1}", "7B-revise/3B-grade", verdict, sha16))
    con.commit()
    
    out = f"{repo}/context_bridge/MASTER_TODO.meshdraft.retry{round_i+1}.{ts}.md"
    open(out, "w").write(
        f"# MASTER_TODO.md mesh rebuild draft — retry {round_i+1}/{max_rounds}\n"
        f"# 7B revised · 3B graded · verdict={verdict} · sha16:{sha16}\n"
        f"# prior feedback: {reasons}\n\n{revised_draft}\n")
    
    print(f"[{'banked' if verdict=='PASS' else 'held'}] round {round_i+1}: verdict={verdict} ({reasons})")
    
    if verdict == "PASS":
        print(f"[banked] PASS achieved after round {round_i+1} — draft ready for human gate: {out}")
        print("[exit=0]")
        sys.exit(0)
    
    # Store for next round
    draft = revised_draft
    prev_verdict = verdict
    prev_reasons = json.dumps({"reasons": reasons.split("; ") if ";" in reasons else [reasons]})

# Exhausted rounds
print(f"[held] exhausted {max_rounds} rounds — still HOLD")
final_path = f"{repo}/context_bridge/MASTER_TODO.meshdraft.final.{ts}.md"
open(final_path, "w").write(draft)
print(f"[held] final draft uncommitted, human gate: {final_path}")
print("[exit=0]")
PYEOF

tag banked "retry loop complete → seed_master-$TS.log"
echo "[exit=0]"
