# AX-023 & PO-018 — Business v0.4 Review (businessphi)

Source: businessphi.md. Status: code exists [in-progress]; two functions broken or misleading [tested]; crossover concept is the keeper.

## Axiom

AX-023: Raw financials are prior to composites. Revenue, expenses, MRR, and burn are reported as measured before any score is computed, and no composite may substitute for them. A resonance number never overrides a dollar number.

## Postulate

PO-018: Crossover — recurring verified revenue exceeding monthly burn — is the operational test of a self-sustaining node. Composites are commentary; crossover is falsifiable, dated, and binary. [in-progress; formula bug fixed below]

## Audit findings [tested by execution, 2026-07-04]

1. biz_phi_alignment treats revenue/cost = φ as optimal. A venture at 5× revenue/cost scores 0.0 — worse than one at 0.5× (0.309). This tells a profitable node to become less efficient, contradicting AX-017/AX-021. Replaced with monotone ratio/(ratio+φ) or simply reporting the raw ratio per AX-023.
2. biz_coop_resonance compounds φ^months where months = len(revenue_log). Fifty logged payments → φ^50 → resonance pegged at 1.0 forever regardless of performance. Metric is meaningless as written; removed until keyed to actual elapsed months and verified cooperation.
3. biz_register_finetune crashes (AttributeError: list.get) whenever lineage is non-empty — which is always, since seeds pre-populate it. Also built_upon is a string in one branch, list in the other. Fixed below.
4. Schema mismatch with Kingdom Engine: this file writes "hours" and "epoch" (string); compound_reward reads "human_input_hours" and "epochs" (int). Business contributions silently feed the compound formula as defaults — cross-engine data degrades without error. Unified on the Kingdom schema.
5. Crossover math bug: monthly burn computed as total_expenses / len(revenue_log) — divides by number of revenue EVENTS, not months elapsed. A node logging weekly payments looks 4× cheaper to run. Fixed: expenses / elapsed months since first entry.
6. biz_symmetry uses min/max fee only. Standard underwriting measures client concentration as top-client share of revenue (flag above ~25%). Replaced.

## What survives review

- The crossover check is the best idea in the file: a dated, binary, falsifiable self-sufficiency test. It is the business-layer twin of the 12×12" panel — proof over projection.
- The permaculture audit that credits $0 recovered hardware is Produce No Waste made auditable. Keep.
- Fine-tunes as lineage entries = Catch & Store Energy: trained capability persists at zero marginal labor. Keep, with the crash fixed.
- Prior art: MRR/burn/crossover are standard SaaS metrics — using them raw (AX-023) reads as competence; wrapping them in φ reads as numerology. Fibonacci retracement / φ-based pricing in markets has no empirical support — same Markowsky/Livio caution as doc 13. Permaculture-in-economics has serious neighbors worth citing: Raworth's Doughnut Economics (2017), Fullerton's Regenerative Capitalism (2015).

## Permaculture mapping

- Obtain a Yield — crossover is the yield test, dated and binary
- Catch & Store Energy — fine-tuned models and recovered hardware as stored capacity
- Use & Value Renewable Resources — $0 recovered-hardware pipeline, multi-source
- Apply Self-Regulation & Accept Feedback — concentration check guards against single-client dependence

## Evaluation rule verdict

Fixes are line-level; benefit is that the one grant-visible financial tool stops recommending inefficiency and stops crashing. good/input very high. ACCEPT. Keeping φ-optimal alignment: REJECT (benefit 0, credibility cost high).

Status: ledger CLI [in-progress]; crossover [in-progress, bug fixed]; phi_alignment + coop_resonance as shipped [rejected]; concentration metric [concept].
