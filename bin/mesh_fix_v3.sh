#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat PAGER=cat
cd /home/jesse/openroot
echo "[canary-head] mesh_fix_v3 paste intact"

echo "[stage-1] re-log lesson 3 with column/value parity (verifying this time)"
sqlite3 data/lessons.db "INSERT INTO lessons (domain,mistake,root_cause,correction,cost,source)
  VALUES ('workflow','3B ignored ranking rubric and free-associated a solution instead',
  '20 task titles overloaded 3B context; small model loses instruction-following at scale',
  'chunk 3B prompts to <=8 items or escalate ranking to 7B','wasted one dispatch','measurement');"
LOGGED=$(sqlite3 data/lessons.db "SELECT COUNT(*) FROM lessons;")
[ "$LOGGED" -eq 3 ] && echo "   [banked] lesson 3 verified in db (grep-verified, not asserted)" \
  || { echo "   [held] insert failed again"; exit 1; }

echo "[stage-2] inspect what the remnant actually contains"
REM=context_bridge/session-20260918_015240.md
echo "   remnant: $(wc -l < "$REM") lines, $(du -h "$REM" | cut -f1)"
grep -n -iE 'goal|todo|task-[0-9]|next|priorit' "$REM" | head -20 || echo "   [none] no task-structure keywords"

echo "[stage-3] replace hollow GOALS.md with honest skeleton"
cat > GOALS.md <<'GOALSHDR'
# GOALS.md — OpenRoot

> Status: UNDER RECONSTRUCTION (v2 2026-09-18)
> The original "todo automation v2.0" 18-task restructure was lost in the
> filter-repo history rewrite (see lessons trail + context_bridge remnant).
> This file is being rebuilt task-by-task. Single-step discipline below.

## NEXT (single step)
- [ ] Wire canonical_index embeddings (34,265 files indexed, 0 embedded) — issue live on GitHub

## ACTIVE QUEUE (priority order)
1. Rebuild this file properly from session remnants (this task)
2. Support Reh1t PR #53 (RAG ingestion) — their clone predates force-push, be gentle
3. Pin 4 repos on profile + README [PHOTO] slot + contact email decision
4. aerocement-panel-v0 standalone repo with build evidence
5. SARE grant framing (COP-boundary language only — never >100% thermo)
6. Weekly onepass_v3.sh cadence

## STANDING DOCTRINE
- eta = J_useful/J_human is the only efficiency metric
- Commit messages assert; grep verifies
- Human is the only commit gate
- Every mistake becomes a lesson in data/lessons.db (currently 3)
GOALSHDR
git add GOALS.md data/lessons.db

echo "[stage-4] correct the record in a fresh seed"
SEED=context_bridge/session-$(date +%Y%m%d_%H%M%S)-fix.md
{ echo "# session: mesh_fix_v3"
  echo "## Corrections to mesh_publish_v2 session"
  echo "- lesson 3 was NOT logged (sql arity bug: 6 values / 5 cols) — now fixed + grep-verified"
  echo "- GOALS.md was hollow (3 lines) — replaced with honest reconstruction skeleton"
  echo "## Verified state"
  echo "- lessons: $(sqlite3 data/lessons.db 'SELECT COUNT(*) FROM lessons;')"
  echo "- HEAD at fix commit (see git log)"; } > "$SEED"
sha256sum "$SEED" | tee -a seed_master.log
git add "$SEED" bin/mesh_fix_v3.sh

echo "[stage-5] commit + push + verify"
git commit -m "fix(mesh): lesson-3 sql parity + honest GOALS.md skeleton (corrects false assertions in prior seed)"
git push origin master:main
git fetch origin
[ "$(git rev-parse origin/main)" = "$(git rev-parse master)" ] \
  && echo "   [VERIFY PASS] @ $(git rev-parse --short master)" || echo "   [held] mismatch"

echo "[stage-6] state"
git log --oneline -3
sqlite3 -header -column data/lessons.db "SELECT id, domain, substr(mistake,1,50) AS mistake FROM lessons;"
echo "[done] [exit=0]"
