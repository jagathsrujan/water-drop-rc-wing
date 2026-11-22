"""Printed vs balsa wing (rev A geometry) - numbers for printed_vs_balsa_wing.md.
Re-uses the part volumes in design/cad/mass_table.csv (no re-modelling). Units: g, mm, MPa, N.
Every material value is listed in MAT / BALSA below with its source; (interp.) values are estimates.
Run: python3 design/studies/printed_vs_balsa_calc.py   (from the repo root)"""
import csv, math, os
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rows = [r for r in csv.DictReader(open(os.path.join(REPO, "design/cad/mass_table.csv"))) if r["part"] != "TOTAL"]

# ---------------- airfoil geometry (SD7062 x 280) ----------------
pts = []
for ln in open(os.path.join(REPO, "design/aero/airfoil_coords/sd7062.dat")).read().splitlines()[1:]:
    s = ln.split()
    if len(s) == 2:
        pts.append((float(s[0]) * 280, float(s[1]) * 280))
ile = min(range(len(pts)), key=lambda i: pts[i][0])
up, lo = pts[:ile + 1][::-1], pts[ile:]
def zat(c, x):
    for (x0, z0), (x1, z1) in zip(c, c[1:]):
        if x0 <= x <= x1:
            return z0 + (z1 - z0) * (x - x0) / (x1 - x0)
    return c[0][1] if x < c[0][0] else c[-1][1]
def arclen(c, xa, xb, n=4000):
    L = 0
    for i in range(n):
        x0, x1 = xa + (xb - xa) * i / n, xa + (xb - xa) * (i + 1) / n
        L += math.hypot(x1 - x0, zat(c, x1) - zat(c, x0))
    return L
def area(xa, xb, n=4000):
    return sum((zat(up, xa + (xb - xa) * (i + .5) / n) - zat(lo, xa + (xb - xa) * (i + .5) / n)) * (xb - xa) / n for i in range(n))
def radius(c, x1, x2, x3):
    (a, b, cc) = [(x, zat(c, x)) for x in (x1, x2, x3)]
    ax, ay = a; bx, by = b; cx, cy = cc
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay) + (cx**2 + cy**2) * (ay - by)) / d
    uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx) + (cx**2 + cy**2) * (bx - ax)) / d
    return math.hypot(ax - ux, ay - uy)
XW = 72.6
s_dbox = arclen(up, 0, XW) + arclen(lo, 0, XW)
h_web = zat(up, XW) - zat(lo, XW)
A_dbox = area(0.001, XW)
A_sec = area(0.001, 279.9)
fwd_frac = area(0.001, 78.6) / A_sec
R_top_aft = radius(up, 30, 50, 72)       # flattest part of the D-box top skin
R_top_fwd = radius(up, 5, 15, 30)
s_shell = arclen(up, 0, 78.6) + arclen(lo, 0, 78.6)
A_shell = s_shell * 984e-6               # m2
print(f"D-box: skin arc {s_dbox:.1f} mm, web {h_web:.1f} mm, enclosed area {A_dbox:.0f} mm2; top-skin radius {R_top_fwd:.0f} mm (x5-30), {R_top_aft:.0f} mm (x30-72)")
print(f"airfoil area {A_sec:.0f} mm2, area fraction forward of x=78.6: {fwd_frac:.2f}; D-box shell area (x0-78.6, 984 mm) {A_shell:.3f} m2")

