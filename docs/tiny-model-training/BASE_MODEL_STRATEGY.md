# Tiny Model Training Strategy

Use a small pretrained instruction model as the base, then train a narrow
LoRA adapter on reviewed OpenLoom examples.

Do not train a language model from scratch for this project. A tiny
domain-specific adapter is cheaper, safer, easier to evaluate, and easier
to replace.

## Base model

Preferred base:

- Qwen2.5 1.5B Instruct

Alternative smaller base:

- Qwen2.5 0.5B Instruct

The base model supplies general language ability. The LoRA adapter teaches
OpenLoom-specific behavior.

## Training objective

Teach the model to:

1. Create bounded OpenLoom tasks.
2. Use supplied database evidence rather than inventing facts.
3. Preserve SHA-256 provenance.
4. Identify missing evidence and uncertainty.
5. Refuse unsafe, destructive, or autonomous publication actions.
6. Format field observations as JSONL.
7. Produce concise, reviewable research plans.

## Required behavior

Every useful answer should include:

- The evidence or database source used.
- A clear statement of missing evidence.
- A bounded next action.
- A safety or human-review boundary when relevant.
