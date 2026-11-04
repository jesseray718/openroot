# OpenRoot Commons — Constitution (v1.0)

Status: ATTESTED (owner covenant, not a derived proof). Sealed by hash on commit.

## Layer 1 — Bill of Rights (unalterable)
Every human holds these; no amendment, statute, or ordinance may violate them:
1. Clean water.
2. A clean vessel — baseline shelter, heat, and compute.
3. Right to fork. Forking is always legal; forks keep their evidence chain.
4. Right to audit. Every sealed claim reproducible by any node.
5. Right to exit with your data. No lock-in, ever.
Enforcement rule: least_first (N07). Where a rule and a right conflict, the right wins.

## Layer 2 — Structures and Powers
Three branches + one ledger:
- Legislative (Bounty Board): proposes bounties, budgets credits. Cannot verify or spend.
- Executive (Builder Loop): executes bounties, merges code, on ratified statutes only.
- Judicial (Audit Verifiers): independently recompute proofs; strike unsound claims.
- Constabulary (Friction Ledger): records everything, publishes receipts, cannot be silenced.

Trust model: a claim is truth iff independently reproduced. A DERIVED theorem or a
green merge requires >= 2 independent reproductions. Single-source = ATTESTED, reduced standing.

## Layer 3 — Amendments
Proposed -> measured benefit evidence (PoPW) -> 21-day cure (N15) -> ratified by >= 3
independent nodes reproducing the proposed sealed state. Rights layer is out of scope: forever.

## Layer 4 — Statutes (machine-checkable)
Statutes live in statutes/checks.jsonl as executable conditions, not prose.
Default statute: merge to main iff proof_resolves AND independent_reproduction >= 2 AND ci_green.

## Layer 5 — Code
Every artifact hangs on a blob (N08) with measured delta (N09). Need-gate (N11):
no module lands while the canon path to it is empty.

## Layer 6 — Ordinances (node-local)
Each node sets local policy. Ordinances may be stricter than statutes, never looser.
Standing provision (agility valve): any node may act unilaterally on its own turf
under fork-and-prove, then present results for retroactive ratification during cure.
A blocked experimenter proceeds; a reckless one answers to the auditors.

## Checks and Balances
- Veto: a verifier vetoes by FAILING TO REPRODUCE a sealed hash. Automatic, recorded
  as a friction event. 2/3 of active verifiers override a spurious veto.
- Payment: credits move only after seal (B4: monetize-after-chain).
- Safety: interlocks, deadman switches, and guards are STATUTE, not feature. Bounties
  for machines without them cannot be sealed.

## Federalism
Repo = federal. Spokes = states (own ordinances under LATTICE.md). Nodes = municipalities.
Forks = secession — always legal (Layer 1).
