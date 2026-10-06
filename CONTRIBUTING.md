# Contributing to OpenRoot

OpenRoot is open-source appropriate technology: passive solar thermal systems,
opencell concrete, permaculture computation, and PoPW-verified ledgers. This
guide references only files that exist in this repository right now.

## Getting started

Clone, then run the test suite:

    git clone https://github.com/jesseray718/openroot.git
    cd openroot
    python3 -m unittest discover -s tests

No requirements.txt is needed for the core suite — it runs on the standard
library. If a script needs more, its docstring says so.

## Project map (verified)
- [docs/PUBLIC_MAP.md](docs/PUBLIC_MAP.md)
- [templates/design-packet/README.md](templates/design-packet/README.md)
- [SECURITY.md](SECURITY.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [docs/CLAIM_STATUS.md](docs/CLAIM_STATUS.md)
- [docs/PUBLIC_BOUNDARY.md](docs/PUBLIC_BOUNDARY.md)
- [docs/HARDWARE_RELEASE_STANDARD.md](docs/HARDWARE_RELEASE_STANDARD.md)
- [docs/REPOSITORIES.md](docs/REPOSITORIES.md)
- [designs/thermal-cascade/README.md](designs/thermal-cascade/README.md)

## Contribution workflow

    Submit Issue → Contribute Code or Docs → Create Pull Request
    → Fill PR Template Honestly → Checks: boundary + validation + provenance
    → Squash Merge → Delete Head Branch

Rules the CI actually enforces:

- Automation changes (.github/workflows, scripts) and public-documentation
  changes go in separate PRs — public-boundary rejects mixed ones.
- Every claim statement needs nearby evidence, assumptions, or an explicit
  non-claim marker — claim-boundary scans for naked public claim language.
- No trailing whitespace — git diff --check runs on every push.
- Squash merge is the default; the head branch is deleted after merge.

## Design packets

New hardware/experiment work starts from
templates/design-packet/README.md. Packets carry an evidence level and
explicit non-claims; do not present an unverified idea as certified,
compliant, or field-ready.

## Local automation tools (bin/)

Tracked helper scripts — all runnable locally: workflow dispatcher
(ALIGN/ASSESS/ACT/VERIFY/DOCUMENT/AMPLIFY envelopes), Ollama relay on :9999,
batch nomic embeddings, and the bottom-tier nanobot. See each file header
for usage.

## Verification checklist before opening a PR

- [ ] python3 -m unittest discover -s tests passes
- [ ] git diff --check is clean (no trailing whitespace)
- [ ] Changed-path list reviewed against the PR template boundary section
- [ ] Measurement claims carry source data or evidence references

## Newton Chain documents

Formal derivation documents (definitions, axioms, propositions, proofs) are
validated by automation/checks/newton_chain_validate.py, which also runs in
CI on docs/newton_chain/*.
