#!/usr/bin/env python3
"""OpenRoot slim-packet query wrapper with recursive clarifying-question loop."""
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

def blake3_hex(b):
    try:
        import blake3
        return blake3.blake3(b).hexdigest()
    except Exception:
        return hashlib.sha256(b).hexdigest()

def assemble_dossier(question, pods, token_cap):
    if not pods or not DOSSIER.is_file():
        return {"text": "", "assembled": False, "reason": "no_pods_or_no_dossier"}
    try:
        r = subprocess.run(
            ["python3", str(DOSSIER), "--pods", *pods, "--query", question, "--max-tokens", str(token_cap)],
            capture_output=True, text=True, timeout=30, cwd=str(REPO), stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return {"text": "", "assembled": False, "reason": "dossier_timeout"}
    if r.returncode != 0:
        return {"text": "", "assembled": False, "reason": f"dossier_exit_{r.returncode}", "stderr": r.stderr[:200]}
    return {"text": r.stdout.strip(), "assembled": True}

def is_clarifying(text):
    head = text.lstrip()[:160].lower()
    markers = ["clarif", "do you mean", "which ", "could you specify", "i need more", "ambiguous", "before i answer", "can you confirm", "do you want", "are you asking", "would you like", "please provide", "to give you"]
    return any(m in head for m in markers)

def call_router(prompt, max_tokens, timeout):
    r = subprocess.run(
        ["python3", str(ROUTER), "--prompt", prompt, "--max-tokens", str(max_tokens)],
        capture_output=True, text=True, timeout=timeout, cwd=str(REPO), stdin=subprocess.DEVNULL)
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
    return {"exit": r.returncode, "stdout": r.stdout, "stderr": r.stderr, "payload": payload}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--question", required=True)
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--router-timeout", type=int, default=180)
    ap.add_argument("--no-packet", action="store_true")
    ap.add_argument("--answer", action="append", default=[])
    args = ap.parse_args()
    pods = list_pods()
    rounds = []
    question = args.question
    if args.answer:
        for i, ans in enumerate(args.answer, 1):
            question += f"\n\n[CLARIFYING_ANSWER_{i}]:\n{ans}"
    for round_idx in range(MAX_CLARIFY_ROUNDS + 1):
        dossier = ({"assembled": False} if args.no_packet else assemble_dossier(question, pods, PACKET_TOKEN_CAP))
        if dossier["assembled"] and dossier["text"]:
            prompt = f"CONTEXT PACKET (BM25+Nomic, slim, from pods_garden):\n{dossier['text']}\n---\nQUESTION:\n{question}\n"
        else:
            prompt = question
        packet_meta = {"round": round_idx, "question": question, "pods_seen": pods, "packet_bytes": len(prompt.encode()), "packet_blake3": blake3_hex(prompt.encode()), "dossier_assembled": dossier["assembled"], "dossier_reason": dossier.get("reason"), "prior_rounds": rounds[:]}
        sys.stderr.write("PACKET_META=" + json.dumps(packet_meta) + "\n")
        sys.stderr.flush()
        result = call_router(prompt, args.max_tokens, args.router_timeout)
        payload = result.get("payload") or {}
        response_text = (payload.get("response", result["stdout"]) if payload else result["stdout"])
        rounds.append({"round": round_idx, "packet_blake3": packet_meta["packet_blake3"], "router_exit": result["exit"], "router_success": payload.get("success") if payload else None, "clarifying_detected": is_clarifying(response_text)})
        if is_clarifying(response_text) and round_idx < MAX_CLARIFY_ROUNDS:
            clar = {"clarifying_question": True, "round": round_idx, "question_to_user": response_text.strip(), "packet_blake3": packet_meta["packet_blake3"], "prior_rounds": rounds, "awaiting_answer": True}
            print(json.dumps(clar, indent=2))
            sys.exit(2)
        if payload:
            out = dict(payload)
            out["packet"] = packet_meta
            out["rounds"] = rounds
            print(json.dumps(out, indent=2))
        else:
            print(result["stdout"], end="")
            if result["stderr"]:
                print(result["stderr"], file=sys.stderr, end="")
        sys.exit(result["exit"] or (0 if payload and payload.get("success") else 1))

if __name__ == "__main__":
    main()
