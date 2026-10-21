#!/data/data/com.termux/files/usr/bin/python3
"""
mdpipe.py — clipboard → LLM → clipboard
Groq-first, local fallback (llama-server on :9999), auto-log failures
"""
import os, sys, json, requests, datetime, subprocess
from pathlib import Path

HOME = os.environ.get('HOME', str(Path.home()))
QUEUE_FILE = f"{HOME}/reports/lumo-queue.md"
LOG_DIR = f"{HOME}/reports/mdpipe"

def rep(msg):
    """Append failure to lumo-queue.md"""
    try:
        os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
        hostname = subprocess.check_output(['hostname'], text=True).strip()
        ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        line = f"## {ts} | {hostname}\n> {msg}\n\n"
        with open(QUEUE_FILE, "a") as f:
            f.write(line)
    except Exception as e:
        print(f"[rep()] failed: {e}", file=sys.stderr)

def log(msg):
    """Write to mdpipe log"""
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        with open(f"{LOG_DIR}/log.md", "a") as f:
            f.write(f"{ts} | {msg}\n")
    except: pass

def groq_request(prompt, key):
    """Call Groq API"""
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 2048
    }
    resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=30)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']

def local_request(prompt):
    """Call local llama-server on :9999"""
    data = {
        "model": "local",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 2048
    }
    resp = requests.post("http://127.0.0.1:9999/v1/chat/completions", json=data, timeout=60)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']

def main():
    # Read from stdin or clipboard
    if sys.stdin.isatty():
        try:
            prompt = subprocess.check_output(['termux-clipboard-get'], text=True).strip()
        except Exception as e:
            rep(f"clipboard-get failed: {e}")
            print("Error: No input provided. Pipe markdown or copy to clipboard.")
            sys.exit(1)
    else:
        prompt = sys.stdin.read().strip()
    
    if not prompt:
        rep("Empty input received")
        sys.exit(1)
    
    groq_key = os.environ.get('GROQ_API_KEY')
    force_local = os.environ.get('MDPIPE_LOCAL') == '1'
    
    # Route: Groq → Local fallback
    try:
        if groq_key and not force_local:
            log("Routing: Groq")
            result = groq_request(prompt, groq_key)
        else:
            if not force_local:
                log("Groq key missing/unset, routing: Local")
            else:
                log("Forced local mode")
            result = local_request(prompt)
    except Exception as e:
        rep(f"Inference failed: {e}")
        log(f"ERROR: {e}")
        print(f"Error: Pipeline failure. Check {QUEUE_FILE}")
        sys.exit(1)
    
    # Write to clipboard
    try:
        p = subprocess.Popen(['termux-clipboard-set'], stdin=subprocess.PIPE)
        p.communicate(input=result.encode())
        log("Success: Output sent to clipboard")
    except Exception as e:
        rep(f"clipboard-set failed: {e}")
        print(f"Warning: Could not set clipboard: {e}")
        print(result)  # Fallback to stdout

if __name__ == "__main__":
    main()
