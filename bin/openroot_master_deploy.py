#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0
# OpenRoot Dense Master Engine: Agape Taxonomy, Aero-Disc Simulation & GitHub Wiki Pipeline

import os, sys, json, math, re, sqlite3, subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("/data/data/com.termux/files/home/openroot") if Path("/data/data/com.termux").exists() else Path.cwd()
OUTDIR = Path("/storage/emulated/0/openroot/outbox") if Path("/storage/emulated/0/openroot").exists() else ROOT / "outbox"
WIKI_DIR = ROOT / "wiki"
WORKFLOW_DIR = ROOT / ".github" / "workflows"

for d in (ROOT / "bin", ROOT / "data", OUTDIR, WIKI_DIR, WORKFLOW_DIR):
    d.mkdir(parents=True, exist_ok=True)

# --- 1. AGAPE ETYMOLOGY & 36-SYMBOL EUCLIDEAN TAXONOMY ---
AGAPE_DRIFT = {
    "el_koine": {"word": "Ἀγάπη", "era": "c. 30 AD", "drift_metric": 0.00, "def": "Unconditional volumetric goodwill"},
    "la_vulgate": {"word": "Caritas", "era": "c. 400 AD", "drift_metric": 0.12, "def": "Precious regard and active care"},
    "en_kjv_1611": {"word": "Charity", "era": "1611 AD", "drift_metric": 0.24, "def": "Benevolent community action"},
    "en_modern": {"word": "Love", "era": "2026 AD", "drift_metric": 0.68, "def": "General emotional preference"}
}

LORDS_PRAYER_WORD_FOR_WORD = [
    {"greek": "Πάτερ ἡμῶν ὁ ἐν τοῖς οὐρανοῖς", "literal": "Father of us, the [one] in the heavens"},
    {"greek": "ἁγιασθήτω τὸ ὄνομά σου", "literal": "let be sanctified the name of You"},
    {"greek": "ἐλθέτω ἡ βασιλεία σου", "literal": "let come the sovereign realm of You"},
    {"greek": "γενηθήτω τὸ θέλημά σου, ὡς ἐν οὐρανῷ καὶ ἐπὶ γῆς", "literal": "let be done the will of You, as in heaven also upon earth"},
    {"greek": "τὸν ἄρτον ἡμῶν τὸν ἐπιούσιον δὸς ἡμῖν σήμερον", "literal": "The bread of us, necessary for existence, give us today"},
    {"greek": "καὶ ἄφες ἡμῖν τὰ ὀφειλήματα ἡμῶν", "literal": "and release for us the debts of us"},
    {"greek": "ὡς καὶ ἡμεῖς ἀφήκαμεν τοῖς ὀφειλέταις ἡμῶν", "literal": "as also we released the debtors of us"},
    {"greek": "καὶ μὴ εἰσενέγκῃς ἡμᾶς εἰς πειρασμόν, ἀλλὰ ῥῦσαι ἡμᾶς ἀπὸ τοῦ πονηροῦ", "literal": "and do not lead us into trial, but deliver us from destructive evil"}
]

SYMBOLS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
FIELDS = [
    "Agape Root Axis", "Biological Energetics", "Civil Construction", "Dynamic Heat Flow",
    "Entropy Mitigation", "Fluid Dynamics", "Geodesic Structure", "Hydrological Cycles",
    "Information Routing", "Jurisprudence Law", "Kinetic Conversion", "Lattice Topologies",
    "Material Science", "Node Recursion", "Open Hardware", "Permaculture Systems",
    "Quantum Thermal State", "Radiant Energy", "Subterranean Mass", "Thermodynamic Ledger",
    "Universal Native Descriptor", "Volumetric Exchange", "Waste Cascades", "Xenobiotic Decay",
    "Yield Optimization", "Zero-Coordination Engine", "Primary Production 0", "Storage Mass 1",
    "Flow Channels 2", "Conversion Gates 3", "Feedback Loops 4", "Boundary Enclosures 5",
    "Resilience Buffer 6", "System Audits 7", "Network Propagation 8", "Ecosystem Equilibrium 9"
]

def build_taxonomy_36():
    tax = {}
    for i, char in enumerate(SYMBOLS):
        ang = (2 * math.pi * i) / 36
        tax[char] = {
            "symbol": char, "field": FIELDS[i],
            "coords": {"x": round(math.cos(ang), 4), "y": round(math.sin(ang), 4), "z": round(i / 36.0, 4)},
            "taxonomy": {"kingdom": "Agape Root", "phylum": f"Domain-{char}", "order": FIELDS[i].split()[0]}
        }
    return tax

