# Targeted dossier compilation: gate test v1

## Scope

One question about task1-to-task6 control flow in a captured gh_window_opener_v1.py source artifact.

This is a targeted compiler test, not a general five-pod retrieval benchmark or a completed 100-question evaluation.

## Provenance

- Baseline test: `3aabe240753b4b4fa49c5b282d65b92c`
- Compiled test: `410a8844b13d47fa897206d3e3ab6c99`
- Source artifact SHA-256: `27fb8b29e0d83a122239150ac5e37bf0863f770acb93024713657c05f2a534bc`
- Model: `openroot-coder:latest`

## Measurements

| Metric | Baseline | Compiled |
|---|---:|---:|
| Prompt tokens | 1994 | 810 |
| Output tokens | 10 | 78 |
| Wall seconds | 72.199 | 44.335 |
| Load seconds | 7.353 | 8.334 |
| Prompt processing seconds | 63.214 | 23.577 |
| Generation seconds | 1.534 | 12.316 |

- Prompt-token reduction: 59.38%.
- Observed wall-time reduction: 38.59%.
- Cache conditions were not controlled; no causal speedup claim.

## Answer review

Human review in the development conversation found the core conclusion correct: task1's hold receipt does not block task6.

The compiled answer omitted the requested citation and did not explicitly identify CONFIRM as task6's actual condition. This is not a full instruction-following pass.

Database test records remain unverified; no automatic promotion to a verified pathway was performed.

## Compiler boundaries

- Extracts original-source spans and local function dependencies.
- Preserves the full input and source in local archives.
- Does not establish complete control-flow coverage.
- Does not demonstrate generalization to another question.
- Does not implement automatic correction/pathway retrieval.
- Makes no GitHub changes during compilation or inference.

## Reproduction

The scripts depend on the existing local pod and interaction databases. Those databases and private evidence are not included.

```bash
python3 bin/compile_gate_dossier_v2.py
python3 bin/test_compiled_gate_v1.py
```

## Script fingerprints

- `bin/compile_gate_dossier_v2.py`: `1c96e4671b0c3a0da4457fe97e473a119e13580d99923e836e507a631e78546e`
- `bin/test_compiled_gate_v1.py`: `f41252b139e9e6b50fa25d381a293801befa2ade5f37dfdd8047efd9b75223df`
