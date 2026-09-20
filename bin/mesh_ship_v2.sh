#!/usr/bin/env bash
# mesh_ship_v2.sh — retry loop + visible drafts + full ship on PASS
# Prints every draft to terminal (chat-visible). On PASS (or exhaust): finalize draft
# as MASTER_TODO.md. CONFIRM=1 → commit+push with provenance message. Human gate = env var.
set -eu
export GIT_PAGER=cat
REPO=/home/jesse/openroot
TS=$(date +%Y%m%d_%H%M%S)
DB=$REPO/data/mesh_refine_v1.db
LLM=http://localhost:11434/api/generate
MAX_ROUNDS=2
CANARY="[canary] paste intact marker"
grep -qF "$CANARY" "$0" || { echo "[held] canary missing — abort"; echo "[exit=0]"; exit 0; }

tag () { echo "[$1] $2" | tee -a "$REPO/context_bridge/seed_master-$TS.log"; }
tag gate "mesh_ship_v2 · db=$DB · CONFIRM=${CONFIRM:-0} · ts=$TS"

python3 - "$REPO" "$DB" "$TS" "$LLM" "$MAX_ROUNDS" <<'PYEOF'
import json, re, sqlite3, sys, urllib.request, hashlib, glob, os, subprocess
repo, db, ts, llm, max_rounds = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
con = sqlite3.connect(db)

def call(model, prompt, expect_json=False):
    body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                       "format": "json" if expect_json else None,
                       "options": {"temperature": 0.15, "num_predict": 768}}).encode()
    req = urllib.request.Request(llm, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())["response"]

def show(title, text):
    print(f"\n========== {title} ==========")
    print(text)
    print("=" * (12 + len(title)) + "\n")

# Load latest prior draft (HOLD'd run)
prior = sorted(glob.glob(f"{repo}/context_bridge/MASTER_TODO.meshdraft.*.md"))[-1]
draft = open(prior).read()
show(f"PRIOR DRAFT ({os.path.basename(prior)})", draft)
reasons = "dedupe items across sections; group under correct headings"

best, best_verdict = draft, "HOLD"
for rnd in range(1, max_rounds + 1):
    print(f"[gate] retry round {rnd}/{max_rounds} — feedback: {reasons}")
    draft = call("qwen2.5-coder:7b",
        f"Revise this MASTER_TODO draft. FEEDBACK: {reasons}\n"
        f"Requirements: (1) no duplicates, (2) each item under exactly one heading: "
        f"Infrastructure / Documentation / Community / Physics-Hardware, "
        f"(3) every item actionable, (4) preserve original wording, invent nothing.\n\n"
        f"DRAFT:\n{draft}")
    show(f"REVISED DRAFT — round {rnd}", draft)
    try:
        v = json.loads(call("qwen2.5:3b",
            "Rubric: (1) actionable items, (2) no duplicates, (3) correct single grouping, "
            "(4) nothing invented. " 'Reply JSON: {"verdict":"PASS"|"HOLD","reasons":["..."]}'
            "\n\nDraft:\n" + draft, expect_json=True))
        verdict = v.get("verdict", "HOLD")
        r = v.get("reasons", [])
        reasons = "; ".join(r) if isinstance(r, list) else str(r)
    except Exception as e:
        verdict, reasons = "HOLD", f"grader unparsable ({e})"
    sha16 = hashlib.sha256(draft.encode()).hexdigest()[:16]
    con.execute("INSERT INTO iters(stage, model, verdict, sha16) VALUES (?,?,?,?)",
                (f"ship_round{rnd}", "7B-revise/3B-grade", verdict, sha16))
    con.commit()
    print(f"[{'banked' if verdict=='PASS' else 'held'}] round {rnd}: {verdict} — {reasons}")
    best, best_verdict = draft, verdict
    if verdict == "PASS":
        break

final = f"{repo}/MASTER_TODO.md"
header = (f"# MASTER_TODO\n"
          f"# rebuilt from context_bridge remnants · 7B-authored · 3B-graded "
          f"({best_verdict}) · {ts} · sha16:{hashlib.sha256(best.encode()).hexdigest()[:16]}\n\n")
open(final, "w").write(header + best.replace("# MASTER_TODO.md mesh rebuild draft", "").strip() + "\n")
show("FINAL PRODUCT — MASTER_TODO.md", open(final).read())
print(f"[banked] written: {final}")

if os.environ.get("CONFIRM", "0") == "1":
    subprocess.run(["git", "-C", repo, "add", "MASTER_TODO.md"], check=True)
    subprocess.run(["git", "-C", repo, "commit", "-m",
        f"MASTER_TODO.md rebuild: FTS5 recall + 7B-authored + 3B-graded ({best_verdict}) "
        f"from context_bridge remnants (recovery of lost todo-automation-v2 content)"], check=True)
    subprocess.run(["git", "-C", repo, "push", "origin", "main"], check=True)
    head = subprocess.run(["git", "-C", repo, "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    print(f"[banked] COMMITTED + PUSHED: {head}")
else:
    print("[held] DRY-RUN: CONFIRM=1 to commit+push MASTER_TODO.md")
    st = subprocess.run(["git", "-C", repo, "diff", "--stat"], capture_output=True, text=True).stdout
    print(st if st.strip() else "(unstaged — file is new/untracked)")
print("[exit=0]")
PYEOF
tag banked "mesh_ship_v2 complete → seed_master-$TS.log"
echo "[exit=0]"
