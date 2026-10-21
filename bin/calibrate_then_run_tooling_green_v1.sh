#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
export GIT_PAGER=cat

REPO="/home/jesse/openroot"
LADDER="/home/jesse/openroot/bin/launch_ladder_v1.py"
DB="/home/jesse/openroot/data/launch_ladder.db"
STAGE="tooling_green"

cd "$REPO"

python3 -m py_compile "$LADDER"
echo "[banked] py_compile PASS: $LADDER"

if [ ! -f "$DB" ]; then
    echo "[held] missing database: $DB"
    echo "[gate] do not proceed without launch_ladder.db"
    echo "# [TOOLINGGREENFLOWV1]"
    echo "[exit=0]"
    exit 0
fi

if ! sqlite3 "$DB" "PRAGMA table_info(stages);" | cut -d'|' -f2 | grep -Fxq "maturity"; then
    echo "[held] stages.maturity absent"
    echo "[gate] repair schema before promotion work"
    echo "# [TOOLINGGREENFLOWV1]"
    echo "[exit=0]"
    exit 0
fi

if ! grep -Fq "ON CONFLICT(name) DO UPDATE SET maturity=excluded.maturity" "$LADDER"; then
    echo "[held] state-preserving registration not present"
    echo "[gate] repair launch_ladder_v1.py before stage execution"
    echo "# [TOOLINGGREENFLOWV1]"
    echo "[exit=0]"
    exit 0
fi

echo "[banked] initial $STAGE state"
sqlite3 -header -column "$DB" \
"SELECT name,status,maturity,checks_ok,attempts,last_action,last_ts
 FROM stages
 WHERE name='$STAGE';"

STATUS="$(sqlite3 "$DB" "SELECT COALESCE(status,'') FROM stages WHERE name='$STAGE';")"

if [ "$STATUS" = "VERIFIED" ]; then
    echo "[banked] $STAGE already VERIFIED; no repeat verification"
    echo "# [TOOLINGGREENFLOWV1]"
    echo "[exit=0]"
    exit 0
fi

if [ "$STATUS" != "CALIBRATED" ]; then
    echo "[gate] bounded real calibration begins: $STAGE"
    python3 "$LADDER" calibrate "$STAGE"
fi

STATUS_AFTER_CALIBRATE="$(sqlite3 "$DB" "SELECT COALESCE(status,'') FROM stages WHERE name='$STAGE';")"

echo "[banked] post-calibration $STAGE state"
sqlite3 -header -column "$DB" \
"SELECT name,status,maturity,checks_ok,attempts,last_action,last_ts
 FROM stages
 WHERE name='$STAGE';"

if [ "$STATUS_AFTER_CALIBRATE" != "CALIBRATED" ] && [ "$STATUS_AFTER_CALIBRATE" != "VERIFIED" ]; then
    echo "[held] $STAGE calibration did not establish CALIBRATED state: '${STATUS_AFTER_CALIBRATE:-missing}'"
    echo "[gate] inspect calibration output; do not force status"
    echo "# [TOOLINGGREENFLOWV1]"
    echo "[exit=0]"
    exit 0
fi

if [ "$STATUS_AFTER_CALIBRATE" != "VERIFIED" ]; then
    echo "[gate] full real run plus exit verification begins: $STAGE"
    python3 "$LADDER" run "$STAGE"
fi

echo "[banked] final $STAGE state"
sqlite3 -header -column "$DB" \
"SELECT name,status,maturity,checks_ok,attempts,last_action,last_ts
 FROM stages
 WHERE name='$STAGE';"

FINAL_STATUS="$(sqlite3 "$DB" "SELECT COALESCE(status,'') FROM stages WHERE name='$STAGE';")"

if [ "$FINAL_STATUS" = "VERIFIED" ]; then
    echo "[banked] $STAGE VERIFIED"
else
    echo "[held] $STAGE finished with status '${FINAL_STATUS:-missing}'"
    echo "[gate] inspect the exact stage output; do not manually update ladder state"
fi

echo "# [TOOLINGGREENFLOWV1]"
echo "[exit=0]"
