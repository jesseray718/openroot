# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env bash
set -Eeuo pipefail

COMMAND="${1:?Usage: ai_stack_setup.sh status|stage|commit|push|pr}"
POD="demo-pod"
BRANCH="$(git branch --show-current)"

case "$COMMAND" in
  status)
    python3 -m openloom.cli verify --pod "$POD"
    git status --short
    git diff --stat
    ;;

  stage)
    git add LICENSE pyproject.toml openloom tests examples docs/OPENLOOM_MVP.md
    git status --short
    git diff --cached --stat
    ;;

  commit)
    git diff --cached --quiet && {
      echo "[held] nothing staged"
      exit 1
    }
    git commit -m "feat: add OpenLoom minimal provenance-bearing knowledge pod CLI"
    git log -1 --oneline
    git show --stat --oneline --summary HEAD
    ;;

  push)
    git diff --cached --quiet || {
      echo "[held] staged changes exist; commit first"
      exit 1
    }
    git push -u origin "$BRANCH"
    ;;

  pr)
    gh pr create --draft \
      --title "Add OpenLoom minimal local knowledge pod CLI" \
      --body "Adds a minimal, local-first OpenLoom CLI for converting approved SQLite, CSV/JSONL, Markdown, and text sources into portable provenance-bearing SQLite knowledge pods."
    ;;

  *)
    echo "Unknown command: $COMMAND"
    exit 1
    ;;
esac
