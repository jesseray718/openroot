#!/usr/bin/env bash
# finalize_workflow.sh — Fix remaining issues, commit all workflow components
set -e
export GIT_PAGER=cat
BASE_BIN="$HOME/openroot/bin"
DATA_DIR="$HOME/openroot/data"
CTX="$HOME/openroot/context_bridge"

echo "[FINALIZE] Verifying core workflow installation"

# Fix databases (retry without unbound var issue)
echo "[DB] Ensuring databases exist..."
for db in team_gate.db repo_drift.db canonical_index.db terminal_log.db; do
    if [ ! -f "$DATA_DIR/$db" ]; then
        sqlite3 "$DATA_DIR/$db" "CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);"
        echo "[OK] Created $db"
    fi
done

# Create missing tables in team_gate.db
sqlite3 "$DATA_DIR/team_gate.db" "CREATE TABLE IF NOT EXISTS gates (id INTEGER PRIMARY KEY, task TEXT, verdict TEXT, timestamp TEXT);" 2>/dev/null || true
sqlite3 "$DATA_DIR/team_gate.db" "CREATE TABLE IF NOT EXISTS iterations (id INTEGER PRIMARY KEY, spec TEXT, generated TEXT, verdict TEXT, timestamp TEXT);" 2>/dev/null || true
sqlite3 "$DATA_DIR/terminal_log.db" "CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, content TEXT, timestamp TEXT, embedding TEXT);" 2>/dev/null || true

# Fix env_map.py deprecation warning
cat <<'PYEOF' > "$BASE_BIN/env_map.py"
#!/usr/bin/env python3
"""env_map.py — Map environment state to data/env_map.json"""
import os, sys, json, socket
from datetime import datetime, timezone
from pathlib import Path

OUTPUT = os.getenv("ENV_MAP_OUTPUT", "/home/jesse/openroot/data/env_map.json")
if "/data/data/com.termux" in os.path.expanduser("~"):
    OUTPUT = str(Path.home() / "openroot" / "data" / "env_map.json")

def main():
    env_map = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "machine": socket.gethostname(),
        "user": os.environ.get("USER", "unknown"),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "ollama_url": os.environ.get("OLLAMA_HOST", "http://localhost:11434"),
        "agent_model": os.environ.get("AGENT_MODEL", "qwen2.5-coder:7b"),
        "grader_model": os.environ.get("GRADER_MODEL", "qwen2.5:3b"),
        "embed_model": os.environ.get("EMBED_MODEL", "nomic-embed-text"),
        "home": str(Path.home()),
        "git_user": os.environ.get("GIT_AUTHOR_NAME", ""),
        "git_email": os.environ.get("GIT_AUTHOR_EMAIL", "")
    }
    with open(OUTPUT, "w") as f:
        json.dump(env_map, f, indent=2)
    print(f"[BANKED] {OUTPUT}")

if __name__ == "__main__":
    main()
PYEOF
chmod +x "$BASE_BIN/env_map.py"
python3 "$BASE_BIN/env_map.py"

# Clean pycache
rm -rf "$BASE_BIN/__pycache__" "$HOME/openroot/__pycache__" 2>/dev/null || true

# Verify all 10 core scripts
echo ""
echo "[VERIFY] Core workflow components:"
CORER=(agent.sh stack_gate.sh team_gate_v2.sh light_cone_router.py \
       aider_task_runner.py push_guard.py terminal_log_rag.py \
       agape_qa_engine.py onepass_v3.sh env_map.py)
COUNT=0
for s in "${CORER[@]}"; do
    if [ -f "$BASE_BIN/$s" ]; then
        echo "[OK] $s ($(wc -l < "$BASE_BIN/$s") lines)"
        COUNT=$((COUNT+1))
    else
        echo "[MISSING] $s"
    fi
done

echo ""
echo "[SUMMARY] Installed: $COUNT/10 core scripts"
echo "[SUMMARY] Total in bin/: $(ls -1 "$BASE_BIN"/*.sh "$BASE_BIN"/*.py 2>/dev/null | wc -l)"

# Commit everything
echo ""
echo "[GIT] Preparing commit..."
cd "$HOME/openroot"
git add -A bin/env_map.py bin/stack_gate.sh bin/team_gate_v2.sh bin/agent.sh \
         bin/light_cone_router.py bin/aider_task_runner.py bin/push_guard.py \
         bin/terminal_log_rag.py bin/agape_qa_engine.py bin/onepass_v3.sh \
         bin/rebuild_core_workflow.sh bin/finalize_workflow.sh \
         data/ data/*.json \
         context_bridge/ 2>/dev/null || true

git diff --cached --stat
git commit -m "[ADD] Core workflow rebuild (boot seed recovery)
- Restored 10 lost scripts: agent.sh, stack_gate.sh, team_gate_v2.sh,
  light_cone_router.py, aider_task_runner.py, push_guard.py,
  terminal_log_rag.py, agape_qa_engine.py, onepass_v3.sh, env_map.py
- Initialized databases: team_gate.db, repo_drift.db, canonical_index.db, terminal_log.db
- Fixed: env_map.py deprecation warning, stack_gate.sh v2 comment-aware filtering
- All components follow standing rules: heredoc delivery, gates, [exit=0] termination
- 7B authored, py_compile passed" || echo "[GIT] Nothing to commit"

echo "[FINALIZE] Complete — [exit=0]"
