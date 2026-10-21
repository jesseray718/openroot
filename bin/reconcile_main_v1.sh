#!/usr/bin/env bash
# reconcile_main_v1 — commit kai artifacts, reconcile diverged main, push, then
# per-branch verdict: PR (unique work) or DELETE (fully merged). No prompts.
# Audit by default; CONFIRM=1 executes mutations.
set -eu
export GIT_PAGER=cat
cd /home/jesse/openroot
CONFIRM="${CONFIRM:-0}"

echo "== [gate] STEP 1: divergence map =="
git fetch origin 2>/dev/null
echo "-- remote-only commits (theirs, unknown to local) --"
git log --oneline main..origin/main || true
echo "-- local-only commits (yours, unpushed) --"
git log --oneline origin/main..main || true

echo "== [gate] STEP 2: pre-divergence sanity — is your unpushed commit safely stored? =="
UNPUSHED=$(git log --oneline origin/main..main | wc -l)
echo "unpushed local commits: $UNPUSHED"

echo "== [gate] STEP 3: per-branch verdict =="
for BR in chore/superloop-ci-cd-foundation copilot/build-offline-first-toolkit \
          copilot/writing-thesis docs-pr42-clean feat/release; do
  BR_SHA=$(git rev-parse "$BR" 2>/dev/null || echo none)
  ON_ORIGIN=$(git show-ref --verify --quiet refs/remotes/origin/"$BR" && echo yes || echo no)
  AHEAD=$(git rev-list --count origin/main.."$BR" 2>/dev/null || echo "?")
  if [ "$AHEAD" = "0" ]; then VERDICT=DELETE
  elif [ "$ON_ORIGIN" = "yes" ]; then VERDICT=PR_READY
  else VERDICT=PUSH_THEN_PR; fi
  echo "$BR | ahead_by_origin_main:$AHEAD | on_origin:$ON_ORIGIN | verdict:$VERDICT"
done

if [ "$CONFIRM" != "1" ]; then
  echo "== [gate] AUDIT ONLY — rerun with CONFIRM=1 to execute =="
  exit 0; fi

echo "== [gate] STEP 4: commit the 13 uncommitted changes (kai pipeline) =="
git add -A bin/ context_bridge/ data/ .gitignore 2>/dev/null || true
git add -f data/cost_ledger.jsonl 2>/dev/null || echo "[held] cost_ledger gitignored — skipping"
if git diff --cached --quiet; then echo "[gate] nothing to commit"; else
  git commit -m "[ADD] kai9000 corpus retrieval+ingestion+FTS pipeline + a15 runner + hygiene tooling — AI-assisted, human-gated"
fi

echo "== [gate] STEP 5: reconcile main (rebase keeps your linear history) =="
git pull --rebase origin main
python3 bin/push_guard.py && git push || echo "[held] push_guard blocked"
echo "[banked] main synced: $(git rev-parse --short HEAD)"

echo "== [gate] STEP 6: execute verdicts =="
for BR in chore/superloop-ci-cd-foundation copilot/build-offline-first-toolkit \
          copilot/writing-thesis docs-pr42-clean feat/release; do
  AHEAD=$(git rev-list --count origin/main.."$BR" 2>/dev/null || echo "?")
  if [ "$AHEAD" = "0" ]; then
    git branch -D "$BR" && echo "[banked] deleted merged branch: $BR"
  else
    git push origin "$BR"
    gh pr create --base main --head "$BR" \
      --title "[HYGIENE] merge $BR" \
      --body "Curated hygiene PR from reconcile_main_v1 — human review required. Branch carried unique work vs origin/main." \
      && echo "[banked] PR opened: $BR" || echo "[held] PR failed/exists: $BR"
  fi
done
echo "[banked] reconcile complete"
