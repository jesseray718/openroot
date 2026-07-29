#!/bin/bash
# OpenRoot Computational Flow Scheduler v2 (PoPW)
# expertise match → assign → emit work_units to ACRE ledger
# nodes: H-003 | ACRE | UNE | GitHub jesseray718/openroot

TEAMS_FILE="teams.json"
TASKS_DIR="tasks"
POW_LOG="logs/pow_log.json"
mkdir -p logs

[ -f "$POW_LOG" ] || echo '[]' > "$POW_LOG"

teams=$(jq -r 'to_entries[] | "\(.key):\(.value.expertise | join(","))"' "$TEAMS_FILE")

echo "=== OpenRoot Swarm v2 @ computational_flow ==="
for task_file in "$TASKS_DIR"/*.json; do
    [ -f "$task_file" ] || continue
    task_id=$(jq -r '.id' "$task_file")
    expertise_needed=$(jq -r '.expertise' "$task_file")
    priority=$(jq -r '.priority // "medium"' "$task_file")
    echo "Scheduling $task_id [$priority] (needs: $expertise_needed)"

    assigned=false
    while IFS= read -r team_line; do
        team_name=$(echo "$team_line" | cut -d':' -f1)
        team_expertise=$(echo "$team_line" | cut -d':' -f2)
        if [[ "$team_expertise" == *"$expertise_needed"* ]]; then
            echo "→ Assigned to $team_name"
            case "$priority" in high) wu=2.5 ;; medium) wu=1.0 ;; *) wu=0.5 ;; esac
            ts=$(date -Iseconds)
            jq --arg id "$task_id" --arg team "$team_name" --arg wu "$wu" --arg ts "$ts" \
               '. += [{"task_id":$id,"team":$team,"work_units":($wu|tonumber),"timestamp":$ts,"verified":false,"source":"comp_flow_v2"}]' \
               "$POW_LOG" > "$POW_LOG.tmp" && mv "$POW_LOG.tmp" "$POW_LOG"
            assigned=true
            break
        fi
    done <<< "$teams"

    [ "$assigned" = false ] && echo "⚠ No team match for $task_id"
done

echo "=== PoPW ledger: $(jq '. | length' "$POW_LOG") tasks logged ==="
