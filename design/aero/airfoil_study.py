#!/usr/bin/env python3
"""Airfoil comparison study with NeuralFoil (xlarge).

Usage:
    python airfoil_study.py <coords_dir> [out_dir]

<coords_dir> holds UIUC-format .dat files (Selig or Lednicer). NACA 4-digit
sections are generated here. Output (CSV, tables, PNG) goes to out_dir
(default: the folder of this script). Coordinate files are parsed as numbers only.
"""
import sys
import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import neuralfoil as nf

# name -> (label, source). source = ("file", filename) or ("naca", "4412")
AIRFOILS = [
    ("Clark Y", ("file", "clarky.dat")),
    ("NACA 4412", ("naca", "4412")),
    ("NACA 6412", ("naca", "6412")),
    ("E423", ("file", "e423.dat")),
    ("S1223", ("file", "s1223.dat")),
    ("SD7062", ("file", "sd7062.dat")),
    ("MH 114", ("file", "mh114.dat")),
    ("CH10", ("file", "ch10sm.dat")),
]
RES = [120e3, 180e3, 250e3]
NCRITS = [9.0, 7.0]
# The requested range is -4 to 18 deg. The run uses -8 to 24 deg (0.5 deg step) so that
# low-CL targets of highly cambered sections and CLmax near 18 deg are inside the grid.
# Plots show -4 to 18 deg only.
ALPHAS = np.arange(-8.0, 24.0001, 0.5)
PLOT_A = (-4.0, 18.0)
CL_TARGETS = [0.6, 0.8, 1.0, 1.2]
MAIN_RE, MAIN_NC = 180e3, 9.0
MODEL = "xlarge"


# ---------------------------------------------------------------- geometry
def naca4(code, n=100):
    m, p, t = int(code[0]) / 100, int(code[1]) / 10, int(code[2:]) / 100
    beta = np.linspace(0, np.pi, n)
    x = 0.5 * (1 - np.cos(beta))
    yt = 5 * t * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x**2
                  + 0.2843 * x**3 - 0.1036 * x**4)  # 0.1036: finite TE, about 0.2 pct
    yc = np.where(x < p, m / p**2 * (2 * p * x - x**2),
                  m / (1 - p)**2 * ((1 - 2 * p) + 2 * p * x - x**2))
    dyc = np.where(x < p, 2 * m / p**2 * (p - x), 2 * m / (1 - p)**2 * (p - x))
    th = np.arctan(dyc)
    xu, yu = x - yt * np.sin(th), yc + yt * np.cos(th)
    xl, yl = x + yt * np.sin(th), yc - yt * np.cos(th)
    # Selig order: upper TE -> LE -> lower TE
    X = np.concatenate([xu[::-1], xl[1:]])
    Y = np.concatenate([yu[::-1], yl[1:]])
    return np.column_stack([X, Y])


def read_dat(path):
    """Parse a UIUC .dat file (numbers only). Returns Selig-ordered Nx2 array."""
    rows, blank_after = [], []
    with open(path, "r", errors="ignore") as f:
        lines = f.read().splitlines()[1:]  # skip title
    for ln in lines:
        parts = ln.replace(",", " ").split()
        if len(parts) == 2:
            try:
                rows.append((float(parts[0]), float(parts[1])))
                continue
            except ValueError:
                pass
        if not parts and rows:
            blank_after.append(len(rows))
    a = np.array(rows)
    if a[0, 0] > 1.5:  # Lednicer: first row = point counts
        nu, nl = int(a[0, 0]), int(a[0, 1])
        a = a[1:]
        up, lo = a[:nu], a[nu:nu + nl]
        return np.vstack([up[::-1], lo[1:]])
    return a


def load(name_src, coords_dir):
    kind, v = name_src
    if kind == "naca":
        return naca4(v)
    return read_dat(os.path.join(coords_dir, v))


def split_surfaces(c):
    i = int(np.argmin(c[:, 0]))
    up = c[:i + 1][::-1]   # LE -> TE
    lo = c[i:]             # LE -> TE
    return up, lo


def geometry(c):
    up, lo = split_surfaces(c)
    xg = np.linspace(0, 1, 2001)
    yu = np.interp(xg, up[:, 0], up[:, 1])
    yl = np.interp(xg, lo[:, 0], lo[:, 1])
    th = yu - yl
    cam = 0.5 * (yu + yl)
    it, ic = int(np.argmax(th)), int(np.argmax(np.abs(cam)))
    te = up[-1, 1] - lo[-1, 1]
    # lower-surface concavity: line from LE to the lower TE point
    line = lo[-1, 1] * xg
    dep = yl - line  # positive where the lower surface lies above the line (concave)
    conc = dep.max()
    return dict(t=th[it] * 100, xt=xg[it] * 100, camber=cam[ic] * 100,
                xcam=xg[ic] * 100, te=te * 100, conc=conc * 100,
                xconc=xg[int(np.argmax(dep))] * 100,
                lower="concave" if conc > 0.005 else ("nearly flat (slightly concave)" if conc > 0.002 else "flat/convex"))


