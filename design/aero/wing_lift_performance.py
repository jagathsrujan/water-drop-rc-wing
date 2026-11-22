"""Wing rev A lift performance: nonlinear lifting line with the SD7062 2D polars.

Geometry: rectangular, span 0.990 m, chord 0.280 m, 0 deg dihedral, 0 twist (design/02_wing_plan.md).
Polars: design/aero/airfoil_polars_all.csv (NeuralFoil xlarge). Run from the repo root:
    python3 design/aero/wing_lift_performance.py
Outputs: printed tables + design/aero/wing_lift_curve.png, design/aero/wing_cl_distribution.png
"""
import csv, math, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
B, C = 0.990, 0.280
S = B * C
AR = B * B / S
G = 9.81
WATER = 0.996
EMPTY = 0.440 + 0.1566         # A1 rest of aircraft incl. 4 servos (interp., wing_mass_model.py) + wing rev A without servos
LOADED = EMPTY + WATER
RHO = {"Bengaluru test": 1.05, "Chennai venue": 1.15}
TAIL_ARM = 0.60                # (interp.) D-001 trim estimate
CLMAX_DERATED = 1.40           # sensitivity: 2D CLmax 11 % below NeuralFoil (interp.)

rows = list(csv.DictReader(open(os.path.join(HERE, "airfoil_polars_all.csv"))))


def polar(Re, nc=9.0, clcap=None):
    R = [r for r in rows if r["airfoil"] == "SD7062" and float(r["Re"]) == Re and float(r["Ncrit"]) == nc]
    a = np.array([float(r["alpha"]) for r in R])
    cl = np.array([float(r["CL"]) for r in R])
    cd = np.array([float(r["CD"]) for r in R])
    cm = np.array([float(r["CM"]) for r in R])
    o = np.argsort(a)
    a, cl, cd, cm = a[o], cl[o], cd[o], cm[o]
    if clcap is not None:
        cl = np.minimum(cl, clcap)
    return a, cl, cd, cm


def lin_params(pol):
    a, cl = pol[0], pol[1]
    m = (a >= -2) & (a <= 6)
    s, b = np.polyfit(a[m], cl[m], 1)
    return s * 180 / math.pi, -b / s                       # a0 per rad, alpha0 deg


def lifting_line(alpha_deg, pol, N=40, iters=400, damp=0.3):
    """Nonlinear lifting line, decambering method: linear Fourier (monoplane) solve with a
    per-station angle correction so that the local cl matches the 2D polar at the local
    effective angle. Symmetric loading, odd terms only, half span."""
    a2d, cl2d, cd2d, _ = pol
    a0, al0 = lin_params(pol)
    th = (np.arange(1, N + 1) - 0.5) * (math.pi / 2) / N   # half span, root near pi/2
    y = -B / 2 * np.cos(th)
    n = np.arange(1, 2 * N, 2)
    Smat = np.sin(np.outer(th, n))
    mu = C * a0 / (4 * B)
    M = Smat * (mu * n[None, :] + np.sin(th)[:, None])
    alpha = math.radians(alpha_deg)
    delta = np.zeros(N)
    for _ in range(iters):
        rhs = mu * (alpha + delta - math.radians(al0)) * np.sin(th)
        A = np.linalg.solve(M, rhs)
        ai = (Smat * n) @ A / np.sin(th)
        aeff = alpha - ai
        cl_lin = 4 * B / C * (Smat @ A)
        cl_pol = np.interp(np.degrees(aeff), a2d, cl2d)
        d_new = delta + (cl_pol - cl_lin) / a0
        if np.max(np.abs(d_new - delta)) < 1e-7:
            delta = d_new
            break
        delta = delta + damp * (d_new - delta)
    rhs = mu * (alpha + delta - math.radians(al0)) * np.sin(th)
    A = np.linalg.solve(M, rhs)
    CL = math.pi * AR * A[0]
    delta = sum(k * (A[i] / A[0]) ** 2 for i, k in enumerate(n) if i > 0)
    e = 1 / (1 + delta)
    ai = (Smat * n) @ A / np.sin(th)
    aeff = np.degrees(alpha - ai)
    cl = np.interp(aeff, a2d, cl2d)
    cdp = np.interp(aeff, a2d, cd2d)
    w = np.sin(th)                                       # dy weight in theta: dy = B/2 sin(th) dth
    CDp = np.sum(cdp * w) / np.sum(w)
    CDi = CL ** 2 / (math.pi * AR * e)
    return CL, CDi, CDp, e, y, cl


def lift_curve(pol, alphas):
    out = []
    for a in alphas:
        CL, CDi, CDp, e, y, cl = lifting_line(a, pol)
        out.append((a, CL, CDi, CDp, e, y, cl))
    return out


