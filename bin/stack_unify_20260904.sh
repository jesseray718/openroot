#!/usr/bin/env bash
# Name the user searched for today. This is not a second stack.
# It is an alias onto bootstrap + FTS ensure.
set -euo pipefail
SELF=$(cd "$(dirname "$0")/.." && pwd)
exec bash "$SELF/bin/bootstrap_openroot_stack.sh" "$SELF"
