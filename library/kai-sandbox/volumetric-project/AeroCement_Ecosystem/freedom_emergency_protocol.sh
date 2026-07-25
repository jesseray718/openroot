#!/bin/bash
# FREEDOM EMERGENCY PROTOCOL - AEROCENT Ecosystem
# PURPOSE: Bundle all active work, clear temp caches, and zip for transport
# WARNING: This clears temporary build artifacts. Your source code is preserved.

echo "[+] INITIATING FREEDOM PROTOCOL..."

# 1. Define Workspace (Adjust if your path differs)
WORKSPACE="${HOME}/aerocement_ecosystem"
BACKUP_NAME="aero_backup_$(date +%Y%m%d_%H%M%S)"
TEMP_DIR="/tmp/aero_clean_${RANDOM}"

# Create backup directory
mkdir -p "${WORKSPACE}/backups/${BACKUP_NAME}"

# 2. Archive Critical Files (Source Code, Docs, Scripts)
echo "[+] Archiving critical assets..."
if [ -d "${WORKSPACE}" ]; then
    cp -r "${WORKSPACE}"/* "${WORKSPACE}/backups/${BACKUP_NAME}/" 2>/dev/null || echo "[!] Some files already moved or missing."
else
    echo "[!] Workspace not found at ${WORKSPACE}. Searching current dir..."
    tar -czf "${WORKSPACE}/backups/${BACKUP_NAME}/current_session.tar.gz" * 2>/dev/null
fi

# 3. Clean System Temp & Build Artifacts (The "Glitch" Cleanup)
echo "[+] Cleaning build artifacts and temp caches..."
find . -name "*.o" -delete
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find /tmp -maxdepth 1 -name "aero_*" -exec rm -rf {} + 2>/dev/null

# 4. Final Zip for Transport
echo "[+] Creating final transportable archive..."
cd "${WORKSPACE}/backups" || exit 1
tar -czf "../${BACKUP_NAME}_COMPLETE.tgz" "${BACKUP_NAME}"

echo ""
echo "=========================================="
echo "[SUCCESS] FREEDOM PROTOCOL COMPLETE"
echo "Archive Location: ${WORKSPACE}/${BACKUP_NAME}_COMPLETE.tgz"
echo "Temp Cache: CLEARED"
echo "Status: READY FOR EXTERNAL TRANSFER"
echo "=========================================="
echo "Next Step: Upload the .tgz file to this chat OR paste the contents of the key script."
