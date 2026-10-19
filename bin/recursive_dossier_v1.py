#!/usr/bin/env python3
"""OpenRoot Recursive Dossier v1 - ReAct loop integrating dossier_engine + cloud_router."""
import argparse, json, os, re, subprocess, sys, time, hashlib
from pathlib import Path

REPO = Path(os.environ.get("OPENROOT_REPO", "/home/jesse/openroot"))
CANARY = "CANARY:OPENROOT-RECURSIVE-DOSSIER-V1"

def log(msg, level="gate"):
    print(f"[{level}] {msg}", file=sys.stderr)

def extract_keywords(question, max_keywords=8):
    """Extract keywords from a question for FTS5 query."""
    stop = {"the","a","an","is","are","was","were","what","how","why","when","where","which","do","does","did","can","could","should","would","will","to","of","in","on","at","for","with","by","and","or","but","not","this","that","these","those","i","you","we","they","it"}
    words = re.findall(r'[a-zA-Z_][a-zA-Z0-9_-]{2,}', question.lower())
    kws = [w for w in words if w not in stop and len(w) > 2]
    # unique preserving order
    seen = set()
    kws = [w for w in kws if not (w in seen or seen.add(w))]
    return kws[:max_keywords]

def build_fts_query(keywords):
    """Convert keyword list to FTS5 OR query."""
    return " ".join(keywords)

