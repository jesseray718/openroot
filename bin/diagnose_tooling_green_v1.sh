#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
export GIT_PAGER=cat

REPO="/home/jesse/openroot"
LADDER="/home/jesse/openroot/bin/launch_ladder_v1.py"
DB="/home/jesse/openroot/data/launch_ladder.db"
OUTDIR="/home/jesse/openroot/data/ladder_diagnostics"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPORT="$OUTDIR/tooling_green.${STAMP}.log"
STAGE="tooling_green"

cd "$REPO"
mkdir -p "$OUTDIR"

{
    echo "[banked] diagnostic_report=$REPORT"
    echo "[banked] timestamp_utc=$STAMP"
    echo

    echo "=== PYTHON COMPILE: LAUNCH LADDER ==="
    python3 -m py_compile "$LADDER"
    echo "[banked] ladder py_compile PASS"
    echo

    echo "=== LADDER: STAGE REGISTRY ==="
    grep -nA14 -B2 "\"name\": \"$STAGE\"" "$LADDER" || true
    echo

    echo "=== LADDER: ENTRY CHECK IMPLEMENTATION ==="
    grep -nE "def .*check|def .*calibr|tooling_green|entry checks|check-bin|py_compile" "$LADDER" || true
    echo

    echo "=== DATABASE: TOOLING GREEN ==="
    sqlite3 -header -column "$DB" \
    "SELECT name,status,maturity,checks_ok,attempts,last_action,last_ts,evidence
     FROM stages
     WHERE name='$STAGE';"
    echo

    echo "=== DATABASE: ALL STAGES ==="
    sqlite3 -header -column "$DB" \
    "SELECT name,status,maturity,checks_ok,attempts,last_action,last_ts
     FROM stages
     ORDER BY name;"
    echo

    echo "=== GIT: CURRENT STATE ==="
    git status --short
    echo
    git --no-pager log --oneline -10
    echo

    echo "=== FILES: REQUIRED LADDER INSTRUMENTS ==="
    for path in \
        "/home/jesse/openroot/bin/a1_core_v1.py" \
        "/home/jesse/openroot/bin/mistake_engine_v1.py" \
        "/home/jesse/openroot/bin/handoff_manager.py" \
        "/home/jesse/openroot/bin/compost_v1.py" \
        "/home/jesse/openroot/bin/agape_vector_index.py"
    do
        if [ -f "$path" ]; then
            printf '[banked] present %s\n' "$path"
            python3 -m py_compile "$path" && printf '[banked] py_compile PASS %s\n' "$path"
        else
            printf '[held] missing %s\n' "$path"
        fi
    done
    echo

    echo "=== LADDER: CALIBRATE DIAGNOSTIC ==="
    set +e
    python3 "$LADDER" calibrate "$STAGE"
    RC=$?
    set -e
    printf '[banked] calibrate_exit_code=%s\n' "$RC"
    echo

    echo "=== DATABASE: POST-CALIBRATE STATE ==="
    sqlite3 -header -column "$DB" \
    "SELECT name,status,maturity,checks_ok,attempts,last_action,last_ts,evidence
     FROM stages
     WHERE name='$STAGE';"
    echo

    echo "=== DIRECT TOOL CHECK: A1 CHECK-BIN ==="
    if [ -f "/home/jesse/openroot/bin/a1_core_v1.py" ]; then
        set +e
        python3 "/home/jesse/openroot/bin/a1_core_v1.py" check-bin
        RC=$?
        set -e
        printf '[banked] a1_check_bin_exit_code=%s\n' "$RC"
    else
        echo "[held] a1_core_v1.py absent; direct check-bin unavailable"
    fi
    echo

    echo "=== GREP: RED/HELD/FAIL SIGNALS ==="
    grep -nE '\[held\]|\[gate\]|FAIL|fail|red|missing|error|Error|Traceback' "$REPORT" 2>/dev/null || true
} 2>&1 | tee "$REPORT"

test -s "$REPORT"
grep -Fq "=== LADDER: CALIBRATE DIAGNOSTIC ===" "$REPORT"
grep -Fq "=== DATABASE: POST-CALIBRATE STATE ===" "$REPORT"

echo "[banked] report_saved=$REPORT"
echo "[banked] extract_following_lines"
grep -nE '\[held\]|\[gate\]|FAIL|fail|red|missing|error|Error|Traceback' "$REPORT" || true
echo "# [TOOLINGGREENDIAGV1]"
echo "[exit=0]"
