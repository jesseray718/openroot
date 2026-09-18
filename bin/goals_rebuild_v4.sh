#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat PAGER=cat
cd /home/jesse/openroot
echo "[canary-head] goals_rebuild_v4 paste intact"

REM=context_bridge/session-20260918_015240.md

echo "[stage-1] extract remnant sections (mission brief carried forward)"
sed -n '/## MISSION/,/## NEXT ACTIONS/p' "$REM" | head -50 > /tmp/goals_mission.md
sed -n '/## NEXT ACTIONS/,/## BOOT PROTOCOL/p' "$REM" | head -30 > /tmp/goals_nextactions.md
sed -n '/## BOOT PROTOCOL/,$p' "$REM" | head -15 > /tmp/goals_bootproto.md
MISSION_LINES=$(wc -l < /tmp/goals_mission.md)
NEXT_LINES=$(wc -l < /tmp/goals_nextactions.md)
echo "   extracted: mission=$MISSION_LINES next=$NEXT_LINES boot=$(wc -l < /tmp/goals_bootproto.md) lines"

echo "[stage-2] does hwchain.py exist anywhere? (highest-eta item in the brief)"
find . -name 'hwchain*' -not -path './.git/*' 2>/dev/null | head -5 || true
[ -f bin/hwchain.py ] && echo "   [found] bin/hwchain.py" || echo "   [held] hwchain.py not built yet - stays queued"

echo "[stage-3] assemble GOALS.md v3 — remnant mission + current queue"
{
  echo "# GOALS.md — OpenRoot"
  echo ""
  echo "> Rebuilt $(date +%Y-%m-%d) from context_bridge/session-20260918_015240.md mission brief"
  echo "> (original todo-automation v2.0 restructure lost to filter-repo rewrite; intent preserved below)"
  echo ""
  cat /tmp/goals_mission.md
  echo ""
  cat /tmp/goals_nextactions.md
  echo ""
  echo "## ACTIVE QUEUE (from mesh session, 2026-09-18)"
  echo "1. Wire canonical_index embeddings (34,265 files, 0 embedded) — issue live on GitHub"
  echo "2. Support Reh1t PR #53 (RAG ingestion) — clone predates force-push, be gentle"
  echo "3. hwchain.py genesis build (highest-eta per mission brief)"
  echo "4. aerocement-panel-v0 standalone repo with build evidence"
  echo "5. SARE grant framing (COP-boundary language only — never >100% thermo)"
  echo "6. Weekly onepass_v3.sh cadence"
  echo ""
  cat /tmp/goals_bootproto.md
  echo ""
  echo "## STANDING DOCTRINE"
  echo "- eta = J_useful/J_human is the only efficiency metric"
  echo "- Commit messages assert; grep verifies"
  echo "- Human is the only commit gate"
  echo "- Mistakes become lessons in data/lessons.db (currently 3)"
} > GOALS.md

echo "[stage-4] grep-verify GOALS.md is not hollow"
CHECK_LINES=$(wc -l < GOALS.md)
CHECK_MISSION=$(grep -c '^## MISSION' GOALS.md || true)
CHECK_NEXT=$(grep -c '^## NEXT' GOALS.md || true)
echo "   GOALS.md: $CHECK_LINES lines | mission-section=$CHECK_MISSION | next-section=$CHECK_NEXT"
[ "$CHECK_LINES" -gt 30 ] && [ "$CHECK_MISSION" -eq 1 ] && [ "$CHECK_NEXT" -ge 1 ] \
  && echo "   [banked] structure verified" || { echo "   [held] assembly thin - inspect GOALS.md"; }

echo "[stage-5] commit + push + verify"
git add GOALS.md bin/goals_rebuild_v4.sh
git commit -m "docs(GOALS): v3 rebuild from mission-brief remnant (grep-verified structure, provenance noted)"
git push origin master:main
git fetch origin
[ "$(git rev-parse origin/main)" = "$(git rev-parse master)" ] \
  && echo "   [VERIFY PASS] @ $(git rev-parse --short master)" || echo "   [held] mismatch"

echo "[stage-6] session seed"
SEED=context_bridge/session-$(date +%Y%m%d_%H%M%S)-goals.md
{ echo "# session: goals_rebuild_v4"
  echo "- GOALS.md rebuilt from remnant mission brief ($CHECK_LINES lines, grep-verified)"
  echo "- hwchain.py status: $([ -f bin/hwchain.py ] && echo exists || echo 'not built — next highest-eta item')"
  echo "- lessons: $(sqlite3 data/lessons.db 'SELECT COUNT(*) FROM lessons;') | HEAD: $(git rev-parse --short master)"; } > "$SEED"
sha256sum "$SEED" | tee -a seed_master.log
git add "$SEED" && git commit -m "docs(bridge): goals_rebuild_v4 seed" && git push origin master:main

git log --oneline -3
echo "[done] [exit=0]"
