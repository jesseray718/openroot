#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Adds missing licenses + descriptions flagged by audit
set -uo pipefail
OWNER=jesseray718

# Example repo fixes (populate from hygiene_flags.tsv)
declare -A LICENSES=(["agape-ipfs"]="mit" ["wisdom-scaffold"]="gpl-3.0")
declare -A DESCRS=(["agapenet"]="Negentropic mesh for Agape energy" ["agape-cascade"]="Percolation economics simulator")

for REPO in "${!LICENSES[@]}"; do
  echo "[update] Adding license to $REPO"
  gh repo edit -R "$OWNER/$REPO" --add-license "${LICENSES[$REPO]}" 2>/dev/null || echo "[warn] license update failed $REPO"
done

for REPO in "${!DESCRS[@]}"; do
  echo "[update] Adding description to $REPO"
  gh repo edit -R "$OWNER/$REPO" --description "${DESCRS[$REPO]}" 2>/dev/null || echo "[warn] desc update failed $REPO"
done

echo "[banked] hygiene fixes complete"
printf '[exit=0]\n'
