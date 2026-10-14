## Value Audit Appendix (post-repair)

Finding: 3 records (entry_id `h003_20260717_weekly`, idx 3/5/7 of repaired chain) carry
`7n_kwh=71084.44` = string-concatenation of week digit '7' + '1084.44' (7*154.92=1084.44).
Their `energy_joules` (255.9 GJ each) derives from the corrupted value; `acre_minted` is correct.
These records also duplicate `weekly_001/_002/_003` content. 756 of 780 GJ in the as-repaired
chain is phantom energy.

Action: quarantined to `context_bridge/quarantine/acre-corrupt-weekly-records.jsonl`.
Canonical v2 (`acre/ledger_v2.jsonl`): 6 records, self-verifying recipe
(hash = sha256 of sorted-compact record minus hash field). `ledger.jsonl` (9 records)
retained as historical as-repaired record, uncertified for energy totals.
