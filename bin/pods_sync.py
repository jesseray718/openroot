#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# OpenRoot — jesseray718
# PANE: BOTH (host-guarded auto-detect: A15 Termux / OptiPlex SSH)
# eta = useful_joules / human_joules
"""pods_sync v2.0 — sync all pods across 4 sites with parked conflicts.

Sites (auto by pane):
  A15 live   /data/data/com.termux/files/home/pods
             /data/data/com.termux/files/home/openroot/pods
  A15 mirror /storage/emulated/0/openroot/pods                   (sdcard)
  SSH live   /home/jesse/pods
             /home/jesse/openroot/pods
  SSH mirror /media/jesse/*/pods and /run/media/jesse/*/pods     (USB)

Policy:
  live   last-writer-wins, decided by _SYNC/state.json (prior hash vs current)
  mirror restore-from-live (live is authority)
  CONFLICT         true divergence — parked, never auto-merged, never overwritten
  CONFLICT_DELETED observed deletion — parked, never executed; human resolves

Exit codes: 0 clean | 1 copy/verify failures | 2 conflicts parked | 3 remote unreachable
Cross leg (A15 live to OptiPlex live over ssh) is owned by the A15 pane.
"""

import argparse
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

VERSION = "pods_sync v2.0 (4-site)"
TS = time.strftime("%Y%m%dT%H%M%S") + "-" + str(os.getpid())
BIG_DEFAULT = 64 * 1024 * 1024

A15_HOME = "/data/data/com.termux/files/home"
BOX_HOME = "/home/jesse"
SDCARD_PODS = "/storage/emulated/0/openroot/pods"
REMOTE_KEY = "/data/data/com.termux/files/home/.ssh/id_ed25519_optiplex"
REMOTE_SELF = "/home/jesse/openroot/bin/pods_sync.py"
REMOTE_LIVE_CANDIDATES = ["/home/jesse/pods", "/home/jesse/openroot/pods"]

MEANING = {0: "clean", 1: "copy/verify failures", 2: "conflicts parked (human gate)",
           3: "remote unreachable"}


def log(msg):
    print(msg, flush=True)


def q(s):
    return shlex.quote(s)


def sha256_file(path, chunk=1048576):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def detect_pane():
    if Path("/data/data/com.termux").exists():
        return "A15"
    if Path(BOX_HOME).exists():
        return "SSH"
    return None


def scan_root(root):
    files = {}
    rp = Path(root)
    if not rp.is_dir():
        return files
    for dirpath, dirnames, filenames in os.walk(rp):
        dirnames[:] = [d for d in dirnames if d not in ("_SYNC", ".stfolder")]
        for name in filenames:
            if ".sync_bak-" in name or name.startswith(".tmp-"):
                continue
            full = Path(dirpath) / name
            if not full.is_file():
                continue
            rel = full.relative_to(rp).as_posix()
            try:
                files[rel] = {"sha256": sha256_file(full), "size": full.stat().st_size}
            except OSError:
                files[rel] = {"sha256": "UNREADABLE", "size": 0}
    return files


def state_path(root):
    return Path(root) / "_SYNC" / "state.json"


def load_state(root):
    try:
        return json.loads(state_path(root).read_text())
    except Exception:
        return {}


def save_state(root, cur, prior, drop):
    merged = {k: v for k, v in prior.items() if k not in drop}
    for rel, meta in cur.items():
        merged[rel] = meta["sha256"]
    p = state_path(root).parent
    p.mkdir(parents=True, exist_ok=True)
    tmp = p / (".tmp-" + TS + "-state.json")
    tmp.write_text(json.dumps(merged, indent=1, sort_keys=True))
    os.replace(str(tmp), str(state_path(root)))
    return merged


