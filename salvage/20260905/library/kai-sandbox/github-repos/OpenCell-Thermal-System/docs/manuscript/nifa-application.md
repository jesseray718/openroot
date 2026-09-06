# USDA NIFA Grant Application Narrative

**Applicant:** Jesse McMillen  
**Project Title:** OpenCell Thermal-Mechanical Energy System: Zero-Electric Cooling and Direct Mechanical Power for Rural Farms  
**Program:** Sustainable Agriculture Research and Education (SARE) / Agriculture and Food Research Initiative (AFRI)  
**Requested Amount:** $5,400 (SARE Farmer/Rancher) / $50,000–$200,000 (AFRI/RDRE)  
**Date:** June 2026  

---

## 1. Project Abstract

Rural farms face a crisis of energy cost and food loss. Without affordable refrigeration, an estimated 30–40% of harvested produce spoils before reaching market. Traditional cold storage requires grid electricity or diesel generators — both expensive and unreliable in remote areas.

The **OpenCell Thermal-Mechanical Energy System** eliminates this dependency entirely. By combining a novel **OpenCell Aerocement** material with subterranean thermal exchange, the system provides:

*   **Zero-electric cooling** to 35°F using the constant 55°F earth temperature as a heat sink.
*   **Fresh water harvesting** of 24–48 gallons/day via passive condensation.
*   **Direct mechanical power** via Stirling engine integration, bypassing electrical conversion losses.

This project requests funding to construct and field-test a prototype unit on a participating farm, validating the thermodynamic model with real-world sensor data over a 12-month period.

---

## 2. Statement of Need

### 2.1 The Post-Harvest Loss Crisis
According to the USDA, post-harvest losses of fruits and vegetables in the United States range from 30–40%, primarily due to inadequate cold chain infrastructure. Small and mid-size farms are disproportionately affected because they lack the capital to install commercial refrigeration systems.

### 2.2 The Energy Cost Burden
Rural electric cooperatives charge an average of $0.14–$0.20/kWh. A single walk-in cooler consuming 8 kWh/day costs approximately $350–$500/year to operate. Diesel generators cost even more and produce emissions.

### 2.3 The Water Scarcity Parallel
Many of the same rural communities facing energy poverty also experience seasonal drought. A system that produces clean water as a byproduct of its cooling cycle addresses two needs simultaneously.

### 2.4 The Technology Gap
Current solutions fall short:
*   **Grid refrigeration:** Expensive, fragile, dependent on infrastructure.
*   **Diesel generators:** Polluting, fuel-dependent, high maintenance.
*   **Evaporative coolers:** Cannot achieve temperatures below wet-bulb; useless in humid climates; consume water instead of producing it.

The OpenCell System fills this gap by providing **compressor-free, fuel-free cooling** with **net-positive water output**.

---

## 3. Project Objectives

1.  **Construct** a full-scale prototype of the OpenCell Subterranean Cold Loop (65 sq ft collector, 10ft depth).
2.  **Validate** the thermodynamic model: Confirm 35°F output air temperature at 330 CFM airflow.
3.  **Quantify** water yield: Measure daily condensation output against the predicted 24–48 gallon/day baseline.
4.  **Document** the OpenCell Aerocement mixing protocol for farmer reproducibility.
5.  **Publish** all findings as open-source documentation (CC-BY-NC-SA 4.0) for maximum public benefit.

---

## 4. Technical Approach

### 4.1 The OpenCell Aerocement
The core innovation is a modified cement matrix that creates an **open-cell foam structure** with capillary channels. The formula uses readily available materials:

*   Portland Cement (Type I/II)
*   Xanthan Gum (15g) as a viscosity modifier
*   Dawn Ultra surfactant (1/4 cup) for bubble stabilization
*   Activated Carbon for blackbody absorption (>95%)

When mixed at a 1:2 gel-to-cement ratio and stirred to the **open-cell transition point** (marked by a visible burst of bubble pops), the material achieves a dual property: **structural strength** (from microscopic spherical voids) and **capillary moisture transport** (from interconnected channels).

### 4.2 The Subterranean Cold Capture Loop
The cooling system operates on three thermodynamic principles:

