#!/usr/bin/env python3
# master_harvest_v3_20260920.py — READ-ONLY. Classify compare failures, bank master head
# SHAs, hunt openroot master for the lost "todo automation v2.0" commit. Mutates NOTHING.
import json, os, subprocess, sys, datetime, hashlib, pathlib
OPENROOT = "/home/jesse/openroot"
STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
os.chdir(OPENROOT)
print("[canary] OPENROOT-master-harvest-v3-20260920 paste intact")
def gh_raw(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True)
def gh_api(endpoint):
    r = gh_raw("api", endpoint)
    if r.returncode != 0:
        return None, r.stderr.strip()
    try:
        return json.loads(r.stdout), None
    except json.JSONDecodeError:
        return None, "non-json: " + r.stdout.strip()[:120]
report = []
def say(m):
    print(m); report.append(m)
say("== STAGE A [classify] why did compare fail? ==")
repos = json.loads(subprocess.run(["gh","repo","list","jesseray718","--limit","300","--json",
    "nameWithOwner,isFork,defaultBranchRef"],capture_output=True,text=True).stdout)
owned = [r for r in repos if not r["isFork"]]
ledger = {}
no_common, no_history, other_err, ok_clean = [], [], [], []
for r in owned:
    repo = r["nameWithOwner"]; default = (r.get("defaultBranchRef") or {}).get("name","") or "main"
    br, _ = gh_api(f"repos/{repo}/branches/master")
    if br is None:
        continue
    head_sha = br["commit"]["sha"]
    ledger[repo] = {"master_head": head_sha, "default": default}
    if default == "master":
        continue  # rename-path repos, already classified
    cmp_, err = gh_api(f"repos/{repo}/compare/{default}...master")
    if cmp_ is not None:
        ok_clean.append((repo, cmp_.get("ahead_by"), cmp_.get("behind_by")))
        say(f"[banked] {repo}: compare OK — master ahead={cmp_.get('ahead_by')} behind={cmp_.get('behind_by')}")
    else:
        el = err.lower()
        if "no common ancestor" in el:
            no_common.append(repo); say(f"[held] {repo}: UNRELATED HISTORY — master is a pre-prune zombie")
        elif "not found" in el or "no history" in el or "404" in el:
            no_history.append(repo); say(f"[held] {repo}: SHAs gone — master head dangling: {head_sha[:8]}")
        else:
            other_err.append(repo); say(f"[held] {repo}: OTHER ERROR :: {err[:140]}")
ledger_path = pathlib.Path(OPENROOT, f"data/master_heads_ledger_{STAMP}.json")
ledger_path.write_text(json.dumps(ledger, indent=2))
say(f"[banked] master-head ledger sealed ({len(ledger)} repos): {ledger_path}")
say(f"[gate] tally: unrelated-history={len(no_common)} dangling={len(no_history)} other={len(other_err)} clean={len(ok_clean)}")

say("== STAGE B [harvest] openroot master — lost todo-v2.0 hunt ==")
ocm, err = gh_api("repos/jesseray718/openroot/commits?sha=master&per_page=100")
if ocm is None:
    say(f"[held] cannot list openroot master commits :: {err[:140]}")
else:
    hits = [c for c in ocm if "todo" in c["commit"]["message"].lower()]
    say(f"[banked] openroot master: {len(ocm)} commits reachable (first 100); {len(hits)} mention 'todo'")
    for c in hits[:10]:
        say(f"    HIT {c['sha'][:8]} :: {c['commit']['message'].splitlines()[0][:110]}")
    say(f"[banked] master tip: {ocm[0]['sha'][:8]} :: {ocm[0]['commit']['message'].splitlines()[0][:110]}" if ocm else "[held] master unreachable")
# fetch file tree at openroot master tip, look for GOALS/MASTER_TODO variants
tip, terr = gh_api("repos/jesseray718/openroot/git/trees/master?recursive=0")
if tip is not None:
    wanted = [e["path"] for e in tip.get("tree",[])
              if e["path"].upper() in ("GOALS.MD","MASTER_TODO.MD","TASK.MD")
              or "TODO" in e["path"].upper() or "GOALS" in e["path"].upper()]
    say(f"[banked] openroot master tip tree: {wanted or 'no GOALS/TODO files found at tip'}")
    for path in wanted:
        blob, berr = gh_api(f"repos/jesseray718/openroot/contents/{path}?ref=master")
        if blob and isinstance(blob, dict) and blob.get("download_url"):
            dl = subprocess.run(["curl","-sSL",blob["download_url"]],capture_output=True,text=True)
            if dl.returncode == 0 and dl.stdout:
                out = pathlib.Path(OPENROOT, "context_bridge", f"recovered_{path}.master_{STAMP}")
                out.write_text(dl.stdout)
                say(f"[banked] RECOVERED {path} from master -> {out} (sha256={hashlib.sha256(dl.stdout.encode()).hexdigest()[:16]}, {len(dl.stdout.splitlines())} lines)")
else:
    say(f"[held] master tip tree fetch failed :: {(terr or '')[:140]}")

say("== STAGE C [inspect] on-disk GOALS/MASTER_TODO/TASK heads ==")
for f in ["GOALS.md","MASTER_TODO.md","TASK.md"]:
    p = pathlib.Path(OPENROOT, f)
    if p.exists():
        lines = p.read_text(errors="ignore").splitlines()
        say(f"[banked] {f}: {len(lines)} lines :: first-task-lines:")
        for l in [x for x in lines if x.strip().startswith(("-","*","1"))][:8]:
            say(f"    {l.strip()[:110]}")

rep = pathlib.Path(OPENROOT, "context_bridge", f"report-master-harvest-{STAMP}.md")
rep.write_text("\n".join(report) + f"\n\n## Handoff {STAMP}\nmode=READ-ONLY-DIAGNOSTIC\n"
    f"unrelated={len(no_common)} dangling={len(no_history)} other={len(other_err)} clean={len(ok_clean)}\n"
    "next: IF openroot master contains GOALS/MASTER_TODO or todo-v2.0 commit -> harvest before ANY master deletion\n"
    "THEN deletion pass becomes safe (ledger records every head SHA for rollback archaeology)\n")
print(f"[banked] report sealed: {rep}")
print("[exit=0]")
