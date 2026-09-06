# AE-GFRC: Autonomous Pneumatic Placement of Air-Entrained Glass Fiber Reinforced Concrete

**Author:** Jesse McMillen - OpenRoot Project
**License:** CC-BY-SA 4.0 | No Patents. Ever.
**Status:** Primary material (volumetric blackbody concrete) - prototype built and tested. Supporting systems in hypothesis stage.

---

## Core Material: Volumetric Open-Cell Blackbody Concrete (Invented)

A lightweight, air-entrained glass fiber reinforced concrete incorporating charcoal (carbon) as a high-emissivity additive, cast in an open-cell geometry. The material has been fabricated and tested by the author. It is not theoretical.

**Key properties:**
- Open-cell structure: Air passages permeate the material, creating a surface-area-to-volume ratio far exceeding flat slab geometry (est. >=50 m2/m3 vs ~2 m2/m3 for flat slab - a 25x increase)
- Charcoal additive: Provides blackbody-level solar absorptivity and thermal emissivity across the solar and infrared spectrum
- Air-entrained GFRC matrix: Spherical air voids serve as lightweight aggregate; glass fiber provides tensile reinforcement
- Triple function: Structural load-bearing + solar thermal collection + thermal regulation in a single material

---

## Primary Hypothesis (H1)

Air-entrained glass fiber reinforced concrete (AE-GFRC) incorporating >=20% zirconium-based binder substitution, wherein spherical air voids function as the primary lightweight aggregate, can achieve structural-grade mechanical performance (compressive strength >= 15 MPa; flexural toughness per ASTM C1550) at a dry density <= 1,200 kg/m3 - sufficiently low to enable continuous pneumatic transport through flexible hose systems over horizontal distances exceeding 1,609 m (1 statute mile) without segregation, excessive pressure loss, or degradation of fiber dispersion.

## Secondary Hypothesis (H2)

The replacement of mineral aggregate with entrained spherical air voids exploits the sphere optimal stress-distribution geometry, yielding a strength-to-weight ratio that meets or exceeds that of conventional lightweight aggregate concrete (LWAC) at equivalent or reduced cementitious content, while eliminating the material handling, transport, and placement energy costs associated with mined aggregate.

## Systems Hypothesis (H3)

Full automation of the concrete placement chain - mixing, pneumatic conveyance, self-leveling deposition, and curing - eliminates human placement labor entirely, achieving a placement efficiency of >=300 m3 per operator-hour with purpose-built equipment, representing a >300-fold improvement over conventional crew-based placement (empirically observed at 0.6-1.0 m3 per worker-hour inclusive of screeding and finishing operations).

## Scale Hypothesis (H4)

An array of N purpose-built pneumatic pump units, each rated at >=300 m3/hour output, can place a continuous monolithic concrete structure of volume V in time T = V/(300N) hours with zero direct human placement labor.

## Delta-T Vehicle Hypothesis (H5)

A vehicle incorporating a thermal power chain achieves self-sustaining propulsion through aerodynamic drag harvesting. The system consists of:

1. SOLAR COLLECTION: Volumetric open-cell blackbody concrete (charcoal-infused) serves as solar collector, capturing up to 98% of incident solar radiation across the solar spectrum. The open-cell geometry provides >=25x the surface area of a flat panel of equivalent footprint.

2. THERMAL STORAGE: Captured solar energy is stored in a high-density thermal mass - either dense concrete or a metal core surrounded by insulating lightweight concrete. This thermal battery stores energy for sustained operation beyond peak solar hours.

3. STIRLING ENGINE: The thermal storage mass feeds directly into a Stirling engine. The hot side of the Stirling engine contacts the thermal storage; the cold side is the vehicle front-facing radiator surface, which receives forced-air cooling from vehicle motion (aerodynamic drag).

4. DRIVETRAIN: The Stirling engine drives a flywheel attached directly to the drivetrain. No transmission, no fuel, no batteries in the electrical sense - purely thermal-mechanical.

