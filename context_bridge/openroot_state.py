#!/usr/bin/env python3
"""
OPENROOT STATE — portable single-file snapshot
Generated 2026-07-23. Carry this file to any new AI.
"""

STATE = {
  "project": "OpenRoot / AeroCement / ACRE PoPW",
  "date": "2026-07-23",
  "canonical_paths": {
    "bridge": "/data/data/com.termux/files/home/openroot/context_bridge/context.json",
    "ledger": "/data/data/com.termux/files/home/openroot/ledger/thermo.db"
  },
  "locked_decisions": [
    "Vortex chimney uses φ geometry (H/D = φ², dc = D/φ²). Air mass-flow is master variable.",
    "One-person Micro-Node: 10-14 m² aperture, 15-18 m chimney, 5-9 m³ wet open-cell labyrinth, hot tank 1.5-2.5 m³, cold tank 2-3.5 m³, radiative lid 5-8 m².",
    "Black Locust Rocket Mass Heater is a parallel, valved draft driver (modes: solar / rmh / dual).",
    "Stirling (free-piston or thermoacoustic) uses discrete thermal charges only (5-8% of tank capacity) + flywheel + high-torque belt + final alternator.",
    "TEGs only on residual ΔT.",
    "Zero-energy cooling path: desiccant → wet labyrinth → ground coupling → radiative lid → cold tank.",
    "Thermodynamic ledger is SQLite and accepts only instrumented joules (heat, cold, mech, elec, human, cpu).",
    "η = useful_joules / human_joules is the governing metric.",
    "ACRE mints solely from the ledger. No theoretical numbers allowed.",
    "Fractal swarm composition depth limited by n_max = floor(ln R / ln p).",
    "All bottlenecks evaluated as joules per unit time."
  ],
  "formulas": {
    "landauer": "E >= kT ln2 ≈ 2.87e-21 J/bit @ 300 K",
    "eta": "η = useful_joules / human_joules",
    "n_max": "n_max = floor(ln R / ln p)",
    "mass_equivalent": "m = E/c² ≈ 1.11e-17 kg/J"
  },
  "pending_physical": [
    "Lock exact Micro-Node dimensions",
    "Instrument first prototype (air flow, ΔT hot, ΔT cold, shaft work)",
    "Start writing real measurements into SQLite ledger",
    "Wire ledger → ACRE minting",
    "Implement continuous duty-cycle + swarm loop driven by ledger"
  ],
  "rules": [
    "Absolute paths only (no tilde)",
    "F1: generate, never auto-push",
    "Only measured joules may enter ledger or ACRE",
    "Nodes are modular: standalone or bus-connected"
  ]
}

if __name__ == "__main__":
    import json
    print(json.dumps(STATE, indent=2))
