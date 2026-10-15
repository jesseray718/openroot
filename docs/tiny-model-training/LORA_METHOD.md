# LoRA Method

LoRA freezes the pretrained model weights and trains small low-rank
adapter matrices. This makes domain adaptation practical on limited
hardware.

## Recommended starting configuration

- Base model: Qwen2.5 1.5B Instruct
- Method: LoRA or QLoRA
- LoRA rank: 16
- LoRA alpha: 32
- LoRA dropout: 0.05
- Maximum sequence length: 2048
- Effective batch size: 8 to 16
- Learning rate: conservative and validated on the evaluation set
- Precision: use the lowest precision supported reliably by the hardware

## Trainer

Use TRL SFTTrainer with PEFT LoRA configuration.

The training dataset should use a conversational format compatible with
the tokenizer and trainer.

## Evaluation gate

Do not deploy an adapter unless it improves:

1. Golden-question score.
2. Refusal-test pass rate.
3. Evidence-grounding behavior.
4. JSONL formatting accuracy.
5. OpenLoom task-boundary compliance.

A model that scores well on training loss but fails refusal tests is not
ready.
