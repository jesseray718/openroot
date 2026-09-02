#!/usr/bin/env python3
"""Comparative CFD: Linear/Staged vs Phi-Spiral Vortex"""
import math
PHI=(1+math.sqrt(5))/2;RHO=1.175;CP=1005;G=9.81;MU=1.84e-5;PR=0.71;K=0.026

class LinearStaged:
    def __init__(self,n=5,a=100.0,solar=1000.0):
        self.n=n;self.a=a;self.A=n*a;self.Q=solar
    def mdot(self):return RHO*0.44*self.A*0.5
    def Qnet(self):i=self.A*self.Q;return i*0.95*(1-0.038-0.093)/1000
    def dT(self):return(self.Qnet()*1000/self.n)/(self.mdot()*CP)*self.n
    def pathL(self):return self.n*10.0
    def resT(self):return self.pathL()/0.5
    def dP(self):
        f=0.05;v=0.5;Dh=0.02;L=10.0
        df=f*(L/Dh)*(0.5*RHO*v**2);dt=2*(0.5*RHO*v**2)
        return self.n*(df+dt)
    def power(self,H=100.0,eta=0.40):
        Ac=math.pi*4.0;dT=self.dT();Ta=25+dT/2+273.15
        vc=math.sqrt(2*G*H*dT/Ta);md=RHO*Ac*vc
        return eta*md*G*H*(dT/Ta)/1000
    def results(self):
        dT=self.dT();P=self.power();dP=self.dP()
        return{"model":"A:Linear/Staged","path_m":self.pathL(),"vel":0.5,
               "resT_s":self.resT(),"mdot":round(self.mdot(),1),
               "dP_Pa":round(dP,1),"dT_C":round(dT,2),
               "Texit_C":round(25+dT,2),"power_kW":round(P,2),
               "WperPa":round(P*1000/max(dP,1),2)}

class PhiSpiral:
    def __init__(self,D=6.0,H=30.0,solar=1000.0):
        self.D=D;self.H=H;self.r0=D/2;self.p=PHI*D
        self.dc=D/(PHI**2);self.Ain=math.pi*(D/2)**2
        self.Aout=math.pi*(self.dc/2)**2;self.Q=solar
    def pathL(self):
        dz=self.H/500;L=0.0
        for i in range(500):
            z=i*dz;Dl=self.D*(1-0.382*z/self.H)
            L+=math.sqrt(dz**2+(2*math.pi*(Dl/2)*dz/self.p)**2)
        return L
    def vel(self):
        vi=2.8;vo=min(vi*math.sqrt(self.Ain/self.Aout),1.5*vi)
        return vi,vo,(vi+vo)/2
    def mdot(self):return RHO*self.Ain*self.vel()[0]
    def dT(self):
        Dawg=self.D*0.8;wa=math.pi*Dawg*self.H*0.6
        q=wa*self.Q*0.95*(1-0.04-0.08)
        return q/(self.mdot()*CP)
    def resT(self):return self.pathL()/self.vel()[2]
    def dP(self):
        _,_,va=self.vel();L=self.pathL();Dh=self.dc
        f=0.03;fc=0.80
        return fc*f*(L/Dh)*(0.5*RHO*va**2)
    def power(self,eta=0.40):
        vi,vo,_=self.vel();dT=self.dT();Ta=25+dT/2+273.15
        md=RHO*self.Aout*vo
        Pjet=0.5*md*vo**2;Pb=eta*md*G*self.H*(dT/Ta)
        return(Pjet*eta+Pb)/1000
    def results(self):
        vi,vo,va=self.vel();dT=self.dT();P=self.power();dP=self.dP()
        return{"model":"B:Phi-Spiral","path_m":round(self.pathL(),1),
               "vel":round(va,2),"resT_s":round(self.resT(),1),
               "mdot":round(self.mdot(),1),"dP_Pa":round(dP,1),
               "dT_C":round(dT,2),"Texit_C":round(25+dT,2),
               "power_kW":round(P,2),
               "WperPa":round(P*1000/max(dP,1),2)}

def run():
    a=LinearStaged();b=PhiSpiral();ra=a.results();rb=b.results()
    print("="*65)
    print("LINEAR vs PHI-SPIRAL: HEAD TO HEAD")
    print("="*65)
    fmt="| {:<25} | {:>14} | {:>14} |"
    print(fmt.format("Metric","Linear/Staged","Phi-Spiral"))
    print("-"*65)
    pairs=[("Path Length (m)","path_m"),("Avg Velocity (m/s)","vel"),
           ("Residence Time (s)","resT_s"),("Mass Flow (kg/s)","mdot"),
           ("Pressure Drop (Pa)","dP_Pa"),("Delta-T (C)","dT_C"),
           ("Exit Temp (C)","Texit_C"),("Net Power (kW)","power_kW"),
           ("W per Pa","WperPa")]
    for label,key in pairs:
        print(fmt.format(label,str(ra[key]),str(rb[key])))
    print("="*65)
    rpp=rb["WperPa"]/max(ra["WperPa"],0.01)
    rdt=rb["dT_C"]/max(ra["dT_C"],0.01)
    print(f" Power/Pressure ratio B/A: {rpp:.2f}x")
    print(f" Delta-T ratio B/A:       {rdt:.2f}x")
    if rpp>1 and rdt>1:print(" GREEN LIGHT: Phi-Spiral wins")
    elif rpp>1:print(" YELLOW: Better W/Pa but dT needs work")
    else:print(" RED: Linear wins. Adjust spiral geometry.")
    print(" NOTE: All values pending physical validation")

if __name__=="__main__":run()
