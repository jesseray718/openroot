#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat PAGER=cat
export OLLAMA_HOST=http://localhost:11434
cd /home/jesse/openroot
echo "[canary-head] weekly_audit_v1 paste intact"

echo "[stage-1] trend snapshot"
sqlite3 -header -column data/lessons.db "
SELECT COUNT(*) AS total_lessons,
       SUM(verified) AS verified_fixed,
       ROUND(100.0 * SUM(verified) / MAX(COUNT(*),1), 1) AS pct_fixed
FROM lessons;"
sqlite3 -header -column data/lessons.db "
SELECT outcome, COUNT(*) AS n FROM tasks WHERE outcome IS NOT NULL GROUP BY outcome;"

echo "[stage-2] 3B root-cause clustering (chunked <=8 lessons per lesson 3)"
GRADER_INPUT=$(sqlite3 data/lessons.db \
  "SELECT domain||': '||mistake||' => '||COALESCE(correction,'uncorrected') FROM lessons ORDER BY id DESC LIMIT 8;")
GRADE=$(printf '%s\n' "$GRADER_INPUT" | timeout 90 ollama run qwen2.5:3b \
  "Cluster these engineering lessons. Name the top repeated root-cause theme and propose ONE process change. Exactly 3 lines: THEME: / CHANGE: / SMART_METRIC:" 2>/dev/null \
  || echo "THEME: unavailable - 3B offline")

echo "[stage-3] bank the report"
RPT=reports/lesson_audit-$(date +%Y%m%d).md
mkdir -p reports
{ echo "# Lesson Audit — $(date +%F)"
  echo ""; echo '```'; echo "$GRADE"; echo '```'
  echo ""; echo "## Metrics"
  echo '- lessons total: '"$(sqlite3 data/lessons.db 'SELECT COUNT(*) FROM lessons;')"
  echo '- pct_fixed: '"$(sqlite3 data/lessons.db 'SELECT ROUND(100.0*SUM(verified)/MAX(COUNT(*),1),1) FROM lessons;')%"
  echo '- repeat_mistake tasks: '"$(sqlite3 data/lessons.db "SELECT COUNT(*) FROM tasks WHERE outcome='repeat_mistake';")"
} > "$RPT"
echo "   [banked] $RPT"
grep -q "THEME:" "$RPT" && echo "   [ok] grader output captured" || echo "   [held] grader drifted/offline - see lesson 3"

echo "[stage-4] seed + leave commit to human"
SEED=context_bridge/session-$(date +%Y%m%d_%H%M%S)-audit.md
{ echo "# session: weekly_audit_v1"; echo "- report: $RPT"; echo "- HEAD: $(git rev-parse --short master)"; } > "$SEED"
sha256sum "$SEED" | tee -a seed_master.log
git add "$RPT" "$SEED" bin/weekly_audit_v1.sh bin/daily_loop_v1.sh bin/fleet_check_v1.sh
git diff --cached --stat | tail -3
echo "   [gate] review staged, then YOU commit: git commit -m 'chore(audit): weekly lesson trend + 3B root-cause cluster'"
echo "[done] [exit=0]"
