#!/usr/bin/env python3
"""
superlinear_setup.py — OpenRoot shared-context initialization and verification.

CANARY: SUPERLINEAR_SETUP_V2_20260923
"""
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE = Path.home() / "openroot"
BIN_DIR = BASE / "bin"
DATA_DIR = BASE / "data"
CONTEXT_BRIDGE = BASE / "context_bridge"
STORE = BIN_DIR / "shared_context_store.py"


def timestamp():
    return datetime.now().isoformat(timespec="seconds")


def run(args, *, input_text=None, env=None, cwd=None):
    return subprocess.run(
        args,
        input=input_text,
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
        check=False,
    )


def banner():
    print("=" * 70)
    print("OPENROOT SUPERLINEAR SETUP — SAFE CONTEXT INITIALIZATION")
    print(f"Timestamp: {timestamp()}")
    print("Canary: SUPERLINEAR_SETUP_V2_20260923")
    print("=" * 70)


def require_store():
    print("\n=== Prerequisite Check ===")
    if not STORE.is_file():
        print(f"✗ Missing required script: {STORE}")
        print("Install shared_context_store.py first.")
        return False

    if shutil.which("python3") is None:
        print("✗ python3 is not available in PATH")
        return False

    print(f"✓ Context store: {STORE}")
    print(f"✓ Python: {sys.executable}")
    return True


def initialize_database():
    print("\n=== Initializing Shared Context Database ===")
    result = run(["python3", str(STORE)], cwd=BASE)

    if result.returncode != 0:
        print("✗ Database initialization failed")
        if result.stderr.strip():
            print(result.stderr.strip())
        return False

    db_path = DATA_DIR / "shared_context.db"
    if not db_path.is_file():
        print(f"✗ Expected database was not created: {db_path}")
        return False

    print(f"✓ Database ready: {db_path}")
    return True


def register_orchestrator():
    session_id = f"window_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"\n=== Registering Session: {session_id} ===")

    result = run(
        ["python3", str(STORE), "register", session_id, "orchestrator"],
        cwd=BASE,
    )

    if result.stdout.strip():
        print(result.stdout.strip())

    if result.returncode != 0:
        print("✗ Session registration failed")
        if result.stderr.strip():
            print(result.stderr.strip())
        return None

    return session_id


def verify_json_round_trip(session_id):
    print("\n=== Testing JSON Storage Round Trip ===")

    payload = {
        "test": "message",
        "timestamp": timestamp(),
        "canary": "STORE_TEST_V2",
        "session_id": session_id,
        "quotes_preserved": 'Value contains "double quotes" correctly.',
    }
    payload_json = json.dumps(payload, separators=(",", ":"))

    env = os.environ.copy()
    env["SESSION_ID"] = session_id

    store_result = run(
        ["python3", str(STORE), "store", "test_workflow", payload_json],
        env=env,
        cwd=BASE,
    )

    if store_result.stdout.strip():
        print(store_result.stdout.strip())

    if store_result.returncode != 0:
        print("✗ Test write failed")
        if store_result.stderr.strip():
            print(store_result.stderr.strip())
        return False

    print("\nRetrieving test message:")
    get_result = run(
        ["python3", str(STORE), "get", "test_workflow"],
        cwd=BASE,
    )

    if get_result.stdout.strip():
        print(get_result.stdout.strip())

    if get_result.returncode != 0:
        print("✗ Test read failed")
        if get_result.stderr.strip():
            print(get_result.stderr.strip())
        return False

    try:
        stored_record = json.loads(get_result.stdout)
        stored_value = stored_record["value"]

        # Support both context-store output contracts:
        # 1. value is a JSON string, requiring json.loads().
        # 2. value is already a decoded JSON object (dict/list/etc.).
        if isinstance(stored_value, str):
            recovered_payload = json.loads(stored_value)
        else:
            recovered_payload = stored_value

    except (json.JSONDecodeError, KeyError, TypeError) as error:
        print(f"✗ JSON validation failed: {error}")
        return False

    if recovered_payload != payload:
        print("✗ JSON round-trip mismatch")
        print("Expected:", json.dumps(payload, indent=2))
        print("Received:", json.dumps(recovered_payload, indent=2))
        return False

    print("✓ JSON round-trip verified; double quotes preserved")
    return True


