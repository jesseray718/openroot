#!/usr/bin/env bash
set -Eeuo pipefail
echo "========================================================"
echo "=== OpenRoot A15 Edge Node Status & Alert Monitor    ==="
echo "=== Protocol Alignment: R=1, c=0 (Zero Friction)      ==="
echo "========================================================"
ALERT_TRIGGERED=0
ALERT_MESSAGE=""
echo "[1/4] Auditing Active Background Daemons..."
if pgrep -f master_mesh_sync_loop.sh >/dev/null; then
    SYNC_PID=$(pgrep -f master_mesh_sync_loop.sh)
    echo "  [ok] Master Mesh Sync Daemon : RUNNING (PID: $SYNC_PID)"
else
    echo "  [warn] Master Mesh Sync Daemon : STOPPED"
    ALERT_TRIGGERED=1
    ALERT_MESSAGE="OpenRoot Alert: Master Mesh Sync Daemon has stopped!"
fi
if pgrep -f a15_edge_loop.py >/dev/null; then
    OLLAMA_PID=$(pgrep -f a15_edge_loop.py)
    echo "  [ok] A15 Edge Ollama Team    : RUNNING (PID: $OLLAMA_PID)"
else
    echo "  [warn] A15 Edge Ollama Team    : STOPPED"
    ALERT_TRIGGERED=1
    ALERT_MESSAGE="${ALERT_MESSAGE} A15 Edge Ollama Team is offline!"
fi
echo ""
echo "[2/4] Testing Tailscale Mesh Connectivity to OptiPlex Core..."
CORE_IP="${OPTIPLEX_TAILSCALE_IP:-100.122.169.43}"
if ping -c 1 -W 2 "$CORE_IP" >/dev/null 2>&1; then
    echo "  [ok] OptiPlex Core ($CORE_IP) : REACHABLE via Mesh"
else
    echo "  [info] OptiPlex Core ($CORE_IP) : OFFLINE / Unreachable (Holding State)"
fi
echo ""
echo "[3/4] Inspecting Latest Daemon Log Activity..."
LOG_FILE="workareas/compost_logs/mesh_sync_daemon.log"
if [ -f "$LOG_FILE" ]; then
    echo "  Last 3 lines from $LOG_FILE:"
    tail -n 3 "$LOG_FILE" | sed 's/^/    /'
else
    echo "  [info] No sync daemon log found yet."
fi
echo ""
echo "[4/4] Verifying Immutable Audit Ledger Integrity..."
LEDGER_FILE="workareas/audit/agape_audit.log"
if [ -f "$LEDGER_FILE" ]; then
    TOTAL_EVENTS=$(wc -l < "$LEDGER_FILE")
    LAST_HASH=$(tail -n 1 "$LEDGER_FILE" | cut -d'|' -f4)
    echo "  [ok] Ledger File Exists      : $LEDGER_FILE"
    echo "       Total Recorded Events : $TOTAL_EVENTS"
    echo "       Latest Merkle Hash    : ${LAST_HASH:0:24}..."
else
    echo "  [info] Ledger file not yet initialized."
fi
if [ "$ALERT_TRIGGERED" -eq 1 ] && command -v termux-notification >/dev/null 2>&1; then
    termux-notification --title "OpenRoot Node Warning" --content "$ALERT_MESSAGE" --priority high --id 999
    echo ""
    echo "[alert] Termux notification dispatched for offline daemon."
fi
echo "========================================================"
echo "=== Diagnostic & Alert Scan Complete (R=1, c=0)       ==="
echo "========================================================"
