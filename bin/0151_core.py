import hashlib
from dataclasses import dataclass, field
from typing import List, Optional
@dataclass
class Prediction:
    content:str; confidence:float; source:str; tags:List[str]=field(default_factory=list); hash:str=""
    def __post_init__(self):
        if not self.hash: self.hash=hashlib.sha256(self.content.encode()).hexdigest()[:16]
@dataclass
class StandingWave:
    content:str; confidence:float; coherence_score:float; synergy:float; sources:List[str]; survivor_count:int; total_predictions:int
class ResonanceFilter:
    def __init__(self,agape_coefficient:float=0.85):
        self.R=max(0.0,min(1.0,agape_coefficient)); self.predictions=[]
    def add_prediction(self,content,confidence=0.5,source="unknown",tags=None):
        self.predictions.append(Prediction(content.strip(),confidence,source,tags or []))
    def coordination_cost(self):
        n=len(self.predictions)
        return 0.0 if n<=1 else (1.0-self.R)*(n*(n-1)/2)/100.0
    def standing_wave(self)->Optional[StandingWave]:
        if not self.predictions: return None
        scored=sorted(self.predictions,key=lambda p:(p.confidence*len(p.content),p.confidence),reverse=True)
        top=scored[0]; survivors=[p for p in scored if p.confidence>=0.4]
        coh=min(1.0,len(survivors)/max(1,len(self.predictions))); syn=1.0+(coh*self.R)
        return StandingWave(top.content,top.confidence*coh,coh,syn,[p.source for p in survivors],len(survivors),len(self.predictions))
