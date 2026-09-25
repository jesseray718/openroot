#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# pathway_settlement_v7.sh — final settlement of uplift pathway PRs + OpenCell fossil removal
# 1) skills-intro #16: ADOPT branch SECURITY.md (newer, Sep 5) to main, close PR, delete branch
# 2) aerocement #12: CLOSE as stale (main newer on all 5 files), delete branch
# 3) agapenet pathway PR: report state (verify vanished)
# 4) OpenCell: confirm pdf-comp.py is heredoc fossil, DELETE from main (CI fix)
# Canary: [PSV7] | Dry-run default. CONFIRM=1 executes.
set -euo pipefail
export GIT_PAGER=cat
export TZ=UTC

ROOT="/home/jesse/openroot"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$ROOT/context_bridge/pathway_settlement_v7_${TS}.md"
CANARY="[PSV7]"
MODE="${CONFIRM:-0}"

mkdir -p "$ROOT/context_bridge"
echo "# Pathway Settlement v7 ${TS}" > "$LOG"
echo "mode: $([ "$MODE" = "1" ] && echo EXECUTE || echo DRY-RUN)" >> "$LOG"
banner() { echo ""; echo "${CANARY} ==== $1"; }
gh auth status >/dev/null 2>&1 || { echo "[held] gh not authed"; exit 1; }

# ---------- STAGE 1: skills-intro #16 — adopt newer SECURITY.md ----------
banner "STAGE 1 — ADOPT skills-intro SECURITY.md (branch newer: Sep 5 > Aug 30)"
R="jesseray718/skills-introduction-to-github"; HEAD="chore/foundation-uplift-20260828-225816"
MSHA="$(gh api "repos/$R/contents/SECURITY.md?ref=main" --jq '.sha' 2>/dev/null || echo "")"
BCONT="$(gh api "repos/$R/contents/SECURITY.md?ref=${HEAD}" --jq '.content' 2>/dev/null || echo "")"
if [ -n "$BCONT" ]; then
  echo "[gate] adopt SECURITY.md: main sha=$MSHA, branch content captured"
  if [ "$MODE" = "1" ]; then
    gh api -X PUT "repos/$R/contents/SECURITY.md" \
      -f message="[ADOPT] SECURITY.md from ${HEAD} (newer revision, blob-sha audit) [AI-assisted, human-gated]" \
      -f content="$BCONT" -f branch=main ${MSHA:+-f sha=$MSHA} >> "$LOG" 2>&1 \
      && echo "[banked] SECURITY.md adopted to main" || echo "[held] adopt FAILED"
  fi
  echo "[gate] close #16 + delete branch (16/17 already identical)"
  [ "$MODE" = "1" ] && {
    gh pr close 16 -R "$R" --comment "16/17 files identical to main; remaining file (SECURITY.md, newer branch revision) adopted directly. Superseded. [AI-assisted, human-gated]" >> "$LOG" 2>&1 || true
    gh api -X DELETE "repos/$R/git/refs/heads/${HEAD}" >> "$LOG" 2>&1 || true; }
else echo "[held] branch content unavailable — check ${HEAD} exists"; fi

# ---------- STAGE 2: aerocement #12 — close stale ----------
banner "STAGE 2 — CLOSE aerocement #12 (main newer on all 5 files)"
R="jesseray718/aerocement"; HEAD="chore/knowledge-unify-20260901-011802-aerocement-"
echo "[gate] main superseded branch (main@2026-09-10 > branch@2026-09-01)"
if [ "$MODE" = "1" ]; then
  gh pr close 12 -R "$R" --comment "Closing as stale: main received newer revisions of all 5 files (Sep 10) after this branch diverged (Sep 1). Blob-sha audited. [AI-assisted, human-gated]" >> "$LOG" 2>&1 || true
  gh api -X DELETE "repos/$R/git/refs/heads/${HEAD}" >> "$LOG" 2>&1 || true
  echo "[banked] closed + deleted"
fi

# ---------- STAGE 3: agapenet PR state ----------
banner "STAGE 3 — VERIFY agapenet pathway PR"
gh pr list -R jesseray718/agapenet --state all --limit 5 \
  --json number,state,title --jq '.[] | "\(.number) \(.state) \(.title)"' | tee -a "$LOG"

# ---------- STAGE 4: OpenCell fossil — pdf-comp.py ----------
banner "STAGE 4 — OpenCell CI FIX: remove heredoc fossil"
R="jesseray718/OpenCell-Thermal-System"; F="1_code/src/pdf-comp.py"
FIRST="$(gh api "repos/$R/contents/${F}?ref=main" --jq '.content' | base64 -d | head -n 1)"
echo "[gate] pdf-comp.py line 1: ${FIRST}"
case "$FIRST" in cat*<<*) MATCH=1;; *) MATCH=0;; esac; if [ "$MATCH" = "1" ]; then
  echo "[gate] CONFIRMED heredoc fossil — shell wrapper saved as .py, breaks py_compile"
  FSHA="$(gh api "repos/$R/contents/${F}?ref=main" --jq '.sha')"
  if [ "$MODE" = "1" ]; then
    gh api -X DELETE "repos/$R/contents/${F}" \
      -f message="[FIX] remove heredoc fossil: shell wrapper pasted as pdf-comp.py, broke python-quality CI [AI-assisted, human-gated]" \
      -f sha="$FSHA" -f branch=main >> "$LOG" 2>&1 \
      && echo "[banked] fossil deleted — CI should go green on next run" || echo "[held] delete FAILED"
  fi
else
  echo "[held] first line doesn't match fossil pattern — eyeball file before acting"
fi

banner "SUMMARY"
sha256sum "$LOG" | tee -a "$LOG"
[ "$MODE" = "1" ] || echo "${CANARY} [DRY-RUN] — then: CONFIRM=1 bash $0"
echo "${CANARY} [exit=0]"
exit 0
