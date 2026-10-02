#!/data/data/com.termux/files/usr/bin/bash
# [HIVESHIV1] Termux hive — local lattice first, OptiPlex spine fallback
# SPDX-License-Identifier: GPL-3.0-only
# Usage: bash bin/hive.sh "your question"
set -euo pipefail

ROOT="/data/data/com.termux/files/home/openroot"
QUERY="${*:-}"
STAMP="$(date -u +%Y%m%d_%H%M%S)"
OUTDIR="${ROOT}/context_bridge/hive_runs"
mkdir -p "${OUTDIR}"
OUTFILE="${OUTDIR}/hive_${STAMP}.txt"

if [ -z "${QUERY}" ]; then
  echo "Usage: bash bin/hive.sh \"your question\""
  exit 1
fi

cd "${ROOT}"

if [ -f "${ROOT}/nanobot_lattice.py" ]; then
  echo "[HIVESHIV1] local fractal lattice path..."
  python3 nanobot_lattice.py "${QUERY}" | tee "${OUTFILE}"
else
  echo "[HIVESHIV1] local lattice absent — delegating to OptiPlex solve.py spine..."
  QUERY_Q=$(printf '%q' "${QUERY}")
  ssh jesse@100.122.169.43 "python3 /home/jesse/openroot/bin/solve.py ${QUERY_Q}" | tee "${OUTFILE}" \
    || { echo "[held] remote delegation failed — check Tailscale"; exit 1; }
fi

echo "[banked] Result saved to: ${OUTFILE}"
echo "[exit=0]"
