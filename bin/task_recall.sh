#!/usr/bin/env bash
set -eu
DB=/home/jesse/openroot/data/lessons.db
DESC="${1:?usage: task_recall.sh <task description>}"
# lexical overlap match — swap for nomic-embed cosine search when canonical_index wired
HITS=$(sqlite3 -separator '|' "$DB" \
  "SELECT id, mistake, correction FROM lessons
   WHERE lower('$DESC') LIKE '%' || lower(replace(substr(mistake,1,40),' ','%')) || '%'
      OR mistake LIKE '%' || substr('$DESC',1,25) || '%'
   ORDER BY id DESC LIMIT 5;")
echo "[recall] prior lessons matching this task:"
if [ -n "$HITS" ]; then echo "$HITS"; else echo "   [none] no prior lesson matches - new territory"; fi
echo "[recall] total lessons on file: $(sqlite3 "$DB" 'SELECT COUNT(*) FROM lessons;')"
