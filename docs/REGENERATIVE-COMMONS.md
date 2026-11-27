# OpenRoot: a regenerative commons of energy and knowledge

OpenRoot's ambition is to help people meet practical needs locally while
making useful work easier to understand, verify, reuse, and improve together.
Its physical systems and knowledge systems are parts of the same project:
each can help the other improve.

This is a working synthesis of the project vision and a user's reported local
results through November 27, 2026. It is not a claim that the complete system,
its physical performance, or a worldwide network has been independently
validated. See the [implementation status](STATUS-2026-11-23.md) for the
earlier evidence and acceptance gates.

## The two connected loops

**The physical loop** begins with a local need. Designs for solar collection,
AeroCement, airflow, thermal exchange, and storage aim to provide useful
services. Sensors and experiments can show what actually happens, including
losses, operating limits, and failures. Those observations can guide the next
design.

**The knowledge loop** preserves the designs, source material, measurements,
methods, results, and corrections needed to understand that work. Local
knowledge pods, retrieval, reusable pathways, and shared evidence are intended
to help another person find and build on it without starting over.

The connection is concrete: a measurement should identify the apparatus and
conditions; an analysis should identify its evidence; an improvement should
identify the design and analysis it builds on. A useful outcome is not merely
more data, but more capability to build, repair, learn, and recover.

## AeroCement and the distributed aperture mesh

