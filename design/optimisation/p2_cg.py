"""P2: centre-of-gravity estimate of rev B (Fusion), empty and with 1 L of water, and the battery position for X 80.

Structure: every body of design/cad_fusion_revB/check/bodies.json at the centre of its bounding box (an ESTIMATE of
its centroid). Masses as in bodies.json except (a) the PETG join bodies that the pod build tagged as steel
(NOSE-RING, SERVO-MOUNT: P2 finding 1), re-massed at PETG 1.27 g/cm3, and (b) the electronics placeholders, whose
volume-based masses are replaced by the catalogue masses of design/FIXED_MASSES.md at the placeholder positions.
Film and glue lines of mass_table.md (mass_summary.group) are put at the centroid of their assembly. Water: 996 g at the bottle's
centroid X 80 (the reservoir build places it there:
design/cad_reservoir/scripts/res_params.py X_CG, checked by res_check.py). Plain Python:  python design/optimisation/p2_cg.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
B = json.load(open(os.path.join(HERE, "..", "cad_fusion_revB", "check", "bodies.json")))
X_TARGET = 80.0
WATER = 996.0
FIXED = {  # placeholder name: catalogue mass g (FIXED_MASSES.md)
    "MOTOR": 52.0, "COLLET": 5.0, "PROP-DISC": 14.0, "ESC": 36.0, "BATTERY": 85.0, "TSERVO-R": 13.4, "TSERVO-L": 13.4,
    "RELEASE-SERVO": 13.4, "SERVO-W-R": 13.7, "SERVO-W-L": 13.7,   # wing: 2 x MG90S + arms = 27.4 g
    "RECEIVER": 13.5,                                               # not selected: placeholder mass kept (estimate)
}
sys.path.insert(0, os.path.join(HERE, "..", "cad_fusion_revB", "scripts"))
import mass_summary as MS  # noqa: E402  same film / glue / lamination-glue lines as mass_table.md
EXTRA = {g: sum(e[1] for e in MS.group(g)[2]) for g in ("Pod", "Wing", "Tail")}


def empty():
    """empty mass g, moment sums and the per-assembly [m, m x, m z] of the model (no water)."""
    tot = mx = mz = 0.0
    asm = {}
    for b in B:
        bb = b["bb"]
        xc, zc = 0.5 * (bb[0] + bb[1]), 0.5 * (bb[4] + bb[5])
        m = b["mass_g"]
        if b["material"] == "Steel" and b["name"] in ("NOSE-RING", "SERVO-MOUNT"):
            m = b["vol_mm3"] * 1.27e-3
        if b["material"] == "Electronics (lumped)":
            if b["name"] not in FIXED:
                continue                                         # servo tabs etc. (in the servo mass)
            m = FIXED[b["name"]]
        top = b["path"].split("/")[0]
        if top.startswith("Jigs") or "Jigs" in b["path"]:
            continue
        a = asm.setdefault(top, [0.0, 0.0, 0.0])
        a[0] += m; a[1] += m * xc; a[2] += m * zc
        tot += m; mx += m * xc; mz += m * zc
    for k, v in EXTRA.items():
        a = asm[k]
        xc, zc = a[1] / a[0], a[2] / a[0]
        tot += v; mx += v * xc; mz += v * zc
    return tot, mx, mz, asm


def main():
    tot, mx, mz, asm = empty()
    x_e, z_e = mx / tot, mz / tot
    xw = 80.0
    x_l = (mx + WATER * xw) / (tot + WATER)
    print("assemblies:", {k: (round(v[0], 1), round(v[1] / v[0], 1)) for k, v in asm.items()})
    print("empty (bodies + fixed masses + film/glue): %.1f g, CG X %.1f Z %.1f" % (tot, x_e, z_e))
    print("water 996 g at X %.1f -> loaded %.1f g, CG X %.1f" % (xw, tot + WATER, x_l))
    batt = [b for b in B if b["name"] == "BATTERY"][0]["bb"]
    xb = 0.5 * (batt[0] + batt[1])
    for lab, M, X in (("empty", tot, x_e), ("loaded", tot + WATER, x_l)):
        dxb = (X_TARGET - X) * M / FIXED["BATTERY"]
        print("%s: battery move for CG X %.0f = %+.1f mm (battery now at X %.1f -> %.1f)" % (lab, X_TARGET, dxb, xb, xb + dxb))
    # levers (empty CG shift, mm; negative = forward)
    bx = {b["name"]: 0.5 * (b["bb"][0] + b["bb"][1]) for b in B}
    lev = [("battery to the front of its tray range (X -120, bal_params BATT_XC_RANGE)", FIXED["BATTERY"] * (-120.0 - xb)),
           ("receiver from X %.0f to the nose bay X -40" % bx["RECEIVER"], FIXED["RECEIVER"] * (-40.0 - bx["RECEIVER"])),
           ("booms 10x8 -> 8x6 tube (-4.7 g each at X %.0f)" % bx["BOOM-R"], -2 * 4.7 * (bx["BOOM-R"] - x_e)),
           ("1 g less in the tail (at X 690)", -1.0 * (690.0 - x_e)),
           ("1 g of nose ballast (at X -180)", 1.0 * (-180.0 - x_e))]
    for lab, m in lev:
        print("lever: %-70s %+6.2f mm" % (lab, m / tot))


if __name__ == "__main__":
    main()
