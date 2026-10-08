#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# [ORCACHEV1] offline pathway-route cache: sha256(query+route) -> response
# Idempotent. No network calls. DB is runtime state — stays untracked in Git.
set -eu
export GIT_PAGER=cat

DB="data/route_cache.db"
CMD="${1:-init}"
QUERY="${2:-}"
ROUTE="${3:-lumo}"

norm_query() { printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | tr -s ' \t\n' ' ' | sed 's/^ //;s/ $//'; }

key_for() { printf '%s::%s' "$(norm_query "$1")" "$2" | sha256sum | awk '{print $1}'; }

init_db() {
  mkdir -p data
  sqlite3 "$DB" "
    CREATE TABLE IF NOT EXISTS route_cache (
      key TEXT PRIMARY KEY,
      query TEXT NOT NULL,
      route TEXT NOT NULL,
      model TEXT DEFAULT '',
      response TEXT NOT NULL,
      hits INTEGER DEFAULT 0,
      provenance TEXT DEFAULT 'network',
      ts TEXT DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_route ON route_cache(route);
  "
  sqlite3 "$DB" "CREATE VIRTUAL TABLE IF NOT EXISTS route_cache_fts USING fts5(query, response, content='route_cache', content_rowid=rowid);" 2>/dev/null || true
  echo "[ORCACHEV1][banked] db init ok: $DB ($(sqlite3 "$DB" 'SELECT COUNT(*) FROM route_cache;') entries)"
}

case "$CMD" in
  init) init_db ;;
  lookup)
    KEY="$(key_for "$QUERY" "$ROUTE")"
    ROW="$(sqlite3 -separator '|' "$DB" "SELECT response,hits FROM route_cache WHERE key='$KEY';" || true)"
    if [ -n "$ROW" ]; then
      RESP="${ROW%%|*}"; HITS="${ROW##*|}"
      sqlite3 "$DB" "UPDATE route_cache SET hits=hits+1 WHERE key='$KEY';"
      echo "[ORCACHEV1][HIT] route=$ROUTE hits=$((HITS+1))"
      printf '%s\n' "$RESP"
    else
      echo "[ORCACHEV1][MISS] route=$ROUTE — dispatch to network, then 'store'"
    fi
    ;;
  store)
    # usage: store <query> <route> <response-file-or--stdin>
    [ "$#" -ge 3 ] || { echo "usage: $0 store <query> <route> <respfile|->" >&2; exit 1; }
    RF="${4:?response file or - required}"
    if [ "$RF" = "-" ]; then RESP="$(cat)"; else RESP="$(cat "$RF")"; fi
    KEY="$(key_for "$QUERY" "$ROUTE")"
    sqlite3 "$DB" "INSERT INTO route_cache(key,query,route,response,provenance)
      VALUES('$KEY','${QUERY//\'/\'\'}','$ROUTE','${RESP//\'/\'\'}','network')
      ON CONFLICT(key) DO UPDATE SET response=excluded.response, ts=datetime('now');"
    echo "[ORCACHEV1][banked] stored key=${KEY:0:16} route=$ROUTE (${#RESP} bytes)"
    ;;
  search)
    sqlite3 -separator ' | ' "$DB" "SELECT substr(key,1,12), route, hits, substr(query,1,60) FROM route_cache WHERE query LIKE '%${QUERY}%';"
    ;;
  stats)
    sqlite3 -separator ' | ' "$DB" "SELECT route, COUNT(*), SUM(hits), MAX(ts) FROM route_cache GROUP BY route;"
    ;;
  offline-check)
    # ping-free network probe: try DNS + TCP to each provider in 2s
    for host in lumo.proton.me api.openai.com generativelanguage.googleapis.com; do
      if timeout 2 bash -c "echo >/dev/tcp/$host/443" 2>/dev/null; then
        echo "[ORCACHEV1] ONLINE via $host — network routes available"
        exit 0
      fi
    done
    echo "[ORCACHEV1] OFFLINE — router must serve from cache/local only"
    ;;
  *) echo "usage: $0 {init|lookup <q> <route>|store <q> <route> <file|->|search <term>|stats|offline-check}" >&2; exit 1 ;;
esac
echo "[ORCACHEV1][exit=0]"