[AeroCement](https://github.com/jesseray718/aerocement) is central to the
physical vision, not an afterthought. It is a family of material and system
research, not a single universal recipe. The proposed thermal architecture
includes carbon-infused open-cell absorber concepts, solar apertures,
stack-driven airflow, desiccant-preconditioned incoming air, porous heat and
mass exchange, and separate hot and cold storage. The documented breathing
arrangement is open and one-pass: air is exhausted after useful exchange, not
assumed to recirculate through the desiccant.

The goal is to combine functions where that improves useful outcomes: collect
and transfer heat, provide appropriate heating or cooling, and explore other
uses where the available conditions support them. The proposed distributed
aperture mesh connects locally useful installations and communities through
shared designs, observations, and improvements; it does not require energy
itself to be transported across the world.

These are design intentions, not certified performance. A blackbody-like
absorber is a design aim, not a measured absorptance. Whether stack effect can
drive sufficient air through a real assembly depends on its pressure losses
and conditions. Test records need the formulation, geometry, environmental
inputs, instrument calibration, useful outputs, auxiliary energy, losses, and
uncertainty. Heat transferred through multiple stages must not be counted
repeatedly as new energy. Structural, combustion, electrical, water, and other
safety requirements require their own review.

## Tidbits: useful things that can become larger useful things

A **tidbit** is the project's proposed unit of reusable work. It might be a
document passage, a function, a measurement, a procedure, a printable part, or
a design. A combination can itself become a tidbit: a subsystem, a complete
installation, or a cluster can be described as a reusable assembly without
hiding the parts and relationships inside it.

The aim is recursive composition: preserve what an object provides, what it
requires, how it connects, its conditions, evidence, and attribution. An
assembly should remain inspectable and open to compatible additions. Changing
an assembly should create a distinguishable version rather than silently
altering an already sealed result.

Design files, fabrication settings, machine instructions, firmware, tests,
maintenance instructions, and licenses are different artifacts. Linking them
helps someone reproduce the actual configuration that was evaluated instead
of guessing which version or settings were used.

## Pods, evidence, and reusable pathways

A knowledge pod is intended to make source material locally searchable and
portable. An autodossier gathers relevant evidence for a question or task; a
pathway records the work and conditions behind an answer or result. When a
previous pathway still applies, the goal is to reuse it rather than pay for
unnecessary recomputation or generation. When evidence changes, corrections,
dependencies, permissions, and applicability need to be checked.

An integrity seal can show that recorded bytes have not changed relative to a
trusted digest. It does **not** show that an answer is correct, a source is
current, a measurement is accurate, or a proof is valid. A sealed wrong answer
is still wrong. If appropriate evidence is missing, the system should say so
rather than make unsupported claims. Independent replication and checking
remain valuable even when work is reusable.

The intended separation between a sealed source pod and a pathway sidecar
allows queries to record operational results without changing the source pod.
Search indexes such as FTS5 are tools for finding records, not independent
authorities on their truth.

## Identity, roots, and contribution

Hashes and linked records can help preserve identities and detect changes.
The architecture distinguishes the identity of **content**, an
**occurrence** of that content in a particular source and context, and an
**assembly** describing how components are connected. This allows identical
content to have multiple documented origins without erasing attribution.

The proposed root-to-root architecture would connect committed objects, pod
snapshots, assemblies, experiments, and cluster manifests. Relationships,
roles, and configuration matter: the same parts connected differently need
not describe the same system. The application-level Merkle protocol and
cross-node exchange need explicit definitions and acceptance tests; a root
alone does not establish truth or availability.

Some newer local work reports SHA-256 and BLAKE3 hashing. Historical `b3`
identities in the existing pipeline mean BLAKE2b-256, not BLAKE3. Existing
seals must not be relabeled or changed to make the names appear consistent.

Proof of Physical Work (PoPW) and ACRE are proposed ways to connect
contribution claims with evidence and possible accounting or exchange.
Measurements, contribution recognition, and transferable value are distinct.
Hashes and timestamps cannot prove that a sensor is calibrated or that a
physical claim is true. Rules for verification, disputes, duplicate claims,
issuance, backing, and redemption remain to be established; no financial
value or return is promised. Access to essential knowledge and mutual aid
should not require buying a token.

## Agape and reciprocal regeneration

The organizing purpose is Agape: care expressed in practical cooperation.
The project vision asks each node to preserve its own continuity while
contributing to the possibility of others' recovery, and communities to do
the same for one another. The seed example is especially concrete: preserve
seeds, knowledge, and the practical capacity to help restore a community after
loss. Its strongest form requires specifying the community, risks, reserves,
and recovery conditions; it should not be assumed that any present node can
already restore everyone else.

The aspiration is that shared capability, transparency, voluntary cooperation,
and mutual care can reduce avoidable scarcity and dependence. Technology
alone cannot guarantee those social outcomes. Support should restore
capability without making people subordinate to those providing it.

## What the November 27 local output shows

The project owner shared a terminal excerpt from a local machine. The
following is a report of that output, not an independent rerun or publication
of the private corpus, implementation, or full receipts:

- A roughly 91 MiB pod was read-only at the filesystem level. Its verification
  command reported that the pod hash matched its receipt. The build report
  listed 16,314 files read, 97,591 chunks, and 36,162 unique cells; it also
  listed skipped files and redactions, so this is not complete coverage.
- Build self-tests reported FTS5 availability, sampled SHA-256 and BLAKE
  recomputation with no mismatches, and a pathway written to a sidecar while
  the pod's pathway table remained untouched. These are reported tests, not
  independent verification of every cell or all possible query paths.
- A ledger-related query against a scratch copy returned source headings; the
  subsequent verifier reported the scratch pod still matched its receipt.
  The excerpt does not establish answer quality or complete end-to-end reuse.
- A local lattice receipt reported an assembly and that the pod stayed
  unchanged during that run. It explicitly listed multi-node agreement and
  root-to-root exchange as not implemented.
- The pod query found 597 files with AeroCement or OpenCell in their paths and
  FTS matches for related terms. These counts show indexed material, not
  exhaustive coverage, retrieval quality, or physical validation.

An earlier, separate instrumented receipt reported generation, exact
zero-generation replay, and refusal after an operator block. The current G22
answer-content and pathway acceptance, clean-clone reproduction, and
cross-device integration remain open as described in the
[dated status](STATUS-2026-11-23.md). The November 27 excerpt does not close
those gates.

## A next demonstration that joins the whole idea

Choose one bounded AeroCement or thermal experiment and preserve the design,
conditions, measurements, limitations, and attribution. Build a source-linked
packet that another node can inspect and use; then introduce a correction and
show how it affects reuse without erasing the original record. Measure the
physical outcome separately from the integrity and reuse tests.

This is a proposed acceptance demonstration, not a claim that the full mesh
already exists. Its value would be showing how physical work, local knowledge,
correction, and shared learning can reinforce one another.

For the detailed earlier engineering backlog, see
[implementation status](STATUS-2026-11-23.md) and
[system questions](SYSTEM-QUESTIONS-2026-11-23.md).
