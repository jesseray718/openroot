#!/usr/bin/env bash
# openroot_recon.sh - READ-ONLY reconnaissance. Writes nothing, stages nothing.
# Usage: bash openroot_recon.sh [path-inside-repo]

set -uo pipefail

TARGET="${1:-$PWD}"
ts()  { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
say() { printf '[%s] %s\n' "$(ts)" "$*"; }

if ! ROOT="$(git -C "$TARGET" rev-parse --show-toplevel 2>/dev/null)"; then
  say "ERROR: not inside a git work tree: $TARGET"
  exit 1
fi

say "work tree : $ROOT"
say "branch    : $(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null)"
say "head      : $(git -C "$ROOT" log -1 --format='%h %ci %s' 2>/dev/null)"
say "paths     : $(git -C "$ROOT" status --porcelain 2>/dev/null | wc -l) changed/untracked"

printf '%s\n' "--- remotes (credentials masked) ---"
git -C "$ROOT" remote -v 2>/dev/null \
  | sed -E 's#(://)[^@/[:space:]]+@#\1***@#g' | sed 's/^/  /'

printf '%s\n' "--- flagged commits ---"
for c in fce8eb0 682fe7b; do
  if git -C "$ROOT" rev-parse --verify --quiet "${c}^{commit}" >/dev/null 2>&1; then
    say "PRESENT: $c"
  else
    say "absent : $c"
  fi
done

printf '%s\n' "--- credential scan (tracked files; locations only) ---"
PATTERNS=(
  'AWS_SECRET_ACCESS_KEY='
  'GROQ_API_KEY=[A-Za-z0-9_-]{40,}'
  'GEMINI_API_KEY=[A-Za-z0-9_-]{40,}'
  'OPENROUTER_API_KEY=[A-Za-z0-9_-]{40,}'
  'XAI_API_KEY=[A-Za-z0-9_-]{40,}'
  'JWT_SECRET=[A-Za-z0-9_-]{32,}'
  'DATABASE_URL=postgresql://[^ ]+:[^ ]+@'
  'TELEGRAM_BOT_TOKEN=[A-Za-z0-9_-]{40,}'
)
hits=0
for p in "${PATTERNS[@]}"; do
  out="$(git -C "$ROOT" grep -nIE -- "$p" -- . 2>/dev/null | cut -d: -f1,2 | head -5)"
  if [ -n "$out" ]; then
    say "MATCH ${p%%=*}= (locations only, values not printed)"
    printf '%s\n' "$out" | sed 's/^/  /'
    hits=1
  fi
done
[ "$hits" -eq 0 ] && say "clean: no credential patterns in tracked files"

printf '%s\n' "--- first 30 changed/untracked paths ---"
git -C "$ROOT" status --short 2>/dev/null | head -30 | sed 's/^/  /'

say "done - nothing was written, staged, or committed"