# --- 2. AERO-DISC FLUID SIMULATION & G-CODE GENERATOR ---
def simulate_aerodisc(flow_lpm=5.0, t_in=80.0, t_amb=20.0):
    m_dot = (flow_lpm / 60.0 / 1000.0) * 997.0
    cp = 4184.0
    h_v = 2500.0 * 150.0
    v_bed = 0.0005
    eff = 1.0 - math.exp(-(h_v * v_bed) / (m_dot * cp))
    q_watts = m_dot * cp * (t_in - t_amb) * eff
    t_out = t_in - (q_watts / (m_dot * cp))
    return {"flow_lpm": flow_lpm, "t_in_c": t_in, "t_out_c": round(t_out, 2), "watts": round(q_watts, 2), "efficiency_pct": round(eff * 100, 1)}

def generate_gcode(path: Path):
    lines = [
        "; Aero-Disc Outer Casing - PETG Parametric",
        "G28 ; Home all axes", "G90 ; Absolute positioning",
        "M104 S240", "M140 S70", "M109 S240", "M190 S70", "G92 E0", "G1 Z0.3 F1200"
    ]
    cx, cy, r, steps = 110.0, 110.0, 40.0, 36
    for layer in range(1, 11):
        z = round(layer * 0.2, 2)
        lines.append(f"; Layer {layer} Z={z}")
        lines.append(f"G1 Z{z} F900")
        for i in range(steps + 1):
            ang = (2 * math.pi * i) / steps
            x = round(cx + r * math.cos(ang), 3)
            y = round(cy + r * math.sin(ang), 3)
            lines.append(f"G1 X{x} Y{y} E{round(i * 0.15, 3)} F1800")
    lines.extend(["M104 S0", "M140 S0", "G1 X0 Y200 F3000", "M84"])
    path.write_text("\n".join(lines), encoding="utf-8")

# --- 3. REPO LINK REPAIR, WIKI & WORKFLOW PERSISTENCE ---
def fix_links_and_build_wiki():
    readme = ROOT / "README.md"
    if readme.exists():
        txt = readme.read_text(encoding="utf-8")
        readme.write_text(re.sub(r'\[([^\]]+)\]\((?!http|https|#)([^)]+)\)', r'[\1](./\2)', txt), encoding="utf-8")

    pages = {
        "Home.md": "# OpenRoot Ecosystem Wiki\n- [[Agape-Taxonomy-36]]\n- [[Aero-Disc-Exchanger]]\n- [[Permaculture-Integration]]",
        "Agape-Taxonomy-36.md": "# 36-Symbol Agape Taxonomy Matrix\nMaps characters A-Z, 0-9 into 3D Euclidean space.",
        "Aero-Disc-Exchanger.md": "# Aero-Disc Volumetric Heat Exchanger\nPorous-matrix thermal simulation and print G-code specs.",
        "Permaculture-Integration.md": "# Permaculture Infrastructure\nBlack Locust coppicing coupled with thermal storage mass."
    }
    for fname, content in pages.items():
        (WIKI_DIR / fname).write_text(content, encoding="utf-8")

    (WORKFLOW_DIR / "main.yml").write_text("""name: OpenRoot Node CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Deploy Verification
        run: python3 bin/openroot_master_deploy.py
""", encoding="utf-8")

# --- EXECUTION ---
if __name__ == "__main__":
    tax_data = build_taxonomy_36()
    sim_data = simulate_aerodisc()
    gcode_path = OUTDIR / "aerodisc_casing.gcode"
    generate_gcode(gcode_path)
    fix_links_and_build_wiki()

    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "agape_drift": AGAPE_DRIFT,
        "lords_prayer_exact": LORDS_PRAYER_WORD_FOR_WORD,
        "taxonomy_36": tax_data,
        "aerodisc_sim": sim_data,
        "artifacts": [str(gcode_path), str(WORKFLOW_DIR / "main.yml")]
    }
    
    (OUTDIR / "agape_master_manifest.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"status": "SUCCESS", "sim": sim_data, "wiki_pages": len(list(WIKI_DIR.glob("*.md")))}, indent=2))
