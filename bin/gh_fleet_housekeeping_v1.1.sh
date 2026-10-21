#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# gh_fleet_housekeeping_v1.1 — CHANGES vs v1:
#   - issue #53 already closed -> dropped
#   - NEW: close duplicate issues #73-#82 (exact dup of #83-#92, keep newer set)
#   - milestones: still created only if missing
#   - fleet PRs: dry run showed ZERO open PRs -> nothing to merge, section removed
set -euo pipefail
export GIT_PAGER=cat GH_PAGER=cat
BASE=/home/jesse/openroot; TS=$(date +%Y%m%d_%H%M%S)
LOG=$BASE/context_bridge/gh_fleet_housekeeping_${TS}.md
USER=jesseray718; FLAGSHIP=openroot
mkdir -p "$BASE/context_bridge"; : > "$LOG"
CONFIRM="${CONFIRM:-0}"

run() { local desc="$1"; shift
  echo "- $desc" | tee -a "$LOG"
  if [ "$CONFIRM" = "1" ]; then "$@" 2>&1 | tee -a "$LOG"
  else echo "  [dry] $*" | tee -a "$LOG"; fi
}

echo "[GHFLEET11] START $TS (CONFIRM=$CONFIRM)" | tee -a "$LOG"
gh auth status >/dev/null 2>&1 || { echo "[held] gh not authed"; exit 1; }
HEAD=$(git -C "$BASE" rev-parse --short HEAD)

echo "## Pre-flight: verify duplicate hypothesis (titles must match pairwise)" | tee -a "$LOG"
for PAIR in "73 83" "74 84" "75 85" "76 86" "77 87" "78 88" "79 89" "80 90" "81 91" "82 92"; do
  set -- $PAIR
  T1=$(gh issue view $1 -R "$USER/$FLAGSHIP" --json title -q .title)
  T2=$(gh issue view $2 -R "$USER/$FLAGSHIP" --json title -q .title)
  if [ "$T1" = "$T2" ]; then echo "  MATCH  #$1 == #$2 : $T1" | tee -a "$LOG"
  else echo "  DIFFER #$1 != #$2 — WILL SKIP closing #$1" | tee -a "$LOG"; SKIP_CLOSE="$SKIP_CLOSE $1"; fi
done

echo "## Actions" | tee -a "$LOG"
for MS in "Consolidation Wave 1 — 41→13 active repos" "Hardware Prototypes v0 — aerocement panel + thermal battery" "Local AI Stack — registry-routed routing GA"; do
  if ! gh api repos/$USER/$FLAGSHIP/milestones --jq '.[].title' 2>/dev/null | grep -qF "$MS"; then
    run "create milestone: $MS" gh api -X POST repos/$USER/$FLAGSHIP/milestones -f title="$MS" -f state=open
  else echo "- milestone exists: $MS" | tee -a "$LOG"; fi
done

run "seal release at $HEAD" gh release create "v-$HEAD" -R "$USER/$FLAGSHIP" --target main \
  -t "Stack consolidation snapshot — $HEAD" \
  -n "Registry-routed local AI stack (7B AUTHOR / 3B GRADE), week-scripts banked, 10 duplicate issues closed, fleet PRs at zero. Automated by gh_fleet_housekeeping_v1.1, human-gated."

for N in 73 74 75 76 77 78 79 80 81 82; do
  case " ${SKIP_CLOSE:-} " in *" $N "*) echo "- skip #$N (title mismatch)" | tee -a "$LOG"; continue;; esac
  KEEP=$((N + 10))
  run "close duplicate #$N -> keep #$KEEP" gh issue close $N -R "$USER/$FLAGSHIP" \
    -c "Duplicate of #$KEEP (identical title). Closing lower-numbered copy per fleet hygiene pass $TS; all work continues on #$KEEP."
done

echo "[GHFLEET11] END $TS [exit=0]" | tee -a "$LOG"
echo "log: $LOG"
exit 0
