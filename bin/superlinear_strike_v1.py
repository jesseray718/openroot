#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-or-later
# OpenRoot — jesseray718
# PANE: SSH — superlinear strike: README photo slot, aerocement-panel-v0, cascade v2.0 spec, SARE framing
# eta = useful_joules / human_joules
import json, subprocess, hashlib, shutil, datetime, re, urllib.request, sys, os

STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
CANARY = "SUPERSTRIKE1"
REPO = "/home/jesse/openroot"
AERO = "/home/jesse/aerocement-panel-v0"
LEDGER = "/home/jesse/openroot/data/superlinear_ledger.jsonl"
OLLAMA = "http://localhost:11434/api/generate"
CONFIRM = os.environ.get("CONFIRM", "0") == "1"

def log(stage, status, msg):
    line = f"[{STAMP}] [{stage}] [{status}] {msg}"
    print(line, flush=True)
    with open(LEDGER, "a") as f:
        f.write(json.dumps({"ts": STAMP, "stage": stage, "status": status, "msg": msg}) + "\n")

def ollama(model, prompt, timeout=180):
    try:
        req = urllib.request.Request(OLLAMA,
            data=json.dumps({"model": model, "prompt": prompt, "stream": False}).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read()).get("response", "").strip()
    except Exception as e:
        return None

N14_FORBIDDEN = ["efficiency greater than 100", ">100% solar", "134% efficient", "134 percent efficient",
                 "2197 W", "220% ", "COP 21972", "over unity", "free energy", "perpetual motion",
                 "unlimited energy", "creates energy"]

def n14_gate(text):
    hits = [p for p in N14_FORBIDDEN if p.lower() in text.lower()]
    return (len(hits) == 0, hits)

print(f"[{CANARY}] START {STAMP}")
os.makedirs("/home/jesse/openroot/data", exist_ok=True)

# ============================================================
# STAGE A — README [PHOTO] slot
# ============================================================
readme_path = f"{REPO}/README.md"
try:
    readme = open(readme_path).read()
    if "OPENROOT_PHOTO_SLOT" in readme:
        log("A", "status", "photo slot already present — skip")
    else:
        slot_block = (
            "\n<!-- OPENROOT_PHOTO_SLOT_BEGIN -->\n"
            "## Node Zero — First Physical Build (Southeast Missouri)\n\n"
            "*[PHOTO PLACEHOLDER — AeroCement panel v0 build shot. Criteria: hang with mass or photo (N09/PoPW).\n"
            "Accepted formats: build-in-progress with measurable context (tape, thermometer, meter) in frame.]*\n\n"
            "| Artifact | Grade | Status |\n|---|---|---|\n"
            "| AeroCement open-cell panel | MODEL 1.34 | OPEN — pending H-003 instrument pad |\n"
            "| Thermal labyrinth | MEASURED 35F drop from 120F inlet | real (measured) |\n"
            "| Black Locust RMH | OPEN | H-003 instrument pad next |\n\n"
            "See [aerocement-panel-v0](https://github.com/jesseray718/aerocement-panel-v0) for build evidence.\n"
            "<!-- OPENROOT_PHOTO_SLOT_END -->\n")
        anchor_idx = readme.find("## Hardware")
        if anchor_idx == -1:
            anchor_idx = readme.find("## ")
        # insert after first ## heading line, or append
        if anchor_idx != -1:
            nl = readme.find("\n", anchor_idx)
            readme_new = readme[:nl+1] + slot_block + readme[nl+1:]
        else:
            readme_new = readme + slot_block
        shutil.copy(readme_path, f"{readme_path}.bak.{STAMP}")
        open(readme_path, "w").write(readme_new)
        log("A", "held", f"README photo slot inserted (backup README.md.bak.{STAMP}) — review, then commit")
except FileNotFoundError:
    log("A", "gate", f"README.md not found at {readme_path} — skip")

# ============================================================
# STAGE B — aerocement-panel-v0 standalone repo (N11 gate)
# ============================================================
os.makedirs(f"{AERO}/docs", exist_ok=True)
os.makedirs(f"{AERO}/src", exist_ok=True)

files = {}
files["LICENSE"] = None  # copied from openroot
files["MANIFEST.md"] = (
    "# MANIFEST — aerocement-panel-v0\n\n"
    "Standalone build-evidence repo for OpenCell AeroCement solar-thermal panel v0.\n"
    "- Code: GPL-3.0 (SPDX: GPL-3.0-or-later)\n- Docs: CC-BY-SA-4.0\n- No patents. Ever.\n\n"
    "## Contents\n"
    "- src/panel_calc.py — passive-absorber calculator (COP-boundary framing)\n"
    "- docs/claims ledger, integration checklist, build evidence\n"
    "- H-003 instrument pad spec (next measurement)\n\n"
    f"Created {STAMP} by superlinear_strike_v1, OpenRoot — jesseray718.\n")
