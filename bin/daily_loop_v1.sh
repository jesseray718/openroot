#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat PAGER=cat
cd /home/jesse/openroot
echo "[canary-head] daily_loop_v1 paste intact"

case "${1:-}" in
  start)
    # ---- BEFORE any task: consult the lesson trail ----
    [ -z "${2:-}" ] && { echo "usage: daily_loop_v1.sh start '<task description>'"; exit 1; }
    bash bin/task_recall.sh "$2"
    sqlite3 data/lessons.db "INSERT INTO tasks (description, lesson_ids, outcome)
      SELECT '$2', '', 'pending' WHERE NOT EXISTS
      (SELECT 1 FROM tasks WHERE description='$2' AND outcome='pending');"
    echo "[gate] lessons above are your constraints. work the task now."
    echo "       when done: daily_loop_v1.sh finish $ '?' '<ok|new_mistake|repeat_mistake>' '[what happened]'"
    ;;

  finish)
    # ---- AFTER the task: record the outcome + any lesson ----
    TS=$(sqlite3 data/lessons.db "SELECT id FROM tasks WHERE description='${2:-}' AND outcome='pending' ORDER BY id DESC LIMIT 1;" 2>/dev/null || echo "")
    OUTCOME="${3:-ok}"; NOTES="${4:-none}"
    if [ -n "$TS" ]; then
      sqlite3 data/lessons.db "UPDATE tasks SET outcome='$OUTCOME' WHERE id=$TS;"
      echo "   [banked] task #$TS recorded: $OUTCOME"
    else
      echo "   [note] no pending task '$2' - logging standalone"
    fi
    if [ "$OUTCOME" != "ok" ]; then
      echo "   [gate] log the lesson now (multi-line; end with DONE alone on a line):"
      sqlite3 data/lessons.db <<SQL
INSERT INTO lessons (domain,mistake,root_cause,correction,source)
VALUES ('${OUTCOME:-unknown}','${NOTES}','(fill in via sqlite)','(fill in via sqlite)','session');
SQL
      echo "   [banked] lesson seeded — flesh out root_cause/correction in data/lessons.db"
      LID=$(sqlite3 data/lessons.db 'SELECT MAX(id) FROM lessons;')
      [ -n "$TS" ] && sqlite3 data/lessons.db "UPDATE tasks SET lesson_ids='[$LID]' WHERE id=$TS;"
    fi
    ;;

  *)
    echo "usage:"
    echo "  bin/daily_loop_v1.sh start 'wire embeddings into canonical_index'"
    echo "  bin/daily_loop_v1.sh finish 'wire embeddings' ok"
    echo "  bin/daily_loop_v1.sh finish 'wire embeddings' new_mistake 'sql arity bug in insert'"
    ;;
esac
echo "[done] [exit=0]"
