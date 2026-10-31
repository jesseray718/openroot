#!/usr/bin/env python3
"""Bottom Tier — Atomic Nanobot Unit. One role, one call, one artifact."""
from __future__ import annotations
import json, os, time, urllib.request, urllib.error
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

HERE = Path(os.environ.get("GOVERNOR_HOME", Path(__file__).resolve().parent.parent))

ROLE_CONTRACTS = {
    "SCOUT": {"system": "You are SCOUT, bottom-tier nanobot. Gather raw facts, numbers, sources, failure modes. No synthesis. Bullet list only. Mark every physical claim [UNVERIFIED].", "max_tokens": 800, "verifier": "human", "autonomy": "parked"},
    "ARCHITECT": {"system": "You are ARCHITECT, bottom-tier nanobot. Convert input into a structured draft: headers, tables, variables, equations. Tag unverified physical claims [THEORETICAL]. Markdown only.", "max_tokens": 1200, "verifier": "human", "autonomy": "parked"},
    "SKEPTIC": {"system": "You are SKEPTIC, bottom-tier nanobot. Red-team the draft. List gaps, false-authority risks, missing falsification tests. Score criticality 0-10. Propose the simplest experiment that could disprove the claim.", "max_tokens": 800, "verifier": "human", "autonomy": "parked"},
    "SCRIBE": {"system": "You are SCRIBE, bottom-tier nanobot. Produce paste-ready markdown. CC-BY-SA 4.0 docs / GPL v3 code. Status line: [draft, verified:T0] — pending T1 human attest. Never claim physical validation.", "max_tokens": 1200, "verifier": "human", "autonomy": "parked"},
    "CODER": {"system": "You are CODER, bottom-tier nanobot. Emit complete, runnable code only. No prose outside comments. Target: Termux / Python 3 / no root. Include a self-test block.", "max_tokens": 1500, "verifier": "deterministic", "autonomy": "auto_iff_tests"},
    "EXTRACTOR": {"system": "You are EXTRACTOR, bottom-tier nanobot. Convert unstructured input to strict JSON matching the provided schema. No commentary. Invalid -> empty object.", "max_tokens": 600, "verifier": "deterministic", "autonomy": "auto"},
}

def now_iso(): return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def load_cfg():
    p = HERE / "swarm-config.json"
    if p.exists(): return json.loads(p.read_text())
    return {"orchestrator": "governor-v1", "providers": ["local", "mock"],
            "models": {"local": "openroot-instruct:7b"}}

@dataclass
class Artifact:
    task_id: str; role: str; content: str; provider: str; model: str
    mode: str; latency_ms: int; status: str
    created: str = field(default_factory=now_iso)
    meta: Dict[str, Any] = field(default_factory=dict)
    def to_markdown(self):
        return self.content.rstrip() + (f"\n\n---\nBottom-tier nanobot · role={self.role} · mode={self.mode} · "
            f"provider={self.provider}/{self.model} · {self.latency_ms}ms · status={self.status} · {self.created}\n")

class BottomTierNanobot:
    def __init__(self, role, mode="mock"):
        role = role.upper()
        if role not in ROLE_CONTRACTS: raise ValueError(f"unknown role {role}")
        self.role, self.mode, self.contract, self.cfg = role, mode, ROLE_CONTRACTS[role], load_cfg()

    def _call_mock(self, u):
        return (f"[{self.role}] (mock) Seed intent echo: {u[:160]}\n", "mock", "deterministic-stub")

    def _call_local(self, u):
        base = os.environ.get("LOCAL_LLM_URL", "http://100.122.169.43:9999").rstrip("/")
        model = os.environ.get("LOCAL_LLM_MODEL") or self.cfg.get("models", {}).get("local", "qwen2.5:3b")
        payload = json.dumps({"model": model, "max_tokens": self.contract["max_tokens"], "temperature": 0.2,
            "messages": [{"role": "system", "content": self.contract["system"]}, {"role": "user", "content": u}]}).encode()
        req = urllib.request.Request(f"{base}/v1/chat/completions", data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as r:
            d = json.loads(r.read())
        return d["choices"][0]["message"]["content"], "local", d.get("model") or model

    def call(self, user_input, provider_pref=None):
        t0 = time.time()
        providers = ["mock"] if self.mode == "mock" else (provider_pref or ["local", "mock"])
        last_err = None; content = provider = model = None
        for p in providers:
            try:
                if p == "mock": content, provider, model = self._call_mock(user_input)
                elif p == "local": content, provider, model = self._call_local(user_input)
                else: continue
                break
            except Exception as e:
                last_err = e; continue
        if content is None: raise RuntimeError(f"all providers failed for {self.role}: {last_err}")
        status = "draft_T0" if self.contract["autonomy"] in ("auto", "auto_iff_tests") else "parked"
        return Artifact(task_id="PENDING", role=self.role, content=content, provider=provider,
                        model=model, mode=self.mode, latency_ms=int((time.time()-t0)*1000),
                        status=status, meta={"contract_verifier": self.contract["verifier"]})

def main():
    import argparse, sys
    ap = argparse.ArgumentParser(description="Bottom-tier nanobot — one role, one call")
    ap.add_argument("--role", required=True, choices=list(ROLE_CONTRACTS))
    ap.add_argument("--input", required=True)
    ap.add_argument("--mode", choices=["mock", "live"], default="mock")
    ap.add_argument("--provider", default="mock")
    ap.add_argument("--id", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    seed = a.input; p = Path(seed)
    if p.exists() and p.is_file(): seed = p.read_text()
    bot = BottomTierNanobot(a.role, mode=a.mode)
    art = bot.call(seed, provider_pref=[x.strip() for x in a.provider.split(",")])
    art.task_id = a.id or f"BT-{a.role}-{int(time.time())}"
    md = art.to_markdown()
    print(md)
    if a.out:
        Path(a.out).write_text(md); print(f"\n[wrote {a.out}]", file=sys.stderr)

if __name__ == "__main__":
    main()
