#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# [GRADEGUARDV1] Grader format-drift guard + retry harness — canary marker
"""
grade_guard.py — kills the '3B regurgitates instead of grading' bug.

Contract enforced from grader models:
    Line 1: VERDICT: PASS  or  VERDICT: FAIL   (case-insensitive)
    Line 2+: brief justification, <= MAX_JUST chars

Failure modes detected:
    - missing/malformed verdict token
    - verdict line not first
    - excessive length (regurgitation signature)
    - echo: >ECHO_FRAC of response copies graded-content substrings

Retry policy: up to RETRIES firmer re-prompts; final failure returns
('ERROR', raw) so callers escalate (never accept a bad grade silently).

Integration (solve.py grader section, AFTER human-gated audit):
    from grade_guard import grade_guarded
    verdict, detail = grade_guarded(call_grader_fn, task, candidate)

call_grader_fn(prompt) -> str  : your existing Ollama call, unchanged.
"""
import re, sys

CANARY = "[GRADEGUARDV1]"
VERDICT_RE = re.compile(r"^\s*VERDICT\s*:\s*(PASS|FAIL)\b", re.IGNORECASE)
MAX_JUST = 600          # justifications longer than this smell like regurgitation
MAX_TOTAL = 1200
ECHO_FRAC = 0.6         # >60% of content-words echoed = regurgitation
RETRIES = 2

CONTRACT = (
    "CRITICAL OUTPUT CONTRACT — violations are discarded and you will be re-asked:\n"
    "Your FIRST line must be exactly one of:\n"
    "    VERDICT: PASS\n"
    "    VERDICT: FAIL\n"
    "Then at most a few sentences of justification. Do NOT repeat the code or\n"
    "content you were given. Grade it; do not echo it.\n"
)

STRICTER = (
    "Your previous response violated the contract (bad verdict line, or you "
    "copied content instead of judging it). Respond NOW with first line "
    "'VERDICT: PASS' or 'VERDICT: FAIL' followed by a SHORT justification. "
    "Do not repeat any content from the material under review."
)

def _echo_fraction(response: str, content: str) -> float:
    """Fraction of response words appearing verbatim in content."""
    if not content:
        return 0.0
    cw = set(re.findall(r"\w+", content.lower()))
    if not cw:
        return 0.0
    rw = re.findall(r"\w+", response.lower())
    if not rw:
        return 0.0
    hit = sum(1 for w in rw if w in cw)
    return hit / len(rw)

def parse_grade(response: str, content: str = ""):
    """Parse + validate. Returns (verdict, reason) — verdict in
    {'PASS','FAIL'} on success, 'ERROR' + reason on contract violation."""
    resp = (response or "").strip()
    m = VERDICT_RE.match(resp)
    if not m:
        return "ERROR", "missing-or-malformed verdict line"
    if len(resp) > MAX_TOTAL:
        return "ERROR", f"response too long ({len(resp)}>{MAX_TOTAL}) — regurgitation"
    body = resp[m.end():].strip()
    if len(body) > MAX_JUST:
        return "ERROR", f"justification too long ({len(body)}>{MAX_JUST})"
    if content and _echo_fraction(body, content) > ECHO_FRAC:
        return "ERROR", f"echo fraction >{ECHO_FRAC:.0%} — content regurgitated"
    return m.group(1).upper(), body or "(no justification given)"

def grade_guarded(call_fn, task: str, candidate: str):
    """
    call_fn(prompt) -> str: existing grader call (your Ollama invocation).
    Retries with firmer prompts on contract violations.
    Returns (verdict, raw_response_or_detail). Verdict 'ERROR' = escalate.
    """
    base_prompt = (
        f"{CONTRACT}\n--- TASK ---\n{task[:2000]}\n"
        f"--- CANDIDATE UNDER REVIEW ---\n{candidate[:6000]}\n"
    )
    prompt = base_prompt
    for attempt in range(RETRIES + 1):
        try:
            resp = call_fn(prompt)
        except Exception as e:
            return "ERROR", f"grader call failed: {e}"
        verdict, reason = parse_grade(resp, candidate)
        if verdict != "ERROR":
            return verdict, reason
        print(f"{CANARY} attempt {attempt+1} rejected: {reason}")
        prompt = f"{STRICTER}\n\n{base_prompt}"
    return "ERROR", "contract never satisfied after retries — escalate"

def _smoke():
    ok = 0
    # 1: clean pass verdict
    v, _ = parse_grade("VERDICT: PASS\nhandles empty input correctly.")
    assert v == "PASS", "clean pass failed"; ok += 1
    # 2: clean fail verdict
    v, _ = parse_grade("verdict: FAIL\nregex is greedy, breaks paths.")
    assert v == "FAIL", "clean fail failed"; ok += 1
    # 3: missing verdict (classic regurgitation)
    content = "def fix(): return parse(this) or that thing here now"
    v, r = parse_grade(f"The code {content}", content)
    assert v == "ERROR", "missing-verdict not caught"; ok += 1
    # 4: echo detection — verdict fine, body copies content
    v, r = parse_grade("VERDICT: FAIL\ndef fix(): return parse(this) or that thing here now",
                       content)
    assert v == "ERROR" and "echo" in r, "echo not caught"; ok += 1
    # 5: retry loop reaches ERROR after firmer re-prompts
    bad_fn = lambda p: "sure! here is the code you wanted:\ndef x(): pass"
    v, _ = grade_guarded(bad_fn, "test task", "test candidate")
    assert v == "ERROR", "retry exhaustion failed"; ok += 1
    # 6: good recovery on 2nd attempt
    calls = {"n": 0}
    def flaky(p):
        calls["n"] += 1
        return "here's the code!" if calls["n"] == 1 else "VERDICT: PASS\nok"
    v, _ = grade_guarded(flaky, "t", "c")
    assert v == "PASS", "recovery-after-retry failed"; ok += 1
    print(f"{CANARY} SMOKE PASS {ok}/6: verdict parse, case-fold, missing-verdict, "
          "echo, retry-exhaustion, recovery-on-retry")
    return 0

if __name__ == "__main__":
    sys.exit(_smoke())
