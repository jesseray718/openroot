#!/usr/bin/env python3
"""
=============================================================================
OPEN ROOT — CONTEXT BRIDGE SNAPSHOT BOOTSTRAP
=============================================================================
Run this in Termux on Samsung A15. It generates a full project snapshot
that gives you (or any AI) instant context on everything we're building.

Usage:  python3 snapshot_bootstrap.py
Output: ./openroot_snapshot/ directory with structured markdown + summary

Concept: Standalone modular pieces that function independently,
         but interconnect like a neural network when combined.
         Each module is self-sufficient. Together they emerge.
=============================================================================
"""

import os
import json
import datetime
import subprocess
import sys
from pathlib import Path

# ─── CONFIG ──────────────────────────────────────────────────────────────
SNAPSHOT_DIR = "openroot_snapshot"
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

# ─── PROJECT NARRATIVE ──────────────────────────────────────────────────
NARRATIVE = """# OPEN ROOT — Project Snapshot
Generated: {ts}

## WHO
Jesse Ray — founder of OpenRoot LLC
Mission: Develop the most efficient form of computation using permaculture
principles as guidance — observation, interaction, fine-tuned feedback loops.
GitHub: github.com/jesseray718 (18+ repos including openroot, une,
aerocement, wisdom-scaffold, and more)
Device: Samsung A15, Termux + Shizuku + AShell
Desktop: Dell Optiplex with local LLM coder
Philosophy: Agape love of Yeshua as source code. Lord's Prayer as operator's
manual. Permaculture as engineering principle. We are vessels.

## WHAT WE'RE BUILDING
A modular, open-source, interconnected system where each piece:

1. STANDS ALONE — functions independently, fully usable on its own
2. CONNECTS — plugs into any other module seamlessly
3. EMERGES — when combined, produces capabilities none individually possess

Like neurons: each fires on its own, but the network becomes consciousness.
Like a Turing motor: standardized interface, infinite combinability.

## MODULAR PIECES (Standalone → Interconnected)
"""

