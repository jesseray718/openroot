#!/bin/bash
# context_bridge.sh — Immortal Context Manager for OpenRoot
# Usage: ./context_bridge.sh [init|save|load|export|import|summarize]

set -euo pipefail

BASE="/sdcard/openroot/context_bridge"
CONTEXT_FILE="$BASE/context.json"
EXPORTS_DIR="$BASE/exports"
LOGS_DIR="$BASE/logs"

init_context() {
    mkdir -p "$BASE" "$EXPORTS_DIR" "$LOGS_DIR"
    
    if [[ ! -f "$CONTEXT_FILE" ]]; then
        cat > "$CONTEXT_FILE" << 'EOF'
{
  "version": "1.0",
  "created": "",
  "last_modified": "",
  "project": {
    "name": "OpenRoot",
    "owner": "jesse",
    "github": "github.com/jesseray718",
    "vision": "Modular perfectly coded engineered computation using permaculture principles",
    "core_principles": [
      "observe_and_interact",
      "catch_and_store_energy",
      "obtain_yield",
      "apply_self_regulation",
      "use_renewable_resources",
      "produce_no_waste",
      "design_from_patterns_to_details",
      "integrate_not_segregate",
      "use_small_and_slow_solutions",
      "use_and_value_diversity",
      "use_edges_and_valuate_marginalia",
      "creatively_use_and_respond_to_change"
    ],
    "spiritual_foundation": {
      "source": "Yeshua teachings",
      "commandment": "Love as I have loved you",
      "approach": "Vessel for power flowing to the least among us"
    }
  },
  "conversation_history": [],
  "code_artifacts": [],
  "system_state": {
    "status": "initialized",
    "last_session": "",
    "pending_tasks": [],
    "completed_tasks": [],
    "known_issues": [],
    "success_patterns": []
  },
  "ai_memory": {
    "preferences": {},
    "learnings": [],
    "feedback_loops": []
  }
}
EOF
        echo "✓ Context bridge initialized at $CONTEXT_FILE"
    else
        echo "⚠ Context already exists at $CONTEXT_FILE"
    fi
}

update_timestamp() {
    local ts
    ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    jq --arg ts "$ts" '.last_modified = $ts' "$CONTEXT_FILE" > "$BASE/tmp.json" && mv "$BASE/tmp.json" "$CONTEXT_FILE"
}

save_session() {
    local session_id
    session_id="session_$(date +%Y%m%d_%H%M%S)"
    
    echo "=== Saving Session: $session_id ==="
    
    tail -100 ~/.bash_history > "$BASE/tmp_history.txt" 2>/dev/null || true
    
    local session_json
    session_json=$(cat << EOF
{
  "id": "$session_id",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "duration_minutes": 0,
  "topics": [],
  "artifacts_created": [],
  "questions_asked": [],
  "decisions_made": []
}
EOF
)
    
    jq ".conversation_history += [$session_json]" "$CONTEXT_FILE" > "$BASE/tmp.json" && mv "$BASE/tmp.json" "$CONTEXT_FILE"
    
    update_timestamp
    echo "✓ Session saved to context_bridge"
}

load_context() {
    if [[ ! -f "$CONTEXT_FILE" ]]; then
        echo "✗ No context file found. Run 'init' first."
        return 1
    fi
    
    echo "=== Loading Context Bridge ==="
    echo "Project: $(jq -r '.project.name' "$CONTEXT_FILE")"
    echo "Vision:  $(jq -r '.project.vision' "$CONTEXT_FILE")"
    echo "Sessions: $(jq '.conversation_history | length' "$CONTEXT_FILE")"
    echo "Artifacts: $(jq '.code_artifacts | length' "$CONTEXT_FILE")"
    echo ""
    echo "Last modified: $(jq -r '.last_modified' "$CONTEXT_FILE")"
    echo ""
    
    jq -c '{
      project_summary: .project,
      recent_sessions: (.conversation_history[-5:]),
      pending_tasks: .system_state.pending_tasks,
      known_issues: .system_state.known_issues,
      success_patterns: .system_state.success_patterns
    }' "$CONTEXT_FILE"
}

export_snapshot() {
    local export_name="${1:-$(date +%Y%m%d_%H%M%S)}"
    local export_file="$EXPORTS_DIR/${export_name}.json"
    
    cp "$CONTEXT_FILE" "$export_file"
    echo "✓ Exported to $export_file"
    
    jq -r '
      "# OpenRoot Context Snapshot\n\n" +
      "**Project:** \(.project.name)\n" +
      "**Owner:** \(.project.owner)\n" +
      "**Created:** \(.created)\n" +
      "**Last Modified:** \(.last_modified)\n\n" +
      "## Vision\n\(.project.vision)\n\n" +
      "## Pending Tasks\n\(.system_state.pending_tasks[]? | "- " + .)\n\n" +
      "## Recent Sessions\n\(.conversation_history[-3:][]? | "### \(.id)\nDate: \(.timestamp)\n")\n" +
      "## Known Issues\n\(.system_state.known_issues[]? | "- " + .)
    ' "$CONTEXT_FILE" > "$EXPORTS_DIR/${export_name}.md"
    
    echo "✓ Human-readable summary: $EXPORTS_DIR/${export_name}.md"
    echo ""
    echo "To resume, run: cd /sdcard/openroot && ./bin/context_bridge.sh import $export_file"
}

