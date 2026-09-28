#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
export GIT_PAGER=cat

REPO="/home/jesse/openroot"
LADDER="/home/jesse/openroot/bin/launch_ladder_v1.py"
ENGINE="/home/jesse/openroot/bin/mistake_engine_v1.py"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="/home/jesse/openroot/bin/launch_ladder_v1.py.pre_mistake_runner_fix.${STAMP}.bak"
OLD='python3 bin/mistake_engine_v1.py list'
NEW='python3 bin/mistake_engine_v1.py compost'

cd "$REPO"

if [ ! -f "$LADDER" ] || [ ! -f "$ENGINE" ]; then
    echo "[held] ladder or mistake engine missing"
    echo "[gate] restore required files before runner repair"
    echo "# [MISTAKERUNNERFIXV1]"
    echo "[exit=0]"
    exit 0
fi

python3 -m py_compile "$LADDER" "$ENGINE"
echo "[banked] pre-repair py_compile PASS"

echo "[banked] supported engine usage"
python3 "$ENGINE" 2>&1 || true

if grep -Fq "$NEW" "$LADDER"; then
    echo "[banked] supported compost runner already installed"
elif grep -Fq "$OLD" "$LADDER"; then
    cp --preserve=mode,timestamps "$LADDER" "$BACKUP"
    test -s "$BACKUP"
    echo "[banked] source backup=$BACKUP"

    python3 - "$LADDER" "$OLD" "$NEW" <<'PY'
# SPDX-License-Identifier: GPL-3.0-only
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
old = sys.argv[2]
new = sys.argv[3]
text = path.read_text(encoding="utf-8")
count = text.count(old)
if count != 1:
    raise SystemExit(f"expected one obsolete runner command; found {count}")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
PY
else
    echo "[held] neither expected obsolete nor supported runner command found"
    echo "[gate] inspect the mistake_engine_ready stage block before changing source"
    grep -nA16 -B2 '"name": "mistake_engine_ready"' "$LADDER" || true
    echo "# [MISTAKERUNNERFIXV1]"
    echo "[exit=0]"
    exit 0
fi

python3 -m py_compile "$LADDER" "$ENGINE"
echo "[banked] post-repair py_compile PASS"

if grep -Fq "$OLD" "$LADDER"; then
    echo "[held] obsolete list runner remains"
    echo "[gate] restore backup and inspect"
    echo "# [MISTAKERUNNERFIXV1]"
    echo "[exit=0]"
    exit 0
fi

grep -nA16 -B2 '"name": "mistake_engine_ready"' "$LADDER"
grep -Fq "$NEW" "$LADDER"
echo "[banked] supported mistake-engine runner verified"

echo "[banked] direct runner proof begins"
python3 "$ENGINE" compost
echo "[banked] direct runner proof passed"

echo "# [MISTAKERUNNERFIXV1]"
echo "[exit=0]"
