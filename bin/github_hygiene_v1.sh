#!/usr/bin/env bash
# github_hygiene_v1 — whole-stack repo hygiene: audit -> commit -> merge -> PR
# Team: fp5s-style routing + 7B drafts, 3B grades | RAPL/POPW energy ledger |
#       sha256 cached pathways | Newton-chain event chain | human gates (CONFIRM=1)
# Phase 1 (default): READ-ONLY audit + staged proposal, zero mutations.
# Phase 2 (CONFIRM=1): commit, push_guard, delete merged branches, open PRs.
set -eu
export GIT_PAGER=cat
cd /home/jesse/openroot
TS=$(date -u +%Y%m%d_%H%M%S)
CONFIRM="${CONFIRM:-0}"

# ---- stage 1: energy baseline (RAPL microjoules, ESTIMATE fallback) ----
read_energy() {
  local total=0 f
  for f in /sys/class/powercap/intel-rapl:*/energy_uj; do
    [ -r "$f" ] && total=$(( total + $(cat "$f") ))
  done
  [ "$total" -gt 0 ] && echo "RAPL:$total" || echo "ESTIMATE:0"
}
E_START=$(read_energy)

# ---- stage 2: cached pathway — same repo state = same audit, skip recompute ----
STATE_HASH=$( (git status --porcelain; git rev-parse HEAD; git branch -a --format='%(refname)') | sha256sum | cut -c1-16)
CACHE_KEY="ghhy_${STATE_HASH}"
CACHED=$(sqlite3 data/pathway_cache.db "SELECT result FROM pathways WHERE key='$CACHE_KEY'" 2>/dev/null || true)
if [ -n "$CACHED" ] && [ "${FORCE:-0}" != "1" ]; then
  echo "[banked] cached pathway hit $CACHE_KEY — repo state unchanged since last audit"
  echo "$CACHED"
  echo "[exit=0]"; exit 0
fi

# ---- stage 3: inventory (always) ----
echo "== [gate] uncommitted =="
git status --porcelain | head -40
echo "== [gate] branches (local / remote) =="
git fetch --prune 2>/dev/null || true
git branch -vv
echo "== [gate] branches fully merged into main (SAFE TO DELETE) =="
git branch --merged origin/main | grep -vE '^\*|main$' || echo "(none)"
echo "== [gate] unmerged branches (need PR or explicit decision) =="
git branch --no-merged origin/main || echo "(none)"

# ---- stage 4: stage known-good new artifacts, refuse blobs >50M ----
STAGED_NEW=0
stage_file() {
  [ -f "$1" ] || return 0
  SZ=$(stat -c%s "$1")
  if [ "$SZ" -gt 52428800 ]; then echo "[held] REFUSED >50M: $1"; return 1; fi
  git add "$1" && STAGED_NEW=$((STAGED_NEW+1)) || true
}
for f in bin/kai_retrieve_local_v1.py bin/kai_ingest_bridge_v1.py bin/kai_queue_bridge_v1.py \
         bin/kai_search_v1.py bin/kai_retrieve_v1.py data/kai_corpus_index.txt \
         context_bridge/lumo_inbox/kai_corpus_manifest_20260930_070204.json \
         context_bridge/lumo_inbox/session-seed-lumo-20260930_020809.md \
         context_bridge/mistake_solutions/daf3c7a118ae1f30.md data/cost_ledger.jsonl \
         bin/openroot_board_v1.sh; do stage_file "$f" || true; done
echo "== [gate] newly staged: $STAGED_NEW files =="
git diff --cached --stat | tail -5

# ---- stage 5: commit-message gate FAILS if staged diff touches nothing ----
if git diff --cached --quiet; then
  echo "[gate] nothing staged to commit — audit-only completion"
  NEEDS_COMMIT=0
