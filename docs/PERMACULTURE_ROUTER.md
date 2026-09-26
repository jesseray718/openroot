<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# OpenRoot Permaculture Router

## Purpose

The OpenRoot Permaculture Router applies all twelve permaculture principles as
explicit, inspectable decision lenses for a proposed system, design, workflow,
experiment, or operational change.

It is a read-only decision-support system.

It may:

- inspect a declared context
- activate relevant principles
- expose missing information
- detect hard safety and evidence gates
- propose bounded next steps
- produce structured JSON and Markdown reports
- support CI validation of repository-contained contexts

It may not:

- execute physical actions
- operate equipment
- make safety claims
- promote evidence levels
- stage, commit, push, tag, or release Git content
- modify live model registry, superloop chain, dashboard pulse, or quarantine state
- replace consent, judgment, local governance, or expert review

## Decision model

```text
Observe → map → evaluate all principles → apply hard gates
→ activate routes → recommend smallest safe reversible step
→ human review → measure → record evidence → repeat
```

Every principle is evaluated for every context. A principle need not be active
for every context. Forcing all principles to produce an intervention creates
complexity and false optimization.

## Evidence levels

| Level | Meaning |
|---|---|
| L0 | Concept, hypothesis, or unverified idea |
| L1 | Documented source, calculation, simulation, or design rationale |
| L2 | Documented controlled physical measurement |
| L3 | Replicated physical measurement |
| L4 | Documented field validation |
| L5 | Independent replication or mature validation |

CI passing means repository checks passed. It does not prove a physical claim,
system performance, safety, regulatory compliance, or field readiness.

## Context files

Place a router context at either:

```text
data/router_examples/<name>.json
designs/<slug>/router_context.json
```

Validate it:

```bash
python3 scripts/validate_permaculture_context.py data/router_examples
```

Run the router:

```bash
python3 scripts/permaculture_router.py \
  data/router_examples/thermal-cascade-l0.json \
  --output .ci/permaculture/thermal-cascade.report.json
```

Render the result:

```bash
python3 scripts/render_permaculture_report.py \
  .ci/permaculture/thermal-cascade.report.json
```

## CI

Run the local pipeline:

```bash
python3 scripts/permaculture_ci.py
```

Strict mode fails when a router context returns `HOLD_FOR_HUMAN_REVIEW`:

```bash
python3 scripts/permaculture_ci.py --strict
```

Use strict mode only for contexts that are expected to be action-ready.
For L0/L1 design intakes, a hold decision is usually correct and informative.

## Optimization rule

OpenRoot seeks durable, distributed benefit with low lifecycle burden:

\[
\text{maximize}
\frac{
\text{benefit across nodes}
\times
\text{durable yield}
\times
\text{resilience}
\times
\text{evidence confidence}
}{
\text{labor}
+
\text{money}
+
\text{energy}
+
\text{maintenance}
+
\text{risk}
}
\]

Hard constraints override optimization:

- safety
- consent
- evidence proportional to risk
- reversibility
- repairability
- maintenance capacity
- ecological regeneration
- human review

## Local runtime boundary

The following paths are operational state and must remain local unless a
deliberate human review promotes a narrowly selected artifact:

```text
data/model_registry.json
data/superloop_chains.json
context_bridge/superloop_DASHBOARD.md
bin/quarantine_pyfails_final_v2/
```
