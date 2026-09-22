#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo " OPENROOT REPOSITORY ROLLOUT & OVERHAUL "
echo " TIME: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "========================================"

# 1. ARCHIVE & SNAPSHOT
SNAPSHOT_TAG="snapshot-pre-rollout-$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="context_bridge/backups/${SNAPSHOT_TAG}"

echo -e "\n[STEP 1/5] Creating safety snapshot tag: ${SNAPSHOT_TAG}..."
git tag -a "${SNAPSHOT_TAG}" -m "State archive before total README overhaul and branch cleanup"
mkdir -p "${BACKUP_DIR}"

if [ -f "README.md" ]; then
    cp README.md "${BACKUP_DIR}/README.md.bak"
    echo "  - Backed up existing README.md to ${BACKUP_DIR}/"
fi

# 2. CONVERGED BRANCH CONSOLIDATION
echo -e "\n[STEP 2/5] Cleaning up converged and dangling branches..."
CURRENT_BRANCH=$(git branch --show-current)

if [ "$CURRENT_BRANCH" != "main" ]; then
    git checkout main
fi

# Fetch and prune remote references
git fetch origin --prune

# Safely delete local branches that have been merged into main
for branch in $(git branch --merged main | grep -v '^\*' | grep -v 'main'); do
    echo "  - Removing merged local branch: $branch"
    git branch -d "$branch" || true
done

# 3. WRITE PROFESSIONAL OPEN SOURCE README.md
echo -e "\n[STEP 3/5] Generating professional README.md..."
cat << 'README_EOF' > README.md
# OpenRoot Platform

[![Stack Gate Audit](https://img.shields.io/badge/Stack%20Gate-PASSING-success.svg)](#)
[![Python Engine](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)

OpenRoot is an offline-first, private development environment and thermodynamic computational framework designed for system verification, hardware modeling, and dynamic ledger state tracking.

---

## 🏛️ System Architecture

OpenRoot operates as an autonomous workspace bridging embedded C/C++ hardware modules, local vector/FTS search layers, and dynamic error resolution pipelines.


