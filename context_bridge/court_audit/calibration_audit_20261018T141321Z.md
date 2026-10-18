# Court v6 Calibration Audit

**Generated:** 20261018T141321Z
**Auditor:** Z.ai (assistant) for Jesse McMillen / OpenRoot
**Status:** PENDING — needs human review of model reasoning

## The substantive question

Is the 0% pass rate earned (real evidence gaps) or miscalibrated (aggressive prosecutor + weak defense)?

## Decision criteria

- FAIL verdicts citing missing chunks / unverified citations / schema violations -> court working
- FAIL verdicts citing vague concerns ('insufficient context,' 'could be stronger') -> miscalibrated
- HOLD verdicts that look pass-worthy but got downgraded by aggressive prosecution -> calibration issue

## What we already know

From prior inspection of the 3 FAIL samples:
- All three FAILs were log files (gh_audit_detached, reh1t_v2, reh1t_v2) with warns=0 and errs=0
- Two HOLDs were also low-signal logs (seed_master.log at 43 bytes, bridge_cycle at 278 bytes)

## Working hypothesis

The court is correctly identifying that raw log files are not structured evidence packages. The court is incorrectly classifying them as failures instead of refusals. The fix is upstream of the court: the docket should only receive items that have been compiled into evidence packages by the deterministic compiler.

## Recommendation (to be confirmed by human review of model reasoning)

The court is not broken. The intake is. The docket should reject raw log files and only accept items that have:
- A package_hash (compiled evidence package)
- Verified citations
- Schema conformance

## Next move (pending human confirmation)

1. Sample 2-3 FAIL verdicts and read the actual model reasoning (the defense and prosecution output)
2. If reasoning cites real gaps -> court is working, fix intake
3. If reasoning is vague -> court is miscalibrated, adjust prompts

This audit doc remains PENDING until human review confirms the model reasoning.
