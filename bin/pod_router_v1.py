#!/usr/bin/env python3
"""Per-pod router: picks 1-3 pods by keyword domain mapping, not all pods.
Deterministic. No AI. Routes clarifying questions back through same pods."""
import re, sys, json, os
from pathlib import Path

REPO = Path(os.environ.get("OPENROOT_REPO", "/home/jesse/openroot"))
GARDEN = REPO / "pods_garden"

# Domain keyword map — add more as pods grow
DOMAIN_MAP = {
    "grants": ["grant","sare","usda","reap","funding","proposal","nrcs","frg","budget","award"],
    "code": ["python","script","subprocess","ssh","git","function","class","import","bash","shell"],
    "thermal": ["aerocement","thermal","cascade","solar","heat","stirling","joules","rapl","delta_t"],
    "mesh": ["mesh","lora","meshtastic","tailscale","node","network","reticulum","lxmf","rnode"],
    "governance": ["axiom","constitution","agape","newton","kingdom","receipt","genesis","epoch"],
    "permaculture": ["permaculture","observe","interact","yield","compost","diversity","edge"],
    "protocols": ["subprocess","ssh","heredoc","cat","eof","installer","cheatsheet","openrouter"],
}

def extract_keywords(text, max_k=8):
    stop = {"the","a","an","is","are","was","what","how","why","do","does","to","of","in","on","for","with","and","or","but","not","this","that","i","you","it"}
    words = re.findall(r'[a-zA-Z_][a-zA-Z0-9_-]{2,}', text.lower())
    kws = [w for w in words if w not in stop and len(w) > 2]
    seen = set()
    return [w for w in kws if not (w in seen or seen.add(w))][:max_k]

def route_to_pods(question, max_pods=3):
    """Pick 1-3 pods by keyword domain match. Deterministic."""
    kws = extract_keywords(question)
    kw_set = set(kws)
    
    # Score each domain by keyword overlap
    domain_scores = {}
    for domain, domain_kws in DOMAIN_MAP.items():
        overlap = len(kw_set & set(domain_kws))
        if overlap > 0:
            domain_scores[domain] = overlap
    
    # If no domain match, return general pods
    if not domain_scores:
        return ["coding_protocols_pasteable_v1", "lesson_plan_script_doctrine"], kws
    
    # Pick top domains
    sorted_domains = sorted(domain_scores.items(), key=lambda x: -x[1])[:max_pods]
    
    # Map domains to actual pods in garden
    pod_map = {
        "grants": ["sare_grants", "grants_pod"],
        "code": ["coding_protocols_pasteable_v1", "tar_bundle_v3"],
        "thermal": ["tar_bundle_v3", "theorem_proofs"],
        "mesh": ["tar_bundle_v3"],
        "governance": ["theorem_proofs", "lesson_plan_script_doctrine"],
        "permaculture": ["lesson_plan_script_doctrine"],
        "protocols": ["coding_protocols_pasteable_v1"],
    }
    
    selected_pods = []
    for domain, score in sorted_domains:
        for pod in pod_map.get(domain, []):
            if (GARDEN / pod).exists() and pod not in selected_pods:
                selected_pods.append(pod)
    
    if not selected_pods:
        selected_pods = ["coding_protocols_pasteable_v1"]
    
    return selected_pods[:max_pods], kws

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--question", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    pods, kws = route_to_pods(args.question)
    if args.json:
        print(json.dumps({"pods": pods, "keywords": kws}))
    else:
        print(f"pods: {pods}")
        print(f"keywords: {kws}")
