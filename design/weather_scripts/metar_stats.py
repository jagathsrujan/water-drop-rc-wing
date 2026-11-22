import csv, numpy as np, collections, sys
KT=0.514444
def run(fn, month, label):
    R=[]
    for r in csv.DictReader(open(fn)):
        v=r['valid']; m=int(v[5:7])
        if m!=month: continue
        R.append(r)
    hr=np.array([int(r['valid'][11:13]) for r in R]); date=np.array([r['valid'][:10] for r in R])
    f=lambda k: np.array([float(r[k]) if r[k] not in ('M','T','') else np.nan for r in R])
    T=(f('tmpf')-32)/1.8; RH=f('relh'); D=f('drct'); V=f('sknt')*KT; G=f('gust')*KT
    wx=np.array([r['wxcodes'] for r in R])
    yrs=sorted(set(d[:4] for d in date))
    print(f"\n===== {label}: {len(R)} reports, {len(set(date))} days, years {yrs[0]}-{yrs[-1]} =====")
    print("hour  T_mean RH  V_mean V_p50 V_p90 V_p99  calm%  gust_rep%")
    for H in range(6,20):
        s=(hr==H)&~np.isnan(V)
        print(f"{H:02d}   {np.nanmean(T[hr==H]):5.1f} {np.nanmean(RH[hr==H]):4.0f}  {V[s].mean():4.1f} {np.median(V[s]):4.1f} {np.percentile(V[s],90):4.1f} {np.percentile(V[s],99):4.1f}  {np.mean(V[s]<0.5)*100:4.0f}  {np.mean(~np.isnan(G[hr==H]))*100:4.1f}")
    day=(hr>=8)&(hr<=17)
    Vd=V[day&~np.isnan(V)]
    print(f"daytime wind: V<3 {np.mean(Vd<3)*100:.0f}%, 3-5 {np.mean((Vd>=3)&(Vd<5))*100:.0f}%, 5-7 {np.mean((Vd>=5)&(Vd<7))*100:.0f}%, >=7 {np.mean(Vd>=7)*100:.0f}%, max {Vd.max():.1f}")
    Gd=G[day&~np.isnan(G)]
    if len(Gd): print(f"daytime reported gusts: n={len(Gd)} ({len(Gd)/day.sum()*100:.1f}% of reports), median {np.median(Gd):.1f}, p90 {np.percentile(Gd,90):.1f}, max {Gd.max():.1f} m/s")
    names=['N','NE','E','SE','S','SW','W','NW']
    for lab,sel in [("08-11",(hr>=8)&(hr<=11)),("12-17",(hr>=12)&(hr<=17))]:
        ok=sel&~np.isnan(D)&(V>=0.5)&(D>0)
        sec=((D[ok]+22.5)//45).astype(int)%8; cnt=np.bincount(sec,minlength=8)/ok.sum()*100
        msp=[V[ok][sec==i].mean() if (sec==i).any() else 0 for i in range(8)]
        vrb=np.mean((V[sel]>=0.5)&((D[sel]==0)|np.isnan(D[sel])))*100
        print(f"dir {lab}: "+"  ".join(f"{names[i]} {cnt[i]:.0f}%({msp[i]:.1f})" for i in range(8))+f"  VRB {vrb:.0f}%")
    rainy=np.array([any(t in w for t in ('RA','DZ','TS','SH')) for w in wx])
    dates=sorted(set(date))
    dr=[rainy[(date==d)].any() for d in dates]; drd=[rainy[(date==d)&day].any() for d in dates]
    ts=[np.array(['TS' in w for w in wx])[(date==d)].any() for d in dates]
    print(f"days with any rain/drizzle report: {np.mean(dr)*100:.0f}% ; with rain report 08-17 h: {np.mean(drd)*100:.0f}% ; thunder days {np.mean(ts)*100:.0f}%")
    # daily Tmax
    tx=[np.nanmax(T[date==d]) for d in dates]; tn=[np.nanmin(T[date==d]) for d in dates]
    print(f"Tmax mean {np.nanmean(tx):.1f} p95 {np.nanpercentile(tx,95):.1f}; Tmin mean {np.nanmean(tn):.1f} p5 {np.nanpercentile(tn,5):.1f}")
    # per-year rain days for spread
    print("rain-report days per year: "+", ".join(f"{y}:{sum(1 for d,x in zip(dates,dr) if d[:4]==y and x)}" for y in yrs))
run("VOMM.csv",1,"VOMM Chennai airport, January")
run("VOBG.csv",12,"VOBG Bengaluru HAL, December")
run("VOBL.csv",12,"VOBL Bengaluru Kempegowda, December")
