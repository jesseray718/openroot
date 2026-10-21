#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# run_handoff_v1.sh — post-run digest for sharing with Lumo.
# Usage: run_handoff_v1.sh <report_dir> [log_file]
# Writes a single bounded digest -> upload THAT file to the Lumo chat.
# [canary] run_handoff_v1_CANARY_MARKER
set -euo pipefail
DIR="${1:?usage: run_handoff_v1.sh <report_dir> [log]}"
LOG="${2:-/dev/null}"
OUT="$DIR/lumo_digest_$(date +%H%M%S).txt"
say(){ printf '[%s] %s\n' "$1" "$2"; }
cap(){ # cap <file> <max_lines> <label>
  local f="$1" max="$2" lbl="$3" n
  [ -f "$f" ] || { echo "-- $lbl: ABSENT"; echo; return; }
  n=$(wc -l < "$f")
  echo "-- $lbl ($n lines)"
  if [ "$n" -gt "$max" ]; then head -n "$max" "$f"; echo "... [truncated $((n-max)) lines — attach full file if needed]"; else cat "$f"; fi
  echo
}
{
echo "=== OpenRoot gh_audit digest $(date -u +%FT%TZ) ==="
echo "report_dir: $DIR"
cap "$DIR/repo_inventory.tsv"   50  "repo inventory (name|default|archived|updated|desc|license)"
cap "$DIR/unmerged_ahead.tsv"   60  "ahead/NCA branches — EYES ONLY, never auto-delete"
cap "$DIR/identical_branches.tsv" 30 "identical branches — CONFIRM=1 delete candidates"
cap "$DIR/stale_branches.tsv"    30 "stale (90d+) branches"
cap "$DIR/closed_unmerged_prs.tsv" 40 "closed-unmerged PRs — resurrection candidates"
cap "$DIR/hygiene_flags.tsv"    40 "hygiene flags (no license/desc)"
echo "-- run log tail (last 25 lines)"
tail -n 25 "$LOG" 2>/dev/null || echo "(no log provided)"
echo
echo "[exit=0]"
} > "$OUT"
# scrub pass — reports shouldn't contain secrets, but verify cheaply
if grep -qE '(ghp_[A-Za-z0-9]{20,}|tskey-auth-[A-Za-z0-9-]+)' "$OUT"; then
  say held "SECRET PATTERN DETECTED in $OUT — do NOT share, scrub first"; exit 1
fi
say banked "digest written: $OUT ($(wc -l < "$OUT") lines, $(du -h "$OUT" | cut -f1))"
say held "attach $OUT to the Lumo chat — do not paste raw terminal transcripts"
printf '[exit=0]\n'
