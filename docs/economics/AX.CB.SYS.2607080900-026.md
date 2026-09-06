# AX-026 — The Utilization Threshold

**Domain:** Credit & Business (CB)
**Type:** Axiom
**Status:** Active

## Statement

Credit utilization below 10% is functionally indistinguishable from 1% in scoring benefit. Above 30% begins penalization. Utilization has no memory across cycles — only the statement-close balance matters. A temporary spike is erased the following cycle by reduction.

## Derivation

FICO scoring models weight utilization at 30% of total score. The scoring algorithm snapshots utilization at statement close date. Historical utilization is not retained between cycles. Therefore, utilization is a tactical variable, not a strategic one — it can be optimized at any point without historical penalty.

## Cross-References

- AX-CB-002 (Utilization Threshold) — self
- AX-CB-014 (Utilization Reset Postulate)
- PO-CB-008 (Utilization Floor Effect)
- PO-CB-011 (Imperfect Utilization Superiority)

## Application

Maintain under 10% utilization during normal operation. If forced into high utilization, optimize the cycle before any score-dependent action (loan application, rental application).
