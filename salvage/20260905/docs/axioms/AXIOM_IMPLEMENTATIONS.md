# Axiom-to-Implementation Mapping

How each permaculture axiom translates to concrete OpenRoot code/hardware.

## Examples

### AX-013 (Cascade Principle)
**Axiom:** Multi-stage energy extraction minimizes loss.

**Implementation in H-003:**
```
Solar input → (1) Desiccant wheel → (2) Underground labyrinth → (3) Cold tank B 
→ (4) Convection to living space → (5) Return to Hot tank A
```
**Code marker:** `DV.GEN.TH.AE01` (desiccant + general + thermal + aerocement)

---

### AX-019 (Junction is Highest Friction)
**Axiom:** Connection points fail first; design for simplicity.

**Implementation in Kingdom Engine:**
```python
# Two-validator consensus (AX-019)
def mint_acre(work_id):
    approvals = count_validators_for(work_id)
    if approvals >= 2:  # Two-validator rule
        return mint_token(work_id, energy_joules / 1000)
    else:
        return error("Insufficient consensus")
```
**UNE marker:** `KI.KNG.EN.VL01` (kingdom + kingdom engine + validator)

---

### AX-022 (Mesh Resilience > Hub-Spoke)
**Axiom:** Mesh topology resilience scales as √n compared to hub-spoke.

**Implementation in Vesica Piscis mesh:**
```json
{
  "topology": "Vesica Piscis (Flower of Life)",
  "nodes": ["ND00", "ND01", "ND02"],
  "connections": [
    ["ND00", "ND01"],
    ["ND01", "ND02"],
    ["ND02", "ND00"]
  ],
  "resilience_factor": 1.732
}
```
**UNE marker:** `DV.MSH.VP.ND00` (desiccant + mesh + vesica piscis + node 00)

---

### AX-032 (Work is Honest Measure)
**Axiom:** Only energy applied to distance is real contribution.

**Implementation in ACRE ledger:**
```jsonl
{"entry_id":"h003_day_001","timestamp":"2026-07-01T00:00:00Z","work_type":"thermal_generation","energy_joules":1550400,"acre_minted":1550.4,"validators":["node00","node01"]}
```
**UNE marker:** `KI.AGP.AC.LG01` (kingdom + agape + acre + ledger)

---

### AX-030 (Fractal Principle)
**Axiom:** Patterns repeat at all scales.

**Implementation in UNE:**
- Layer 0: Single digit (0-9) = fundamental state
- Layer 1: Single letter (A-Z) = primary function
- Layer 2: Pair (a-z) = modifier/state
- Layer 3: Numeric suffix = instance

All levels compose fractally:
- `DV` = desiccant + void (simplest level)
- `DV.GEN` = desiccant thermal, general class (adding detail)
- `DV.GEN.TH` = thermal system specificity (adding detail)
- `DV.GEN.TH.AE01` = aerocement iteration 1 (full specificity)

---

## Validation Checklist

Before deploying any system:

- [ ] Which axioms does it satisfy?
- [ ] Which UNE code designates it?
- [ ] Can you draw the two-validator consensus flow?
- [ ] Does it increase yield per input (AX-034)?
- [ ] Is it documented in CC-BY-SA 4.0 (AX-036)?
- [ ] Does it serve the least first (AX-039)?

---

*CC-BY-SA 4.0 | No Patents. Ever. | One Human Family*
