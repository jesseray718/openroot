# GOVERNOR-01 — Bounded LLM Swarm Orchestration

**Status:** [in-progress] — GOVERNOR skeleton live (TASK-001 passed); routing/verification tiers below are [concept] until implemented
**Path:** `research/epistemology/GOVERNOR-01.md`
**Extends:** EPISTEMOLOGY-SWARM-01.md
**License:** CC-BY-SA-4.0 · **Copyright:** One Human Family
**Device target:** Samsung Galaxy A15, Termux, no root

## 0. What this is and is not

This system is a set of LLM API calls and local subprocesses orchestrated through a file-based queue on one phone. It is not nanobots, not autonomous agents, and not a verification system. Naming stays literal: overclaiming here is the false-authority failure mode identified in CONVERGENCE-ANALYSIS-01 (risk #6), and it is a direct credibility liability for academic outreach.

**Operating rule (candidate axiom, proposed for the AX series — Jesse to accept/reject):**

> Agreement among language models is correlated error, not evidence. Consensus is not a verification event. Disagreement among models is useful signal (flags for human review); agreement grants nothing.

The swarm's epistemic value is therefore inverted from the naive framing: it is a **divergence detector and draft forge**, never a truth source.

## 1. Objective function

good/input = (benefit × urgency × (1−slump)) / (cost × effort × verification_overhead)
The dominant optimization is in the denominator. Raw output volume is a vanity metric; unreviewed output accumulates verification debt. Fitness is measured against Stage 1 benchmark: first external verified action within 60 days.
Design law: autonomy per task class is proportional to verification cheapness.
Verifier type | Example | Autonomy granted
Deterministic | tests pass, JSON validates, links resolve | Auto-advance, may chain
Human judgment | doc drafts, protocols, issue text | Park for review; cannot spawn children
Physical | thermal claims, pours, bench tests | Exits swarm entirely → VERIFY-01
Backpressure cap: parked/ holds ≤ 10 unreviewed artifacts. When full, all generation halts.

## 2. Scored configurations
Config | benefit | urgency | slump | cost | effort | verif_ovh | score
A. Free-running autonomous swarm | 2 | 1 | 0.6 | 3 | 4 | 5 | 0.013
B. Gated forge (this spec) | 4 | 4 | 0.2 | 2 | 2 | 2 | 1.6
C. Divergence panel (advisory) | 3 | 3 | 0.5 | 2 | 2 | 3 | 0.38
Adopted: Config B, with C bounded inside it as one worker role.

## 3. Topology — hub-and-spoke over a file bus
No agent-to-agent chatter. Star topology only:
tasks.queue → ROUTER → [worker: single call] → VERIFIER
  deterministic pass → done/ (may enqueue child task)
  needs human judgment → parked/ (Jesse reviews; no children)
  fail ×3 → dead/ (with logs)

Message bus = filesystem. Directories under $HOME/.governor/:
queue/     pending task envelopes
work/      in-flight (atomic mv from queue/ claims the task)
parked/    awaiting human review (hard cap 10)
done/      T0-verified artifacts
dead/      failed ×3, logs attached
providers.json   per-provider health + rate-limit headers
budget.json      daily token/request spend

## 4. Worker roles and provider bindings
Role | Provider (primary → fallback) | Domain | Verifier | Autonomy
router | keyword rules → local Qwen2.5-1.5B | task classification | envelope schema check | auto
drafter | Groq 70B → Lumo | docs, protocols, issue bodies | human read | parked
critic | local Qwen (different family) | adversarial review vs. checklist | human read | parked
coder | Groq → local Qwen2.5-Coder-1.5B | scripts, fixes | tests actually run | auto iff tests pass
extractor | jq/awk/python-stdlib first; LLM only if unstructured | format conversion | round-trip validation | auto
divergence panel | ≥2 healthy providers | claim stress-test pre-publish | human reads report | advisory only
scribe | local | state.md deltas, session logs | human approves before commit | parked

## 5. Routing protocol
Task envelope:
{
  "id": "TASK-042",
  "class": "draft|critique|code|extract|diverge|scribe",
  "input": "path or inline text",
  "provider_pref": ["groq", "local"],
  "verifier": "deterministic|human|physical",
  "chain_depth": 0,
  "retries": 0,
  "created": "2026-07-07T00:00:00Z"
}

Routing rules:
1. Deterministic tool exists → use it. No LLM call.
2. JSON encoding via python stdlib, never jq -Rs.
3. Provider health gate — skip providers with failures in last hour.
4. Rate limits recorded from response headers, never assumed.
5. Chaining rule (anti-runaway): worker may enqueue child task only if output passed deterministic verifier. Human-parked outputs cannot spawn children.
6. Chain depth ≤ 3.

## 6. Verification tiers
Tier | Verifier | Grants status | Who/what
T0 | deterministic | [draft, verified:T0] | swarm, automatically
T1 | human (Jesse) | publish-approved | Jesse only
T2 | ≥2 independent humans | attested | external contributors
T3 | physical bench test | validated | physics
Swarm ceiling: T0. No combination of model calls promotes past T0.

## 7. Hard firewalls — non-negotiable
1. No publish path. Swarm never invokes publish-all, git push, Zenodo, IPFS, ACRE mint, or email.
2. Provenance in git history. Commits with swarm content carry Draft-Origin: governor/TASK-ID footer.
3. Backpressure cap: parked ≤ 10, then full stop.
4. Local inference only while charging or foregrounded.

## 8. Android/Termux reality
- No root ⇒ no reliable daemon. Burst mode only: governor drain empties queue when invoked.
- Free-tier rate limits bound throughput.
- Known broken: Cerebras/Mistral payload schema, clipboard interference.
- Bus factor = 1. Swarm is throughput multiplier, not redundancy.

## 9. KPIs
KPI | Target | Falsifies
Draft latency (enqueue → parked) | ≤ 48 h | forge usefulness
Human review minutes per accepted artifact | trending ↓ | net-negative overhead
Parked rejection rate | < 50% | drafter prompt quality
Unauthorized publish events | 0 | firewall integrity
Stage 1 benchmark | first external verified action ≤ 60 days | config-B thesis

## 10. Immediate integration — next 24 h
Task | Route | Verifier
Draft WBTE-01-TEST-PROTOCOL.md | drafter → critic → parked | T1
Draft aerocement/BUILD-001-test-tile.md | drafter → critic → parked | T1
Generate 3 good-first-issue bodies | drafter → parked | T1
Insert [THEORETICAL] headers on specs | script, no LLM | T0
Repo link check | script, no LLM | T0

## 11. Open items
- epi payload fix for Cerebras/Mistral — unblocks real divergence panels.
- Ed25519 for FEDERATION-01: ssh-keygen -Y sign/verify (OpenSSH in Termux).
- NOMOS schema: add attestations[] + attestation_threshold.

Self-scored numbers carry gameability caveat. This document describes orchestration, not verification. Nothing in it produces evidence about the physical world.
