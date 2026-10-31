# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env bash
# kai_bridge_poller_v1.sh — ingest kai_inbox files into lesson pods, receipt to kai_outbox
# Kanban: kai_inbox (in) -> pods_garden (work) -> kai_outbox (receipt). Idempotent.
set -u
export GIT_PAGER=cat PYTHONDONTWRITEBYTECODE=1
cd /home/${OPENROOT_USER}/openroot
IN=context_bridge/kai_inbox
OUT=context_bridge/kai_outbox
mkdir -p "$IN" "$OUT" "pods_garden"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
DONE="$IN/.done"; mkdir -p "$DONE"
COUNT=0
for f in "$IN"/*; do
  [ -f "$f" ] || continue
  case "$f" in */.*|.done*) continue;; esac
  NAME=$(basename "$f")
  SLUG=$(echo "$NAME" | tr " .:" "---" | tr -c "a-z0-9-" "-" | cut -c1-40)
  OUTLOG="$OUT/receipt_${SLUG}_${STAMP}.md"
  {
    echo "# kai bridge receipt: $NAME"
    echo "timestamp: $STAMP"
    python3 bin/pod_pipeline_v1.py ingest "kai-imports" "$f" 2>&1
    echo "ingested_from: $f"
  } > "$OUTLOG" 2>&1
  mv "$f" "$DONE/"
  COUNT=$((COUNT+1))
done
if [ "$COUNT" -gt 0 ]; then
  echo "[banked] kai bridge: $COUNT file(s) processed $STAMP" >> "$OUT/bridge.log"
  git add context_bridge/kai_outbox 2>/dev/null; git add context_bridge/kai_inbox/*.md context_bridge/kai_inbox/*.txt 2>/dev/null || true
  git commit -m "kai bridge: $COUNT artifact(s) ingested, receipts banked $STAMP" 2>/dev/null || true
fi
exit 0