The Delta-T arises from:
- HOT SIDE: Solar-heated blackbody concrete + thermal storage mass (temperature elevated by solar absorption)
- COLD SIDE: Front radiator surface cooled by forced convection from vehicle motion

At highway speeds (25 m/s), forced convection coefficients reach 100-200 W/m2-K. With the open-cell radiator providing 500+ m2 of exchange surface in a compact volume, the cold-side heat extraction rate is sufficient to maintain a large Delta-T across the Stirling engine, sustaining continuous mechanical power output.

The vehicle effectively harvests energy from its own aerodynamic drag - converting the parasitic energy loss of moving through air (which conventional vehicles waste as heat and noise) into the cold-side reservoir that drives the Stirling cycle.

Key insight: Aerodynamic drag, normally a parasitic loss, becomes the mechanism that sustains the thermal gradient powering the engine. Faster vehicle = more forced convection = larger heat extraction = stronger Stirling cycle. The drag and the power source are coupled constructively rather than destructively.

## Pumping Hypothesis (H6)

A purpose-built pneumatic pump system designed specifically for air-entrained lightweight concrete (density <= 1,200 kg/m3, no coarse aggregate) achieves throughput >= 300 m3/hour at pressures <= 30 bar - a 2-4x improvement over conventional boom pump capacity (80-180 m3/hr for dense concrete) - by exploiting:

- Reduced density (<=1,200 kg/m3 vs 2,400 kg/m3): ~60% less mass per unit volume = less energy per meter of hose
- No coarse aggregate: enables smaller-diameter hose (2-3 inch vs 4-6 inch), reducing equipment weight and complexity
- Spherical void lubrication: air bubbles act as ball bearings along the pipe wall, reducing friction coefficient
- Lower viscosity: mix flows more like a fluid than a slurry
- Homogeneous structure: no segregation risk over distance

Current foam concrete pumps (adapted conventional units) achieve 30-50 m3/hr. A purpose-built system is unconstrained by the design compromises of dual-use equipment and could reasonably target 300-500 m3/hr.

## Null Hypotheses

- H01: AE-GFRC with >=20% zirconium substitution cannot achieve simultaneous structural sufficiency and pneumatic pumpability at kilometer-scale transport distances.
- H05: Forced convection through open-cell blackbody concrete at vehicle speeds does not generate a sufficient Delta-T for practical Stirling engine operation.
- H06: Purpose-built AE-GFRC pumps do not exceed conventional pump throughput due to foam stability degradation under sustained pumping pressure.

---

## Quantitative Basis

### Volume: 1-Mile Radius x 1-Mile High Cylinder
- V = pi x (1,609.34 m)^2 x 1,609.34 m = 13.09 x 10^9 m3
- Conventional mass (at 2,400 kg/m3): ~31.4 billion tonnes
- AE-GFRC mass (at ~1,000 kg/m3): ~13.1 billion tonnes

### Traditional Crew Placement
- 10-person crew: ~20 m3/day (incl. screeding/finishing)
- 1-mile hill requires: 654.5 million crew-days = 17.93 million man-years
- 100 crews (1,000 workers): 17,932 years
- 10,000 crews (100,000 workers): 179 years

### Purpose-Built AE-GFRC Pump Array Placement
- Per pump: 300 m3/hr (conservative), 24/7, 3 operators (shift rotation)
- 1 pump:        4,978 years, 14,934 operator-years
- 100 pumps:     49.8 years, 14,940 operator-years
- 1,000 pumps:   ~5 years, 15,000 operator-years
- 10,000 pumps:  ~6 months, 15,000 operator-years

### Efficiency Ratio (Corrected for Lightweight Pumping)
- Traditional: ~0.6-1.0 m3 per man-hour
- Autonomous (purpose-built): ~100-167 m3 per operator-hour (at 300 m3/hr with 3 operators)
- Improvement: 100x-280x per unit of human labor

