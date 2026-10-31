#!/usr/bin/env python3
import json,time,os,hashlib,urllib.request,platform,socket
from datetime import datetime,timezone
U="http://127.0.0.1:11434"
H=os.path.expanduser("~")
R=os.path.join(H,"agapenet")
os.makedirs(R,exist_ok=True)
def L(m):print(f"[{datetime.now(timezone.utc).isoformat()}] {m}")
def HSH(o):return hashlib.sha256(json.dumps(o,sort_keys=True,default=str).encode()).hexdigest()[:16]
def SI():
 i={"ts":datetime.now(timezone.utc).isoformat(),"plat":platform.platform(),"mach":platform.machine(),"py":platform.python_version(),"host":socket.gethostname()}
 try:
  for l in open("/proc/meminfo"):
   if l.startswith("MemTotal:"):i["mem_t"]=int(l.split()[1])
   elif l.startswith("MemAvailable:"):i["mem_a"]=int(l.split()[1])
 except:pass
 try:
  c=open("/proc/cpuinfo").read();i["cores"]=c.count("processor")
  for l in c.splitlines():
   if l.startswith("Hardware"):i["cpu"]=l.split(":",1)[-1].strip();break
 except:pass
 try:i["load"]=open("/proc/loadavg").read().split()[:3]
 except:pass
 try:i["up"]=float(open("/proc/uptime").read().split()[0])
 except:pass
 try:
  st=os.statvfs(H);i["df"]= (st.f_bavail*st.f_frsize)//1048576;i["dt"]=(st.f_blocks*st.f_frsize)//1048576
 except:pass
 return i
def ML():
 try:
  with urllib.request.urlopen(urllib.request.Request(f"{U}/api/tags"),timeout=6) as r:
   return[{"name":m["name"],"mb":round(m.get("size",0)/1048576,1)} for m in json.loads(r.read()).get("models",[])]
 except Exception as e:L(f"Ollama down: {e}");return[]
def BM(n,p="Explain permaculture in one sentence."):
 try:
  t0=time.time()
  with urllib.request.urlopen(urllib.request.Request(f"{U}/api/generate",data=json.dumps({"model":n,"prompt":p,"stream":False,"options":{"temperature":0.3,"num_predict":48}}).encode(),headers={"Content-Type":"application/json"}),timeout=90) as r:
   d=json.loads(r.read());el=time.time()-t0;ec=d.get("eval_count",0)
   return{"model":n,"resp":(d.get("response") or "")[:200],"tok":ec,"sec":round(el,2),"tps":round(ec/el,2) if el>0 else 0,"st":"ok"}
 except Exception as e:return{"model":n,"st":"err","err":str(e)[:120]}
def WR(si,ml,bk):
 ok=sum(1 for b in bk if b.get("st")=="ok")
 rep={"id":f"diag_{int(time.time())}","ts":datetime.now(timezone.utc).isoformat(),"type":"node_diagnostics","op":"jesse_ray_openroot","sys":si,"models":ml,"bench":bk,"agape":{"res":"active" if ok else "dormant","ent":"low" if ok else "high","ready":len(ml)>0,"score":f"{ok}/{len(bk)}","next":"deploy_api_gateway" if ok else "start_ollama_or_pull"}}
 rep["hash"]=HSH({k:v for k,v in rep.items() if k!="hash"})
 jp=os.path.join(R,f"{rep['id']}.json")
 with open(jp,"w") as f:json.dump(rep,f,indent=2)
 mp=os.path.join(R,"MASTER_NODE_STATUS.md")
 with open(mp,"w") as f:
  f.write(f"---\nid: {rep['id']}\nts: {rep['ts']}\nhash: {rep['hash']}\nstatus: {'operational' if ok else 'needs_attention'}\nagape_score: {rep['agape']['score']}\nresonance: {rep['agape']['res']}\n---\n\n# AGAPE_NET Node Status\n\n## System\n- Cores: {si.get('cores','?')}  CPU: {si.get('cpu','?')}\n- RAM: {si.get('mem_a',0)//1024}MB / {si.get('mem_t',0)//1024}MB\n- Load: {si.get('load','?')}  Up: {round(si.get('up',0)/3600,1)}h\n- Disk free: {si.get('df','?')}MB\n- Ollama: {U}\n\n## Models ({len(ml)})\n")
  for m in ml:f.write(f"- **{m['name']}** — {m['mb']} MB\n")
  f.write("\n## Benchmarks\n")
  for b in bk:
   if b.get("st")=="ok":f.write(f"- {b['model']}: {b['tps']} tok/s • {b['tok']} tok • {b['sec']}s\n")
   else:f.write(f"- {b['model']}: FAIL — {b.get('err','')}\n")
  f.write(f"\n## Agape\n- Resonance: {rep['agape']['res']}\n- Entropy: {rep['agape']['ent']}\n- Next: {rep['agape']['next']}\n\nHash: `{rep['hash']}`\n")
 return jp,mp,rep
def main():
 L("=== AGAPE_NET Node Bootstrap ===")
 L("1 System...")
 si=SI();L(f"  Cores:{si.get('cores','?')} RAM:{si.get('mem_a',0)//1024}/{si.get('mem_t',0)//1024}MB Disk:{si.get('df','?')}MB")
 L("2 Models...")
 ml=ML();L(f"  {len(ml)}: {[m['name'] for m in ml]}")
 L("3 Bench...")
 bk=[]
 for m in ml:
  L(f"  {m['name']}...")
  r=BM(m["name"]);bk.append(r)
  L(f"    → {r.get('tps','?')} tps" if r.get("st")=="ok" else f"    → FAIL {r.get('err','')}")
 L("4 Report...")
 jp,mp,rep=WR(si,ml,bk)
 L(f"JSON {jp}");L(f"MD {mp}");L(f"Hash {rep['hash']}")
 print("\n--- RESULTS ---")
 if not bk:print("  No models. Start ollama + pull one.")
 for b in bk:print(f"  {b['model']}: {b.get('tps','FAIL')}")
 print(f"\nNext: cat $HOME/agapenet/MASTER_NODE_STATUS.md")
if __name__=="__main__":main()
