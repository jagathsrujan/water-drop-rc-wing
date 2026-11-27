"""P5: AVL (Drela & Youngren, MIT, v3.52, GPL) model of the rev B water-drop aircraft, written from the same parameter
files as the CAD (wing_params / fus_params / bal_params via revb_params), so the aero model is the modelled aircraft.

    python design/simulation/aero/make_avl.py      -> design/simulation/aero/avl/revB.avl, revB_pod.dat, sd7062.dat

Geometry (aircraft frame, metres; X aft from the wing LE, Y right, Z up; CG X 0.080):
- wing: rectangular 0.990 x 0.280 m, SD7062 (design/aero/airfoil_coords), incidence +3 deg (wing_params INCIDENCE /
  build_wing.py), dihedral 0 (D-012), ailerons y 112.5 .. 437.5 mm, hinge x/c 0.75;
- horizontal stabiliser: LE X 647, chord 132, half span 245, Z +45 (fus_params, D-057), flat plate (3 mm built-up
  frame under film), elevator hinge x/c 0.70 (HINGE_X 739.65);
- fin: root chord 110 at Z -30 (tail-block top), tip chord 85 at Z +135, hinge line vertical at X 739.65 (rudder 35 %);
- pod: a body of revolution with the pod's equivalent radius sqrt(width x height / pi) along X (bal_params PLAN,
  BOTTOM, TOP), as AVL's slender-body model (a first-order estimate of the pod's destabilising moment);
- booms (10 mm tubes) are not modelled (thin: small effect, stated in the report).
Profile drag: CDCL from the SD7062 polar at Re 180 000 (NeuralFoil xlarge, design/aero/airfoil_polars_all.csv):
(CL, CD) = (0.031, 0.0160), (0.555, 0.0119), (1.443, 0.0232); stab and fin: flat 3 mm plate, CD0 0.012 (estimate).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.dirname(os.path.dirname(HERE))
for p in ("cad_fuselage_balsa/scripts", "cad_fuselage/scripts", "cad_reservoir/scripts", "cad/scripts", "cad_fusion_revB/scripts"):
    sys.path.insert(0, os.path.join(DESIGN, p))
from revb_params import WP, FP, BP     # noqa: E402

OUT = os.path.join(HERE, "avl")
M = 1e-3
X_CG = 0.080
CDCL_WING = (0.031, 0.0160, 0.555, 0.0119, 1.443, 0.0232)


def airfoil():
    src = os.path.join(DESIGN, "aero", "airfoil_coords", "sd7062.dat")
    lines = [l for l in open(src).read().splitlines() if l.strip()]
    open(os.path.join(OUT, "sd7062.dat"), "w").write("\n".join(lines) + "\n")


def interp(pts, x):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[0][1] if x < pts[0][0] else pts[-1][1]


def pod_body():
    """equivalent body of revolution: r(x) = sqrt(4 hw (zt - zb) / pi) / 2 * ... (area-equivalent circle)."""
    xs = [BP.X_FRONT + i * (BP.X_END - BP.X_FRONT) / 40.0 for i in range(41)]
    rows = []
    for x in xs:
        hw = interp(BP.PLAN, x)
        h = interp(BP.TOP, x) - interp(BP.BOTTOM, x)
        r = math.sqrt(2.0 * hw * h / math.pi)               # area 2 hw x h = pi r^2
        rows.append((x, r))
    L = BP.X_END - BP.X_FRONT
    # AVL BFILE: airfoil-like x/L, y/L of the upper and lower contour (TE -> LE -> TE)
    up = [((x - BP.X_FRONT) / L, r / L) for x, r in rows]
    lo = [((x - BP.X_FRONT) / L, -r / L) for x, r in rows]
    pts = list(reversed(up)) + lo[1:]
    open(os.path.join(OUT, "revB_pod.dat"), "w").write("revB pod (equivalent body)\n" +
                                                        "\n".join("%.5f %.5f" % p for p in pts) + "\n")
    zc = 0.5 * (interp(BP.TOP, 100.0) + interp(BP.BOTTOM, 100.0))
    return L, zc


def main():
    os.makedirs(OUT, exist_ok=True)
    airfoil()
    Lpod, zpod = pod_body()
    c, b2 = WP.CHORD * M, WP.HALF_SPAN * M
    inc = WP.__dict__.get("INCIDENCE", 3.0)
    ail0, ail1 = WP.AIL_Y[0] * M, WP.AIL_Y[1] * M
    xh_w = (WP.AIL_X[0]) / WP.CHORD                         # aileron hinge x/c (210 / 280)
    cs, bs2, xs, zs = FP.STAB_C * M, FP.STAB_HS * M, FP.STAB_LE_X * M, FP.STAB_Z * M
    xh_s = (FP.HINGE_X - FP.STAB_LE_X) / FP.STAB_C
    cr, ct = FP.FIN_CR * M, FP.FIN_CT * M
    zr, zt = FP.FIN_ROOT_Z * M, FP.FIN_TIP_Z * M
    hinge = FP.HINGE_X * M
    xr, xt = hinge - 0.65 * cr, hinge - 0.65 * ct
    S, cref, bref = 2 * b2 * c, c, 2 * b2
    L = []
    L += ["WaterDrop rev B (Fusion model, optimisation P5)",
          "#Mach", "0.0",
          "#IYsym IZsym Zsym", "0 0 0.0",
          "#Sref Cref Bref", "%.5f %.4f %.4f" % (S, cref, bref),
          "#Xref Yref Zref  (CG)", "%.4f 0.0 0.0" % X_CG,
          "#CDp (booms, wires, gaps: estimate)", "0.0", ""]
    # wing
    L += ["SURFACE", "Wing", "#Nchord Cspace Nspan Sspace", "12 1.0 32 -2.0", "YDUPLICATE", "0.0",
          "CDCL", "%.3f %.4f %.3f %.4f %.3f %.4f" % CDCL_WING, ""]
    for y, ctrl in ((0.0, False), (ail0, True), (ail1, True), (b2, False)):
        L += ["SECTION", "#Xle Yle Zle Chord Ainc", "0.0 %.4f 0.0 %.4f %.2f" % (y, c, inc), "AFILE", "sd7062.dat"]
        if ctrl:
            L += ["CONTROL", "#name gain Xhinge XYZhvec SgnDup", "aileron 1.0 %.3f 0 0 0 -1" % xh_w]
        L.append("")
    # horizontal stabiliser (flat plate)
    L += ["SURFACE", "Stab", "10 1.0 16 1.0", "YDUPLICATE", "0.0", "CDCL", "-0.6 0.020 0.0 0.012 0.6 0.020", ""]
    for y in (0.0, bs2):
        L += ["SECTION", "%.4f %.4f %.4f %.4f 0.0" % (xs, y, zs, cs), "CONTROL", "elevator 1.0 %.3f 0 0 0 1" % xh_s, ""]
    # fin
    L += ["SURFACE", "Fin", "10 1.0 14 1.0", "CDCL", "-0.6 0.020 0.0 0.012 0.6 0.020", ""]
    for x, z, ch in ((xr, zr, cr), (xt, zt, ct)):
        L += ["SECTION", "%.4f 0.0 %.4f %.4f 0.0" % (x, z, ch), "CONTROL", "rudder 1.0 0.65 0 0 0 1", ""]
    # pod body
    L += ["BODY", "Pod", "#Nbody Bspace", "24 1.0", "SCALE", "%.4f %.4f %.4f" % (Lpod * M, Lpod * M, Lpod * M),
          "TRANSLATE", "%.4f 0.0 %.4f" % (BP.X_FRONT * M, zpod * M), "BFILE", "revB_pod.dat", ""]
    open(os.path.join(OUT, "revB.avl"), "w").write("\n".join(L) + "\n")
    print("written", os.path.join(OUT, "revB.avl"), "S %.4f m2, stab %.4f m2, fin %.4f m2" % (
        S, 2 * bs2 * cs, 0.5 * (cr + ct) * (zt - zr)))


if __name__ == "__main__":
    main()
