#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat TERM=dumb
# CANARY:PPLX-RELAY-V3
# hygiene: preserve v1 and incoming evidence; never execute clipboard wrappers.
printf '%s\n' \
  '[gate] Root cause: SSH received no payload stdin; remote cat captured terminal input instead.' \
  '[gate] Fix: extract heredoc body, supply explicit stdin, validate bash syntax before execution.' \
  '[gate] RUN=1 would start watcher; EXECUTE=1 would authorize remote script execution.' \
  '[gate] CONFIRM=1 would allow replacement of a different remote script; default refuses.' \
  '[gate] COMMIT=1 and PUSH=1 reserved; this script neither commits nor pushes.'
command -v python >/dev/null 2>&1 || {
  printf '%s\n' '[held] python missing; no changes to existing relay.' '[exit=0]'
  exit 0
}
state=/data/data/com.termux/files/home/.pplx_relay
mkdir -p "$state"
worker=$(mktemp "$state/relay-worker-v3-XXXXXXXX.py")
cat > "$worker" <<'INNER_PY'
import hashlib
import os
import pathlib
import re
import shlex
import subprocess
import sys
import time
import uuid

ROOT = pathlib.Path("/data/data/com.termux/files/home/.pplx_relay")
HOST = "jesse@100.122.169.43"
SSH = ["ssh", "-T", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
       "-o", "ServerAliveInterval=10", "-o", "ServerAliveCountMax=2", HOST]

def emit(tag, text):
    print(f"[{tag}] {text}", flush=True)

def parse(text):
    lines = text.splitlines()
    if len(lines) < 4:
        raise ValueError("wrapper too short")
    match = re.fullmatch(
        r"cat > (/home/jesse/openroot/(?:scripts|relay)/[A-Za-z0-9_.-]+\.sh) <<'([A-Za-z_][A-Za-z0-9_]*)'",
        lines[0])
    if not match:
        raise ValueError("expected exact server scripts/relay wrapper")
    target, delimiter = match.groups()
    try:
        end = lines.index(delimiter, 1)
    except ValueError:
        raise ValueError("closing delimiter absent")
    if lines[end + 1:] != ["bash " + target]:
        raise ValueError("unexpected wrapper trailer")
    body = "\n".join(lines[1:end]) + "\n"
    if not body.strip():
        raise ValueError("empty payload")
    return target, body

def syntax(body):
    result = subprocess.run(["bash", "-n"], input=body, text=True,
                            capture_output=True, timeout=15)
    if result.returncode:
        raise ValueError("payload bash-n failed")

