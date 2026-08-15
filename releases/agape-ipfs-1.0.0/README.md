# agape-ipfs

Local-first IPFS pinning CLI with deterministic SHA-256 ledger, multi-provider fallback, verification, and proof generation.

Part of the OpenRoot / Agape Net stack (PoPW thermodynamic ledger).

## Quick start

```bash
./install.sh
agape-ipfs version
agape-ipfs pin ./some-file
agape-ipfs status
agape-ipfs proof <cid>
Commands
Command
Purpose
pin <path>
Local-first pin + ledger append
status
Last 12 ledger entries
hash <path>
Deterministic tree hash
proof <cid>
Markdown proof artifact
verify <cid>
Gateway reachability
get <cid>
Fetch content
return <cid>
Lineage lookup
version
Print version
Environment
PINATA_JWT — optional cloud fallback
GITHUB_TOKEN — optional gist proofs
OPENROOT_LEDGER / OPENROOT_IPFS — override default paths
License
MIT — see LICENSE.
