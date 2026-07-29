# AX-035 — The Business Credit Sequence

**Domain:** Credit & Business (CB)
**Type:** Axiom
**Status:** Active

## Statement

Business credit cannot be shortcut. It requires: (1) EIN, (2) DUNS number, (3) business bank account, (4) initial tradelines reporting, (5) time. Steps cannot be reordered or skipped. Each gate is a prerequisite for the next.

## Derivation

Business credit bureaus require a DUNS number to create a file. DUNS requires a legal entity (EIN). Tradelines require a business bank account for payment verification. PAYDEX scoring requires tradelines reporting for 30+ days. The dependency chain is strictly sequential — no step can be bypassed.

## Cross-References

- AX-CB-004 (Dual Profile Separation)
- PO-CB-003 (PAYDEX Acceleration Window)
- PO-CB-013 (Compound Timeline)

## Application

Execute business credit steps in order. File EIN → obtain DUNS → open business bank → apply for secured business card → add Net-30 vendors → wait for PAYDEX. Do not attempt to skip ahead.