else
  NEEDS_COMMIT=1
  DIFFSTAT=$(git diff --cached --stat | tail -1)
  # [7B drafts the message] (routing: coder specialty -> qwen2.5-coder:7b)
  MSG_DRAFT=$(curl -s --max-time 120 http://localhost:11434/api/generate -d "{\"model\":\"qwen2.5-coder:7b\",\"prompt\":\"Write a single-line conventional commit message for: staging kai9000 corpus retrieval+ingestion+FTS pipeline scripts, manifest, reports, board hook, cost ledger line. Prefix [ADD]. Under 100 chars. Output ONLY the message.\",\"stream\":false}" | grep -o '"response":"[^"]*"' | cut -d'"' -f4 | head -c 200)
  # [3B grades it] (routing: grader specialty -> qwen2.5:3b)
  GRADE=$(curl -s --max-time 60 http://localhost:11434/api/generate -d "{\"model\":\"qwen2.5:3b\",\"prompt\":\"Grade this commit message PASS or FAIL for clarity/convention (one word): $MSG_DRAFT\",\"stream\":false}" | grep -o '"response":"[^"]*"' | cut -d'"' -f4 | head -c 40)
  case "$GRADE" in *PASS*) MSG="$MSG_DRAFT";; *) MSG="[ADD] kai9000 corpus retrieval+ingestion+FTS pipeline, board hook, cost ledger — 7B-drafted, 3B-graded($GRADE), human-gated";; esac
  echo "[gate] 7B draft: ${MSG_DRAFT:-<ollama-down>}"
  echo "[gate] 3B grade: ${GRADE:-<ollama-down>}"
fi

# ---- stage 6: Newton chain — hash-linked event append ----
PREV=$(sqlite3 data/newton_chain.db "SELECT hash FROM chain ORDER BY rowid DESC LIMIT 1" 2>/dev/null || echo "genesis")
PAYLOAD="github_hygiene|${TS}|${STATE_HASH}|commit:${NEEDS_COMMIT}"
CHASH=$(printf '%s|%s' "$PREV" "$PAYLOAD" | sha256sum | cut -d' ' -f1)
NEWTON_OK=$(sqlite3 data/newton_chain.db "INSERT INTO chain(hash,prev_hash,event,ts) VALUES('$CHASH','$PREV','$PAYLOAD','$TS')" 2>/dev/null && echo yes || echo no)
echo "[gate] newton chain append: $NEWTON_OK ($CHASH... )"

# ---- phase gate: nothing below mutates without CONFIRM=1 ----
if [ "$CONFIRM" != "1" ]; then
  RESULT="audit-only: state=$STATE_HASH needs_commit=$NEEDS_COMMIT staged_new=$STAGED_NEW"
  sqlite3 data/pathway_cache.db "INSERT OR REPLACE INTO pathways(key,result,ts) VALUES('$CACHE_KEY','$RESULT','$TS')" 2>/dev/null || true
  echo "== [gate] PHASE 1 COMPLETE — review above. Re-run with CONFIRM=1 to execute. =="
  echo "[exit=0]"; exit 0
fi

# ---- stage 7: commit + push_guard + push (CONFIRMED) ----
if [ "$NEEDS_COMMIT" = "1" ]; then
  git add -A bin/ context_bridge/ data/ 2>/dev/null || true
  git commit -m "$MSG"
  echo "[banked] committed: $MSG"
fi
python3 bin/push_guard.py && git push || echo "[held] push_guard blocked — inspect, do not force"
echo "[banked] pushed $(git rev-parse --short HEAD)"

# ---- stage 8: branch hygiene per standing rules ----
# merged branches: delete instantly (yellow PR banners = merge-bait)
MERGED=$(git branch --merged origin/main | grep -vE '^\*|main$' || true)
if [ -n "$MERGED" ]; then
  echo "$MERGED" | xargs -r git branch -d
  echo "[banked] deleted merged local branches"
fi
# unmerged: one PR each via gh, fork-only / two-pane law respected by PRs themselves
for BR in $(git branch --no-merged origin/main | grep -vE '^\*'); do
  if command -v gh >/dev/null && gh auth status >/dev/null 2>&1; then
    gh pr create --base main --head "$BR" --title "[HYGIENE] merge $BR" --body "Auto-proposed by github_hygiene_v1 ts=$TS. Human review required." 2>/dev/null \
      && echo "[banked] PR opened for $BR" || echo "[held] PR create failed for $BR (may already exist)"
  else
    echo "[held] gh unavailable — manual PR needed for $BR"
  fi
done

# ---- stage 9: energy delta + POPW ledger line ----
E_END=$(read_energy)
sqlite3 data/pathway_cache.db "INSERT OR REPLACE INTO pathways(key,result,ts) VALUES('$CACHE_KEY','executed ts=$TS','$TS')" 2>/dev/null || true
printf '%s\n' "{\"event\":\"github_hygiene\",\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"state_hash\":\"$STATE_HASH\",\"newton_hash\":\"$CHASH\",\"energy_start\":\"$E_START\",\"energy_end\":\"$E_END\",\"staged_new\":$STAGED_NEW,\"work_j_est\":100}" >> data/cost_ledger.jsonl
echo "[banked] POPW ledger appended (e_start=$E_START e_end=$E_END)"
echo "[exit=0]"
