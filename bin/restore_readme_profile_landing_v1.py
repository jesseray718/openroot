#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0
# restore_content_v1.py — Restore README, Profile, Landing page after v2 rewrite
# Restores: badges (PoPW, Thermal Ledger, Zenodo, CI/CD), hardware overview,
#           profile page, landing page index.html
# DRY-RUN default. CONFIRM=1 commits+pushes. Human is the only commit gate.
# [canary] restore_content_v1_CANARY_MARKER
import os, sys, platform, subprocess
from datetime import datetime, timezone

REPO = "/home/jesse/openroot"
CONFIRM = os.environ.get("CONFIRM", "0") == "1"

def say(tag, msg): print(f"[{tag}] {msg}")

def sh(cmd, check=True):
    r = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=REPO,
                       capture_output=True, text=True)
    if check and r.returncode != 0:
        say("held", f"FAIL: {cmd}\n{r.stderr.strip()[:300]}"); sys.exit(1)
    return r

assert platform.node() == "optiplex3060", "[held] run on optiplex3060"
os.chdir(REPO)
print("[gate] start CONFIRM=" + str(CONFIRM))

# ── STAGE 1: README.md restoration ───────────────────────────────
readme = """# OpenRoot — The Thermodynamic Commons

**Physical infrastructure + the computational swarm that serves it.**

> η = useful_joules / human_joules
> Every cycle must close on real thermal, material, or food yield.

---

## Status Badges

| Proof | Ledger | Publication | Quality |
|-------|--------|-------------|---------|
| ![Proof of Physical Work](https://img.shields.io/badge/PoPW-8.13M%20ACRE-brightgreen?style=flat-square&logo=bitcoin) | ![Thermal Ledger](https://img.shields.io/badge/Thermal%20Ledger-12.91%20kWh/m²%2Fnight-blue?style=flat-square&logo=thermal) | ![Zenodo](https://img.shields.io/badge/Zenodo-10.5281/zenodo.21225683-589632?style=flat-square&logo=zenodo) | ![License GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-orange?style=flat-square&logo=gnu) |
| ![ACRE Token](https://img.shields.io/badge/ACRE-16.27M%20cumulative-purple?style=flat-square&logo=solana) | ![Bitcoin Anchor](https://img.shields.io/badge/Bitcoin%20Anchor-3%20confirmed-black?style=flat-square&logo=bitcoin) | ![IPFS](https://img.shields.io/badge/IPFS-4%20CIDs%20pinned-ff5500?style=flat-square&logo=ipfs) | ![Last Commit](https://img.shields.io/github/last-commit/jesseray718/openroot?style=flat-square) |

---

## Quick Jump

| If you want... | Click here | Why |
|----------------|------------|-----|
| **Plain-language intro** | [START-HERE.md](START-HERE.md) | No jargon — credit, energy, what to do this week |
| **Full thesis** | [THESIS.md](THESIS.md) | The complete thermodynamic argument |
| **Hardware builds** | [aerocement/](aerocement/) | Volumetric blackbody concrete recipes |
| **Talent alignment** | [TALENT-ALIGNMENT-PROMPT.md](TALENT-ALIGNMENT-PROMPT.md) | Map ANY skill to the Four Engines |
| **Community standards** | [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | How we treat each other |

---

## The Four Engines

| Engine | Purpose | Live Components |
|--------|---------|-----------------|
| **Knowledge** | Axioms, postulates, governance | 7 physics axioms, fractal constitution |
| **Energy** | Passive solar-thermal, storage | Black Locust coppice + RMH, H-003 thermal cascade |
| **Material** | Shelter, water, food | Aerated GFRC panels, ferrocement domes, aquaponics |
| **Finance** | Credit-building, ACRE token | PRF-001 routing, PoWr minting, thermodynamic ledger |

**Permaculture principle:** Each engine serves multiple functions. Each node generates surplus. Nothing extracted, nothing wasted.

---

## Hardware We're Building

### ① AeroCement H-003 Thermal Cascade
- **Volumetric blackbody concrete** — 95%+ solar absorption
- **Passive stack-effect circulation** — no pumps
- **Subterranean thermal storage** — 35°F cooling from 120°F inlet
- **Target:** 12.91 kWh/m² nightly capture (validated simulation)
- **Status:** Simulation complete, physical prototype needed

### ② Black Locust Coppice + Rocket Mass Heater
- **Carbon-negative forestry** — roots sequester while tops are burned
- **85-95% combustion efficiency** vs 50-70% conventional stoves
- **12-24 hour thermal mass storage** — one burn cycle heats a day
- **η multiplier:** 75-100× over traditional firewood processing

### ③ Ferrocement Dome Panels
- **Bolt-together modular** — LEGO-like assembly
- **Hurricane/earthquake/fire resistant**
- **Single-material structure** — walls + insulation + foundation
- **Drill-and-bucket buildable** — no industrial equipment

### ④ Offline Mesh Node
- **Recycled hardware** — phones, routers, mini PCs
- **Offline LLMs** — Ollama/llama.cpp, no cloud dependency
- **Long-range mesh radios** — comms that cannot be shut off
- **Energy independent** — solar-powered, battery-buffered

---

## Thermodynamic Ledger

The ledger proves every claim with measurable joules:

| Component | Status | Proof |
|-----------|--------|-------|
| Merkle audit trail | ✅ Live | `audit_trail.jsonl` → 32-byte root |
| Bitcoin-anchored snapshots | ✅ Confirmed | 3 OpenTimestamps on Bitcoin blockchain |
| Landauer + E=mc² bridge | ✅ Working | 256 bits → 7.36e-19 J → 8.19e-36 kg |
| ARM energy measurement | ✅ Live | CPU freq scaling → joule estimation |
| Kai9000 heartbeat | ⏳ Instrumenting | 0.26234 J/cycle target |

**Properties:**
- Root size: 32 bytes (constant, regardless of history length)
- Verification cost: log₂(N) hash operations
- Bitcoin-anchored via OpenTimestamps (independently verifiable)

---

## Contributing

**Shared credit is the doctrine.** See [CONTRIBUTING.md](CONTRIBUTING.md) and [START-HERE.md](START-HERE.md).

### How to Join
1. Read the talent alignment prompt above
2. Post output as GitHub issue with label `talent-alignment`
3. Fork relevant repo, submit PR within 2 weeks
4. Receive credit in README (auto-updated via `bin/pr_intake.sh`)

### Current Priorities
| Role | What You'd Do | Capital Needed | Timeline |
|------|--------------|----------------|----------|
| Experimentalist | Build H-003 prototype, log 30 days data | $2,000-5,000 | 8 weeks |
| Smart Contract Dev | ACRE validator on Solana | $0 (devnet free) | 10 weeks |
| Mesh Engineer | Deploy offline node on Raspberry Pi | $180-250 | 10 weeks |
| Material Scientist | Validate AE-GFRC simulations | $500-1,500 | 12 weeks |

See issue #5: [Call to Builders — OpenRoot Needs You](https://github.com/jesseray718/openroot/issues/5)

---

## Publications & Proofs

| Medium | Identifier | Content |
|--------|------------|---------|
| Zenodo | [10.5281/zenodo.21225683](https://doi.org/10.5281/zenodo.21225683) | Thermal system specs (WBTE-01, CTBS-01, AE-GFRC-01) |
| IPFS | QmbNEo5Qjqtug1BRYj4GKNyohdo1EkvLrZZRNrfmqMKpzY | v0.6 milestone publication |
| Solana | 3fF26gcj1ednMUASxJxo1dt5rQ2ZegXbH7k4ynJazerk | ACRE smart contract |
| Bitcoin | 3 OpenTimestamps confirmed | Ledger snapshots anchored |

---

## License

- **Hardware/Documentation:** CC-BY-SA-4.0
- **Software:** GPL-3.0
- **Patents:** None. Ever. Defensive publication only.

**Copyright:** One Human Family

---

## Contact

- **Email:** jrm8908@proton.me
- **GitHub:** [github.com/jesseray718](https://github.com/jesseray718)
- **Profile Atlas:** [jesseray718.github.io](https://jesseray718.github.io)
- **SimpleX Channel:** [Join the mesh](https://smp9.simplex.im/a#vklZrSjZTQdgXBqW_sLK1h5FeajDoa7wTaSWGSw62Sw)

---

*Engineering as an act of unconditional integration.*
*The unification is not something you do. It is something you stop denying.*
"""

