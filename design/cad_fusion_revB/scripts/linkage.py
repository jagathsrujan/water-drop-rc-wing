"""Control linkages: aileron servo arms, horns, horn ribs, 1.2 mm steel pushrods with Z-bends (wing frame), and the
tail servo arms + carbon pushrods with steel Z-bend ends (aircraft frame). Values: wing_params (rev A stage B),
fus_params (stage F-C).

Wing (per side, rev A layout): MG90S lies flat in the bay between ribs 110 and 165, shaft outboard (+Y); single arm
pointing down through a slot in the servo hatch; arm hole 4 mm below the lower skin; 1.2 mm steel wire under the
skin, parallel to X, to the PETG horn on the aileron; horn hole on the hinge line (X 209), so the travel is
symmetric; the horn is glued to a 2 mm horn rib and the aileron LE.
Tail: 9 g servos on the tail-servo tray, arms 8 mm outboard; 2 mm carbon rods with 1.2 mm steel Z-bend ends
(6 mm) at both ends, through the exit slots in the tail cone to the elevator and rudder horns."""
import math
import geo as G
import wing as W
import pod as POD
import fus_params as FP

P, A, S = W.P, W.A, W.P.MG90S
WIRE_R = P.PUSHROD_D / 2          # 0.6
END = 6.0                         # steel Z-bend end length (tail)


def hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def stadium(c1, r1, c2, r2, n=40):
    return G.ccw(hull([(round(c[0] + r * math.cos(2 * math.pi * k / n), 6), round(c[1] + r * math.sin(2 * math.pi * k / n), 6))
                       for c, r in ((c1, r1), (c2, r2)) for k in range(n)]))


def wing_geom():
    xs = P.SERVO_SHAFT_X
    cx1 = xs + S["SHAFT_FROM_END"]
    cx0 = cx1 - S["L"]
    ccx = 0.5 * (cx0 + cx1)
    tx0, tx1 = ccx - S["TAB_L"] / 2, ccx + S["TAB_L"] / 2
    zl_max = max(A.zl(tx0 + (tx1 - tx0) * i / 20) for i in range(21))
    zc0 = zl_max + P.HATCH_T + P.SERVO_GAP
    zsh = zc0 + S["W"] / 2
    ya0 = P.SERVO_Y0 + S["H_TOP"] + 0.7
    ya1 = ya0 + P.ARM_T
    yarm = 0.5 * (ya0 + ya1)
    za = A.zl(xs) - P.ARM_BELOW_SKIN
    yh0, yh1 = yarm - P.HORN_T / 2, yarm + P.HORN_T / 2
    yr = max(ya1, yh1) + 0.1 + WIRE_R
    return dict(xs=xs, zsh=zsh, ya0=ya0, ya1=ya1, za=za, yh0=yh0, yh1=yh1, yr=yr)


def hatch_slot():
    """The arm slot in the servo hatch (world X, Y ranges, right side)."""
    g = wing_geom()
    return (g["xs"] - P.ARM_SLOT_HALF, g["xs"] + P.ARM_SLOT_HALF, g["ya0"] - 1.0, g["ya1"] + 1.0)


def wing_parts():
    """Plate parts (part dicts, wing frame) and round parts for both ailerons."""
    g = wing_geom()
    xs, zsh, za = g["xs"], g["zsh"], g["za"]
    xr = P.AIL_X[0] + P.AIL_LE_T
    zl = A.zl
    arm = stadium((xs, zsh), 3.5, (xs, za), 2.0)
    arm_cut = [("circle", xs, za, 0.7), ("circle", xs, zsh, S["SPLINE_D"] / 2)]
    horn = G.ccw([(xr, 6.0), (232.0, 6.0), (232.0, zl(232.0)), (222.0, zl(222.0)), (211.5, za - 3.0), (206.5, za - 3.0),
                  (206.5, za + 3.0), (xr, zl(xr))])
    horn_cut = [("circle", P.HINGE_X, za, 0.75)]
    rib = W.outer_clip(xr, P.X_TE)
    parts, rounds = [], []
    for s, Sd in ((1, "R"), (-1, "L")):
        def yp(name, grp, outline, a, b, mat, cl=(), labels=()):
            lo, hi = (a, b) if s > 0 else (-b, -a)
            parts.append(dict(name=name, grp=grp, outline=outline, t=hi - lo, mat=mat, cutters=list(cl), labels=list(labels),
                              z0=0.0, fr=G.frame((0.0, hi, 0.0), (1, 0, 0), (0, 0, 1))))
        yp("SERVO-ARM-W-" + Sd, "Wing_Servo", arm, g["ya0"], g["ya1"], "elec", arm_cut)
        yp("AIL-HORN-" + Sd, "Wing_Aileron", horn, g["yh0"], g["yh1"], "petg", horn_cut)
        nm = "AH-" + Sd
        yp(nm, "Wing_Aileron", rib, g["yh1"], g["yh1"] + P.AIL_RIB_T, "balsa_med", [], W.lbl(rib, [], nm + " HORN RIB <LE", h=2.0, min_h=1.6))
        y = s * g["yr"]
        rounds.append(("PUSHROD-AIL-" + Sd, (xs, y, za), (P.HINGE_X, y, za), WIRE_R, 0.0, "steel", "Wing_Servo"))
        rounds.append(("ZBEND-AIL-SERVO-" + Sd, (xs, s * (g["ya0"] - 0.8), za), (xs, s * (g["yr"] - WIRE_R), za), WIRE_R, 0.0, "steel", "Wing_Servo"))
        rounds.append(("ZBEND-AIL-HORN-" + Sd, (P.HINGE_X, s * (g["yh0"] - 0.8), za), (P.HINGE_X, s * (g["yr"] - WIRE_R), za), WIRE_R, 0.0, "steel", "Wing_Servo"))
    return parts, rounds