# ---------------- materials ----------------
# printed: rho g/cm3, E_xy, E_z (MPa), st_xy, st_z (tensile MPa), bend_z (MPa), charpy unnotched xy / z (kJ/m2), HDT 0.45 MPa (C)
MAT = {
    "PLA":      dict(rho=1.24, Exy=2680, Ez=2160, sxy=39, sz=35, bz=68, cxy=26.6, cz=13.8, hdt=57, cte=68e-6),   # Bambu PLA Basic TDS V2.0; cte (interp.)
    "PETG":     dict(rho=1.27, Exy=1810, Ez=1540, sxy=34, sz=23, bz=48, cxy=None, cz=None, hdt=69, cte=60e-6),  # Bambu PETG HF TDS V1.0 (3rd-party copy); impact not read; cte (interp.)
    "ASA":      dict(rho=1.07, Exy=2200, Ez=1500, sxy=37, sz=24, bz=40, cxy=None, cz=None, hdt=95, cte=90e-6),  # (interp.) typical ASA filament TDS, Bambu ASA sheet not read
    "PETG-CF":  dict(rho=1.25, Exy=2460, Ez=1340, sxy=59, sz=38, bz=62, cxy=41.2, cz=10.7, hdt=74, cte=40e-6),  # Bambu PETG-CF TDS V2.0; cte (interp.)
}
# foamed grades: E and strength scaled from the unfoamed to the foamed colorFabb LW-PLA points (3350 MPa/43 MPa at 1.2 g/cm3,
# 860 MPa/10 MPa at 45 % flow = ~0.54 g/cm3): E ~ rho^1.70, strength ~ rho^1.82 (interp. power-law fit through 2 TDS points)
nE = math.log(3350 / 860) / math.log(1.2 / 0.54)
nS = math.log(43 / 10) / math.log(1.2 / 0.54)
def lw(rho, base="LW-PLA"):
    if base == "LW-PLA":
        E = 3350 * (rho / 1.2) ** nE; s = 43 * (rho / 1.2) ** nS; hdt = 53   # Bambu PLA Aero HDT 0.45 MPa 53 C; colorFabb HDT-B 60 C (unfoamed)
    else:  # ASA Aero: Bambu TDS (low-foam specimens) E 2010 / 1180 (Z), 32 / 21 MPa, HDT 85 C at 0.45 MPa; foamed by the same law (interp.)
        E = 2010 * (rho / 0.99) ** nE; s = 32 * (rho / 0.99) ** nS; hdt = 85
    # Z (across layers) bending strength ratio from PLA Aero / ASA Aero TDS: 17/45 and 24/58 -> ~0.4 of XY bending; XY bending ~1.9 x tensile
    return dict(rho=rho, Exy=E, Ez=0.9 * E, sxy=s, sz=0.75 * s, bz=0.4 * 1.9 * s, cxy=None, cz=3.1, hdt=hdt, cte=70e-6)
for r in (0.55, 0.70, 0.85):
    MAT[f"LW-PLA {r:.2f}"] = lw(r)
MAT["ASA-Aero 0.70"] = lw(0.70, "ASA")
print(f"foam law: E ~ rho^{nE:.2f}, strength ~ rho^{nS:.2f}")
for k in ("LW-PLA 0.55", "LW-PLA 0.70", "LW-PLA 0.85", "ASA-Aero 0.70"):
    m = MAT[k]; print(f"  {k}: E {m['Exy']:.0f} MPa, tensile {m['sxy']:.1f} MPa, Z bend {m['bz']:.1f} MPa")

# balsa along grain (L) / across (T): E_L from PNG medium class 2037 MPa, Wood Handbook 3400 MPa @ ~160 (secondhand) -> scaled linear with density (interp.)
BALSA = {90: dict(EL=1700), 100: dict(EL=1900), 130: dict(EL=2500), 160: dict(EL=3400)}
for rho, b in BALSA.items():
    b["ET"] = 0.015 * b["EL"]; b["G"] = 0.045 * b["EL"]        # Wood Handbook ratios E_T/E_L 0.015, G_LT/E_L 0.037, G_LR/E_L 0.054 (mean 0.045)
    b["sc"] = 9.2 * rho / 150; b["sb_T"] = 1.5 * rho / 130      # compression || 9.2 MPa @ 120-180 class (PNG study); across-grain bending 1.5 MPa @130 (interp.)
    b["c_perp"] = 0.07 * 9.2 * rho / 150                       # compression perpendicular ~7 % of parallel (interp.)

print("\nSPECIFIC PROPERTIES")
for rho, b in BALSA.items():
    print(f"  balsa {rho}: E_L {b['EL']} E/rho {b['EL']/rho:.1f} MJ/kg | E_T {b['ET']:.0f} -> {b['ET']/rho:.2f} | sc {b['sc']:.1f} -> {b['sc']/rho*1000:.0f} kJ/kg | skin bend eff E_L^(1/3)/rho {b['EL']**(1/3)/(rho/1000):.0f}, E_T^(1/3)/rho {b['ET']**(1/3)/(rho/1000):.0f}")
for k, m in MAT.items():
    print(f"  {k}: E/rho {m['Exy']/1000/m['rho']:.2f} MJ/kg (Z {m['Ez']/1000/m['rho']:.2f}) | s/rho {m['sxy']/m['rho']:.0f} kJ/kg (Z {m['sz']/m['rho']:.0f}) | E^(1/3)/rho {m['Exy']**(1/3)/m['rho']:.0f} | HDT {m['hdt']}")

