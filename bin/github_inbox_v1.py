# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""OpenRoot GitHub CI/CD Inbox v1 - polls Actions status, surfaces failures."""
import argparse, json, os, subprocess, sys, time
from pathlib import Path

REPO = Path(os.environ.get("OPENROOT_REPO", "/home/jesse/openroot"))
INBOX = REPO / "data" / "github_inbox.jsonl"
STATE = REPO / "data" / "github_inbox_state.json"

def gh_api(endpoint):
    """Call GitHub API via gh CLI (handles auth)."""
    r = subprocess.run(
        ["gh", "api", endpoint],
        capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        return None, r.stderr
    try:
        return json.loads(r.stdout), None
    except:
        return None, "parse_error"

def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"seen_runs": [], "last_check": None}

def save_state(state):
    STATE.write_text(json.dumps(state, indent=2))

def poll_repos(repos, poll_window_minutes=30):
    """Poll recent workflow runs for given repos. Surface new failures."""
    state = load_state()
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    state["last_check"] = now
    
    new_events = []
    for repo in repos:
        # Get recent runs (last 30 min by default)
        runs, err = gh_api(f"repos/{repo}/actions/runs?per_page=10")
        if not runs:
            continue
        for run in runs.get("workflow_runs", [])[:10]:
            run_id = run["id"]
            if run_id in state["seen_runs"]:
                continue
            state["seen_runs"].append(run_id)
            # Keep only last 200 seen runs
            if len(state["seen_runs"]) > 200:
                state["seen_runs"] = state["seen_runs"][-200:]
            
            conclusion = run.get("conclusion")
            status = run.get("status")
            event = {
                "ts": now,
                "repo": repo,
                "run_id": run_id,
                "workflow": run.get("name", "?"),
                "branch": run.get("head_branch", "?"),
                "status": status,
                "conclusion": conclusion,
                "html_url": run.get("html_url"),
                "event_type": "ci_failure" if conclusion == "failure" else "ci_event",
            }
            new_events.append(event)
    
    # Append to inbox
    with open(INBOX, "a") as f:
        for ev in new_events:
            f.write(json.dumps(ev) + "\n")
    
    save_state(state)
    return new_events

def show_inbox(n=10, failures_only=False):
    """Print recent inbox entries."""
    if not INBOX.exists():
        print("  [held] no inbox yet")
        return
    lines = INBOX.read_text().strip().split("\n")
    if failures_only:
        lines = [l for l in lines if json.loads(l).get("conclusion") == "failure"]
    for line in lines[-n:]:
        ev = json.loads(line)
        marker = "FAIL" if ev.get("conclusion") == "failure" else "OK  "
        print(f"  [{marker}] {ev['ts'][:19]} {ev['repo']} #{ev['run_id']} {ev['workflow']}")

def main():
    p = argparse.ArgumentParser(description="OpenRoot GitHub CI/CD Inbox v1")
    p.add_argument("--poll", action="store_true", help="poll for new events")
    p.add_argument("--repos", nargs="+", default=["jesseray718/openroot"])
    p.add_argument("--show", action="store_true", help="show recent inbox")
    p.add_argument("--failures", action="store_true", help="show failures only")
    p.add_argument("--n", type=int, default=10)
    args = p.parse_args()
    
    print(f"[gate] CANARY:OPENROOT-GITHUB-INBOX-V1", file=sys.stderr)
    
    if args.poll:
        events = poll_repos(args.repos)
        print(f"[banked] polled {len(args.repos)} repos, {len(events)} new events", file=sys.stderr)
        for ev in events:
            if ev["event_type"] == "ci_failure":
                print(f"  [FAIL] {ev['repo']} #{ev['run_id']} {ev['workflow']}", file=sys.stderr)
                print(f"         {ev['html_url']}", file=sys.stderr)
    elif args.show:
        show_inbox(args.n, args.failures)
    else:
        print("Specify --poll or --show")

if __name__ == "__main__":
    main()
