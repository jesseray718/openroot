#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# hygiene_fix_driver_v3.sh — data-driven license/desc fixes from gh_audit report
# v3 rebuild: v2 paste was garbled by interleaved job notification, state unknown — regenerated clean.
# Selects newest COMPLETE report (non-empty hygiene_flags.tsv); GH_AUDIT_BASE overrides.
# Dry-run default. CONFIRM=1 pushes LICENSE files via contents API.
# [canary] hygiene_fix_driver_v3_CANARY_MARKER
set -euo pipefail
export GIT_PAGER=cat PAGER=cat
[ "$(hostname)" = "optiplex3060" ] || { echo "[held] run on optiplex3060, not $(hostname)"; exit 1; }
command -v gh >/dev/null || { echo "[held] gh CLI missing"; exit 1; }
CONFIRM="${CONFIRM:-0}"
OWNER="jesseray718"
say(){ printf '[%s] %s\n' "$1" "$2"; }

if [ -n "${GH_AUDIT_BASE:-}" ]; then
  BASE="$GH_AUDIT_BASE"
else
  BASE=""
  for d in $(ls -1dt "$HOME"/openroot/reports/gh_audit_* 2>/dev/null); do
    if [ -s "$d/hygiene_flags.tsv" ]; then BASE="$d"; break; fi
  done
fi
[ -n "${BASE:-}" ] && [ -s "$BASE/hygiene_flags.tsv" ] || { echo "[held] no COMPLETE audit report (non-empty hygiene_flags.tsv)"; exit 1; }

DEFAULT_LICENSE="gpl-3.0"
declare -A LICENSE_OVERRIDE=( )  # ["doc-repo"]="cc-by-sa-4.0"
declare -A DESCRIPTIONS=( )      # ["agapenet"]="Negentropic mesh"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT

say gate "source $BASE CONFIRM=$CONFIRM"
NO_LIC=$(awk -F'|' '$2=="NO_LICENSE"{print $1}' "$BASE/hygiene_flags.tsv" | sort -u)
NO_DESC=$(awk -F'|' '$2=="NO_DESC"{print $1}' "$BASE/hygiene_flags.tsv" | sort -u)
NL=$(echo "$NO_LIC" | grep -c . || true); ND=$(echo "$NO_DESC" | grep -c . || true)
say banked "flags: no-license=$NL no-desc=$ND"

while IFS= read -r R; do
  [ -z "$R" ] && continue
  L="${LICENSE_OVERRIDE[$R]:-$DEFAULT_LICENSE}"
  gh api "repos/$OWNER/$R/contents/LICENSE" >/dev/null 2>&1 && { say banked "LICENSE present: $R"; continue; }
  gh api "/licenses/$L" --jq '.content' | base64 -d > "$WORK/LICENSE" || { say held "no text for $L ($R)"; continue; }
  if [ "$CONFIRM" = "1" ]; then
    gh api -X PUT "repos/$OWNER/$R/contents/LICENSE" \
      -f message="Add $L (SPDX) — hygiene_fix_driver_v3" \
      -f content="$(base64 -w0 "$WORK/LICENSE")" >/dev/null \
      && say banked "licensed $R <- $L" || say held "license push failed $R"
  else
    say held "DRY RUN: would push $L ($(wc -c < "$WORK/LICENSE") bytes) -> $R/LICENSE"
  fi
done <<< "$NO_LIC"

while IFS= read -r R; do
  [ -z "$R" ] && continue
  D="${DESCRIPTIONS[$R]:-}"
  if [ -z "$D" ]; then say held "no description drafted: $R — fill DESCRIPTIONS[] and re-run"
  elif [ "$CONFIRM" = "1" ]; then
    gh repo edit -R "$OWNER/$R" --description "$D" >/dev/null && say banked "described $R"
  else
    say held "DRY RUN: would set desc on $R: $D"
  fi
done <<< "$NO_DESC"
say banked "complete — review above, then CONFIRM=1 to apply"
printf '[exit=0]\n'
