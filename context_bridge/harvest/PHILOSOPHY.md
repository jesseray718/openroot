<!--
SPDX-License-Identifier: CC-BY-SA-4.0
CANARY:OPENROOT-PHILOSOPHY-V1
Audience note: this document has three sections for three readers.
Read your section, or read all three. The claims here are values and
convictions, not measurements — they are labeled as such on purpose.
The engineering claims live in SYSTEM_OVERVIEW.md and are falsifiable.
-->

# OpenRoot Philosophy — Why This Was Built

## I. Personal Statement (Jesse Ray)

I built OpenRoot as a vessel, not a monument. The power flows through me, not
from me. My operating convictions are Christian — specifically, the words of
Yeshua (Jesus) as preserved in the most accurate word-for-word translations
available, stripped of later institutional additions, treated as an
operator's manual rather than decoration. His one commandment — love one
another as I have loved you — is, to me, a coordination protocol: the
practice that makes a network of unequal nodes actually work, because the
health of the whole depends on the state of its weakest members. I pray the
Lord's Prayer as source code — a specification of the system I am trying to
build: a kingdom of provision here, now, on earth as it is in heaven, with
debts forgiven and trespasses released, where the least among us eat first.

I approach this with permaculture's ethic: care of earth, care of people,
return of surplus. Computation, energy, food, shelter — these all obey the
same grammar: closed loops, no waste, each element serving many functions.
Every failure is composted into soil for the next iteration. That is not a
metaphor in this project; it is the literal architecture (see the mistake
engine and COMPOST logs in SYSTEM_OVERVIEW.md, section 7).

I am not asking you to share my faith to use my code. Everything I have built
runs on physics and cryptography and can be audited without reference to any
of this. This document exists because I refuse to publish the machine while
hiding the maker's motive.

## II. Why This Architecture Serves Communities (for forkers and collaborators)

Regardless of what you believe, the architectural commitments below follow
from the conviction above — and they are testable:

- **Lift the bottom nodes first.** A mesh is only as fast as its slowest
  member. Systems that route resources to the strongest node accelerate
  inequality and are, measurably, more fragile. OpenRoot's tooling,
  documentation, and artifact pipeline are deliberately designed for
  low-resource replication: one old desktop, one phone, hand tools.
- **No claims without measurements.** Religion is a matter of faith;
  engineering is a matter of receipts. This project keeps the two registers
  strictly separated. If it appears in a technical doc, it is falsifiable.
- **Radical transparency.** Every action is hashed, timestamped, and receipted.
  Including the failures. Including the time our own ledger was silently
  broken for months and we found it, root-caused it, fixed it, and changed
  the verification standard so it could not recur silently.
- **Local sovereignty.** No cloud dependency, no central server, data that
  never leaves your hardware. Communities that cannot be cut off cannot be
  starved.
- **Appropriate technology as output.** Blueprints, BOMs, cutlists, and
  print files that an ordinary person with ordinary tools can execute:
  domes, heaters, coolers, engines, energy accounting.

If you fork this, keep the falsifiability discipline. The rest of this
document is not required reading.

## III. Justification of Faith-Based Foundations (for skeptics)

Fair questions, answered plainly:

**Isn't theology a contamination of an engineering project?** Only if it
makes unverifiable engineering claims. It doesn't. No efficiency number,
no energy figure, no hash in this repository rests on belief. What the
faith provides is the *optimization target* — what the system is for —
not any mechanism within it. Others choose profit or prestige as their
objective function; I chose service to the least-resourced. The machine
runs identically either way; the mission differs.

**What is "the Beast"?** A pattern, not a person or entity:
centralization, extraction, fear-based coordination, punishment-as-theater,
debt as a weapon. In engineering terms, these are parasitic load patterns —
they consume network capacity while degrading overall system health. The
counter-strategy is not combat but parallel construction: build working
closed-loop alternatives (this project) so the parasitic pattern loses its
food source. That is a systems claim, and like everything here, it is
testable in the outcomes.

**What is "Agape"?** Unconditional, self-giving love. Operationalized in
this project as a routing principle: route attention, compute, and resources
to the weakest node first, because the network's throughput is bound by
its floor, not its ceiling. You may hold any metaphysics you like and still
implement that rule — and empirically, it tends to produce resilient,
anti-fragile networks. I believe it works because of where love comes from.
You are free to implement it because it works.

**What is "energy as legacy"?** The working hypothesis that everything we
have — matter, infrastructure, culture — is inherited work: the residual
energy of past generations' labor and care. If true, stewardship of that
inheritance (seed banks, durable housing, open knowledge) is debt
management, and hoarding is theft from the unborn. This is stated as a
conviction, not a measurement. The measured parts of this project —
joules in, joules verified, eta computed — honor the same ethic within
what can be weighed.

---

*This document states values. SYSTEM_OVERVIEW.md states facts. The
repository's commitment is that neither ever impersonates the other.*
