#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -Eeuo pipefail
IFS=$'\n\t'

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIVE_ROOT="${OPENROOT_LIVE_ROOT:-$ROOT}"
DB="${OPENROOT_ROUTE_CACHE_DB:-$LIVE_ROOT/data/route_cache.db}"
QUERY="${1:-read-only OpenRoot route cache probe}"
KEY="ce678d1529540ee80d86348a813fcb331177e3a9b953752684e5a79eefc45ef9"

echo "=== SOURCE SYNTAX ==="
python3 -m py_compile \
  "$ROOT/bin/turing_tidbits_v1.py" \
  "$ROOT/bin/tidbit_registry_v1.py" \
  "$ROOT/bin/route_promotion_plan_v1.py" \
  "$ROOT/bin/router_cache_probe_v1.py" \
  "$ROOT/bin/router_cache_probe_v2.py" \
  "$ROOT/bin/smart_router.py" \
  "$ROOT/bin/cache_pathway_orchestrator_v1.py"

bash -n "$ROOT/bin/offline_route_cache_v1.sh"

echo "syntax=PASS"

echo
echo "=== SEALED RECEIPTS ==="
while IFS= read -r receipt; do
  [[ -n "$receipt" ]] || continue
  if [[ -f "$receipt.sha256" ]]; then
    (
      cd "$(dirname "$receipt")"
      sha256sum -c "$(basename "$receipt").sha256"
    )
  fi
done < <(
  find "$ROOT/examples/l0_cached_pathway/receipts" \
    -maxdepth 1 \
    -type f \
    ! -name '*.sha256' \
    -print \
    | sort
)

echo
echo "=== LIVE CACHE CHECK ==="
test -f "$DB"
sqlite3 "$DB" 'PRAGMA quick_check;' | grep -qx 'ok'

ROW="$(sqlite3 -noheader "$DB" \
  "SELECT COUNT(*) FROM route_cache WHERE key='$KEY';")"

test "$ROW" = "1"

sqlite3 -header -column "$DB" \
  "SELECT key, query, route, model, hits, length(response) AS response_chars,
          length(provenance) AS provenance_chars, ts
     FROM route_cache
    WHERE key='$KEY';"

echo
echo "=== EXACT PROBE ==="
test -f "$LIVE_ROOT/bin/router_cache_probe_v2.py"
OPENROOT_HOME="$LIVE_ROOT" \
  python3 "$LIVE_ROOT/bin/router_cache_probe_v2.py" "$QUERY"

echo
echo "=== DECLARED LIMIT ==="
echo "L0_EXACT_REUSE=ACTIVE"
echo "L1_FTS_SEMANTIC_REUSE=HELD_UNSYNCED_FTS_INDEX"
echo "VERIFY_L0=PASS"
