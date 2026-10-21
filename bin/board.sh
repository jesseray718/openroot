#!/bin/bash
# [BOARDV2] OpenRoot status board — read-only
# SPDX-License-Identifier: GPL-3.0-only
cd /home/jesse/openroot
echo "== BOARD $(date '+%F %T') =="
git log --oneline -1
echo "ahead: $(git rev-list --count origin/main..HEAD)"
echo "dirty: $(git status --short | grep -vc '^??')"
echo "untracked: $(git status --short | grep -c '^??')"
echo "-- machine --"
free -h | awk '/^Mem:/{print "mem "$3"/"$2}'
df -h / | awk 'NR==2{print "disk "$3"/"$2" ("$5")"}'
uptime | grep -oP 'load average.*'
echo "-- stack --"
for s in ollama fail2ban tailscaled; do
  echo "$s: $(systemctl is-active $s 2>/dev/null)"
done
ollama ps 2>/dev/null | tail -n +2
echo "-- flywheel --"
python3 bin/embed_cache.py stats 2>/dev/null
echo "-- quarantine --"
git ls-files | grep -qE '.MARKETPLACE_MARKER_PLACEHOLDER' \
  && echo "FAIL: quarantined file tracked" || echo "PASS"
echo "== BOARDV2 [exit=0] =="
