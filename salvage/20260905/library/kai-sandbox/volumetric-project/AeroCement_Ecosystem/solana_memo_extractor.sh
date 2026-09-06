#!/bin/bash
# AEROCENT SOLANA MEMO EXTRACTION
# PURPOSE: Retrieve memo from self-transfer and anchor to thesis ledger

TX_SIG="2fXw4y3pV74zk6pi2dCBTHKJJ69zfvmaRC4ng3sxqY5g9JzNUtdhGrxonL4dHw64TbcVK3C4YqAmskSdow7MYyX8"

echo "[+] INITIATING MEMO EXTRACTION..."
echo ""

# PREREQUISITE CHECK: Is solana CLI installed?
if ! command -v solana &> /dev/null; then
    echo "[!] ERROR: solana CLI not found."
    echo "    Install via: sh -c \"$(curl -sSfL https://release.anza.stable/mainnet/install)\""
    echo "    OR use browser alternative below."
    
    # FALLBACK: Web verification instructions
    cat << WEBEOF
======================================================================
WEB-BASED VERIFICATION INSTRUCTIONS
======================================================================
1. Go to: https://solscan.io/tx/${TX_SIG}
   OR https://explorer.solana.com/tx/${TX_SIG}

2. Look for these fields:
   [a] Memo Program Instruction (usually program ID: MemoSq4jQ...)
   [b] Text content of memo
   [c] Confirm finality status

3. COPY the memo text exactly.

4. Paste it below when prompted.
======================================================================

[INFO] If you cannot access Solana explorer right now, proceed offline:
