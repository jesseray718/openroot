#!/data/data/com.termux/files/usr/bin/bash
# OpenRoot Termux:API monitor — device health for H-003 / PoPW / Kai RAG
set -euo pipefail
BAT_JSON=$(termux-battery-status 2>/dev/null || echo '{"percentage":0,"plugged":"unknown","error":"termux-api missing"}')
STORAGE_PCT=$(df /data 2>/dev/null | awk 'NR==2 {print $5}' || echo "N/A")
TIMESTAMP=$(date -Iseconds)
jq -n \
  --argjson battery "$BAT_JSON" \
  --arg storage "$STORAGE_PCT" \
  --arg ts "$TIMESTAMP" \
  --arg node "openroot-ws" \
  --arg sys "H-003 thermal + PoPW + UNE" \
  '{timestamp:$ts, node:$node, system:$sys, battery:$battery, storage_used:$storage}'
