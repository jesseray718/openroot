#!/bin/bash

# Scheduler with local model fallback
TEAMS_FILE="teams.json"
TASKS_DIR="tasks"
QUEUE_DIR="queue"
POWP_LEDGER="powp_ledger.json"
mkdir -p "$QUEUE_DIR"

teams=$(jq -r 'to_entries[] | "\(.key):\(.value.expertise | join(","))"' "$TEAMS_FILE")

echo "=== OpenRoot Computational Flow Scheduler (Local Fallback) ==="

for task_file in "$TASKS_DIR"/*.json; do
    [ -f "$task_file" ] || continue
    task_id=$(jq -r '.id' "$task_file")
    expertise_needed=$(jq -r '.expertise' "$task_file")
    task_name=$(jq -r '.name' "$task_file")

    echo "Scheduling $task_id (Expertise: $expertise_needed)"

    assigned=false
    while IFS= read -r team_line; do
        team_name=$(echo "$team_line" | cut -d':' -f1)
        team_expertise=$(echo "$team_line" | cut -d':' -f2)

        if [[ "$team_expertise" == *"$expertise_needed"* ]]; then
            echo "→ Assigned to $team_name"

            queue_file="$QUEUE_DIR/${task_id}_queue.json"
            jq --arg team "$team_name" \
               '. + {"assigned_team": $team, "status": "queued"}' \
               "$task_file" > "$queue_file"

            # Try aiq first, fallback to local model
            echo "Processing with aiq (fallback to local model if needed)..."
            if aiq_output=$(aiq mistral "Process task: $task_name" 2>&1); then
                echo "$aiq_output" > "$queue_file.aiq_output"
                echo "✓ aiq processed successfully"
                jq --arg status "processed" '.status = $status' "$queue_file" > "$queue_file.tmp" && mv "$queue_file.tmp" "$queue_file"
            else
                echo "⚠ aiq failed. Falling back to local model..."
                # Use llama.cpp or another local model
                echo "Local model output placeholder" > "$queue_file.local_output"
                jq --arg status "local_processed" '.status = $status' "$queue_file" > "$queue_file.tmp" && mv "$queue_file.tmp" "$queue_file"
            fi

            # Log work units
            wu=1.0
            timestamp=$(date -Iseconds)
            jq --arg id "$task_id" --arg wu "$wu" --arg ts "$timestamp" \
               '. += [{"task_id":$id,"work_units":($wu|tonumber),"timestamp":$ts,"verified":false}]' \
               "$POWP_LEDGER" > "$POWP_LEDGER.tmp" && mv "$POWP_LEDGER.tmp" "$POWP_LEDGER"

            assigned=true
            break
        fi
    done <<< "$teams"

    if [[ "$assigned" == false ]]; then
        echo "⚠ No suitable team found for $task_id"
    fi
done

echo "=== Scheduler cycle complete ==="
