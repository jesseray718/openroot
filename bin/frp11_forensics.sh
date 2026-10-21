#!/usr/bin/env bash
# frp11_forensics.sh — identify Sep 19 coordinated master pushes + python-quality failure root cause
set -euo pipefail
export GIT_PAGER=cat
REPO=/home/jesse/openroot
GH_USER=jesseray718
TS=$(date +%Y%m%d_%H%M%S)
RPT=$REPO/analysis/frp11_${TS}
mkdir -p "$RPT"
echo "[frp11] $TS — forensics only, zero mutations"

# ---------- [stage:mystery-push] ----------
{
  for r in openroot-product kai-memory fractallattice etaledger agaperesonance agape-primitives; do
    echo "== $r master tip =="
    gh api "repos/$GH_USER/$r/commits/master" --jq \
      '{sha: .sha[0:12], author: .commit.author.name, github_login: (.author.login // "none"),
        date: .commit.committer.date, msg: (.commit.message | split("\n")[0])}'
  done
} | tee "$RPT/mystery_push.json"

# ---------- [stage:ci-failure] ----------
# grab the latest python-quality run + its failing job log from a representative repo
gh run list -R "$GH_USER/OpenCell-Thermal-System" --workflow python-quality.yml --limit 3 \
  --json displayTitle,conclusion,createdAt,headBranch,databaseId > "$RPT/runs.json" || true
RUN_ID=$(python3 -c 'import json;r=json.load(open("'"$RPT"'/runs.json"));print(next((x["databaseId"] for x in r if x.get("conclusion")=="failure"), r[0]["databaseId"] if r else ""))' 2>/dev/null || true)
if [ -n "${RUN_ID:-}" ]; then
  gh run view "$RUN_ID" -R "$GH_USER/OpenCell-Thermal-System" --log-failed > "$RPT/python_quality_failure.log" 2>&1 || \
    gh run view "$RUN_ID" -R "$GH_USER/OpenCell-Thermal-System" --log > "$RPT/python_quality_failure.log" 2>&1 || true
  echo "[stage:ci-failure] log captured -> $RPT/python_quality_failure.log"
  grep -E 'error|Error|FAILED|ruff' "$RPT/python_quality_failure.log" | head -20 || echo "(no matching lines — inspect full log)"
else
  echo "[held] no runs found under python-quality.yml — will need workflow filename check:"
  gh api "repos/$GH_USER/OpenCell-Thermal-System/actions/workflows" --jq '.workflows[].name' || true
fi

# ---------- [stage:workflow-diff] ----------
# is the failing workflow the SAME file everywhere? fingerprint it across repos
{
  for r in OpenCell-Thermal-System openroot-thesis agapenet; do
    SHA=$(gh api "repos/$GH_USER/$r/contents/.github/workflows/python-quality.yml" --jq '.sha' 2>/dev/null || echo "absent")
    echo "$r python-quality.yml sha=$SHA"
  done
} | tee "$RPT/workflow_fingerprint.txt"

echo "[held] review: $RPT/mystery_push.json + $RPT/python_quality_failure.log + $RPT/workflow_fingerprint.txt"
tail -1 "$0" | grep -q "# \[canary] frp11 paste intact" || { echo "CANARY FAIL — paste truncated"; exit 1; }
echo "[exit=0]"
# [canary] frp11 paste intact
