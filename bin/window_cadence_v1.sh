#!/usr/bin/env bash
# window_cadence_v1.sh - runs window_loop only when the window CHANGED.
# WINDCADV1 canary. A loop is justified iff marginal output > marginal
# cost; unchanged window sha = rest (near-zero cost).
set -eu
export GIT_PAGER=cat
cd /home/jesse/openroot
STATE=data/.last_window_sha
CUR=$(find context_bridge bin analysis docs workareas \
       -type f -newer data/.window_marker 2>/dev/null | wc -l; \
       find context_bridge bin analysis docs \
       -type f -mmin -1440 -exec sha256sum {} + 2>/dev/null | \
       sha256sum | cut -c1-16)
NEW=$(find context_bridge bin analysis docs -type f -mmin -1440 \
      -exec sha256sum {} + 2>/dev/null | sha256sum | cut -c1-16)
LAST=$(cat "$STATE" 2>/dev/null || echo none)
if [ "$NEW" = "$LAST" ]; then
  echo "[WINDCADV1] window unchanged ($NEW) - loop rests, zero tokens burned"
else
  echo "$NEW" > "$STATE"
  bash bin/window_loop_v1.sh
fi
echo "[exit=0]"
