# OPENROOT RIDE-ALONG STATE
<!-- Single source of truth for every AI instance. Read FIRST. Update after acting. -->
<!-- snapshot regenerates CURRENT STATE; event log is append-only history -->

## MISSION (immutable)
Superlinear permaculture: maximize eta = J_useful / J_human. Cache every proven pathway.
A pathway proven once (SHA256-sealed in the Newton chain) is NEVER recomputed.
Compound modular Turing tidbits upward: input -> hash -> sealed pathway -> bigger modules.
Route everything: hash-first, embed-second, model-last. Proof (CLIDdy/ReGen style):
if a theorem stands, the whole system inherits it as flag and skips recompute.
The endgame: an interconnected organism where the least among us is lifted by the
accumulated proven pathways of everything that came before.

## CURRENT STATE (regenerated 2026-10-11T14:04:11.869882+00:00)
- Git: main @ 7049831 (45 dirty entries)
- Pathway ledger: 10 rows, 2 embeddings, latest seal 6da4fc773592 (2026-10-11T13:51:43)
- Latest reports: /home/jesse/openroot/reports/audit-bin-20261011T135143Z.md
/home/jesse/openroot/reports/audit-openroot-20261011T134748Z.md
/home/jesse/openroot/reports/audit-openroot-20261011T132554Z.md

## ACTIVE QUEUE (delete when done, never leave stale)
- [ ] SOLUTION 1 — commit-state hashing: input basis = git rev-parse HEAD (+ dirty bit), NOT working-tree diff. Daemon ledger churn stops invalidating pathways. Audit validates what will be PUSHED.
- [ ] SOLUTION 2 — parent-child lineage: ALTER pathways table ADD COLUMN parents TEXT (JSON list of row_shas). A->B->C composes into theorem T instead of 3 isolated seals. Bookshelf becomes spine.
- [ ] SOLUTION 3 — thresholded semantic routing: wire cosine similarity into lookup. Semantic hit needs confidence score (start 0.75, calibrate). Hash = binary truth, embed = scored neighbor, model = last resort.
- [ ] phi4-router front door: query -> hash lookup -> embed neighbor (scored) -> model call -> seal. NEXT ORGAN.
- [ ] tighten audit system prompt: 7B echoes scripts back instead of enumerating per-file risks.
- [ ] verify --embed flag fires on every audit (auto-embed new seals).
- [ ] theorem flags: CLIDdy/ReGen proven theorem = permanent ledger flag, never recompute.
- [ ] weekly onepass_v3.sh absorbs this snapshot.

## EVENT LOG
(empty — history starts now)
- [2026-10-11T14:04:11Z] [1cca118a8687f76f] RIDE-ALONG v2 sealed (f-string brace bug structurally fixed). Superlinear loop CLOSED: cache-hit proven, self-churn fixed, embeddings live, pushes 5de90de + 7049831. Ledger 10 rows GREEN.
- [2026-10-11T14:04:11Z] [3b494ccbf826d451] Queue upgraded with 3 structural solutions: (1) commit-state hashing via git HEAD, (2) parent-child lineage columns for pathway composition, (3) thresholded cosine semantic routing. phi4-router remains NEXT ORGAN.
