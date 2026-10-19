import argparse, hashlib, json, os, shlex, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

parser = argparse.ArgumentParser(description="Query OpenRoot desktop router with slim-packet assembly.")
parser.add_argument("question", nargs="?")
parser.add_argument("--max-tokens", type=int, default=256)
parser.add_argument("--timeout", type=int, default=240)
parser.add_argument("--latest", action="store_true")
parser.add_argument("--identity", default=os.environ.get("OPENROOT_QUERY_IDENTITY", os.path.expanduser("~/.ssh/id_ed25519")))
parser.add_argument("--answer", action="append", default=[])
parser.add_argument("--no-packet", action="store_true")
parser.add_argument("--max-rounds", type=int, default=3)
args = parser.parse_args()

home = Path.home()
base = home / ".local/state/openroot-query"
base.mkdir(parents=True, exist_ok=True)
os.chmod(base, 0o700)

if args.latest:
    receipts = sorted(base.glob("*/receipt.json"), reverse=True)
    if not receipts: raise SystemExit("No query receipts yet.")
    print(receipts[0].read_text())
    raise SystemExit(0)

if not args.question: parser.error("Provide a question, or use --latest.")
if not 1 <= args.max_tokens <= 4096: parser.error("--max-tokens must be between 1 and 4096.")
if args.timeout < 1: parser.error("--timeout must be positive.")

identity = os.path.expanduser(args.identity)
if not Path(identity).is_file(): parser.error(f"--identity file not found: {identity}")

now = datetime.now(timezone.utc)
request_id = now.strftime("%Y%m%dT%H%M%S%fZ")
run = base / request_id
run.mkdir(mode=0o700)
target = "jesse@100.122.169.43"
pending_answers = list(args.answer)
used_answers = []
rounds_log = []
final_payload = None
final_text = None
final_stdout = ""
final_stderr = ""
final_transport_status = "unknown"
final_exit_code = 0
MAX_ROUNDS = max(1, args.max_rounds)