# ---------------------------------------------------------------- solver
def run_polar(c, Re, nc):
    r = nf.get_aero_from_coordinates(coordinates=c, alpha=ALPHAS, Re=Re,
                                     n_crit=nc, model_size=MODEL)
    return {k: np.asarray(r[k], float) for k in ("CL", "CD", "CM", "analysis_confidence")}


def metrics(p):
    CL, CD, CM, conf = p["CL"], p["CD"], p["CM"], p["analysis_confidence"]
    ok = np.isfinite(CL) & np.isfinite(CD) & np.isfinite(CM)
    out = dict(nan_rows=int((~ok).sum()))
    CLm = np.where(ok, CL, -9)
    i = int(np.argmax(CLm))
    out["CLmax"], out["a_CLmax"] = CL[i], ALPHAS[i]
    out["at_limit"] = bool(i >= len(ALPHAS) - 2)
    j = i + 4  # +2 deg
    out["drop2"] = CL[i] - CL[j] if j < len(CL) else np.nan
    # pre-stall branch, up to CLmax, forced monotonic in CL
    pre = np.arange(0, i + 1)
    pre = pre[ok[pre]]
    clp = np.maximum.accumulate(CL[pre])
    keep = np.concatenate([[True], np.diff(clp) > 1e-6])
    pre, clp = pre[keep], clp[keep]
    for t in CL_TARGETS:
        if clp[0] <= t <= clp[-1]:
            cd = np.interp(t, clp, CD[pre])
            out[f"Cd@{t}"], out[f"LD@{t}"] = cd, t / cd
            out[f"conf@{t}"] = float(np.interp(t, clp, conf[pre]))
        else:
            out[f"Cd@{t}"] = out[f"LD@{t}"] = out[f"conf@{t}"] = np.nan
    if clp[0] <= 0.8 <= clp[-1]:
        out["Cm@0.8"] = np.interp(0.8, clp, CM[pre])
        out["a@0.8"] = np.interp(0.8, clp, ALPHAS[pre])
    else:
        out["Cm@0.8"] = out["a@0.8"] = np.nan
    ld = CL[pre] / CD[pre]
    k = int(np.argmax(ld))
    out["LDmax"], out["CL@LDmax"], out["a@LDmax"] = ld[k], CL[pre][k], ALPHAS[pre][k]
    pos = CL[pre] > 0.05
    en = np.where(pos, np.abs(CL[pre])**1.5 / CD[pre], 0.0)
    k = int(np.argmax(en))
    out["E15max"], out["CL@E15max"] = en[k], CL[pre][k]
    # confidence over the pre-stall range
    sel = pre[ALPHAS[pre] >= -4.0]
    out["conf_min"] = float(conf[sel].min())
    out["conf_mean"] = float(conf[sel].mean())
    # alpha for CL=0 (zero-lift angle)
    out["alpha0"] = float(np.interp(0.0, clp, ALPHAS[pre])) if clp[0] <= 0 <= clp[-1] else np.nan
    out["CLalpha"] = float(np.polyfit(ALPHAS[pre][(clp > 0.2) & (clp < 1.0)], clp[(clp > 0.2) & (clp < 1.0)], 1)[0]) \
        if ((clp > 0.2) & (clp < 1.0)).sum() > 3 else np.nan
    return out


# ---------------------------------------------------------------- output
def f(x, n=3):
    return "n/a" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{n}f}"


def md_table(header, rows):
    s = "| " + " | ".join(header) + " |\n|" + "---|" * len(header) + "\n"
    for r in rows:
        s += "| " + " | ".join(str(v) for v in r) + " |\n"
    return s


