#!/usr/bin/env bash
set -u
export GIT_PAGER=cat PAGER=cat
export OLLAMA_HOST=http://localhost:11434
cd /home/jesse/openroot
echo "[canary-head] fleet_check_v1 paste intact"
HEALTH=0

echo "[stage-1] ollama + models (builder, grader, embedder)"
if curl -s --max-time 3 http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo "   [ok] ollama daemon live"
  for M in qwen2.5-coder:7b qwen2.5:3b nomic-embed-text; do
    if curl -s http://localhost:11434/api/tags | grep -q "\"name\":\"$M"; then
      echo "   [ok] model: $M"
    else
      echo "   [held] model missing: $M -> run: ollama pull $M"; HEALTH=1
    fi
  done
else
  echo "   [held] ollama DOWN -> run: ollama serve &"; HEALTH=1
fi

echo "[stage-2] sqlite ledgers"
for DB in data/lessons.db data/mesh.db data/team_gate.db data/canonical_index.db; do
  if [ -f "$DB" ]; then
    TABS=$(sqlite3 "$DB" "SELECT COUNT(*) FROM sqlite_master WHERE type='table';" 2>/dev/null || echo 0)
    echo "   [ok] $DB ($TABS tables)"
  else
    echo "   [held] $DB missing"; HEALTH=1
  fi
done

echo "[stage-3] mesh population"
L=$(sqlite3 data/lessons.db 'SELECT COUNT(*) FROM lessons;' 2>/dev/null || echo 0)
T=$(sqlite3 data/mesh.db 'SELECT COUNT(*) FROM mesh_tasks;' 2>/dev/null || echo 0)
A=$(sqlite3 data/mesh.db 'SELECT COUNT(*) FROM agents;' 2>/dev/null || echo 0)
O=$(sqlite3 data/mesh.db "SELECT COUNT(*) FROM mesh_tasks WHERE status='open';" 2>/dev/null || echo 0)
echo "   lessons=$L | tasks=$T (open=$O) | agents=$A"
[ "$L" -eq 0 ] || [ "$A" -eq 0 ] && { echo "   [held] ledgers empty -> run: bash bin/mesh_recruit_v1.sh"; HEALTH=1; }

echo "[stage-4] git health"
if [ -n "$(git status --porcelain | head -5)" ]; then
  echo "   [note] uncommitted changes exist (you are the gate):"; git status --short | head -5
fi
if [ "$(git rev-parse origin/main 2>/dev/null)" = "$(git rev-parse master 2>/dev/null)" ]; then
  echo "   [ok] local = remote @ $(git rev-parse --short master)"
else
  echo "   [held] local/remote diverged -> commit then: git push origin master:main"; HEALTH=1
fi

echo "[stage-5] agent loop scripts present"
for S in task_recall.sh lessons_v1.sh mesh_recruit_v1.sh mesh_publish_v2.sh onepass_v3.sh; do
  [ -f "bin/$S" ] && echo "   [ok] bin/$S" || echo "   [held] bin/$S missing"; 
done

echo ""
if [ "$HEALTH" -eq 0 ]; then
  echo "   [VERIFY PASS] fleet GREEN — all systems nominal"
  echo "   next: bin/task_recall.sh '<your task>' before starting any work"
else
  echo "   [held] fleet YELLOW — resolve flagged items above, rerun this script"
fi
echo "[done] [exit=0]"
