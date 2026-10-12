#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# goals_rebuild_v1.sh — reconstruct GOALS.md + MASTER_TODO.md from context_bridge remnants
# (the lost "todo automation v2.0" 18-task restructure). Mines sessions, dedupes, ranks by
# recency*frequency, emits DRAFTS first — human reviews, CONFIRM=1 commits. Idempotent.
# Sources: context_bridge/*.md, seed_master.log, existing GOALS.md, IMMEDIATE queue order.
# [canary] goals_rebuild_v1_CANARY_MARKER
set -euo pipefail
export GIT_PAGER=cat PAGER=cat
REPO=/home/jesse/openroot
CONFIRM="${CONFIRM:-0}"
cd "$REPO"
say(){ printf '[%s] %s\n' "$1" "$2"; }
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
say gate "goals_rebuild_v1 start $TS CONFIRM=$CONFIRM"

CB=context_bridge
OUT_DRAFT=$REPO/reports/goals_draft
mkdir -p "$OUT_DRAFT"

# [1] inventory the remnant corpus
SEEDS=$(ls "$CB"/session-*.md 2>/dev/null | wc -l)
LOGS=$( [ -f "$CB/seed_master.log" ] && echo yes || echo no )
say banked "remnant corpus: $SEEDS session files, seed_master.log=$LOGS, existing GOALS.md=$( [ -f GOALS.md ] && echo yes || echo no )"
[ "$SEEDS" -eq 0 ] && { say held "no context_bridge sessions found — nothing to mine, abort"; printf '[exit=0]\n'; exit 0; }

# [2] mine actionable lines: numbered tasks, checkboxes, NEXT/NEXT ACTIONS blocks
grep -hE '^- \[ \]|^[0-9]+\. |^###? *(NEXT|Next|ACTION|TASK)|next action' "$CB"/session-*.md 2>/dev/null \
  | sed -E 's/^[-0-9. ]*\[ \]? *//; s/^#* *//' | sed 's/[[:space:]]*$//' \
  | grep -vE '^$|^.{0,4}$' | sort | uniq -c | sort -rn > "$OUT_DRAFT/task_freq.tsv"
MINED=$(wc -l < "$OUT_DRAFT/task_freq.tsv")
say banked "mined $MINED unique task strings (count-weighted in task_freq.tsv)"

# [3] remnant files from the LOST todo-automation-v2.0 commit — check what physical remnants exist
for F in GOALS.md MASTER_TODO.md; do
  [ -f "$F" ] && say banked "existing $F retained at repo root ($(wc -l < "$F") lines)" \
               || say held "$F absent (expected — v2.0 commit was lost)"
done
[ -f "$REPO/setup_restore_v1.sh" ] && say banked "setup_restore_v1.sh present (gate-verified SAFE per boot seed)" || true

# [4] assemble DRAFT GOALS.md — boot-seed structure + top mined priorities
cat > "$OUT_DRAFT/GOALS.draft.md" <<DRAFT
# GOALS — OpenRoot
<!-- REBUILT $TS from context_bridge remnants + boot seed. Draft only — verify each line
     against your intent before CONFIRM. Source: goal_rebuild_v1, provenance $SEEDS sessions. -->

## North Star
Maximize eta = J_useful/J_human. Agape-as-parallelism-tech guides all engineering.
Falsifiable claims only, no hype, never >100% thermo.

## Standing Objectives (boot-seed verified)
1. SINGLE TRUNK: main is the only default; branches preserved as archival workstreams (16 non-stale, diagnostic 2026-09-19).
2. AUDIT INSTRUMENTS BEFORE BUILDERS — gates get tested more than the code they gate.
3. Human is only commit gate; every script dry-runs by default (CONFIRM=1 mutates).
4. Filter-repo aftercare: repo ~15MiB cap, no >50M blobs ever re-enter history.
5. Local-sovereignty stack: Ollama 7B-builder/3B-grader/FTS5/nomic-embed; no cloud dependency.

## Active Project Tracks
- A: Local AI stack compounding (theorem_compounder, MCP surface, refinement loops)
- B: AeroCement/OpenCell physical validation (panel casts, logging, SARE grant framing)
- C: Community growth (Reh1t onboarding, README/GRLE visibility, profile pinning)
DRAFT

# [5] assemble DRAFT MASTER_TODO — ordered per boot-seed IMMEDIATE queue + mined items
cat > "$OUT_DRAFT/MASTER_TODO.draft.md" <<DRAFT2
# MASTER TODO — OpenRoot
<!-- REBUILT $TS. Order per boot-seed IMMEDIATE QUEUE, mined tasks appended by frequency. -->

## Queue (ordered)
1. [ ] GOALS.md + MASTER_TODO: THIS REBUILD — review drafts in reports/goals_draft/
2. [ ] Reh1t PR #53 (RAG ingestion): gentle first contact — note force-pushed history, their clone is stale
3. [ ] Profile: pin 4 repos + [PHOTO] slot in openroot README
4. [ ] aerocement-panel-v0 standalone repo with build evidence
5. [ ] SARE grant framing (COP-boundary language)
6. [ ] weekly onepass_v3.sh cadence

## Carried-over items awaiting verification (mined from context_bridge, ranked by frequency)
DRAFT2
awk '{n=$1; $1=""; sub(/^ /,""); print n" | "$0}' "$OUT_DRAFT/task_freq.tsv" | head -18 >> "$OUT_DRAFT/MASTER_TODO.draft.md"
echo "" >> "$OUT_DRAFT/MASTER_TODO.draft.md"
echo "<!-- Each mined item above needs: keep / done / drop decision. Trim to the v2.0 ~18-task target. -->" >> "$OUT_DRAFT/MASTER_TODO.draft.md"

# [6] verify drafts non-empty + canary intact
[ -s "$OUT_DRAFT/GOALS.draft.md" ] && [ -s "$OUT_DRAFT/MASTER_TODO.draft.md" ] || { say held "draft assembly failed"; exit 1; }
LINES=$(wc -l < "$OUT_DRAFT/MASTER_TODO.draft.md")
say banked "drafts sealed: GOALS=$(wc -l < "$OUT_DRAFT/GOALS.draft.md") lines, MASTER_TODO=$LINES lines"
grep -q 'goals_rebuild_v1_CANARY_MARKER' "$0" && say banked "canary intact"

# [7] COMMIT (gated) — drafts promote to repo root ONLY on confirmation
if [ "$CONFIRM" = "1" ]; then
  cp "$OUT_DRAFT/GOALS.draft.md" GOALS.md
  cp "$OUT_DRAFT/MASTER_TODO.draft.md" MASTER_TODO.md
  git add GOALS.md MASTER_TODO.md "$OUT_DRAFT/" 
  git commit -m "rebuild GOALS.md + MASTER_TODO.md from context_bridge remnants — supersedes lost todo-automation-v2.0 (18-task restructure, pruned in filter-repo); mined $MINED task strings from $SEEDS sessions; human-reviewed; provenance: goals_rebuild_v1" \
    && say banked "committed $(git rev-parse --short HEAD)"
  git push origin main && say banked "pushed"
else
  say held "DRAFTS ONLY in reports/goals_draft/ — review, edit, then CONFIRM=1 to promote to repo root + commit"
fi
say banked "NEXT: human review of drafts -> CONFIRM=1 -> Reh1t #53 -> pin repos"
printf '[exit=0]\n'