def main():
    coords_dir = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)
    shapes, geo, polars, mets = {}, {}, {}, {}
    for name, src in AIRFOILS:
        c = load(src, coords_dir)
        shapes[name], geo[name] = c, geometry(c)
        for Re in RES:
            for nc in NCRITS:
                p = run_polar(c, Re, nc)
                polars[(name, Re, nc)] = p
                mets[(name, Re, nc)] = metrics(p)
        print("done", name, flush=True)

    # CSV and JSON
    keys = list(next(iter(mets.values())).keys())
    with open(os.path.join(out_dir, "airfoil_results.csv"), "w") as fh:
        fh.write("airfoil,Re,Ncrit," + ",".join(keys) + "\n")
        for (n, Re, nc), m in mets.items():
            fh.write(f"{n},{int(Re)},{nc}," + ",".join(str(m[k]) for k in keys) + "\n")
    with open(os.path.join(out_dir, "airfoil_polars_all.csv"), "w") as fh:
        fh.write("airfoil,Re,Ncrit,alpha,CL,CD,CM,confidence\n")
        for (n, Re, nc), p in polars.items():
            for i, a in enumerate(ALPHAS):
                fh.write(f"{n},{int(Re)},{nc},{a},{p['CL'][i]:.5f},{p['CD'][i]:.6f},"
                         f"{p['CM'][i]:.5f},{p['analysis_confidence'][i]:.3f}\n")

    names = [n for n, _ in AIRFOILS]
    T = []
    T.append("### Table A. Geometry\n" + md_table(
        ["Airfoil", "t/c %", "x/c of t", "Camber %", "x/c of camber", "TE thickness %c (mm at 270 mm chord)",
         "Lower surface", "Max concavity %c (at x/c %)"],
        [[n, f(geo[n]["t"], 2), f(geo[n]["xt"], 1), f(geo[n]["camber"], 2), f(geo[n]["xcam"], 1),
          f"{geo[n]['te']:.3f} ({geo[n]['te'] * 2.7:.2f})", geo[n]["lower"], f"{geo[n]['conc']:.2f} ({geo[n]['xconc']:.0f})"]
         for n in names]))
    def row_main(n, nc):
        m = mets[(n, MAIN_RE, nc)]
        return m
    for nc in NCRITS:
        tag = "main case" if nc == MAIN_NC else "rough case"
        T.append(f"### Table B{'' if nc == MAIN_NC else '2'}. Stall, drag, moment: Re 180k, Ncrit {nc:g} ({tag})\n" + md_table(
            ["Airfoil", "CLmax", "alpha CLmax", "CL drop in 2 deg", "alpha0 deg",
             "Cd@0.6", "Cd@0.8", "Cd@1.0", "Cd@1.2", "Cm@0.8"],
            [[n, f(row_main(n, nc)["CLmax"], 2), f(row_main(n, nc)["a_CLmax"], 1),
              f(row_main(n, nc)["drop2"], 3), f(row_main(n, nc)["alpha0"], 1)] +
             [f(row_main(n, nc)[f"Cd@{t}"], 4) for t in CL_TARGETS] +
             [f(row_main(n, nc)["Cm@0.8"], 3)] for n in names]))
        T.append(f"### Table C{'' if nc == MAIN_NC else '2'}. L/D: Re 180k, Ncrit {nc:g}\n" + md_table(
            ["Airfoil", "L/D@0.6", "L/D@0.8", "L/D@1.0", "L/D@1.2", "L/D max", "CL at L/D max",
             "max CL^1.5/Cd", "CL at max CL^1.5/Cd"],
            [[n] + [f(row_main(n, nc)[f"LD@{t}"], 1) for t in CL_TARGETS] +
             [f(row_main(n, nc)["LDmax"], 1), f(row_main(n, nc)["CL@LDmax"], 2),
              f(row_main(n, nc)["E15max"], 1), f(row_main(n, nc)["CL@E15max"], 2)] for n in names]))
    hdr = ["Airfoil"] + [f"Re {int(Re/1000)}k Nc{nc:g}" for Re in RES for nc in NCRITS]
    T.append("### Table D. CLmax (alpha at CLmax, deg) for all Re and Ncrit\n" + md_table(
        hdr, [[n] + [f"{mets[(n, Re, nc)]['CLmax']:.2f} ({mets[(n, Re, nc)]['a_CLmax']:.1f})"
                     for Re in RES for nc in NCRITS] for n in names]))
    T.append("### Table E. Stall sharpness (CL drop in the 2 deg after CLmax) for all Re and Ncrit\n" + md_table(
        hdr, [[n] + [f(mets[(n, Re, nc)]['drop2'], 3) for Re in RES for nc in NCRITS] for n in names]))
    T.append("### Table F. Cd at CL 0.8 for all Re and Ncrit\n" + md_table(
        hdr, [[n] + [f(mets[(n, Re, nc)]['Cd@0.8'], 4) for Re in RES for nc in NCRITS] for n in names]))
    T.append("### Table H. NeuralFoil confidence at the CL targets (Re 180k, Ncrit 9)\n" + md_table(
        ["Airfoil", "conf@0.6", "conf@0.8", "conf@1.0", "conf@1.2"],
        [[n] + [f(mets[(n, MAIN_RE, MAIN_NC)][f"conf@{t}"], 2) for t in CL_TARGETS] for n in names]))
    T.append("### Table G. Solver checks (pre-stall range, all cases)\n" + md_table(
        ["Airfoil", "NaN rows", "CLmax at alpha limit (24 deg)?", "Min NeuralFoil confidence", "Mean confidence"],
        [[n, sum(mets[(n, Re, nc)]["nan_rows"] for Re in RES for nc in NCRITS),
          "yes" if any(mets[(n, Re, nc)]["at_limit"] for Re in RES for nc in NCRITS) else "no",
          f(min(mets[(n, Re, nc)]["conf_min"] for Re in RES for nc in NCRITS), 2),
          f(np.mean([mets[(n, Re, nc)]["conf_mean"] for Re in RES for nc in NCRITS]), 2)] for n in names]))
    with open(os.path.join(out_dir, "airfoil_tables.md"), "w") as fh:
        fh.write("\n".join(T))
    print("\n".join(T))

    # ------------------------------------------------------------- plots
    cols = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#17becf"]
    ls = ["-", "-", "--", "-", "-", "--", "-", "--"]
    fig, ax = plt.subplots(1, 3, figsize=(17, 5.6))
    for k, n in enumerate(names):
        p = polars[(n, MAIN_RE, MAIN_NC)]
        w = (ALPHAS >= PLOT_A[0]) & (ALPHAS <= PLOT_A[1])
        ax[0].plot(ALPHAS[w], p["CL"][w], color=cols[k], ls=ls[k], label=n)
        ax[1].plot(p["CD"][w], p["CL"][w], color=cols[k], ls=ls[k], label=n)
        ist = int(np.argmax(p["CL"])) + 2  # drop the post-stall loop in the L/D panel
        w2 = w & (np.arange(len(ALPHAS)) <= ist)
        ax[2].plot(p["CL"][w2], (p["CL"] / p["CD"])[w2], color=cols[k], ls=ls[k], label=n)
    ax[0].set(xlabel="alpha (deg)", ylabel="CL", title="CL vs alpha")
    ax[1].set(xlabel="CD", ylabel="CL", title="Drag polar", xlim=(0, 0.06))
    ax[2].set(xlabel="CL", ylabel="CL/CD", title="L/D vs CL", xlim=(0, 2.0))
    for a in ax:
        a.grid(alpha=0.3)
    ax[0].legend(fontsize=8, ncol=2)
    fig.suptitle(f"NeuralFoil ({MODEL}), Re = {int(MAIN_RE/1000)}k, Ncrit = {MAIN_NC:g}")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "airfoil_polars.png"), dpi=140)
    plt.close(fig)

    fig, axs = plt.subplots(4, 2, figsize=(10, 9.5), sharex=True, sharey=True)
    for k, n in enumerate(names):
        a = axs.flat[k]
        c = shapes[n]
        a.fill(c[:, 0], c[:, 1], color=cols[k], alpha=0.35)
        a.plot(c[:, 0], c[:, 1], color=cols[k], lw=1.2)
        a.plot([0, 1], [0, 0], "k:", lw=0.5)
        g = geo[n]
        a.set_title(f"{n}: t {g['t']:.1f}%, camber {g['camber']:.1f}%", fontsize=9)
        a.set_aspect("equal")
        a.set_ylim(-0.08, 0.2)
        a.grid(alpha=0.25)
    fig.suptitle("Airfoil outlines, same scale (x/c, y/c)")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "airfoil_shapes.png"), dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    for k, n in enumerate(names):
        for a, nc, st in ((ax[0], 9.0, "-o"), (ax[1], 7.0, "-o")):
            a.plot([r / 1000 for r in RES], [mets[(n, r, nc)]["CLmax"] for r in RES], st,
                   color=cols[k], ls=ls[k], ms=4, label=n)
    for a, nc in ((ax[0], 9), (ax[1], 7)):
        a.set(xlabel="Re (thousand)", ylabel="CLmax", title=f"CLmax vs Re, Ncrit {nc}")
        a.set_xticks([120, 180, 250])
        a.grid(alpha=0.3)
    ax[0].legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "airfoil_Re_sensitivity.png"), dpi=140)
    plt.close(fig)
    print("outputs in", out_dir)


if __name__ == "__main__":
    main()
