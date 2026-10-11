#!/usr/bin/env bash
# cross_repo_census_v1.sh — sibling-repo thermal asset census + flagship hygiene audit
# CANARY:OPENROOT-CROSS-REPO-CENSUS-V1
# READ-ONLY. Reports only. No deletes, no commits, no pushes.
set -eu
export GIT_PAGER=cat TERM=dumb
BASE=/home/jesse
R="$BASE/openroot"
OUT="$R/reports"
TS=$(date -u +%Y%m%dT%H%M%SZ)
REPORT="$OUT/cross_repo_census-$TS.md"
HOST=$(hostname)
[ "$HOST" = "optiplex3060" ] || { echo "[held] run on optiplex3060"; exit 1; }

echo "[gate] stage 0 — sibling repo discovery"
REPOS="aerocement aerocement-panel-v0 black-locust-rmh OpenCell-Thermal-System openroot-canon openroot-edge openroot-thesis openroot-spoke-template"
{
echo "# cross-repo thermal asset census — $TS"
echo
echo "## 1. Thermal/asset census per sibling repo"
} > "$REPORT"
for repo in $REPOS; do
  DIR="$BASE/$repo"
  [ -d "$DIR" ] || { echo "- $repo: MISSING at $DIR" >> "$REPORT"; continue; }
  {
  echo
  echo "### $repo ($(cd "$DIR" && git rev-parse --short HEAD 2>/dev/null || echo no-git))"
  echo '- BOM/spec/packet/thermal files: ' $(cd "$DIR" && git ls-files 2>/dev/null | grep -Ei '\.(md|csv|txt)$' | grep -Eciv '' || true)
  echo '- thermal-keyword files: ' $(cd "$DIR" && git ls-files 2>/dev/null | grep -ciE '(thermal|stirling|solar|cement|absorb|cascade|labyrinth|locust|bom)' || true)
  echo '- build evidence (photos/measurements/receipts): ' $(cd "$DIR" && git ls-files 2>/dev/null | grep -ciE '(build|cast|pour|measure|test|photo|img|evidence|journal|log-)' || true)
  echo '#### Thermal-knowledgeable filenames:'
  cd "$DIR" && git ls-files 2>/dev/null | grep -iE '(thermal|stirling|solar|absorb|cascade|labyrinth|locust|bom)' | head -25 || true
  } >> "$REPORT"
done

echo "[gate] stage 1 — flagship hygiene audit (openroot)"
{
echo
echo "## 2. Hygiene debt — openroot flagship"
echo '- tracked pyc: ' $(cd "$R" && git ls-files | grep -c '\.pyc$' || true)
echo '- tracked bak: ' $(cd "$R" && git ls-files | grep -cE '\.(bak|before)$' || true)
echo '- tracked log: ' $(cd "$R" && git ls-files | grep -c '\.log$' || true)
echo '- tracked gz/binaries: ' $(cd "$R" && git ls-files | grep -cE '\.(gz|zip|tar)' || true)
echo
echo '### tracked files > 5MiB (repo bloat source)'
cd "$R" && git ls-files -z | xargs -0 du -b 2>/dev/null | awk '$1>5000000' | sort -rn || true
echo
echo '### .git size trend'
du -sh "$R/.git"
echo
echo '### Proposed untrack list (report only — execute separately with CONFIRM=1)'
cd "$R" && git ls-files | grep -E '\.(pyc|bak|before)$' | head -40
echo "...(full list: git ls-files | grep -E '\.(pyc|bak|before)$')"
} >> "$REPORT"

echo "[gate] stage 2 — orphan integration check"
{
echo
echo "## 3. Orphan deepdive_latest.md"
echo '- path: /home/jesse/deepdive_latest.md'
echo '- size: ' $(stat -c%s /home/jesse/deepdive_latest.md 2>/dev/null || echo 0) 'bytes'
echo '- sha256: ' $(sha256sum /home/jesse/deepdive_latest.md 2>/dev/null | awk '{print $1}' || echo none)
echo '- verdict: integrate into reports/deepdive/ as historical baseline, then remove from home'
} >> "$REPORT"

SHA=$(sha256sum "$REPORT" | awk '{print $1}')
{
echo "---"
echo "CANARY:OPENROOT-CROSS-REPO-CENSUS-V1 COMPLETE"
echo "sha256: $SHA"
echo "[held] review, then human-gated commit"
} >> "$REPORT"
echo "[banked] report: $REPORT"
echo "[banked] sha256: $SHA"
echo "[exit=0]"