with open("README.md", "w") as f:
    f.write(readme)

say("banked", "README.md regenerated with all badges, hardware overview, ledger status")

# ── STAGE 2: Profile Page Update (jesseray718.github.io) ─────────────
profile_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Jesse Ray — OpenRoot</title>
<style>
  :root{--bg:#0c0c0c;--card:#161616;--border:#2a2a2a;--text:#e8e8e8;--muted:#999;--accent:#7dd3a0}
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;line-height:1.6;padding:1.5rem;max-width:680px;margin:0 auto}
  header{padding:1.5rem 0;border-bottom:1px solid var(--border);margin-bottom:2rem}
  h1{font-size:2rem;font-weight:700;margin-bottom:.5rem}
  .subtitle{color:var(--muted);font-size:1.1rem}
  section{margin-bottom:2rem}
  h2{font-size:1rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:.8rem}
  .grid{display:grid;gap:1rem}
  a.card{display:block;background:var(--card);border:1px solid var(--border);border-radius:10px;padding:1rem;text-decoration:none;color:var(--text)}
  a.card:hover{border-color:var(--accent)}
  a.card strong{display:block;font-size:1.1rem;margin-bottom:.3rem;color:var(--accent)}
  a.card span{font-size:.9rem;color:var(--muted)}
  .bio{background:var(--card);padding:1.2rem;border-radius:10px;border-left:3px solid var(--accent)}
  footer{margin-top:2.5rem;padding-top:1.2rem;border-top:1px solid var(--border);font-size:.85rem;color:var(--muted)}
  footer a{color:var(--accent);text-decoration:none}
