#!/usr/bin/env bash
# CANARY:OPENROOT-HARVEST-V2 (CORPUS-GROUNDED)
# Fetch estate context via FTS5+embedding, prepend to seed, then call 7B
set -eu; export GIT_PAGER=cat TERM=dumb

INBOX=/home/${OPENROOT_USER}/openroot/context_bridge/lumo_inbox
HARVEST=/home/${OPENROOT_USER}/openroot/context_bridge/harvest
RECEIPTS=/home/${OPENROOT_USER}/openroot/data/harvest_receipts.jsonl
DB=/home/${OPENROOT_USER}/openroot/data/corpus_goal_index.db  # or your FTS5 ledger DB
MODEL="${AGENT_MODEL:-openroot-instruct:7b}"

mkdir -p "$INBOX" "$HARVEST"

# [gate] ollama + model
curl -s --max-time 5 http://localhost:11434/api/tags | grep -q "\"${MODEL%%:*}\" || {
  echo "[held] ollama/model missing"; exit 1; }

processed_hashes() { grep -o '"seed_sha256": *"[a-f0-9]*"' "$RECEIPTS" 2>/dev/null \
  | tr -d '"' | awk '{print $2}' || true; }

for f in "$INBOX"/*.md; do
  [ -e "$f" ] || { echo "[held] inbox empty"; break; }
  h=$(sha256sum "$f" | awk '{print $1}')
  if printf '%s\n' "$(processed_hashes)" | grep -qx "$h"; then
    echo "[cached] $h already banked"; continue; fi

  # [stage 1] retrieve estate context via FTS5/embedding
  ctx=$(python3 - "$f" "$DB" <<'PYEOF'
import sqlite3, sys, json, os
seed = open(sys.argv[1]).read()
dbpath = sys.argv[2]
conn = sqlite3.connect(dbpath)
# FTS5 search for keywords in seed
terms = [t.lower().strip('.,!?:') for t in seed.split() if len(t)>3][:20]
query = 'SELECT path, snippet, score FROM content_idx WHERE content MATCH ? ORDER BY score DESC LIMIT 5'
matches = []
for t in terms[:5]:
    try:
        for r in conn.execute(query, (t,)).fetchall():
            matches.append({'path':r[0], 'snippet':r[1][:150]})
    except: continue
# dedup by path, return top 3
seen=set(); uniq=[]
for m in matches:
    if m['path'] not in seen: seen.add(m['path']); uniq.append(m)
    if len(uniq)>=3: break
conn.close()
print(json.dumps(uniq))
PYEOF
)

  # [stage 2] build grounded prompt
  seed_txt=$(cat "$f")
  prompt=$(python3 - <<'PYEOF'
import json, sys
ctx_json = '''%s''' % '''%s''' % (repr('''%s'''%"""$(printf '%s' "$ctx")"""), "")
ctx = json.loads(ctx_json) if ctx_json.strip() else []
seed = """$seed_txt"""
sys_prompt = (
  "You are embedded in the OpenRoot estate. Your knowledge is limited to the "
  "following retrieved context from the estate ledger:\n\n" +
  "\n".join(f"[FILE] {m['path']}: {m['snippet']}..." for m in ctx[:3]) if ctx else "No estate context found.\n\n" +
  "SEED DOCUMENT TO PROCESS:\n" + seed +
  "\n\nTASK: Extract ONLY build-relevant actions from the seed. For each:\n"
  "1) What to build (concrete, not abstract)\n"
  "2) Which estate component it chains to (path to file/ledger/module)\n"
  "3) First verifiable step (script path, test command, receipt format)\n"
  "If seed contains enterprise boilerplate (Airflow, Tableau, cloud), discard it and say so."
)
print(json.dumps({"model": "placeholder", "stream": False, "options": {"num_ctx": 8192}, "prompt": sys_prompt}))
PYEOF
)

  # [stage 3] call local model
  resp=$(curl -s --max-time 600 http://localhost:11434/api/generate \
    -d "${prompt//placeholder/$MODEL}")
  out=$(printf '%s' "$resp" | python3 -c 'import json,sys; print(json.load(sys.stdin)["response"])')
  rh=$(printf '%s' "$out" | sha256sum | awk '{print $1}')
  ts=$(date -u +%Y%m%dT%H%M%SZ)

  printf '%s' "$out" > "$HARVEST/${ts}_$(basename "$f" .md)_${h:0:8}.md"
  printf '{"ts":"%s","seed":"%s","seed_sha256":"%s","model":"%s","resp_sha256":"%s","estate_ctx_match":%d}\n' \
    "$ts" "$(basename "$f")" "$h" "$MODEL" "$rh" "${#ctx}" >> "$RECEIPTS"

  echo "[banked] $(basename "$f") -> ${ts}_${h:0:8}.md (estate_ctx=%d)" "${#ctx}"
done
echo "[banked] harvest complete"
exit 0
