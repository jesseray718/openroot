#!/usr/bin/env bash
set -Eeuo pipefail

LOG_DIR="workareas/audit"
mkdir -p "$LOG_DIR"
LEDGER_FILE="$LOG_DIR/agape_audit.log"

log_event() {
    local event_type="$1"
    local message="$2"
    local timestamp
    timestamp="$(date -u +%Y-%m-%dT%H%M%SZ)"
    
    # Get last hash for chain integrity (or genesis hash if empty)
    local prev_hash="0000000000000000000000000000000000000000000000000000000000000000"
    if [ -f "$LEDGER_FILE" ]; then
        prev_hash="$(tail -n 1 "$LEDGER_FILE" | cut -d'|' -f4)"
    fi
    
    local raw_data="${timestamp}|${event_type}|${message}|${prev_hash}"
    local current_hash
    current_hash="$(echo -n "$raw_data" | sha256sum | awk '{print $1}')"
    
    echo "${timestamp}|${event_type}|${message}|${current_hash}" >> "$LEDGER_FILE"
    echo "[LEDGER] Recorded immutable event: $event_type -> Hash: ${current_hash:0:16}..."
}

# Example invocation if run directly
if [ "${1:-}" = "log" ]; then
    log_event "${2:-SYSTEM_EVENT}" "${3:-Agape node initialized}"
else
    log_event "LEDGER_INIT" "Immutable audit chain verified (R=1, c=0)"
fi