1.  **Sensible Cooling:** Warm ambient air (90°F) enters a sealed trench lined with OpenCell Aerocement at 10ft depth. Heat conducts from the air to the 55°F earth mass.
2.  **Latent Cooling:** As air cools, it reaches its dew point. Moisture condenses on the aerocement walls, releasing latent heat into the earth and dehumidifying the air.
3.  **Capillary Wicking:** The aerocement continuously draws ground moisture to its surface, sustaining the evaporative/condensation cycle indefinitely.

**Result:** Air exits the labyrinth at approximately **35°F**, having been both cooled and dehumidified, suitable for direct use in walk-in coolers or greenhouses.

### 4.3 The Mechanical Power Train (Secondary)
Excess thermal energy from the solar collector or rocket mass heater drives a **Stirling engine** with:
*   Hot side: Embedded in 150°F+ aerocement collector.
*   Cold side: Embedded in the 35°F subterranean loop.
*   Delta-T: ~115°F — significantly higher than standard atmospheric Stirling configurations.

This maximizes Carnot efficiency and provides direct belt-drive mechanical power for farm tools (pumps, saws, grinders) without electrical conversion.

---

## 5. Methodology & Timeline

| Month | Activity | Deliverable |
| :--- | :--- | :--- |
| 1–2 | Procure materials; cast test panels | Aerocement sample data (strength, absorption) |
| 3–4 | Excavate trench; install labyrinth lining | Completed Cold Loop installation |
| 5–6 | Install sensor array; begin data collection | Baseline thermal data (first 60 days) |
| 7–10 | Continuous monitoring through seasons | Full summer/winter performance dataset |
| 11–12 | Data analysis; publish findings | Final report + open-source documentation update |

---

## 6. Expected Outcomes & Impacts

### Quantitative Targets
*   Air output temperature: ≤ 35°F
*   Cooling capacity: ≥ 19,500 BTU/hr (1.6 Tons)
*   Water yield: ≥ 24 gallons/day
*   System cost: < $5,400 per unit

### Qualitative Impacts
*   **Food Security:** Reduced post-harvest loss for small farms.
*   **Energy Independence:** Elimination of grid/diesel dependency for cooling.
*   **Water Access:** Net-positive water production in drought-prone areas.
*   **Knowledge Transfer:** Open-source publication ensures any farmer can replicate the system.

### Long-Term Vision
If validated, the OpenCell System scales to:
*   **Individual farms:** Single-unit cold storage.
*   **Communities:** Multi-unit shared cooling hubs.
*   **Global deployment:** Low-cost, no-grid solution for developing regions.

---

## 7. Budget Justification

| Category | Amount | Justification |
| :--- | :--- | :--- |
| Materials (Cement, Carbon, Surfactants) | $800 | Bulk purchase for prototype + test samples |
| Excavation Equipment Rental | $1,500 | Trenching at 10ft depth requires machinery |
| Sensors & Data Loggers | $400 | Temperature, humidity, airflow monitoring |
| Project Manager Stipend | $2,000 | 2 months dedicated labor for construction |
| Contingency (15%) | $700 | Unforeseen material or equipment needs |
| **Total** | **$5,400** | |

---

## 8. Qualifications

**Jesse McMillen** is an independent researcher and inventor with hands-on experience in thermal systems, masonry, and material formulation. He has developed the OpenCell Aerocement formula through iterative experimentation and has validated the thermodynamic model through established engineering formulas (see `cold-storage-calculations.md`).

The project is supported by open-source documentation on GitHub (https://github.com/jesseray718/OpenCell-Thermal-System) and permanently archived on IPFS (CID: QmRkBpJg8SPJjvKjsEaqeyFMqwxdko417FZrDtWBNd493w).

---

## 9. Sustainability & Dissemination

*   **Open Source:** All designs, formulas, and data are published under CC-BY-NC-SA 4.0, ensuring permanent public access.
*   **Reproducibility:** The mixing protocol requires no specialized equipment — any farmer can produce Aerocement with basic tools.
*   **Commercial Pathway:** Commercial derivatives require a licensing agreement, creating a self-sustaining revenue stream for continued R&D.
*   **Dissemination:** Results will be shared via GitHub, agricultural extension offices, SARE conference presentations, and farmer workshops.

---

*Prepared by Jesse McMillen for the OpenCell Thermal-Mechanical Energy System Project.*
