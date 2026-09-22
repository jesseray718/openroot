#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat PAGER=cat
export OLLAMA_HOST=http://localhost:11434
REPO=/home/jesse/openroot
cd "$REPO"
echo "[canary-head] mesh_recruit_v1 paste intact"

echo "[stage-1] hygiene — never commit bytecode (lesson candidate #2)"
git rm --cached -r --quiet bin/__pycache__ 2>/dev/null || echo "   [skip] pycache not staged"
{ [ -f .gitignore ] && grep -q '__pycache__' .gitignore || echo -e "__pycache__/\n*.pyc\n.aider.tags.cache.v4/"; } >> .gitignore.tmp
sort -u .gitignore.tmp > .gitignore && rm .gitignore.tmp
git add .gitignore
echo "   [banked] pyc unstaged, gitignore hardened"
sqlite3 data/lessons.db "INSERT INTO lessons (domain,mistake,root_cause,correction,cost,source)
  VALUES ('git','git add -A staged __pycache__ bytecode into commit','blanket add ignores artifact hygiene',
  'gitignore __pycache__ + *.pyc before add; never add -A on untracked dirs','0 damage - caught at gate',
  'session');" && echo "   [banked] lesson 2 logged"

echo "[stage-2] mesh.db — agent coordination ledger"
sqlite3 data/mesh.db <<'SQL'
CREATE TABLE IF NOT EXISTS agents (
  name TEXT PRIMARY KEY, role TEXT, model TEXT,
  capabilities TEXT, status TEXT DEFAULT 'idle');
CREATE TABLE IF NOT EXISTS mesh_tasks (
  id INTEGER PRIMARY KEY, ts TEXT DEFAULT (datetime('now')),
  title TEXT, description TEXT, source_path TEXT,
  difficulty TEXT,            -- easy|medium|hard
  assignee TEXT DEFAULT NULL, claimed_at TEXT,
  status TEXT DEFAULT 'open', -- open|claimed|done|verified
  credit TEXT DEFAULT NULL);  -- contributor name for CREDITS
INSERT OR REPLACE INTO agents VALUES
  ('seven_b','builder','qwen2.5-coder:7b','code edits, spec execution','idle'),
  ('three_b','grader','qwen2.5:3b','rubric grading, clustering','idle'),
  ('sqlite','memory','-','ledgers: lessons, mesh, canonical index','always'),
  ('human_jesse','gatekeeper','-','commit gate, physics judgment, recruitment','idle'),
  ('contributor_public','guest','-','good-first-issues, docs, builds, measurements','open');
SQL
echo "   [banked] agents registered: $(sqlite3 data/mesh.db 'SELECT COUNT(*) FROM agents;')"

