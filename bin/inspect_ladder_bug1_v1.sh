#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
export GIT_PAGER=cat
DB="/home/jesse/openroot/data/launch_ladder.db"
LADDER="/home/jesse/openroot/bin/launch_ladder_v1.py"
python3 -m py_compile "$LADDER"
echo "[banked] py_compile PASS"
sqlite3 "$DB" "PRAGMA table_info(stages);"
sqlite3 -header -column "$DB" "SELECT name,status,maturity,checks_ok,attempts,last_action,last_ts FROM stages ORDER BY name;"
echo "# [LADDERINSPECTV1]"
echo "[exit=0]"
