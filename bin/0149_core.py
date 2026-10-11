import hashlib, math, time, json
from dataclasses import dataclass
from typing import List, Optional, Dict
KB=1.380649e-23; T_ROOM=298.15; LN2=math.log(2)
def landauer_cost(bits,T=T_ROOM): return bits*KB*T*LN2
def a15_energy(seconds,duty=0.7): return 1.1*duty*seconds
def measure(useful,human): return 0.0 if human<=0 else useful/human
def capture(data:bytes):
    h=hashlib.sha256(data).hexdigest(); return h, landauer_cost(len(data)*8)
def merkle_root(hashes:List[str]):
    if not hashes: return hashlib.sha256(b"empty").hexdigest()
    level=[bytes.fromhex(h) if len(h)==64 else hashlib.sha256(h.encode()).digest() for h in hashes]
    while len(level)>1:
        if len(level)%2: level.append(level[-1])
        level=[hashlib.sha256(level[i]+level[i+1]).digest() for i in range(0,len(level),2)]
    return level[0].hex()
@dataclass
class Claim:
    name:str; value:float; unit:str; basis:str; notes:str=""
    def to_dict(self): return {"name":self.name,"value":self.value,"unit":self.unit,"basis":self.basis,"notes":self.notes}
class BottleneckTracker:
    def __init__(self): self._e=[]
    def record(self,name,duration,meta=None): self._e.append({"name":name,"duration":duration,"meta":meta or {},"ts":time.time()})
    def worst(self): return max(self._e,key=lambda x:x["duration"])["name"] if self._e else None
def commit(claims,extra=None):
    p={"claims":[c.to_dict() for c in claims],"extra":extra or {},"ts":time.time()}
    raw=json.dumps(p,sort_keys=True).encode(); return {"merkle":hashlib.sha256(raw).hexdigest(),"payload":p}