def plan_pair(pname, policy, cur_a, cur_b, st_a, st_b):
    rows = []
    rels = sorted(set(cur_a) | set(cur_b) | set(st_a) | set(st_b))
    for rel in rels:
        in_a, in_b = rel in cur_a, rel in cur_b
        ha = cur_a[rel]["sha256"] if in_a else None
        hb = cur_b[rel]["sha256"] if in_b else None
        sa, sb = st_a.get(rel), st_b.get(rel)
        size = max(cur_a[rel]["size"] if in_a else 0,
                   cur_b[rel]["size"] if in_b else 0)
        if in_a and in_b:
            if ha == hb:
                action = "SAME"
            elif policy == "mirror":
                action = "UPDATE_B_FROM_A"
            else:
                a_cur, b_cur = (sa == ha), (sb == hb)
                if a_cur and b_cur:
                    action = "CONFLICT"
                elif a_cur:
                    action = "UPDATE_A_FROM_B"
                elif b_cur:
                    action = "UPDATE_B_FROM_A"
                else:
                    action = "CONFLICT"
        elif in_a or in_b:
            has, lacks = ("A", "B") if in_a else ("B", "A")
            lacks_state = sb if lacks == "B" else sa
            if lacks_state:
                action = "CONFLICT_DELETED_AT_" + lacks
            else:
                action = "ADD_" + has + "_TO_" + lacks
        else:
            action = "GONE_ALL_SITES"
        rows.append({"pair": pname, "policy": policy, "rel": rel,
                     "action": action, "size": size, "sha_a": ha, "sha_b": hb})
    return rows


def exec_row_local(row, root_a, root_b, big_bytes):
    act, rel = row["action"], row["rel"]
    if act in ("SAME", "GONE_ALL_SITES"):
        return "SKIP", {}
    if act.startswith("CONFLICT"):
        return "PARKED", {}
    if act in ("UPDATE_B_FROM_A", "ADD_A_TO_B"):
        src_root, dst_root = root_a, root_b
    elif act in ("UPDATE_A_FROM_B", "ADD_B_TO_A"):
        src_root, dst_root = root_b, root_a
    else:
        return "FAIL", {"why": "unknown action " + act}
    sp = Path(src_root) / rel
    dp = Path(dst_root) / rel
    if not sp.is_file():
        return "FAIL", {"why": "source vanished"}
    size = sp.stat().st_size
    if size > big_bytes:
        return "SKIP_BIG", {"bytes": size}
    try:
        free = shutil.disk_usage(str(dst_root)).free
    except OSError:
        free = 0
    if free < size * 1.2 + 1048576:
        return "SKIP_SPACE", {"free": free}
    dp.parent.mkdir(parents=True, exist_ok=True)
    backup = None
    if dp.exists():
        backup = str(dp) + ".sync_bak-" + TS
        try:
            shutil.copy2(str(dp), backup)
        except OSError as exc:
            return "FAIL", {"why": "backup failed: " + str(exc)}
    tmp = dp.parent / (".tmp-" + TS + "-" + dp.name)
    try:
        shutil.copy2(str(sp), str(tmp))
        os.replace(str(tmp), str(dp))
    except OSError as exc:
        try:
            tmp.unlink()
        except OSError:
            pass
        return "FAIL", {"why": str(exc)}
    if sha256_file(dp) != sha256_file(sp):
        return "FAIL", {"why": "sha mismatch after copy"}
    return "COPIED", {"bytes": size, "backup": backup}


def ssh_args(key, scp=False):
    base = ["scp" if scp else "ssh",
            "-o", "BatchMode=yes",
            "-o", "ConnectTimeout=8",
            "-o", "StrictHostKeyChecking=accept-new"]
    if key:
        base += ["-i", key]
    return base