</style>
</head>
<body>
<header>
  <h1>Jesse Ray</h1>
  <p class="subtitle">Independent Appropriate-Technology Inventor — OpenRoot</p>
</header>

<section class="bio">
  <p><strong>Building decentralized infrastructure for food, energy, shelter, and community.</strong></p>
  <p style="margin-top:.8rem">Working from a Samsung Galaxy A15 using Termux and open-source toolchains. Not affiliated with any institution. The entire OpenRoot framework is documented on-device and published to IPFS/Zenodo/Bitcoin.</p>
</section>

<section>
  <h2>Primary Projects</h2>
  <div class="grid">
    <a class="card" href="https://github.com/jesseray718/openroot">
      <strong>OpenRoot</strong>
      <span>Thermodynamic commons — physical infrastructure + AI swarm. Thermal cascade, aerated concrete, ACRE token.</span>
    </a>
    <a class="card" href="https://github.com/jesseray718/agape-une">
      <strong>Agape-UNE</strong>
      <span>Theory layer — ethics, axioms, mathematics of cooperation.</span>
    </a>
    <a class="card" href="https://github.com/jesseray718/aerocement">
      <strong>AeroCement</strong>
      <span>Glass-fiber aerated concrete recipes + passive cooling systems.</span>
    </a>
    <a class="card" href="https://github.com/jesseray718/openroot-spoke-template">
      <strong>Spoke Template</strong>
      <span>Fork skeleton for new OpenRoot nodes. Ready for deployment.</span>
    </a>
  </div>
</section>

<section>
  <h2>Publications & Proofs</h2>
  <div class="grid">
    <a class="card" href="https://doi.org/10.5281/zenodo.21225683">
      <strong>Zenodo DOI</strong>
      <span>Thermal system specifications (WBTE-01, CTBS-01, AE-GFRC-01)</span>
    </a>
    <a class="card" href="https://github.com/jesseray718/openroot/blob/main/THESIS.md">
      <strong>OpenRoot Thesis v3.0</strong>
      <span>Complete thermodynamic argument. Bitcoin-anchored.</span>
    </a>
  </div>
</section>

<section>
  <h2>Contact</h2>
  <p>Email: jrm8908@proton.me</p>
  <p>SimpleX: <a href="https://smp9.simplex.im/a#vklZrSjZTQdgXBqW_sLK1h5FeajDoa7wTaSWGSw62Sw" style="color:var(--accent)">Join mesh channel</a></p>
  <p>Location: Sikeston, Missouri</p>