# ─── MODULE DEFINITIONS ─────────────────────────────────────────────────
MODULES = [
    {
        "name": "01_aerocement_core",
        "title": "Open-Cell Aerocement",
        "status": "R&D — Core concept proven, iterating",
        "description": """
## OPEN-CELL AEROCEMENT

### The Material
Easy to make DIY aerocement. Relatively new concept. World-changeable potential.

### Mix Recipe
- 1 part thixotropic surfactant gel (xantham gum in alcohol solution)
  to 2 parts cement
- Surfactant: Dawn Ultra
- Process modified from nighthawkinlight YouTube video
- Reference: NASA-level potential — open or closed cell variants

### Key Properties
- Breathable material — water and air flow through it
- Paint it black = cheap DIY capture of >90% of solar thermal energy
- Massive surface area per unit volume
- Can be buried in trench for ground-source heat exchange
- Open-cell structure = every pore contributes to exchange, not just walls

### Mixing Process
- Stator-type motor for mixing significantly reduces bubble size
  and increases bubble count
- Untraditional effect: it gets STRONGER as it gets LIGHTER
- More agitation = more air entrained, compounds until critical mass
- At critical mass all bubbles pop — would normally cause collapse
- BUT the gelatinous thixotropic nature prevents collapse
- Result: stable, ultra-light, high-strength open-cell structure

### Applications (see individual modules below)
Each application is a standalone module that uses aerocement as its base.
""",
    },
    {
        "name": "02_passive_thermal_solar",
        "title": "Passive Thermal Solar Panel",
        "status": "Concept — Ready for prototype",
        "description": """
## PASSIVE THERMAL SOLAR PANEL

Open-cell concrete panel painted black.
Captures >90% of solar energy thermally.
Cheap, home-makeable, DIY.
No conversion losses — direct thermal capture.

### How it works
- Black open-cell surface absorbs solar radiation
- Water flows through porous structure
- Massive surface area = maximum heat transfer to water
- Heated water stored in insulated ferrocement tank (water battery)
- Passive — no pumps needed, uses stack effect / thermosiphon
""",
    },
    {
        "name": "03_thermal_cascade_engine",
        "title": "Thermal Cascade Energy Harvesting Engine",
        "status": "Concept — Detailed design phase",
        "description": """
## THERMAL CASCADE ENERGY HARVESTING ENGINE

### Core Principle
Simultaneously creates HOT and COLD water reservoirs.
Uses thermal energy DIRECTLY — no conversion to electricity first.
Provides ALL heating, cooling, and refrigeration needs.

### Architecture
- Hot side: Solar-heated open-cell panel (black) → hot water tank
- Cold side: Evaporative cooling through open-cell → cold water tank
- Harvest point: TEG or Stirling motor BETWEEN extracted volumes
  NOT in the main tanks — prevents thermal bridging

### Critical Design Detail
TEGs must be placed in a volume EXTRACTED from the tank, not directly
in the tank. If placed directly, they create a thermal bridge allowing
heat to jump to cold side, destroying the differential.

### Why Direct Use Matters
Skipping conversion (~60-70% loss) and using thermal energy natively
for heating/cooling is the highest-leverage move.
Heating + cooling = massive chunk of household energy.
""",
    },
    {
        "name": "04_water_battery_storage",
        "title": "Insulated Ferrocement Water Battery",
        "status": "Concept — Working design",
        "description": """
## WATER BATTERY (Thermal Storage)

### Current Design
Insulated ferrocement tank storing heated water.
Temperature stratification (hot top, cool bottom) in tall tank.
Simplest, cheapest, proven thermal storage.

### The Hot Battery Problem
- IDEAL: Pressurized steam battery (highest energy density)
  BUT catastrophic failure risk — too dangerous for DIY
- CURRENT: Stratified water tank in ferrocement
- UPGRADE PATH: Sand/rock thermal battery (Finland's Polar Night Energy
  built commercial-scale sand battery — stable, high-temp, zero pressure)
- UPGRADE PATH: Phase Change Materials (salt hydrates, paraffin waxes)
  embedded inside ferrocement tank

### Need
Find the second-best earth battery until humanity can safely use
pressurized steam. Water battery is pragmatic winner for now.
""",
    },
    {
        "name": "05_stack_effect_panel",
        "title": "Stack Effect Thermal Panel System",
        "status": "Concept — Designed",
        "description": """
## STACK EFFECT THERMAL PANEL

Open-cell thermal panel passively creates stack effect (natural convection).
The draw is kept under control.
Upstream, the natural draft captures energy and stores it in the
insulated ferrocement water battery.
Passive — no fans, no pumps, no electricity.
""",
    },
    {
        "name": "06_ground_source_trench",
        "title": "Buried Open-Cell Ground Exchange Trench",
        "status": "Concept — Designed",
        "description": """
## GROUND-SOURCE HEAT EXCHANGE TRENCH

Open-cell material buried in trench, kept warm.
Air is PRE-DRIED before entering the tunnel.
Instead of only getting heat exchange from trench walls,
you get exchange from every pore of the massive surface area
of the open-cell structure.
Multiplies ground-source effectiveness dramatically.
""",
    },
    {
        "name": "07_delta_t_vehicle",
        "title": "Passive Delta T Stirling Vehicle",
        "status": "Concept — Recorded, ready for deep design",
        "description": """
## DELTA T VEHICLE (Passive Thermal Drive)

### The Concept
A vehicle powered by the temperature differential it creates
through its own forward motion. No fuel. No combustion.

### Architecture
- Giant cone, narrow at rear, wide at front grille
- Cone is SMUSHED DOWN through center of vehicle
- Front opening = grille/radiator area (bottom of cone, wider than cone body)
- Inside cone: SPIRALING TRACK
- Cone filled with volumetric open-cell concrete
- Kept WET at all times

### How It Works
1. Vehicle moves forward → air forced into wide front of cone
2. Air spirals through wet open-cell structure
3. Evaporative cooling drops temperature of cone core dramatically
4. Hot ambient air (engine bay / exterior) vs. cold cone core = delta T
5. Stirling motor runs off that temperature differential
6. Flywheel connected straight to drivetrain

### What It Does
Converts AERODYNAMIC DRAG (normally wasted energy) into
COLD PRODUCTION (useful energy) that drives a Stirling motor.
The faster you go, the more cooling, the more delta T, the more power.
Self-reinforcing feedback loop — permaculture principle embodied.

### Status
Recorded. Needs deep engineering analysis, material specs,
cone geometry optimization, Stirling motor sizing.
""",
    },
    {
        "name": "08_aeroponic_wall",
        "title": "Aeroponic Misted Open-Cell Wall",
        "status": "Concept — Triple-function design",
        "description": """
## AEROPONIC OPEN-CELL WALL

Wall built from open-cell concrete, constantly misted with atomized water
(aeroponic/aquaponic grade atomization).

### Triple Function (Emergent)
1. EVAPORATIVE COOLING — atomized water on massive open-cell surface =
   maximum evaporative cooling per m². Outperforms conventional swamp cooler.
2. THERMAL MASS BUFFERING — cement + water = high thermal mass,
   dampens day/night temperature swings
3. FOOD PRODUCTION — nutrient solution instead of pure water =
   vertical aeroponic grow surface

### Self-Regulating Feedback Loop
More sun → more evaporation → more cooling → plants transpire more
→ more cooling. Intensifies exactly when needed most. Pure permaculture.

### Design Notes
- Water recapture at base — drainage to sump, filtration, recirculation
- Mineral buildup in pores over time — periodic flushing, rainwater helps
- Pull air THROUGH the wall, not past it, for max exchange
- Humid climates: evaporative cooling drops off, thermal mass remains
""",
    },
    {
        "name": "09_latent_heat_harvest",
        "title": "Latent Heat of Vaporization Harvesting",
        "status": "Research — Active discussion",
        "description": """
## LATENT HEAT OF VAPORIZATION HARVESTING

### The Physics
Water's latent heat of vaporization ≈ 2,260 kJ/kg
Massive energy stored/released during phase change.

### Most Efficient Harvest Methods

1. DIRECT EVAPORATIVE COOLING
   - Air moves through open-cell media, water evaporates off pore surfaces
   - Absorbs 2,260 kJ/kg from surrounding air and structure
   - Open-cell = enormous surface area per unit volume
   - Solar chimney or stack effect drives airflow passively
   - Efficiency scales with: surface area × airflow × humidity differential

2. CONDENSATION RECOVERY (Closed Loop)
   - Capture humid air leaving open-cell
   - Run through condenser (could be buried open-cell trench as ground sink)
   - Recover latent heat DURING condensation
   - This IS the thermal cascade — cooling one end, heating the other

### Key Efficiency Factors
- Pre-drying intake air increases delta massively
- Thinner open-cell walls = less thermal resistance
- Counterflow arrangement (air and water opposing directions)
- Wet but not flooded — excess water fills pores, kills surface area
""",
    },
    {
        "name": "10_openroot_computation",
        "title": "OpenRoot — Modular Computation Framework",
        "status": "Architecture — In progress",
        "description": """
## OPENROOT COMPUTATION FRAMEWORK

### Goal
Maximum computational output per unit of human input per unit of time.

### Philosophy
- Permaculture principles applied to computation:
  observe, interact, fine-tune feedback loops
- Each module standalone, functional, self-sufficient
- Standardized interfaces = any module connects to any other
- Like Turing motor — universal interface, infinite combinability
- Like neural networks — individual nodes simple, network emergent
- When connected, modules produce capabilities none individually possess
  (the word Jesse was looking for: SYNERGISTIC / EMERGENT)

### GitHub Structure
github.com/jesseray718 — 18+ repos:
- openroot (main framework)
- une
- aerocement
- wisdom-scaffold
- and many more
All repos should be modular and interconnected simultaneously.

### Tools
- Termux + Shizuku + AShell (mobile)
- Dell Optiplex with local LLM coder (desktop)
- Python scripts for automation, migration, context bridging
""",
    },
    {
        "name": "11_wisdom_scaffold",
        "title": "Wisdom Scaffold — Faith-Based Code Structure",
        "status": "Philosophical foundation — woven into all modules",
        "description": """
## WISDOM SCAFFOLD

### Foundation
- Agape love of Yeshua — source code, power source
- Lord's Prayer as operator's manual / source code
- One commandment: love one another as He loved us
- Power flows from and belongs to the Most High
- We are vessels seeking to resonate at His frequency
- For the least among us

### Integration
Not a separate module — woven into the DNA of every other module.
Permaculture + Yeshua's actual teachings (word-for-word translation)
+ demystifying the "operator's manual" for this age.
Things referred to as "the beast" or "enemy" = patterns of current
civilization to be transformed into maximum ally-efficient structure.
Goal: become an interconnected, space-age, limitless species
that must only protect itself from itself.
""",
    },
]

