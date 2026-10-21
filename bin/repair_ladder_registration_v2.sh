#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
export GIT_PAGER=cat

REPO="/home/jesse/openroot"
LADDER="/home/jesse/openroot/bin/launch_ladder_v1.py"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="/home/jesse/openroot/bin/launch_ladder_v1.py.pre_registration_fix_v2.${STAMP}.bak"
OLD='INSERT OR REPLACE INTO stages(name, maturity) VALUES(?, ?)'
NEW='INSERT INTO stages(name, maturity) VALUES(?, ?) ON CONFLICT(name) DO UPDATE SET maturity=excluded.maturity'

cd "$REPO"

if [ ! -f "$LADDER" ]; then
    echo "[held] missing ladder: $LADDER"
    echo "[gate] stop and restore the ladder before repair"
    echo "# [LADDERREGFIXV2]"
    echo "[exit=0]"
    exit 0
fi

python3 -m py_compile "$LADDER"
echo "[banked] pre-repair py_compile PASS"

if grep -Fq "$NEW" "$LADDER"; then
    echo "[banked] state-preserving registration already installed"
    grep -nF "$NEW" "$LADDER"
    echo "# [LADDERREGFIXV2]"
    echo "[exit=0]"
    exit 0
fi

MATCHES="$(grep -Foc "$OLD" "$LADDER" || true)"
if [ "$MATCHES" != "1" ]; then
    echo "[held] expected one unsafe SQL fragment; found $MATCHES"
    echo "[gate] inspect registration lines before any modification"
    grep -nE "INSERT|REPLACE|ON CONFLICT|stages\(name" "$LADDER" || true
    echo "# [LADDERREGFIXV2]"
    echo "[exit=0]"
    exit 0
fi

cp --preserve=mode,timestamps "$LADDER" "$BACKUP"
test -s "$BACKUP"
echo "[banked] source backup saved: $BACKUP"

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
    raise SystemExit(f"expected exactly one unsafe SQL fragment, found {count}")
updated = text.replace(old, new, 1)
path.write_text(updated, encoding="utf-8")
PY

python3 -m py_compile "$LADDER"
echo "[banked] post-repair py_compile PASS"

if grep -Fq "$OLD" "$LADDER"; then
    echo "[held] unsafe INSERT OR REPLACE registration remains"
    echo "[gate] restore from the recorded backup before further edits"
    echo "# [LADDERREGFIXV2]"
    echo "[exit=0]"
    exit 0
fi

if ! grep -Fq "$NEW" "$LADDER"; then
    echo "[held] replacement registration not found after edit"
    echo "[gate] restore from the recorded backup before further edits"
    echo "# [LADDERREGFIXV2]"
    echo "[exit=0]"
    exit 0
fi

grep -nF "$NEW" "$LADDER"
echo "[banked] state-preserving registration verified"
diff -u "$BACKUP" "$LADDER" || true
echo "# [LADDERREGFIXV2]"
echo "[exit=0]"
