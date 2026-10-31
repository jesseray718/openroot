"""
groq_max_cycles.py
──────────────────
Maximizes Groq token throughput by cycling across all available models,
respecting per-model TPD and TPM limits extracted from your usage CSV.

Strategy:
  1. Maintain a per-model budget tracker (TPD remaining, TPM window)
  2. On each request, pick the model with the most remaining TPD budget
     that also has TPM headroom right now
  3. When a model hits TPD → drop it for the rest of the day
  4. When a model hits TPM → back off for that window (~60s) then retry
  5. Rotate through all live models in a round-robin if budgets are equal
  6. Log every call so you can reload state after a restart

Usage:
    pip install groq
    export GROQ_API_KEY=gsk_...
    python groq_max_cycles.py --prompt "Hello" --max-tokens 500 --calls 1000

    # Or import and call directly:
    from groq_max_cycles import MaxCycler
    cycler = MaxCycler()
    for result in cycler.run(messages=[{"role":"user","content":"Hello"}], n=100):
        print(result["model"], result["output_tokens"])
"""

import os
import re
import time
import json
import logging
import argparse
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Optional

try:
    from groq import Groq
except ImportError:
    raise SystemExit("Install the Groq SDK first:  pip install groq")

# ─────────────────────────────────────────────────────────────────────────────
# RATE LIMIT TABLE  (extracted from your CSV + Groq free-tier docs)
# Expand or adjust these as your account tier changes.
# ─────────────────────────────────────────────────────────────────────────────
MODEL_LIMITS = {
    # model_id: { tpd, tpm, rpm }
    "meta-llama/llama-4-scout-17b-16e-instruct": {
        "tpd": 500_000,   # tokens per day   ← from your CSV
        "tpm": 30_000,    # tokens per minute ← from your CSV
        "rpm": 30,        # requests per minute (Groq free tier default)
    },
    "llama-3.3-70b-versatile": {
        "tpd": 100_000,
        "tpm": 100_000,   # TPM = TPD for this model on your plan
        "rpm": 30,
    },
    "openai/gpt-oss-120b": {
        "tpd": 200_000,   # not seen in CSV; use conservative default
        "tpm": 8_000,     # from your CSV
        "rpm": 30,
    },
    "openai/gpt-oss-20b": {
        "tpd": 200_000,
        "tpm": 15_000,
        "rpm": 30,
    },
    "qwen/qwen3-32b": {
        "tpd": 200_000,
        "tpm": 15_000,
        "rpm": 30,
    },
    # Add more Groq models here as needed:
    # "llama-3.1-8b-instant":     { "tpd": 500_000, "tpm": 30_000, "rpm": 30 },
    # "mixtral-8x7b-32768":       { "tpd": 500_000, "tpm": 30_000, "rpm": 30 },
    # "gemma2-9b-it":             { "tpd": 500_000, "tpm": 30_000, "rpm": 30 },
}

# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("groq_cycles")


@dataclass
class ModelState:
    """Live budget tracking for one model."""
    model_id: str
    tpd_limit: int
    tpm_limit: int
    rpm_limit: int

    # Persisted counters (reset daily)
    tpd_used: int = 0
    day_start: float = field(default_factory=time.time)

    # Sliding windows
    tpm_window: deque = field(default_factory=deque)   # (timestamp, tokens)
    rpm_window: deque = field(default_factory=deque)   # timestamp

    # Back-off state
    backed_off_until: float = 0.0
    consecutive_429s: int = 0

    def _prune_windows(self):
        now = time.time()
        # Reset daily counter if a new UTC day has started
        if now - self.day_start >= 86_400:
            self.tpd_used = 0
            self.day_start = now
            log.info(f"[{self.model_id}] Daily counter reset")

        cutoff = now - 60
        while self.tpm_window and self.tpm_window[0][0] < cutoff:
            self.tpm_window.popleft()
        while self.rpm_window and self.rpm_window[0] < cutoff:
            self.rpm_window.popleft()

    @property
    def tpd_remaining(self) -> int:
        self._prune_windows()
        return max(0, self.tpd_limit - self.tpd_used)

    @property
    def tpm_used_1min(self) -> int:
        self._prune_windows()
        return sum(t for _, t in self.tpm_window)

    @property
    def tpm_remaining(self) -> int:
        return max(0, self.tpm_limit - self.tpm_used_1min)

    @property
    def rpm_used_1min(self) -> int:
        self._prune_windows()
        return len(self.rpm_window)

    @property
    def rpm_remaining(self) -> int:
        return max(0, self.rpm_limit - self.rpm_used_1min)

    def is_available(self, want_tokens: int) -> bool:
        if time.time() < self.backed_off_until:
            return False
        if self.tpd_remaining < want_tokens:
            return False
        if self.tpm_remaining < want_tokens:
            return False
        if self.rpm_remaining < 1:
            return False
        return True

    def record_success(self, tokens_used: int):
        now = time.time()
        self.tpd_used += tokens_used
        self.tpm_window.append((now, tokens_used))
        self.rpm_window.append(now)
        self.consecutive_429s = 0
        self.backed_off_until = 0.0

    def record_rate_limit(self, retry_after_sec: float = 60.0):
        self.consecutive_429s += 1
        backoff = min(retry_after_sec * (1.5 ** (self.consecutive_429s - 1)), 3600)
        self.backed_off_until = time.time() + backoff
        log.warning(
            f"[{self.model_id}] Rate limited. "
            f"Backing off {backoff:.0f}s (attempt #{self.consecutive_429s})"
        )

    def seconds_until_available(self) -> float:
        now = time.time()
        if now < self.backed_off_until:
            return self.backed_off_until - now
        # How long until TPM window frees up?
        if self.tpm_window:
            oldest = self.tpm_window[0][0]
            return max(0.0, oldest + 60 - now)
        return 0.0

    def status(self) -> str:
        bo = ""
        if time.time() < self.backed_off_until:
            bo = f" | BO:{self.backed_off_until - time.time():.0f}s"
        return (
            f"TPD {self.tpd_remaining:>7,}/{self.tpd_limit:,} "
            f"| TPM {self.tpm_remaining:>6,}/{self.tpm_limit:,} "
            f"| RPM {self.rpm_remaining:>2}/{self.rpm_limit}"
            f"{bo}"
        )


