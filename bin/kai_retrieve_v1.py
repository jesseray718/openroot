#!/usr/bin/env python3
"""kai_retrieve_v1 — locate/pull/verify Kai 9000 assets from OptiPlex."""
import os, sys, subprocess, hashlib, tarfile
from datetime import datetime, timezone

HOST_CANDIDATES = ["jesse@optiplex", "jesse@192.168.1.193", "jesse@100.122.169.43"]
FIND_ROOTS = ["/home/jesse/openroot/data/operator_holds", "/home/jesse/openroot", "/home/jesse/src/openroot"]
BUDGET_MB = int(os.environ.get("KAI_BUDGET_MB", "1024"))
DEST = os.path.expanduser("~/kai_recovery")
SSH_OPTS = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=6", "-o", "StrictHostKeyChecking=accept-new"]
TAR_EXTS = (".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar")

def p(tag, msg): print(f"{tag} {msg}", flush=True)

def run(args, inp=None, timeout=120):
    return subprocess.run(args, capture_output=True, text=False, input=inp, timeout=timeout)

def pick_host():
    for h in HOST_CANDIDATES:
        p("[gate]", f"probing host {h} ...")
        try:
            r = run(["ssh", *SSH_OPTS, h, "true"], timeout=12)
            if r.returncode == 0:
                p("[banked]", f"connected via {h}")
                return h
        except Exception as e:
            p("[held]", f"{h} unreachable: {e}")
    return None

def sha256_local(path, chunk=1<<20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()

def main():
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    os.makedirs(DEST, exist_ok=True)
    host = pick_host()
    if not host:
        p("[held]", "no reachable host — check Tailscale/WiFi"); sys.exit(2)

    find_cmd = "; ".join(
        f'[ -d "{r}" ] && find "{r}" -name .git -prune -o -type f -iname "*kai*" -printf "%s\\t%p\\n"'
        for r in FIND_ROOTS)
    p("[gate]", "discovering kai files (operator_holds prioritized) ...")
    r = run(["ssh", *SSH_OPTS, host, find_cmd], timeout=90)
    if r.returncode != 0:
        err = r.stderr.decode(errors="replace")[:400]
        p("[held]", f"find failed rc={r.returncode}: {err}"); sys.exit(3)
    files = []
    for ln in r.stdout.decode(errors="replace").splitlines():
        if "\t" in ln:
            sz, path = ln.split("\t", 1)
            if path not in [f[1] for f in files]:
                files.append((int(sz or 0), path))
    if not files:
        p("[held]", "NO kai-named files found. Dumping operator_holds listing:")
        r2 = run(["ssh", *SSH_OPTS, host,
                  'find /home/jesse/openroot/data/operator_holds -maxdepth 2 -type f -printf "%s\\t%p\\n"'], timeout=60)
        print(r2.stdout.decode(errors="replace")); sys.exit(4)

    tier_a = [(s, f) for s, f in files if "/operator_holds/" in f]
    tier_b = [(s, f) for s, f in files if f.lower().endswith(TAR_EXTS) and (s, f) not in tier_a]
    tier_c = [(s, f) for s, f in files if (s, f) not in tier_a + tier_b]
    p("[gate]", f"found: {len(tier_a)} treasure, {len(tier_b)} tarballs, {len(tier_c)} other")

    chosen, spent = [], 0
    for s, f in tier_a + tier_b:
        if spent + s > BUDGET_MB << 20:
            p("[held]", f"budget skip: {f} ({s>>20}MB)"); continue
        chosen.append((s, f)); spent += s
    if not chosen:
        p("[held]", "nothing within budget — raise KAI_BUDGET_MB"); sys.exit(5)

    p("[gate]", "computing remote sha256 for chosen files ...")
    payload = b"".join(f.encode() + b"\0" for _, f in chosen)
    r = run(["ssh", *SSH_OPTS, host, "xargs -0 sha256sum"], inp=payload, timeout=300)
    remote = {}
    for ln in r.stdout.decode(errors="replace").splitlines():
        parts = ln.split(None, 1)
        if len(parts) == 2: remote[parts[1].lstrip("*").strip()] = parts[0]

    report, ok = [], 0
    for size, rf in chosen:
        rel = rf.replace("/home/jesse/", "").lstrip("/")
        lpath = os.path.join(DEST, rel)
        os.makedirs(os.path.dirname(lpath), exist_ok=True)
        if os.path.exists(lpath):
            if remote.get(rf) and sha256_local(lpath) == remote[rf]:
                p("[banked]", f"already pulled+verified, skip: {rel}"); ok += 1
                report.append((rel, size, remote[rf], "skip-verified")); continue
        p("[gate]", f"pulling {rel} ({size>>10}KB) ...")
        rc = subprocess.run(["scp", *SSH_OPTS, f"{host}:{rf}", lpath]).returncode
        if rc != 0:
            report.append((rel, size, "?", "scp-failed")); p("[held]", f"scp failed {rel}"); continue
        lsum = sha256_local(lpath)
        rsum = remote.get(rf, "?")
        if lsum != rsum:
            os.unlink(lpath); report.append((rel, size, lsum, "MISMATCH-deleted"))
            p("[held]", f"sha256 MISMATCH on {rel} — deleted locally, retry"); continue
        ok += 1
        report.append((rel, size, lsum, "verified"))
        p("[banked]", f"verified: {rel} sha256={lsum[:16]}...")
        if rf.lower().endswith(TAR_EXTS):
            exdir = os.path.join(DEST, "extracted", os.path.basename(rf).split(".")[0])
            try:
                os.makedirs(exdir, exist_ok=True)
                with tarfile.open(lpath) as tf:
                    tf.extractall(exdir, filter="data")
                n = sum(len(fs) for _, _, fs in os.walk(exdir))
                p("[banked]", f"extracted {rel} -> {exdir} ({n} files)")
            except Exception as e:
                p("[held]", f"extract failed for {rel}: {e}")

    rep = os.path.join(DEST, f"kai_retrieve_report_{ts}.md")
    with open(rep, "w") as fh:
        fh.write(f"# kai_retrieve_v1 report {ts} (host={host})\n\n"
                 f"| file | size | sha256 | status |\n|---|---|---|---|\n")
        for rel, s, h, st in report: fh.write(f"| {rel} | {s} | `{h}` | {st} |\n")
        fh.write("\n## Listed-not-pulled (tier C):\n")
        for s, f in tier_c: fh.write(f"- {f} ({s}B)\n")
    p("[gate]", f"report: {rep}")
    if tier_c: print("\n".join(f"  [listed] {f} ({s}B)" for s, f in tier_c[:25]))
    p("[banked]", f"{ok}/{len(chosen)} files pulled and sha256-verified into {DEST}")
    print("[exit=0]"); sys.exit(0)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: p("[held]", "aborted by operator"); sys.exit(130)
    except Exception as e: p("[held]", f"fatal: {e!r}"); sys.exit(1)
