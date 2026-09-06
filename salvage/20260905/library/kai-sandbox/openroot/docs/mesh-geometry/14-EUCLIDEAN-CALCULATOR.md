# AX-022 & PO-017 — Euclidean Calc v0.1 Review (calculator)

Source: calculator_script.md (openroot v0.1, the 8-step pipeline). This is the ancestor of the whole formal system: state axioms → form postulates → apply permaculture → compute. Status: shipped [in-progress].

## Axiom

AX-022: A reasoning pipeline must be able to fail. Every report states at least one observation that would falsify or lower its own conclusion. A pipeline that always succeeds is a formatter, not a reasoner. (Popper: falsifiability demarcates.)

## Postulate

PO-017: Lexical overlap measures topical adjacency, not entailment. Axiom selection by keyword match is retrieval and is labeled retrieval; a confidence number derived from keyword counts is a retrieval score, not an epistemic probability. [tested by inspection of step1/step5 — relevance = |keyword ∩ statement words|]

## Audit findings

1. The "confidence %" in step 5 is arithmetic on keyword overlap. As shipped it decorates the report with false precision. Renamed retrieval_score; AX-022 adds a falsification line to every report.
2. C_r = 0.618 shipped as "optimal proportion constant." No evidence exists that φ⁻¹ is an optimum for knowledge conversion or anything else here (Markowsky 1992; Livio, The Golden Ratio, 2002). Removed as a default; may be reintroduced only with a measured justification.
3. The genuinely strong core: the ledgered axiom/postulate store — stable IDs, from_axioms provenance, add/remove CLI — is a citable knowledge graph and the correct foundation. It is the same structural pattern as the NOMOS hash chain minus hashing. Upgrade path: chain SHA-256 of each axiom/postulate record to make the formal system tamper-evident. [concept]

## Prior art (name the lineage honestly)

- The 8-step pipeline is Euclid's method as workflow: definitions → postulates → common notions → propositions (Elements, c. 300 BC). Say so in the README; it strengthens the repo.
- good/input is a descendant of Bentham's felicific calculus (1789): his seven dimensions (intensity, duration, certainty, propinquity, fecundity, purity, extent) map onto benefit, urgency, and verification terms. Modern field: multi-criteria decision analysis (MCDA; Saaty's AHP). Standing critique that applies to us: quantified "good" invites Goodhart's law — when a measure becomes a target, it ceases to be a good measure. AX-022 and two-validator verification are the countermeasures.

## Permaculture mapping

- Design from Patterns to Details — axioms before postulates before application is exactly this principle as method
- Use Small & Slow Solutions — stdlib-only, single-file, state.json increments; no dependency towers
- Creatively Use & Respond to Change — step 4 (axiom refinement from feedback) builds revision into the formal system
- Obtain a Yield — every deepdive run emits a dated, reviewable report artifact

## Evaluation rule verdict

Relabeling confidence and deleting C_r costs minutes and removes the two largest false-precision surfaces in the founding tool. ACCEPT. Hash-chaining the axiom ledger: moderate effort, high benefit (tamper-evident formal system, aligns with NOMOS). ACCEPT as next milestone.

Status: CLI + ledger [in-progress]; keyword retrieval [tested, relabeled]; confidence-as-probability [rejected]; hash-chained ledger [concept].
