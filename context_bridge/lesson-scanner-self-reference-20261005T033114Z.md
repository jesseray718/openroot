# Lesson: Scanner flagged its own probe list

## Occurrence
Purge aftermath audit reported 10 orphaned consumer references. All 10 were
purge_aftermath_audit_v1.sh referencing the DELETED_DB list it carries internally.

## Class
Self-reference false positive — scanner-scans-scanner.

## Remediation
Scanners must exclude their own path (and sibling probe artifacts) before
reporting hits. Audit instruments before builders, and audit the auditors.

## Outcome
DB-orphan hold DISMISSED — zero real consumers reference deleted data/*.db.
