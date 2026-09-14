# ROLE PROPOSAL REQUEST — addressed to Grok
# You are being offered ONE seat in the OpenRoot loop. Propose your role.

## CONTEXT (read-only, do not modify anything)
OpenRoot is an offline-first appropriate-tech mesh (Termux node + OptiPlex 3060).
Selection of work is done by rc_circuit.py (RC low-pass + McCulloch-Pitts gates,
winner-take-all on resistance). Cross-node communication uses the Q&A loop
engine (SQLite questions/answers tables, SHA256-hashed IDs, confidence-weighted
resistance discounts). All completed work is sealed to SHA256-chained JSONL.

## OPEN ROLES (propose exactly one)
- capability_scanner: enumerate exposable functions/abilities across repos,
  build the yield table (what each function produces per unit effort).
- yield_analyst: score scraped capabilities by eta gain, rank for bounty pricing.
- contract_drafter: draft Solana/Anchor specs for PoPW attestations
  (thermal.ledger joule events -> ACRE tokens).
- bounty_board_architect: design the on-chain bounty board consuming the
  capability table + ACRE + STEP settlement.

## REQUIRED OUTPUT FORMAT (JSON, save as circuits/proposals/grok-proposal-<ts>.json)
{
  "role": "<one of the four>",
  "why_this_role": "<= 2 sentences",
  "capability_tags": ["<tag>", "..."],
  "first_task_spec": {
    "action": "<concrete verb>",
    "inputs": ["<path or table>"],
    "outputs": ["<path or table>"],
    "check": "<how the 3B grader verifies it>"
  },
  "qa_interface": {
    "questions_you_answer": ["<what queries other nodes may send you>"],
    "expected_confidence": 0.0
  },
  "risk_notes": ["<what could go wrong>"]
}

## CONSTRAINTS (non-negotiable)
1. READ-ONLY first task. No writes to seals, ledgers, or repos without a gate.
2. Your proposal is graded by the 3B grader (aider_task_runner.py pattern),
   then sealed by scribe.py gate. A rejected proposal is archived, not retried blindly.
3. No central authority claims. You are a node, not an owner.
4. Idempotency: re-running your first task must be a no-op after success.

## SUBMISSION
Echo the JSON to stdout AND write the file. The fleet operator (jesse) runs the gate.
