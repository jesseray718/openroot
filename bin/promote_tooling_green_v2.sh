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
REPORT="$OUTDIR/promote_${STAGE}.${STAMP}.log"

cd "$REPO"
mkdir -p "$OUTDIR"

{
    echo "[banked] report=$REPORT"
    echo "[banked] stage=$STAGE"
    echo "[banked] timestamp_utc=$STAMP"

    for path in \
        "$LADDER" \
        "/home/jesse/openroot/bin/a1_core_v1.py" \
        "/home/jesse/openroot/bin/compost_v1.py" \
        "/home/jesse/openroot/bin/agape_vector_index.py" \
        "/home/jesse/openroot/bin/mistake_engine_v1.py" \
        "/home/jesse/openroot/bin/handoff_manager.py"
    do
        if [ ! -f "$path" ]; then
            echo "[held] missing required file: $path"
            echo "[gate] repair required instrument before ladder promotion"
            exit 0
        fi
        python3 -m py_compile "$path"
        echo "[banked] py_compile PASS: $path"
    done

    if ! sqlite3 "$DB" "PRAGMA table_info(stages);" | cut -d'|' -f2 | grep -Fxq "maturity"; then
        echo "[held] stages.maturity absent"
        echo "[gate] database schema must be repaired before promotion"
        exit 0
    fi

    if ! grep -Fq "ON CONFLICT(name) DO UPDATE SET maturity=excluded.maturity" "$LADDER"; then
        echo "[held] state-preserving registration repair absent"
        echo "[gate] do not run ladder until state preservation is present"
        exit 0
    fi

    echo "=== PRE-CALIBRATION STATE ==="
    sqlite3 -header -column "$DB" \
    "SELECT name,status,maturity,checks_ok,attempts,last_action,last_ts,evidence
     FROM stages WHERE name='$STAGE';"

    echo "=== ENTRY CHECKS: RAW ==="
    set +e
    python3 "$LADDER" calibrate "$STAGE"
    CALIBRATE_RC=$?
    set -e
    echo "[banked] calibrate_exit_code=$CALIBRATE_RC"

    echo "=== POST-CALIBRATION STATE ==="
    sqlite3 -header -column "$DB" \
    "SELECT name,status,maturity,checks_ok,attempts,last_action,last_ts,evidence
     FROM stages WHERE name='$STAGE';"

    STATUS="$(sqlite3 "$DB" "SELECT COALESCE(status,'') FROM stages WHERE name='$STAGE';")"

    if [ "$STATUS" != "CALIBRATED" ] && [ "$STATUS" != "VERIFIED" ]; then
        echo "[held] calibration did not establish CALIBRATED: ${STATUS:-missing}"
        echo "[gate] inspect report signals; do not force state"
        exit 0
    fi

    if [ "$STATUS" = "CALIBRATED" ]; then
        echo "=== FULL RUN AND EXIT VERIFICATION ==="
        set +e
        python3 "$LADDER" run "$STAGE"
        RUN_RC=$?
        set -e
        echo "[banked] run_exit_code=$RUN_RC"
    fi

    echo "=== FINAL STATE ==="
    sqlite3 -header -column "$DB" \
    "SELECT name,status,maturity,checks_ok,attempts,last_action,last_ts,evidence
     FROM stages WHERE name='$STAGE';"

    FINAL="$(sqlite3 "$DB" "SELECT COALESCE(status,'') FROM stages WHERE name='$STAGE';")"

    if [ "$FINAL" = "VERIFIED" ]; then
        echo "[banked] tooling_green VERIFIED"
        echo "[banked] next permitted stage=mistake_engine_ready calibration"
    else
        echo "[held] tooling_green final status=${FINAL:-missing}"
        echo "[gate] inspect exact failures before another attempt"
    fi
} 2>&1 | tee "$REPORT"

test -s "$REPORT"
echo "[banked] report_saved=$REPORT"
echo "[banked] failure_signal_extract"
grep -nE '\[held\]|\[gate\]|Traceback|SyntaxError|FAIL|fail|missing|error|Error' "$REPORT" || true
echo "# [TOOLINGGREENPROMOTEV2]"
echo "[exit=0]"
