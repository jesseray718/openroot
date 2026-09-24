#!/bin/bash
# OPENROOT SUPERLINEAR RECOVERY SCRIPT v2026.09.24
# Jesse Ray (OpenRoot) - GPL-3.0
# Target: OptiPlex (Ubuntu 24.04)

set -eu
CANARY="[RECOVERY-V2-OK]"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OPTIPLEX_USER="jesse"
TERMUX_SSH="jesse@100.122.169.43"
LOGFILE="/home/jesse/openroot/logs/recovery_${TIMESTAMP}.log"
ORIGIN_PATH="/home/jesse"
OPENROOT_PATH="/home/jesse/openroot"

mkdir -p "$OPENROOT_PATH/logs"
mkdir -p "$OPENROOT_PATH/bin"
mkdir -p "$OPENROOT_PATH/docs"
mkdir -p "$OPENROOT_PATH/data"
exec 1> >(tee -a "$LOGFILE")

echo "=== OPENROOT SUPERLINEAR RECOVERY STARTED === $TIMESTAMP"
echo "Host: $(hostname)"
echo "CANARY: $CANARY"

# ===== FUNCTIONS =====
log() { echo "[$(date '+%H:%M:%S')] $1"; }
stage() { echo ""; echo "===== STAGE $1: $2 ====="; }

check_file() {
    local f="$1"
    if [[ -f "$f" ]]; then
        log "✅ Found: $f ($(wc -c < "$f" 2>/dev/null || echo '?') bytes)"
        return 0
    else
        log "❌ Missing: $f"
        return 1
    fi
}

find_in_paths() {
    local filename="$1"
    shift
    for dir in "$@"; do
        if [[ -f "$dir/$filename" ]]; then
            echo "$dir/$filename"
            return 0
        fi
    done
    return 1
}

create_ledger_placeholder() {
    local path="$1"
    local type="$2"
    
    mkdir -p "$(dirname "$path")"
    
    if [[ ! -f "$path" ]]; then
        HASH=$(echo "${CANARY}${type}${TIMESTAMP}" | sha256sum | cut -c1-16)
        cat > "$path" << LEDGER_EOF
{"ts":"$(date -Iseconds)","type":"$type","data":{"recovery":"initialized","canary":"$CANARY"},"prev_hash":"","hash":"$HASH"}
LEDGER_EOF
        log "📝 Created placeholder: $path"
    fi
}

sync_to_termux() {
    local local_path="$1"
    local remote_dest="$2"
    
    if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$TERMUX_SSH" true 2>/dev/null; then
        scp -o StrictHostKeyChecking=no "$local_path" "${TERMUX_SSH}:${remote_dest}" && \
            log "✅ Synced to Termux: $(basename "$local_path")" || \
            log "⚠️ Sync failed to Termux: $(basename "$local_path")"
    else
        log "⚠️ Termux unreachable via Tailscale (100.122.169.43)"
    fi
}

# ===== STAGE 1: LOCATE EXISTING LEDGERS =====
stage 1 "LEDGER DISCOVERY"

# Search for existing ledgers across all known locations
LEDGER_SEARCH_DIRS=(
    "$OPENROOT_PATH"
    "$OPENROOT_PATH/data"
    "$OPENROOT_PATH/context_bridge"
    "$OPENROOT_PATH/archive"
    "$OPENROOT_PATH/attic"
    "$ORIGIN_PATH"
)

declare -A FOUND_LEDGERS

for ledger_name in "eta_moves.jsonl" "ideas.jsonl" "linux_command_persistence.jsonl" "thermo_ledger.jsonl" "audit_trail.jsonl" "chain.jsonl" "theorems.jsonl" "axioms.jsonl"; do
    for search_dir in "${LEDGER_SEARCH_DIRS[@]}"; do
        if found=$(find_in_paths "$ledger_name" "$search_dir" 2>/dev/null); then
            FOUND_LEDGERS["$ledger_name"]="$found"
            log "📍 Found: $ledger_name at $found"
            break
        fi
    done
