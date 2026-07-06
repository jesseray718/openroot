# OPENROOT CONTEXT BRIDGE — SESSION HANDOFF 20260706 (REV-B)

## IDENTITY
Jesse Ray. Permaculture systems designer, appropriate technology inventor, polymath.
Device: Samsung Galaxy A15, Termux, Shizuku, no root.
GitHub: jesseray718 | Email: jrm8908@proton.me

## SESSION SUMMARY (2026-07-06)
Morning: full deployment sprint (8 artifacts published, DOI live, IPFS pinned).
Afternoon: CONTRIBUTING.md shipped. Claude deep convergence analysis completed — 87 sources, full system map, staged roadmap adopted. START-HERE.md + FUNDING.md created.

## PUBLISHED ARTIFACTS
| Artifact | Location | Status |
|----------|----------|--------|
| WBTE-01 (Wet-Bulb Thermal Engine) | research/thermal-systems/ | ✅ GitHub [THEORETICAL] |
| CTBS-01 (Cascading Thermal Battery) | research/thermal-systems/ | ✅ GitHub [THEORETICAL] |
| AE-GFRC-01 (Aerated GFRC w/ zirconium) | research/thermal-systems/ | ✅ GitHub [THEORETICAL] |
| Thermal block diagram (PNG) | research/thermal-systems/ | ✅ GitHub |
| Profile Atlas README | jesseray718/jesseray718 repo | ✅ GitHub |
| Epistemology swarm spec | research/epistemology/ | ✅ GitHub |
| CONTRIBUTING.md | repo root | ✅ GitHub |
| START-HERE.md | repo root | ✅ (this session) |
| FUNDING.md | repo root | ✅ (this session) |
| Zenodo DOI 10.5281/zenodo.21225683 | zenodo.org/records/21225683 | ✅ Published |
| IPFS CID QmVJxfQmFoTVDp1GRui8bEKJ7x7J154h8RX3EmxQBcCrBt | ipfs.io | ✅ Pinned |
| Convergence Analysis (Claude) | research/strategy/ | ✅ Saved as reference doc |

## CLAUDE CONVERGENCE ANALYSIS — KEY DECISIONS ADOPTED
1. Force-multiplier moves > linear subsystem tuning until first external contributor fires
2. Bus factor = 1 is the dominant risk — every action evaluated against reducing it
3. Thermal claims must carry explicit [THEORETICAL]/[concept] headers — radical integrity
4. G-score self-scoring is a genuine exploit — VERIFY-01 spec needed before ACRE has value
5. Zenodo de-ranking is real — remedy: log in via ORCiD/GitHub, get uploads into communities
6. Academic co-authorship is the durable credibility route, not Zenodo search
7. Named academic targets identified (see STAGE 2 below)

## ACTIVE ROADMAP (ADOPTED FROM CLAUDE ANALYSIS)

### STAGE 1 — Make the engine fireable by a stranger (next 2-4 weeks)
- [x] CONTRIBUTING.md — rules of engagement
- [x] START-HERE.md — 5-minute onramp
- [x] FUNDING.md — funder archetype entry
- [ ] Enable GitHub Discussions (Introductions + Show-your-build categories)
- [ ] Pin START-HERE.md to repo
- [ ] Tag ≥25% of issues "good first issue"; create 3 genuine ones (doc, code, build)
- [ ] Add explicit [THEORETICAL]/[concept] headers to WBTE-01, CTBS-01, AE-GFRC-01
- [ ] Write aerocement/BUILD-001-test-tile.md — stranger-reproducible builder on-ramp
- **Benchmark:** first external verified action within 60 days. If not achieved → pivot to permies.com, Appropedia, OSE forum, subreddits.

### STAGE 2 — Make verification and credit trustworthy (weeks 4-10)
- [ ] Write research/governance/VERIFY-01.md (iNaturalist model: ≥2 independent confirmations of capture-time-hashed evidence)
- [ ] Extend NOMOS schema with attestations[] and attestation_threshold
- [ ] Fill PROF-COLLAB-01.md with named targets and send 3-5 emails
- [ ] Write research/thermal-systems/WBTE-01-TEST-PROTOCOL.md (falsifiable)
- [ ] Add FUNDING.md + transparent funds ledger ← DONE, needs activation
- [ ] Zenodo: log in via ORCiD/GitHub, apply for community membership to get safelisted
- **Academic targets (prioritized):**
  1. Prof. Xudong Zhao — University of Hull, UK — dew-point evaporative cooling
  2. Prof. Osman Gencel — Bartın University, Turkey — GFRC + foam + PCM
  3. Dr. Qianjun Mao — University of South China (confirm dept) — cascaded PCM tanks
  4. Prof. Yong Shuai — Harbin Institute of Technology — cascaded packed-bed thermal storage
  5. Dr. Eric Hu — University of Adelaide — indirect evaporative cooling
  6. HardwareX (Joshua Pearce, editor-in-chief) — fallback publication path
- **Benchmark:** one academic reply engaging on substance + one claim reaching "attested" via independent confirmation. If PIs don't bite in 90 days → pivot to grad students + HardwareX.

### STAGE 3 — Reduce bus factor structurally (months 3-6)
- [ ] Recruit one co-maintainer from Stage 1/2 contributors
- [ ] Implement asymmetric signing (Ed25519) — research/governance/FEDERATION-01.md
- [ ] Give co-maintainer triage/attestation/merge access
- **Benchmark:** a second person with merge/attestation rights.

## IMPORTANT CORRECTIONS / WARNINGS
- All thermal performance numbers are THEORETICAL — disclaimers must be visible at TOP of each doc
- G-score self-scoring is an exploit — fix before ACRE has value
- Epistemology swarm (LLM consensus) is NOT physical-world verification — label as [concept] advisory only
- Zenodo de-ranking is active — DOIs resolve but search discovery is compromised until safelisted
- Complexity is outrunning adoption — every abstraction not on a contributor's critical path is currently a COST
- aiq CLI breaks on long prompts (>100 chars) — jq -Rs issue. Workaround: Lumo for long content, Groq for short.
- epi swarm: only Groq confirmed working; Cerebras/Mistral throw JSON errors (payload schema mismatch)

## KEY FILE PATHS
- Specs: ~/projects/openroot/research/thermal-systems/{WBTE-01,CTBS-01,AE-GFRC-01}.md
- Epistemology: ~/projects/openroot/research/epistemology/EPISTEMOLOGY-SWARM-01.md
- Outreach: ~/projects/openroot/research/outreach/{PROF-COLLAB-01,CALL-TO-BUILDERS-01}.md
- Strategy ref: ~/projects/openroot/research/strategy/ (Claude convergence analysis)
- Profile README: ~/projects/jesseray718/README.md
- Publisher: ~/bin/publish-all
- Swarm CLI: ~/bin/epi
- Zenodo token: ~/.zenodo-token
- AIQ config: ~/.config/aiq/config.sh

## EXISTING PUBLISHED DOIS
- 10.5281/zenodo.21210931 (earlier thermal cascade dataset)
- 10.5281/zenodo.21225683 (thermal systems release)

## REPO STATS
- 90+ markdown files (added CONTRIBUTING.md, START-HERE.md, FUNDING.md)
- Main branch, merge strategy, push origin main

## PHILOSOPHY
All work follows agape-une principles: engineer as an act of unconditional integration.
Copyright: One Human Family. License: CC-BY-SA-4.0 (docs) / GPL-3.0 (code).
Permaculture ethics: obtain a yield, integrate rather than segregate, use edges and value the marginal.
Force-multiplier > linear. Bus factor reduction is the dominant priority.