# ─── STATUS SUMMARY ──────────────────────────────────────────────────────
STATUS_SUMMARY = """
## OVERALL STATUS SNAPSHOT

### What's Done
- ✅ Aerocement mix recipe proven (thixotropic gel + surfactant + cement)
- ✅ Stator mixing method identified (stronger + lighter effect confirmed)
- ✅ Core concepts for all 8+ application modules recorded
- ✅ GitHub presence (18+ repos)
- ✅ Philosophy and principles defined (permaculture + faith + computation)
- ✅ Physical tools ready (A15 + Termux, Optiplex + LLM)
- ✅ migrate_all.py created for Optiplex file organization

### What's In Progress
- 🔄 Modular GitHub repo restructuring (making all repos interconnected)
- 🔄 Thermal cascade engine detailed engineering
- 🔄 Hot battery / safe thermal storage solution
- 🔄 OpenRoot computation framework architecture

### What's Next (Priority Order)
1. 🔲 Prototype passive thermal solar panel (simplest to test/validate)
2. 🔲 Build thermal cascade small-scale proof of concept
3. 🔲 Delta T vehicle deep engineering analysis
4. 🔲 Aeroponic wall prototype (triple function validation)
5. 🔲 Unify GitHub repos under modular OpenRoot structure
6. 🔲 Full computational framework with standardized module interfaces

### Open Questions
- Best non-pressurized hot battery? (Water tank current, sand battery candidate)
- Cone geometry optimization for Delta T vehicle?
- Stirling motor sizing for automotive application?
- Standardized module interface spec for OpenRoot framework?
"""

