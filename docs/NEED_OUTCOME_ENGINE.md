<!-- SPDX-License-Identifier: Apache-2.0 -->
# Need-to-Outcome Engine 0.1.1

A deterministic, standard-library-only foundation for evidence-linked
appropriate-technology comparisons and reusable computational pathways.

## Implemented

- Versioned request contract enforced by Python validation.
- Explicit required-gate handling: PASS, HOLD, EXCLUDE.
- Evidence references and comparison-basis identifiers for measurements.
- Pareto comparison among eligible options using supplied point estimates.
- Exact-request cache keyed by full request and implementation hash.
- Cache-result integrity checking.
- SQLite execution receipts.
- Dependency ordering and approval-intervention propagation.
- Isolated regression tests.

## Not implemented

This is not a deployment controller or a complete mission optimizer.
It does not verify the truth of supplied evidence or gate attestations.
It does not resolve permissions, monitor files, inspect actual corpus
generations, execute planned workers, grant approvals, call models,
build embeddings, or connect the existing OpenRoot routers.

Callers must supply current, authorized inputs and meaningful versioned
comparison bases. Receipts explicitly mark freshness as unverified.
Do not use this cache as a substitute for permission or freshness checks.
Unknown gate or measurement data results in HOLD; malformed contracts
raise an error. PASS does not mean safe for deployment.

Evidence references identify assertions; they are not independently
verified citations. Pareto ranking does not account for uncertainty,
subgroup distribution, temporal effects, or unlisted alternatives.
No social or physical performance claim is made.

## Interface

    python3 -m openloom.need_outcome evaluate request.json
    python3 -m openloom.need_outcome evaluate request.json --db cache.sqlite
    python3 -m openloom.need_outcome plan chain.json

The evaluate input contract is illustrated by fixture() in
tests/test_need_outcome.py. All values in that fixture are synthetic.

Chain inputs are lists of objects with id, worker, depends_on, and
approval_required. Planning never executes commands.

Cache databases contain potentially sensitive requests' fingerprints and
decision outputs. Keep runtime databases private and outside Git.
The CLI does not create missing parent directories for a cache database.

## Test

    python3 -m unittest discover -s tests -p test_need_outcome.py -v

## Integration contract

Existing workers can call evaluate(), plan_chain(), or cached_evaluate().
A future dispatcher must resolve current authorization and generations
before requesting cache reuse. Register source and policy dependencies
in the existing provenance system before claiming change-aware freshness.

Historical receipts remain historical evidence. Changed assumptions,
sources, permissions, or policy require revalidation, not erased history.


## Hardening contract: 0.1.1

- Request identifiers need_id, context_id, policy_id, and access_scope
  must contain at least one non-whitespace character.
- freshness must be a nonempty, flat mapping of nonblank string names
  to nonblank string generation identifiers. Nested objects, nulls,
  booleans, and numeric generation values are rejected.
- Oversized measurement integers that overflow the finite-number check
  produce ValueError rather than an unhandled OverflowError.
- Chain-plan output includes the engine version.
- The implementation/version change changes cache identity.

These checks validate the supplied labels, not their real-world truth.
Freshness and authorization are still not independently verified.

### Local verification

The hardened implementation passed 16 regression test methods and a
459-case refinement battery with no failures or remaining probe gaps.
The refinement battery used deterministic seeds 17, 2026, and 718.

These are synthetic tests, not evidence of live source tracking,
concurrent-writer reliability, physical safety, or social outcomes.
The refinement report is retained privately outside the repository.
