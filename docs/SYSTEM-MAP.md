# OpenRoot — System Interconnection Map

**How every subsystem feeds every other subsystem.**
┌─────────────────────────┐
                 │    1. MESH (comms)      │
                 │  Sikeston Node Zero     │
                 │  ESP32 + LoRa + WiFi    │
                 └────────────┬────────────┘
                              │ enables coordination
                              ▼
                 ┌─────────────────────────┐
                 │   2. CONTRIBUTION LEDGER │
                 │   + ACRE TOKEN          │
                 │   Solana / Anchor       │
                 │   Affiliate coins       │
                 └────────────┬────────────┘
                              │ rewards verified work
                              ▼
      ┌───────────────────────┼───────────────────────┐
      ▼                       ▼                       ▼## Build Order (Dependency Chain)

| Step | What                        | Depends On                  | Unlocks                          | Primary Document |
|------|-----------------------------|-----------------------------|----------------------------------|------------------|
| 1    | Mesh node (Sikeston)        | Nothing (first seed)        | Communication + ACRE-eligible work | `construction/SIKESTON-NODE-ZERO-IMPLEMENTATION.md` |
| 2    | Contribution Ledger         | Mesh (coordination)         | ACRE minting + affiliate tracking   | `technical/SMART-CONTRACT-IMPLEMENTATION-DETAILS.md` |
| 3    | Thermal system (H-003)      | ACRE (funding)              | Free energy + heating/cooling       | `handbook/energy/` |
| 4    | Shelter (Dome)              | Thermal + ACRE              | Zero-debt housing                   | `construction/GEODESIC-DOME-AE-GFRC-HOUSING-SYSTEM.md` |
| 5    | Food & Health systems       | Land + Thermal              | Food security + medicine            | `health/bio-stack.md` |
| 6    | Team of 50 formation        | All above                   | Distributed capacity + mutual aid   | `core/KEY-CONVERSATION-BRIEF.md` |
| 7    | 501c3 + Land                | Team + Ledger               | Permanence + long-term storage      | `governance/CONTRIBUTOR-TRANSITION-AND-501C3-PREPAREDNESS-FRAMEWORK.md` |

## Feedback Loops

- **Energy → Production → More Energy**
- **ACRE → Work → More ACRE**
- **Team → Node → More Teams**
- **Land → Food → Health → Capacity → More Land**

**Rule:** Build in dependency order. Skipping layers creates fragility. Building sequentially creates compounding momentum.

One Human Family. Build the first link. The chain forms itself.
