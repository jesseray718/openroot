import asyncio, hashlib, time
from typing import Callable, Dict, Awaitable, List
NANOBOT_NAMES=["translate","analyze","feedback","synthesize","validate","amplify"]
NANOBOT_PROMPTS={
"translate":"Restate the question in the clearest physical and practical terms. No jargon.",
"analyze":"Identify the dominant physical constraints, energy flows and failure modes.",
"feedback":"What would go wrong in the first 30 days of implementing the current best answer?",
"synthesize":"Produce the single highest-leverage action that satisfies the constraints found so far.",
"validate":"Does the proposed action obey conservation of energy and local material availability? Yes/No + reason.",
"amplify":"Scale the validated action by 10x with zero additional human coordination cost. What breaks?"
}
class Lattice:
    def __init__(self,call_fn:Callable[[str,str],Awaitable[str]],depth:int=1):
        self.call_fn=call_fn; self.depth=max(1,min(depth,3)); self.trace=[]; self._start=None
    def theoretical_nodes(self): return 6*(1+self.depth)
    async def _run_bot(self,name,prompt,system):
        t0=time.time(); out=await self.call_fn(prompt,system); dt=time.time()-t0
        self.trace.append({"bot":name,"dt":dt,"chars":len(out),"hash":hashlib.sha256(out.encode()).hexdigest()[:16]})
        return out
    async def run(self,query:str)->Dict[str,str]:
        self._start=time.time(); results={}
        for name in NANOBOT_NAMES:
            results[name]=await self._run_bot(name,query,NANOBOT_PROMPTS[name])
        if self.depth>1:
            bottleneck=max(self.trace,key=lambda t:t["dt"])["bot"]
            deepen=f"Deepen only this: {results[bottleneck]}\nOriginal: {query}"
            results[f"{bottleneck}_d1"]=await self._run_bot(f"{bottleneck}_d1",deepen,NANOBOT_PROMPTS[bottleneck])
        return results
    def trace_hash(self): return hashlib.sha256("".join(t["hash"] for t in self.trace).encode()).hexdigest()
    def elapsed(self): return time.time()-self._start if self._start else 0.0