# ---------------- 1. MASS: direct substitution ----------------
def fill(p):
    if p.startswith("LE"): return 0.50
    if p.startswith("TE_") or p.startswith("Ail_TE"): return 0.85
    if p.startswith(("FalseSpar", "TipCap", "TipRib_", "Rib_110", "Ail_LE")): return 0.66
    return 1.00
GRP = [("TipRib", "ribs"), ("Rib", "ribs"), ("DBox", "D-box skins"), ("CSheet", "centre sheeting"), ("LE", "LE"),
       ("SparBalsa", "spar caps, balsa part"), ("FalseSpar", "false spar"), ("ShearWeb", "shear webs"), ("Caps_", "cap strips"),
       ("TE_", "TE wedges"), ("TipCap", "tip caps"), ("Ail_", "ailerons")]
groups, keep, balsa_m, balsa_v = {}, 0.0, 0.0, 0.0
for r in rows:
    m = float(r["mass_g"])
    if r["material"] in ("sheet", "light", "medium", "hard"):
        v = float(r["volume_cm3"]); balsa_m += m; balsa_v += v
        g = next(n for k, n in GRP if r["part"].startswith(k))
        d = groups.setdefault(g, dict(bal=0, v=0, veff=0)); d["bal"] += m; d["v"] += v; d["veff"] += v * fill(r["part"])
    else:
        keep += m
veff = sum(d["veff"] for d in groups.values())
E0, W0, WATER = 580.0, 156.6, 996.0
def dscore(dm, e0=E0): return 100 * (e0 / (e0 + dm) - 1)
def vstall(dm): return 8.8 * math.sqrt((E0 + WATER + dm) / (E0 + WATER))
print(f"\nbalsa parts {balsa_m:.1f} g, {balsa_v:.1f} cm3 -> printed volume {veff:.1f} cm3; kept parts {keep:.1f} g")
cols = ["PLA", "PETG", "ASA", "PETG-CF", "LW-PLA 0.55", "LW-PLA 0.70", "LW-PLA 0.85", "ASA-Aero 0.70"]
print("| group | balsa g | balsa cm3 | printed cm3 | " + " | ".join(cols) + " |")
for k, d in sorted(groups.items(), key=lambda kv: -kv[1]["bal"]):
    print(f"| {k} | {d['bal']:.1f} | {d['v']:.1f} | {d['veff']:.1f} | " + " | ".join(f"{d['veff']*MAT[c]['rho']:.0f}" for c in cols) + " |")
DIRECT = {}
print("\nDIRECT SUBSTITUTION")
for c in cols:
    tot = keep + veff * MAT[c]["rho"]; DIRECT[c] = tot; dm = tot - W0
    print(f"  {c:14s} {tot:5.0f} g  x{tot/W0:.1f}  {dm:+5.0f} g  score {dscore(dm):+5.1f} % (597 g basis {dscore(dm, 597):+5.1f} %)  loaded stall {vstall(dm):.1f} m/s")
A_sheet = (arclen(up, 0, 80) + arclen(lo, 0, 80)) * 984e-6 + (arclen(up, 80, 255) + arclen(lo, 80, 255)) * 112e-6
print(f"  film on sheeted areas {A_sheet:.3f} m2 = {A_sheet*50:.1f} g (can be left off printed skins)")

# ---------------- redesigned variants ----------------
print("\nREDESIGNS (different design, not rev A)")
ribs_bal = groups["ribs"]["bal"]
removed = 8.49 + 20.25 + 6.64 + fwd_frac * ribs_bal + A_shell * 50       # LE, D-box skins, front web, rib noses, film on the D-box
R1 = {}
for case, t, rho, k_int in [("R1a low", 0.45, 0.44, 1.35), ("R1a mid", 0.45, 0.58, 1.45), ("R1a high", 0.45, 0.71, 1.60),
                           ("R1b low", 0.80, 0.44, 1.10), ("R1b mid", 0.80, 0.58, 1.10), ("R1b high", 0.80, 0.71, 1.10)]:
    a = t * rho                                     # kg/m2
    skin = A_shell * a * 1000
    web = h_web * 984e-6 * a * 1000
    nose = 0.10 * skin
    shell = (skin + web + nose) * k_int + 2.0       # k_int: geodetic stiffeners (R1a) or 55 mm diaphragms (R1b); +2 g joints
    tot = W0 - removed + shell; R1[case] = (tot, t, rho)
    print(f"  {case}: t {t} rho {rho} ({a:.2f} kg/m2) shell {shell:.1f} g, removed {removed:.1f} g -> wing {tot:.0f} g ({tot-W0:+.0f} g, score {dscore(tot-W0):+.1f} %)")
