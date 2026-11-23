# OpenRoot

<!-- OPENROOT-STATUS-2026-11-23 -->
## November 23, 2026: working pods, correction retrieval passed, end-to-end acceptance next

OpenRoot is building local-first knowledge pods and correction-aware, sealed answer pathways: preserve evidence, retrieve before generating, and replay valid results without another generation request.

Latest operator-reported local results: tree-to-pod tooling passed a 249-cell sanity run and an 18-cell docs-pod run; G22 retrieval-only acceptance passed all six assertions, including corrective facts present in the packet and zero model requests. An earlier instrumented integration receipt records generation, exact zero-generation replay, and operator-blocked replay. These are different test scopes, not a claim of complete production integration.

Next gates: one metered G22 answer-content test, its pathway/replay/block verification, then AeroCement exhaustive-selection and quality acceptance on its separate lane. Legacy `b3` means BLAKE2b-256, not BLAKE3. Payload stays out of Git; pinned identity-bearing files and existing seals stay unchanged.

[Current status, evidence boundaries, and remaining build list](docs/STATUS-2026-11-23.md) · [Specific questions to resolve through the system](docs/SYSTEM-QUESTIONS-2026-11-23.md)

This is a documentation publication of reviewed receipts and the operator's latest handoff. Newer local-only tooling and receipts have not been independently retrieved or executed by this publication agent. Publishing this page does not deploy them.
<!-- /OPENROOT-STATUS-2026-11-23 -->

### Local capability. Shared knowledge. A distributed commons.

OpenRoot is an open-source appropriate-technology project connecting physical infrastructure, local computing, evidence, and shared contribution. Its ambition is a worldwide web of locally useful clusters: communities able to build, measure, repair, and improve essential systems while sharing what works.

The computer serves the physical outcome—not the other way around. Useful heat, cooling, shelter, water, food, repair, and access to knowledge are the intended benefits.

