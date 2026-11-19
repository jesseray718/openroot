# Newton Chain Contract

A Newton Chain receipt links a claim or candidate change to:

- source artifact identifiers
- SHA-256 evidence where appropriate
- stated assumptions
- validation commands
- observed outcome
- timestamp
- reviewer decision

Public Git history receives sanitized schemas and examples, never live local
databases or private evidence records.


## Conditional conclusions

A Newton-chain conclusion records what follows under its declared definitions,
assumptions, evidence inputs, and inference rules. Formal derivation and
empirical validation are recorded separately.

## Reusable pathways

A verified pathway may be reused when the subject content hash, declared
dependency fingerprint, inference-rule version, and execution environment match
the recorded receipt. When a dependency changes, affected results become stale
pending targeted reevaluation; historical receipts remain available.

See the [evidence ledger](newton_chain/README.md),
[Euclidean elements](newton_chain/ELEMENTS.md),
[proof-object schema](newton_chain/SCHEMA.yaml),
[inference rules](newton_chain/INFERENCE_RULES.md), and
[bounded thermal example](newton_chain/EXAMPLES/thermal_energy_bound.yaml).
