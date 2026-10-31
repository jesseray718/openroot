import os, re, time, json, logging, argparse
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Optional
try:
    import groq; Groq = groq.Groq
except ImportError:
    pass

MODEL_LIMITS = {
    "meta-llama/llama-4-scout-17b-16e-instruct": {"tpd":500000,"tpm":30000,"rpm":30},
    "llama-3.3-70b-versatile":                   {"tpd":100000,"tpm":100000,"rpm":30},
    "openai/gpt-oss-120b":                       {"tpd":200000,"tpm":8000,"rpm":30},
    "openai/gpt-oss-20b":                        {"tpd":200000,"tpm":15000,"rpm":30},
    "qwen/qwen3-32b":                            {"tpd":200000,"tpm":15000,"rpm":30},
}

logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)-7s %(message)s",datefmt="%H:%M:%S")
log = logging.getLogger("groq_cycles")

@dataclass
class ModelState:
    model_id: str
    tpd_limit: int
    tpm_limit: int
    rpm_limit: int
    tpd_used: int = 0
    day_start: float = field(default_factory=time.time)
    tpm_window: deque = field(default_factory=deque)
    rpm_window: deque = field(default_factory=deque)
    backed_off_until: float = 0.0
    consecutive_429s: int = 0

    def _prune(self):
        now = time.time()
        if now - self.day_start >= 86400:
            self.tpd_used = 0
            self.day_start = now
            log.info(f"[{self.model_id}] Daily counter reset")
        cut = now - 60
        while self.tpm_window and self.tpm_window[0][0] < cut: self.tpm_window.popleft()
        while self.rpm_window and self.rpm_window[0] < cut: self.rpm_window.popleft()

    @property
    def tpd_remaining(self):
        self._prune(); return max(0, self.tpd_limit - self.tpd_used)
    @property
    def tpm_remaining(self):
        self._prune(); return max(0, self.tpm_limit - sum(t for _,t in self.tpm_window))
    @property
    def rpm_remaining(self):
        self._prune(); return max(0, self.rpm_limit - len(self.rpm_window))

    def is_available(self, want):
        if time.time() < self.backed_off_until: return False
        return self.tpd_remaining >= want and self.tpm_remaining >= want and self.rpm_remaining >= 1

    def record_success(self, tokens):
        now = time.time()
        self.tpd_used += tokens
        self.tpm_window.append((now, tokens))
        self.rpm_window.append(now)
        self.consecutive_429s = 0
        self.backed_off_until = 0.0

    def record_rate_limit(self, retry_after=60.0):
        self.consecutive_429s += 1
        backoff = min(retry_after * (1.5 ** (self.consecutive_429s - 1)), 3600)
        self.backed_off_until = time.time() + backoff
        log.warning(f"[{self.model_id}] Rate limited. Backoff {backoff:.0f}s")

    def seconds_until_available(self):
        now = time.time()
        if now < self.backed_off_until: return self.backed_off_until - now
        if self.tpm_window: return max(0.0, self.tpm_window[0][0] + 60 - now)
        return 0.0

    def status(self):
        bo = f" BO:{self.backed_off_until-time.time():.0f}s" if time.time()<self.backed_off_until else ""
        return f"TPD {self.tpd_remaining:>7,}/{self.tpd_limit:,} TPM {self.tpm_remaining:>6,}/{self.tpm_limit:,} RPM {self.rpm_remaining}/{self.rpm_limit}{bo}"

