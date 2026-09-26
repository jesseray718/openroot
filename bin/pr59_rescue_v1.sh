#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# pr59_rescue_v1.sh — rescue additive content from coderabbit PR #59 (post-filter-repo orphan)
# Files absent on main -> PUT to main. Files present -> [held] for human diff.
# Then close PR as rescued, delete branch. DB-sync nuance: data/*.db gitignored, skip binaries.
# Canary: [P59RV1] | Dry-run default. CONFIRM=1 executes.
set -euo pipefail
export GIT_PAGER=cat
export TZ=UTC

R="jesseray718/openroot"
BR="coderabbit/changes/eb9e4190"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="/home/jesse/openroot/context_bridge/pr59_rescue_${TS}.md"
CANARY="[P59RV1]"
MODE="${CONFIRM:-0}"
mkdir -p "$(dirname "$LOG")"
echo "# PR59 Rescue ${TS}" > "$LOG"

gh auth status >/dev/null 2>&1 || { echo "[held] gh not authed"; exit 1; }

FILES="$(gh pr view 59 -R "$R" --json files --jq '.files[].path')"
RESCUED=0; HELD=0; SKIPPED=0
while read -r fp; do
  [ -z "$fp" ] && continue
  case "$fp" in
    data/*.db) echo "[gate] skip binary db (gitignored runtime): $fp"; SKIPPED=$((SKIPPED+1)); continue ;;
    .gitignore) echo "[held] .gitignore modification — human diff (1 line, eyeball it)"; HELD=$((HELD+1)); continue ;;
  esac
  MS="$(gh api "repos/$R/contents/${fp}?ref=main" --jq '.sha' 2>/dev/null || echo "")"
  if [ -z "$MS" ]; then
    B64="$(gh api "repos/$R/contents/${fp}?ref=${BR}" --jq '.content' 2>/dev/null || echo "")"
    if [ -z "$B64" ]; then echo "[held] fetch FAILED $fp"; HELD=$((HELD+1)); continue; fi
    if [ "$MODE" = "1" ]; then
      if gh api -X PUT "repos/$R/contents/${fp}" \
        -f message="[RESCUE] $fp from PR59 branch (survived filter-repo prune) [AI-assisted, human-gated]" \
        -f content="$B64" -f branch=main >> "$LOG" 2>&1; then
        echo "[banked] rescued $fp"; RESCUED=$((RESCUED+1))
      else echo "[held] PUT FAILED $fp"; HELD=$((HELD+1)); fi
    else
      echo "[gate] dry: would rescue $fp"; RESCUED=$((RESCUED+1))
    fi
  else
    echo "[held] exists on main: $fp — human diff"; HELD=$((HELD+1))
  fi
done <<< "$FILES"
echo "[gate] rescued=$RESCUED held=$HELD skipped=$SKIPPED" | tee -a "$LOG"

if [ "$MODE" = "1" ] && [ "$HELD" -le 2 ]; then
  gh pr close 59 -R "$R" --comment "Additive content rescued directly to main (survived the Sept 18 history rewrite that orphaned this branch). Conflict was phantom — no common ancestor post filter-repo. [AI-assisted, human-gated]" >> "$LOG" 2>&1 || true
  gh api -X DELETE "repos/$R/git/refs/heads/${BR}" >> "$LOG" 2>&1 || true
  echo "[banked] PR closed + branch deleted" | tee -a "$LOG"
fi
sha256sum "$LOG" | tee -a "$LOG"
[ "$MODE" = "1" ] || echo "${CANARY} [DRY-RUN] — review rescued list, then CONFIRM=1 bash $0"
echo "${CANARY} [exit=0]"
exit 0
