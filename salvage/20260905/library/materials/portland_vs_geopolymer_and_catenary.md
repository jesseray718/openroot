# Portland vs Geopolymer + Monolithic Catenary Vault Direction
**UNE:** DV.CON.FUND.BINDER.VAULT.001  
**Status:** draft  
**η note:** Binder choice + pure-compression geometry are the two highest-leverage decisions for long-life, low-maintenance community nodes.

## 1. Portland Cement vs Geopolymer — Core Comparison

| Property                    | Portland Cement (OPC)                  | Geopolymer (alkali-activated)              | Winner for OpenRoot |
|-----------------------------|----------------------------------------|--------------------------------------------|---------------------|
| Primary reaction            | Hydration of C₃S / C₂S → C-S-H         | Geopolymerization (Si-Al oligomers → 3D network) | — |
| Process heat / CO₂          | High (kiln \~1450 °C, \~0.8–1.0 t CO₂/t) | Much lower (often 40–60 % less energy)     | Geopolymer |
| Heat of reaction            | High early heat                        | Generally lower and more controllable      | Geopolymer |
| Acid / chemical resistance  | Moderate                               | Excellent                                  | Geopolymer |
| High-temperature residual strength | Loses strength, can spall         | Often retains more strength to 600–800 °C  | Geopolymer |
| Ambient curing              | Reliable                               | Some formulations need mild heat or careful activator | OPC easier |
| Local materials             | Limestone + clay everywhere            | Needs reactive aluminosilicate (fly ash, metakaolin, slag) | Depends on site |
| Fiber compatibility (AR glass) | Excellent                            | Good, but activator chemistry must be checked | Both usable |
| Current field maturity      | Extremely high                         | Growing, less standardized                 | OPC for first prototypes |

### Hydration / Reaction Heat (Typical Order of Magnitude)

| Binder                  | Peak heat evolution          | Notes |
|-------------------------|------------------------------|-------|
| Ordinary Portland       | High (C₃A and C₃S driven)    | Can cause thermal cracking in large pours |
| Geopolymer (fly-ash / slag) | Lower and broader peak     | Easier temperature control in thick sections |
| Blended / low-heat OPC  | Reduced                      | Compromise option |

Exact numbers vary strongly with formulation, ambient temperature, and section size. Always measure on the actual mix.

## 2. Monolithic Double-Catenary / Stress-Skin Vault Concept

**Core idea (compression-only shell)**
- Shape the outer shell as a double-curvature catenary (or close approximation) so that under its own weight and design loads the internal forces stay almost pure compression.
- The shell is monolithic (continuous pour or carefully jointed).
- The lower edge of the shell hooks or thickens into a continuous footing that is also in compression / bearing.
- The interior void can be filled (or partially filled) with low-density open-cell cellular concrete for thermal mass, insulation, and service routing.
- Because the primary load path is compression, conventional tensile reinforcement (rebar) can be minimized or eliminated in large regions of the shell.  
  **Important correction**: rebar is not “useless until concrete fails.” In conventional beams and slabs it carries tension from the beginning. In a correctly shaped compression shell the need for it is greatly reduced, which is the real advantage.

**Practical advantages for community scale**
- Very long potential service life when kept in compression and protected from water ingress at the foundation.
- High resistance to distributed loads and many blast / impact scenarios (thin-shell concrete has historical precedent in protective structures).
- Natural water-shedding shape → easy integration of catchment into large ferrocement cisterns (10k–50k gallon class).
- Interior volume can host food systems (tilapia + duckweed tanks, aquaponics) while the shell itself is the structure and thermal mass.

**Implementation notes**
- Formwork for true double-curvature is the hardest part. Airforms, fabric forms, or segmented temporary supports are common approaches.
- Cellular (open-cell) concrete fill must remain light enough not to overload the shell while still providing the desired thermal and acoustic performance.
- Foundation must be designed for the outward thrust that any arch/vault produces; the “hook under” detail is one way to resist that thrust.

## 3. Integration with Food & Water Stack

- Roof catchment → large ferrocement or GFRC cisterns (target 20–50k gallon community scale).
- Cisterns can be partially buried or integrated into the vault footing for thermal stability.
- Interior or adjacent tanks for tilapia + duckweed (or other polyculture) use the same cellular-concrete thermal mass principles.
- Black locust or other durable timber for internal platforms, catwalks, and tank covers.

## 4. Next Physical Actions
1. Decide binder for first prototype panels: stay with Portland + AR glass for speed, or run parallel geopolymer trials if reactive aluminosilicate is locally available.
2. Build a small-scale catenary arch or vault segment (even 1–2 m span) to feel the pure-compression behavior and formwork challenges.
3. Log density and strength of any cellular fill used inside the test vault.

## Related
- cement_basics.md
- aerated_nanobubble_gfrc.md
- prototype_folded_bl.md
- energy/DV.GEN.BL.RMH.001.md