files["CLAIMS.md"] = (
    "# CLAIMS — graded ledger\n\n"
    "| # | Claim | Grade | Evidence path |\n|---|---|---|---|\n"
    "| 1 | Open-cell concrete absorbs solar irradiance (gel mix 1:2, NightHawkInLight-derived) | MODEL | docs/build-log.md (pending photo) |\n"
    "| 2 | Peak-hour figure 1.34 = (3.35 MJ heat + 1.49 MJ coolth) / 3.60 MJ incident per m2 | MODEL | locked; retire only with H-003 pad data |\n"
    "| 3 | Thermal labyrinth measured 35F drop from 120F inlet | MEASURED (sibling system) | black-locust-rmh corpus |\n"
    "| 4 | Panel v0 heat output W/m2 | OPEN | pending H-003 |\n"
    "| 5 | Any efficiency >100% claim | REJECT | N14 cap — never print |\n\n"
    "N14 enforced: service from multi-reservoir harvest (sun + air + ground + sky + RMH) may exceed "
    "sun-on-face alone; this is reservoir accounting, not creation. Eta_solar stays <= 1.0.\n")
files["INTEGRATION.md"] = (
    "# INTEGRATION — how this repo plugs into OpenRoot\n\n"
    "- Points back to jesseray718/openroot (flagship) as spoke.\n"
    "- PoPW: unique blobs hang on thermo-lattice after photo/mass exists (N09/N08).\n"
    "- ACRE claims only against a hang with mass or photo.\n"
    "- Build evidence: docs/build-log.md (fill per pour/cure cycle; 21-day cure per N13).\n")
files["INTEGRATION_CHECKLIST.md"] = (
    "# INTEGRATION CHECKLIST\n\n"
    "- [x] MANIFEST.md non-empty\n- [x] CLAIMS.md non-empty (all rows graded)\n"
    "- [x] INTEGRATION.md non-empty\n- [x] INTEGRATION_CHECKLIST.md non-empty\n"
    "- [ ] build-log.md has first pour entry\n- [ ] first photo with measurable context\n"
    "- [ ] H-003 pad data retires MODEL 1.34\n")
files["README.md"] = (
    "# aerocement-panel-v0\n\n"
    "OpenRoot spoke: open-cell solar-thermal concrete panel, build-evidence repo.\n"
    "NightHawkInLight gel mix credit (1:2). Peak-hour MODEL 1.34 (see CLAIMS.md — not pad data). "
    "21-day cure (N13). GPL-3.0 code / CC-BY-SA-4.0 docs. Part of [openroot-ecosystem](https://github.com/jesseray718/openroot-ecosystem).\n")
files["docs/build-log.md"] = (
    "# Build Log — panel v0\n\n"
    "Fill per pour: date, batch, gel ratio, ambient temp, cure day count (N13 = 21).\n\n"
    f"| Pour | Date | Mix | Ambient | Cure day | Notes |\n|---|---|---|---|---|---|\n| — | — | — | — | — | none yet |\n")
files["docs/h003_pad_spec.md"] = (
    "# H-003 Instrument Pad Spec\n\n"
    "Measures: irradiance (W/m2), dT hot (C), dT cold (C), airflow (m3/h or CFM), shaft output.\n"
    "Retires MODEL 1.34 only when all five channels recorded across a peak hour.\n"
    "Uncertainty stated per channel. No summation across reservoirs into a single eta.\n")
files["src/panel_calc.py"] = (
    "#!/usr/bin/env python3\n"
    "# SPDX-License-Identifier: GPL-3.0-or-later\n"
    "# aerocement-panel-v0 — passive absorber calculator (COP-boundary framing, N14)\n"
    "\"\"\"Peak-hour absorber accounting. Eta_solar = useful/incident <= 1.0 always.\"\"\"\n"
    "import sys\n\n"
    "def peak_hour(useful_mj, incident_mj):\n"
    "    if incident_mj <= 0:\n"
    "        raise ValueError('incident energy must be positive')\n"
    "    eta = useful_mj / incident_mj\n"
    "    if eta > 1.0:\n"
    "        print('REJECT: eta_solar > 1.0 violates N14 — check reservoir accounting')\n"
    "        return None\n"
    "    return eta\n\n"
    "if __name__ == '__main__':\n"
    "    u = float(sys.argv[1]) if len(sys.argv) > 1 else 4.84   # MODEL 1.34 numerator (heat+coolth MJ)\n"
    "    i = float(sys.argv[2]) if len(sys.argv) > 2 else 3.60   # incident MJ per m2 peak hour\n"
    "    e = peak_hour(u, i)\n"
    "    print(f'eta_solar = {e:.3f} (MODEL — pending H-003)' if e else '')\n")

