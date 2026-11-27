"""P5: AVL runs of the rev B model (avl/revB.avl from make_avl.py). Plain Python; AVL 3.52 exe path in AVL_EXE.

    python design/simulation/aero/run_avl.py [--exe path\\to\\avl352.exe] [--mass-empty g] [--xcg mm]

Writes avl/out/*.txt (raw AVL output), results.json and the figures in fig/:
- alpha sweep -4 .. 12 deg (elevator 0): CL, CDi, CD (with the SD7062 / plate profile drag), Cm;
- stability derivatives and the neutral point (ST);
- trimmed flight (elevator for Cm = 0) at the loaded and empty masses, sea-level to venue densities;
- CLmax by the critical-section method: the trimmed wing stalls when its most-loaded strip reaches the SD7062 section
  clmax (1.58 at Re 180 000, NeuralFoil polar) - the method used with VLM codes such as AVL / XFLR5; it ignores the
  stall progression, so it is a first-order estimate.
Numbers used (sources in design/optimisation/references.md and design/01_weather_design_inputs.md): water 996 g,
air density 1.05 kg/m3 (Bengaluru, design) and 1.15 kg/m3 (Chennai), g 9.81."""
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AVL_DIR = os.path.join(HERE, "avl")
OUTD = os.path.join(AVL_DIR, "out")
FIG = os.path.join(HERE, "fig")
AVL_EXE = os.environ.get("AVL_EXE", "")
WATER_G = 996.0
RHO = {"Bengaluru (design)": 1.05, "Chennai (venue)": 1.15}
CLMAX_SECTION = 1.58           # SD7062, Re 180 000 (design/aero/airfoil_polars_all.csv, NeuralFoil)
S, CREF = 0.2772, 0.280


def avl(cmds, tag):
    p = subprocess.run([AVL_EXE], input="\n".join(cmds) + "\n\n\n\nQUIT\n", cwd=AVL_DIR, capture_output=True, text=True,
                       timeout=120)
    os.makedirs(OUTD, exist_ok=True)
    open(os.path.join(OUTD, tag + ".txt"), "w").write(p.stdout)
    return p.stdout


def num(txt, key):
    m = re.findall(r"%s\s*=\s*([-0-9.Ee+]+)" % re.escape(key), txt)
    return float(m[-1]) if m else float("nan")


def sweep():
    rows = []
    for a in range(-4, 13):
        t = avl(["LOAD revB.avl", "OPER", "A A %g" % a, "X"], "alpha_%+03d" % a)
        rows.append(dict(alpha=a, CL=num(t, "CLtot"), CD=num(t, "CDtot"), CDi=num(t, "CDind"), Cm=num(t, "Cmtot")))
    return rows


def stability(cl):
    t = avl(["LOAD revB.avl", "OPER", "A C %.4f" % cl, "D2 PM 0", "X", "ST"], "stability_CL%.2f" % cl)
    keys = ["CLa", "Cma", "Cnb", "Clb", "CYb", "Xnp", "Cmq", "Cnr", "Clp"]
    d = {k: num(t, k) for k in keys}
    d["elevator"] = num(t, "elevator")
    d["alpha"] = num(t, "Alpha")
    return d


def strips_clmax(cl):
    """wing CL at which the most-loaded wing strip reaches the section clmax (trimmed with the elevator)."""
    t = avl(["LOAD revB.avl", "OPER", "A C %.4f" % cl, "D2 PM 0", "X", "FS"], "strips_CL%.2f" % cl)
    cls = []
    in_wing = False
    for line in t.splitlines():
        if "Surface #" in line:
            in_wing = "Wing" in line
        if in_wing:
            f = line.split()
            if len(f) >= 15 and f[0].isdigit():
                try:
                    cls.append(float(f[9]))          # j Xle Yle Zle Chord Area c_cl ai cl_norm cl cd ...
                except ValueError:
                    pass
    cmax = max(cls) if cls else float("nan")
    cl_tot = num(t, "CLtot")
    return cl_tot * CLMAX_SECTION / cmax, cmax, cl_tot


def trim(mass_g, rho, v):
    W = mass_g / 1000.0 * 9.81
    cl = 2 * W / (rho * v * v * S)
    t = avl(["LOAD revB.avl", "OPER", "A C %.4f" % cl, "D2 PM 0", "X"], "trim_%dg_%.2f_%.1f" % (mass_g, rho, v))
    cd = num(t, "CDtot")
    return dict(mass_g=mass_g, rho=rho, V=v, CL=cl, alpha=num(t, "Alpha"), elevator=num(t, "elevator"), CD=cd,
                LD=cl / cd, drag_N=0.5 * rho * v * v * S * cd, power_W=0.5 * rho * v ** 3 * S * cd)


def main():
    global AVL_EXE
    a = sys.argv
    if "--exe" in a:
        AVL_EXE = a[a.index("--exe") + 1]
    empty = float(a[a.index("--mass-empty") + 1]) if "--mass-empty" in a else 708.0
    xcg = float(a[a.index("--xcg") + 1]) if "--xcg" in a else 80.0
    if abs(xcg - 80.0) > 1e-6:
        src = open(os.path.join(AVL_DIR, "revB.avl")).read()
        src = re.sub(r"(#Xref Yref Zref  \(CG\)\n)([-0-9.]+)", lambda m: m.group(1) + "%.4f" % (xcg / 1000.0), src)
        open(os.path.join(AVL_DIR, "revB.avl"), "w").write(src)
    loaded = empty + WATER_G
    res = dict(empty_g=empty, loaded_g=loaded, xcg_mm=xcg)
    res["sweep"] = sweep()
    res["stab_cruise"] = stability(0.5)
    xnp = res["stab_cruise"]["Xnp"]
    res["static_margin_pct"] = 100.0 * (xnp - xcg / 1000.0) / CREF
    clmax, cmax, clt = strips_clmax(1.0)
    res["CLmax_trimmed"] = clmax
    res["stall"] = {}
    for site, rho in RHO.items():
        for lab, m in (("loaded", loaded), ("empty", empty)):
            W = m / 1000.0 * 9.81
            res["stall"]["%s, %s" % (lab, site)] = math.sqrt(2 * W / (rho * S * clmax))
    res["trim"] = []
    for site, rho in RHO.items():
        for m in (loaded, empty):
            for v in (10.0, 12.0, 14.0, 16.0):
                res["trim"].append(dict(site=site, **trim(m, rho, v)))
    json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    print("Xnp %.1f mm, static margin %.1f %% MAC (CG X %.0f), CLa %.3f /rad, Cma %.3f /rad" % (
        1000 * xnp, res["static_margin_pct"], xcg, res["stab_cruise"]["CLa"], res["stab_cruise"]["Cma"]))
    print("CLmax trimmed (critical section) %.3f; stall speeds:" % clmax,
          {k: round(v, 2) for k, v in res["stall"].items()})
    for r in res["trim"]:
        if r["V"] in (10.0, 12.0):
            print("  %-20s %5.0f g V %4.1f: CL %.3f alpha %5.2f elev %6.2f deg  CD %.4f  L/D %.1f  drag %.2f N  P %.1f W" % (
                r["site"], r["mass_g"], r["V"], r["CL"], r["alpha"], r["elevator"], r["CD"], r["LD"], r["drag_N"], r["power_W"]))


if __name__ == "__main__":
    main()