### Historical Context
- Total concrete poured in human history: ~1.5 trillion tonnes
- 1-mile hill (conventional): ~2.1% of all concrete ever poured
- 1-mile hill (AE-GFRC): ~0.87% of all concrete ever poured
- Current global annual production: ~33 billion tonnes/year
- 1-mile hill = ~0.95 years (conventional) or ~0.40 years (lightweight) of current global output
- 10,000 purpose-built pumps could match global output rate in ~6 months with 30,000 operators

### Flat Pad Efficiency (75 m3 residential foundation)
- Traditional 10-person crew: 80-100 man-hours -> ~0.75 m3/man-hr
- Autonomous pump (300 m3/hr): 15 minutes, 0.25 operator-hours -> 300 m3/operator-hr
- Per-man-hour improvement: 400x

### Delta-T Vehicle Thermal Chain (Order of Magnitude)
- Open-cell SA/V ratio: ~50 m2/m3 (vs ~2 m2/m3 flat)
- Vehicle skin area: ~10 m2 -> effective exchange surface = 500 m2
- Solar input (peak): ~1000 W/m2 x 10 m2 x 0.98 absorptivity = 9.8 kW
- Thermal storage: dense concrete or metal core, insulated by lightweight concrete jacket
- Cold-side radiator: front-facing open-cell surface, force-cooled by vehicle motion
- Convective extraction at 25 m/s: h ~ 150 W/m2-K
- If Delta-T = 20 K: Q = 150 x 500 x 20 = 1,500 kW thermal exchange capacity
- Stirling engine efficiency: 30-50% of Carnot limit; with Delta-T = 200K (hot storage ~250C, cold side ~50C), Carnot = 40%, Stirling = 12-20%
- Estimated mechanical output: 180-300 kW (240-400 hp equivalent)
- Note: Upper bounds; real-world depends on thermal mass dynamics, solar intermittency, and radiator geometry optimization

---

## Required Testing Protocols
1. Compressive strength: ASTM C39 (cylindrical specimens, 7/14/28-day cure)
2. Flexural toughness: ASTM C1550 (round panel test)
3. Density: ASTM C138 (unit weight)
4. Air content: ASTM C231 (pressure method) / ASTM C457 (microscopic)
5. Pumpability: ASTM C1716 (pumping acceptance criteria)
6. Fiber dispersion: post-test sectioning and optical analysis
7. Solar absorptivity/emissivity: ASTM E903 (spectral) / ASTM C1371 (portable emissometer)
8. Forced convection heat transfer: wind tunnel testing at 5/15/25 m/s
9. Stirling engine integration: bench test with simulated hot/cold reservoirs
10. Long-distance pump trial: progressive 100m -> 500m -> 1,000m -> 1,609m

## Mix Design Parameters (Proposed)
- Binder: Portland cement + >=20% zirconium-based substitution
- Reinforcement: alkali-resistant glass fiber (AR-GF), 2-5% by volume
- Air entrainment: 20-40% void volume (target density <= 1,200 kg/m3)
- No coarse aggregate (air voids serve as aggregate surrogate)
- Charcoal (carbon) additive for blackbody properties (already prototyped)
- Admixtures: superplasticizer for flowability, foam agent for controlled void structure

## Delta-T Vehicle Architecture (Proposed)
- Exterior (sun-facing): Volumetric open-cell blackbody concrete (solar collector)
- Core: Dense concrete or metal thermal mass (storage battery)
- Insulation layer: Lightweight AE-GFRC (thermal break between collector and cabin)
- Front-facing surface: Open-cell radiator (Stirling cold side, force-cooled by vehicle motion)
- Engine: Stirling engine with flywheel, direct-coupled to drivetrain (no transmission)
- No fuel. No electrical batteries. No combustion. Pure thermal-mechanical.

## Current Status
- Volumetric open-cell blackbody concrete: PROTOTYPED (charcoal-infused, open-cell, functional)
- AE-GFRC structural testing: PENDING (requires lab access for ASTM protocols)
- Purpose-built pump system: CONCEPTUAL (no existing manufacturer; requires engineering partnership)
- Delta-T vehicle: CONCEPTUAL (thermal model needs validation via wind tunnel + Stirling bench test)
