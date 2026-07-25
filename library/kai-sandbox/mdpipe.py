#!/data/data/com.termux/files/usr/bin/env python3
"""mdpipe v2: stdin or clipboard markdown → Groq structured yield."""
import os, sys, json, urllib.request, urllib.error, subprocess, datetime, time

HOME = '/data/data/com.termux/files/home' if os.path.exists('/data/data/com.termux/files/home') else os.environ.get('HOME') or '/root'
CLIP_GET = '/data/data/com.termux/files/usr/bin/termux-clipboard-get'
CLIP_SET = '/data/data/com.termux/files/usr/bin/termux-clipboard-set'

def main():
    input_md = ""
    if not sys.stdin.isatty():
        input_md = sys.stdin.read().strip()
    else:
        try: input_md = subprocess.check_output([CLIP_GET], text=True).strip()
        except: pass
    if not input_md:
        print("mdpipe: no input. Copy markdown to clipboard, then run: python3 $HOME/mdpipe.py"); return
    api_key = os.environ.get('GROQ_API_KEY') or ""
    if not api_key and os.path.exists(os.path.join(HOME, '.groq_api_key')):
        try:
            with open(os.path.join(HOME, '.groq_api_key')) as f: api_key = f.read().strip()
        except: pass
    if not api_key:
        print("GROQ_API_KEY missing. Run: echo 'sk-...' > $HOME/.groq_api_key && chmod 600 $HOME/.groq_api_key"); return
    payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": os.environ.get('MDPIPE_SYSTEM_PROMPT') or "You are GROK-NODE. Respond ONLY in exact ## ALIGN/## ASSESS/## ACT/## AMPLIFY format."}, {"role": "user", "content": input_md}], "max_tokens": 4096, "temperature": 0.15}
    try:
        req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=json.dumps(payload).encode(), headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=90) as resp:
            result = json.loads(resp.read().decode('utf-8'))
        content = result.get('choices', [{}])[0].get('message', {}).get('content', 'ERROR')
        print("\n=== mdpipe YIELD ===\n" + content + "\n=== END ===\n")
        try: time.sleep(0.3); subprocess.check_call([CLIP_SET, content]); print("[OK] Clipboard updated")
        except Exception as ce: print(f"[WARN] Clipboard failed ({ce}) — output visible above")
        log_dir = os.path.join(HOME, 'reports', 'mdpipe'); os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, 'log.md'), 'a') as f: f.write(f"\n### mdpipe {datetime.datetime.now().isoformat()}\n**In:** {input_md[:180]}...\n**Out:** {content[:180]}...\n---\n")
        print("Logged to reports/mdpipe/log.md")
    except Exception as e:
        print(f"mdpipe ERROR: {str(e)[:300]}"); log_dir = os.path.join(HOME, 'reports', 'mdpipe'); os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, 'log.md'), 'a') as f: f.write(f"\n### mdpipe FAILURE {datetime.datetime.now().isoformat()}\n{str(e)}\n---\n")

if __name__ == "__main__": main()
