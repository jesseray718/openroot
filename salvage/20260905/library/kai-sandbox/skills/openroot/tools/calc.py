#!/usr/bin/env python3
# OpenRoot SI calculator — PLANNING ESTIMATES; verify vs supplier/engineer
import math
P={'cement_bag':16.0,'sand_m3':45.0,'gravel_m3':50.0,'mesh_m2':3.5,
   'labor_hr':50.0,'markup':0.35}   # EDIT to local prices (USD)
FT,IN,YD3,GAL=0.3048,0.0254,0.7646,3.785
f=lambda x:f"{x:,.2f}"
def concrete(v):  # 1:2:3 mix ~7 bags(42.6kg)/m3
    b=math.ceil(v*7);s=v*.5;g=v*.75
    return b,s,g,b*P['cement_bag']+s*P['sand_m3']+g*P['gravel_m3']
def mortar(v):    # ferrocement 1:2 ~15 bags/m3 (cement-rich by design)
    b=math.ceil(v*15);s=v*1.0
    return b,s,b*P['cement_bag']+s*P['sand_m3']
while 1:
    m=input("\n1 slab 2 ferro-shell 3 tank-vol 4 convert 5 quote 0 exit > ").strip()
    if m=='1':
        L,W,t=(float(input(k+" m: "))for k in("L","W","thick"))
        v=L*W*t*1.08;b,s,g,c=concrete(v)
        print(f"{f(v)} m³ | {b} bags | sand {f(s)} m³ | gravel {f(g)} m³ | mat ${f(c)}")
    elif m=='2':
        r=float(input("radius m: "));cv=float(input("coverage (0.5=hemisphere): "))
        t=float(input("thick m (0.03 typ): "));ly=int(input("mesh layers: "))
        sa=4*math.pi*r*r*cv;v=sa*t*1.10;mesh=sa*ly*1.15
        b,s,c=mortar(v);c+=mesh*P['mesh_m2']
        print(f"SA {f(sa)} m² | mortar {f(v)} m³ | {b} bags | sand {f(s)} m³ | mesh {f(mesh)} m² | mat ${f(c)}")
    elif m=='3':
        r,h=float(input("radius m: ")),float(input("height m: "))
        v=math.pi*r*r*h;print(f"{f(v)} m³ = {f(v*1000)} L = {f(v*1000/GAL)} gal")
    elif m=='4':
        u=input("a ft→m b in→mm c yd³→m³ d gal→L e kg→lb > ");x=float(input("val: "))
        print(f({'a':x*FT,'b':x*IN*1000,'c':x*YD3,'d':x*GAL,'e':x*2.2046}[u]))
    elif m=='5':
        mat=float(input("materials $: "));h=float(input("labor hrs: "))
        r=float(input(f"$/hr [{P['labor_hr']}]: ")or P['labor_hr'])
        k=float(input(f"markup [{P['markup']}]: ")or P['markup'])
        sub=mat+h*r;print(f"${f(mat)}+labor ${f(h*r)}=${f(sub)} | +{int(k*100)}% → QUOTE ${f(sub*(1+k))}")
    elif m=='0':break
