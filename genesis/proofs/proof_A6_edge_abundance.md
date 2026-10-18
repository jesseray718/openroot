# Proof A6: Edge Abundance

**Theorem:** Retired hardware + open weights = compute for the poor.
**Status:** PROVEN (existence proof + logical synthesis)
**Sealed in:** v1.2 receipt

## Definitions

- "Retired hardware" = computing devices no longer in primary use (corporate refresh cycles, consumer upgrades, e-waste stream)
- "Open weights" = ML model parameters published under permissive licenses (Llama, Qwen, Mistral, DeepSeek, etc.)
- "Compute for the poor" = accessible computational capacity at near-zero marginal cost

## Proof

### Part 1 — Existence of retired hardware (empirical premise)

- UN Global E-waste Monitor 2024: 62 million metric tons of e-waste generated annually
- Of this, a substantial fraction is functional computing hardware (CPUs, RAM, SSDs, GPUs)
- EPA: only ~15% of e-waste is properly recycled; the rest goes to landfill or informal recovery
- Therefore: large quantities of functional compute hardware exist outside primary markets at near-zero acquisition cost

### Part 2 — Existence of open weights (empirical premise)

- Llama 3.x, Qwen 2.5/3, Mistral, DeepSeek, Granite, Phi — all published under permissive licenses
- Models range from 0.5B to 70B+ parameters
- Downloadable via Hugging Face, Ollama, direct torrent
- Therefore: a library of capable models exists at zero acquisition cost

### Part 3 — Existence of runtime environments (empirical premise)

- llama.cpp: runs modern transformer models on CPU, including x86, ARM, RISC-V
- Ollama: packaging layer that simplifies deployment
- GGUF quantization: enables 4-bit, 8-bit inference within RAM constraints
- Therefore: software exists to run open weights on commodity hardware

### Part 4 — Synthesis (logical step)

- Premise A: Functional retired hardware exists (Part 1)
- Premise B: Open weights exist (Part 2)
- Premise C: Runtime software exists (Part 3)
- Combining: all three are independently available at near-zero marginal cost
- Therefore: the system {retired hardware + open weights + runtime} provides compute at near-zero marginal cost
- Therefore: compute is accessible to those without capital for new hardware (the "poor" in the claim)

### Part 5 — Existence proof (empirical confirmation)

The Qwen 1.5B model running on a Samsung Galaxy A15 with no internet connection — the existence proof cited in the v1.0 axioms document itself — demonstrates the claim concretely. This is not theoretical; it is operational today.

## Limitations

- This proof establishes existence, not scale. The claim "compute for the poor" is proven for individual instances; scaling to global poor populations requires additional infrastructure (mesh distribution of weights, hardware redistribution logistics).
- This proof does not address model quality. Smaller open-weights models are less capable than frontier proprietary models. "Compute for the poor" is technically accurate but does not imply capability parity.

## Conclusion

A6 is proven by combining empirical premises (existence of inputs) with logical synthesis (combination of inputs produces output) and confirmed by existence proof (A15 + Qwen 1.5B running today).

QED.
