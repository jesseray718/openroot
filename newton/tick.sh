#!/usr/bin/env bash
# newton tick — append one hash-linked block
# FIXED: grep hash: of previous block (was prev: — fan-link bug F-NEWTON-BROKEN-LINK)
set -euo pipefail
CHAIN="$(cd "$(dirname "$0")" && pwd)/chain"; mkdir -p "$CHAIN"
LAST="$(ls -1 "$CHAIN" 2>/dev/null | sort | tail -n1 || true)"
PREV="genesis"
[ -n "$LAST" ] && PREV="$(sed -n 's/^hash: *//p' "$CHAIN/$LAST" | tail -n1)"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"; PAYLOAD="tick"
H="$(printf '%s|%s|%s' "$PREV" "$TS" "$PAYLOAD" | sha256sum | cut -d' ' -f1)"
{ echo "ts: $TS"; echo "prev: $PREV"; echo "payload: $PAYLOAD"; echo "hash: $H"; } > "$CHAIN/$TS"
echo "newton block $TS (prev=${PREV:0:12})"
