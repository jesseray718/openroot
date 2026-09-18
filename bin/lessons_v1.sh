#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat PAGER=cat
export OLLAMA_HOST=http://localhost:11434
REPO=/home/jesse/openroot
DB=$REPO/data/lessons.db
mkdir -p $REPO/data
echo "[canary-head] lessons_v1 paste intact"

echo "[stage-1] initialize lessons.db (idempotent)"
sqlite3 "$DB" <<'SQL'
CREATE TABLE IF NOT EXISTS lessons (
  id INTEGER PRIMARY KEY,
  ts TEXT DEFAULT (datetime('now')),
  domain TEXT NOT NULL,            -- git|build|physics|workflow|social
  mistake TEXT NOT NULL,          -- what actually happened
  root_cause TEXT,                -- why it happened
  correction TEXT,                -- what fixes it
  cost TEXT,                      -- quantified damage (time/data/$)
  verified INTEGER DEFAULT 0,     -- 1 once recurrence tested and absent
  recurrence_of INTEGER REFERENCES lessons(id),
  source TEXT                     -- session|7b|3b|human|measurement
);
CREATE INDEX IF NOT EXISTS idx_lessons_domain ON lessons(domain);
CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY,
  ts TEXT DEFAULT (datetime('now')),
  description TEXT,
  lesson_ids TEXT,                -- json array of lessons consulted pre-task
  outcome TEXT                    -- ok|repeat_mistake|new_mistake|success
);
SQL
echo "   [banked] schema live"

echo "[stage-2] seed first lesson — the one we just lived through"
SEED_COUNT=$(sqlite3 "$DB" "SELECT COUNT(*) FROM lessons;")
if [ "$SEED_COUNT" -eq 0 ]; then
  sqlite3 "$DB" "INSERT INTO lessons (domain, mistake, root_cause, correction, cost, source)
  VALUES ('workflow',
  'script pasted directly into interactive shell instead of heredoc-saved file; produced junk files and cd errors',
  'skipped the self-writing paste protocol under time pressure',
  'always cat-heredoc to file + tail-line canary check before execution',
  '~10 min cleanup, 3 junk files in repo root',
  'session');"
  echo "   [banked] seed lesson 1 recorded"
else
  echo "   [skip] lessons exist ($SEED_COUNT)"
fi

echo "[stage-3] pre-task retrieval hook — consults history before every new task"
cat > $REPO/bin/task_recall.sh <<'HOOK'
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
HOOK
chmod +x $REPO/bin/task_recall.sh
echo "   [banked] bin/task_recall.sh installed"

echo "[stage-4] 3B weekly grader — is the system actually getting smarter?"
GRADER_SQL=$(sqlite3 "$DB" \
  "SELECT domain||': '||mistake||' => '||COALESCE(correction,'uncorrected') FROM lessons ORDER BY id DESC LIMIT 20;")
GRADE=$(printf '%s\n' "$GRADER_SQL" | timeout 90 ollama run qwen2.5:3b \
  "These are logged engineering lessons. Cluster them, name the top repeated root-cause theme, and propose ONE process change to prevent recurrence. Output: THEME: <one line> CHANGE: <one line> SMART_METRIC: <one line>" 2>/dev/null || echo "THEME: unavailable - 3B offline")
echo "   $GRADE" | tee -a $REPO/logs/lesson_grades.log 2>/dev/null || echo "   $GRADE"

echo "[stage-5] smartness metric — recurrence rate must trend DOWN"
sqlite3 -header -column "$DB" "
SELECT COUNT(*) AS total_lessons,
       SUM(verified) AS verified_fixed,
       ROUND(100.0 * SUM(verified) / MAX(COUNT(*),1), 1) AS pct_fixed
FROM lessons;"
echo "   [gate] workflow improves iff pct_fixed rises over weeks and repeat_mistake outcomes drop"

echo "[stage-6] example usage pattern"
cat <<'USE'
  # before any task:
  /home/jesse/openroot/bin/task_recall.sh "force push to github after filter-repo"
  # after success or failure, log what happened:
  sqlite3 /home/jesse/openroot/data/lessons.db "INSERT INTO lessons (domain,mistake,root_cause,correction,source) VALUES (...);"
  # log the task outcome:
  sqlite3 /home/jesse/openroot/data/lessons.db "INSERT INTO tasks (description,outcome) VALUES ('force push','ok');"
USE

echo "[stage-7] state"
git -C $REPO status --short | grep -E "lessons|task_recall" || echo "   [note] new files untracked - commit when satisfied"
git -C $REPO log --oneline -1
echo "[done] [exit=0]"
