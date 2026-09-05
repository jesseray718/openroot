# ACRE Smart Contract Spec (status: concept — DO NOT DEPLOY YET)
Why not now: minting requires VERIFIED physical work; the verification oracle
doesn't exist yet. A mintable token before the oracle = premine by another name,
and it would burn the zero-premine credibility that is ACRE's entire moat.
## Design, when ready
- Solana SPL token; freeze authority burned at genesis (no one can freeze holders)
- Mint authority: 2-of-3 multisig (founder + two community verifiers) until oracle
- Every mint MUST reference: LEDGER.jsonl seq hash + evidence CID on IPFS
  (photos/video of the work) + verifier signatures
- Git ledger stays the source of truth; the chain mirrors it, never leads it
- Path: devnet test → 3 verified work events on the paper ledger → mainnet
Interim truth: LEDGER.jsonl + Solana memo anchors ARE the honest chain today.
[paste Part 1 above]
