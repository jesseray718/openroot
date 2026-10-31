#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# ci_fail_diagnosis_v1.sh — pull CI failure log from OpenCell #12's python-quality job
# Outputs: exact error text causing FAILURE (ruff/pyright/pytest output)
set -euo pipefail
export GIT_PAGER=cat

gh api \
  "repos/jesseray718/OpenCell-Thermal-System/actions/runs?head_sha=$(gh pr view 12 -R jesseray718/OpenCell-Thermal-System --json headSha --jq .headSha)" \
  --jq '.workflow_runs[0].id' 2>/dev/null | xargs -I{} gh api \
  "/repos/jesseray718/OpenCell-Thermal-System/actions/runs/{}/jobs" \
  --jq '.jobs[] | select(.name | contains("python-quality")) | {id:.id,name:.name,status:.status,conclusion:.conclusion}' 2>/dev/null | \
  while read -r meta; do
    JOB_ID=$(echo "$meta" | grep -oP '"id":\s*\K\d+')
    [ -z "$JOB_ID" ] && continue
    echo "--- Job $JOB_ID ---"
    gh api "/repos/jesseray718/OpenCell-Thermal-System/actions/jobs/$JOB_ID/logs" 2>/dev/null | \
      grep -A 20 -i "failed\|error\|assertion\|ruff\|pyright" | head -n 30 || true
  done