fixed = 9.16 + 11.2 + 1.3 + 1.2 + 0.8 + 4.0
R2 = {}
for case, a, k in [("R2 low", 0.20, 1.35), ("R2 mid", 0.26, 1.45), ("R2 high", 0.32, 1.60)]:
    tot = 0.585 * a * 1000 * k + fixed; R2[case] = tot
    print(f"  {case}: {a} kg/m2 x {k} + {fixed:.1f} -> {tot:.0f} g ({tot-W0:+.0f} g, score {dscore(tot-W0):+.1f} %)")
rv = groups["ribs"]["v"]
print(f"  ASA-Aero R2 mid (same areal as LW-PLA mid): {R2['R2 mid']:.0f} g")
for n, rho in [("LW-PLA 0.70", 0.70), ("PETG", 1.27)]:
    same = rv * rho; tr = rv * (1.6 / 2.0) * (0.45 / 0.67) * rho
    print(f"  H1 printed ribs {n}: same geometry {same:.0f} g ({same-ribs_bal:+.0f}); truss 1.6 mm, 55 % open {tr:.0f} g ({tr-ribs_bal:+.0f}, score {dscore(tr-ribs_bal):+.1f} %)")

# ---------------- 2. STRENGTH ----------------
print("\nSPAR BENDING n = 6, M 8.9 N.m, h 33 mm")
F = 8.9 / 0.033; Ec, Ac, Ab = 130e3, 3.0, 18.0     # carbon E 130 GPa (interp.)
w, L = 42 / 0.495, 0.495
for k, E, s in [("hard balsa", 3400, 9.2 * 160 / 150), ("PLA", 2680, 39), ("PETG", 1810, 34), ("PETG-CF", 2460, 59), ("LW-PLA 0.70", MAT["LW-PLA 0.70"]["Exy"], MAT["LW-PLA 0.70"]["sxy"])]:
    EA = Ec * Ac + E * Ab; eps = F / EA; EI = 2 * EA * 16.5**2 * 1e-6
    EI2 = 2 * E * Ab * 16.5**2 * 1e-6
    print(f"  {k:11s}: carbon {Ec*eps:.0f} MPa (allow ~400 -> {400/(Ec*eps):.1f}), cap {E*eps:.1f} MPa vs {s:.0f}, strain {eps*1e6:.0f} ue, EI {EI:.0f} N.m2, tip {w*L**4/(8*EI)*1000:.1f} mm"
          f" | no carbon: cap {F/Ab:.1f} MPa (margin {s/(F/Ab):.1f}), tip {w*L**4/(8*EI2)*1000:.0f} mm")
eps6 = F / (Ec * Ac + 3400 * Ab)
def M_root(m_tot, m_w, n=6): return n * 9.81 * ((m_tot / 2) * 0.212 - (m_w / 2) * 0.247)
dP = (DIRECT["PLA"] - W0) / 1000
print(f"  root moment model (n=6, lift at 0.212 m, wing mass at 0.247 m): rev A {M_root(1.576, 0.184):.1f} N.m; PLA direct {M_root(1.576 + dP, 0.184 + dP):.1f} N.m (wing mass relief)")
for k, mw in [("rev A", 184.0), ("LW-PLA 0.70 direct", DIRECT["LW-PLA 0.70"] + 27.4), ("PLA direct", DIRECT["PLA"] + 27.4), ("R2 mid", R2["R2 mid"] + 27.4)]:
    Mi = 10 * 9.81 * (mw / 2000) * 0.247
    print(f"  hard landing, wing inertia only, 10 g (interp.): {k} wing {mw:.0f} g -> root moment {Mi:.1f} N.m ({Mi/8.9*100:.0f} % of the n=6 design moment)")
for k, t, tau in [("balsa 1.5 web", 1.5, 1.9), ("PLA 1.5 web", 1.5, 0.6 * 39), ("LW-PLA 0.70 web", 1.5, 0.6 * MAT["LW-PLA 0.70"]["sxy"])]:
    s = 42 / (t * h_web); print(f"  {k}: shear {s:.2f} MPa vs {tau:.1f} -> margin {tau/s:.1f}")

