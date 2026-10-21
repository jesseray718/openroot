#!/usr/bin/env python3
"""kai_retrieve_local_v1 — runs ON OptiPlex: find, copy, verify, extract kai assets locally."""
import os, sys, shutil, hashlib, tarfile
from datetime import datetime, timezone

FIND_ROOTS = ["/home/jesse/openroot/data/operator_holds", "/home/jesse/openroot", "/home/jesse/src/openroot"]
BUDGET_MB = int(os.environ.get("KAI_BUDGET_MB", "2048"))
DEST = "/home/jesse/kai_recovery"
TAR_EXTS = (".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar")

def p(tag, msg): print(f"{tag} {msg}", flush=True)

def sha256(path, chunk=1<<20):
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
    files = []
    seen = set()
    for root in FIND_ROOTS:
        for dirpath, dirnames, filenames in os.walk(root):
            if ".git" in dirpath.split(os.sep): continue
            for fn in filenames:
                if "kai" not in fn.lower(): continue
                full = os.path.join(dirpath, fn)
                if full in seen: continue
                seen.add(full)
                try:
                    files.append((os.path.getsize(full), full))
                except OSError:
                    continue
    if not files:
        p("[held]", "NO kai-named files — dumping operator_holds:")
        for dp, _, fns in os.walk(FIND_ROOTS[0]):
            for fn in fns: print(f"  [listed] {os.path.join(dp, fn)}")
        sys.exit(4)
    tier_a = [(s,f) for s,f in files if "/operator_holds/" in f]
    tier_b = [(s,f) for s,f in files if f.lower().endswith(TAR_EXTS) and (s,f) not in tier_a]
    tier_c = [(s,f) for s,f in files if (s,f) not in tier_a+tier_b]
    p("[gate]", f"found: {len(tier_a)} treasure, {len(tier_b)} tarballs, {len(tier_c)} other")
    chosen, spent = [], 0
    for s, f in tier_a + tier_b:
        if spent + s > BUDGET_MB << 20:
            p("[held]", f"budget skip: {f}"); continue
        chosen.append((s, f)); spent += s
    report, ok = [], 0
    for size, src in chosen:
        rel = src.replace("/home/jesse/", "").lstrip("/")
        dst = os.path.join(DEST, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst) and sha256(dst) == sha256(src):
            p("[banked]", f"already copied+verified: {rel}"); ok += 1; continue
        p("[gate]", f"copying {rel} ({size>>10}KB) ...")
        shutil.copy2(src, dst)
        if sha256(dst) != sha256(src):
            os.unlink(dst); p("[held]", f"MISMATCH {rel} — deleted"); continue
        ok += 1
        h = sha256(dst)
        report.append((rel, size, h)); p("[banked]", f"verified: {rel} sha256={h[:16]}...")
        if src.lower().endswith(TAR_EXTS):
            exdir = os.path.join(DEST, "extracted", os.path.basename(src).split(".")[0])
            try:
                os.makedirs(exdir, exist_ok=True)
                with tarfile.open(dst) as tf: tf.extractall(exdir, filter="data")
                p("[banked]", f"extracted -> {exdir}")
            except Exception as e: p("[held]", f"extract failed: {e}")
    rep = os.path.join(DEST, f"kai_local_report_{ts}.md")
    with open(rep, "w") as fh:
        fh.write(f"# kai local retrieval {ts}\n\n| file | size | sha256 |\n|---|---|---|\n")
        for rel, s, h in report: fh.write(f"| {rel} | {s} | `{h}` |\n")
    p("[gate]", f"report: {rep}")
    p("[banked]", f"{ok}/{len(chosen)} files copied+verified -> {DEST}/{'extracted/' if tier_b else ''}")
    print("[exit=0]"); sys.exit(0)

if __name__ == "__main__":
    try: main()
    except Exception as e: import traceback; traceback.print_exc(); p("[held]", "fatal — traceback above"); sys.exit(1)
