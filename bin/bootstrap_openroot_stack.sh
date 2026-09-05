#!/usr/bin/env bash
# SSH pane only. Copy this file onto the box then run it.
# Does not clone. Does not wipe. Does not start 7B.
set -euo pipefail
WISDOM=/home/jesse/wisdom-scaffold
SRC=${1:-}
if [[ -z "${SRC}" ]]; then
  echo "usage: bootstrap_openroot_stack.sh /absolute/path/to/wisdom-pipeline"
  exit 2
fi
[[ "${SRC}" == /* ]] || { echo "SRC must be absolute"; exit 2; }
[[ -d "${SRC}" ]] || { echo "missing ${SRC}"; exit 2; }
mkdir -p \
  "${WISDOM}/handbook" \
  "${WISDOM}/scripts/rag" \
  "${WISDOM}/scripts/unification" \
  "${WISDOM}/data" \
  /home/jesse/openroot/bin
cp -a "${SRC}/handbook/." "${WISDOM}/handbook/"
cp -a "${SRC}/scripts/rag/." "${WISDOM}/scripts/rag/"
cp -a "${SRC}/scripts/unification/." "${WISDOM}/scripts/unification/"
if [[ -f "${SRC}/bin/bootstrap_openroot_stack.sh" ]]; then
  cp -a "${SRC}/bin/." /home/jesse/openroot/bin/
fi
chmod 0755 \
  "${WISDOM}/handbook/"*.py \
  "${WISDOM}/scripts/rag/"*.py \
  "${WISDOM}/scripts/unification/"*.py \
  /home/jesse/openroot/bin/*.sh 2>/dev/null || true
echo "landed into ${WISDOM}"
python3 "${WISDOM}/handbook/audit_pipeline.py" || true
python3 "${WISDOM}/scripts/rag/fts5_ensure.py" --ingest --limit-files 80
python3 "${WISDOM}/scripts/rag/hybrid_rag_router.py" --mode fts "fts5 hybrid N14 need_gate"
echo "bootstrap done. do not run nomic indexer in the same breath."
