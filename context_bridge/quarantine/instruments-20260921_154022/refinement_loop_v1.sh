#!/usr/bin/env bash
set -eu
export OLLAMA_HOST=http://localhost:11434
cd /home/jesse/openroot

print_stage() { printf '[%s] %s\n' "$1" "$2"; }
log_lesson() { sqlite3 data/lessons.db "INSERT INTO lessons (domain,mistake,root_cause,correction,cost,source) VALUES('$1','$2','$3','$4','${5:-1 cycle}','session');" }

init_db() {
    sqlite3 data/refinement.db "CREATE TABLE IF NOT EXISTS iterations (id INTEGER PRIMARY KEY AUTOINCREMENT, doc_ref TEXT, attempt INTEGER, content TEXT, grade TEXT, accepted INTEGER DEFAULT 0)"
    sqlite3 data/refinement.db "CREATE TABLE IF NOT EXISTS templates (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, prompt_template TEXT, rubric TEXT)"
    print_stage "db_init" "refinement.db initialized"
}

register_template() {
    local name="$1" prompt="$2" rubric="$3"
    sqlite3 data/refinement.db "INSERT OR REPLACE INTO templates (name,prompt_template,rubric) VALUES ('$name', '$(echo "$prompt" | sed "s/'/''/g")', '$(echo "$rubric" | sed "s/'/''/g")')"
    print_stage "template" "$name registered"
}

doc_exists() {
    [ -f "$1" ] && [ -s "$1" ]
}

coder_edit() {
    local instruction="$1" context="$2"
    timeout 120 ollama run qwen2.5-coder:7b "$instruction" <<<"$context" 2>/dev/null || echo "CODER_OFFLINE"
}

grader_score() {
    local content="$1" rubric="$2"
    timeout 90 ollama run qwen2.5:3b "Grade this output. Rubric: $rubric. Output exactly 3 lines: VERDICT: PASS|FAIL | ACCURACY: high|medium|low | SPEED: fast|slow | FIX: <one-line improvement>" 2>/dev/null <<<"$content" || echo "GRADER_OFFLINE"
}

loop_until_pass() {
    local doc_ref="$1" rubric="$2" max_attempts="${3:-5}"
    local attempt=0 content="" grade="" accepted=0
    
    print_stage "loop_start" "max attempts: $max_attempts"
    
    while [ $attempt -lt $max_attempts ] && [ $accepted -eq 0 ]; do
        attempt=$((attempt + 1))
        print_stage "attempt" "$attempt/$max_attempts"
        
        if doc_exists "/home/jesse/openroot/data/${doc_ref}.txt"; then
            context=$(cat "/home/jesse/openroot/data/${doc_ref}.txt" | head -50)
        else
            context="NO_PREVIOUS_CONTEXT"
        fi
        
        content=$(coder_edit "Edit/improve: $rubric. Previous context: ${context:0:500}" "$context")
        
        grade=$(grader_score "$content" "$rubric")
        
        print_stage "grade" "$grade"
        
        echo "$content" > "/home/jesse/openroot/data/${doc_ref}_attempt${attempt}.txt"
        
        sqlite3 data/refinement.db "INSERT INTO iterations (doc_ref, attempt, content, grade) VALUES ('$doc_ref', $attempt, '$(echo "$content" | sed "s/'/''/g")', '$grade')"
        
        if echo "$grade" | grep -q "VERDICT: PASS"; then
            accepted=1
            print_stage "accept" "document: data/${doc_ref}_attempt${attempt}.txt"
        else
            local fix=$(echo "$grade" | grep "FIX:" | sed 's/FIX: //')
            print_stage "fix" "applying: $fix"
            if [ -z "$fix" ] || [ "$fix" = "<one-line improvement>" ]; then
                print_stage "warn" "no concrete fix provided, injecting iteration"
                fix="improve accuracy and completeness"
            fi
        fi
        
        sleep 1
    done
    
    if [ $accepted -eq 0 ]; then
        log_lesson "refinement_loop" "max attempts reached without pass" "rubric too strict or grader inconsistent" "adjust rubric or increase max_attempts" "failed_${attempt}_attempts"
        print_stage "fail" "max attempts exceeded - manual review needed"
        return 1
    fi
    
    mv "/home/jesse/openroot/data/${doc_ref}_attempt${attempt}.txt" "/home/jesse/openroot/docs/${doc_ref}.md"
    print_stage "banked" "docs/${doc_ref}.md"
    return 0
}

main() {
    init_db
    print_stage "ready" "refinement_loop_v1 loaded - 7B coder + 3B grader + SQLite ledger"
    print_stage "usage" "bash bin/refinement_loop_v1.sh loop <doc_name> '<rubric>' <max_attempts>"
    print_stage "example" "bash bin/refinement_loop_v1.sh loop my_article 'Explain solar thermal systems clearly' 3"
    print_stage "[exit=0]" ""
}

case "${1:-help}" in
    loop) shift; loop_until_pass "$@" ;;
    *) main ;;
esac
