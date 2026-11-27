# Claims and evidence

This table separates project documentation from local results reported by the
operator. It does not establish that the local machines or private receipts
were inspected for this document. The evidence scope is November 27, 2026.

| Claim | Status | Source and boundary |
|---|---|---|
| OpenRoot aims to build local-first knowledge pods and correction-aware answer pathways. | CLAIMED | [README](../README.md): project description, not complete-system acceptance. |
| Earlier local pod and correction-retrieval tests passed. | OPERATOR-REPORTED | [November 23 status](STATUS-2026-11-23.md): earlier reported tests; their full local artifacts are not available here. |
| A later local pod build read 16,314 files and stored 36,162 unique cells. Its build report listed 12 passing self-tests, including writing a pathway to a sidecar without changing the pod's pathway table. | OPERATOR-REPORTED | [November 27 summary](REGENERATIVE-COMMONS.md#what-the-november-27-local-output-shows): terminal output shared by the operator; neither the pod nor the full build receipt is available here. |
| A ledger-related query returned source headings from a scratch pod copy, after which the pod and receipt hashes matched according to the local command. | OPERATOR-REPORTED | [November 27 summary](REGENERATIVE-COMMONS.md#what-the-november-27-local-output-shows): retrieval smoke test, not evidence of answer quality or generation. |
| Multi-node agreement and root-to-root exchange were listed as not implemented in the reported lattice receipt. | OPERATOR-REPORTED | [November 27 summary](REGENERATIVE-COMMONS.md#what-the-november-27-local-output-shows): local receipt was not opened here. |
| The public repository demonstrates a pathway-cache component with disposable fixtures. | CLAIMED | [Example documentation](../examples/pathway-cache-behavior/README.md): component behavior and limitations, not full-system acceptance. |

Grounded local-model answers are an objective and an area of ongoing testing,
not a blanket claim about every answer or deployed route. A matching hash
does not establish that an answer is correct or its evidence is current.
