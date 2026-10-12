#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat TERM=dumb
BIN=/home/jesse/openroot/bin
HARVEST=/home/jesse/openroot/context_bridge/harvest
TS=$(date -u +%Y%m%dT%H%M%SZ)
RUNDIR=/home/jesse/openroot/logs/bot-receipt-kernel-$TS
mkdir -p "$RUNDIR" "$HARVEST"
REPORT=$HARVEST/bot-report-receipt-kernel-$TS.md
CANARY="CANARY:BOT-RECEIPT-KERNEL-V1"
for t in seal_event_log_v1.py env_hash_v1.py thermo_baseline_v1.py; do
    [ -f "$BIN/$t" ] || { echo "[held] missing $BIN/$t"; exit 1; }
    python3 -m py_compile "$BIN/$t"
done
[ -f "$BIN/mistake_canary_ci_v1.sh" ] || { echo "[held] missing CI"; exit 1; }
bash -n "$BIN/mistake_canary_ci_v1.sh"
echo "[STAGE 0] verified [banked]"
"$BIN/seal_event_log_v1.py" append "{\"event\":\"bot_run\",\"run\":\"$TS\"}" > "$RUNDIR/01-event.log" 2>&1
echo "[STAGE 1] sealed [banked]"
"$BIN/env_hash_v1.py" > "$RUNDIR/02-envhash.log" 2>&1
echo "[STAGE 2] hashed [banked]"
"$BIN/thermo_baseline_v1.py" --seconds 8 --label bot_idle > "$RUNDIR/03-thermo.log" 2>&1
echo "[STAGE 3] sampled [banked]"
bash "$BIN/mistake_canary_ci_v1.sh" > "$RUNDIR/04-mistake.log" 2>&1 || echo "[held]" >> "$RUNDIR/04-mistake.log"
echo "[STAGE 4] replayed [banked]"
"$BIN/seal_event_log_v1.py" validate > "$RUNDIR/05-validate.log" 2>&1
{
    echo "# BOT REPORT: RECEIPT KERNEL V1 - $TS"
    echo "- suite: signed-eventlog + env-hash + thermo-baseline + mistake-canary-CI"
    echo
    for f in "$RUNDIR"/*.log; do
        echo "## $(basename "$f")"
        tail -n 12 "$f" | sed 's/^/    /'
        echo
    done
    echo "## Gate"
    echo "- run dir: $RUNDIR"
    echo "- report: $REPORT"
    echo "$CANARY"
} > "$REPORT"
echo "[STAGE 5] done [banked]"
cat "$REPORT"
echo "[exit=0]"