print("\nSKIN COMPRESSION BUCKLING at n = 6 (top D-box skin, panel 53 x 75 mm, strain %d ue)" % (eps6 * 1e6))
a_p, b_p = 53.0, 75.0
k_c = (b_p / a_p + a_p / b_p) ** 2
def sig_cr_iso(E, t, R): return k_c * math.pi**2 * E / (12 * 0.91) * (t / b_p) ** 2 + 0.3 * E * t / R / math.sqrt(3 * 0.91)
def sig_cr_balsa(b, t, R):
    D11, D22, D3 = b["EL"] * t**3 / 12, b["ET"] * t**3 / 12, (0.01 * b["ET"] + 2 * b["G"]) * t**3 / 12
    N = math.pi**2 / b_p**2 * (D11 * (b_p / a_p) ** 2 + 2 * D3 + D22 * (a_p / b_p) ** 2)
    return N / t + 0.3 * math.sqrt(b["EL"] * b["ET"]) * t / R / math.sqrt(3 * 0.91)
B90 = BALSA[90]
cases = [("balsa 1.5 (90 kg/m3)", None, 1.5, B90["EL"])]
for k in ("PLA", "PETG", "LW-PLA 0.70"):
    cases.append((f"{k} 1.5", k, 1.5, MAT[k]["Exy"]))
for case in ("R1a low", "R1a mid", "R1b low", "R1b mid"):
    tot, t, rho = R1[case]; cases.append((f"{case} {t} mm @ {rho}", None, t, lw(rho)["Exy"]))
for name, k, t, E in cases:
    R = R_top_aft
    sc = sig_cr_balsa(B90, t, R) if name.startswith("balsa") else sig_cr_iso(E, t, R)
    if name.startswith("R1a"):   # geodetic stiffeners: panel 25 x 25 mm (interp.)
        sc = 4 * math.pi**2 * E / (12 * 0.91) * (t / 25) ** 2 + 0.3 * E * t / R / math.sqrt(3 * 0.91)
    s = E * eps6
    print(f"  {name:26s}: applied {s:.2f} MPa, sigma_cr {sc:.2f} MPa -> margin {sc/s:.1f}")

print("\nD-BOX TORSION (Bredt), design torque T (interp.)")
qd = 0.5 * 1.15 * 25**2
Mcm = (0.08 + 0.2165 * math.radians(15) * 325 / 495) * qd * (0.495 * 0.28) * 0.28
Mlift = 42 * 0.040
T = 4.0
print(f"  torque: Cm {Mcm:.2f} + lift offset {Mlift:.2f} = {Mcm+Mlift:.2f} N.m -> design T = {T} N.m")
q = T * 1000 / (2 * A_dbox)
web_bal = h_web / (BALSA[130]["G"] * 1.5)
def tau_cr_iso(E, t, b, R): return (5.35 + 4 * (b / 75) ** 2) * math.pi**2 * E / (12 * 0.91) * (t / b) ** 2 + 0.1 * E * t / R
tc = []
tc.append(("balsa 1.5 skin + balsa web", B90["G"] * 1.5, web_bal, 1.5, 1.9, (5.35 + 4 * (53 / 75) ** 2) * math.pi**2 * math.sqrt(B90["EL"] * B90["ET"]) / (12 * 0.91) * (1.5 / 53) ** 2 + 0.1 * math.sqrt(B90["EL"] * B90["ET"]) * 1.5 / R_top_aft))
for k in ("PLA", "PETG", "ASA", "LW-PLA 0.70"):
    m = MAT[k]; G = m["Exy"] / 2.7
    tc.append((f"{k} 1.5", G * 1.5, h_web / (G * 1.5), 1.5, 0.6 * m["sz"], tau_cr_iso(m["Exy"], 1.5, 53, R_top_aft)))
for case in ("R1a low", "R1a mid", "R1b low", "R1b mid"):
    tot, t, rho = R1[case]; m = lw(rho); G = m["Exy"] / 2.7
    b = 25 if case.startswith("R1a") else 53
    tc.append((f"{case} {t} mm @ {rho}", G * t, h_web / (G * t), t, 0.6 * m["sz"], tau_cr_iso(m["Exy"], t, b, R_top_aft)))
GJ0 = None
for name, Gt, wterm, t, tau_a, tcr in tc:
    GJ = 4 * A_dbox**2 / (s_dbox / Gt + wterm) * 1e-6
    GJ0 = GJ0 or GJ
    tau = q / t
    print(f"  {name:26s}: GJ {GJ:6.1f} N.m2 ({GJ/GJ0:4.1f} x)  tau {tau:.2f} MPa: strength {tau_a:.1f} (margin {tau_a/tau:.1f}), shear buckling {tcr:.2f} (margin {tcr/tau:.1f})")

