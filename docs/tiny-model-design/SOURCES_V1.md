# Tiny Model Design Sources V1

Approved initial corpus:

1. NVIDIA — How Small Language Models Are Key to Scalable Agentic AI
2. arXiv 2506.02153 — Small Language Models are the Future of Agentic AI
3. arXiv 2501.05465 — Small Language Models Can Still Pack a Punch: A Survey
4. arXiv 2411.03350 — Comprehensive Survey of Small Language Models
5. Hugging Face SmolLM3-3B model card
6. Hugging Face function-calling guide

Ingestion rule:
- Ingest text/markdown only.
- Preserve source URI, capture time, license, and SHA-256.
- Do not ingest model weights or unlicensed datasets.
- Return NOT IN EVIDENCE when the corpus does not answer a design question.
