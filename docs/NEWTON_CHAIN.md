# Newton-chain design

## Purpose

A Newton chain is an open, inspectable, cumulative reasoning pathway. It makes
the basis of a conclusion visible: definitions, common notions, assumptions,
postulates, evidence inputs, inference rules, proof steps, limitations, and
revision history.

It is designed for human and AI collaboration. A future contributor can propose
a new definition, challenge an assumption, add evidence, supply a counterexample,
derive a corollary, or extend a verified pathway without needing private session
context.

## Conditional proof

A Newton-chain conclusion has conditional meaning:

```text
(definitions, assumptions, evidence inputs, inference rules) ⊢ conclusion
```

A formal verification answers whether a conclusion follows under the declared
premises and rules. Empirical validation separately asks whether the premises,
measurements, and model adequately represent the system being studied.

A conclusion may be formally verified while remaining experimentally unconfirmed.
An observation may be measured while remaining insufficient to support a broader
model. Neither category is treated as a substitute for the other.

## Euclidean structure

| Element | Role |
|---|---|
| Definitions | Meaning, units, boundaries, variables, and identifiers |
| Common notions | General logical, arithmetic, dimensional, or accounting principles |
| Assumptions | Declared conditions accepted for one reasoning pathway |
| Postulates | Proposed model relationships or operating rules |
| Evidence records | Measurements, source extracts, observations, simulations, or test records |
| Propositions | Statements offered for derivation or examination |
| Proofs | Ordered derivation steps with cited premises and rules |
| Theorems | Stable propositions verified under a versioned rule set |
| Corollaries | Additional consequences of a theorem |
| Counterexamples | Cases that narrow, qualify, or invalidate a proposition |
| Reproduction records | Independent attempts to repeat empirical observations |
| Revision records | Changes to definitions, assumptions, evidence, rules, or conclusions |

## Open participation

Newton chains are not permission gates. Humans and AI collaborators may create
drafts, propose proofs, offer counterarguments, identify ambiguity, find
counterexamples, add evidence, or derive extensions.

Statement type and status preserve clarity without preventing exploration:

```text
draft → proposed → reviewed → formally verified → empirically supported
      → independently reproduced → superseded, narrowed, or withdrawn
```

A status describes what is currently known about a record. It does not prohibit
future work or prevent alternate branches.

## Cached pathways

A verified path can be reused when its declared dependency state is unchanged.
The cache is a reusable certificate, not an assertion that reality has stopped
changing.

```text
unchanged dependency hashes
→ reuse a verified proof result
→ avoid repeating equivalent computation

changed definition, assumption, evidence, or rule
→ mark dependent results stale
→ reevaluate only reachable downstream conclusions
→ retain the prior result and its historical dependency state
```

For a proof object \(P\), validity at a given state requires:

\[
\operatorname{valid}(P) =
\bigwedge_{d \in \operatorname{deps}(P)}
\left(
\operatorname{hash}_{stored}(d)
=
\operatorname{hash}_{current}(d)
\right)
\]

This permits targeted recomputation rather than full recomputation.

## Receipts and public records

A Newton-chain receipt connects a claim, candidate change, proof step, or
evidence record to its inspectable operational basis:

- Source artifact identifiers and content hashes where appropriate.
- Declared definitions, assumptions, and inference rules.
- Evidence inputs, validation commands, and observed outcomes.
- Timestamp, provenance, reviewer notes, and revision decision.
- Stated scope, uncertainty, and conditions that would require reevaluation.

Public Git history should contain reviewable schemas, examples, summaries, and
sanitized proof records. Private local databases, raw operational records,
credentials, personal information, and unreviewed evidence remain outside the
public record unless deliberately reviewed and prepared for publication.

## Scope discipline

Each conclusion should state:

- What it establishes.
- The assumptions and evidence it depends on.
- Its stated environment, boundary, and units.
- What it does not establish.
- What evidence, counterexample, or revised premise would change it.

This makes ambitious work reusable without presenting a model, simulation, or
proposal as a measured physical, legal, financial, safety, or deployment result.

## Thermal example

The example in `EXAMPLES/thermal_energy_bound.yaml` derives only a bounded
thermal-energy quantity from \(Q = m c_p \Delta T\) under declared assumptions.
It does not establish thermal collection efficiency, durability, safety,
electricity generation, mobility, economics, or field readiness.