def remote_run(spec, key, cmd, timeout=60):
    try:
        r = subprocess.run(ssh_args(key) + [spec, cmd],
                           capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout after " + str(timeout) + "s"
    except OSError as exc:
        return 125, "", str(exc)


def remote_candidates(override):
    if override:
        return [(override, None if override == "optiplex" else REMOTE_KEY)]
    return [("optiplex", None),
            ("jesse@192.168.1.193", REMOTE_KEY),
            ("jesse@100.122.169.43", REMOTE_KEY)]


def exec_cross(stats, exec_log, local_root, spec, key, remote_root,
               big_bytes, pre_local_state):
    fails = 0
    gone = set()
    rc0, out0, err0 = remote_run(spec, key,
                                 "python3 " + q(REMOTE_SELF) + " scan " + q(remote_root),
                                 120)
    if rc0 != 0:
        log("CROSS scan FAIL rc=" + str(rc0) + " " + err0.strip()[:120])
        return 1, set()
    rscan = json.loads(out0)
    cur_b, st_b = rscan.get("files", {}), rscan.get("state", {})
    free0 = rscan.get("free", 0)
    log("CROSS remote_root=" + remote_root +
        " remote_files=" + str(len(cur_b)) + " free=" + str(free0))
    cur_a = scan_root(local_root)
    rows = plan_pair("CROSS", "live", cur_a, cur_b, pre_local_state, st_b)
    pushed, pushed_bytes = [], 0
    for row in rows:
        act, rel = row["action"], row["rel"]
        if act == "SAME":
            continue
        if act == "GONE_ALL_SITES":
            gone.add(rel)
            row["result"] = "PURGED_STATE"
            exec_log.append(row)
            log("EXEC PURGED_STATE GONE_ALL_SITES CROSS " + rel)
            continue
        if act.startswith("CONFLICT"):
            row["result"] = "PARKED"
            exec_log.append(row)
            stats["parked"] += 1
            log("EXEC PARKED " + act + " CROSS " + rel)
            continue
        rpath = remote_root + "/" + rel
        rdir = remote_root + "/" + (rel.rsplit("/", 1)[0] if "/" in rel else "")
        if act in ("UPDATE_B_FROM_A", "ADD_A_TO_B"):
            sp = Path(local_root) / rel
            if not sp.is_file():
                row["result"] = "FAIL"
                exec_log.append(row)
                log("EXEC FAIL CROSS " + rel + " source vanished")
                fails += 1
                continue
            size = sp.stat().st_size
            if size > big_bytes:
                row["result"] = "SKIP_BIG"
                exec_log.append(row)
                stats["skip_big"] += 1
                log("EXEC SKIP_BIG " + act + " CROSS " + rel)
                continue
            want = sha256_file(sp)
            if pushed_bytes + size * 1.2 + 1048576 > free0:
                row["result"] = "SKIP_SPACE"
                exec_log.append(row)
                stats["skip_space"] += 1
                log("EXEC SKIP_SPACE " + act + " CROSS " + rel)
                continue
            rc = remote_run(spec, key, "mkdir -p " + q(rdir), 30)[0]
            tmp = rdir + "/.tmp-" + TS + "-" + rel.rsplit("/", 1)[-1]
            try:
                r2 = subprocess.run(ssh_args(key, scp=True) +
                                    [str(sp), spec + ":" + q(tmp)],
                                    capture_output=True, text=True, timeout=900)
                rc = r2.returncode
            except (subprocess.TimeoutExpired, OSError) as exc:
                rc, r2 = 125, None
                log("CROSS scp push error " + rel + " " + str(exc)[:80])
            if rc == 0:
                rc = remote_run(spec, key, "mv -f " + q(tmp) + " " + q(rpath), 60)[0]
            if rc != 0:
                remote_run(spec, key, "rm -f " + q(tmp), 30)
                row["result"] = "FAIL"
                exec_log.append(row)
                log("EXEC FAIL push CROSS " + rel)
                fails += 1
                continue
            pushed.append((rel, want))
            pushed_bytes += size
            row["result"] = "COPIED"
            row["extra"] = {"bytes": size, "dir": "push"}
            exec_log.append(row)
            stats["copied"] += 1
            stats["bytes"] += size
            log("EXEC COPIED " + act + " CROSS " + rel + " (push)")
        else:
            meta = cur_b.get(rel)
            if not meta or meta.get("sha256") in (None, "UNREADABLE"):
                row["result"] = "FAIL"
                exec_log.append(row)
                log("EXEC FAIL pull CROSS " + rel + " remote unreadable")
                fails += 1
                continue
            size = meta["size"]
            want = meta["sha256"]
            if size > big_bytes:
                row["result"] = "SKIP_BIG"
                exec_log.append(row)
                stats["skip_big"] += 1
                log("EXEC SKIP_BIG " + act + " CROSS " + rel)
                continue
            try:
                free = shutil.disk_usage(str(local_root)).free
            except OSError:
                free = 0
            if free < size * 1.2 + 1048576:
                row["result"] = "SKIP_SPACE"
                exec_log.append(row)
                stats["skip_space"] += 1
                log("EXEC SKIP_SPACE " + act + " CROSS " + rel)
                continue
            lp = Path(local_root) / rel
            lp.parent.mkdir(parents=True, exist_ok=True)
            backup = None
            if lp.exists():
                backup = str(lp) + ".sync_bak-" + TS
                shutil.copy2(str(lp), backup)
            tmp = lp.parent / (".tmp-" + TS + "-" + lp.name)
            try:
                r2 = subprocess.run(ssh_args(key, scp=True) +
                                    [spec + ":" + q(rpath), str(tmp)],
                                    capture_output=True, text=True, timeout=900)
                rc = r2.returncode
            except (subprocess.TimeoutExpired, OSError) as exc:
                rc, r2 = 125, None
                log("CROSS scp pull error " + rel + " " + str(exc)[:80])
            if rc != 0:
                row["result"] = "FAIL"
                exec_log.append(row)
                log("EXEC FAIL pull CROSS " + rel)
                fails += 1
                continue
            os.replace(str(tmp), str(lp))
            if sha256_file(lp) != want:
                row["result"] = "FAIL"
                exec_log.append(row)
                log("EXEC FAIL pull verify CROSS " + rel)
                fails += 1
                continue
            row["result"] = "COPIED"
            row["extra"] = {"bytes": size, "dir": "pull", "backup": backup}
            exec_log.append(row)
            stats["copied"] += 1
            stats["bytes"] += size
            if backup:
                stats["backups"] += 1
            log("EXEC COPIED " + act + " CROSS " + rel + " (pull)")
    if pushed:
        rc1, out1, err1 = remote_run(spec, key,
                                     "python3 " + q(REMOTE_SELF) + " scan " + q(remote_root),
                                     120)
        r2 = json.loads(out1) if rc1 == 0 else {}
        for rel, want in pushed:
            got = r2.get("files", {}).get(rel, {}).get("sha256")
            if got != want:
                log("EXEC FAIL push verify CROSS " + rel)
                fails += 1
    if gone:
        cmd = "python3 " + q(REMOTE_SELF) + " state-rebuild " + q(remote_root)
        cmd += " --drop " + q(",".join(sorted(gone)))
        remote_run(spec, key, cmd, 120)
    return fails, gone


def build_sites(args):
    pane = detect_pane()
    if args.root_live or args.root_mirror:
        lives = list(args.root_live)
        mirrors = list(args.root_mirror)
        for r in lives + mirrors:
            if not r.startswith("/"):
                return None, "REFUSE: root not absolute: " + r
        return {"pane": pane, "mode": "override", "lives": lives, "mirrors": mirrors,
                "remote": False, "notes": ["REMOTE: disabled (override roots)"]}, None
    if pane is None:
        return None, ("REFUSE: pane unknown (need A15 Termux or " + BOX_HOME +
                      "); or pass --root-live/--root-mirror (absolute)")
    if pane == "A15":
        lives = [A15_HOME + "/pods", A15_HOME + "/openroot/pods"]
        mirrors = [SDCARD_PODS]
    else:
        lives = [BOX_HOME + "/pods", BOX_HOME + "/openroot/pods"]
        mirrors = []
        for base in ("/media/jesse", "/run/media/jesse"):
            b = Path(base)
            if b.is_dir():
                for child in sorted(b.iterdir()):
                    if (child / "pods").is_dir():
                        mirrors.append(str(child / "pods"))
    notes = []
    if pane == "SSH" and not mirrors:
        notes.append("USB mirror: none mounted under /media/jesse or /run/media/jesse")
    return {"pane": pane, "mode": "auto", "lives": lives, "mirrors": mirrors,
            "remote": (pane == "A15") and not getattr(args, "no_remote", False),
            "notes": notes}, None


def cmd_run(args):
    t0 = time.time()
    ts = args.ts.replace("/", "-")
    sites, err = build_sites(args)
    if sites is None:
        log(err)
        return 2
    pane, lives, mirrors = sites["pane"], sites["lives"], sites["mirrors"]
    remote_enabled = sites["remote"]
    notes = list(sites["notes"])
    dedup = lambda xs: [x for i, x in enumerate(xs) if x not in xs[:i]]
    lives, mirrors = dedup(lives), dedup(mirrors)
    for r in lives:
        try:
            Path(r).mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            notes.append("ROOT FAIL " + r + " " + str(exc))
    keep = []
    for r in mirrors:
        try:
            Path(r).mkdir(parents=True, exist_ok=True)
            keep.append(r)
        except OSError as exc:
            notes.append("MIRROR ABSENT " + r + " (" + str(exc) + ")")
    mirrors = keep
    if not lives:
        log("REFUSE: no usable live roots")
        return 2
    log(VERSION + " pane=" + str(pane) + " mode=" + sites["mode"] + " ts=" + ts)
    pre = {r: scan_root(r) for r in lives + mirrors}
    for r in lives + mirrors:
        role = "live" if r in lives else "mirror"
        log("SITE " + role + " files=" + str(len(pre[r])) +
            " bytes=" + str(sum(m["size"] for m in pre[r].values())) +
            " state=" + str(len(load_state(r))) + " " + r)
    primary = lives[0]
    log("PRI = " + primary + " (stable: first live root)")
    for n in notes:
        log("NOTE " + n)
    run_dir = Path(primary) / "_SYNC" / "runs" / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    for i, r in enumerate(lives + mirrors):
        role = "live" if r in lives else "mirror"
        (run_dir / ("MANIFEST_" + str(i) + "_" + role + ".json")).write_text(
            json.dumps({"root": r, "role": role, "files": pre[r]},
                       indent=1, sort_keys=True))
    all_present = set()
    for r in lives + mirrors:
        all_present |= set(pre[r])
    pre_states = {r: load_state(r) for r in lives + mirrors}
    exec_log = []
    stats = {"copied": 0, "bytes": 0, "backups": 0, "skip_big": 0,
             "skip_space": 0, "fails": 0, "parked": 0}
    pairs = []
    for i in range(len(lives)):
        for j in range(i + 1, len(lives)):
            pairs.append(("L" + str(i) + "<->L" + str(j), lives[i], lives[j], "live"))
    for k, m in enumerate(mirrors):
        pairs.append(("PRI<->M" + str(k), primary, m, "mirror"))
    fails_total = conflict_total = 0
    seen_parked = set()
    for pass_no in (1, 2, 3):
        copied_this_pass = 0
        for pname, ra, rb, policy in pairs:
            cur_a, cur_b = scan_root(ra), scan_root(rb)
            st_a = {k: v for k, v in pre_states[ra].items() if k in all_present}
            st_b = {k: v for k, v in pre_states[rb].items() if k in all_present}
            for row in plan_pair(pname, policy, cur_a, cur_b, st_a, st_b):
                res, extra = exec_row_local(row, ra, rb, args.big_bytes)
                row["result"], row["extra"] = res, extra
                if res == "SKIP":
                    continue
                pkey = (row["pair"], row["rel"], row["action"])
                if res == "PARKED":
                    if pkey in seen_parked:
                        continue
                    seen_parked.add(pkey)
                if pass_no > 1:
                    row["extra"] = {**(extra if isinstance(extra, dict) else {}),
                                    "pass": pass_no}
                exec_log.append(row)
                suffix = ""
                if res == "COPIED":
                    copied_this_pass += 1
                    stats["copied"] += 1
                    stats["bytes"] += extra.get("bytes", 0)
                    if extra.get("backup"):
                        stats["backups"] += 1
                        suffix = " backup=" + extra["backup"]
                elif res == "SKIP_BIG":
                    stats["skip_big"] += 1
                elif res == "SKIP_SPACE":
                    stats["skip_space"] += 1
                elif res == "PARKED":
                    stats["parked"] += 1
                    conflict_total += 1
                elif res == "FAIL":
                    stats["fails"] += 1
                    fails_total += 1
                    suffix = " why=" + extra.get("why", "")
                log("EXEC " + res + " " + row["action"] + " " + pname + " " +
                    row["rel"] + suffix)
        if copied_this_pass == 0:
            break
    remote_line = "disabled"
    remote_attempted = False
    remote_ok = False
    if remote_enabled:
        cands = remote_candidates(args.remote_host)
        spec = key = None
        for c_spec, c_key in cands:
            rc, _, _ = remote_run(c_spec, c_key, "true", 15)
            if rc == 0:
                spec, key = c_spec, c_key
                break
        remote_attempted = True
        if spec is None:
            remote_line = "unreachable (" + ", ".join(c[0] for c in cands) + ")"
            notes.append("CROSS: no reachable host; local legs still receipted")
        else:
            remote_ok = True
            remote_line = spec
            log("CROSS host=" + spec)
            remote_run(spec, key, "mkdir -p " + q(Path(REMOTE_SELF).parent), 30)
            remote_run(spec, key,
                       "if test -f " + q(REMOTE_SELF) + "; then cp -f " +
                       "--preserve=timestamps " + q(REMOTE_SELF) + " " +
                       q(REMOTE_SELF + ".sync_bak-" + TS) + "; fi", 30)
            try:
                r2 = subprocess.run(ssh_args(key, scp=True) +
                                    [str(Path(__file__).resolve()),
                                     spec + ":" + q(REMOTE_SELF)],
                                    capture_output=True, text=True, timeout=300)
                if r2.returncode != 0:
                    notes.append("CROSS: self-deploy scp failed rc=" +
                                 str(r2.returncode))
            except (subprocess.TimeoutExpired, OSError) as exc:
                notes.append("CROSS: self-deploy error " + str(exc)[:80])
            rrc, rout, _ = remote_run(spec, key,
                                      "python3 " + q(REMOTE_SELF) +
                                      " run --no-remote", 600)
            (run_dir / "REMOTE_RUN.log").write_text(rout)
            if rrc != 0:
                notes.append("CROSS: remote internal run rc=" + str(rrc) +
                             " (see REMOTE_RUN.log)")
            rroot = None
            best = -1
            for cand in REMOTE_LIVE_CANDIDATES:
                rc3, out3, _ = remote_run(spec, key,
                                          "python3 " + q(REMOTE_SELF) +
                                          " scan " + q(cand), 120)
                if rc3 == 0:
                    n = len(json.loads(out3).get("files", {}))
                    if n > best:
                        best, rroot = n, cand
            if rroot is None:
                notes.append("CROSS: no remote live root scannable")
                fails_total += 1
            else:
                cf, cgone = exec_cross(stats, exec_log, primary, spec, key,
                                       rroot, args.big_bytes, pre_states[primary])
                fails_total += cf
                conflict_total += sum(1 for r in exec_log
                                      if r.get("result") == "PARKED"
                                      and r.get("pair") == "CROSS")
                if cgone:
                    notes.append("CROSS: purged remote state entries: " +
                                 ",".join(sorted(cgone)))
    post = {r: scan_root(r) for r in lives + mirrors}
    known = set()
    for r in lives + mirrors:
        known |= set(post[r])
    if remote_ok and remote_line != "unreachable":
        pass
    gone_rows = []
    for r in lives + mirrors:
        stale = set(pre_states[r]) - set(post[r]) - known
        if remote_enabled and remote_ok:
            pass
        save_state(r, post[r], pre_states[r], stale)
        for rel in sorted(stale):
            gone_rows.append({"pair": "STATE", "rel": rel,
                              "action": "GONE_ALL_SITES", "result": "PURGED_STATE"})
            log("EXEC PURGED_STATE GONE_ALL_SITES STATE " + r + " " + rel)
    exec_log.extend(gone_rows)
    self_sha = sha256_file(Path(__file__))
    pc = {"A15": Path(A15_HOME) / "openroot/bin/pathway_cache_v1.py",
          "SSH": Path(BOX_HOME) / "openroot/bin/pathway_cache_v1.py"}.get(pane)
    pathway = ("absent (seal by hand)" if not (pc and pc.exists())
               else "present at " + str(pc) + " (hand-seal this receipt)")
    L = []
    L.append("# PODS SYNC RECEIPT " + ts)
    L.append("- tool: " + VERSION + " sha256:" + self_sha)
    L.append("- pane: " + str(pane) + " mode: " + sites["mode"] +
             " primary: " + primary)
    L.append("- policy: live=LWW via _SYNC/state.json | mirror=restore-from-live"
             " | conflicts+deletions parked (human gate)")
    L.append("- remote: " + remote_line)
    for n in notes:
        L.append("- note: " + n)
    L.append("")
    L.append("## SITES")
    L.append("| role | files | bytes | state | root |")
    L.append("|---|---|---|---|---|")
    for r in lives + mirrors:
        role = "live" if r in lives else "mirror"
        L.append("| " + role + " | " + str(len(post[r])) + " | " +
                 str(sum(m["size"] for m in post[r].values())) + " | " +
                 str(len(load_state(r))) + " | " + r + " |")
    same_n = sum(1 for r in exec_log if r["action"] == "SAME")
    L.append("")
    L.append("## PLAN (" + str(same_n) + " SAME rows collapsed)")
    for row in exec_log:
        if row["action"] == "SAME":
            continue
        L.append("- " + row["action"] + " -> " + str(row.get("result")) +
                 " [" + row["pair"] + "] " + row["rel"])
    L.append("")
    L.append("## EXEC")
    L.append("copied=" + str(stats["copied"]) + " bytes=" + str(stats["bytes"]) +
             " backups=" + str(stats["backups"]) + " skip_big=" +
             str(stats["skip_big"]) + " skip_space=" + str(stats["skip_space"]) +
             " fails=" + str(stats["fails"]) + " parked=" + str(stats["parked"]))
    parked = [r for r in exec_log if r.get("result") == "PARKED"]
    if parked:
        L.append("")
        L.append("## CONFLICTS PARKED (human gate — never auto-merged)")
        for row in parked:
            L.append("- [" + row["pair"] + "] " + row["action"] + " " + row["rel"])
        L.append("- resolve: copy the keeper over the loser by hand, or delete the")
        L.append("  stale entry in <root>/_SYNC/state.json. A script never merges.")
    L.append("")
    L.append("## PATHWAY")
    L.append("- pathway_cache_v1.py: " + pathway)
    receipt_text = "\n".join(L) + "\n"
    (run_dir / "SYNC_RECEIPT.md").write_text(receipt_text)
    receipt_sha = sha256_file(run_dir / "SYNC_RECEIPT.md")
    (run_dir / "EXEC_LOG.json").write_text(
        json.dumps(exec_log, indent=1, sort_keys=True))
    stats["elapsed_s"] = round(time.time() - t0, 2)
    (run_dir / "STATS.json").write_text(json.dumps(stats, indent=1, sort_keys=True))
    ev = []
    for f in sorted(run_dir.iterdir()):
        if f.name == "EVIDENCE.sha256" or not f.is_file():
            continue
        ev.append(sha256_file(f) + "  " + f.name)
    (run_dir / "EVIDENCE.sha256").write_text("\n".join(ev) + "\n")
    log("")
    log(receipt_text.rstrip())
    log("- receipt sha256:" + receipt_sha)
    log("RUN_DIR " + str(run_dir))
    exit_code = 1 if fails_total else (2 if conflict_total else
                                       (3 if remote_attempted and not remote_ok
                                        else 0))
    log("EXIT: " + str(exit_code) + " (" + MEANING[exit_code] + ")")
    return exit_code


def cmd_scan(args):
    if not args.root.startswith("/"):
        log("REFUSE: root not absolute")
        return 2
    rp = Path(args.root)
    out = {"root": args.root, "files": scan_root(args.root),
           "state": load_state(args.root),
           "free": shutil.disk_usage(str(rp)).free if rp.exists() else 0}
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


def cmd_state_rebuild(args):
    if not args.root.startswith("/"):
        log("REFUSE: root not absolute")
        return 2
    prior = load_state(args.root)
    cur = scan_root(args.root)
    drop = set(x for x in args.drop.split(",") if x)
    merged = save_state(args.root, cur, prior, drop)
    log("state-rebuild " + args.root + " entries=" + str(len(merged)) +
        " dropped=" + str(len(drop)))
    return 0


def cmd_status(args):
    sites, err = build_sites(args)
    if sites is None:
        log(err)
        return 2
    log(VERSION + " pane=" + str(sites["pane"]) + " mode=" + sites["mode"])
    for r in sites["lives"] + sites["mirrors"]:
        role = "live" if r in sites["lives"] else "mirror"
        n = len(scan_root(r))
        last = ""
        runs = Path(r) / "_SYNC" / "runs"
        if runs.is_dir():
            names = sorted(p.name for p in runs.iterdir() if p.is_dir())
            if names:
                last = " last_run=" + names[-1]
        log("SITE " + role + " files=" + str(n) + " state=" +
            str(len(load_state(r))) + last + " " + r)
    for n in sites["notes"]:
        log("NOTE " + n)
    log("EXIT: 0 (clean)")
    return 0


def main():
    ap = argparse.ArgumentParser(prog="pods_sync.py", description=VERSION)
    sub = ap.add_subparsers(dest="cmd")
    rp = sub.add_parser("run", help="sync all sites on this pane (+cross from A15)")
    rp.add_argument("--root-live", action="append", default=[])
    rp.add_argument("--root-mirror", action="append", default=[])
    rp.add_argument("--big-bytes", type=int, default=BIG_DEFAULT)
    rp.add_argument("--no-remote", action="store_true")
    rp.add_argument("--remote-host", default=None)
    rp.add_argument("--ts", default=TS)
    sp = sub.add_parser("scan", help="print json manifest+state for one root")
    sp.add_argument("root")
    tp = sub.add_parser("state-rebuild",
                        help="merge current scan into state.json")
    tp.add_argument("root")
    tp.add_argument("--drop", default="")
    vp = sub.add_parser("status", help="short site table")
    vp.add_argument("--root-live", action="append", default=[])
    vp.add_argument("--root-mirror", action="append", default=[])
    args = ap.parse_args()
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "scan":
        return cmd_scan(args)
    if args.cmd == "state-rebuild":
        return cmd_state_rebuild(args)
    if args.cmd == "status":
        return cmd_status(args)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
