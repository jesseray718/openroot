#!/data/data/com.termux/files/usr/bin/env python3
"""mdpipe: stdin or clipboard markdown -> Groq structured yield (ALIGN/ASSESS/ACT/AMPLIFY)."""
import os
import sys
import json
import urllib.request
import urllib.error
import subprocess
import datetime

HOME = os.environ.get('HOME') or '/data/data/com.termux/files/home'

def log_failure(input_preview, err):
    log_dir = os.path.join(HOME, 'reports', 'mdpipe')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'log.md')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n\n### mdpipe FAILURE {datetime.datetime.now().isoformat()}\n**Input preview:** {input_preview[:180].replace(chr(10), ' ')}...\n**Error:** {err[:300]}\n---\n")

def main():
    if not sys.stdin.isatty():
        input_md = sys.stdin.read().strip()
    else:
        try:
            input_md = subprocess.check_output(['termux-clipboard-get'], text=True).strip()
        except Exception:
            input_md = ""
    if not input_md:
        msg = "mdpipe: no input. Pipe markdown or set clipboard first."
        print(msg)
        try:
            subprocess.check_call(['termux-clipboard-set', msg])
        except:
            pass
        return

    system_prompt = os.environ.get('MDPIPE_SYSTEM_PROMPT') or """You are GROK-NODE in the OpenRoot ecosystem. MAXIMUM SYSTEMIC BENEFIT PER UNIT OF HUMAN EFFORT.
Respond ONLY in exact format below. No other text. Terminal-native. Highest density.

## ALIGN
[one sentence]

## ASSESS
[metrics, edge cases, confidence 0-100, assumptions flagged, dissent if swarm]

## ACT
[paste-ready atomic command or code block.]

## AMPLIFY
[how this compounds future infrastructure]"""

    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        err = "GROQ_API_KEY not set. Run: export GROQ_API_KEY=sk-... then re-run mdpipe."
        print(err)
        try:
            subprocess.check_call(['termux-clipboard-set', err])
        except:
            pass
        return

    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_md}
        ],
        "max_tokens": 4096,
        "temperature": 0.15,
        "top_p": 0.9
    }
    data = json.dumps(payload).encode('utf-8')
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json"
    }

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=90) as resp:
            result = json.loads(resp.read().decode('utf-8'))
        if 'error' in result:
            content = "## ALIGN\nGroq API error self-regulated.\n\n## ASSESS\n" + str(result['error']) + "\n\n## ACT\nCheck key validity, quota, network.\n\n## AMPLIFY\nError logged."
        elif 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
        else:
            content = "## ALIGN\nUnexpected Groq response.\n\n## ASSESS\nRaw: " + str(result)[:500] + "\n\n## ACT\nDebug payload or switch model.\n\n## AMPLIFY\nThis iteration improves swarm resilience."
        subprocess.check_call(['termux-clipboard-set', content])
        log_dir = os.path.join(HOME, 'reports', 'mdpipe')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'log.md')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write("\n\n### mdpipe Run " + datetime.datetime.now().isoformat() + "\n**Input preview:** " + input_md[:180].replace('\n', ' ') + "...\n**Output preview:** " + content[:180].replace('\n', ' ') + "...\n---\n")
        print("mdpipe: yield obtained.")
    except urllib.error.HTTPError as e:
        err = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
        error_msg = "## ALIGN\nHTTP error in Groq call.\n\n## ASSESS\n" + err[:300] + "\nInput preview: " + input_md[:100] + "\n\n## ACT\nVerify key, internet, rate limits.\n\n## AMPLIFY\nFailure queued."
        try:
            subprocess.check_call(['termux-clipboard-set', error_msg])
        except:
            pass
        log_failure(input_md[:100], err)
        print("mdpipe HTTP error:", err[:200])
    except Exception as e:
        error_msg = "## ALIGN\nPipeline exception self-regulated.\n\n## ASSESS\nError: " + str(e) + "\n\n## ACT\nCheck termux-clipboard, python3, network.\n\n## AMPLIFY\nQueued to mdpipe log."
        try:
            subprocess.check_call(['termux-clipboard-set', error_msg])
        except:
            pass
        log_failure(input_md[:100], str(e))
        print("mdpipe error:", str(e)[:200])

if __name__ == "__main__":
    main()
