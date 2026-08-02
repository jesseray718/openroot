#!/bin/bash
# Surgical Loop Orchestrator
# Phone -> OptiPlex -> Phone (η-preserving)

set -e

# CONFIGURATION
PHONE_ROOT="/data/data/com.termux/files/home/openroot"
OPTIPLEX_USER="jesse"
OPTIPLEX_IP="192.168.1.193"
TARGET_FILE="$PHONE_ROOT/une/computational_flow/core_atomic.py"
TMP_DIR="$PHONE_ROOT/tmp"
LATTICE_SCRIPT="$PHONE_ROOT/bin/nanobot_lattice.py"
METRICS_SCRIPT="$PHONE_ROOT/bin/extract_metrics.py"
PROMPT_SCRIPT="$PHONE_ROOT/bin/lattice_to_llm.py"
VERIFY_SCRIPT="$PHONE_ROOT/bin/verify_and_learn.py"
AXIOM_DB="$PHONE_ROOT/une/axiom_lattice.json"

echo "=== OPENROOT SURGICAL LOOP ==="
echo "Target: $TARGET_FILE"
echo "OptiPlex: $OPTIPLEX_USER@$OPTIPLEX_IP"

# --- STEP 1: MEASURE & MINT ACRE ---
echo "[1/6] Measuring metrics and minting ACRE..."
mkdir -p "$TMP_DIR"
python3 "$METRICS_SCRIPT" "$TARGET_FILE" > "$TMP_DIR/target.json"
python3 "$LATTICE_SCRIPT" "$AXIOM_DB" "$TMP_DIR/target.json" 8 > "$TMP_DIR/last_acre.json"
echo "   ✓ ACRE minted: $(cat $TMP_DIR/last_acre.json | grep -o '"eta": [0-9.]*' || echo "N/A")"

# --- STEP 2: GENERATE CONSTRAINED PROMPT ---
echo "[2/6] Generating constrained prompt..."
python3 "$PROMPT_SCRIPT" "$TMP_DIR/last_acre.json" "$TARGET_FILE" > "$TMP_DIR/llm_prompt.txt"
echo "   ✓ Prompt generated ($(wc -c < $TMP_DIR/llm_prompt.txt) bytes)"

# --- STEP 3: TRANSFER TO OPTIPLEX ---
echo "[3/6] Transferring prompt to OptiPlex..."
ssh -o StrictHostKeyChecking=no "$OPTIPLEX_USER@$OPTIPLEX_IP" "mkdir -p /home/$OPTIPLEX_USER/openroot/tmp"
scp -o StrictHostKeyChecking=no "$TMP_DIR/llm_prompt.txt" "$OPTIPLEX_USER@$OPTIPLEX_IP:/home/$OPTIPLEX_USER/openroot/tmp/llm_prompt.txt"
echo "   ✓ Transferred"

# --- STEP 4: RUN MODEL ON OPTIPLEX ---
echo "[4/6] Running coding model on OptiPlex (this may take a minute)..."
# Using password-based auth via SSH agent or prompt. 
# If you have ssh-agent running, it uses keys. Otherwise, it prompts for password.
ssh -o StrictHostKeyChecking=no "$OPTIPLEX_USER@$OPTIPLEX_IP" \
  "cat /home/$OPTIPLEX_USER/openroot/tmp/llm_prompt.txt | \
   OLLAMA_TEMPERATURE=0.2 ollama run codellama:7b-instruct \
   > /home/$OPTIPLEX_USER/openroot/tmp/llm_output.txt"

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Model execution failed on OptiPlex."
    exit 1
fi
echo "   ✓ Model finished"

# --- STEP 5: PULL RESULT BACK ---
echo "[5/6] Pulling optimized code back to phone..."
scp -o StrictHostKeyChecking=no "$OPTIPLEX_USER@$OPTIPLEX_IP:/home/$OPTIPLEX_USER/openroot/tmp/llm_output.txt" "$TMP_DIR/llm_output.txt"
echo "   ✓ Pulled ($(wc -l < $TMP_DIR/llm_output.txt) lines)"

# --- STEP 6: VERIFY & LEARN ---
echo "[6/6] Verifying η and learning..."
python3 "$VERIFY_SCRIPT" "$TMP_DIR/last_acre.json" "$TMP_DIR/llm_output.txt" "$TARGET_FILE"

RESULT=$?
if [ $RESULT -eq 0 ]; then
    echo "✅ SUCCESS: Loop complete. η increased. Code accepted."
else
    echo "❌ REJECTED: η did not increase. Code discarded."
fi

echo "=== END LOOP ==="
