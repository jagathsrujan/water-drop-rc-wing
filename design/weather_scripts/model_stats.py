import json, sys, math
import numpy as np
def load(fn, month):
    d=json.load(open(fn)); h=d['hourly']
    t=np.array(h['time']); m=np.array([int(x[5:7]) for x in t]); hr=np.array([int(x[11:13]) for x in t])
    k=m==month
    out={v:np.array(h[v],dtype=float)[k] for v in h if v!='time'}
    out['hr']=hr[k]; out['date']=np.array([x[:10] for x in t])[k]; out['elev']=d['elevation']
    return out
def rho(T,p,RH):
    es=6.1078*10**(7.5*T/(T+237.3)); e=RH/100*es
    return (p-e)*100/(287.05*(T+273.15)) + e*100/(461.5*(T+273.15))
def dalt(r): # ISA density altitude
    return 44330.8*(1-(r/1.225)**0.234969)
def report(name,fn,month):
    D=load(fn,month); print(f"\n===== {name}  (model elev {D['elev']} m) =====")
    r=rho(D['temperature_2m'],D['surface_pressure'],D['relative_humidity_2m'])
    D['rho']=r
    day=(D['hr']>=8)&(D['hr']<=17)
    print("hour  T_mean T_p5 T_p95  RH  p_hPa  rho   DA_m  V_mean V_p50 V_p90 G_p50 G_p90 G_p99")
    for H in range(6,20):
        s=D['hr']==H; T=D['temperature_2m'][s]; V=D['wind_speed_10m'][s]; G=D['wind_gusts_10m'][s]
        print(f"{H:02d}   {T.mean():5.1f} {np.percentile(T,5):5.1f} {np.percentile(T,95):5.1f} {D['relative_humidity_2m'][s].mean():4.0f} {D['surface_pressure'][s].mean():6.1f} {r[s].mean():.3f} {dalt(r[s].mean()):5.0f}  {V.mean():4.1f} {np.median(V):4.1f} {np.percentile(V,90):4.1f}  {np.median(G):4.1f} {np.percentile(G,90):4.1f} {np.percentile(G,99):4.1f}")
    # daily
    dates=np.unique(D['date'])
    tmax=[D['temperature_2m'][D['date']==x].max() for x in dates]; tmin=[D['temperature_2m'][D['date']==x].min() for x in dates]
    rain=np.array([D['precipitation'][D['date']==x].sum() for x in dates]); rainday=np.array([D['precipitation'][(D['date']==x)&day].sum() for x in dates])
    print(f"daily Tmax mean {np.mean(tmax):.1f} (p95 {np.percentile(tmax,95):.1f}, max {np.max(tmax):.1f}); Tmin mean {np.mean(tmin):.1f} (p5 {np.percentile(tmin,5):.1f}, min {np.min(tmin):.1f})")
    print(f"days {len(dates)}; days with rain>=1mm: {np.mean(rain>=1)*100:.0f}% ; >=10mm {np.mean(rain>=10)*100:.0f}% ; daytime(08-17) rain>=0.5mm {np.mean(rainday>=0.5)*100:.0f}% ; monthly mean total {rain.sum()/len(np.unique([x[:4] for x in dates])):.0f} mm")
    print(f"daytime rho: mean {r[day].mean():.3f}, p5(worst) {np.percentile(r[day],5):.3f}, min {r[day].min():.3f}; DA worst p5 {dalt(np.percentile(r[day],5)):.0f} m")
    print(f"daytime RH mean {D['relative_humidity_2m'][day].mean():.0f}%, dew point mean {D['dew_point_2m'][day].mean():.1f} C")
    # wind direction rose daytime, morning vs afternoon
    for lab,sel in [("08-11",(D['hr']>=8)&(D['hr']<=11)),("12-17",(D['hr']>=12)&(D['hr']<=17))]:
        wd=D['wind_direction_10m'][sel]; ws=D['wind_speed_10m'][sel]
        sec=((wd+22.5)//45).astype(int)%8; names=['N','NE','E','SE','S','SW','W','NW']
        cnt=np.bincount(sec,minlength=8)/len(sec)*100
        msp=[ws[sec==i].mean() if (sec==i).any() else 0 for i in range(8)]
        print(f"dir {lab}: "+"  ".join(f"{names[i]} {cnt[i]:.0f}%({msp[i]:.1f})" for i in range(8)))
    Vd=D['wind_speed_10m'][day]; Gd=D['wind_gusts_10m'][day]
    print(f"daytime wind: share V<3 {np.mean(Vd<3)*100:.0f}%, V 3-5 {np.mean((Vd>=3)&(Vd<5))*100:.0f}%, V 5-7 {np.mean((Vd>=5)&(Vd<7))*100:.0f}%, V>=7 {np.mean(Vd>=7)*100:.0f}% ; gust>=8 {np.mean(Gd>=8)*100:.0f}%, gust>=10 {np.mean(Gd>=10)*100:.0f}%, max gust {Gd.max():.1f}")
    print(f"gust factor (G/V daytime median) {np.median(Gd/np.maximum(Vd,0.5)):.2f}")
report("Bengaluru, December 2015-2025","blr.json",12)
report("Chennai (IIT Madras), January 2016-2026","maa.json",1)
