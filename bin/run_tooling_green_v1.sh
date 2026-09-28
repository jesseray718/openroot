#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
export GIT_PAGER=cat

REPO="/home/jesse/openroot"
LADDER="/home/jesse/openroot/bin/launch_ladder_v1.py"
DB="/home/jesse/openroot/data/launch_ladder.db"

cd "$REPO"

python3 -m py_compile "$LADDER"
echo "[banked] py_compile PASS: $LADDER"

if [ ! -f "$DB" ]; then
    echo "[held] missing database: $DB"
    echo "[gate] do not run tooling_green without its ladder database"
    echo "# [TOOLINGGREENRUNV1]"
    echo "[exit=0]"
    exit 0
fi

if ! sqlite3 "$DB" "PRAGMA table_info(stages);" | cut -d'|' -f2 | grep -Fxq "maturity"; then
    echo "[held] stages.maturity absent"
    echo "[gate] restore the successful Bug #1 schema migration before running"
    echo "# [TOOLINGGREENRUNV1]"
    echo "[exit=0]"
    exit 0
fi

if ! grep -Fq "ON CONFLICT(name) DO UPDATE SET maturity=excluded.maturity" "$LADDER"; then
    echo "[held] state-preserving stage registration not verified"
    echo "[gate] do not run ladder until registration repair is present"
    echo "# [TOOLINGGREENRUNV1]"
    echo "[exit=0]"
    exit 0
fi

echo "[banked] pre-run tooling_green state"
sqlite3 -header -column "$DB" \
"SELECT name,status,maturity,checks_ok,attempts,last_action,last_ts
 FROM stages
 WHERE name='tooling_green';"

echo "[gate] real tooling_green calibration and exit verification begins"
python3 "$LADDER" run tooling_green

echo "[banked] post-run tooling_green state"
sqlite3 -header -column "$DB" \
"SELECT name,status,maturity,checks_ok,attempts,last_action,last_ts
 FROM stages
 WHERE name='tooling_green';"

STATUS="$(sqlite3 "$DB" "SELECT COALESCE(status,'') FROM stages WHERE name='tooling_green';")"

if [ "$STATUS" = "VERIFIED" ]; then
    echo "[banked] tooling_green VERIFIED"
else
    echo "[held] tooling_green finished with status '${STATUS:-missing}'"
    echo "[gate] inspect real verification output; do not force stage status"
fi

echo "# [TOOLINGGREENRUNV1]"
echo "[exit=0]"