class MaxCycler:
    def __init__(self, api_key=None, models=None, state_file="groq_cycle_state.json", verbose=True):
        self.client = Groq(api_key=api_key or os.environ["GROQ_API_KEY"])
        self.states = {mid: ModelState(model_id=mid,tpd_limit=c["tpd"],tpm_limit=c["tpm"],rpm_limit=c.get("rpm",30))
                       for mid,c in (models or MODEL_LIMITS).items()}
        self.state_file = state_file
        self.verbose = verbose
        self._load_state()

    def _load_state(self):
        if not self.state_file or not os.path.exists(self.state_file): return
        try:
            saved = json.load(open(self.state_file))
            for mid,d in saved.items():
                if mid in self.states:
                    self.states[mid].tpd_used = d.get("tpd_used",0)
                    self.states[mid].day_start = d.get("day_start",time.time())
            log.info(f"Loaded state from {self.state_file}")
        except Exception as e: log.warning(f"Could not load state: {e}")

    def _save_state(self):
        if not self.state_file: return
        json.dump({mid:{"tpd_used":s.tpd_used,"day_start":s.day_start} for mid,s in self.states.items()},
                  open(self.state_file,"w"), indent=2)

    def pick_model(self, want=500):
        c = [s for s in self.states.values() if s.is_available(want)]
        return max(c, key=lambda s: s.tpd_remaining) if c else None

    def wait_for_any(self, want=500):
        while True:
            m = self.pick_model(want)
            if m: return m
            waits = [s.seconds_until_available() for s in self.states.values() if s.tpd_remaining >= want]
            if not waits: raise RuntimeError("All models exhausted for today.")
            sleep = max(1.0, min(waits))
            log.info(f"All models at capacity. Sleeping {sleep:.0f}s...")
            time.sleep(sleep)

    def call(self, messages, max_tokens=512, temperature=0.7, retries=5, **kw):
        for attempt in range(1, retries+1):
            state = self.wait_for_any(want=max_tokens)
            t0 = time.time()
            try:
                resp = self.client.chat.completions.create(
                    model=state.model_id, messages=messages,
                    max_tokens=max_tokens, temperature=temperature, **kw)
                u = resp.usage
                total = (u.prompt_tokens or 0) + (u.completion_tokens or 0)
                state.record_success(total)
                self._save_state()
                if self.verbose:
                    log.info(f"OK {state.model_id:<45} in={u.prompt_tokens} out={u.completion_tokens} ({time.time()-t0:.2f}s) | {state.status()}")
                return {"model":state.model_id,"content":resp.choices[0].message.content,
                        "input_tokens":u.prompt_tokens,"output_tokens":u.completion_tokens,
                        "total_tokens":total,"latency_s":round(time.time()-t0,3)}
            except Exception as exc:
                sc = getattr(exc,"status_code",None)
                msg = str(exc)
                if sc == 429:
                    ra = 60.0
                    m = re.search(r"try again in ([\d.]+)([smh])",msg,re.I)
                    if m: ra = float(m.group(1))*{"s":1,"m":60,"h":3600}.get(m.group(2).lower(),1)
                    state.record_rate_limit(ra); continue
                elif sc == 413:
                    log.warning(f"[{state.model_id}] 413 too large, skipping")
                    state.backed_off_until = time.time()+5; continue
                elif sc == 400: log.error(f"400 bad request: {msg[:200]}"); raise
                elif sc == 404: log.error(f"404 model not found, removing"); del self.states[state.model_id]; raise
                else: log.warning(f"{sc} error attempt {attempt}: {msg[:100]}"); time.sleep(2**attempt)
        raise RuntimeError(f"Failed after {retries} retries")

    def run(self, messages, n=100, max_tokens=512, temperature=0.7, **kw):
        totals = defaultdict(int)
        for i in range(n):
            r = self.call(messages, max_tokens=max_tokens, temperature=temperature, **kw)
            totals[r["model"]] += r["total_tokens"]
            r["call_number"] = i+1
            yield r
        log.info("=== CYCLE COMPLETE ===")
        for model,toks in sorted(totals.items(),key=lambda x:-x[1]):
            s = self.states[model]
            log.info(f"  {model:<45} {toks:>8,} tokens ({toks/s.tpd_limit*100:.1f}% of daily limit)")

    def report(self):
        print("\n=== GROQ MODEL BUDGET ===")
        for mid,s in sorted(self.states.items(),key=lambda x:-x[1].tpd_remaining):
            avail = "OK" if s.is_available(100) else "--"
            print(f"  [{avail}] {mid:<45} {s.status()}")
        print()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt",default="Say the word token ten times.")
    p.add_argument("--system",default="You are a helpful assistant.")
    p.add_argument("--calls",type=int,default=50)
    p.add_argument("--max-tokens",type=int,default=512)
    p.add_argument("--temperature",type=float,default=0.7)
    p.add_argument("--report",action="store_true")
    p.add_argument("--state-file",default="groq_cycle_state.json")
    args = p.parse_args()
    cycler = MaxCycler(state_file=args.state_file)
    if args.report:
        cycler.report(); return
    cycler.report()
    messages=[{"role":"system","content":args.system},{"role":"user","content":args.prompt}]
    total_in=total_out=0
    t0=time.time()
    for r in cycler.run(messages,n=args.calls,max_tokens=args.max_tokens,temperature=args.temperature):
        total_in+=r["input_tokens"]; total_out+=r["output_tokens"]
    print(f"\nDone: {args.calls} calls in {time.time()-t0:.1f}s")
    print(f"Input: {total_in:,}  Output: {total_out:,}  Total: {total_in+total_out:,}")
    cycler.report()

if __name__=="__main__":
    main()