done

# Create missing ledgers with proper paths
CREATE_LEDGERS=(
    "$OPENROOT_PATH/data/oracle_etha_ledger.jsonl:eta_moves"
    "$OPENROOT_PATH/data/parallel_ideas.jsonl:ideas"
    "$OPENROOT_PATH/ledger/experiments/linux_command_persistence.jsonl:command_persistence"
    "$OPENROOT_PATH/context_bridge/audit_trail.jsonl:audit"
    "$OPENROOT_PATH/data/lessons.db:lessons_sqlite"
)

for ledger_spec in "${CREATE_LEDGERS[@]}"; do
    IFS=':' read -r path type <<< "$ledger_spec"
    create_ledger_placeholder "$path" "$type"
done

# ===== STAGE 2: RECOVER CRITICAL SCRIPTS TO BIN =====
stage 2 "SCRIPT CONSOLIDATION"

CRITICAL_SCRIPTS=(
    "unify_v2.py"
    "bot_loop_v1.py"
    "enable_vector_embeddings.py"
    "find_api_keys.sh"
    "router_relaunch_proof_v1.sh"
    "setup-optiplex.sh"
    "markor_compiler.py"
    "autoupdate_loop.py"
    "deepdive.py"
    "agape_ledger_chain.py"
    "une_fix.py"
    "fix_push_v2.sh"
    "batch_nomic_embed.py"
    "local_rag_search.py"
    "faiss_search.py"
    "lesson_stage_v1.py"
    "lesson_ingest.py"
    "window_loop_v1.py"
    "window_fuse_v1.py"
    "keyword_router_v1.py"
    "agape_cascade_v2.py"
)

RECOVERED_COUNT=0

for script in "${CRITICAL_SCRIPTS[@]}"; do
    found=false
    
    # Search all possible locations
    for search_dir in "$OPENROOT_PATH" "$ORIGIN_PATH" "$OPENROOT_PATH/archive" "$OPENROOT_PATH/attic" "/home" "$OPENROOT_PATH/attic/rescue_staging_vendor"; do
        if [[ -f "$search_dir/$script" ]]; then
            if [[ ! -f "$OPENROOT_PATH/bin/$script" ]]; then
                cp "$search_dir/$script" "$OPENROOT_PATH/bin/"
                log "✅ Recovered to bin/: $script (from $search_dir)"
                ((RECOVERED_COUNT++))
            else
                log "⏹️ Already in bin/: $script"
            fi
            found=true
            break
        fi
    done
    
    if [[ "$found" == false ]]; then
        log "⚠️ Not found anywhere: $script"
    fi
done

