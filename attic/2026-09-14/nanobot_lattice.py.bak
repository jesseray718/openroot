#!/usr/bin/env python3
"""
FRACTAL NANOBOT LATTICE
6 base units, recursive squaring composition.
Built by Jesse Ray. Reconstructed 2026-07-16.
"""
import json, asyncio, os, sys, urllib.request

def get_api_key():
    k = os.environ.get("GROQ_API_KEY", "")
    if k and not k.startswith("YOUR_"):
        return k
    for p in ["~/.groq_api_key", "~/.config/groq_env"]:
        p = os.path.expanduser(p)
        if os.path.exists(p):
            v = open(p).read().strip()
            if "GROQ_API_KEY=" in v:
                return v.split("=",1)[1].strip().strip('"').strip("'")
            return v
    return None

API_KEY = get_api_key()

async def call_llm(prompt: str, system: str = "") -> str:
    if API_KEY:
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps({
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                "max_tokens": 1024,
            }).encode(),
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[LLM] API failed: {e}, using stub", file=sys.stderr)
    return f"[stub:{system[:20]}] {prompt[:80]}..."

async def nb_translate(ctx):
    ctx['translate'] = await call_llm(f"Translate into clear plain meaning:\n{ctx.get('input','')}", "You are a translator between languages, domains, and abstraction levels.")
    return ctx

async def nb_analyze(ctx):
    ctx['analyze'] = await call_llm(f"Analyze structure and key components of:\n{ctx.get('input','')}", "You are an analyst. Decompose into parts, relationships, patterns.")
    return ctx

async def nb_feedback(ctx):
    pieces = {k: v for k, v in ctx.items() if k != 'input'}
    ctx['feedback'] = await call_llm(f"Evaluate for completeness and coherence. Flag gaps:\n{json.dumps(pieces)}", "You are a feedback loop monitor. Detect gaps, redundancies, circular logic.")
    return ctx

async def nb_synthesize(ctx):
    pieces = {k: v for k, v in ctx.items() if k not in ('input',)}
    ctx['synthesize'] = await call_llm(f"Synthesize into one unified answer:\n{json.dumps(pieces)}", "You are a synthesizer. Merge multiple perspectives into one coherent whole.")
    return ctx

async def nb_validate(ctx):
    ctx['validate'] = await call_llm(f"Original: {ctx.get('input','')}\nSynthesis: {ctx.get('synthesize','')}\nDoes synthesis faithfully represent original? Flag distortions.", "You are a validator. Check fidelity between source and output.")
    return ctx

async def nb_amplify(ctx):
    src = ctx.get('validate', '') + '\n' + ctx.get('synthesize', '')
    ctx['amplify'] = await call_llm(f"Amplify this insight. Sharpen, deepen, make actionable:\n{src}", "You are an amplifier. Enhance clarity, depth, and impact without distortion.")
    return ctx

BASE = [nb_translate, nb_analyze, nb_feedback, nb_synthesize, nb_validate, nb_amplify]

async def fractal(ctx, level, max_depth):
    if level >= max_depth:
        return ctx
    if level == 0:
        results = await asyncio.gather(*[nb(ctx.copy()) for nb in BASE])
    else:
        results = await asyncio.gather(*[fractal(ctx.copy(), level - 1, max_depth) for _ in range(6)])
    merged = {'input': ctx.get('input', ''), 'level': level}
    for r in results:
        for k, v in r.items():
            if k in merged and isinstance(merged[k], str) and isinstance(v, str):
                merged[k] = merged[k] + "\n---\n" + v
            elif k not in merged:
                merged[k] = v
            else:
                merged[k] = str(merged[k]) + "\n---\n" + str(v)
    return merged

async def run(query, depth=6):
    nodes = 6 ** (2 ** depth) if depth > 0 else 6
    print(f"\n{'='*60}\nFRACTAL NANOBOT LATTICE\nDepth: {depth} | Theoretical nodes: 6^(2^{depth}) = {nodes:.2e}\n{'='*60}\n")
    result = await fractal({'input': query}, depth - 1, depth)
    print(f"\n{'='*60}\nMETA OUTPUT (top of lattice)\n{'='*60}")
    print(result.get('amplify', result.get('synthesize', json.dumps(result, indent=2, default=str))))
    return result

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "What is the relationship between permaculture principles and recursive AI architecture?"
    d = int(os.environ.get("DEPTH", "2"))  # Default depth=2 for testing
    asyncio.run(run(q, depth=d))