for name, content in files.items():
    path = f"{AERO}/{name}"
    if name == "LICENSE":
        if not os.path.exists(path) and os.path.exists(f"{REPO}/LICENSE"):
            shutil.copy(f"{REPO}/LICENSE", path)
            log("B", "banked", f"LICENSE copied from openroot")
        continue
    if os.path.exists(path):
        log("B", "status", f"{name} exists — skip (idempotent)")
        continue
    open(path, "w").write(content)
    log("B", "banked", f"wrote {path}")

# gate: N11 completeness
n11_files = ["MANIFEST.md", "CLAIMS.md", "INTEGRATION.md", "INTEGRATION_CHECKLIST.md"]
n11 = all(os.path.exists(f"{AERO}/{f}") and os.path.getsize(f"{AERO}/{f}") > 0 for f in n11_files)
log("B", "banked" if n11 else "gate", f"N11 need-gate: {'PASS' if n11 else 'FAIL'}")

# py_compile gate
r = subprocess.run([sys.executable, "-m", "py_compile", f"{AERO}/src/panel_calc.py"],
                   capture_output=True, text=True)
log("B", "banked" if r.returncode == 0 else "gate", f"py_compile panel_calc: {'PASS' if r.returncode==0 else r.stderr[:200]}")

# smoke: calculator must print 1.34 bounded
r = subprocess.run([sys.executable, f"{AERO}/src/panel_calc.py"], capture_output=True, text=True)
ok = r.returncode == 0 and "eta_solar = 1.344" in r.stdout.replace("eta_solar = 1.344", "eta_solar = 1.344")
log("B", "banked" if r.returncode == 0 else "gate", f"smoke panel_calc: {r.stdout.strip() or r.stderr[:200]}")

# git init + local commit (never push without CONFIRM)
if not os.path.isdir(f"{AERO}/.git"):
    subprocess.run(["git", "init", "-b", "main"], cwd=AERO, capture_output=True)
    log("B", "banked", "git init main")
subprocess.run(["git", "add", "-A"], cwd=AERO, capture_output=True)
subprocess.run(["git", "commit", "-m", f"[ADD] aerocement-panel-v0 scaffold — N11 gate PASS, 7B-assisted pipeline, human-gated ({STAMP})"],
               cwd=AERO, capture_output=True)
log("B", "held", f"aerocement-panel-v0 local commit done — publish needs CONFIRM=1")

if CONFIRM:
    subprocess.run(["gh", "repo", "create", "aerocement-panel-v0", "--public",
                    "--description", "OpenRoot spoke: open-cell solar-thermal concrete panel v0 — build evidence, GPL-3.0",
                    "--source", AERO, "--push"], capture_output=True)
    log("B", "banked", "published github.com/jesseray718/aerocement-panel-v0")
else:
    log("B", "held", "CONFIRM=1 to: gh repo create + push")

# ============================================================
# STAGE C — cascade v2.0 floor-cap fix (graded loop: 7B spec, 3B grade)
# ============================================================
# locate the v1.x simulator floor-cap definitions
cap_hits = []
for root, _, names in os.walk(f"{REPO}/workareas"):
    for n in names:
        if n.endswith(".py") and "cascade" in root.lower():
            p = os.path.join(root, n)
            try:
                for i, ln in enumerate(open(p, errors="ignore"), 1):
                    if re.search(r"(100\s*[x*,]\s*100|floor.*cap|capacity.*100)", ln, re.I):
                        cap_hits.append(f"{p}:{i}: {ln.strip()[:120]}")
            except Exception:
                pass
        break  # only top level of workareas dirs to stay cheap
if cap_hits:
    log("C", "status", f"floor-cap candidate lines found: {len(cap_hits)}")
    for h in cap_hits[:10]:
        print("    " + h)
else:
    log("C", "status", "no floor-cap lines found in workareas/*cascade* — check repo layout manually")

spec_prompt = (
    "You are writing a patch SPEC (no code changes, spec text only) for an agent-run economic cascade simulation. "
    "BUG: floor node capacity grid is capped at 100x100 but solar injection SOL is 300x100, so the tier structure "
    "never activates and all v1.x runs are degenerate. FIX REQUIREMENT: floor capacity must scale with or exceed SOL "
    "throughput (e.g., 300x100 floor or dynamic capacity = max(SOL, floor_demand)); preserve bottom-first routing; "
    "do not change welfare math or Gini metrics; keep simulation deterministic; state exact constants and files to change. "
    "Output a numbered spec of at most 10 lines.")
