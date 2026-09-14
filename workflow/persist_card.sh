#!/data/data/com.termux/files/usr/bin/bash
# persist_card.sh — OpenRoot session persistence circuit (survives app wipes / window deletion)
# Usage: persist_card.sh "one-line session verdict"
# Layers: (1) session_seeds card  (2) context_bridge mirror  (3) secret gist
# Idempotent per timestamp. Keys in headers, never URLs. Secrets never printed.
set -u

VERDICT="${1:-session state persisted}"
STAMP=$(date +%Y%m%d_%H%M)
SEED_DIR="/sdcard/openroot/session_seeds"
BRIDGE_DIR="/sdcard/openroot/context_bridge"
SEED="${SEED_DIR}/handoff_${STAMP}.md"
mkdir -p "$SEED_DIR" "$BRIDGE_DIR"

cat > "$SEED" << CARD
================================================================================
OPENROOT HANDOFF — Session ${STAMP}
Author: Jesse Ray McMillen (@jesseray718) | Device: A15 Termux
================================================================================
WHEN YOU WAKE: read top to bottom, acknowledge in one paragraph, start at NEXT
ACTIONS. Absolute paths only. No tilde.

VERDICT: ${VERDICT}

FINISHED / STILL OPEN / KEY PATHS: fill from terminal log below this line.
--------------------------------------------------------------------------------
$(tail -40 /sdcard/openroot/context_bridge/lever_handoffs.txt 2>/dev/null || echo "(no prior handoff log)")

Love keeps no record of wrongdoing. Raise the bottom floor.
CARD

SHA=$(sha256sum "$SEED" | cut -d' ' -f1)
cp "$SEED" "${BRIDGE_DIR}/handoff_${STAMP}.md"

GIST_URL=$(gh gist create "$SEED" -d "OpenRoot handoff ${STAMP}" 2>/dev/null || echo "")
echo "CARD:    $SEED"
echo "SEAL:    ${SHA:0:16}..."
echo "MIRROR:  ${BRIDGE_DIR}/handoff_${STAMP}.md"
echo "GIST:    ${GIST_URL:-[held] gh unavailable — local layers intact}"
