#!/usr/bin/env bash
# =============================================================================
# openroot_sync_all_in_one.sh -- Public Repo Sync, Branch Push & WORK_LOG Hook
# =============================================================================
set -euo pipefail

REPO_DIR="${HOME}/openroot"
WORK_LOG="${REPO_DIR}/WORK_LOG.md"
cd "${REPO_DIR}" || { echo "FATAL: Directory ${REPO_DIR} does not exist." >&2; exit 1; }

echo "============================================================================="
echo " OPENROOT ALL-IN-ONE PUBLIC SYNC & LOGGING INITIATOR"
echo "============================================================================="

# 1. Ensure WORK_LOG.md exists
touch "${WORK_LOG}"

# Logging Hook Function
log_status() {
    local status_type="$1"
    local message="$2"
    local timestamp
    timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    local current_sha
    current_sha="$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")"
    local state_hash
    state_hash="$(tar -czf - . 2>/dev/null | sha256sum | awk '{print $1}')"
    local log_entry="[${timestamp}] SYNC ${status_type}: repo=openroot-dossier commit=${current_sha} sha256=${state_hash} details=\"${message}\""
    echo "${log_entry}" >> "${WORK_LOG}"
}

trap 'if [ $? -ne 0 ]; then log_status "FAILURE" "Script aborted unexpectedly."; fi' EXIT

# 2. Configure remote origin
if ! git remote get-url origin >/dev/null 2>&1; then
    git remote add origin https://github.com/jesseray718/openroot-dossier.git
else
    git remote set-url origin https://github.com/jesseray718/openroot-dossier.git
fi

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "[status] Active local branch: ${CURRENT_BRANCH}"

# 3. Create public repository on GitHub if missing
if ! gh repo view jesseray718/openroot-dossier >/dev/null 2>&1; then
    echo "[setup] Creating PUBLIC repository 'openroot-dossier' on GitHub..."
    gh repo create openroot-dossier --public --description "OpenRoot distributed ledger & release dossier" || {
        log_status "FAILURE" "Failed to create public GitHub repository."
        exit 1
    }
else
    echo "[status] Public repository already exists on GitHub."
fi

# 4. Stage and commit any uncommitted work logs or state updates
if [ -n "$(git status --porcelain)" ]; then
    echo "[status] Staging uncommitted local changes..."
    git add WORK_LOG.md 2>/dev/null || true
    git commit -m "chore: automated public sync state update $(date -u +"%Y-%m-%dT%H:%M:%SZ")" || true
fi

# 5. Push to the existing branch upstream with tags
echo "[status] Pushing branch '${CURRENT_BRANCH}' and tags to origin..."
git push -u origin "${CURRENT_BRANCH}" --tags || {
    log_status "FAILURE" "Git push to origin failed."
    exit 1
}

# 6. Log success
log_status "SUCCESS" "Branch '${CURRENT_BRANCH}' successfully pushed and synced as public."
trap - EXIT

echo "============================================================================="
echo " ALL-IN-ONE PUBLIC SYNC COMPLETE & LOGGED"
echo "============================================================================="
