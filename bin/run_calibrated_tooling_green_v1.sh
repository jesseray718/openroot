#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
export GIT_PAGER=cat

REPO="/home/jesse/openroot"
LADDER="/home/jesse/openroot/bin/launch_ladder_v1.py"
DB="/home/jesse/openroot/data/launch_ladder.db"
STAGE="tooling_green"
OUTDIR="/home/jesse/openroot/data/ladder_diagnostics"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPORT="$OUTDIR/run_${STAGE}.${STAMP}.log"

cd "$REPO"
mkdir -p "$OUTDIR"

{
    python3 -m py_compile "$LADDER"
    echo "[banked] py_compile PASS: $LADDER"

    STATUS="$(sqlite3 "$DB" "SELECT COALESCE(status,'') FROM stages WHERE name='$STAGE';")"
    echo "[banked] pre_run_status=${STATUS:-missing}"

    if [ "$STATUS" = "verified" ]; then
        echo "[banked] $STAGE already verified; no repeat full run"
        exit 0
    fi

    if [ "$STATUS" != "calibrated" ]; then
        echo "[held] expected calibrated status, found '${STATUS:-missing}'"
        echo "[gate] do not force state; calibrate must succeed before run"
        exit 0
    fi

    echo "[gate] full real run plus exit verification begins: $STAGE"
    set +e
    python3 "$LADDER" run "$STAGE"
    RUN_RC=$?
    set -e
    echo "[banked] ladder_run_exit_code=$RUN_RC"

    FINAL="$(sqlite3 "$DB" "SELECT COALESCE(status,'') FROM stages WHERE name='$STAGE';")"
    echo "[banked] final_status=${FINAL:-missing}"

    sqlite3 -header -column "$DB" \
    "SELECT name,status,maturity,checks_ok,attempts,last_action,last_ts,evidence
     FROM stages
     WHERE name='$STAGE';"

    if [ "$FINAL" = "verified" ]; then
        echo "[banked] tooling_green VERIFIED"
        echo "[banked] next permitted action=calibrate mistake_engine_ready"
    else
        echo "[held] tooling_green final status='${FINAL:-missing}'"
        echo "[gate] inspect exact runner or exit-verification failure"
    fi
} 2>&1 | tee "$REPORT"

test -s "$REPORT"
echo "[banked] report_saved=$REPORT"
grep -nE '\[held\]|\[gate\]|Traceback|SyntaxError|FAIL|fail|missing|error|Error' "$REPORT" || true
echo "# [RUNTOOLINGGREENV1]"
echo "[exit=0]"
