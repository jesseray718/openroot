# STARTHERE — OpenRoot in five minutes

You are looking at a local-first epistemic commons: documents, tools, and
sealed evidence chains that compound into each other. Everything here is
free and open. Nothing publishes, pushes, or deletes without a human.

## The 5-minute quickstart

```bash
cd ~/openroot
python3 bin/friction_observer_v1.py        # what needs fixing right now?
python3 openroot_recall_bot.py --self-test 2>/dev/null \
  || python3 bin/openroot_recall_bot.py --self-test \
  || echo "recall bot not found - skip (optional)"
pod status                                 # git + latest model output
```

The friction observer is the front door: it reads the whole commons (docs,
tools, chains, entry points) and returns a ranked list of friction points.
Fix one, then record how you fixed it (see The Compounding Loop below).

## The tool map

| tool | where | what it does |
|---|---|---|
| friction_observer_v1.py | bin/ | ranks broken links, stub docs, orphan tools, sprawl, stale chains |
| pathway_cache_v1.py | bin/ | seals reusable step-by-step pathways into a hash chain |
| openroot_recall_bot.py | repo root | local evidence retrieval, staged review packets, receipts |
| newton_chain_discovery.py | bin/ | seals whitelisted documents into a discovery chain |
| openroot_activity_digest.py | bin/ | rolling summary of chains, heartbeats, and git |
| fts_pod_search.py | bin/ | search historical pod records; `ask` answers locally with evidence IDs |
| openroot-phone-v1 | bin/ | verify phone snapshots and run the shared pod query |
| pod | PATH | OpenLoom client: `pod ask`, `pod project`, `pod check`, `pod ui` |

## The compounding loop

This is the whole engine. Every piece below feeds the next, and the loop
repeats at every scale — that is the design.

1. **Observe** — run the friction observer; take the top finding.
2. **Fix** — do the work (edit a doc, wire an orphan tool, repair a link).
3. **Record** — seal the working process into the pathway cache:
   ```bash
   python3 bin/pathway_cache_v1.py record --name "wire orphan tool X" \
       --step "edit docs/tool-map.md" \
       --step "python3 bin/friction_observer_v1.py" \
       --evidence docs/tool-map.md --notes "observer now finds 0 orphans"
   ```
4. **Share** — regenerate the human-readable pathways doc:
   ```bash
   python3 bin/pathway_cache_v1.py export-md PATHWAYS.md
   ```
5. **Replay** — the next person replays your pathway instead of rediscovering
   it, refines it, and records the refinement (each entry chains to its
   parent, so improvements compound linearly and are hash-verifiable).

Do the loop once and you have saved yourself time. Do it twice and you have
saved the next person's time. That is the compounding.

## Evidence rules (from the OpenLoom handbook)

1. Raw evidence is never overwritten.
2. Every imported artifact has a SHA-256 hash.
3. AI output is a proposal, not canonical evidence.
4. SQLite databases stay local.
5. JSONL, Markdown, manifests, and receipts are safe to synchronize.
6. Nothing is committed or pushed without human review.

## Publishing boundary

The local tools may create task files, query local evidence, run local
models, write run outputs, and prepare proposed changes. They may never —
without explicit human approval — commit, push, open or merge PRs, delete
evidence, spend money, or run destructive system commands.

## Where things live

- `docs/`, `reports/`, `designs/` — the written commons
- `bin/` — the tools
- `ledger/newton_chain.jsonl`, `data/*.jsonl` — the sealed chains
- `data/pathway_cache.jsonl` — the pathway chain (created on first record)
- `PATHWAYS.md` — generated newcomer view of every cached pathway
- `context_bridge/mistake_solutions/` — 791 recorded mistakes and their fixes

## License and stance

OpenRoot is Absolute Commons: the protocol, the tools, and the knowledge are
free for all. There are no paid tiers. Value is proven at the point of
Verification and returned to everyone at the point of Creation.
