#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
export GIT_PAGER=cat

REPO="/home/jesse/openroot"
LADDER="/home/jesse/openroot/bin/launch_ladder_v1.py"
ENGINE="/home/jesse/openroot/bin/mistake_engine_v1.py"
DB="/home/jesse/openroot/data/launch_ladder.db"
STAGE="mistake_engine_ready"
OUTDIR="/home/jesse/openroot/data/ladder_diagnostics"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPORT="$OUTDIR/promote_${STAGE}.${STAMP}.log"

cd "$REPO"
mkdir -p "$OUTDIR"

{
    python3 -m py_compile "$LADDER" "$ENGINE"
    echo "[banked] py_compile PASS: ladder and mistake engine"

    if ! grep -nA16 '"name": "mistake_engine_ready"' "$LADDER" | grep -Fq 'python3 bin/mistake_engine_v1.py compost'; then
        echo "[held] supported compost runner absent from mistake_engine_ready block"
        echo "[gate] repair stage runner before promotion"
        exit 0
    fi

    echo "[banked] direct runner proof"
    python3 "$ENGINE" compost

    STATUS="$(sqlite3 "$DB" "SELECT COALESCE(status,'') FROM stages WHERE name='$STAGE';")"
    echo "[banked] pre_calibration_status=${STATUS:-missing}"

    sqlite3 -header -column "$DB" \
    "SELECT name,status,maturity,checks_ok,attempts,last_action,last_ts,evidence
     FROM stages
     WHERE name='$STAGE';"

    if [ "$STATUS" = "verified" ]; then
        echo "[banked] $STAGE already verified; no repeat work"
        exit 0
    fi

    if [ "$STATUS" = "locked" ] || [ "$STATUS" = "failed" ]; then
        echo "[gate] bounded real calibration begins: $STAGE"
        set +e
        python3 "$LADDER" calibrate "$STAGE"
        CALIBRATE_RC=$?
        set -e
        echo "[banked] calibrate_exit_code=$CALIBRATE_RC"
    fi

    CALIBRATED="$(sqlite3 "$DB" "SELECT COALESCE(status,'') FROM stages WHERE name='$STAGE';")"
    echo "[banked] post_calibration_status=${CALIBRATED:-missing}"

    sqlite3 -header -column "$DB" \
    "SELECT name,status,maturity,checks_ok,attempts,last_action,last_ts,evidence
     FROM stages
     WHERE name='$STAGE';"

    if [ "$CALIBRATED" != "calibrated" ] && [ "$CALIBRATED" != "verified" ]; then
        echo "[held] calibration did not establish calibrated state: '${CALIBRATED:-missing}'"
        echo "[gate] inspect calibration evidence; do not force ladder state"
        exit 0
    fi

    if [ "$CALIBRATED" = "calibrated" ]; then
        echo "[gate] full real run plus exit verification begins: $STAGE"
        set +e
        python3 "$LADDER" run "$STAGE"
        RUN_RC=$?
        set -e
        echo "[banked] ladder_run_exit_code=$RUN_RC"
    fi

    FINAL="$(sqlite3 "$DB" "SELECT COALESCE(status,'') FROM stages WHERE name='$STAGE';")"
    echo "[banked] final_status=${FINAL:-missing}"

    sqlite3 -header -column "$DB" \
    "SELECT name,status,maturity,checks_ok,attempts,last_action,last_ts,evidence
     FROM stages
     WHERE name='$STAGE';"

    if [ "$FINAL" = "verified" ]; then
        echo "[banked] mistake_engine_ready VERIFIED"
        echo "[banked] next_stage=vector_index_calibrated"
        echo "[banked] next_stage_calibration may have auto-triggered"
    else
        echo "[held] mistake_engine_ready final status='${FINAL:-missing}'"
        echo "[gate] inspect exact runner or exit verification output"
    fi
} 2>&1 | tee "$REPORT"

test -s "$REPORT"
echo "[banked] report_saved=$REPORT"
grep -nE '\[held\]|\[gate\]|Traceback|SyntaxError|FAIL|fail|missing|error|Error' "$REPORT" || true
echo "# [PROMOTEMISTAKEENGINEV2]"
echo "[exit=0]"
