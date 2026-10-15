# Training Data Rules

Training data must be reviewed before use.

## Source layers

1. Reference corpus
   - Manuals, articles, local notes, code, and receipts.
   - Used for retrieval and grounding.

2. Training dataset
   - Curated instruction/response pairs derived from reviewed material.
   - Each example teaches one clear behavior.

3. Evaluation dataset
   - Golden questions and refusal tests.
   - Used to measure real improvement.

## JSONL training format

Use conversational messages:

```json
{
  "messages": [
    {"role": "system", "content": "You are OpenLoom."},
    {"role": "user", "content": "Task or question"},
    {"role": "assistant", "content": "Reviewed answer"}
  ]
}
```

## Quality rules

- One behavior per example.
- No copied long passages.
- No secrets, API keys, or private paths.
- Mark uncertainty explicitly.
- Prefer correct refusal over confident invention.
- Keep a validation split that is never trained on.
- Keep refusal tests separate from ordinary training examples.

## Initial target

Start with 300 to 600 reviewed examples.

Suggested split:

- 80 percent training
- 10 percent validation
- 10 percent test
