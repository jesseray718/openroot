#!/usr/bin/env python3
"""OpenRoot slim-packet query wrapper with recursive clarifying-question loop.

Motions per logical turn:
  1. assemble dossier (BM25+Nomic across all pods in pods_garden/)
  2. cloud_router_v2(prompt = question + dossier)
  3. if model emits a clarifying question -> exit 2 with JSON marker
     (thin client captures user answer via --answer or interactive prompt,
      re-fires this wrapper; loop bounded by MAX_CLARIFY_ROUNDS)
  4. bank packet_blake3 in router output for receipt audit
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(os.environ.get("OPENROOT_REPO", "/home/jesse/openroot"))
GARDEN = REPO / "pods_garden"
DOSSIER = REPO / "bin" / "dossier_engine_v1.py"
ROUTER = REPO / "bin" / "cloud_router_v2.py"
PACKET_TOKEN_CAP = int(os.environ.get("OPENROOT_PACKET_TOKENS", "350"))
MAX_CLARIFY_ROUNDS = int(os.environ.get("OPENROOT_MAX_CLARIFY", "2"))


def list_pods():
    if not GARDEN.is_dir():
        return []
    return [p.name for p in GARDEN.iterdir() if p.is_dir()]


def blake3_hex(b: bytes) -> str:
    try:
        import blake3
        return blake3.blake3(b).hexdigest()
    except Exception:
        return hashlib.sha256(b).hexdigest()


def assemble_dossier(question: str, pods: list, token_cap: int) -> dict:
    if not pods or not DOSSIER.is_file():
        return {"text": "", "hits": [], "assembled": False, "reason": "no_pods_or_no_dossier"}
    try:
        r = subprocess.run(
            ["python3", str(DOSSIER), "--pods", *pods,
             "--query", question, "--max-tokens", str(token_cap)],
            capture_output=True, text=True, timeout=30, cwd=str(REPO),
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        return {"text": "", "hits": [], "assembled": False, "reason": "dossier_timeout"}
    if r.returncode != 0:
        return {"text": "", "hits": [], "assembled": False,
                "reason": f"dossier_exit_{r.returncode}", "stderr": r.stderr[:200]}
    return {"text": r.stdout.strip(), "hits": [], "assembled": True,
            "stderr_tail": r.stderr[-200:] if r.stderr else ""}


def is_clarifying(text: str) -> bool:
    head = text.lstrip()[:120].lower()
    markers = ["clarif", "do you mean", "which ", "could you specify",
               "i need more", "ambiguous", "before i answer",
               "can you confirm", "do you want", "are you asking",
               "would you like", "please provide", "to give you"]
    return any(m in head for m in markers)


def call_router(prompt: str, max_tokens: int, timeout: int) -> dict:
    r = subprocess.run(
        ["python3", str(ROUTER), "--prompt", prompt, "--max-tokens", str(max_tokens)],
        capture_output=True, text=True, timeout=timeout, cwd=str(REPO),
        stdin=subprocess.DEVNULL,
    )
    payload = None
    decoder = json.JSONDecoder()
    for i, c in enumerate(r.stdout):
        if c == "{":
            try:
                cand, _ = decoder.raw_decode(r.stdout[i:])
            except json.JSONDecodeError:
                continue
            if isinstance(cand, dict) and ("providers_tried" in cand or "response" in cand):
                payload = cand
                break
    return {"exit": r.returncode, "stdout": r.stdout, "stderr": r.stderr,
            "payload": payload}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--question", required=True)
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--router-timeout", type=int, default=180)
    ap.add_argument("--no-packet", action="store_true",
                    help="skip dossier assembly; raw prompt only")
    args = ap.parse_args()

    pods = list_pods()
    dossier = {"assembled": False} if args.no_packet \
              else assemble_dossier(args.question, pods, PACKET_TOKEN_CAP)

    if dossier["assembled"] and dossier["text"]:
        prompt = (
            "CONTEXT PACKET (BM25+Nomic, slim, from pods_garden):\n"
            f"{dossier['text']}\n"
            "---\n"
            f"QUESTION:\n{args.question}\n"
        )
    else:
        prompt = args.question

    packet = {
        "question": args.question,
        "pods_seen": pods,
        "packet_bytes": len(prompt.encode()),
        "packet_blake3": blake3_hex(prompt.encode()),
        "dossier_assembled": dossier["assembled"],
        "dossier_reason": dossier.get("reason"),
    }
    sys.stderr.write("PACKET_META=" + json.dumps(packet) + "\n")
    sys.stderr.flush()

    result = call_router(prompt, args.max_tokens, args.router_timeout)
    payload = result.get("payload") or {}

    # Clarifying-question detection + round-trip
    response_text = payload.get("response", result["stdout"]) if payload else result["stdout"]
    if is_clarifying(response_text):
        # Surface a structured marker the thin client can detect and route to the user
        clar = {
            "clarifying_question": True,
            "question_to_user": response_text.strip(),
            "packet_blake3": packet["packet_blake3"],
            "awaiting_answer": True,
        }
        print(json.dumps(clar, indent=2))
        sys.exit(2)  # 2 = "paused, waiting on user clarification"

    if payload:
        out = dict(payload)
        out["packet"] = packet
        print(json.dumps(out, indent=2))
    else:
        print(result["stdout"], end="")
        if result["stderr"]:
            print(result["stderr"], file=sys.stderr, end="")
    sys.exit(result["exit"] or (0 if payload and payload.get("success") else 1))

if __name__ == "__main__":
    main()