</section>

<footer>
  <p>Licensed CC-BY-SA-4.0 (docs) / GPL-3.0 (code). No patents. Ever.</p>
  <p style="margin-top:.4rem"><a href="https://github.com/jesseray718">GitHub Profile</a> · <a href="https://github.com/jesseray718/openroot">OpenRoot Repo</a></p>
</footer>
</body>
</html>
"""

os.makedirs("site", exist_ok=True)
with open("site/index.html", "w") as f:
    f.write(profile_html)

say("banked", "Profile page updated: site/index.html")

# ── STAGE 3: Landing Page Upgrade (index.html in root) ────────────
landing_html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OpenRoot — Nanobot Swarm + Physical Infrastructure</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🌱</text></svg>">
<style>
  :root{--bg:#0c0c0c;--card:#161616;--border:#2a2a2a;--text:#e8e8e8;--muted:#999;--accent:#7dd3a0;--accent2:#6bb3f0;--warn:#e0b060}
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;line-height:1.55;padding:1.25rem;max-width:720px;margin:0 auto}
  header{margin-bottom:2.2rem}
  h1{font-size:1.85rem;font-weight:700;letter-spacing:-0.03em;margin-bottom:.35rem}
  .tagline{color:var(--muted);font-size:1.05rem}
  .quote{margin:1.4rem 0;padding:1rem 1.1rem;border-left:3px solid var(--accent);background:var(--card);font-size:.95rem;color:#ccc}
  section{margin-bottom:2.1rem}
  h2{font-size:.78rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-bottom:.8rem}
  .grid{display:grid;gap:.7rem}
  a.card{display:block;background:var(--card);border:1px solid var(--border);border-radius:10px;padding:.95rem 1.1rem;text-decoration:none;color:var(--text)}
  a.card:hover,a.card:active{border-color:var(--accent)}
  a.card strong{display:block;font-size:1.05rem;margin-bottom:.15rem}
  a.card span{font-size:.88rem;color:var(--muted)}
  .primary{border-color:#3a5a4a;background:#121a15}
  .primary strong{color:var(--accent)}
  .live{border-color:#4a3a1a;background:#1a1610}
  .live strong{color:var(--warn)}
  footer{margin-top:2.8rem;padding-top:1.4rem;border-top:1px solid var(--border);font-size:.82rem;color:var(--muted)}
  footer a{color:var(--accent2);text-decoration:none}
</style>
</head>
<body>
<header>
  <h1>OpenRoot</h1>
  <p class="tagline">Physical infrastructure + the computational swarm that serves it</p>
  <div class="quote">
    η = useful_joules / human_joules<br>
    Every cycle must close on real thermal, material, or food yield.
  </div>
</header>

<section>
  <h2>Status</h2>
  <div class="grid">
    <a class="card live" href="https://github.com/jesseray718/openroot">
      <strong>Latest: PR #63 Squash-Merged</strong>
      <span>Reh1t: LLM & SQLite RAG Integration (issue #53 closed). HEAD: 181702a9</span>
    </a>
  </div>
</section>

<section>
  <h2>Primary Attraction — Nanobot Swarm</h2>
  <div class="grid">
    <a class="card primary" href="https://github.com/jesseray718/openroot/blob/main/nanobot_team_blueprint.md">
      <strong>Nanobot Swarm Blueprint (Scaled v2)</strong>
      <span>Fractal tiers 0→4 · UNE nomenclature · physical circuit closure · ACRE from verified yield</span>
    </a>
    <a class="card live" href="https://github.com/jesseray718/openroot/blob/main/computational_flow/scheduler_local.sh">
      <strong>Live Local Scheduler (v0.3)</strong>
      <span>Tier router running on phone today. Local-first, thermal-aware, logs PoWr</span>
    </a>
    <a class="card" href="https://github.com/jesseray718/openroot/blob/main/nanobot_lattice.py">
      <strong>nanobot_lattice.py</strong>
      <span>Core lattice implementation</span>
    </a>
    <a class="card" href="https://github.com/jesseray718/openroot/tree/main/context_bridge">
      <strong>Context Absorbers</strong>
      <span>absorb_now · absorb_full_session · absorb_to_wisdom</span>
    </a>
    <a class="card" href="https://github.com/jesseray718/openroot/tree/main/swarm">
      <strong>swarm/</strong>
      <span>Current swarm directory + ratchet</span>
    </a>
  </div>
</section>

<section>
  <h2>Start Here (Human Path)</h2>
  <div class="grid">
    <a class="card" href="https://github.com/jesseray718/openroot/blob/main/START-HERE.md">
      <strong>START-HERE.md</strong>
      <span>Plain-language entry — credit, energy, what to do this week</span>
    </a>
    <a class="card" href="https://github.com/jesseray718/openroot/blob/main/THESIS.md">
      <strong>THESIS.md</strong>
      <span>Full argument — thermodynamics of abundance</span>
    </a>
    <a class="card" href="https://github.com/jesseray718/openroot/blob/main/STRUCTURE.md">
      <strong>STRUCTURE.md</strong>
      <span>How the repo is organized</span>
    </a>
  </div>
</section>

<section>
  <h2>Physical Systems the Swarm Serves</h2>
  <div class="grid">
    <a class="card" href="https://github.com/jesseray718/openroot/tree/main/aerocement">
      <strong>aerocement / H-003</strong>
      <span>Volumetric blackbody concrete + Thermal Loop (12.91 kWh/m² nightly target)</span>
    </a>
    <a class="card" href="https://github.com/jesseray718/openroot/tree/main/black-locust-rmh">
      <strong>black-locust-rmh</strong>
      <span>Rocket mass heater + permaculture spoke</span>
    </a>
    <a class="card" href="https://github.com/jesseray718/openroot/tree/main/une">
      <strong>une/</strong>
      <span>Joule-native rules + structure enforcer</span>
    </a>
    <a class="card" href="https://github.com/jesseray718/openroot/tree/main/ledger">
      <strong>ledger/</strong>
      <span>Thermodynamic + PoWr ledger (measured joules only)</span>
    </a>
  </div>
</section>

<section>
  <h2>Publications</h2>
  <div class="grid">
    <a class="card" href="https://doi.org/10.5281/zenodo.21225683">
      <strong>Zenodo DOI</strong>
      <span>Thermal system specs (WBTE-01, CTBS-01, AE-GFRC-01)</span>
    </a>
    <a class="card" href="https://github.com/jesseray718/openroot/blob/main/genesis.sh">
      <strong>Genesis Archive</strong>
      <span>Broadcast via IPFS + Zenodo + Solana + Bitcoin anchor</span>
    </a>
  </div>
</section>

<footer>
  <p>Open hardware CC-BY-SA 4.0 · Software GPL-3.0 · No patents</p>
  <p style="margin-top:.4rem">
    <a href="https://github.com/jesseray718/openroot">GitHub</a> ·
    <a href="https://doi.org/10.5281/zenodo.21225683">Zenodo</a> ·
    <a href="https://github.com/jesseray718">Profile</a> ·
    jrm8908@proton.me
  </p>
</footer>
</body>
</html>
"""

with open("index.html", "w") as f:
    f.write(landing_html)

say("banked", "Landing page upgraded: index.html (updated status, Zenodo, publications)")

# ── STAGE 4: Verify + Commit ───────────────────────────────────────
modified = ["README.md", "index.html"]
if os.path.exists("site/index.html"):
    modified.append("site/index.html")

for f in modified:
    assert os.path.exists(f), f"[held] {f} missing after write"
    size = os.path.getsize(f)
    assert size > 1000, f"[held] {f} too small ({size}B) — write failed"
    say("banked", f"verified {f}: {size:,} bytes")

def commit(msg):
    if CONFIRM:
        sh(["git", "add", "-f", *modified])
        stat = sh("git diff --cached --stat").stdout.strip()
        sh(["git", "commit", "-m", msg])
        sh(["git", "push", "origin", "main"])
        head = sh("git rev-parse --short HEAD").stdout.strip()
        say("banked", f"pushed {head}: {msg}")
    else:
        say("held", f"DRY would commit+push — {msg} ({len(modified)} files)")

commit("docs: restore README badges + hardware overview, upgrade profile & landing page")

print("[exit=0]")
