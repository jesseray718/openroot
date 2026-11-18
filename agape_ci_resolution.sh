#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
ROOT="$PWD"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
TASK_DIR="workareas/release/ci_resolution_tasks"
mkdir -p "$TASK_DIR"
echo "========================================================"
echo "=== Agape CI Resolution → Git Task Pipeline          ==="
echo "========================================================"
cat > "\( TASK_DIR/task_ \){TS}_pages_traffic.md" << TASK
# CI Resolution Task — Pages + Traffic Stats

**Source:** GitHub notifications (jesseray718/jesseray718)
**Failures observed:**
- pages build and deployment workflow run failed for main
- GitHub Traffic Stats workflow run failed (multiple)

**Root causes (order of probability):**
1. Missing or broken .github/workflows/*.yml in the personal repo
2. Pages source branch / folder mismatch
3. Traffic stats action permissions or deprecated API
4. Secrets / GITHUB_TOKEN scope

**Resolution steps (machine with gh auth):**
cd /path/to/jesseray718
gh workflow list
gh run list --limit 10
cat .github/workflows/*pages* .github/workflows/*traffic* 2>/dev/null || true

**OpenRoot impact:** none on the openroot flagship. Personal-repo hygiene.
**Priority:** low
**Email-bot payload ready:** yes
TASK

cat > "\( TASK_DIR/tasks_ \){TS}.json" << JSON
{
  "schema": "agape_ci_resolution_v1",
  "timestamp": "$TS",
  "node": "a15_edge",
  "tasks": [
    {
      "id": "pages-traffic-fail",
      "repo": "jesseray718/jesseray718",
      "severity": "pages + traffic stats workflows failing on main",
      "priority": "low",
      "action": "inspect and disable or rewrite workflows",
      "blocks_openroot": false
    },
    {
      "id": "newton-chain-validate",
      "repo": "jesseray718/openroot",
      "severity": "newton-chain-validate.yml failed on ghost/a15-old-lineage",
      "priority": "medium",
      "action": "confirm branch is archived or fix validator",
      "blocks_openroot": false
    }
  ]
}
JSON
echo "[ok] Resolution tasks written to $TASK_DIR"
echo "    - task_${TS}_pages_traffic.md"
echo "    - tasks_${TS}.json"
echo "========================================================"
