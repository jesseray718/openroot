#!/usr/bin/env bash
set -Eeuo pipefail
echo "== Uplift Health =="
echo "date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "host: $(hostname)"
echo "-- shell files --"
ls -lah "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/shell" 2>/dev/null || true
echo "-- keyring errors (last 80) --"
journalctl --user -n 200 2>/dev/null | grep -E "gnome-keyring|SystemPrompter|dbus" | tail -n 80 || true