def tail_parts():
    """Tail servo arms (XY plates on the 9 g servos) and the pushrods with steel Z-bend ends."""
    parts, rounds = [], []
    sx = FP.TSERVO_SHAFT_X
    za0, za1 = FP.ARM_Z - 2.5, FP.ARM_Z - 1.0
    fr = G.frame((0.0, 0.0, za0), (1, 0, 0), (0, 1, 0))
    for s, nm, horn_axis in ((1, "RUD", "z"), (-1, "ELEV", "y")):
        sy, hy = s * FP.TSERVO_YC, s * FP.ARM_HOLE_Y
        arm = stadium((sx, sy), 3.5, (sx, hy), 2.0)
        parts.append(dict(name="SERVO-ARM-%s" % nm, grp="Tail_Hardware", outline=arm, t=za1 - za0, fr=fr, mat="elec",
                          cutters=[("circle", sx, hy, 0.7), ("circle", sx, sy, 2.4)], labels=[], z0=0.0))
        a, b = POD.ROD_START[s], POD.ROD_END[s]
        L = math.sqrt(sum((q - p) ** 2 for p, q in zip(a, b)))
        u = tuple((q - p) / L for p, q in zip(a, b))
        a6 = tuple(p + c * END for p, c in zip(a, u))
        b6 = tuple(q - c * END for q, c in zip(b, u))
        rounds.append(("PUSHROD-%s" % nm, a6, b6, FP.PUSHROD_D / 2, 0.0, "carbon", "Tail_Hardware"))
        rounds.append(("ROD-END-%s-SERVO" % nm, a, a6, WIRE_R, 0.0, "steel", "Tail_Hardware"))
        b15 = tuple(q - c * 1.5 for q, c in zip(b, u))          # the bend into the horn hole starts 1.5 short of the plate
        rounds.append(("ROD-END-%s-HORN" % nm, b6, b15, WIRE_R, 0.0, "steel", "Tail_Hardware"))
        # Z-bends: through the arm hole (vertical) and through the horn hole (normal to the horn plate)
        rounds.append(("ZBEND-%s-SERVO" % nm, (a[0], a[1], za0 - 0.8), (a[0], a[1], a[2] - WIRE_R), WIRE_R, 0.0, "steel", "Tail_Hardware"))
        if horn_axis == "y":
            p0, p1 = (b[0], b[1] + 1.6, b[2]), (b[0], b[1] - 1.6, b[2])
        else:
            p0, p1 = (b[0], b[1], b[2] - 1.6), (b[0], b[1], b[2] + 1.6)
        rounds.append(("ZBEND-%s-HORN" % nm, p0, p1, WIRE_R, 0.0, "steel", "Tail_Hardware"))
    return parts, rounds


if __name__ == "__main__":
    print(wing_geom())
    for f in (wing_parts, tail_parts):
        pp, rr = f()
        for p in pp:
            print(p["name"], [round(v, 1) for v in G.bbox(p["outline"])], round(p["t"], 2), [l[0] for l in p["labels"]])
        for r in rr:
            print(r[0], [round(v, 1) for v in r[1]], [round(v, 1) for v in r[2]])
