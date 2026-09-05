# DELTA-T VEHICLE SPECIFICATION
## DV.GEN.TH.DT01 — Mobile Thermal Cascade Generator

### CONCEPT

Vehicle-mounted thermal cascade system:
- RMH (ferrocement/refractory composite) generates heat from biomass
- Small pressurized vessel generates steam
- TEG embedded in cold side (immersed in cold water reservoir)
- Steam on hot side, cold water on cold side
- Generates electricity 24/7 — parked or driving
- Gravity-fed fuel hopper enables autonomous feeding

### RMH CONSTRUCTION — ALL CEMENTITIOUS

Composite wall (no firebrick needed):

Layer 1 (inner): Ferrocement + refractory coating
  - 22ga galvanized mesh, 2 layers
  - Refractory mix: fireclay + perlite + castable refractory (1:1:0.5)
  - Withstands: up to 1,100°C
  - Thermal shock resistant (steel mesh flexes)

Layer 2 (middle): Open-cell aerated concrete (AE-GFRC)
  - 25-50mm thick
  - Insulation: R-value ~1 per inch
  - Temp range: 300-800°C

Layer 3 (outer): Closed-cell aerated concrete
  - 25-50mm thick
  - Better insulation (trapped air pockets, no convection)
  - Surface temp: <300°C even at full burn
  - Can be coated with silicone for weatherproofing (vehicle mount)

### STEAM VESSEL SIZING

| Config | Volume | Pressure | Temp | Energy Stored | Burn Time | Runtime |
|--------|--------|----------|------|---------------|-----------|---------|
| 1 atm | 2 L | 1 bar | 100°C | 5,148 kJ | ~17 min | ~30 min |
| 10 bar | 2 L | 10 bar | 180°C | 5,324 kJ | ~18 min | ~30 min |
| 1 atm | 5 L | 1 bar | 100°C | 12,870 kJ | ~43 min | ~75 min |
| 10 bar | 5 L | 10 bar | 180°C | 13,310 kJ | ~44 min | ~75 min |

Note: Pressurized vessels MUST be steel, not ferrocement.

### GRAVITY-FED FUEL HOPPER

Design:
- Vertical tube mounted above RMH feed opening
- Sticks/branches loaded from top
- Gravity feeds into combustion chamber
- Adjustable gate controls feed rate
- Refractory-lined at base (where heat rises)

Capacity estimate:
- 6-inch tube × 2 feet = ~10L fuel volume
- Wood density: ~400 kg/m³
- Fuel mass: ~4 kg
- Energy content: 4 kg × 16 MJ/kg = 64 MJ = 17.8 kWh
- At 5 kW output: ~3.5 hours of continuous burn per load

### TEG PLACEMENT — COLD SIDE IMMERSION

Optimal design:
- TEG hot side: bonded to steam vessel wall (steel)
- TEG cold side: immersed in cold water reservoir
- Cold water reservoir: insulated tank, 5°C target
- Multiple TEG modules can be stacked around vessel circumference

Power output (per TEG module):
| Source | Hot Side | Cold Side | ΔT | Power | 24h Energy |
|--------|---------|----------|-----|-------|-----------|
| Solar (day) | 47°C | 5°C | 42°C | 4.2W | 0.034 kWh |
| RMH exhaust | 200°C | 5°C | 195°C | 19.5W | 0.029 kWh |
| Steam (1 atm) | 100°C | 5°C | 95°C | 9.5W | varies |
| Steam (10 bar) | 180°C | 5°C | 175°C | 17.5W | varies |

With 4 TEG modules + steam at 10 bar:
- Peak output: 4 × 17.5W = 70W
- If steam available 2 hours/day: 70W × 2h = 0.14 kWh
- Solar mode 8 hours: 4 × 4.2W × 8h = 0.134 kWh
- Residual ΔT 14 hours: 4 × 3W × 14h = 0.168 kWh
- Daily total: ~0.44 kWh = enough for LED lighting, phone charging, sensors

### VEHICLE INTEGRATION

Mounting options:
- Front: RMH in grille area, airflow-optimized
- Rear: bed-mounted, gravity-feed from above
- Side: saddle-style with hopper access

Aerodynamic considerations:
- Steam vessel at stagnation points (highest pressure, lowest flow)
- Cold water reservoir at points of maximum airflow
- Insulated ducting routes ambient air past cold reservoir

The vehicle itself becomes part of the thermal system:
- Wind passes over cold reservoir → maintains cold side
- Solar gain on black surfaces supplements hot side
- Motion increases convective heat transfer on both sides

### ACRE MINTING — MOBILE NODE

This is a mobile ACRE minting node:
- All joules captured from RMH → ACRE minted
- GPS coordinates stamped on each batch
- Vehicle can drive to different locations, mint ACRE from local biomass
- Demonstrates: PoPW (Proof of Physical Work) is location-independent

### SAFETY

1. Pressure vessel = STEEL ONLY (Schedule 40 pipe minimum)
2. Pressure relief valve on all sealed systems
3. Cold water reservoir overflow vent
4. Steam exhaust path (if engine not consuming all steam)
5. Temperature monitoring: hot side, cold side, steam, water
6. Fire suppression: water reservoir doubles as emergency fire water
7. Vehicle mount: heat shields between system and fuel tank

### DEPENDENCIES
- AE-GFRC-01 (aerated cement for insulation layer)
- CTBS-01 (cold battery — ferrocement tank)
- STEAM-INTEGRATION-SPEC (phased deployment)
- RMH-COMPOSITE-SPEC (ferrocement/refractory composite wall)

### STATUS
- Hypothesis: H-002 (Delta-T thermal vehicle) — COMPLETED design
- Validation: T0 (theoretical, awaits physical T3)
- Parent: agape-une
- License: GPL v3 (code), CC-BY-SA 4.0 (docs)
- Copyright: One Human Family
