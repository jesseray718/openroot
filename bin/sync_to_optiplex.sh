#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
exec python3 "$REPO_ROOT/bin/node_bridge_sync.py" "$@"
