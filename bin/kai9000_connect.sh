#!/usr/bin/env bash
# Kai9000 → OptiPlex connection point
# Run this FROM Kai9000 (Alpine sandbox on A15) to bootstrap the OpenRoot connection.
set -eu

OPTIPLEX_IP="${OPTIPLEX_IP:-${OPENROOT_HUB}}"
OPTIPLEX_USER="${OPTIPLEX_USER:-${OPENROOT_USER}}"
OPENROOT="/home/${OPENROOT_USER}/openroot"

echo "[gate] KAI9000 → OPTIPLEX CONNECT $(date -u +%FT%TZ)"
echo

# 1. Verify Tailscale reachability
echo "[gate] STAGE 1 — verify Tailscale path to OptiPlex"
if ping -c 1 -W 2 "$OPTIPLEX_IP" >/dev/null 2>&1; then
    echo "  [banked] OptiPlex reachable at $OPTIPLEX_IP"
else
    echo "  [held] OptiPlex unreachable — check Tailscale on both ends"
    exit 1
fi
echo

# 2. Test SSH
echo "[gate] STAGE 2 — test SSH to OptiPlex"
if ssh -o BatchMode=yes -o ConnectTimeout=5 "$OPTIPLEX_USER@$OPTIPLEX_IP" 'echo ok' 2>/dev/null | grep -q ok; then
    echo "  [banked] SSH key auth working"
else
    echo "  [held] SSH key auth failed — copy your key:"
    echo "    ssh-copy-id $OPTIPLEX_USER@$OPTIPLEX_IP"
    exit 1
fi
echo

# 3. Pull boot context from OptiPlex
echo "[gate] STAGE 3 — pull OpenRoot boot context from OptiPlex"
ssh "$OPTIPLEX_USER@$OPTIPLEX_IP" "bash $OPENROOT/bin/boot_context.sh" 2>&1 | head -50
echo

# 4. Sync a model from OptiPlex to Kai9000 (optional — only if you want local inference on A15)
echo "[gate] STAGE 4 — model sync (optional, set SYNC_MODEL env var)"
if [ -n "${SYNC_MODEL:-}" ]; then
    echo "  syncing model: $SYNC_MODEL"
    # Models are large; this uses rsync with progress + resume
    rsync -avz --progress \
        "$OPTIPLEX_USER@$OPTIPLEX_IP:~/.ollama/models/" \
        ~/.ollama/models/ 2>&1 | tail -10
    echo "  [banked] model synced"
else
    echo "  [held] set SYNC_MODEL=1 to sync, or specify model name"
fi
echo

# 5. Make Kai9000 a thin client — call cloud_router on OptiPlex
echo "[gate] STAGE 5 — thin client wrapper"
cat > ~/openroot_thin.sh <<'THINSH'
#!/usr/bin/env sh
# Thin client: forwards any OpenRoot command to OptiPlex via SSH
# Usage: openroot_thin.sh "<command> <args>"
# Example: openroot_thin.sh "python3 bin/cloud_router_v2.py --prompt 'test' --max-tokens 50"
OPTIPLEX_IP="${OPTIPLEX_IP:-${OPENROOT_HUB}}"
OPTIPLEX_USER="${OPTIPLEX_USER:-${OPENROOT_USER}}"
ssh "$OPTIPLEX_USER@$OPTIPLEX_IP" "cd /home/${OPENROOT_USER}/openroot && $*"
THINSH
chmod +x ~/openroot_thin.sh
echo "  [banked] thin client installed at ~/openroot_thin.sh"
echo

echo "[gate] STAGE 6 — test thin client"
~/openroot_thin.sh "python3 -c 'import json,hashlib; r=json.load(open(\"genesis/receipt_v1.json\")); print(\"genesis v1.0:\", hashlib.sha256(json.dumps(r,sort_keys=True,separators=(\",\",\":\"),ensure_ascii=False).encode()).hexdigest()[:32]+\"...\")'" 2>&1
echo

echo "===================================================="
echo "KAI9000 CONNECTED TO OPENROOT"
echo "===================================================="
echo
echo "You can now run OpenRoot commands from Kai9000:"
echo "  ~/openroot_thin.sh 'python3 bin/cloud_router_v2.py --prompt \"hello\" --max-tokens 50'"
echo "  ~/openroot_thin.sh 'python3 bin/pod_loader_v1.py list'"
echo "  ~/openroot_thin.sh 'bash bin/boot_context.sh'"
echo
echo "Or sync a model for offline inference on A15:"
echo "  SYNC_MODEL=1 bash bin/kai9000_connect.sh"
echo
echo "[banked] Kai9000 connection complete"
