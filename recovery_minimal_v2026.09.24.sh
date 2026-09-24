#!/bin/bash
# OPENROOT MINIMAL RECOVERY - Simplified for reliability
# Jesse Ray (OpenRoot) - GPL-3.0

CANARY="RECOVERY-V2-OK"
TS=$(date +%Y%m%d_%H%M%S)
LOG="/home/jesse/openroot/logs/recovery_${TS}.log"
OR=/home/jesse/openroot
OD=/home/jesse

mkdir -p "$OR/logs" "$OR/bin" "$OR/docs" "$OR/data" "$OR/db_backups"
exec > >(tee -a "$LOG") 2>&1

echo "=== RECOVERY STARTED $TS ==="
echo "CANARY: $CANARY"

# STAGE 1: CREATE MISSING LEDGERS
echo "--- STAGE 1: LEDGERS ---"
for f in data/oracle_etha_ledger.jsonl data/parallel_ideas.jsonl ledger/experiments/linux_command_persistence.jsonl; do
    fp="$OR/$f"
    if [ ! -f "$fp" ]; then
        mkdir -p "$(dirname "$fp")"
        echo "{\"ts\":\"$(date -Iseconds)\",\"type\":\"$f\",\"data\":{\"recovery\":true},\"hash\":\"$(echo $CANARY$f | sha256sum | cut -c1-16)\"}" > "$fp"
        echo "Created: $fp"
    fi
done

# STAGE 2: FIND EXISTING JSONL LEDGERS
echo "--- STAGE 2: DISCOVER LEDGERS ---"
find "$OR" "$OD" -name "*.jsonl" -type f 2>/dev/null | head -20 | while read f; do
    sz=$(stat -c%s "$f" 2>/dev/null || echo "?")
    echo "Found: $f ($sz bytes)"
done

# STAGE 3: COPY SCRIPTS TO BIN
echo "--- STAGE 3: SCRIPTS ---"
for s in unify_v2.py bot_loop_v1.py enable_vector_embeddings.py deepdive.py agape_ledger_chain.py une_fix.py batch_nomic_embed.py local_rag_search.py faiss_search.py markor_compiler.py autoupdate_loop.py; do
    src=$(find "$OR" "$OD" -maxdepth 3 -name "$s" -type f 2>/dev/null | head -1)
    if [ -n "$src" ] && [ ! -f "$OR/bin/$s" ]; then
        cp "$src" "$OR/bin/"
        echo "Copied: $s -> bin/"
    elif [ -f "$OR/bin/$s" ]; then
        echo "Exists: $s"
    else
        echo "Missing: $s"
    fi
done

# STAGE 4: COPY VENDOR PYTHON
echo "--- STAGE 4: VENDOR SCRIPTS ---"
if [ -d "$OR/attic/rescue_staging_vendor" ]; then
    cnt=$(ls "$OR/attic/rescue_staging_vendor"/*.py 2>/dev/null | wc -l)
    cp "$OR/attic/rescue_staging_vendor"/*.py "$OR/bin/" 2>/dev/null
    echo "Vendor scripts: $cnt"
fi

# STAGE 5: BACKUP DOCUMENTATION
echo "--- STAGE 5: DOCUMENTS ---"
for d in MASTER_TODO.md GOALS.md SUPERLINEAR.md README.md CONSTITUTION.md CONTRIBUTING.md SCOPE.md SYSTEM_ACTION_PLAN.md UNIFIED_ARCHITECTURE.md; do
    src=$(find "$OR" "$OD" -maxdepth 3 -name "$d" -type f 2>/dev/null | head -1)
    if [ -n "$src" ] && [ ! -f "$OR/docs/$d" ]; then
        cp "$src" "$OR/docs/"
        echo "Backed up: $d"
    fi
done

# STAGE 6: PRESERVE CONTEXT BRIDGE
echo "--- STAGE 6: CONTEXT ---"
if [ -d "$OR/context_bridge" ]; then
    bn="ctx_backup_${TS}"
    cp -r "$OR/context_bridge" "$OR/$bn"
    echo "Context backup: $bn"
    find "$OR/context_bridge" -name "*.jsonl" 2>/dev/null | wc -l | xargs -I{} echo "JSONL files: {}"
    find "$OR/context_bridge" -name "*.md" 2>/dev/null | wc -l | xargs -I{} echo "MD files: {}"
fi

if [ -d "$OR/lessons" ]; then
    ls "$OR/lessons"/*.md 2>/dev/null | wc -l | xargs -I{} echo "Lessons: {} files"
fi

# STAGE 7: DATABASE CHECK
echo "--- STAGE 7: DATABASES ---"
find "$OR" "$OD" -name "*.db" -o -name "*.sqlite" 2>/dev/null | head -10 | while read db; do
    sz=$(du -h "$db" 2>/dev/null | cut -f1)
    echo "Database: $db ($sz)"
    if command -v sqlite3 >/dev/null 2>&1; then
        res=$(sqlite3 "$db" "PRAGMA integrity_check;" 2>/dev/null | head -1)
        echo "Integrity: $res"
    fi
done

# STAGE 8: GIT STATUS
echo "--- STAGE 8: GIT ---"
cd "$OR" 2>/dev/null || true
if [ -d ".git" ]; then
    br=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    echo "Branch: $br"
    git log --oneline -3 2>/dev/null | while read line; do echo "Commit: $line"; done
    chg=$(git status --short 2>/dev/null | wc -l)
    echo "Uncommitted: $chg"
else
    echo "Not a git repo"
fi

# STAGE 9: REPORT
echo "--- STAGE 9: REPORT ---"
RP="$OR/context_bridge/recovery_report_${TS}.md"
mkdir -p "$OR/context_bridge"

cat > "$RP" << REPORTEND
# Recovery Report
Date: $(date -Iseconds)
Host: $(hostname)
Canary: $CANARY

## Stats
- Bin scripts: $(ls "$OR/bin/"*.py "$OR/bin/"*.sh 2>/dev/null | wc -l)
- Doc backups: $(ls "$OR/docs/"*.md 2>/dev/null | wc -l)
- JSONL ledgers: $(find "$OR" -name "*.jsonl" 2>/dev/null | wc -l)
- SQLite DBs: $(find "$OR" "$OD" -name "*.db" -o -name "*.sqlite" 2>/dev/null | wc -l)

## Hash Chain
$(find "$OR" -name "*.jsonl" -type f 2>/dev/null | head -10 | xargs -I{} sh -c 'echo "{}: $(sha256sum "{}" | cut -c1-16)"')

## Next Steps
1. Verify: head -1 $OR/data/*.jsonl
2. Test: python3 -m py_compile $OR/bin/bot_loop_v1.py
3. Sync: ssh jesse@100.122.169.43

$CANARY
REPORTEND

echo "Report: $RP"

# FINAL
echo ""
echo "=== RECOVERY COMPLETE $TS ==="
echo "Log: $LOG"
echo "Report: $RP"
echo "BIN: $(ls "$OR/bin/" 2>/dev/null | wc -l) files"
echo "DOCS: $(ls "$OR/docs/" 2>/dev/null | wc -l) files"
echo "CANARY: $CANARY"
echo "[exit=0]"

exit 0