class MaxCycler:
    """
    Round-robins requests across all live Groq models to maximise
    total tokens consumed per day.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        models: Optional[dict] = None,
        state_file: Optional[str] = "groq_cycle_state.json",
        verbose: bool = True,
    ):
        self.client = Groq(api_key=api_key or os.environ["GROQ_API_KEY"])
        limits = models or MODEL_LIMITS
        self.states: dict[str, ModelState] = {
            mid: ModelState(
                model_id=mid,
                tpd_limit=cfg["tpd"],
                tpm_limit=cfg["tpm"],
                rpm_limit=cfg.get("rpm", 30),
            )
            for mid, cfg in limits.items()
        }
        self.state_file = state_file
        self.verbose = verbose
        self._load_state()

    # ── State persistence ────────────────────────────────────────────────────

    def _load_state(self):
        if not self.state_file or not os.path.exists(self.state_file):
            return
        try:
            with open(self.state_file) as f:
                saved = json.load(f)
            for mid, data in saved.items():
                if mid in self.states:
                    s = self.states[mid]
                    s.tpd_used = data.get("tpd_used", 0)
                    s.day_start = data.get("day_start", time.time())
            log.info(f"Loaded state from {self.state_file}")
        except Exception as e:
            log.warning(f"Could not load state: {e}")

    def _save_state(self):
        if not self.state_file:
            return
        data = {}
        for mid, s in self.states.items():
            data[mid] = {
                "tpd_used": s.tpd_used,
                "day_start": s.day_start,
            }
        with open(self.state_file, "w") as f:
            json.dump(data, f, indent=2)

    # ── Model selection ──────────────────────────────────────────────────────

    def pick_model(self, want_tokens: int = 500) -> Optional[ModelState]:
        """
        Returns the model with the most TPD headroom that is currently
        available (not backed-off, has TPM/RPM room).
        """
        candidates = [
            s for s in self.states.values()
            if s.is_available(want_tokens)
        ]
        if not candidates:
            return None
        # Prefer the model with the most remaining TPD (max coins)
        return max(candidates, key=lambda s: s.tpd_remaining)

    def wait_for_any_model(self, want_tokens: int = 500) -> ModelState:
        """Block until at least one model becomes available."""
        while True:
            m = self.pick_model(want_tokens)
            if m:
                return m
            # Find shortest wait
            waits = [s.seconds_until_available() for s in self.states.values()
                     if s.tpd_remaining >= want_tokens]
            if not waits:
                raise RuntimeError(
                    "All models have exhausted their daily token budgets. "
                    "Come back tomorrow."
                )
            sleep_sec = max(1.0, min(waits))
            log.info(f"All models at capacity. Sleeping {sleep_sec:.0f}s …")
            time.sleep(sleep_sec)

    # ── Single call ──────────────────────────────────────────────────────────

    def call(
        self,
        messages: list[dict],
        max_tokens: int = 512,
        temperature: float = 0.7,
        retries: int = 5,
        **kwargs,
    ) -> dict:
        """
        Makes one completion call, auto-selecting the best model.
        Returns a result dict with model, content, tokens, latency.
        """
        attempt = 0
        while attempt < retries:
            attempt += 1
            state = self.wait_for_any_model(want_tokens=max_tokens)

            t0 = time.time()
            try:
                resp = self.client.chat.completions.create(
                    model=state.model_id,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs,
                )
                elapsed = time.time() - t0
                usage = resp.usage
                total_tok = (usage.prompt_tokens or 0) + (usage.completion_tokens or 0)
                state.record_success(total_tok)
                self._save_state()

                if self.verbose:
                    log.info(
                        f"✓ {state.model_id:<45} "
                        f"in={usage.prompt_tokens} out={usage.completion_tokens} "
                        f"({elapsed:.2f}s)  │ {state.status()}"
                    )

                return {
                    "model": state.model_id,
                    "content": resp.choices[0].message.content,
                    "input_tokens": usage.prompt_tokens,
                    "output_tokens": usage.completion_tokens,
                    "total_tokens": total_tok,
                    "latency_s": round(elapsed, 3),
                    "finish_reason": resp.choices[0].finish_reason,
                }

            except Exception as exc:
                msg = str(exc)
                status = getattr(exc, "status_code", None)

                if status == 429:
                    # Parse retry-after from error message if present
                    retry_after = 60.0
                    m_wait = re.search(r"try again in ([\d.]+)([smh])", msg, re.I)
                    if m_wait:
                        val, unit = float(m_wait.group(1)), m_wait.group(2).lower()
                        retry_after = val * {"s": 1, "m": 60, "h": 3600}.get(unit, 1)
                    state.record_rate_limit(retry_after)
                    continue  # try again with a different model

                elif status == 413:
                    # Context too large for this model; log and skip
                    log.warning(f"[{state.model_id}] 413 payload too large – skipping")
                    # Temporarily back off this model for a few seconds
                    state.backed_off_until = time.time() + 5
                    continue

                elif status == 400:
                    log.error(f"[{state.model_id}] 400 bad request: {msg[:200]}")
                    raise  # Don't retry 400s – they're prompt/schema errors

                elif status == 404:
                    log.error(f"[{state.model_id}] 404 model not found – removing")
                    del self.states[state.model_id]
                    raise

                else:
                    log.warning(f"[{state.model_id}] {status} error: {msg[:200]} – retry {attempt}/{retries}")
                    time.sleep(2 ** attempt)

        raise RuntimeError(f"Failed after {retries} retries")

    # ── Batch run ────────────────────────────────────────────────────────────

    def run(
        self,
        messages: list[dict],
        n: int = 100,
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs,
    ):
        """
        Generator: yields n results, cycling across models to max out TPD.
        """
        totals = defaultdict(int)
        for i in range(n):
            result = self.call(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )
            totals[result["model"]] += result["total_tokens"]
            result["call_number"] = i + 1
            yield result

        log.info("\n=== CYCLE COMPLETE ===")
        for model, toks in sorted(totals.items(), key=lambda x: -x[1]):
            s = self.states[model]
            pct = toks / s.tpd_limit * 100
            log.info(f"  {model:<45} {toks:>8,} tokens  ({pct:.1f}% of daily limit)")

    # ── Budget report ────────────────────────────────────────────────────────

    def report(self):
        print("\n╔══ GROQ MODEL BUDGET REPORT ══════════════════════════════════════╗")
        for mid, s in sorted(self.states.items(), key=lambda x: -x[1].tpd_remaining):
            avail = "✓" if s.is_available(100) else "✗"
            print(f"  {avail} {mid:<45}  {s.status()}")
        print("╚══════════════════════════════════════════════════════════════════╝\n")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Max out Groq coins via model cycling")
    parser.add_argument("--prompt", default="Say 'token' ten times.", help="User prompt")
    parser.add_argument("--system", default="You are a helpful assistant.", help="System prompt")
    parser.add_argument("--calls", type=int, default=50, help="Number of API calls to make")
    parser.add_argument("--max-tokens", type=int, default=512, help="Max output tokens per call")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--report", action="store_true", help="Show budget report and exit")
    parser.add_argument("--state-file", default="groq_cycle_state.json")
    args = parser.parse_args()

    cycler = MaxCycler(state_file=args.state_file)

    if args.report:
        cycler.report()
        return

    cycler.report()

    messages = [
        {"role": "system", "content": args.system},
        {"role": "user", "content": args.prompt},
    ]

    total_in, total_out = 0, 0
    t_start = time.time()

    for result in cycler.run(messages, n=args.calls, max_tokens=args.max_tokens,
                             temperature=args.temperature):
        total_in += result["input_tokens"]
        total_out += result["output_tokens"]

    elapsed = time.time() - t_start
    print(f"\n{'─'*60}")
    print(f"Completed {args.calls} calls in {elapsed:.1f}s")
    print(f"Total input tokens:  {total_in:,}")
    print(f"Total output tokens: {total_out:,}")
    print(f"Total tokens:        {total_in + total_out:,}")
    print(f"Avg tokens/call:     {(total_in+total_out)/args.calls:.0f}")
    cycler.report()


if __name__ == "__main__":
    main()