def health_check():
    print("\n=== System Health Check ===")

    checks = [
        ("Bot daemon", ["pgrep", "-af", "bot_daemon.py"]),
        ("Ollama service", ["pgrep", "-x", "ollama"]),
        ("Git branch", ["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        ("Latest commit", ["git", "log", "--oneline", "-1"]),
    ]

    for label, command in checks:
        result = run(command, cwd=BASE if label.startswith("Git") or label.startswith("Latest") else None)
        output = (result.stdout or result.stderr).strip()
        healthy = result.returncode == 0 and bool(output)
        marker = "✓" if healthy else "✗"
        print(f"{marker} {label}: {output[:100] if output else 'NOT_AVAILABLE'}")

    if shutil.which("ollama"):
        models = run(["ollama", "ps"])
        if models.returncode == 0:
            loaded = models.stdout.strip()
            coder = "LOADED" if "qwen2.5-coder:7b" in loaded else "COLD (available on demand)"
            grader = "LOADED" if "qwen2.5:3b" in loaded else "COLD (available on demand)"
            print(f"✓ 7B coder model: {coder}")
            print(f"✓ 3B grader model: {grader}")
        else:
            print("✗ Ollama model query failed")
    else:
        print("✗ ollama command not found")


def write_context_guide():
    print("\n=== Creating Context Bridge Guide ===")
    CONTEXT_BRIDGE.mkdir(parents=True, exist_ok=True)
    guide_path = CONTEXT_BRIDGE / "memory_enable_guide.md"

    guide_path.write_text(
        f"""# OpenRoot Context Bridge

Generated: {timestamp()}
Canary: CONTEXT_GUIDE_V2_20260923

## Canonical shared context

Use the local SQLite context store for durable cross-terminal and cross-process coordination:

```bash
export SESSION_ID="window_A"

python3 ~/openroot/bin/shared_context_store.py \\
  store task_key \\
  '{{"status":"complete","result":"example","canary":"TASK_V1"}}'

python3 ~/openroot/bin/shared_context_store.py get task_key
python3 ~/openroot/bin/shared_context_store.py sessions
```

## Quote rule

At a Bash prompt, surround JSON with single quotes:

```bash
'{{"key":"value","message":"double quotes are safe here"}}'
```

Inside Python, use `json.dumps()` and pass the value as an argument-list element to
`subprocess.run()`. Avoid `shell=True`, `echo`, pipes, and `$(cat)` for JSON payloads.

## OpenRoot paths

- Base: `{BASE}`
- Scripts: `{BIN_DIR}`
- Data: `{DATA_DIR}`
- Context database: `{DATA_DIR / "shared_context.db"}`
- Context bridge: `{CONTEXT_BRIDGE}`

## Workflow boundary

- Review all changes with `git status`, `git diff --check`, and `git diff`.
- Use `CONFIRM=1` for destructive operations.
- Commit messages use OpenRoot tags such as `[ADD]`, `[FIX]`, `[CASCADE]`, and `[SEAL]`.
- Git push remains explicitly human-gated.
""",
        encoding="utf-8",
    )

    print(f"✓ Guide created: {guide_path}")


def next_steps():
    print("\n" + "=" * 70)
    print("SETUP COMPLETE — VERIFY CROSS-WINDOW CONTEXT")
    print("=" * 70)
    print("""
Terminal/window A:
  export SESSION_ID="test_window_A"
  python3 ~/openroot/bin/shared_context_store.py \\
    store cross_window_test \\
    '{"msg":"hello from A","canary":"CROSS_WINDOW_V2"}'

Terminal/window B:
  export SESSION_ID="test_window_B"
  python3 ~/openroot/bin/shared_context_store.py get cross_window_test

Inspect before any commit:
  cd ~/openroot
  git status --short
  git diff --check
  git diff -- bin/superlinear_setup.py context_bridge/memory_enable_guide.md

Human-gated commit, only after review:
  git add bin/superlinear_setup.py context_bridge/memory_enable_guide.md
  git commit -m "[FIX] Safe superlinear setup JSON round-trip"
""")


def main():
    banner()

    if not require_store():
        return 1

    if not initialize_database():
        return 1

    session_id = register_orchestrator()
    if not session_id:
        return 1

    if not verify_json_round_trip(session_id):
        return 1

    health_check()
    write_context_guide()
    next_steps()

    print("\n✓ SUPERLINEAR_SETUP_V2 completed successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
