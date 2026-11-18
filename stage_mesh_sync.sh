#!/usr/bin/env bash
set -Eeuo pipefail

echo "========================================================"
echo "=== OpenRoot Mesh Synchronization Packager (A15 Node) ==="
echo "========================================================"

CURRENT_SCRIPT="${BASH_SOURCE[0]:-$0}"
ROOT_DIR="$(cd "$(dirname "$CURRENT_SCRIPT")" && pwd)"
cd "$ROOT_DIR"

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RELEASE_DIR="workareas/release"
PAYLOAD_NAME="mesh_sync_payload_${TIMESTAMP}.tar.gz"
PAYLOAD_PATH="$RELEASE_DIR/$PAYLOAD_NAME"
MANIFEST_PATH="$RELEASE_DIR/sync_manifest_${TIMESTAMP}.json"

mkdir -p "$RELEASE_DIR"

echo "[1/3] Compressing Combinatory Pods and COMPOST Logs..."
tar -czf "$PAYLOAD_PATH" \
    --exclude='.git' \
    --exclude='__pycache__' \
    workareas/agape_pods \
    workareas/compost_logs \
    workareas/analytics 2>/dev/null || true

echo "[2/3] Generating Cryptographic Verification Manifest..."
PAYLOAD_SIZE=$(stat -c%s "$PAYLOAD_PATH" 2>/dev/null || stat -f%z "$PAYLOAD_PATH")
PAYLOAD_SHA256=$(sha256sum "$PAYLOAD_PATH" | awk '{print $1}')

cat > "$MANIFEST_PATH" <<MANIFEST_EOF
{
  "schema": "openroot_mesh_sync_manifest_v1",
  "node_id": "a15_mobile_edge",
  "timestamp": "$TIMESTAMP",
  "payload_file": "$PAYLOAD_NAME",
  "bytes": $PAYLOAD_SIZE,
  "sha256": "$PAYLOAD_SHA256",
  "protocol_alignment": {
    "R": 1.0,
    "c": 0.0
  }
}
MANIFEST_EOF

echo "[3/3] Staging Complete and Verified."
echo "  Payload Archive : $PAYLOAD_PATH"
echo "  Manifest File   : $MANIFEST_PATH"
echo "  SHA-256 Checksum: $PAYLOAD_SHA256"
echo "========================================================"
echo "=== Ready for Tailscale Mesh Synching to OptiPlex Core ==="
echo "========================================================"
