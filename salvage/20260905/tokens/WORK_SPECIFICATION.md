# WORK Token Specification

**Status:** Concept  
**Date:** 2026-07-24  
**License:** CC-BY-SA 4.0 (docs) | GPL v3 (code) | No patents.  
**Relation:** Lives on the same thermodynamic ledger as ACRE, STEP, and SKILL.

---

## Core Definition

**WORK** is the base unit of verified useful joules delivered to the OpenRoot system.

η = useful_joules / human_joules remains the only performance language.  
WORK is the ledger’s native accounting token for those useful joules.

Any energy form that performs useful work scores the same:
- Passive solar thermal capture
- Photovoltaic
- Human muscle
- Mechanical (truck, pump, wind, water)
- Computational
- Kinetic (vibration, motion, impact)
- Hybrid circuits of the above

E = mc² equivalence is respected: the ledger does not care aboutHere is the shortest path.

One single paste writes every core document cleanly:

```bash
cd $HOME/openroot && mkdir -p tokens bounties && cat > tokens/WORK_SPECIFICATION.md << 'EOF'
# WORK Token Specification

**Status:** Concept  
**Date:** 2026-07-24  
**License:** CC-BY-SA 4.0 (docs) | GPL v3 (code) | No patents.  
**Relation:** Lives on the same thermodynamic ledger as ACRE, STEP, and SKILL.

---

## Core Definition

**WORK** is the base unit of verified useful joules delivered to the OpenRoot system.

η = useful_joules / human_joules remains the only performance language.  
WORK is the ledger’s native accounting token for those useful joules.

Any energy form that performs useful work scores the same:
- Passive solar thermal capture
- Photovoltaic
- Human muscle
- Mechanical (truck, pump, wind, water)
- Computational
- Kinetic (vibration, motion, impact)
- Hybrid circuits of the above

E = mc² equivalence is respected: the ledger does not care about the source, only the measured useful energy that advanced the system.

---

## Thermodynamic Proof Mechanism

The preferred proof path is the **Capture → Store → Exert** cycle.  
It is self-verifying for many cases and minimizes external oracles.

### Cycle

1. **Capture**  
   Sensors record incoming energy (irradiance, ΔT, vibration amplitude, flow rate, etc.).

2. **Store**  
   The system logs the rise in potential (thermal mass temperature, capacitor voltage, kinetic RPM, chemical SOC, gravitational height, etc.).

3. **Exert**  
   Useful work is performed and measured (mechanical output, computation completed, heat delivered, water moved, mesh packet transmitted under load, etc.).

Because energy cannot appear from nowhere, the existence of stored potential that is later converted into measured useful work is strong physical evidence that real capture occurred.

### Assurance Levels

| Level | Requirement | Typical use |
|-------|-------------|-------------|
| L0    | Single sensor set + local hash | Early prototypes, low-value WORK |
| L1    | Capture + Store + Exert logged, raw data hashed to IPFS | Standard WORK mint |
| L2    | L1 + second independent sensor set or second node attestation | Higher-value or disputed claims |
| L3    | L2 + two human validators (agape rule) | Crosses into ACRE territory or large continuous streams |

Failures and negative η are also recorded. The ledger tells the truth.

---

## Kinetic Energy Harvesting (First-Class WORK Source)

Kinetic sources are treated identically to thermal or electrical sources.  
Any motion already present in an OpenRoot node should be harvested where practical.

### Practical methods ranked for OpenRoot context

1. **Electromagnetic** (highest practical priority)  
   Magnets + coils on pumps, wind-driven elements, vehicle suspension near rural nodes, door/gate motion, rotating shafts. Robust, scalable, low-cost materials possible.

2. **Piezoelectric**  
   Vibration from machinery, foot traffic around domes, pressure on walkways, structural flex of geodesic elements. Low power but excellent for powering the sensor/mesh nodes themselves.

3. **Triboelectric**  
   Contact-separation materials on moving parts or flexible surfaces. Extremely low cost, flexible, still maturing.

4. **Gravitational / potential**  
   Counterweights, falling water, elevators, any existing height differential. Already close to classic hydro.

5. **Hybrid thermal-kinetic**  
   Structures that experience both temperature gradients and vibration (aerocement walls, cooling labyrinths, pumps). One physical object yields two WORK streams on the same sensor bus.

### Integration rule

Every kinetic harvester must report on the same sensor/mesh bus that already carries thermal and electrical data.  
One data stream → multiple WORK categories.  
No separate parallel systems.

---

## How the Four Tokens Weave
- **WORK** is the common language.
- **STEP** is an intentional, funded improvement that raises the future rate of WORK generation.
- **SKILL** tags the human labor that made the physical system exist and report truthfully.
- **ACRE** remains the permanent record of *new knowledge*. High-η WORK records and successful STEP claims can multiply or auto-qualify ACRE under the existing Category rules.

No token is bought into existence.  
All minting is downstream of measured useful joules or verified new knowledge.

---

## Efficiency Rules (Non-Negotiable)

1. Single ledger. No parallel accounting systems.
2. Single sensor/mesh bus for thermal, kinetic, electrical, and computational data.
3. Prefer passive or already-moving sources over new actuators.
4. Capture → Store → Exert is the default proof path.
5. Raw data is hashed and preferably published (IPFS / GitHub) so any node can re-verify.
6. Human joules are minimized; machine and computational joules that replace them are rewarded.
7. The Advancement Engine watches WORK generation rates and proposes the next STEP that most increases future WORK per human joule.

---

## Minting Sketch (to be formalized)

- Continuous or batched WORK mint proportional to measured useful joules (after L1 or higher proof).
- A successful STEP that demonstrably raises the WORK generation rate of a node or mesh earns additional STEP tokens and can multiply future WORK claims.
- The humans who installed the sensors, harvesters, or performed the physical validation earn SKILL tagged to those WORK records.
- If the same event also produced new knowledge (design improvement, new climate data, new failure mode documented), it can claim ACRE under existing rules, with the η gain acting as multiplier.

---

## Next Concrete Steps

1. Instrument one existing or prototype node with both thermal and simple electromagnetic/piezo kinetic sensing on the same bus.
2. Log a full Capture → Store → Exert cycle and publish the raw data + hash.
3. Write the first formal minting formula that converts measured joules into WORK tokens.
4. Feed that data into the Advancement Engine so it can propose the highest-leverage next STEP.

---

*The ledger does not reward effort.  
It rewards useful joules the species no longer has to spend by hand.*