def selftest():
    test = ("cat > /home/jesse/openroot/relay/test_v3.sh <<'EOF'\n"
            "printf '%s\\n' '[banked] canary'\nEOF\n"
            "bash /home/jesse/openroot/relay/test_v3.sh\n")
    target, body = parse(test)
    syntax(body)
    assert target.endswith("/test_v3.sh") and body.startswith("printf")
    for bad in [test.replace("/home/jesse/openroot/relay/", "/tmp/"),
                test + "echo injected\n",
                test.replace("EOF\nbash", "MISSING\nbash")]:
        try:
            parse(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid wrapper accepted")
    emit("banked", "parser positive/negative tests=PASS; bash-n=PASS")
    old = ROOT / "incoming-20261009T194302Z.sh"
    if old.exists():
        target, body = parse(old.read_text())
        syntax(body)
        emit("banked", f"recorded canary extracted bytes={len(body.encode())}; no replay")
    emit("banked", f"worker sha256={hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}")

def remote_run(target, body):
    syntax(body)
    quoted = shlex.quote(target)
    parent = shlex.quote(str(pathlib.PurePosixPath(target).parent))
    confirm = "1" if os.environ.get("CONFIRM") == "1" else "0"
    command = (
        "set -eu; export GIT_PAGER=cat TERM=dumb; "
        f"mkdir -p {parent}; "
        f"tmp=$(mktemp {parent}/.relay-stage-XXXXXXXX); "
        'trap \'rm -f -- "$tmp"\' EXIT; '
        'cat > "$tmp"; '
        'test -s "$tmp"; bash -n "$tmp"; '
        f"if [ -L {quoted} ]; then "
        "printf '[held] symlink destination refused\\n'; exit 73; fi; "
        f"if [ -e {quoted} ] && ! cmp -s \"$tmp\" {quoted}; then "
        "printf '[gate] CONFIRM=1 would replace differing destination\\n'; "
        f"if [ {confirm} != 1 ]; then "
        "printf '[held] replacement withheld\\n'; exit 73; fi; fi; "
        f'cp -- "$tmp" {quoted}; '
        f"printf '[banked] remote payload installed and syntax checked\\n'; bash {quoted}"
    )
    return subprocess.run(SSH + [command], input=body, text=True,
                          capture_output=True, timeout=600)

def watch():
    if os.environ.get("EXECUTE") != "1":
        emit("held", "RUN requires EXECUTE=1; clipboard remains untouched")
        return
    for executable in ["termux-clipboard-get", "termux-clipboard-set", "ssh"]:
        import shutil
        if not shutil.which(executable):
            raise ValueError(f"missing executable={executable}")
    probe = subprocess.run(SSH + ["printf ready"], capture_output=True,
                           text=True, timeout=30)
    if probe.returncode or probe.stdout != "ready":
        raise ValueError("noninteractive SSH probe failed")
    emit("banked", "watcher armed; only validated server wrappers accepted")
    last = None
    while True:
        clip = subprocess.run(["termux-clipboard-get"], capture_output=True,
                              text=True, timeout=15)
        text = clip.stdout
        digest = hashlib.sha256(text.encode()).hexdigest()
        if clip.returncode or not text.startswith("cat > ") or digest == last:
            time.sleep(2)
            continue
        last = digest
        try:
            target, body = parse(text)
            syntax(body)
        except ValueError as exc:
            emit("held", str(exc))
            time.sleep(2)
            continue
        token = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-" + uuid.uuid4().hex[:8]
        (ROOT / f"incoming-{token}.sh").write_text(text)
        try:
            result = remote_run(target, body)
            raw = result.stdout + result.stderr
            rc = result.returncode
        except subprocess.TimeoutExpired as exc:
            raw = "Remote timeout; execution outcome unknown. Do not replay automatically.\n"
            rc = 124
        (ROOT / f"remote-{token}.txt").write_text(raw)
        lines = raw.splitlines()
        report = [f"[gate] relay={token} script={pathlib.PurePosixPath(target).name}",
                  f"[gate] payload-sha256={hashlib.sha256(body.encode()).hexdigest()}"]
        report += ["[gate] remote: " + line[:500] for line in lines[:45]]
        if len(lines) > 45:
            report.append(f"[held] additional remote lines archived={len(lines)-45}")
        report += [f"[{'banked' if rc == 0 else 'held'}] remote-exit={rc}",
                   "[exit=0]"]
        rendered = "\n".join(report) + "\n"
        (ROOT / f"report-{token}.txt").write_text(rendered)
        current = subprocess.run(["termux-clipboard-get"], capture_output=True,
                                 text=True, timeout=15)
        if current.returncode == 0 and current.stdout == text:
            copied = subprocess.run(["termux-clipboard-set"], input=rendered,
                                    text=True, capture_output=True, timeout=15)
            emit("banked" if copied.returncode == 0 else "held",
                 f"remote-exit={rc}; report={token}; clipboard-set-exit={copied.returncode}")
        else:
            emit("held", f"clipboard changed; preserved new input; report={token}")
        time.sleep(2)

try:
    selftest()
    if os.environ.get("RUN") == "1":
        watch()
    else:
        emit("held", "dry-run complete; start with RUN=1 EXECUTE=1 bash /data/data/com.termux/files/home/relay_v3.sh")
except KeyboardInterrupt:
    emit("held", "watcher stopped by operator")
except Exception as exc:
    emit("held", f"{type(exc).__name__}: {str(exc).replace(chr(10), ' ')[:400]}")
    sys.exit(1)
INNER_PY
if ! python -m py_compile "$worker" >/dev/null 2>&1; then
  printf '%s\n' '[held] worker py_compile=FAIL; execution withheld.' '[exit=0]'
  exit 0
fi
printf '%s\n' '[banked] worker py_compile=PASS; previous relay unchanged.'
if python "$worker"; then
  :
else
  printf '%s\n' '[held] relay worker failed; inspect tagged output; no automatic retry.'
fi
printf '%s\n' '[exit=0]'