import_snapshot() {
    local import_file="${1:-}"
    
    if [[ -z "$import_file" || ! -f "$import_file" ]]; then
        echo "Usage: ./context_bridge.sh import <export_file>"
        return 1
    fi
    
    echo "=== Importing Snapshot ==="
    echo "From: $import_file"
    
    cp "$import_file" "$CONTEXT_FILE"
    echo "✓ Context restored from snapshot"
    
    load_context
}

add_artifact() {
    local name="${1:-unnamed}"
    local description="${2:-No description}"
    local code_file="${3:-}"
    
    if [[ -f "$code_file" ]]; then
        local code_content
        code_content=$(base64 -w 0 < "$code_file")
        
        jq --arg n "$name" --arg d "$description" --arg c "$code_content" '
          .code_artifacts += [{
            "name": $n,
            "description": $d,
            "added": now | strftime("%Y-%m-%dT%H:%M:%SZ"),
            "content_base64": $c
          }]
        ' "$CONTEXT_FILE" > "$BASE/tmp.json" && mv "$BASE/tmp.json" "$CONTEXT_FILE"
        
        update_timestamp
        echo "✓ Artifact added: $name"
    else
        echo "✗ File not found: $code_file"
        return 1
    fi
}

extract_artifacts() {
    local output_dir="${1:-$EXPORTS_DIR/artifacts}"
    mkdir -p "$output_dir"
    
    local count
    count=$(jq '.code_artifacts | length' "$CONTEXT_FILE")
    
    echo "=== Extracting $count Artifacts ==="
    
    for i in $(seq 0 $((count - 1))); do
        local name
        name=$(jq -r ".code_artifacts[$i].name" "$CONTEXT_FILE")
        local code_b64
        code_b64=$(jq -r ".code_artifacts[$i].content_base64" "$CONTEXT_FILE")
        
        echo "$code_b64" | base64 -d > "$output_dir/$name"
        echo "  → $output_dir/$name"
    done
    
    echo "✓ All artifacts extracted to $output_dir"
}

full_summary() {
    echo "=========================================="
    echo "     OPENROOT CONTEXT BRIDGE SUMMARY"
    echo "=========================================="
    echo ""
    echo "PROJECT:"
    jq -r '.project | "  Name: \(.name)\n  Vision: \(.vision)\n  Core Principles: \(.core_principles | join(", "))"' "$CONTEXT_FILE"
    echo ""
    echo "SESSION HISTORY: $(jq '.conversation_history | length' "$CONTEXT_FILE") sessions"
    echo "CODE ARTIFACTS: $(jq '.code_artifacts | length' "$CONTEXT_FILE") stored"
    echo ""
    echo "SYSTEM STATE:"
    jq -r '.system_state | "  Status: \(.status)\n  Pending: \(.pending_tasks | length) tasks\n  Completed: \(.completed_tasks | length) tasks\n  Known Issues: \(.known_issues | length)"' "$CONTEXT_FILE"
    echo ""
    echo "PENDING TASKS:"
    jq -r '.system_state.pending_tasks[]? | "  • \(.)"' "$CONTEXT_FILE" || echo "  (none)"
    echo ""
    echo "KNOWN ISSUES:"
    jq -r '.system_state.known_issues[]? | "  ⚠ \(.)"' "$CONTEXT_FILE" || echo "  (none)"
    echo ""
    echo "SUCCESS PATTERNS:"
    jq -r '.system_state.success_patterns[]? | "  ✓ \(.)"' "$CONTEXT_FILE" || echo "  (none)"
    echo ""
    echo "=========================================="
    echo "Export command: ./context_bridge.sh export <name>"
    echo "Import command: ./context_bridge.sh import <file>"
    echo "=========================================="
}

case "${1:-summary}" in
    init)
        init_context
        ;;
    save)
        save_session
        ;;
    load)
        load_context
        ;;
    export)
        export_snapshot "${2:-}"
        ;;
    import)
        import_snapshot "${2:-}"
        ;;
    add-artifact)
        add_artifact "${2:-}" "${3:-}" "${4:-}"
        ;;
    extract-artifacts)
        extract_artifacts "${2:-}"
        ;;
    summary)
        full_summary
        ;;
    *)
        echo "Usage: ./context_bridge.sh [command]"
        echo ""
        echo "Commands:"
        echo "  init            — Create new context file"
        echo "  save            — Save current session to context"
        echo "  load            — Display loaded context summary"
        echo "  export [name]   — Export snapshot for closing window"
        echo "  import <file>   — Restore from snapshot"
        echo "  add-artifact    — Store a code file in context"
        echo "  extract-artifacts [dir] — Pull all artifacts to disk"
        echo "  summary         — Full project summary"
        ;;
esac
