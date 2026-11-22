"""Wing chord sweep: stall speed, cruise CL, Re, wing mass (balsa built-up) and score.
Uses the 2D polars from design/aero/airfoil_polars_all.csv (NeuralFoil) for alpha and Cd.
Run with a Python that has the packages in design/aero/requirements.txt (pip install -r design/aero/requirements.txt)."""
import csv, math, subprocess, sys, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, '..', 'aero', 'airfoil_polars_all.csv'))))
b = 1.0; e = 0.85; water = 996.0; other = 440.0
rho_t, rho_v = 1.05, 1.15          # Bengaluru test, Chennai venue (stage 1)
nu = 1.75e-5
k3d = 0.85                          # wing CLmax / airfoil CLmax (rectangular, no flaps, trim loss) (interp.)
def polar(name, Re=180000, nc=9.0):
    R = [r for r in rows if r['airfoil'] == name and float(r['Re']) == Re and float(r['Ncrit']) == nc]
    a = np.array([float(r['alpha']) for r in R]); cl = np.array([float(r['CL']) for r in R]); cd = np.array([float(r['CD']) for r in R])
    i = np.argmax(cl); return a[:i+1], cl[:i+1], cd[:i+1], cl[i]
def balsa_mass(c, tc):
    out = subprocess.run([sys.executable, os.path.join(HERE, 'wing_mass_model.py'), str(c), str(tc)], capture_output=True, text=True).stdout
    return float([l for l in out.splitlines() if l.startswith('Balsa')][0].split('wing')[1].split('g')[0])
for name, tc in (('SD7062', 0.14), ('Clark Y', 0.117), ('MH 114', 0.131)):
    a, cl, cd, clmax = polar(name)
    CLw = k3d * clmax
    print(f"\n{name}: airfoil CLmax {clmax:.2f} -> wing CLmax {CLw:.2f}")
    print(" chord  S     AR   wing g empty g score  loaded kg  WL kg/m2  Vs test  Vs venue  CL@13 m/s loaded/empty  Re@13  alpha2D@CL0.6")
    for c in (0.22, 0.24, 0.26, 0.28, 0.30, 0.32):
        S = b * c; wm = balsa_mass(c, tc); em = other + wm; ml = (em + water) / 1000
        W = ml * 9.81; We = em / 1000 * 9.81
        Vs_t = math.sqrt(2 * W / (rho_t * S * CLw)); Vs_v = math.sqrt(2 * W / (rho_v * S * CLw))
        CLc = 2 * W / (rho_t * S * 13**2); CLe = 2 * We / (rho_t * S * 13**2)
        o = np.argsort(cl); a06 = np.interp(0.6, cl[o], a[o])
        print(f" {c:.2f}  {S:.3f} {b/c:4.2f}  {wm:5.0f}  {em:5.0f}  {water/em*100:5.1f}   {ml:.3f}     {ml/S:4.1f}     {Vs_t:4.1f}     {Vs_v:4.1f}       {CLc:.2f} / {CLe:.2f}          {13*c/nu/1e3:3.0f}k   {a06:4.1f}")