def summarise(curve, clmax2d):
    CLs = np.array([c[1] for c in curve])
    i_peak = int(np.argmax(CLs))
    first = None
    for c in curve:
        if np.max(c[6]) >= clmax2d - 0.005:
            first = c
            break
    return curve[i_peak], first


def main():
    alphas = np.arange(-4, 22.01, 0.5)
    base = polar(180000, 9.0)
    rough = polar(180000, 7.0)
    low = polar(120000, 9.0)
    derated = polar(180000, 9.0, clcap=CLMAX_DERATED)
    cases = {
        "Re 180k, Ncrit 9 (base)": base,
        "Re 120k, Ncrit 9": low,
        "Re 180k, Ncrit 7 (rough film)": rough,
        f"2D CLmax capped at {CLMAX_DERATED} (sensitivity)": derated,
    }
    curves = {}
    print(f"Wing: span {B} m, chord {C} m, S {S:.4f} m2, AR {AR:.3f}")
    print(f"Masses: empty {EMPTY*1000:.0f} g, loaded {LOADED*1000:.0f} g "
          f"(wing loading {LOADED*1000/(S*100):.1f} / {EMPTY*1000/(S*100):.1f} g/dm2)\n")

    # 2D slope and alpha0
    a, cl, _, cm = base
    m = (a >= -2) & (a <= 6)
    a2d_slope, b2d = np.polyfit(a[m], cl[m], 1)
    alpha0 = -b2d / a2d_slope
    cm0 = float(np.interp(0.6, cl[a < 14], cm[a < 14]))
    a0r = a2d_slope * 180 / math.pi
    k = a0r / (math.pi * AR)
    helm = a0r / (math.sqrt(1 + k * k) + k)
    print(f"2D: slope {a2d_slope:.4f} /deg ({a0r:.2f} /rad), alpha0 {alpha0:.2f} deg, Cm(c/4) at cl 0.6 {cm0:.3f}")

    print("\nCase                                   | 3D slope /deg | alpha0 | CL first local stall (alpha) | CL peak (alpha) | CLmax3D/clmax2D | e at CL 0.6")
    for name, pol in cases.items():
        cur = lift_curve(pol, alphas)
        curves[name] = cur
        CLs = np.array([c[1] for c in cur])
        mm = (alphas >= -2) & (alphas <= 6)
        s3, b3 = np.polyfit(alphas[mm], CLs[mm], 1)
        peak, first = summarise(cur, float(np.max(pol[1])))
        e06 = float(np.interp(0.6, CLs[:int(np.argmax(CLs))], [c[4] for c in cur][:int(np.argmax(CLs))]))
        print(f"{name:39s}| {s3:.4f}        | {-b3/s3:5.2f}  | {first[1]:.3f} ({first[0]:.1f})             "
              f"| {peak[1]:.3f} ({peak[0]:.1f})   | {peak[1]/np.max(pol[1]):.3f}           | {e06:.3f}")
    print(f"Helmbold check (base): 3D slope {helm*math.pi/180:.4f} /deg")

    # performance tables
    def CLw(name):
        """Usable wing CLmax = CL when the first station reaches the 2D clmax (conservative)."""
        cur = curves[name]
        return float(summarise(cur, float(np.max(cases[name][1])))[1][1])

    def alpha_at(name, CL):
        cur = curves[name]
        CLs = np.array([c[1] for c in cur]); i = int(np.argmax(CLs))
        return float(np.interp(CL, CLs[:i + 1], alphas[:i + 1]))

    def ld_at(name, CL):
        cur = curves[name]
        CLs = np.array([c[1] for c in cur]); i = int(np.argmax(CLs))
        CD = np.array([c[2] + c[3] for c in cur])
        return float(np.interp(CL, CLs[:i + 1], CD[:i + 1]))

    print("\nStall speed, m/s (1 g, wing alone / with tail download for Cm, tail arm 0.6 m interp.)")
    print("Case                                   | mass   | Bengaluru 1.05      | Chennai 1.15        | 30 deg bank (Blr) | 45 deg bank (Blr)")
    for name in (list(cases)[0], list(cases)[3]):
        CLmx = CLw(name)
        for lab, mass in (("loaded", LOADED), ("empty", EMPTY)):
            out = []
            for site, rho in RHO.items():
                W = mass * G
                vs = math.sqrt(2 * W / (rho * S * CLmx))
                q = 0.5 * rho * vs * vs
                for _ in range(5):
                    Lt = abs(cm0) * q * S * C / TAIL_ARM
                    vs = math.sqrt(2 * (W + Lt) / (rho * S * CLmx)); q = 0.5 * rho * vs * vs
                out.append((math.sqrt(2 * W / (rho * S * CLmx)), vs))
            vb = out[0][1]
            print(f"{name:39s}| {lab:6s} | {out[0][0]:.2f} / {out[0][1]:.2f}         | {out[1][0]:.2f} / {out[1][1]:.2f}         "
                  f"| {vb*math.sqrt(1/math.cos(math.radians(30))):.2f}             | {vb*math.sqrt(1/math.cos(math.radians(45))):.2f}")

    name = list(cases)[0]
    CLmx = CLw(name)
    print("\nCruise points (base polar, Bengaluru rho 1.05; CL includes the tail download)")
    print("V m/s | mass   | CL wing | wing alpha deg | wing CD | wing L/D | CL/CLmax | n max (stall-limited)")
    for V in (10, 11, 12, 13, 15, 18):
        for lab, mass in (("loaded", LOADED), ("empty", EMPTY)):
            q = 0.5 * 1.05 * V * V
            Lt = abs(cm0) * q * S * C / TAIL_ARM
            CL = (mass * G + Lt) / (q * S)
            if CL > CLmx:
                print(f"{V:5.0f} | {lab:6s} | {CL:.2f}    | stalled"); continue
            CD = ld_at(name, CL)
            print(f"{V:5.0f} | {lab:6s} | {CL:.3f}   | {alpha_at(name, CL):5.1f}          | {CD:.4f}  | {CL/CD:5.1f}    "
                  f"| {CL/CLmx:.2f}     | {CLmx*q*S/(mass*G):.2f}")

    # plots
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(base[0], base[1], color="#8a8a86", lw=1.2, ls=(0, (1, 1)), label="SD7062 2D airfoil (Re 180k, Ncrit 9)")
    colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]   # validated categorical slots 1-4
    styles = ["-", "--", "-.", ":"]                          # secondary encoding (contrast WARN on 3, 4)
    for (nm, cur), col, ls in zip(curves.items(), colors, styles):
        ax.plot(alphas, [c[1] for c in cur], color=col, ls=ls, lw=2, label="Wing 3D: " + nm)
    for lab, mass in ((f"loaded {LOADED:.2f} kg", LOADED),):
        for V in (11, 13):
            q = 0.5 * 1.05 * V * V
            CL = (mass * G + abs(cm0) * q * S * C / TAIL_ARM) / (q * S)   # same basis as the table
            ax.axhline(CL, color="#444", lw=0.6, ls=":")
            ax.text(-3.8, CL + 0.02, f"{lab}, {V} m/s, Bengaluru: CL {CL:.2f}", fontsize=8, color="#444")
    ax.set_xlim(-4, 22); ax.set_ylim(-0.2, 1.8)
    ax.set_xlabel("Angle of attack, deg (wing chord line)"); ax.set_ylabel("Lift coefficient")
    ax.set_title("Wing rev A lift curve (nonlinear lifting line, AR 3.54)")
    ax.grid(alpha=0.2, lw=0.5); [ax.spines[k].set_visible(False) for k in ("top", "right")]; ax.legend(fontsize=8, loc="lower right", frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "wing_lift_curve.png"), dpi=160)

    fig, ax = plt.subplots(figsize=(8, 4))
    cur = curves[list(cases)[0]]
    for a_show, col in ((4, "#86b6ef"), (8, "#3987e5"), (12, "#1c5cab"), (16, "#0d366b")):   # ordinal blue ramp
        c = cur[int(np.argmin(np.abs(alphas - a_show)))]
        ax.plot(np.abs(c[5]) * 1000, c[6] / np.max(base[1]), color=col, lw=1.8, label=f"alpha {a_show} deg, CL {c[1]:.2f}")
    ax.axvspan(112.5, 437.5, color="#8a8a86", alpha=0.10)
    ax.text(275, 0.05, "aileron (y 112.5-437.5)", ha="center", fontsize=8, color="#444")
    ax.axhline(1.0, color="#444", lw=0.6, ls=":")
    ax.set_xlim(0, 495); ax.set_ylim(0, 1.1)
    ax.set_xlabel("Span station y, mm (root = 0, tip = 495)"); ax.set_ylabel("local cl / 2D clmax")
    ax.set_title("Local lift along the half span (base polar): the root stalls first")
    ax.grid(alpha=0.2, lw=0.5); [ax.spines[k].set_visible(False) for k in ("top", "right")]; ax.legend(fontsize=8, frameon=False, loc="lower left")
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "wing_cl_distribution.png"), dpi=160)


if __name__ == "__main__":
    main()
