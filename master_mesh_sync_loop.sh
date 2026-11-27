#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"

: "${OPTIPLEX_TAILSCALE_IP:?Set OPTIPLEX_TAILSCALE_IP to the destination host}"
: "${MESH_SSH_USER:?Set MESH_SSH_USER to the destination account}"
: "${MESH_REMOTE_DIR:?Set MESH_REMOTE_DIR to the destination directory}"
SYNC_INTERVAL="${SYNC_INTERVAL:-60}"
MESH_PAYLOAD_KEEP="${MESH_PAYLOAD_KEEP:-10}"
if [[ ! "$SYNC_INTERVAL" =~ ^[1-9][0-9]{0,5}$ ||
      ! "$MESH_PAYLOAD_KEEP" =~ ^[1-9][0-9]{0,5}$ ]]; then
  echo "[error] SYNC_INTERVAL and MESH_PAYLOAD_KEEP must be positive integers" >&2
  exit 2
fi

mkdir -p workareas/release
shopt -s nullglob
while true; do
  if [[ ! -d workareas/mesh_export_redacted ]]; then
    echo "[warn] No operator-prepared export directory available"
  else
    timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
    payload="$(mktemp "workareas/release/mesh_sync_payload_${timestamp}_XXXXXXXX.tar.gz")"
    if tar -czf "$payload" --exclude='.git' --exclude='__pycache__' \
      workareas/mesh_export_redacted; then
      if scp -o BatchMode=yes -o ConnectTimeout=5 "$payload" \
        "${MESH_SSH_USER}@${OPTIPLEX_TAILSCALE_IP}:${MESH_REMOTE_DIR}"; then
        echo "[ok] transmitted"
      else
        echo "[warn] transfer failed" >&2
      fi
    else
      echo "[error] payload creation failed" >&2
      rm -f -- "$payload"
    fi
  fi
  mapfile -d '' -t payloads < <(
    find workareas/release -maxdepth 1 -type f -name 'mesh_sync_payload_*.tar.gz' \
      -printf '%T@ %p\0' | sort -z -n
  )
  while (( ${#payloads[@]} > MESH_PAYLOAD_KEEP )); do
    rm -f -- "${payloads[0]#* }"
    payloads=("${payloads[@]:1}")
  done
  sleep "$SYNC_INTERVAL"
done
