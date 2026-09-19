#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat PAGER=cat
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd) || exit 1
REPO_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd) || exit 1
cd "$REPO_ROOT" || exit 1
SQLITE_PARAMS=(python3 bin/sqlite_params.py)
echo "[canary-head] daily_loop_v1 paste intact"

case "${1:-}" in
  start)
    # ---- BEFORE any task: consult the lesson trail ----
    [ -z "${2:-}" ] && { echo "usage: daily_loop_v1.sh start '<task description>'"; exit 1; }
    bash bin/task_recall.sh "$2"
    "${SQLITE_PARAMS[@]}" data/lessons.db \
      "INSERT INTO tasks (description, lesson_ids, outcome)
       SELECT ?, '', 'pending' WHERE NOT EXISTS
       (SELECT 1 FROM tasks WHERE description=? AND outcome='pending')" "$2" "$2"
    echo "[gate] lessons above are your constraints. work the task now."
    echo "       when done: daily_loop_v1.sh finish $ '?' '<ok|new_mistake|repeat_mistake>' '[what happened]'"
    ;;

  finish)
    # ---- AFTER the task: record the outcome + any lesson ----
    TS=$("${SQLITE_PARAMS[@]}" data/lessons.db \
      "SELECT id FROM tasks WHERE description=? AND outcome='pending' ORDER BY id DESC LIMIT 1" \
      "${2:-}" 2>/dev/null || echo "")
    OUTCOME="${3:-ok}"; NOTES="${4:-none}"
    if [ -n "$TS" ]; then
      "${SQLITE_PARAMS[@]}" data/lessons.db \
        "UPDATE tasks SET outcome=? WHERE id=?" "$OUTCOME" "$TS"
      echo "   [banked] task #$TS recorded: $OUTCOME"
    else
      echo "   [note] no pending task '$2' - logging standalone"
    fi
    if [ "$OUTCOME" != "ok" ]; then
      echo "   [gate] log the lesson now (multi-line; end with DONE alone on a line):"
      "${SQLITE_PARAMS[@]}" data/lessons.db \
        "INSERT INTO lessons (domain,mistake,root_cause,correction,source)
         VALUES (?, ?, '(fill in via sqlite)', '(fill in via sqlite)', 'session')" \
        "${OUTCOME:-unknown}" "$NOTES"
      echo "   [banked] lesson seeded — flesh out root_cause/correction in data/lessons.db"
      LID=$(sqlite3 data/lessons.db 'SELECT MAX(id) FROM lessons;')
      [ -n "$TS" ] && "${SQLITE_PARAMS[@]}" data/lessons.db \
        "UPDATE tasks SET lesson_ids=? WHERE id=?" "[$LID]" "$TS"
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
