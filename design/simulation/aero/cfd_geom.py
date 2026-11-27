"""P5 CFD: outer shape of the rev B aircraft for SOLIDWORKS Flow Simulation, from the same part data as the CAD.
    python design/simulation/aero/cfd_geom.py      -> cfd/wing.json, cfd/aircraft.json (built by SwCfdGeom.cs)

Half models (the symmetry plane is the aircraft centre plane). SOLIDWORKS axes: X = aircraft X + X0 (flow along +X),
Y = aircraft Z (up), Z = aircraft Y (span, right half). Shapes:
- wing: the outer section of wing.py (SD7062, chord 280, turned +3 deg about the LE as built), straight to the tip Y 495;
- pod: flat sides, top and floor, so it is exactly the side profile (TOP / BOTTOM lines of the pod part data)
  intersected with the plan (PLAN half widths). Under the wing the pod top is taken up 1 mm into the wing (the
  saddle and foam fill that gap in the real aircraft);
- motor can (D35 x 33) ahead of the nose; the propeller is left out (unpowered glide, as AVL);
- boom (D10) X 235 ... 725 at Y 16, Z -40; tail block; stabiliser and elevator as one 3 mm plate (X 647 ... 779,
  Z 43.5 ... 46.5, to Y 245); fin and rudder as one 3 mm plate (half 1.5 mm on the symmetry plane).
Left out: skids, saddles' straps, hinge gaps, the hatch seams, wires and horns (small)."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.dirname(os.path.dirname(HERE))
for p in ("cad_fuselage_balsa/scripts", "cad_fuselage/scripts", "cad_reservoir/scripts", "cad/scripts", "cad_fusion_revB/scripts"):
    sys.path.insert(0, os.path.join(DESIGN, p))
from revb_params import BP, FP, WP  # noqa: E402
import wing as W                    # noqa: E402

OUT = os.path.join(HERE, "cfd")
X0 = 250.0                           # shift so every sketch plane is at a positive X


def interp(pts, x):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[0][1] if x < pts[0][0] else pts[-1][1]


def wing_section():
    """outer section in the aircraft frame: wing.py's section turned by the incidence about the LE (Y axis), as
    build_wing.py places the wing (fxlib.rot_y)."""
    th = math.radians(WP.__dict__.get("INCIDENCE", 3.0))
    return [(u * math.cos(th) + v * math.sin(th), -u * math.sin(th) + v * math.cos(th)) for u, v in W.outer_clip(0.0, WP.CHORD)]


def lower_z(sec, x):
    """lowest z of the section outline at x (vertical line through the polygon)."""
    zs = []
    for (x0, z0), (x1, z1) in zip(sec, sec[1:] + sec[:1]):
        if min(x0, x1) <= x <= max(x0, x1) and x1 != x0:
            zs.append(z0 + (z1 - z0) * (x - x0) / (x1 - x0))
    return min(zs) if zs else None


def wing_body(sec):
    return dict(kind="extrude", name="WING", loops=[[[u + X0, v] for u, v in sec]], z0=0.0, depth=WP.HALF_SPAN)


def pod_bodies(sec):
    xs = sorted(set([BP.X_FRONT, BP.X_END] + [x for x, _ in BP.TOP] + [x for x, _ in BP.BOTTOM] +
                    [x for x, _ in BP.PLAN] + [2.0 + 4.0 * i for i in range(70)]))
    xs = [x for x in xs if BP.X_FRONT <= x <= BP.X_END]
    top = []
    for x in xs:
        z = interp(BP.TOP, x)
        if 1.0 <= x <= WP.CHORD - 2.0:
            zl = lower_z(sec, x)
            if zl is not None:
                z = max(z, zl + 1.0)          # into the wing: one body
        top.append((x, z))
    bot = [(x, interp(BP.BOTTOM, x)) for x in xs]
    side = [[x + X0, z] for x, z in bot] + [[x + X0, z] for x, z in reversed(top)]
    hw_max = max(h for _, h in BP.PLAN)
    # plan cut: everything outside the half width, as a Top-plane sketch (sketch x = X, sketch y = -Z)
    xa, xb = BP.X_FRONT - 1.0, BP.X_END + 1.0
    edge = [(x, interp(BP.PLAN, x)) for x in sorted(set([xa, xb] + [x for x, _ in BP.PLAN]))]
    cut = [[x + X0, -h] for x, h in edge] + [[xb + X0, -(hw_max + 10.0)], [xa + X0, -(hw_max + 10.0)]]
    return [dict(kind="extrude", name="POD", loops=[side], z0=0.0, depth=hw_max + 1.0),
            dict(kind="cut_top", name="POD-PLAN", loops=[cut])]


def tail_bodies():
    b = []
    b.append(dict(kind="cyl_x", name="BOOM", x0=235.0 + X0, length=725.0 - 235.0, y=FP.SOCK_Z, z=FP.SOCK_Y, r=5.0))
    # tail block down to the boom axis: the clamp collars (TB-COLLAR) join block and boom in the aircraft
    b.append(dict(kind="extrude", name="TAILBLOCK", loops=[[[667.0 + X0, FP.SOCK_Z], [738.0 + X0, FP.SOCK_Z], [738.0 + X0, -22.0],
                                                             [667.0 + X0, -22.0]]], z0=0.0, depth=FP.SOCK_Y))
    xs0, xs1 = FP.STAB_LE_X, 779.0
    b.append(dict(kind="extrude", name="STAB", loops=[[[xs0 + X0, 43.5], [xs1 + X0, 43.5], [xs1 + X0, 46.5], [xs0 + X0, 46.5]]],
                  z0=0.0, depth=FP.STAB_HS))
    hinge, te_r, te_t = FP.HINGE_X, 778.0, 778.0
    xr, xt = hinge - 0.65 * FP.FIN_CR, hinge - 0.65 * FP.FIN_CT
    fin = [[xr + X0, -31.6], [te_r + X0, -31.6], [te_t + X0, FP.FIN_TIP_Z], [xt + X0, FP.FIN_TIP_Z]]
    b.append(dict(kind="extrude", name="FIN", loops=[fin], z0=0.0, depth=1.5))
    return b


def main():
    os.makedirs(OUT, exist_ok=True)
    sec = wing_section()
    motor = dict(kind="cyl_x", name="MOTOR", x0=-203.0 + X0, length=33.5, y=-50.0, z=0.0, r=17.5)
    wing = dict(name="wing", x0=X0, bodies=[wing_body(sec)])
    ac = dict(name="aircraft", x0=X0, bodies=[motor] + pod_bodies(sec) + [wing_body(sec)] + tail_bodies())
    for m in (wing, ac):
        m["part"] = os.path.join(OUT, "cfd_%s.SLDPRT" % m["name"])
        json.dump(m, open(os.path.join(OUT, m["name"] + ".json"), "w"), indent=1)
        print("geometry", m["name"], len(m["bodies"]), "features")
    zl = [lower_z(sec, x) for x in (0.5, 140.0, 279.0)]
    print("wing section: %d points, x %.1f..%.1f, z %.1f..%.1f; lower z at x 0.5/140/279: %s" % (
        len(sec), min(u for u, _ in sec), max(u for u, _ in sec), min(v for _, v in sec), max(v for _, v in sec), zl))


if __name__ == "__main__":
    main()
