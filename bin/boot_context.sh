#!/usr/bin/env bash
set -eu
cd /home/jesse/openroot
echo "=== OPENROOT SESSION CONTEXT $(date -u +%FT%TZ) ==="
echo "HEAD: $(git rev-parse --short HEAD)"
echo "Receipt chain:"
for v in v1 v1_1 v1_2 v2_0; do
  [ -f genesis/receipt_${v}.json ] && echo "  ${v}: $(python3 -c "import json,hashlib;r=json.load(open('genesis/receipt_${v}.json'));print(hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()[:16])" 2>/dev/null)"
done
echo "Pods: $(ls pods_garden/ 2>/dev/null | wc -l)"
echo "Dirty: $(git status --porcelain | wc -l) files"
