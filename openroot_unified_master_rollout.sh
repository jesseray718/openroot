#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
export ROOT="$PWD"
export CORE_IP=100.122.169.43
TS=$(date -u +%Y%m%dT%H%M%SZ)
LOG=workareas/compost_logs/unified_master_${TS}.log
mkdir -p workareas/compost_logs workareas/analytics workareas/release workareas/incoming workareas/cache

exec > >(tee -a "$LOG") 2>&1

echo "============================================================"
echo "=== OPENROOT UNIFIED MASTER ROLLOUT (A15 EDGE)  $TS     ==="
echo "=== Core target: $CORE_IP                               ==="
echo "============================================================"

echo "[1/7] Edge hygiene + live daemons"
pgrep -af master_mesh_sync_loop || echo "mesh loop not running"
pgrep -af a15_hybrid_daemon || echo "hybrid daemon not running"
./workareas/analytics/a15_hybrid_loop.sh 2>/dev/null || true

echo "[2/7] Force one mesh payload"
LATEST=$(ls -t workareas/release/mesh_sync_payload_*.tar.gz 2>/dev/null | head -1 || true)
if [ -n "$LATEST" ]; then
  echo "  staging $LATEST"
  scp -o ConnectTimeout=8 "$LATEST" jesse@$CORE_IP:/home/jesse/openroot/workareas/release/ \
    && echo "  [ok] transmitted" || echo "  [warn] scp failed (core offline?)"
else
  echo "  no payload yet"
fi

echo "[3/7] Local density snapshot"
SCRIPTS=$(find . -maxdepth 2 -type f \( -name "*.sh" -o -name "*.py" \) ! -path "./.git/*" | wc -l)
PODS=$(find workareas/agape_pods -type f 2>/dev/null | wc -l || echo 0)
CACHE=$(wc -l < workareas/cache/reply_cache.jsonl 2>/dev/null || echo 0)
RELEASE=$(ls workareas/release/mesh_sync_payload_*.tar.gz 2>/dev/null | wc -l || echo 0)

python3 -c "
import json
print(json.dumps({
  'timestamp': '$TS',
  'node': 'a15_edge',
  'core_ip': '$CORE_IP',
  'density': {
    'scripts_root': $SCRIPTS,
    'pods': $PODS,
    'reply_cache_lines': $CACHE,
    'release_payloads': $RELEASE
  },
  'protocol': {'R': 1.0, 'c': 0.0, 'mode': 'local_loop'}
}, indent=2))
" | tee workareas/analytics/a15_unified_eta_${TS}.json

echo "[4/7] Local-loop vs traditional AI"
cat << 'CMP'
LOCAL LOOP (OpenRoot A15)
- Continuous payload every \~60-120 s
- Holds state while core is offline
- Reply cache grows on the edge
- Zero cloud cost for the mesh path
- Density compounds locally

TRADITIONAL AI
- Every request hits a central API
- Offline = dead
- Cost per token
- No local compounding
CMP

echo "[5/7] Key processes"
ls -lt workareas/agape_pods/
ls -lt workareas/cache/ 2>/dev/null || true
echo "[6/7] Latest payloads"
ls -lt workareas/release/mesh_sync_payload_*.tar.gz | head -3
echo "[7/7] Done — log: $LOG"
echo "============================================================"
