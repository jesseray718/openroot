# Newton-chain inference rules

## Rule categories

Inference rules must be explicit, versioned, and scoped. A rule is a reusable
description of a valid transformation from stated premises to a conclusion.

## Core rules

| ID | Rule | Permitted use |
|---|---|---|
| RULE-LOGIC-001 | Modus ponens | From `P` and `P → Q`, derive `Q` |
| RULE-LOGIC-002 | Conjunction | From `P` and `Q`, derive `P ∧ Q` |
| RULE-LOGIC-003 | Case analysis | Derive a conclusion only when all declared cases support it |
| RULE-ALGEBRA-001 | Algebraic substitution | Substitute equal quantities within declared units and domains |
| RULE-UNIT-001 | Dimensional consistency | Reject or hold a calculation when dimensions do not reconcile |
| RULE-INTERVAL-001 | Interval propagation | Propagate bounded uncertainty through a declared formula |
| RULE-ENERGY-001 | Thermal energy relation | Under declared conditions, use `Q = m c_p ΔT` |
| RULE-EVIDENCE-001 | Evidence reference | Attach an observation or source record without converting it into a broader conclusion |
| RULE-SCOPE-001 | Scope limitation | State exclusions that do not follow from the premises |
| RULE-DEPENDENCY-001 | Dependency validation | Reuse a cached result only when all declared dependency hashes match |

## Evidence rule

An evidence record can support a premise only within its documented collection
conditions, units, calibration, method, time interval, and uncertainty. A
citation, simulation, or observation is not automatically a proof of a broader
claim.

## Counterexample rule

A credible counterexample does not erase historical work. It narrows, qualifies,
or invalidates the conclusion within the stated scope, and records why.

## Cache rule

A proof certificate may be reused only when its definition, assumption, evidence,
rule-set, and environment dependencies are unchanged. If a dependency changes,
the record becomes stale pending reevaluation; it is not silently treated as
current.
