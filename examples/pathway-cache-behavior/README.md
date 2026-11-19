# Reproducible pathway-cache behavior

Python 3.10+; standard library only. Run from the repository root:

    python3 examples/pathway-cache-behavior/demo.py
    python3 examples/pathway-cache-behavior/demo.py --self-test

Expected exits: original=0; external file changed=0; invalid JSON added=0; entry tampered=1.
The verifier opens only the fixture ledger. All files changed by the demo are temporary fixtures.

This freezes reviewed source 1c148b1c6f9a4474c3b1840ba0819de6fa343457d2681bec1812ae9107cffc5c. It is not an installed-tool replacement.
Success reproduces this version's behavior, including its limitations; it does not endorse those limitations.
The hash check detects alteration of the frozen snapshot, not proof of every claim.

observations.json contains selected real A/B/C/D receipts and the failed D answer.
Sequential timings do not establish a curriculum-caused inference speedup.
No private terminal logs, database contents, endpoints, or credentials are included.

Not demonstrated: automatic trimmer repair, canonical lesson ingestion, or offline A15 reuse.
The snapshot and example follow the repository's software license.