def run_dossier(pods, query, top_k=18, budget=8000):
    """Call the existing dossier_engine_v1.py."""
    result = subprocess.run(
        ["python3", str(REPO / "bin" / "dossier_engine_v1.py"),
         "--pods", *pods, "--query", query,
         "--top-k", str(top_k), "--budget", str(budget),
         "--output", "/tmp/dossier_out.json"],
        capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        log(f"dossier_engine failed: {result.stderr}", "held")
        return None
    return json.loads(Path("/tmp/dossier_out.json").read_text())

def build_prompt(question, dossier, iteration, prior_context=""):
    """Build the prompt for the cloud router with dossier context."""
    chunks_text = ""
    for i, chunk in enumerate(dossier.get("dossier", []), 1):
        chunks_text += f"\n--- CHUNK {i} (pod={chunk['pod']}, score={chunk['bm25_score']:.2f}) ---\n"
        chunks_text += chunk["text"][:500] + "\n"
    
    sys_prompt = f"""You are part of OpenRoot, a verifiable local autonomy system. Iteration {iteration}.

You will receive:
1. A user question
2. A dossier of relevant context chunks from the pod garden

Your job:
1. Inspect the attachment (the dossier chunks)
2. Answer the question using ONLY the dossier context
3. If you need MORE information to give a complete answer, ask clarifying questions
4. Each clarifying question will be routed back to the dossier engine automatically
5. When you have enough information, end with: ANSWER_COMPLETE

Format your response as JSON:
{{
  "answer": "<your current best answer based on the dossier>",
  "clarifying_questions": ["<question 1>", "<question 2>"],
  "answer_complete": true/false,
  "citation_chunks": ["chunk_blake3 hash of chunks you cited"]
}}

Be conservative. Only ask clarifying questions if the dossier genuinely lacks information needed."""
    
    full_prompt = f"{sys_prompt}\n\n"
    if prior_context:
        full_prompt += f"PRIOR CONTEXT FROM PREVIOUS ITERATIONS:\n{prior_context}\n\n"
    full_prompt += f"USER QUESTION:\n{question}\n\n"
    full_prompt += f"DOSSIER (iteration {iteration}, {dossier.get('chunks_returned', 0)} chunks, {dossier.get('total_chars', 0)} chars):\n{chunks_text}\n\nRESPOND:"
    return full_prompt

def parse_ai_response(response_text):
    """Parse the AI's JSON response. Tolerant of markdown code blocks."""
    # Strip markdown code fences
    text = response_text.strip()
    if text.startswith("```"):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON from the response
        m = re.search(r'\{[\s\S]*\}', text)
        if m:
            try:
                return json.loads(m.group(0))
            except:
                pass
        return {
            "answer": response_text,
            "clarifying_questions": [],
            "answer_complete": True,
            "citation_chunks": [],
            "_parse_warning": "non-JSON response, treating as final"
        }

def run_cloud_router(prompt, model=None, max_tokens=1500):
    """Call the cloud_router_v1.py."""
    cmd = ["python3", str(REPO / "bin" / "cloud_router_v1.py"),
           "--prompt", prompt, "--max-tokens", str(max_tokens)]
    if model:
        cmd += ["--model", model]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if result.returncode != 0:
        log(f"cloud_router failed: {result.stderr}", "held")
        return None
    return json.loads(result.stdout)

def recursive_dossier(question, pods, max_iterations=5, top_k=18, budget=8000, model=None):
    """Run the recursive ReAct loop. Each iteration produces a receipt."""
    log(f"CANARY:OPENROOT-RECURSIVE-DOSSIER-V1 {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    log(f"question: {question[:80]}...")
    log(f"pods: {pods}")
    log(f"max_iterations: {max_iterations}")
    
    iterations = []
    prior_context = ""
    iteration_receipts = []
    
    for i in range(1, max_iterations + 1):
        log(f"", "")
        log(f"=== ITERATION {i}/{max_iterations} ===")
        
        # Extract keywords from question + prior context
        keywords = extract_keywords(f"{question} {prior_context}")
        log(f"keywords: {keywords}")
        
        # Build FTS query and run dossier
        fts_query = build_fts_query(keywords)
        dossier = run_dossier(pods, fts_query, top_k, budget)
        if not dossier:
            log(f"dossier failed at iteration {i}", "held")
            break
        
        log(f"dossier: {dossier['chunks_returned']} chunks, {dossier['total_chars']} chars")
        
        # Build prompt
        prompt = build_prompt(question, dossier, i, prior_context)
        
        # Call cloud router
        log(f"calling cloud_router (model={model or 'auto'})...")
        router_result = run_cloud_router(prompt, model)
        if not router_result or not router_result.get("success"):
            log(f"cloud_router failed at iteration {i}", "held")
            break
        
        log(f"cloud_router: provider={router_result.get('provider')}, tokens={router_result.get('tokens')}")
        
        # Parse AI response
        parsed = parse_ai_response(router_result.get("response", ""))
        
        iteration_receipt = {
            "iteration": i,
            "keywords": keywords,
            "fts_query": fts_query,
            "dossier_chunks": dossier["chunks_returned"],
            "dossier_chars": dossier["total_chars"],
            "provider": router_result.get("provider"),
            "model": router_result.get("model"),
            "tokens_used": router_result.get("tokens"),
            "answer": parsed.get("answer", ""),
            "clarifying_questions": parsed.get("clarifying_questions", []),
            "answer_complete": parsed.get("answer_complete", False),
            "citation_chunks": parsed.get("citation_chunks", []),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        iterations.append(iteration_receipt)
        
        # Update prior context
        prior_context += f"\n[Iteration {i} answer]: {parsed.get('answer', '')[:500]}\n"
        if parsed.get("clarifying_questions"):
            prior_context += f"[Iteration {i} clarifying questions]: {', '.join(parsed['clarifying_questions'])}\n"
        
        # Termination check
        if parsed.get("answer_complete", False):
            log(f"answer complete at iteration {i}")
            break
        if not parsed.get("clarifying_questions"):
            log(f"no clarifying questions at iteration {i}, terminating")
            break
    
    # Build final receipt
    final_receipt = {
        "canary": CANARY,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "question": question,
        "pods_searched": pods,
        "iterations_run": len(iterations),
        "iterations": iterations,
        "final_answer": iterations[-1].get("answer", "") if iterations else "",
        "providers_used": list(set(it["provider"] for it in iterations if it.get("provider"))),
        "total_tokens": sum(it.get("tokens_used", 0) or 0 for it in iterations),
        "total_dossier_chunks": sum(it.get("dossier_chunks", 0) for it in iterations),
        "question_sha256": hashlib.sha256(question.encode()).hexdigest(),
    }
    return final_receipt

def main():
    p = argparse.ArgumentParser(description="OpenRoot Recursive Dossier v1")
    p.add_argument("--question", required=True)
    p.add_argument("--pods", nargs="+", required=True)
    p.add_argument("--max-iterations", type=int, default=5)
    p.add_argument("--top-k", type=int, default=18)
    p.add_argument("--budget", type=int, default=8000)
    p.add_argument("--model", default=None)
    p.add_argument("--output", help="write receipt JSON to file")
    args = p.parse_args()
    
    receipt = recursive_dossier(args.question, args.pods, args.max_iterations,
                                args.top_k, args.budget, args.model)
    
    out = json.dumps(receipt, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(out)
        log(f"receipt -> {args.output}")
        log(f"iterations: {receipt['iterations_run']}")
        log(f"tokens: {receipt['total_tokens']}")
        log(f"chunks retrieved: {receipt['total_dossier_chunks']}")
        log(f"providers: {receipt['providers_used']}")
    else:
        print(out)

if __name__ == "__main__":
    main()