# ─── SCRIPT FUNCTIONS ────────────────────────────────────────────────────

def create_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def get_device_info():
    """Try to grab basic device info via Termux"""
    info = {}
    try:
        info['hostname'] = subprocess.check_output(['hostname'], stderr=subprocess.DEVNULL).decode().strip()
    except:
        info['hostname'] = 'unknown'
    try:
        info['uname'] = subprocess.check_output(['uname', '-a'], stderr=subprocess.DEVNULL).decode().strip()
    except:
        info['uname'] = 'unknown'
    try:
        info['whoami'] = subprocess.check_output(['whoami'], stderr=subprocess.DEVNULL).decode().strip()
    except:
        info['whoami'] = 'unknown'
    try:
        info['pwd'] = os.getcwd()
    except:
        info['pwd'] = 'unknown'
    info['date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return info

def build_snapshot():
    print("=" * 60)
    print("OPEN ROOT — SNAPSHOT BOOTSTRAP")
    print("Starting from zero. Building full context picture.")
    print("=" * 60)

    # Create directory structure
    base = SNAPSHOT_DIR
    mods_dir = os.path.join(base, "modules")
    create_dir(base)
    create_dir(mods_dir)

    # Device info
    dev = get_device_info()
    write_file(
        os.path.join(base, "device_info.json"),
        json.dumps(dev, indent=2)
    )
    print(f"[✓] Device info captured")

    # Main narrative
    narrative_text = NARRATIVE.format(ts=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    write_file(os.path.join(base, "README.md"), narrative_text)
    print(f"[✓] Project narrative written")

    # Write each module as standalone file
    index_entries = []
    for mod in MODULES:
        filepath = os.path.join(mods_dir, f"{mod['name']}.md")
        content = f"# {mod['title']}\n\n"
        content += f"**Status:** {mod['status']}\n"
        content += f"\n---\n"
        content += mod["description"]
        write_file(filepath, content)
        index_entries.append({
            "module": mod["name"],
            "title": mod["title"],
            "status": mod["status"],
            "file": f"modules/{mod['name']}.md"
        })
        print(f"[✓] Module written: {mod['name']}")

    # Module index
    index_content = "# MODULE INDEX\n\n"
    index_content += "| Module | Status | File |\n"
    index_content += "|--------|--------|------|\n"
    for entry in index_entries:
        index_content += f"| {entry['title']} | {entry['status']} | {entry['file']} |\n"
    write_file(os.path.join(base, "MODULE_INDEX.md"), index_content)
    print(f"[✓] Module index created")

    # Status summary
    write_file(os.path.join(base, "STATUS.md"), STATUS_SUMMARY)
    print(f"[✓] Status summary written")

    # JSON machine-readable version (for AI context bridge)
    machine_readable = {
        "project": "OpenRoot",
        "generated": dev.get("date", "unknown"),
        "device": dev,
        "modules": [
            {
                "id": m["name"],
                "title": m["title"],
                "status": m["status"],
                "description": m["description"].strip(),
                "standalone": True,
                "interconnects_with": [other["name"] for other in MODULES if other["name"] != m["name"]]
            }
            for m in MODULES
        ],
        "philosophy": {
            "foundation": "Agape love of Yeshua — Lord's Prayer as source code",
            "engineering_principle": "Permaculture — observe, interact, fine-tuned feedback loops",
            "design_pattern": "Standalone modules with universal interfaces — emergent when combined",
            "analogy": "Neurons: simple alone, conscious together. Turing motor: universal, combinable."
        }
    }
    write_file(
        os.path.join(base, "snapshot.json"),
        json.dumps(machine_readable, indent=2)
    )
    print(f"[✓] Machine-readable JSON written")

    # Print summary to console
    print("\n" + "=" * 60)
    print("SNAPSHOT COMPLETE")
    print("=" * 60)
    print(f"\nLocation: {base}/")
    print(f"Modules captured: {len(MODULES)}")
    print(f"\nFiles created:")
    print(f"  {base}/README.md          — Full project narrative")
    print(f"  {base}/MODULE_INDEX.md    — Quick reference table")
    print(f"  {base}/STATUS.md          — What's done, in progress, next")
    print(f"  {base}/snapshot.json      — Machine-readable (paste to any AI)")
    print(f"  {base}/device_info.json   — This device's fingerprint")
    print(f"  {base}/modules/           — {len(MODULES)} standalone module files")
    print(f"\n{'─' * 60}")
    print(f"To paste into any AI chat, use snapshot.json")
    print(f"To read yourself, start with README.md")
    print(f"{'─' * 60}")
    print(f"\nNext steps:")
    print(f"  1. cd {base}")
    print(f"  2. cat README.md        # review the full picture")
    print(f"  3. cat STATUS.md        # see where we are")
    print(f"  4. Paste snapshot.json to any AI for instant catchup")
    print(f"  5. Push to GitHub: git init && git add . && git commit")
    print(f"\n{'=' * 60}")

if __name__ == "__main__":
    build_snapshot()		