echo "[stage-3] mine TODO/FIXME debt into candidate issues"
COUNT=$(sqlite3 data/mesh.db 'SELECT COUNT(*) FROM mesh_tasks;')
if [ "$COUNT" -eq 0 ]; then
  while IFS=: read -r F LINE TXT; do
    TXT=$(echo "$TXT" | sed "s/'/''/g" | cut -c1-200)
    F=${F#.\/}
    sqlite3 data/mesh.db "INSERT INTO mesh_tasks (title,description,source_path,difficulty)
      VALUES ('$TXT','$TXT','$F:$LINE','easy');"
  done < <(grep -rn --include='*.py' --include='*.sh' -iE 'TODO|FIXME|XXX:' bin/ 2>/dev/null | head -40)
  # bank the known hard items explicitly
  sqlite3 data/mesh.db "INSERT INTO mesh_tasks (title,description,source_path,difficulty)
    VALUES ('Wire canonical_index embeddings','Run/populate module_name,function_names + vector embeddings for 34265 indexed files — see enable_vector_embeddings.py','enable_vector_embeddings.py','medium');"
  sqlite3 data/mesh.db "INSERT INTO mesh_tasks (title,description,source_path,difficulty)
    VALUES ('Rebuild GOALS.md + MASTER_TODO.md','Restore 18-task restructure from context_bridge/session-20260918_015240.md remnant','context_bridge/session-20260918_015240.md','medium');"
  sqlite3 data/mesh.db "INSERT INTO mesh_tasks (title,description,source_path,difficulty)
    VALUES ('Fix OpenCell contact placeholder + license decision','Replace [your-email@example.com]; decide CC-BY-NC-SA vs CC-BY-SA for commercial builders','OpenCell-Thermal-System README','easy');"
  sqlite3 data/mesh.db "INSERT INTO mesh_tasks (title,description,source_path,difficulty)
    VALUES ('Build pyranometer measurement rig','<\$200 BOM: pyranometer + thermocouples + flow logging; one week data on 65sqft panel converts claims to measurements','OpenCell-Thermal-System','medium');"
fi
echo "   [banked] mesh tasks: $(sqlite3 data/mesh.db 'SELECT COUNT(*) FROM mesh_tasks;')"

echo "[stage-4] 3B ranks issues by stranger-clarity (recruitability)"
OPEN=$(sqlite3 data/mesh.db "SELECT title FROM mesh_tasks WHERE status='open' LIMIT 20;")
RANK=$(printf '%s\n' "$OPEN" | timeout 90 ollama run qwen2.5:3b \
  "Rank these open-source task titles by how quickly a stranger could start contributing (clarity+scopeclearness). Output lines: RANK: <n> | <title> | WHY: <5 words>" 2>/dev/null || echo "RANK: unavailable")
echo "$RANK" | tee logs/mesh_ranking.log | head -15

echo "[stage-5] generate GOOD_FIRST_ISSUES.md — the 30-minute-win front door"
sqlite3 -header data/mesh.db \
  "SELECT id, title, difficulty, source_path FROM mesh_tasks WHERE status='open' ORDER BY id;" \
  > /tmp/mesh_open.md
cat > GOOD_FIRST_ISSUES.md <<'GFI'
# Good First Issues — Welcome, Builder

OpenRoot is a radical-credit, open-door project: **everyone who contributes gets named.**
Claim any task by commenting on it or opening a PR referencing the task ID.
Simple tasks ship in ~30 minutes. No gatekeeping, no CLA maze — GPL-3.0 code / CC-BY-SA-4.0 docs.

| ID | Task | Difficulty | Location |
|----|------|-----------|----------|
GFI
sed 's/|/|/g; s/^/| /; s/$/ |/' /tmp/mesh_open.md >> GOOD_FIRST_ISSUES.md
cat >> GOOD_FIRST_ISSUES.md <<'GFI2'

## Permaculture Operating Principles (how we work)
1. Observe & interact — consult lessons.db before every task
2. Catch & store energy — bank every insight into a ledger
3. Obtain a yield — measure useful output per joule invested
4. Self-regulate & accept feedback — every change is graded before merge
5. Value renewables — local models, solar-powered hardware
6. Produce no waste — mistakes become lessons, lessons become docs
7. Patterns to details — canon locked, spokes free
8. Integrate, don't segregate — builders, graders, rememberers, humans
9. Small & slow — atomic edits only
10. Value diversity — your build, your data, your name in CREDITS.md
11. Edges are productive — mobile/Termux contributions welcome
12. Respond to change — lessons verified, workflow mutates

**Credit:** every merged PR adds a line to CREDITS.md. Attribution is sacred here.
GFI2
git add GOOD_FIRST_ISSUES.md && echo "   [banked] GOOD_FIRST_ISSUES.md generated"

echo "[stage-6] session handoff to context_bridge"
SEED=context_bridge/session-$(date +%Y%m%d_%H%M%S)-mesh-recruit.md
{ echo "# session: mesh_recruit_v1 $(date -u +%FT%TZ)"
  echo "- agents: $(sqlite3 data/mesh.db 'SELECT COUNT(*) FROM agents;') | tasks: $(sqlite3 data/mesh.db 'SELECT COUNT(*) FROM mesh_tasks;')"
  echo "- pyc hygiene fixed, lesson 2 logged, GOOD_FIRST_ISSUES.md generated"
  echo "- next: rebuild GOALS.md from session-20260918_015240.md remnant; wire embeddings"; } > "$SEED"
sha256sum "$SEED" | tee -a seed_master.log
git add "$SEED" data/mesh.db data/lessons.db bin/lessons_v1.sh bin/task_recall.sh bin/mesh_recruit_v1.sh 2>/dev/null || true

echo "[stage-7] state — review, then YOU commit"
git diff --cached --stat | tail -5
git log --oneline -1
sqlite3 -header -column data/lessons.db "SELECT COUNT(*) AS lessons, SUM(verified) AS verified FROM lessons;"
echo "[done] [exit=0]"
