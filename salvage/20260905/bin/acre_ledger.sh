#!/data/data/com.termux/files/usr/bin/bash
set -e

LEDGER_FILE="${1:-$HOME/projects/openroot/acre/ledger.jsonl}"
mkdir -p "$(dirname "$LEDGER_FILE")"

if [[ ! -f "$LEDGER_FILE" ]]; then
    GENESIS_HASH=$(echo "OpenRoot ACRE Genesis $(date -u +%Y-%m-%dT%H:%M:%SZ)" | sha256sum | cut -d' ' -f1)
    echo "{\"entry_id\":\"genesis\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"hash\":\"$GENESIS_HASH\",\"work_type\":\"system_init\",\"energy_joules\":0,\"previous_hash\":\"0000000000000000\",\"validators\":[\"system\",\"system\"]}" >> "$LEDGER_FILE"
    echo "ACRE Ledger initialized. Genesis: $GENESIS_HASH"
    echo "$GENESIS_HASH" | termux-clipboard-set
else
    LAST_HASH=$(tail -1 "$LEDGER_FILE" | grep -o '"hash":"[^"]*' | cut -d'"' -f4)
    echo "ACRE Ledger exists. Last entry hash: $LAST_HASH"
fi
