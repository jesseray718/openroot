#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
export GIT_PAGER=cat

REPO="/home/jesse/openroot"
LADDER="/home/jesse/openroot/bin/launch_ladder_v1.py"
ENGINE="/home/jesse/openroot/bin/mistake_engine_v1.py"
DB="/home/jesse/openroot/data/launch_ladder.db"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="/home/jesse/openroot/bin/launch_ladder_v1.py.pre_mistake_runner_fix_v2.${STAMP}.bak"

cd "$REPO"

python3 -m py_compile "$LADDER" "$ENGINE"
echo "[banked] pre-repair py_compile PASS"

cp --preserve=mode,timestamps "$LADDER" "$BACKUP"
test -s "$BACKUP"
echo "[banked] source backup=$BACKUP"

python3 - "$LADDER" <<'PY'
# SPDX-License-Identifier: GPL-3.0-only
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
pattern = re.compile(
    r'("name": "mistake_engine_ready",.*?"runner": \{"cmd": ")'
    r'python3 bin/mistake_engine_v1\.py list'
    r'(", "timeout": \d+\})',
    re.DOTALL,
)
updated, count = pattern.subn(
    r'\1python3 bin/mistake_engine_v1.py compost\2',
    text,
    count=1,
)
if count != 1:
    raise SystemExit(f"expected exactly one mistake_engine_ready runner replacement; found {count}")
path.write_text(updated, encoding="utf-8")
PY

python3 -m py_compile "$LADDER" "$ENGINE"
echo "[banked] post-repair py_compile PASS"

echo "[banked] repaired stage block"
grep -nA16 -B2 '"name": "mistake_engine_ready"' "$LADDER"

if ! grep -nA16 '"name": "mistake_engine_ready"' "$LADDER" | grep -Fq 'python3 bin/mistake_engine_v1.py compost'; then
    echo "[held] supported runner absent inside mistake_engine_ready block"
    echo "[gate] restore from backup and inspect stage registry"
    echo "# [MISTAKERUNNERFIXV2]"
    echo "[exit=0]"
    exit 0
fi

echo "[banked] direct engine runner proof"
python3 "$ENGINE" compost

echo "[banked] resetting only failed stage to locked for fresh real calibration"
sqlite3 "$DB" \
"UPDATE stages
 SET status='locked',
     checks_ok=0,
     last_action='runner repaired; awaiting fresh calibration',
     last_ts=strftime('%Y-%m-%dT%H:%M:%fZ','now'),
     evidence='runner changed from unsupported list to supported compost'
 WHERE name='mistake_engine_ready'
   AND status='failed';"

sqlite3 -header -column "$DB" \
"SELECT name,status,maturity,checks_ok,attempts,last_action,last_ts,evidence
 FROM stages
 WHERE name='mistake_engine_ready';"

echo "[banked] runner repair and failed-stage reset verified"
echo "# [MISTAKERUNNERFIXV2]"
echo "[exit=0]"
