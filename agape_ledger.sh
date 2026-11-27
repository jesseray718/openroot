#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
LEDGER_FILE="${AGAPE_LEDGER_FILE:-$SCRIPT_DIR/workareas/audit/agape_audit.log}"
GENESIS="0000000000000000000000000000000000000000000000000000000000000000"

verify_chain() {
    local line prefix timestamp rest event digest actual previous="$GENESIS" count=0
    while :; do
        line=""
        if IFS= read -r line; then
            :
        elif [[ -n "$line" ]]; then
            echo "[error] incomplete ledger line" >&2
            return 1
        else
            break
        fi

        if [[ "$line" != *"|"*"|"*"|"* ]]; then
            echo "[error] malformed ledger line $((count + 1))" >&2
            return 1
        fi
        digest="${line##*|}"
        prefix="${line%|*}"
        timestamp="${prefix%%|*}"
        rest="${prefix#*|}"
        event="${rest%%|*}"
        if [[ -z "$timestamp" || -z "$event" || ! "$digest" =~ ^[0-9a-f]{64}$ ]]; then
            echo "[error] malformed ledger line $((count + 1))" >&2
            return 1
        fi
        actual="$(printf '%s' "$prefix|$previous" | sha256sum)"
        actual="${actual%% *}"
        if [[ "$actual" != "$digest" ]]; then
            echo "[error] hash mismatch at ledger line $((count + 1))" >&2
            return 1
        fi
        previous="$digest"
        count=$((count + 1))
    done < "$LEDGER_FILE"

    if (( count == 0 )); then
        echo "[error] ledger is empty" >&2
        return 1
    fi
    LAST_HASH="$previous"
    ENTRY_COUNT="$count"
}

log_event() {
    local event="$1" message="$2" timestamp previous="$GENESIS" digest
    if [[ -z "$event" || "$event" == *"|"* || "$event" == *$'\n'* ||
          "$event" == *$'\r'* || "$message" == *$'\n'* || "$message" == *$'\r'* ]]; then
        echo "[error] event must be nonempty without delimiters; message must be one line" >&2
        return 1
    fi
    if [[ -s "$LEDGER_FILE" ]]; then
        verify_chain
        previous="$LAST_HASH"
    fi
    timestamp="$(date -u +%Y-%m-%dT%H%M%SZ)"
    digest="$(printf '%s' "$timestamp|$event|$message|$previous" | sha256sum)"
    digest="${digest%% *}"
    printf '%s|%s|%s|%s\n' "$timestamp" "$event" "$message" "$digest" >> "$LEDGER_FILE"
    printf '[LEDGER] Recorded event: %s -> Hash: %.16s...\n' "$event" "$digest"
}

command -v flock >/dev/null || { echo "[error] flock is required" >&2; exit 1; }
case "${1:-log}" in
    log)
        (( $# <= 3 )) || { echo "[error] usage: $0 log [event] [message]" >&2; exit 2; }
        mkdir -p -- "$(dirname -- "$LEDGER_FILE")"
        exec {lock_fd}>"$LEDGER_FILE.lock"
        flock -x "$lock_fd"
        if (( $# == 0 )); then
            log_event "LEDGER_INIT" "Agape ledger initialized"
        else
            log_event "${2:-SYSTEM_EVENT}" "${3:-Agape node initialized}"
        fi
        ;;
    verify)
        (( $# == 1 )) || { echo "[error] usage: $0 verify" >&2; exit 2; }
        [[ -f "$LEDGER_FILE" ]] || { echo "[error] ledger not found" >&2; exit 1; }
        exec {lock_fd}>"$LEDGER_FILE.lock"
        flock -s "$lock_fd"
        verify_chain
        printf '[ok] chain verified: %s entries\n' "$ENTRY_COUNT"
        ;;
    *)
        echo "[error] usage: $0 {log [event] [message]|verify}" >&2
        exit 2
        ;;
esac