[Project overview](https://jesseray718.github.io/openroot/) · [Contribute](CONTRIBUTING.md) · [Concrete work](https://github.com/jesseray718/openroot/issues) · [Design-packet template](https://github.com/jesseray718/openroot-design-packet-template)

## The connected architecture

| Layer | Purpose |
|---|---|
| Physical systems | Open designs for locally maintainable appropriate technology, including AeroCement and thermal-cascade research. |
| Local intelligence | Searchable source material, lightweight local computing, and reusable procedures for ordinary phones and used computers. |
| Distributed mesh | Nodes and clusters that exchange designs, evidence, corrections, and useful results, with offline operation as a design priority. |
| Evidence and telemetry | Traceable measurements, assumptions, source identities, calibration records, and independent replication. |
| Contribution ledger | Cryptographic attribution and linked histories of work, review, reuse, and correction; blockchain anchoring or settlement where justified. |
| ACRE | An experimental contribution and exchange concept whose issuance, governance, backing, and redemption rules require explicit verification. |

These layers describe the intended system. They are not a claim that a worldwide deployment or complete integration already exists.

Agape, permaculture, and shared credit guide the design: integrate compatible functions, preserve useful yield, accept feedback, reduce waste, and serve people with the fewest resources first.

## Physical technology is central

[AeroCement](https://github.com/jesseray718/aerocement) is a material-family research program, not one universal recipe. Material architecture, formulation, curing, geometry, and test conditions must accompany results.

The thermal-cascade design thesis includes carbon-infused open-cell AeroCement absorber concepts, desiccant-preconditioned incoming air, wet porous heat-and-mass exchange, and separate hot and cold reservoirs. The documented breathing arrangement is open and one-pass: air is exhausted after useful exchange, rather than assumed to recirculate through the desiccant. Blackbody language describes an absorber design aim, not a certified absorptance or system efficiency.

Related work includes [Black Locust / rocket-mass-heater research](https://github.com/jesseray718/black-locust-rmh), thermal storage, repairable hardware, and community-scale infrastructure. Each subsystem needs its own evidence; combining proposed functions does not establish combined performance.

Physical records should distinguish design thesis, calculation, simulation, instrumented measurement, and independent replication. Energy accounting must include environmental inputs, parasitic loads, losses, storage changes, and uncertainty. Nothing here is structural, combustion, pressure-vessel, potable-water, or electrical safety certification.

## Preserve work instead of paying for rediscovery

The zero-cost-recompute ambition is to make useful work reusable at the lowest practical marginal cost—not to claim literally free computation or energy.

The intended workflow is:

1. Identify a local need and retrieve relevant source evidence.
2. Reuse a checked method or result when its conditions apply.
3. Recompute or experiment when inputs, dependencies, or confidence require it.
4. Preserve the method, inputs, evidence, limits, and attribution.
5. Share a portable packet that another node can inspect and use.
6. Propagate corrections without erasing the original record or its credit.

A cache hit is useful only when the result remains applicable. A valid ledger hash is not proof that external evidence is fresh.

## Contribution ledger, telemetry, and blockchain

The proposed contribution record links an artifact and license to its authors, dependencies, tests, measurements, reviewers, replications, and corrections. The Joule Tracking Ledger is the physical-accounting side: distinguish measured from estimated energy, record methods and uncertainty, and connect inputs to useful outputs.

Cryptographic signatures and hashes can support attribution and tamper detection under their verification assumptions. They do not establish sensor accuracy, scientific truth, useful yield, or financial value. A recorded claim can still be wrong.

A blockchain may support shared settlement or external anchoring when participants need it. It is not a substitute for calibration, independent checks, correction handling, or access to the underlying evidence. Local evidence access and useful participation should not require buying a token.

## ACRE: keep recognition, measurement, and exchange distinct

ACRE belongs in the broader architecture, but contribution recognition, physical energy accounting, and transferable exchange claims are different things.

Historical repository material discusses token experiments and anchoring. This README does not verify current contracts, balances, issuance, backing, redemption, regulatory status, or economic sustainability. Any operational proposal needs published rules, audit evidence, dispute handling, and safeguards against duplicate or fabricated claims. No token value or return is promised.

## Start with a reproducible component

From a checkout containing the example, with Python 3.10 or newer:

```bash
python3 examples/pathway-cache-behavior/demo.py
python3 examples/pathway-cache-behavior/demo.py --self-test
```

[Source, instructions, observations, and limitations](examples/pathway-cache-behavior/README.md). The published example documents four cases and seven tests using disposable fixtures. Once the source is present, it needs no network, model server, API key, or private database. It does not execute recorded workflow steps.

It characterizes ledger-integrity behavior and its distinction from external evidence freshness. It is a component demonstration, not proof of the complete distributed system.

## Current evidence boundary

| Area | Current public-entry claim |
|---|---|
| Component behavior | Published executable example with documented observations and limitations. |
| Correction-aware retrieval and reuse | G22 retrieval acceptance reported locally; earlier instrumented generation/replay/block receipt reviewed. Current metered content test and actual-route acceptance remain open; see the dated status above. |
| Cross-device offline pathway | Transfer and component work do not establish complete disconnected reuse. |
| Physical systems | Preserve the documented designs; require configuration-specific measurement and replication for performance claims. |
| Independent clusters | Intended adoption model, not an established worldwide network. |
| ACRE economics | Experimental concept; this page establishes no financial backing or value. |

A useful next demonstration joins the layers: one bounded experiment, a source-linked signed evidence packet, independent reuse on a second node, and a correction that reaches that node without losing attribution. Any experimental contribution credit should reference that evidence without implying unverified monetary or physical backing.

## Find the existing work

- [Dated implementation status and remaining build list](docs/STATUS-2026-11-23.md).
- [Questions to resolve through source retrieval and receipted acceptance](docs/SYSTEM-QUESTIONS-2026-11-23.md).
- [Start here](START-HERE.md) and [contribution guide](CONTRIBUTING.md).
- [Recovered dossier compiler: usage, dependencies, and limitations](docs/recovery/COMPILED_DOSSIER_V2.md).
- [Pathway-cache component example](examples/pathway-cache-behavior/README.md).
- [Thesis](THESIS.md): design arguments require their own evidence review.
- [Previous README and detailed historical rollout notes](https://github.com/jesseray718/openroot/blob/2563eae80a885973740615b0a680bad19a6378c3/README.md): retained in Git history, not promoted to current verified results.

## Bring one useful improvement

Reproduce a test, report a retrieval miss, document a failed mix, calibrate a sensor, review an energy balance, repair an instruction, or independently replicate a bounded experiment. Include sources, conditions, licensing, limitations, and a clear account of what changed. Keep credentials, private corpora, and sensitive raw telemetry out of public contributions.

[Open an issue](https://github.com/jesseray718/openroot/issues) · [Contribution guide](CONTRIBUTING.md) · [Community standards](CODE_OF_CONDUCT.md)

## Licensing and credit

OpenRoot's documented model is GPL-3.0-only for software and CC BY-SA 4.0 for non-code material. Follow the actual [license](LICENSE), individual file headers, and applicable third-party terms. Preserve contributor attribution. This documentation update changes no license and introduces no token entitlement.

*Engineering as an act of unconditional integration.*
