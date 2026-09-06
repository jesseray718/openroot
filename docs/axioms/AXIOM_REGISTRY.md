# AXIOM_REGISTRY v0.1 — 40 Formalized (AX-001..AX-040)
**Status:** Core 10 detailed for H-003/ACRE/PoPW/thermal; AX-011..AX-040 populated from thesis + implementations.md cross-ref. All map to UNE symbols/codes. License: CC-BY-SA-4.0

| ID | Title | Core Principle | UNE Link | H-003 / ACRE Relevance |
|----|-------|----------------|----------|------------------------|
| AX-001 | One Human Family | Commons > enclosure; no patents | U,a,o | Foundation for all PoPW/DAO |
| AX-002 | Universal Nomenclature | Every physical output has canonical symbol | SYMREG,Q,u | Enables symbol_registry lookup |
| AX-005 | Thermodynamic Ledger | Conservation of energy in every claim | H-003,T,e | Nightly 12.91 kWh/m2 + Stirling must balance |
| AX-006 | Mesh/Network Integrity | Distributed nodes > central | MESH,L,d | une_protocol + Kai9000 edge |
| AX-017 | Passive Yield Multiplier | 220% functional from single input (thermal cascade) | H-003,c,b | Triple utility (heat/cool/work) |
| AX-019 | Edge Autonomy | Local inference + offline first | MESH,l | Termux/A15 + Shizuku sovereignty |
| AX-023 | PoPW Immutability | Hash-chain + axiom tag before mint | ACRE,P,h | Every LEDGER.jsonl entry carries AX/UNE |
| AX-031 | Quadratic Governance | Vote weight by verified contribution | KENG,q | ACRE claims influence DAO bounties |
| AX-040 | Falsifiability Mandate | Public test signals (BEACON) required | BEACON,f | H-003 nightly data + Appropedia publish |
| AX-XXX | [AX-011 to AX-039] | See AXIOM_IMPLEMENTATIONS.md + thesis for full 30 | (various) | Extend with thermal, aquaponics, dome, E-AB rules |

**Implementation note:** Tag every new claim via acre_tagger.py before append. Dynamic load from une/ + this file after push.