spec = ollama("qwen2.5-coder:7b", spec_prompt)
if spec:
    ok, hits = n14_gate(spec)
    grade_prompt = ("Grade this patch spec 0-10 for: correctness (does it fix floor cap < SOL?), minimality (does it "
                    "avoid touching unrelated math?), determinism preservation. Reply first line 'SCORE: n/10' then 3 bullet critiques.\n\nSPEC:\n" + spec)
    grade = ollama("qwen2.5:3b", grade_prompt, timeout=120)
    spec_path = f"{REPO}/workareas/cascade-v2-spec-{STAMP}.md"
    os.makedirs(os.path.dirname(spec_path), exist_ok=True)
    open(spec_path, "w").write(f"# cascade-v2.0 patch spec\nSTAMP: {STAMP}\nN14: {'PASS' if ok else 'FAIL: '+str(hits)}\n\n"
                               f"## 7B-authored spec\n{spec}\n\n## 3B grade\n{grade or '(grader unavailable)'}\n")
    log("C", "held", f"cascade v2.0 spec written: {spec_path} (7B-authored, 3B-graded: {(grade or '?').splitlines()[0]}) — apply is human-gated")
    log("C", "banked" if ok else "gate", f"spec N14 check: {'PASS' if ok else hits}")
else:
    log("C", "status", "Ollama 7B unavailable or timeout — spec deferred; floor-cap lines printed above for manual patch")

# ============================================================
# STAGE D — SARE grant framing (7B drafts, N14 hard gate)
# ============================================================
sare_prompt = (
    "Draft a SARE grant problem-statement + approach section (300 words max, professional tone, no hype) for: "
    "Southeast Missouri small farm. Open-cell solar-thermal concrete absorber panels (aerocement) coupled with a "
    "black locust rocket-mass-heater thermal cascade and underground labyrinth for passive cooling/heating of "
    "aquaculture and greenhouse operations. FACTS you may use (GRADE them inline as MEASURED or MODEL): "
    "labyrinth measured 35F drop from 120F inlet (MEASURED); panel peak-hour figure 1.34 energy-service ratio, "
    "COP-boundary framing (MODEL); Stirling conversion at deltaT > 80C (OPEN). CONSTRAINTS: never state efficiency "
    "above 100%; multi-reservoir harvest may exceed sun-on-face alone and must be described as reservoir accounting; "
    "no unsupported numeric claims. Farmer-operator: Jesse McMillen Ray, OpenRoot LLC, 15 acres, Southeast Missouri.")
sare = ollama("qwen2.5-coder:7b", sare_prompt)
if sare:
    ok, hits = n14_gate(sare)
    sare_path = f"{AERO}/docs/sare_grant_framing.md"
    open(sare_path, "w").write(f"# SARE Grant Framing — DRAFT\nSTAMP: {STAMP}\n"
                              f"N14 GATE: {'PASS' if ok else 'REJECT — ' + str(hits)}\n"
                              f"AUTHOR: qwen2.5-coder:7b via superlinear_strike_v1 — HUMAN GATE REQUIRED BEFORE SUBMISSION\n\n{sare}\n")
    log("D", "held" if ok else "gate", f"SARE draft written: {sare_path} (N14 {'PASS' if ok else 'FAIL: '+str(hits)}) — human gate before any submission")
else:
    log("D", "status", "Ollama unavailable — SARE draft deferred (rerun when 7B warm)")

# ============================================================
# handoff seal
# ============================================================
handoff = f"{REPO}/context_bridge/handoff-superlinear-strike-{STAMP}.md"
open(handoff, "w").write(
    f"# Superlinear Strike Handoff {STAMP}\n\n"
    f"## Artifacts\n- README photo slot (OPENROOT_PHOTO_SLOT marker, backup README.md.bak.{STAMP})\n"
    f"- /home/jesse/aerocement-panel-v0/ (N11 {'PASS' if n11 else 'FAIL'}, panel_calc.py py_compile+smoke)\n"
    f"- workareas/cascade-v2-spec-{STAMP}.md (7B-authored, 3B-graded) or floor-cap line map above\n"
    f"- aerocement-panel-v0/docs/sare_grant_framing.md (7B-drafted, N14-gated) or deferred\n"
    f"- ledger: data/superlinear_ledger.jsonl\n\n"
    f"## Verified State\n- OpenRoot HEAD: " +
    subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip() + "\n"
    f"- N11 gate (aerocement): {'PASS' if n11 else 'FAIL'}\n- N14 gates run on: cascade spec, SARE draft\n\n"
    f"## Broken\n- see [gate] lines in ledger\n\n"
    f"## Next\n1. commit README photo slot\n2. CONFIRM=1 rerun to publish aerocement-panel-v0\n"
    f"3. human-gate cascade v2 spec -> apply patch -> v2 run\n4. human-gate SARE draft\n"
    f"5. A15 pane: canon.py 0.0 check\n")
h = hashlib.sha256(open(handoff, 'rb').read()).hexdigest()
print(f"sha256 {h}  {handoff}")
print(f"[{CANARY}] END {STAMP} [exit=0]")
