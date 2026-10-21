#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# OpenRoot — jesseray718
# PANE: SSH — add Reh1t contributor acknowledgment to README.md
# eta = useful_joules / human_joules
set -euo pipefail
export GIT_PAGER=cat
REPO=/home/jesse/openroot
STAMP=$(date +%Y%m%d_%H%M%S)
CANARY="CONTRIB1"
LOG=/home/jesse/openroot/logs/contributor_ack_${STAMP}.log
mkdir -p "$(dirname "$LOG")"
exec > >(tee -a "$LOG") 2>&1
echo "[$CANARY] START $STAMP"
cd "$REPO"

README=/home/jesse/openroot/README.md
BACKUP="$README.bak.${STAMP}"

# [gate] does README exist?
[[ -f "$README" ]] || { echo "[gate] README.md not found at $README"; exit 1; }

# [banked] backup before edit
cp "$README" "$BACKUP"
echo "[banked] backup: $BACKUP"

# [gate] does CONTRIBUTOR section already exist?
if grep -q "Reh1t\|Rehan Tariq" "$README" 2>/dev/null; then
  echo "[status] Reh1t already credited in README — skip (idempotent)"
else
  # Insert Contributors section before "## License" or at end
  if grep -q "^## License" "$README"; then
    awk '/^## License/{
      print ""
      print "## Contributors"
      print ""
      print "### Early Contributors"
      print ""
      print "- **Rehan Tariq** (@Reh1t) — [PR #63](https://github.com/jesseray718/openroot/pull/63): Local LLM Agents + SQLite RAG Integration"
      print "  - Implemented zero-dependency LLM agent orchestration with SQLite FTS5 indexing"
      print "  - Enabled local 7B/3B model routing for authoring/validation loops"
      print "  - Authorship preserved through history rewrites (commit eb247e94)"
      print "  - *Note: main branch was force-pushed via git filter-repo to strip >50MB blobs; work was reconciled onto new main.*"
      print ""
      next
    }
    {print}' "$README" > "$README.tmp"
    mv "$README.tmp" "$README"
    echo "[banked] inserted Contributors section before License"
  else
    cat >> "$README" <<_EOF_CONTRIB_

## Contributors

### Early Contributors

- **Rehan Tariq** (@Reh1t) — [PR #63](https://github.com/jesseray718/openroot/pull/63): Local LLM Agents + SQLite RAG Integration
  - Implemented zero-dependency LLM agent orchestration with SQLite FTS5 indexing
  - Enabled local 7B/3B model routing for authoring/validation loops
  - Authorship preserved through history rewrites (commit eb247e94)
  - *Note: main branch was force-pushed via git filter-repo to strip >50MB blobs; Reh1t's work was reconciled onto new main.*
_EOF_CONTRIB_
    echo "[banked] appended Contributors section at end"
  fi
fi

# Show the new section
echo ""
echo "[status] Contributors section in README.md:"
grep -A 10 "^## Contributors" "$README" || echo "(section not found — check edit)"

# [held] review and commit
sha256sum "$README"
echo ""
echo "Next: Review the diff, then:"
echo "  git diff HEAD README.md  # review changes"
echo "  git add README.md && git commit -m \"[DOC] add Reh1t contributor acknowledgment\" && git push origin main"
echo ""
echo "[$CANARY] END $STAMP [exit=0]"