print("\nSKIN DENT (point load on a plate): crack load ~ sigma_weak t^2, dent stiffness ~ E_weak t^3; ratio to balsa 1.5 mm")
ref_c, ref_k = B90["sb_T"] * 1.5**2, B90["ET"] * 1.5**3
dent = [("balsa 1.5 D-box (weak = across grain)", B90["sb_T"], B90["ET"], 1.5)]
for k in ("PLA", "PETG", "PETG-CF", "LW-PLA 0.70"):
    m = MAT[k]; dent.append((f"{k} 1.5 curved, printed LE-up (weak = Z)", m["bz"], m["Ez"], 1.5))
for k in ("PLA", "LW-PLA 0.70"):
    m = MAT[k]; dent.append((f"{k} 1.5 flat-printed panel (XY)", 1.9 * m["sxy"] if k.startswith("LW") else 76, m["Exy"], 1.5))
for case in ("R1a low", "R1a mid", "R1b low", "R1b mid"):
    tot, t, rho = R1[case]; m = lw(rho); dent.append((f"{case} {t} mm @ {rho} (Z)", m["bz"], m["Ez"], t))
for name, s, E, t in dent:
    print(f"  {name:44s}: crack {s*t*t/ref_c:5.1f} x   stiffness {E*t**3/ref_k:6.1f} x")

print("\nRIB SQUEEZE: 50 N over 20 mm of rib edge (interp.)")
for name, t, s in [("balsa 2 mm (across grain)", 2.0, BALSA[130]["c_perp"]), ("PLA 2 mm flat print", 2.0, 39), ("PETG 2 mm", 2.0, 34),
                   ("LW-PLA 0.70 2 mm", 2.0, MAT["LW-PLA 0.70"]["sxy"]), ("LW-PLA 0.58 truss 1.6 mm", 1.6, lw(0.58)["sxy"])]:
    st = 50 / (t * 20); print(f"  {name:28s}: {st:.2f} MPa vs {s:.1f} -> margin {s/st:.1f}")
for tt in (1.2, 1.6):
    E = lw(0.58)["Exy"]; I = 3 * tt**3 / 12; P = math.pi**2 * E * I / (0.7 * 25) ** 2
    print(f"  truss strut {tt} x 3 mm, 25 mm, LW-PLA 0.58: P_cr {P:.1f} N each; 50 N on 3 struts = 16.7 N -> margin {P/16.7:.1f}")

print("\nIMPACT")
print(f"  balsa crush energy along grain: {0.7*9.2*0.7:.1f} MJ/m3 = {0.7*9.2*0.7/150*1000:.0f} J/g (150 kg/m3); across grain {0.7*0.65*0.7:.2f} MJ/m3 = {0.7*0.65*0.7/130*1000:.1f} J/g (interp.)")
print(f"  bending fracture energy density MOR^2/2E: balsa {16.6**2/(2*2037):.3f} MJ/m3 ({16.6**2/(2*2037)/0.15:.2f} J/g); PLA {76**2/(2*2750):.2f} ({76**2/(2*2750)/1.24:.2f} J/g); PLA Aero Z {17**2/(2*1410):.3f} ({17**2/(2*1410)/1.0:.2f} J/g)")
for k, mw in [("rev A", 184.0), ("LW-PLA 0.70 direct", DIRECT["LW-PLA 0.70"] + 27.4), ("PLA direct", DIRECT["PLA"] + 27.4), ("R1a mid", R1["R1a mid"][0] + 27.4), ("R2 mid", R2["R2 mid"] + 27.4)]:
    print(f"  wing KE at 9 m/s: {k} {0.5*mw/1000*81:.1f} J")

print("\nHEAT: margin of HDT (0.45 MPa) above 60 C surface; thermal stress against carbon for dT = 30 K")
print(f"  balsa: no softening; CTE ~4e-6/K along grain -> {BALSA[90]['EL']*4e-6*30:.2f} MPa")
for k in ("PLA", "PETG", "ASA", "PETG-CF", "LW-PLA 0.70", "ASA-Aero 0.70"):
    m = MAT[k]; print(f"  {k:14s}: HDT {m['hdt']} C, margin {m['hdt']-60:+d} C; thermal stress {m['Exy']*m['cte']*30:.1f} MPa vs tensile {m['sxy']:.0f} ({m['Exy']*m['cte']*30/m['sxy']*100:.0f} %)")