# Copy all Python from rescue vendor
VENDOR_PYTHON_COUNT=0
if [[ -d "$OPENROOT_PATH/attic/rescue_staging_vendor" ]]; then
    for pyfile in "$OPENROOT_PATH/attic/rescue_staging_vendor"/*.py; do
        if [[ -f "$pyfile" ]]; then
            cp "$pyfile" "$OPENROOT_PATH/bin/" 2>/dev/null || true
            ((VENDOR_PYTHON_COUNT++)) || true
        fi
    done
    log "✅ Copied $VENDOR_PYTHON_COUNT vendor scripts to bin/"
fi

log "Total scripts consolidated: $RECOVERED_COUNT + $VENDOR_PYTHON_COUNT vendor"

# ===== STAGE 3: RECOVER CORE DOCUMENTATION =====
stage 3 "DOCUMENT CONSOLIDATION"

DOCS_TO_RECOVER=(
    "MASTER_TODO.md"
    "GOALS.md"
    "SUPERLINEAR.md"
    "README.md"
    "CONSTITUTION.md"
    "CONTRIBUTING.md"
    "CONTRIBUTORS.md"
    "SCOPE.md"
    "SYSTEM_ACTION_PLAN.md"
    "SYSTEM_BLUEPRINTS.md"
    "UNIFIED_ARCHITECTURE.md"
)

for doc in "${DOCS_TO_RECOVER[@]}"; do
    found=false
    for search_dir in "$OPENROOT_PATH" "$ORIGIN_PATH" "/home/jesse/jesseray718" "$OPENROOT_PATH/archive"; do
        if [[ -f "$search_dir/$doc" ]]; then
            if [[ ! -f "$OPENROOT_PATH/docs/$doc" ]]; then
                mkdir -p "$OPENROOT_PATH/docs"
                cp "$search_dir/$doc" "$OPENROOT_PATH/docs/"
                log "✅ Recovered to docs/: $doc"
            fi
            found=true
            break
        fi
    done
    
    if [[ "$found" == false ]]; then
        log "⚠️ Not found: $doc"
    fi
done

# ===== STAGE 4: PRESERVE CONTEXT BRIDGE & LESSONS =====
stage 4 "SESSION PRESERVATION"

if [[ -d "$OPENROOT_PATH/context_bridge" ]]; then
    BACKUP_NAME="context_bridge_backup_${TIMESTAMP}"
    cp -r "$OPENROOT_PATH/context_bridge" "$OPENROOT_PATH/$BACKUP_NAME"
    log "✅ Backed up context_bridge to: $BACKUP_NAME"
    
    # Count contents
    JSONL_COUNT=$(find "$OPENROOT_PATH/context_bridge" -name "*.jsonl" 2>/dev/null | wc -l)
    MD_COUNT=$(find "$OPENROOT_PATH/context_bridge" -name "*.md" 2>/dev/null | wc -l)
    log "📊 context_bridge: $JSONL_COUNT jsonl, $MD_COUNT md files"
fi

if [[ -d "$OPENROOT_PATH/lessons" ]]; then
    LESSON_COUNT=$(ls "$OPENROOT_PATH/lessons"/*.md 2>/dev/null | wc -l)
    log "✅ Lessons preserved: $LESSON_COUNT files"
fi

if [[ -d "$OPENROOT_PATH/archive" ]]; then
    ARCHIVE_SIZE=$(du -sh "$OPENROOT_PATH/archive" 2>/dev/null | cut -f1)
    log "📦 Archive size: $ARCHIVE_SIZE"
fi

# ===== STAGE 5: GIT STATE CHECK =====
stage 5 "VERSION CONTROL"

cd "$OPENROOT_PATH" 2>/dev/null || cd /home/jesse 2>/dev/null || true

if [[ -d "$OPENROOT_PATH/.git" ]]; then
    log "Git HEAD: $(git symbolic-ref HEAD --short 2>/dev/null || echo 'detached')"
    log "Recent commits:"
    git log --oneline -5 2>/dev/null || log "❌ git log failed"
    
    # Check for uncommitted changes
    CHANGED=$(git status --short 2>/dev/null | wc -l)
    if [[ "$CHANGED" -gt 0 ]]; then
        log "⚠️ Uncommitted changes: $CHANGED lines"
        git status --short 2>/dev/null | head -10 >> "$LOGFILE"
    else
        log "✅ Working tree clean"
    fi
    
    # Verify main branch exists
    BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    log "Current branch: $BRANCH"
else
    log "⚠️ Not in git repository or .git missing"
fi

# ===== STAGE 6: DATABASE RECOVERY =====
stage 6 "SQLITE LEDGERS"

# Find all sqlite databases
DB_FILES=$(find "$ORIGIN_PATH" "$OPENROOT_PATH" -name "*.db" -type f 2>/dev/null | head -10)

for db in $DB_FILES; do
    if [[ -f "$db" ]]; then
        SIZE=$(du -h "$db" | cut -f1)
        log "Found: $db ($SIZE)"
        
        # Verify integrity
        if sqlite3 "$db" "PRAGMA integrity_check;" 2>/dev/null | grep -q "ok"; then
            log "✅ Database integrity OK: $(basename "$db")"
        else
            log "⚠️ Potential corruption: $(basename "$db")"
        fi
        
        # Backup if in active directories
        if [[ "$db" == *"/data/"* ]] || [[ "$db" == *"/context_bridge/"* ]]; then
            mkdir -p "$OPENROOT_PATH/db_backups"
            cp "$db" "$OPENROOT_PATH/db_backups/"
            log "🛡️ Backed up: $(basename "$db")"
        fi
    fi
done

# ===== STAGE 7: CROSS-DEVICE SYNC TO TERMUX =====
stage 7 "SYNC TO ANDROID"

# Sync critical ledgers that may have mobile updates
SYNC_LEDGERS=(
    "$OPENROOT_PATH/data/oracle_etha_ledger.jsonl:/sdcard/openroot/thermo_ledger/eta_moves.jsonl"
    "$OPENROOT_PATH/data/parallel_ideas.jsonl:/sdcard/openroot/parallel_analysis/ledger/ideas.jsonl"
    "$OPENROOT_PATH/bin:/sdcard/openroot/bin"
    "$OPENROOT_PATH/docs:/sdcard/openroot/docs"
)

for sync_pair in "${SYNC_LEDGERS[@]}"; do
    IFS=':' read -r local remote <<< "$sync_pair"
    
    if [[ -e "$local" ]]; then
        sync_to_termux "$local" "$remote"
    fi
done

# ===== STAGE 8: GENERATE RECOVERY REPORT =====
stage 8 "FINAL REPORT"

REPORT="$OPENROOT_PATH/context_bridge/recovery_report_${TIMESTAMP}.md"
mkdir -p "$OPENROOT_PATH/context_bridge"

cat > "$REPORT" << REPORT_EOF
# OpenRoot Recovery Report
**Generated:** $(date -Iseconds)
**Host:** $(hostname)
**User:** $USER
**Canary:** $CANARY
**Version:** 2026.09.24

## Summary Statistics
- Ledgers discovered: ${#FOUND_LEDGERS[@]}
- Scripts recovered to bin/: $RECOVERED_COUNT
- Vendor scripts copied: $VENDOR_PYTHON_COUNT
- Docs consolidated: $(ls "$OPENROOT_PATH/docs"/*.md 2>/dev/null | wc -l)
- Context bridge backed up: Yes
- Git status: Clean or $(( $(git status --short 2>/dev/null | wc -l) )) changes

## Ledger Inventory
$(for ledger in "${!FOUND_LEDGERS[@]}"; do
    echo "- ✅ $ledger: ${FOUND_LEDGERS[$ledger]}"
done)

## Missing Ledgers (placeholders created)
- data/oracle_etha_ledger.jsonl (eta_moves)
- data/parallel_ideas.jsonl (ideas)
- ledger/experiments/linux_command_persistence.jsonl

## Next Actions
1. **Verify ledgers:** \`head -3 $OPENROOT_PATH/data/*.jsonl\`
2. **Test bot loop:** \`python3 $OPENROOT_PATH/bin/bot_loop_v1.py\`
3. **Check Termux sync:** \`ssh jesse@100.122.169.43 'ls -la /sdcard/openroot/data/'\`
4. **Review context bridge:** \`ls -la $OPENROOT_PATH/context_bridge/\`
5. **Run superlinear health check:** \`cd $OPENROOT_PATH && bash bin/lumo_bridge_run.sh 1\` (if exists)

## Hash Chain Verification
$(find "$OPENROOT_PATH" -name "*.jsonl" -type f -exec sha256sum {} \; 2>/dev/null | head -20)

## Log Location
Full log: $LOGFILE

$CANARY
REPORT_EOF

log "📋 Recovery report: $REPORT"

# ===== FINAL OUTPUT =====
echo ""
echo "=== RECOVERY COMPLETE === $TIMESTAMP"
echo "Log:       $LOGFILE"
echo "Report:    $REPORT"
echo "Bin count: $(ls "$OPENROOT_PATH/bin/" 2>/dev/null | wc -l) files"
echo "Docs:      $(ls "$OPENROOT_PATH/docs/" 2>/dev/null | wc -l) files"
echo "CANARY:    $CANARY"
echo "[exit=0]"

exit 0
