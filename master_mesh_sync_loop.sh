#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
CORE_IP="${OPTIPLEX_TAILSCALE_IP:-100.122.169.43}"
SYNC_INTERVAL=60
mkdir -p workareas/compost_logs workareas/release
while true; do
  TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
  echo "[$(date -u +%T)] [SYNC-LOOP] Probing core $CORE_IP"
  if ping -c 1 -W 2 "$CORE_IP" >/dev/null 2>&1; then
    echo "[$(date -u +%T)] [ok] Core online — staging"
    PAYLOAD="workareas/release/mesh_sync_payload_${TIMESTAMP}.tar.gz"
    tar -czf "$PAYLOAD" --exclude='.git' --exclude='__pycache__' \
      workareas/agape_pods workareas/compost_logs workareas/analytics 2>/dev/null || true
    scp -o ConnectTimeout=5 "$PAYLOAD" "jesse@$CORE_IP:/home/jesse/openroot/workareas/release/" >/dev/null 2>&1 \
      && echo "[$(date -u +%T)] [ok] transmitted" \
      || echo "[$(date -u +%T)] [warn] scp failed"
  else
    echo "[$(date -u +%T)] [info] Core offline — holding"
  fi
  sleep "$SYNC_INTERVAL"
done
