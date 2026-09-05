#!/usr/bin/env python3
import json
import subprocess
import urllib.request
from pathlib import Path

LLAMA_URL = "http://127.0.0.1:8080/v1/chat/completions"
MODEL_NAME = "qwen2.5-coder-7b"
OUTPUT_DIR = Path("/home/jesse/openroot/reports/pr_fixes")

def run_cmd(cmd, cwd=None):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def ask_local_coder(prompt):
    payload = json.dumps({
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are qwen2.5-coder-7b on optiplex3060. Output executable bash or python scripts only without markdown wrapper."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 1024
    }).encode("utf-8")
    
    req = urllib.request.Request(LLAMA_URL, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"# Error contacting local 7B coder on 127.0.0.1:8080: {e}"

def audit_and_merge_prs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    repos_raw, _, _ = run_cmd("gh repo list jesseray718 --limit 50 --json name")
    if not repos_raw:
        print("[!] No repos returned from gh CLI or gh not authenticated.")
        return

    repos = json.loads(repos_raw)
    
    for repo_obj in repos:
        repo = f"jesseray718/{repo_obj['name']}"
        print(f"[*] Auditing PRs for {repo}...")
        
        prs_raw, _, _ = run_cmd(f"gh pr list --repo {repo} --json number,title,headRefName,statusCheckRollup,mergeable")
        if not prs_raw or prs_raw == "[]":
            continue
            
        prs = json.loads(prs_raw)
        for pr in prs:
            num = pr["number"]
            title = pr["title"]
            branch = pr["headRefName"]
            
            checks = pr.get("statusCheckRollup", [])
            all_green = len(checks) > 0 and all(c.get("state") in ["SUCCESS", "COMPLETED"] or c.get("conclusion") == "SUCCESS" for c in checks)
            can_merge = pr.get("mergeable") == "MERGEABLE"
            
            if all_green and can_merge:
                print(f"  [+] Merging PR #{num} ({title})...")
                run_cmd(f"gh pr merge {num} --repo {repo} --squash --delete-branch")
            else:
                print(f"  [!] PR #{num} blocked/failing. Escalating to 7B Coder on OptiPlex...")
                diff_out, _, _ = run_cmd(f"gh pr diff {num} --repo {repo}")
                
                prompt = (
                    f"PR #{num} '{title}' in {repo} on branch '{branch}' needs resolution.\n"
                    f"Check status: {json.dumps(checks)}\n"
                    f"Diff snippet:\n{diff_out[:1500]}\n\n"
                    f"Write a standalone script to fix issues, commit, and push to {branch}."
                )
                
                fix_script = ask_local_coder(prompt)
                script_path = OUTPUT_DIR / f"{repo_obj['name']}_pr_{num}_fix.sh"
                script_path.write_text(fix_script)
                print(f"  [->] Suggested fix script saved to {script_path}")

if __name__ == "__main__":
    audit_and_merge_prs()
