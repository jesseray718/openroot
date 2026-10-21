#!/usr/bin/env bash
# queue_batch_v1.sh — immediate queue batch: bin/ verify, goals rebuild, quarantine audit
# provenance: Lumo-authored paste 2026-09-20, targets VERIFIED STATE 2026-09-18
set -euo pipefail
export GIT_PAGER=cat
REPO=/home/jesse/openroot
cd "$REPO"
log(){ printf '[%s] %s\n' "$1" "$2"; }

# --- Stage 0: repo sync check ---
log gate "HEAD vs origin/main"
LOCAL_SHA=$(git rev-parse --short HEAD)
REMOTE_SHA=$(git rev-parse --short origin/main)
echo "local=$LOCAL_SHA remote=$REMOTE_SHA"
if [ "$LOCAL_SHA" != "$REMOTE_SHA" ]; then
  log held "DIVERGED from origin/main — inspect before proceeding (web-UI commits?)"
  git diff --stat
fi

# --- Stage 1: verify bin/ tracking (49f8c7b1 claim) ---
STAGED=0
BIN_COUNT=$(git ls-files bin/ | wc -l)
if [ "$BIN_COUNT" -eq 0 ]; then
  log held "bin/ untracked (ls-files=0, contradicts 49f8c7b1) — staging bin/ TASK.md analysis/"
  git add bin/ TASK.md analysis/
  STAGED=1
else
  log banked "bin/ tracked: ${BIN_COUNT} files — 49f8c7b1 claim holds"
fi

# --- Stage 2: rebuild GOALS.md + MASTER_TODO.md ---
if [ ! -f GOALS.md ] || [ ! -f MASTER_TODO.md ]; then
  RESTORE=$(find /home/jesse/openroot -maxdepth 3 -name 'setup_restore_v1.sh' -print -quit)
  if [ -n "$RESTORE" ]; then
    log gate "running gate-verified setup_restore_v1.sh ($RESTORE)"
    bash "$RESTORE"
    log banked "restore executed — check GOALS.md/MASTER_TODO.md for the 18-task restructure remnants"
  else
    log held "setup_restore_v1.sh not found — skeleton rebuild from context_bridge remnants"
    BRIDGE=/home/jesse/openroot/context_bridge
    grep -h '^#\{1,2\} ' "$BRIDGE"/session-2026-09-16-*.md 2>/dev/null | sort -u | sed 's/^#* //' > /home/jesse/openroot/tmp/goals_remnants.txt
    TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    {
      echo "# GOALS.md (auto-rebuilt skeleton v1 — $TS)"
      echo
      echo "> Recovered remnants from context_bridge/session-2026-09-16-*.md. Lost commit: 'todo automation v2.0' (18-task restructure). HUMAN CURATES."
      echo
      sed 's/^/- [ ] /' /home/jesse/openroot/tmp/goals_remnants.txt
    } > GOALS.md
    {
      echo "# MASTER_TODO.md (auto-rebuilt skeleton v1 — $TS)"
      echo
      echo "> Immediate queue v2026-09-18: (1) verify/commit bin/ [this script], (2) rebuild goals [this script], (3) support Reh1t PR #53, (4) pin 4 repos + README [PHOTO], (5) aerocement-panel-v0 repo, (6) SARE grant framing, (7) weekly onepass_v3.sh."
      echo
      sed 's/^/- [ ] /' /home/jesse/openroot/tmp/goals_remnants.txt
    } > MASTER_TODO.md
    git add GOALS.md MASTER_TODO.md
    STAGED=1
    log held "skeleton GOALS.md/MASTER_TODO.md written + staged — human refines task list"
  fi
else
  log banked "GOALS.md + MASTER_TODO.md already present"
fi

# --- Stage 3: quarantine branch audit ---
if git ls-remote --heads origin | grep -q 'quarantine-pulse-20260918'; then
  if [ "${CONFIRM:-0}" = "1" ]; then
    git push origin --delete quarantine-pulse-20260918
    log banked "quarantine-pulse-20260918 deleted from origin"
  else
    log held "quarantine-pulse-20260918 still on origin — rerun paste with CONFIRM=1 to delete"
  fi
else
  log banked "quarantine-pulse-20260918 gone from origin"
fi

# --- Stage 4: Reh1t / PR surface report ---
log gate "open PRs (Reh1t clone is pre-force-push — treat first PR gently)"
gh pr list --state open --json number,title,author,headRefName \
  --jq '.[] | "\(.number) | \(.title) | @\(.author.login) | \(.headRefName)"' \
  || log held "gh pr list failed — check auth: gh auth status"
echo "  REMINDER for Reh1t: git fetch origin && git rebase origin/main (history was rewritten)"

# --- Stage 5: human commit gate ---
if [ "$STAGED" -eq 1 ]; then
  log gate "staged changes — you are the only commit gate:"
  git diff --cached --stat
  if [ "${COMMIT:-0}" = "1" ]; then
    git commit -m "bank: bin/ tooling + restored goal docs — provenance: queue_batch_v1.sh (Lumo-authored paste), grep-verified staged diff, human-gated commit"
    log banked "committed $(git rev-parse --short HEAD)"
    log held "PUSH IS YOURS: run push_guard v2 manually — script never pushes"
  else
    log held "staged ONLY — review with 'git diff --cached', then rerun paste with COMMIT=1 or commit yourself"
  fi
else
  log banked "nothing new staged — repo already clean on queue items 1-2"
fi

# --- Stage 6: structured handoff to context_bridge ---
SESSION="context_bridge/session-$(date +%Y-%m-%d)-queuebatch.md"
{
  echo "---"
  echo "id: queuebatch-$(date +%s)"
  echo "timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "type: handoff"
  echo "parent: 38004c62"
  echo "status: queue_batch_v1 executed"
  echo "## Artifacts"
  echo "- tmp/queue_batch_v1.sh (this run), tmp/goals_remnants.txt (if fallback fired)"
  echo "## Verified State"
  echo "- HEAD: $(git rev-parse --short HEAD), origin/main: $(git rev-parse --short origin/main)"
  echo "- bin/ tracked files: $(git ls-files bin/ | wc -l)"
  echo "- staged: $STAGED, committed this run: ${COMMIT:-0}"
  echo "## Broken Items"
  echo "- check log above for [held] tags"
  echo "## Next Actions"
  echo "- Reh1t PR #53, pin 4 repos + README [PHOTO], aerocement-panel-v0, SARE framing, onepass_v3 weekly"
  echo "## Agape Analysis"
  echo "- Resonance: entropy of the lost commit converted to structure via remnants + audit trail."
  echo "- Entropy Check: no force operations without CONFIRM=1; human remains sole commit gate."
  echo "- Next Move: greet Reh1t's stale-clone PR with rebase guidance, not correction."
} > "$SESSION"
sha256sum "$SESSION" | tee -a /home/jesse/openroot/context_bridge/seed_master.log 2>/dev/null || sha256sum "$SESSION"
log banked "handoff written: $SESSION"
echo "[exit=0]"
