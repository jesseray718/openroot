#!/bin/bash
GROQ_API_KEY="${GROQ_API_KEY:-}"
MODEL="llama-3.3-70b-versatile"
MAX_TOKENS=2048
check_key() {
    if [ -z "$GROQ_API_KEY" ]; then
        echo "Get free key at console.groq.com"
        echo "Then: echo 'export GROQ_API_KEY=\"gsk_yourkey\"' >> ~/.bashrc && source ~/.bashrc"
        exit 1
    fi
}
SYSTEM='You are Kai 9000 — co-pilot to Jesse McMillen, builder of OpenRoot. The thermal loop: Fresh air → Desiccant (at fresh air intake) → Underground labyrinth (FILLED SOLID with wet open-cell aerocement, air through millions of pores, 35°F out) → Cold Tank B (copper coil, radiative lid) → Panel inlet → Solar panel (air through volumetric aerocement, 98% absorption, 77°C out) → Hot Tank A (copper coil, heat-sink lid) → Stirling engine (between tanks, belt drive) → back to desiccant. Hard constraints: 21-day wet cure. Desiccant at fresh air intake. Tunnel filled solid not lined. Two separate tanks. No patents. Ever. Greatest good, least effort. All code as complete copy-paste blocks.'
ask() {
    pkg install -y curl jq 2>/dev/null 1>/dev/null
    PAYLOAD=$(jq -n --arg m "$MODEL" --arg s "$SYSTEM" --arg u "$1" --argjson t $MAX_TOKENS '{model:$m,max_tokens:$t,messages:[{role:"system",content:$s},{role:"user",content:$u}]}')
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    curl -s -H "Authorization: Bearer $GROQ_API_KEY" -H "Content-Type: application/json" -d "$PAYLOAD" "https://api.groq.com/openai/v1/chat/completions" | jq -r '.choices[0].message.content // .error.message'
    echo ""
}
interactive() {
    echo "⚡ KAI 9000 | quit to exit"
    while true; do
        printf "Jesse → "
        read -r INPUT
        case "$INPUT" in
            quit|q) echo "Build it."; break ;;
            "") continue ;;
            *) ask "$INPUT" ;;
        esac
    done
}
check_key
case "${1:-}" in
    --interactive|-i) interactive ;;
    "") interactive ;;
    *) ask "$*" ;;
esac
