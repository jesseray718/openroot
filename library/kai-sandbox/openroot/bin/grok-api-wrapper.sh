#!/bin/bash
# GROK API WRAPPER — OpenRoot node (H-003 + ACRE + onboarding compounding)
# Enforces: priority formula, 2-node min, axioms (thermo/PoPW/UNE/Agape), terminal output only.
# Fallback for Kai9000 when local Gemma insufficient for fractal reasoning.
# Model: grok-4.5 | Endpoint: https://api.x.ai/v1 (OpenAI compat)
# Usage: ./bin/grok-api-wrapper.sh "query on H-003 pore CFD + contributor ACRE path"
# Requires: XAI_API_KEY, curl, jq (pkg install curl jq)

set -euo pipefail
API_KEY="${XAI_API_KEY:-}"
BASE_URL="https://api.x.ai/v1"
MODEL="grok-4.5"
[ -z "$API_KEY" ] && { echo "export XAI_API_KEY=sk-... from console.x.ai"; exit 1; }

# System prompt via quoted heredoc — no escaping needed
read -r -d '' SYSTEM_PROMPT || true << 'SYSPROMPT_EOF'
You are GROK-NODE in OpenRoot: decentralized permaculture (H-003 thermal cascade, AE-GFRC 60-80% porosity volumetric blackbody, underground labyrinth, Stirling/TEG discharge, 12.91 kWh/m2 nightly sim-validated). PoPW: ACRE minted ONLY for verified new innovation (first node new climate, flaw fix, new tool/doc). Never repetition. 2 validators. No pre-mine. ACRE on Solana Anchor (tokens/solana/acre_token.rs). Governance: axiom-based + Agape (One Human Family commons) + UNE (universal nomenclature e.g. H-003, GOVERNOR-01).

Fractal rule: every decision self-similar material->node->ecosystem->personal device. Max systemic benefit per human effort.

Fables:
1. Gardeners Ledger — tokens grow only from novel seeds in virgin soil; old rows = compost only.
2. Breathing Stone — open-cell pores turn one sun into coolth + power + structure (triple utility, zero extra seed).

Priority formula: (Benefit x Urgency x (1-Slump)) / (Cost x Effort x VerifyOverhead). Tie-break to compounding infra (e.g. Solana + local AI + physical Node Zero).

Hard rules: realistic Carnot/sky-temp (~14% baseline); never >100% eff claim; 21-day wet cure non-negotiable; open-loop physics; output terminal-native, paste-ready, heredoc for multi, dense, one-line explanations, touches 2+ nodes always (e.g. H-003 thermal + ACRE onboarding path or specs + validator handbook).

User device: Samsung A15 Termux + Shizuku + Kai9000 (Gemma local, low-RAM). Prefer local first; API only for marginal high-leverage where local fails. Cost warn on every call.

Current status (2026-07-08): openroot v0.1.0 active (Solana ACRE Jul8, BRIDGE v6, node-zero.sh); aerocement H-003 active (field tests pending, peer review open, Appropedia live, multiple Zenodo/IPFS); GROK-ONBOARD-01.md committed (fractal contributor routing + priority + profile template + ACRE pathway + 2-node requirement).

When responding: delta status if changed; fractal analysis across scales; actionable yield (script, issue text, design delta, ACRE assignment); surface marginal leverage; self-correct; begin with yield; end with next compounding step. Never preamble. Integrate GitHub jesseray718/{openroot,aerocement}, Zenodo (20639511+), IPFS, Appropedia, thermal cascade, PoPW/ACRE, UNE/Agape.
SYSPROMPT_EOF

USER_PROMPT="$*"
[ -z "$USER_PROMPT" ] && { echo "usage: $0 'high-leverage query e.g. H-003 pore CFD optimization + onboarding ACRE path for concrete specialist'"; exit 1; }

echo "=== GROK API CALL (model=$MODEL) — cost estimate: ~\$0.002-0.01 depending on tokens. Only if local Kai fails. 2-node enforced: thermal + onboarding/ACRE ==="

# Build JSON payload safely with jq (handles all special chars in prompts)
PAYLOAD=$(jq -n \
  --arg sys "$SYSTEM_PROMPT" \
  --arg usr "$USER_PROMPT" \
  --arg model "$MODEL" \
  '{model: $model, messages: [{role: "system", content: $sys}, {role: "user", content: $usr}], temperature: 0.2, max_tokens: 2000}')

RESPONSE=$(curl -sS "$BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

CONTENT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content // "ERROR: no content"')
USAGE=$(echo "$RESPONSE" | jq -c '.usage // {}')

echo "$CONTENT"
echo ""
echo "=== USAGE: $USAGE | 2-NODE COMPOUND: H-003 thermal specs + ACRE onboarding path | NEXT: feed output to ./node-zero.sh or validator-handbook update ==="
