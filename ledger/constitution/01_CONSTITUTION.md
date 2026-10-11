# OPENROOT CONSTITUTION
Tiers: Bill of Rights (immutable) > Constitution (amendments recorded) > Statutes (add/delete).
Amendments append to amendments.jsonl as a sha256 chain — no rewrite, no deletion.
Statutes register in statutes.jsonl (append-only, status open/removed).
All mutations pass bin/constitution_gate_v1.py verify first; RED pin halts everything.
