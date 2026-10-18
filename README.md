# OpenRoot

**Verifiable local autonomy. Sealed evidence, measured energy, auditable actions, physical work receipts.**

OpenRoot is a decentralized, open-source framework for civilizational regeneration based on permaculture principles, fractal mesh geometry, contribution economics, and direct work attestation.

## Receipt chain

```
v1.0 (genesis):      a5a988e5879eb4f2ce14aadc0c72ae29eded0987b0c3ca9fcf4eeb9cacf5a889
  sealed:            2026-10-18T09:21:54Z
  documents:         14 founding docs
  signed by:         Ed25519 (genesis/genesis_ed25519.pub)

v1.1 (theorem reg):    11f7934c5c1e42ca9303e939bae26425b905c186aa634190d63304092a5bfc57
  sealed:            2026-10-18T11:49:28Z
  parent:            a5a988e5... (v1.0)
  theorems registered: 3
  formal proofs:     pending v1.2

v1.2 (theorem proofs): e194bfc179af841933446906482137b3ea1c43a7afe1d753023f0ccb4c50ca7c
  sealed:              2026-10-18T14:06:32Z
  parent:              11f7934c... (v1.1)
  proofs sealed:       3 (A6, P2, P4)
```

## Pod Loader Tool — Make Your Own Pods

OpenRoot ships a pod loader that converts any text into a sealed SQLite3 pod with dual-hash content addressing, FTS5 indexing, and optional nomic embeddings.

### Quick start

```bash
# Ingest a file or directory
python3 bin/pod_loader_v1.py ingest my_pod ./my_docs/

# Optional: generate nomic embeddings (requires 'ollama pull nomic-embed-text')
python3 bin/pod_loader_v1.py embed my_pod

# Seal the pod (computes merkle root)
python3 bin/pod_loader_v1.py seal my_pod

# Query the pod
python3 bin/pod_loader_v1.py query my_pod "your search query"

# Generate a ride-along dossier across multiple pods
python3 bin/dossier_engine_v1.py --pods my_pod other_pod --query "your query"
```

### Pod architecture

- **documents** table: file identity (sha256), path, size, mtime, metadata
- **chunks** table: chunk identity (blake3), doc reference, text, char count
- **chunks_fts** virtual table: FTS5 full-text index with BM25 ranking
- **vectors** table: per-chunk nomic embeddings (blob of floats)
- **pod_meta** table: merkle_root, sealed_at, chunk_count

### Why dual-hash?

- **sha256 of file** = file identity (same file = same hash, regardless of path)
- **blake3 of chunk** = content identity (same paragraph in two pods = same chunk hash, enables cross-pod dedup)

Chunks are content-addressed objects, not local rows. They can be deduplicated, provenanced, and verified across pods.

### Embedding strategy

Per-chunk embeddings (current): fine semantic retrieval within a pod.
Per-pod embeddings (future, when pod garden hits 20+): coarse routing across many pods.

BM25 (FTS5) remains the deterministic fallback. Embeddings drift when models update; BM25 is forever.

## Founding corpus (14 documents)

| # | Document | Layer |
|---|---|---|
| 01 | Trillion Dollar Redirect | Economics |
| 02 | Full Systemic Reallocation Model | Economics |
| 03 | Combined Telecom-Energy Reallocation | Economics |
| 04 | Global Fractal Mesh Framework (Cloud 9 canonical) | Mesh |
| 05 | Societal Transformation | Vision |
| 06 | Aerocement Whitepaper v1.0 | Energy |
| 07 | Aerocement Defensive Publication | IP |
| 08 | Human Continuity Master v1.0 | Resilience |
| 09 | OpenRoot Lumo Context Bridge | Project |
| 10 | Axioms (Euclidean taxonomy, theorems marked) | Foundation |
| 11 | AX-039 Absolute Protection (Shield Law) | Governance |
| 12 | Newton Chain Kingdom Engine | Governance |
| 13 | 12 Agape Formalized | Governance |
| 14 | ACRE Specification | Token economics |

## Script Doctrine (Lesson Plan)

See `docs/LESSON_PLAN_script_doctrine.md` for the 12 laws of script doctrine (file-on-disk-first, compile gate, canary markers, stage markers, idempotency, deterministic output, separate code paths, pre-flight safety, one-paste execution, receipt logging, tool=subprocess, dry-run default).

The lesson plan is itself sealed as a pod (`lesson_plan_script_doctrine`) — proof of concept that the pod loader works on real OpenRoot documents.

## Independent verification

```bash
git clone [https://github.com/jesseray718/openroot](https://github.com/jesseray718/openroot)
cd openroot

# Verify v1.0 genesis receipt:
python3 -c "
import json, hashlib
r = json.load(open('genesis/receipt_v1.json'))
canonical = json.dumps(r, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
print('receipt_id:', hashlib.sha256(canonical.encode()).hexdigest())
"
openssl pkeyutl -verify -pubin -inkey genesis/genesis_ed25519.pub -rawin \
  -in canon_v1.bin -sigfile genesis/receipt_v1.sig
# (where canon_v1.bin is the canonical bytes — see verify script in bin/)
```

## Doctrine

- **The receipt is the constitution.** Every action either chains from the genesis or doesn't.
- **Verifiers are pure code.** Models propose. Code disposes. No exceptions.
- **Receipts are canonical, independently verifiable.** Stdlib + openssl only.
- **Act as One Human Family.** Cut what harms. Grow what heals.

## License

- Documentation: CC-BY-SA 4.0
- Code: GPL v3
- Aerocement hardware: CERN-OHL-S v2 (pending license refactor)

---
One Human Family. Build what serves. Track transparently. Reward contribution and care.