for round_idx in range(MAX_ROUNDS):
    if round_idx > 0:
        if pending_answers:
            used_answers.append(pending_answers.pop(0))
        else:
            sys.stderr.write("\n[router asks a clarifying question]\n")
            if rounds_log and rounds_log[-1].get("clarifying_question"):
                sys.stderr.write(rounds_log[-1]["clarifying_question"] + "\n")
            sys.stderr.write("\nYour answer (or empty to abort): ")
            sys.stderr.flush()
            try:
                user_answer = input().strip()
            except (EOFError, KeyboardInterrupt):
                user_answer = ""
            if not user_answer:
                sys.stderr.write("[abort] no answer provided; banking partial receipt.\n")
                break
            used_answers.append(user_answer)

    remote = r"""
import json, subprocess, sys
from pathlib import Path
root = Path("/home/jesse/openroot")
request = json.load(sys.stdin)
head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, stdin=subprocess.DEVNULL)
print("OPENROOT_HEAD=" + head.stdout.strip(), file=sys.stderr, flush=True)
wrapper = root / "bin" / "packet_query_v1.py"
cmd = ["python3", str(wrapper), "--question", request["question"], "--max-tokens", str(request["max_tokens"]), "--router-timeout", str(request.get("timeout", 180))]
if request.get("no_packet"): cmd.append("--no-packet")
for ans in request.get("answers", []): cmd += ["--answer", ans]
result = subprocess.run(cmd, cwd=str(root))
sys.exit(result.returncode)
"""

    request_payload = {
        "question": args.question,
        "max_tokens": args.max_tokens,
        "timeout": args.timeout,
        "no_packet": args.no_packet,
        "answers": used_answers,
    }

    command = [
        "ssh", "-T",
        "-o", "IdentitiesOnly=yes",
        "-o", f"IdentityFile={identity}",
        "-o", "ConnectTimeout=15",
        "-o", "ServerAliveInterval=15",
        "-o", "ServerAliveCountMax=3",
        "-o", "BatchMode=yes",
        target,
        "python3 -c " + shlex.quote(remote),
    ]

    started = time.monotonic()
    transport_status = "unknown"
    raw_stdout = ""
    raw_stderr = ""
    exit_code = 0
    try:
        result = subprocess.run(command, input=json.dumps(request_payload), text=True, capture_output=True, timeout=args.timeout, check=False)
        exit_code = result.returncode
        raw_stdout = result.stdout or ""
        raw_stderr = result.stderr or ""
        transport_status = "completed"
    except subprocess.TimeoutExpired:
        exit_code = 124
        transport_status = "client_timeout_remote_completion_unknown"
    except OSError as exc:
        raw_stderr = str(exc)
        exit_code = 127
        transport_status = "client_launch_failed"

    elapsed = time.monotonic() - started
    payload = None
    clarifying = None
    decoder = json.JSONDecoder()
    for i, c in enumerate(raw_stdout):
        if c == "{":
            try:
                cand, _ = decoder.raw_decode(raw_stdout[i:])
            except json.JSONDecodeError:
                continue
            if isinstance(cand, dict):
                if cand.get("clarifying_question"):
                    clarifying = cand
                    break
                if "providers_tried" in cand or "response" in cand:
                    payload = cand
                    break

    final_stdout = raw_stdout
    final_stderr = raw_stderr
    final_transport_status = transport_status
    final_exit_code = exit_code

    rounds_log.append({
        "round": round_idx,
        "transport_status": transport_status,
        "exit_code": exit_code,
        "client_wall_seconds": round(elapsed, 4),
        "answers_used": list(used_answers),
        "clarifying_detected": clarifying is not None,
        "payload_received": payload is not None,
        "clarifying_question": (clarifying or {}).get("question_to_user"),
    })

    if clarifying and round_idx < MAX_ROUNDS - 1:
        continue

    final_payload = payload
    final_text = (payload.get("response", raw_stdout) if payload else raw_stdout)
    break

receipt = {
    "request_id": request_id,
    "timestamp_utc": now.isoformat(),
    "question": args.question,
    "answers_used": used_answers,
    "transport_status": final_transport_status,
    "exit_code": final_exit_code,
    "rounds": rounds_log,
    "router_success": final_payload.get("success") if final_payload else None,
    "provider": final_payload.get("provider") if final_payload else None,
    "model": final_payload.get("model") if final_payload else None,
    "tokens_reported": final_payload.get("tokens") if final_payload else None,
    "packet_blake3": (final_payload.get("packet", {}) if final_payload else {}).get("packet_blake3"),
    "pods_seen": (final_payload.get("packet", {}) if final_payload else {}).get("pods_seen"),
    "dossier_assembled": (final_payload.get("packet", {}) if final_payload else {}).get("dossier_assembled"),
    "answer_independently_verified": False,
    "cost_usd": None,
    "energy_joules": None,
    "accounting_note": "Unknown cost and energy are not recorded as zero.",
    "timeout_note": "A client timeout does not prove remote execution stopped.",
}
(run / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
(run / "stdout.txt").write_text(final_stdout)
(run / "stderr.txt").write_text(final_stderr)

checksums = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}" for p in sorted(run.iterdir()) if p.is_file()]
(run / "SHA256SUMS").write_text("\n".join(checksums) + "\n")

if final_text:
    print(final_text, end="" if final_text.endswith("\n") else "\n")
if final_stderr:
    print(final_stderr, file=sys.stderr, end="")

print("\n=== ROUTER TELEMETRY / QUERY RECEIPT ===")
print(json.dumps(receipt, indent=2))
print(f"\n[banked] receipt={run / receipt.json}")
print("[held] Receipts can contain private prompts and responses; review before sharing.")
sys.exit(final_exit_code if final_exit_code else (0 if final_payload and final_payload.get("success") else 1))
