"""Balsa pod rev B, remodelled for Fusion and for laser cutting (no hex lightening in this pass).
Frame: wing frame, mm (origin wing LE on the centreline, X aft, Y right, Z up). Numbers: bal_params (BP),
fus_params (FP), res_params (RP) - the FreeCAD rev B model stays the reference.

Manufacturing rules used here (see ../README.md):
- Balsa sheet 100 x 300 mm usable (grain along 300): no balsa part over 100 mm across the grain.
- Sides: outer 1.5 mm (grain X) in a lower and an upper strip (joint at Z -40), inner 1.0 mm (grain Z) in pieces
  <= 100 mm wide whose joints are staggered from the outer joint: the cross-laminate bridges every joint.
- Every former has 3 floor tabs (2 on the split / end formers) and 2-3 side tabs per side that pass through slots in
  the floor and in both side layers; the bulkhead and end former also have 2 tabs up through the aft deck.
- Sides and floor meet in finger joints: side tabs (both layers) drop into notches in the floor edge.
- Floor pieces join in dovetail keys; the hatch halves join in dovetail keys.
- Saddle layers have floor tabs, keel notches and 3 pin holes (2 mm toothpicks) so the stack self-aligns.
- Every laser part has its name engraved (0.2 mm) on the face that stays visible while building, with a FWD / UP hint;
  the floor and sides carry the mating former's name next to its slots."""
import math
import geo as G
import bal_params as BP
import fus_params as FP
import res_params as RP

K0, K1 = BP.NOSE_KINK, BP.AFT_KINK
XF, XE = BP.X_FRONT, BP.X_END
SEGS = [(XF, K0), (K0, K1), (K1, XE)]
SEGN = "NMT"
T_OUT, T_IN, T_FL = BP.T_SIDE_OUT, BP.T_SIDE_IN, BP.T_FLOOR
T_LAM = T_OUT + T_IN
FT = BP.FRAME_T
SPLIT_Z = -40.0                   # outer side layer: lower / upper strip joint
TAB_W = BP.TAB_W
KINK_TRIM = 0.3                   # side and floor pieces stop 0.3 short of a kink (miter overlap of the laminate)
FLOOR_TOP = FP.FLOOR_Z            # -115.5
H_LBL = 4.0

# side inner-layer joints (X) and the grip zone (inner layer in 1.0 birch ply below Z -70)
INNER_SPLITS = {"N": [-92.0], "M": [30.0, 80.0, 130.0, 195.0], "T": []}
GRIP = BP.GRIP_PLY                # (30, 130, -70)
SERVO = BP.SERVO_ZONE_R           # (44, 96): right side single layer, 1.5 mm birch ply insert
FLOOR_SPLITS = {"N": [-115.0], "M": [28.0, 115.0, 200.0], "T": []}
FINGERS = {"N": [-155.0, -72.0, -48.0], "M": [-12.0, 150.0, 186.0, 220.0], "T": [255.0, 280.0]}
FINGERS_L_ONLY = {"M": [85.0]}

# tail servo tray (replaces the rev B pads): 3 mm lite-ply between the sides, servo tabs on it
TST_X, TST_Z = (202.0, 232.0), (-84.0, -81.0)
TST_TABS_X = [208.0, 226.0]
TSERVO_OPEN = (FP.TSERVO[0] + 0.4, FP.TSERVO[1] + 0.4)


# ---------------- outer lines ----------------
def hw(x):
    return G.interp(BP.PLAN, x)


def zb(x):
    return G.interp(BP.BOTTOM, x)


def zt(x):
    return G.interp(BP.TOP, x)


def seg_of(x):
    for k, (a, b) in enumerate(SEGS):
        if a - 1e-6 <= x < b:
            return k
    return 2


def plan_cos(k):
    a, b = SEGS[k]
    return (b - a) / math.hypot(b - a, hw(b) - hw(a))


def floor_cos(k):
    a, b = SEGS[k]
    return (b - a) / math.hypot(b - a, zb(b) - zb(a))


def hi(x, k=None):
    """Inner half-width (inside the 2.5 mm laminate) at x."""
    k = seg_of(x) if k is None else k
    return hw(x) - T_LAM / plan_cos(k)


def zf(x, k=None):
    """Floor top at x."""
    k = seg_of(x) if k is None else k
    return zb(x) + T_FL / floor_cos(k)


def tan_plan(k):
    a, b = SEGS[k]
    return abs(hw(b) - hw(a)) / (b - a)


def tan_floor(k):
    a, b = SEGS[k]
    return abs(zb(b) - zb(a)) / (b - a)


# a vertical former tab crosses a tapered (nose / tail cone) panel at an angle: its slot is opened by this much
SIDE_SHIFT = [T_LAM * tan_plan(k) for k in range(3)]
FLOOR_SHIFT = [T_FL * tan_floor(k) for k in range(3)]
# panel ends at a kink: the inside face of a tapered panel leans over the kink by T * tan(angle)
SIDE_TRIM = {(0, "b"): KINK_TRIM + SIDE_SHIFT[0], (1, "a"): KINK_TRIM, (1, "b"): KINK_TRIM, (2, "a"): KINK_TRIM + SIDE_SHIFT[2]}
FLOOR_TRIM = {(0, "b"): KINK_TRIM + FLOOR_SHIFT[0], (1, "a"): KINK_TRIM, (1, "b"): KINK_TRIM, (2, "a"): KINK_TRIM + FLOOR_SHIFT[2]}
FLOOR_KEYS = {115.0: [-40.0, 40.0]}          # dovetail keys per floor joint (|Y| < 20 is the belly opening at X 115)

ZD0 = zt(K1)
ZD_SLOPE = (-15.7 - ZD0) / 44.0       # deck top plane through the TOP line at X 236 and 1 mm under the wing at X 280


def zdeck(x):
    return ZD0 + (x - K1) * ZD_SLOPE


# ---------------- formers ----------------
FORMERS = [  # name, x0 (front face), kind, material
    ("N1", -130.0, "nose", "liteply"), ("N2", -100.0, "nose", "liteply"),
    ("FS", K0, "stop", "liteply"), ("B1", 38.0, "U", "liteply"), ("B2", 105.0, "split", "liteply"),
    ("B4", FP.SADDLE2_X[1] + 0.05, "U", "liteply"), ("BH", K1, "bulkhead", "ply"), ("EF", BP.END_X[0], "end", "liteply")]
FLOOR_TABS = {"N1": [0.0, -20.0, 20.0], "N2": [0.0, -24.0, 24.0], "FS": [0.0, -40.0, 40.0], "B1": [0.0, -38.0, 38.0],
              "B2": [-36.0, 36.0], "B4": [0.0, -38.0, 38.0], "BH": [0.0, -30.0, 30.0], "EF": [-12.0, 12.0]}
TOP_TABS = {"BH": [-25.0, 25.0], "EF": [-12.0, 12.0]}

# strips that pass through the formers: (name, x0, x1, kind)
KEEL_X = (FP.STOP_X[1], K1 - 0.5)
LONG_SEGS = {+1: [(K0 + 1.0, 44.0), (96.0, K1 - 1.0)], -1: [(K0 + 1.0, 37.5), (70.0, K1 - 1.0)]}
CAP_X = (0.0, K1)
LEDGE_X = [(-165.0, K0 - 1.0), (FP.STOP_X[1], -2.5)]


def former_geom(name, x0, kind):
    k = seg_of(x0 + 1.5)
    x1 = x0 + FT
    h = min(hi(x0, k), hi(x1, k))
    zfl = max(zf(x0, k), zf(x1, k))
    if kind in ("bulkhead", "end"):
        ztp = min(zdeck(x0), zdeck(x1)) - T_FL      # deck (1.5) sits on top
    else:
        ztp = min(zt(x0), zt(x1))
    depth = min(hw(x0), hw(x1)) - h                 # side tabs end flush with the outer face
    return dict(k=k, x0=x0, x1=x1, hi=h, zfl=zfl, ztp=ztp, depth=depth)


def side_tab_z(g, kind):
    top_strip = 3.0 if kind in ("nose", "U", "split") else 0.0
    zs = []
    lo0, lo1 = g["zfl"] + 8.0, SPLIT_Z - 6.0
    if kind in ("U", "split"):
        lo0 = max(lo0, g["zfl"] + 6.0)
    if lo1 - lo0 > 40:
        zs += [lo0 + (lo1 - lo0) / 3.0, lo0 + 2 * (lo1 - lo0) / 3.0]
    elif lo1 - lo0 > 8:
        zs.append(0.5 * (lo0 + lo1))
    up0, up1 = SPLIT_Z + 6.0, g["ztp"] - top_strip - 2.0
    if up1 - up0 >= 8:
        zs.append(0.5 * (up0 + up1))
    return zs


SIDE_TABS = {}
GEOM = {}
for _n, _x0, _k, _m in FORMERS:
    GEOM[_n] = former_geom(_n, _x0, _k)
    SIDE_TABS[_n] = side_tab_z(GEOM[_n], _k)


# ---------------- pushrods and tubes ----------------
ROD_START = {+1: (FP.TSERVO_SHAFT_X, FP.ARM_HOLE_Y, FP.ARM_Z), -1: (FP.TSERVO_SHAFT_X, -FP.ARM_HOLE_Y, FP.ARM_Z)}
ROD_END = {+1: FP.RUD_HORN_PT, -1: FP.ELEV_HORN_PT}
TUBE_Y, TUBE_Z, TUBE_R = FP.SOCK_Y, FP.SOCK_Z, FP.SOCK_BORE / 2.0


def rod_at_x(s, x):
    a, b = ROD_START[s], ROD_END[s]
    t = (x - a[0]) / (b[0] - a[0])
    return tuple(a[i] + t * (b[i] - a[i]) for i in range(3))


# ---------------- part list ----------------
PARTS = []


def add(name, grp, outline, t, fr, mat, cutters=(), labels=(), z0=0.0, **kw):
    d = dict(name=name, grp=grp, outline=outline, t=t, fr=fr, mat=mat, cutters=list(cutters), labels=list(labels), z0=z0)
    d.update(kw)
    PARTS.append(d)
    return d


def lbl(poly, cutters, text, h=H_LBL, prefer=None, min_h=2.0):
    while h >= min_h:
        p = G.label_spot(poly, cutters, text, h, prefer=prefer)
        if p:
            return [(text, p[0], p[1], h)]
        h -= 0.5
    return []


def slot_x(x0, x1, xa, xb):
    """A slot x range, run 1 mm past a piece end it touches (so the cut is open there)."""
    a, b = x0, x1
    if abs(a - xa) < 0.6:
        a -= 1.0
    if abs(b - xb) < 0.6:
        b += 1.0
    return a, b


# ---------------- sides ----------------
def side_frame(s, k):
    xa, xb = SEGS[k]
    if s > 0:
        return G.frame((xa, hw(xa), 0.0), (xb - xa, hw(xb) - hw(xa), 0.0), (0, 0, 1))
    return G.frame((xb, -hw(xb), 0.0), (xa - xb, hw(xb) - hw(xa), 0.0), (0, 0, 1))


def side_u(s, k, x):
    xa, xb = SEGS[k]
    L = math.hypot(xb - xa, hw(xb) - hw(xa))
    return (x - xa) * L / (xb - xa) if s > 0 else (xb - x) * L / (xb - xa)


def side_outline(s, k):
    xa, xb = SEGS[k]
    pts = [(xa, zf(xa, k)), (xb, zf(xb, k))]
    tops = [(x, z) for x, z in BP.TOP if xa < x < xb]
    pts += [(xb, zt(xb))] + list(reversed(tops)) + [(xa, zt(xa))]
    return G.ccw(G.clean([(side_u(s, k, x), z) for x, z in pts]))


def side_cutters(s, k, layer):
    """Slots and holes through the side laminate, in the (u, Z) frame of side s, segment k."""
    xa, xb = SEGS[k]
    cl, marks = [], []
    for n, x0, kind, _ in FORMERS:
        g = GEOM[n]
        if g["k"] != k:
            continue
        a, b = slot_x(x0, x0 + FT, xa, xb)
        ua, ub = sorted((side_u(s, k, a), side_u(s, k, b)))
        ua, ub = ua - SIDE_SHIFT[k], ub + SIDE_SHIFT[k]
        for zc in SIDE_TABS[n]:
            cl.append(G.rect(ua, ub, zc - TAB_W / 2, zc + TAB_W / 2))
        if SIDE_TABS[n]:
            marks.append((n, 0.5 * (ua + ub), SIDE_TABS[n][0] + TAB_W / 2 + 3.5))
    if k == 1:   # tail servo tray tabs
        for xc in TST_TABS_X:
            ua, ub = sorted((side_u(s, k, xc - TAB_W / 2), side_u(s, k, xc + TAB_W / 2)))
            cl.append(G.rect(ua, ub, TST_Z[0], TST_Z[1]))
        # band stubs
        cl.append(("circle", side_u(s, k, FP.STUB_X), FP.STUB_Z, FP.STUB_D / 2 + 0.1))
        if s > 0:   # D-059 pocket window (right)
            (px0, px1), (pz0, pz1) = FP.POCKET_X, FP.POCKET_Z
            w = FP.POCKET_WALL
            ua, ub = sorted((side_u(s, k, px0 - w), side_u(s, k, px1 + w)))
            cl.append(G.rect(ua, ub, FLOOR_TOP - 3.0, pz1 + w))
        else:       # safety-pin flag hole (left)
            fx, fz = FP.SAF_PIN_POS
            cl.append(("circle", side_u(s, k, fx), fz, FP.FLAG_HOLE_D / 2))
    if k == 2:
        cl.append(("circle", side_u(s, k, FP.DOWEL_X), FP.DOWEL_Z, FP.DOWEL_D / 2 + 0.2 + SIDE_SHIFT[k]))
        # pushrod exit: where the rod crosses the laminate mid-plane, an obround slot along the rod
        xm = rod_cross_x(s)
        if xm is not None:
            p = rod_at_x(s, xm)
            u = side_u(s, k, xm)
            half = 5.0
            cl += [G.rect(u - half, u + half, p[2] - 3.0, p[2] + 3.0), ("circle", u - half, p[2], 3.0), ("circle", u + half, p[2], 3.0)]
    return cl, marks


def rod_cross_x(s):
    """X where pushrod s crosses the tail-cone laminate mid-plane (|Y| = hw - 1.25/cos)."""
    k = 2
    xa, xb = SEGS[k]
    f = lambda x: abs(rod_at_x(s, x)[1]) - (hw(x) - 0.5 * T_LAM / plan_cos(k))
    lo, hi_ = xa, xb
    if f(lo) * f(hi_) > 0:
        return None
    for _ in range(60):
        m = 0.5 * (lo + hi_)
        if f(lo) * f(m) <= 0:
            hi_ = m
        else:
            lo = m
    return 0.5 * (lo + hi_)


def add_fingers(poly, s, k, xr, floor_v):
    """Finger tabs on the bottom edge of a side piece covering x range xr."""
    xs = list(FINGERS[SEGN[k]])
    if s < 0:
        xs += FINGERS_L_ONLY.get(SEGN[k], [])
    xs = [x for x in xs if xr[0] + TAB_W / 2 + 4 <= x <= xr[1] - TAB_W / 2 - 4]
    if not xs:
        return poly
    i = G.find_edge(poly, lambda u, v: abs(v - floor_v(u)) < 0.05)
    P, Q = poly[i], poly[(i + 1) % len(poly)]
    L = math.hypot(Q[0] - P[0], Q[1] - P[1])
    du, dv = (Q[0] - P[0]) / L, (Q[1] - P[1]) / L
    cents = []
    for x in xs:
        u = side_u(s, k, x)
        cents.append((u - P[0]) * du + (floor_v(u) - P[1]) * dv)
    return G.tabs_on_edge(poly, i, cents, TAB_W, T_FL)


def build_sides():
    for s, S in ((+1, "R"), (-1, "L")):
        for k in range(3):
            xa, xb = SEGS[k]
            seg = SEGN[k]
            full = side_outline(s, k)
            ua_, ub_ = sorted((side_u(s, k, xa), side_u(s, k, xb)))
            trim_a = SIDE_TRIM.get((k, "a"), 0.0)
            trim_b = SIDE_TRIM.get((k, "b"), 0.0)
            if s > 0:
                ua_, ub_ = ua_ + trim_a, ub_ - trim_b
            else:
                ua_, ub_ = ua_ + trim_b, ub_ - trim_a
            fr = side_frame(s, k)
            u_xa, u_xb = side_u(s, k, xa), side_u(s, k, xb)
            floor_v = lambda u, k=k, s=s: zf(xa + (xb - xa) * ((u - u_xa) / (u_xb - u_xa)), k)
            hint = "< FWD" if s > 0 else "FWD >"

            def piece(name, xr, zr, layer, mat):
                u0, u1 = sorted((side_u(s, k, xr[0]), side_u(s, k, xr[1])))
                u0, u1 = max(u0, ua_), min(u1, ub_)
                poly = G.clip_rect(full, u0, u1, zr[0], zr[1])
                if len(poly) < 3:
                    return
                if zr[0] < -200:
                    poly = add_fingers(poly, s, k, xr, floor_v)
                cl, marks = side_cutters(s, k, layer)
                labs = lbl(poly, cl, name + "\n" + hint)
                pb = G.bbox(poly)
                for txt, um, vm in marks:
                    if pb[0] + 3 < um < pb[1] - 3 and pb[2] + 3 < vm < pb[3] - 3:
                        labs.append((txt, um, vm, 3.0))
                z0, t = (0.0, T_OUT) if layer == "O" else (T_OUT, T_IN)
                if mat == "ply" and layer == "O":
                    t = 1.5
                add(name, "Pod_Sides", poly, t, fr, mat, cl, labs, z0=z0)

            # outer layer
            if s > 0 and k == 1:
                xranges = [(xa, SERVO[0]), (SERVO[0], SERVO[1]), (SERVO[1], xb)]
            else:
                xranges = [(xa, xb)]
            for j, xr in enumerate(xranges):
                tag = "" if len(xranges) == 1 else str(j + 1)
                if s > 0 and k == 1 and j == 1:
                    piece("RO-MP", xr, (-999, 999), "O", "ply")
                    continue
                piece("%sO-%s%sL" % (S, seg, tag), xr, (-999, SPLIT_Z), "O", "balsa_med")
                piece("%sO-%s%sU" % (S, seg, tag), xr, (SPLIT_Z, 999), "O", "balsa_med")
            # inner layer
            cuts = [xa] + INNER_SPLITS[seg] + [xb]
            if s > 0 and k == 1:
                cuts = [xa, GRIP[0], SERVO[0], SERVO[1], GRIP[1], 195.0, xb]
            idx = 0
            for a, b in zip(cuts, cuts[1:]):
                if s > 0 and k == 1 and (a, b) == SERVO:
                    continue
                idx += 1
                in_grip = k == 1 and a >= GRIP[0] - 1e-6 and b <= GRIP[1] + 1e-6
                if in_grip:
                    piece("%sI-M%dU" % (S, idx), (a, b), (GRIP[2], 999), "I", "balsa_med")
                    if s > 0 or (a, b) == (GRIP[0], 80.0):
                        xr = (a, b) if s > 0 else (GRIP[0], GRIP[1])
                        piece("%sI-M%dG" % (S, idx), xr, (-999, GRIP[2]), "I", "ply")
                else:
                    piece("%sI-%s%d" % (S, seg, idx), (a, b), (-999, 999), "I", "balsa_med")


# ---------------- floor ----------------
def floor_frame(k):
    xa, xb = SEGS[k]
    return G.frame((xa, 0.0, zb(xa)), (xb - xa, 0.0, zb(xb) - zb(xa)), (0, 1, 0))


def floor_u(k, x):
    xa, xb = SEGS[k]
    return (x - xa) * math.hypot(xb - xa, zb(xb) - zb(xa)) / (xb - xa)


SADDLES = [("S1", FP.SADDLE1_X), ("S2", FP.SADDLE2_X)]
SADDLE_HW, SADDLE_TOP, SADDLE_R = 42.0, -80.0, 40.3
SADDLE_TAB_Y = 36.0
BRIDGE_Y = (43.0, 46.0)
BRIDGE_XC = {"S1": 0.5 * sum(FP.SADDLE1_X), "S2": FP.SADDLE2_X[1] - 14.0}     # S2: clear of former B4 (X 170)


def floor_cutters(k):
    xa, xb = SEGS[k]
    cl, marks = [], []
    for n, x0, kind, _ in FORMERS:
        g = GEOM[n]
        if g["k"] != k:
            continue
        a, b = slot_x(x0, x0 + FT, xa, xb)
        ua, ub = floor_u(k, a) - FLOOR_SHIFT[k], floor_u(k, b) + FLOOR_SHIFT[k]
        for y in FLOOR_TABS[n]:
            cl.append(G.rect(ua, ub, y - TAB_W / 2, y + TAB_W / 2))
        marks.append((n, 0.5 * (ua + ub) + 5.0, 14.0 if n not in ("B2",) else 30.0))
    if k == 1:
        fr = FP.FLOOR_HOLE_RECT
        cl.append(G.rect(floor_u(k, fr[0]), floor_u(k, fr[1]), fr[2], fr[3]))
        for n, (sa, sb) in SADDLES:
            for y in (-SADDLE_TAB_Y, SADDLE_TAB_Y):
                cl.append(G.rect(floor_u(k, sa), floor_u(k, sb), y - TAB_W / 2, y + TAB_W / 2))
            xc = BRIDGE_XC[n]
            for y0, y1 in (BRIDGE_Y, (-BRIDGE_Y[1], -BRIDGE_Y[0])):
                for a, b in ((xc - 12, xc - 9), (xc + 9, xc + 12)):
                    cl.append(G.rect(floor_u(k, a), floor_u(k, b), y0, y1))
            marks.append((n, floor_u(k, xc), 0.0))
    return cl, marks


def build_floor():
    for k in range(3):
        xa, xb = SEGS[k]
        seg = SEGN[k]
        Ls = floor_u(k, xb)
        full = [(0.0, -hw(xa)), (Ls, -hw(xb)), (Ls, hw(xb)), (0.0, hw(xa))]
        cuts = [xa] + FLOOR_SPLITS[seg] + [xb]
        fr = floor_frame(k)
        cl, marks = floor_cutters(k)
        for j, (a, b) in enumerate(zip(cuts, cuts[1:])):
            u0 = floor_u(k, a) + (FLOOR_TRIM.get((k, "a"), 0.0) if a == xa else 0.0)
            u1 = floor_u(k, b) - (FLOOR_TRIM.get((k, "b"), 0.0) if b == xb else 0.0)
            poly = G.clip_rect(full, u0, u1, -200, 200)
            # dovetail keys at the joints between floor pieces (male on the front piece)
            keys_b = FLOOR_KEYS.get(b, [-40.0, 0.0, 40.0])
            keys_a = FLOOR_KEYS.get(a, [-40.0, 0.0, 40.0])
            if b != xb:
                i = G.find_edge(poly, lambda u, v: abs(u - u1) < 1e-6)
                P = poly[i]
                poly = G.dovetail_edge(poly, i, [y - P[1] for y in keys_b], male=True)
            if a != xa:
                i = G.find_edge(poly, lambda u, v: abs(u - u0) < 1e-6)
                P = poly[i]
                poly = G.dovetail_edge(poly, i, [P[1] - y for y in keys_a], male=False)
            # finger notches on both side edges
            for s in (+1, -1):
                xs = list(FINGERS[seg]) + (FINGERS_L_ONLY.get(seg, []) if s < 0 else [])
                xs = [x for x in xs if a + 8 <= x <= b - 8]
                if not xs:
                    continue
                i = G.find_edge(poly, lambda u, v, s=s: (v * s > 1.0) and abs(abs(v) - hw(xa + (u / Ls) * (xb - xa))) < 0.05)
                P, Q = poly[i], poly[(i + 1) % len(poly)]
                L = math.hypot(Q[0] - P[0], Q[1] - P[1])
                du, dv = (Q[0] - P[0]) / L, (Q[1] - P[1]) / L
                cents = [(floor_u(k, x) - P[0]) * du + (s * hw(x) - P[1]) * dv for x in xs]
                tol = 0.0 if k == 1 else 0.2
                poly = G.tabs_on_edge(poly, i, cents, TAB_W + 2 * (SIDE_SHIFT[k] + FLOOR_SHIFT[k]) + tol,
                                      T_LAM + FLOOR_SHIFT[k] + tol, kind="notch")
            name = "FL-%s%d" % (seg, j + 1)
            pb = G.bbox(poly)
            labs = lbl(poly, cl, name + "\n< FWD", prefer=(0.5 * (pb[0] + pb[1]), -0.4 * hw(0.5 * (a + b))))
            for txt, um, vm in marks:
                if pb[0] + 3 < um < pb[1] - 3:
                    labs.append((txt, um, vm, 3.0))
            add(name, "Pod_Floor", poly, T_FL, fr, "balsa_med", cl, labs)


# ---------------- formers ----------------
def strip_notches(g):
    """Notches in a former for the strips that pass through it."""
    x0, x1, h, zfl, ztp = g["x0"], g["x1"], g["hi"], g["zfl"], g["ztp"]
    cl = []
    over = lambda a, b: a < x1 and b > x0
    if over(*KEEL_X):
        for s in (1, -1):
            y0, y1 = sorted((s * (BP.KEEL_Y - 0.2), s * (BP.KEEL_Y + BP.KEEL_W + 0.2)))
            cl.append(G.rect(y0, y1, zfl - 2.0, FLOOR_TOP + BP.KEEL_H + 0.2))
    for s, segs in LONG_SEGS.items():
        if any(over(a, b) for a, b in segs):
            t = BP.LONGERON + 0.3
            cl.append([(s * (h + 1), zfl - 1), (s * (h - t - 1), zfl - 1), (s * (h + 1), zfl + t + 1)])
    if over(*CAP_X):
        for s in (1, -1):
            y0, y1 = sorted((s * (h - BP.LIP_W - 0.2), s * (h + 1)))
            cl.append(G.rect(y0, y1, ztp - BP.LIP_T - 0.2, ztp + 1))
    if any(over(a, b) for a, b in LEDGE_X):
        for s in (1, -1):
            y0, y1 = sorted((s * (h - BP.LEDGE - 0.2), s * (h + 1)))
            cl.append(G.rect(y0, y1, ztp - BP.LEDGE - 0.2, ztp + 1))
    return cl


def former_outline(n, g, kind, yrange=None):
    h, zfl, ztp = g["hi"], g["zfl"], g["ztp"]
    y0, y1 = yrange if yrange else (-h, h)
    poly = G.rect(y0, y1, zfl, ztp)        # edges: 0 bottom, 1 right, 2 top, 3 left
    # insert from the last edge back so the earlier indices stay valid
    if n in TOP_TABS:
        poly = G.tabs_on_edge(poly, 2, [y1 - y for y in TOP_TABS[n] if y0 < y < y1], TAB_W, T_FL)
    if y0 <= -h + 1e-6:
        poly = G.tabs_on_edge(poly, 3, [ztp - z for z in SIDE_TABS[n]], TAB_W, g["depth"])
    if y1 >= h - 1e-6:
        poly = G.tabs_on_edge(poly, 1, [z - zfl for z in SIDE_TABS[n]], TAB_W, g["depth"])
    poly = G.tabs_on_edge(poly, 0, [y - y0 for y in FLOOR_TABS[n] if y0 + 5 < y < y1 - 5], TAB_W, T_FL)
    return poly


def former_cutters(n, g, kind):
    h, zfl, ztp = g["hi"], g["zfl"], g["ztp"]
    cl = strip_notches(g)
    zc = RP.AXIS_Z
    if kind == "nose":
        tz = FP.TRAY_Z - BP.TRAY_T
        cl.append(G.rect(-BP.NOSE_HW, BP.NOSE_HW, tz, ztp + 5))
        for s in (1, -1):
            a, b = sorted((s * (BP.NOSE_HW - 0.1), s * (BP.TRAY_HW + 5.2)))
            cl.append(G.rect(a, b, tz, FP.TRAY_Z))
    elif kind == "stop":
        cl.append(("circle", 0.0, zc, BP.STOP_ANNULUS[0]))
        r_out, rim, sp = BP.STOP_ANNULUS[1], BP.STOP_RIM, BP.STOP_SPOKE / 2
        for sy in (1, -1):
            for zr in ((zc + sp, ztp - rim), (zfl + rim, zc - sp)):
                y0, y1 = sorted((sy * sp, sy * (h - rim)))
                cl.append(G.poly_minus_disk(G.rect(y0, y1, zr[0], zr[1]), (0.0, zc), r_out))
    elif kind in ("U", "split"):
        cl.append(("circle", 0.0, zc, BP.U_R))
        cl.append(G.rect(-BP.U_R, BP.U_R, zc, ztp + 5))
        strip = 8.0
        for sy in (1, -1):
            y0, y1 = sorted((0.0, sy * (h - strip)))
            cl.append(G.poly_minus_disk(G.rect(y0, y1, zfl + strip, zc), (0.0, zc), BP.FRAME_BAND_R))
    elif kind == "bulkhead":
        bar = (TUBE_Z - TUBE_R - 6.0, TUBE_Z + TUBE_R + 6.0)
        for s in (1, -1):
            cl.append(("circle", s * TUBE_Y, TUBE_Z, TUBE_R))
        cl.append(G.rect(-(h - 5), h - 5, bar[1], ztp - 5))
        cl.append(G.rect(-(h - 5), h - 5, zfl + 5, bar[0]))
    elif kind == "end":
        for s in (1, -1):
            cl.append(("circle", s * TUBE_Y, TUBE_Z, TUBE_R))
    return [c for c in cl if (isinstance(c, tuple) or len(c) >= 3)]


def build_formers():
    for n, x0, kind, mat in FORMERS:
        g = GEOM[n]
        fr = G.frame((x0, 0.0, 0.0), (0, 1, 0), (0, 0, 1))
        cl = former_cutters(n, g, kind)
        if kind == "split":
            for s, S in ((1, "R"), (-1, "L")):
                yr = (BP.SPLIT_HW, g["hi"]) if s > 0 else (-g["hi"], -BP.SPLIT_HW)
                poly = former_outline(n, g, kind, yr)
                nm = "%s-%s" % (n, S)
                add(nm, "Pod_Formers", poly, FT, fr, mat, cl, lbl(poly, cl, nm + "\nUP ^", h=3.0), former=n)
            continue
        poly = former_outline(n, g, kind)
        prefer = (0.0, 0.5 * (g["zfl"] + RP.AXIS_Z - BP.U_R)) if kind in ("U",) else None
        add(n, "Pod_Formers", poly, FT, fr, mat, cl, lbl(poly, cl, n + " UP ^", h=4.0, prefer=prefer), former=n)


# ---------------- saddles and strap bridges ----------------
def build_saddles():
    base = G.poly_minus_disk(G.rect(-SADDLE_HW, SADDLE_HW, FLOOR_TOP, SADDLE_TOP), (0.0, RP.AXIS_Z), SADDLE_R)
    i = G.find_edge(base, lambda u, v: abs(v - FLOOR_TOP) < 1e-6)
    P = base[i]
    outline = G.tabs_on_edge(base, i, [y - P[0] for y in (-SADDLE_TAB_Y, SADDLE_TAB_Y)], TAB_W, T_FL)
    cl = []
    for s in (1, -1):
        y0, y1 = sorted((s * (BP.KEEL_Y - 0.2), s * (BP.KEEL_Y + BP.KEEL_W + 0.2)))
        cl.append(G.rect(y0, y1, FLOOR_TOP - 2, FLOOR_TOP + BP.KEEL_H + 0.2))
    # lightening: a 5 mm band stays round the bottle, along the floor and at the sides, plus a centre post
    band = 5.0
    for sy in (1, -1):
        y0, y1 = sorted((sy * 3.0, sy * (SADDLE_HW - band)))
        win = G.poly_minus_disk(G.rect(y0, y1, FLOOR_TOP + 7.0, SADDLE_TOP - band), (0.0, RP.AXIS_Z), SADDLE_R + band)   # 7 mm over the keel notches
        if len(win) >= 3 and abs(G.area(win)) > 20:
            cl.append(win)
    pins = [("circle", -38.5, -88.0, 1.05), ("circle", 38.5, -88.0, 1.05), ("circle", 0.0, -103.0, 1.05)]
    for n, (sa, sb) in SADDLES:
        nl = int(round((sb - sa) / BP.SADDLE_LAYER))
        for j in range(nl):
            x0 = sa + j * BP.SADDLE_LAYER
            fr = G.frame((x0, 0.0, 0.0), (0, 1, 0), (0, 0, 1))
            nm = "%s%s" % (n, "abcd"[j])
            mat = "liteply" if j in (0, nl - 1) else "balsa_med"      # outer layers lite-ply (tabs), inner layers balsa
            add(nm, "Pod_Saddles", outline, BP.SADDLE_LAYER, fr, mat, cl + pins, [(nm, 0.0, -109.0, 2.5)])
        xc = BRIDGE_XC[n]
        for s, S in ((1, "R"), (-1, "L")):
            br = [(xc - 12, FLOOR_TOP - T_FL), (xc - 9, FLOOR_TOP - T_FL), (xc - 9, FLOOR_TOP + 3.0),
                  (xc + 9, FLOOR_TOP + 3.0), (xc + 9, FLOOR_TOP - T_FL), (xc + 12, FLOOR_TOP - T_FL),
                  (xc + 12, FLOOR_TOP + 6.0), (xc - 12, FLOOR_TOP + 6.0)]
            y_or = BRIDGE_Y[1] if s > 0 else -BRIDGE_Y[0]
            fr = G.frame((0.0, y_or, 0.0), (1, 0, 0), (0, 0, 1))      # w = -Y
            nm = "%sB%s" % (n, S)
            add(nm, "Pod_Saddles", G.ccw(br), BRIDGE_Y[1] - BRIDGE_Y[0], fr, "liteply", [], [(nm, xc, FLOOR_TOP + 4.5, 2.0)])


# ---------------- strips (strip stock, cut to length; not laser) ----------------
def build_strips():
    fr_xy = G.frame((0.0, 0.0, FLOOR_TOP), (1, 0, 0), (0, 1, 0))
    for s, S in ((1, "R"), (-1, "L")):
        y0, y1 = sorted((s * BP.KEEL_Y, s * (BP.KEEL_Y + BP.KEEL_W)))
        add("Keel-%s" % S, "Pod_Strips", G.rect(KEEL_X[0], KEEL_X[1], y0, y1), BP.KEEL_H, fr_xy, "balsa_med")
        for j, (a, b) in enumerate(LONG_SEGS[s]):
            wi = BP.KEEL_Y * 0 + (FP.Y_LIMIT - T_LAM)
            t = BP.LONGERON
            tri = [(s * wi, FLOOR_TOP), (s * (wi - t), FLOOR_TOP), (s * wi, FLOOR_TOP + t)]
            fr = G.frame((a, 0.0, 0.0), (0, 1, 0), (0, 0, 1))
            add("Longeron-%s%d" % (S, j + 1), "Pod_Strips", G.ccw(tri), b - a, fr, "balsa_med")
        # wing-seat capstrip: bent 6 x 3 strip under the seat line, X 0 .. 236
        wi = FP.Y_LIMIT - T_LAM
        xs = [CAP_X[0]] + [x for x, _ in BP.TOP if CAP_X[0] < x < CAP_X[1]] + [CAP_X[1]]
        band = [(x, zt(x)) for x in xs] + [(x, zt(x) - BP.LIP_T) for x in reversed(xs)]
        oy = wi if s > 0 else -(wi - BP.LIP_W)
        fr = G.frame((0.0, oy, 0.0), (1, 0, 0), (0, 0, 1))
        add("Capstrip-%s" % S, "Pod_Strips", G.ccw(band), BP.LIP_W, fr, "balsa_med")
        # hatch ledges 3 x 3: nose (straight in plan and profile) and front (flat)
        for j, (a, b) in enumerate(LEDGE_X):
            k = seg_of(0.5 * (a + b))
            if k == 1:
                oy = wi if s > 0 else -(wi - BP.LEDGE)
                fr = G.frame((0.0, oy, 0.0), (1, 0, 0), (0, 0, 1))
                add("Ledge-%s%d" % (S, j + 1), "Pod_Strips", G.rect(a, b, zt(a) - BP.LEDGE, zt(a)), BP.LEDGE, fr, "balsa_med")
            else:
                # nose: a band under the (straight) top line in the side panel's own frame, inside the laminate
                ua, ub = sorted((side_u(s, k, a), side_u(s, k, b)))
                xa_, xb_ = (a, b) if s > 0 else (b, a)
                band = G.ccw([(ua, zt(xa_)), (ub, zt(xb_)), (ub, zt(xb_) - BP.LEDGE), (ua, zt(xa_) - BP.LEDGE)])
                add("Ledge-%s%d" % (S, j + 1), "Pod_Strips", band, BP.LEDGE, side_frame(s, k), "balsa_med", z0=T_LAM)


# ---------------- skins on top, small parts ----------------
def build_top():
    # nose hatch: 2 halves (L / R) with dovetail keys on the centreline, light balsa, grain X
    Ls = math.hypot(K0 - XF, zt(K0) - zt(XF))
    frn = G.frame((XF, 0.0, zt(XF)), (K0 - XF, 0.0, zt(K0) - zt(XF)), (0, 1, 0))
    u1 = Ls - KINK_TRIM
    keys = [35.0, 95.0]
    r = [(0.2, 0.0), (u1, 0.0), (u1, hw(K0 - KINK_TRIM)), (0.2, hw(XF))]
    r = G.dovetail_edge(r, 0, [k - 0.2 for k in keys], male=True)          # edge starts at u 0.2
    l = [(0.2, -hw(XF)), (u1, -hw(K0 - KINK_TRIM)), (u1, 0.0), (0.2, 0.0)]
    l = G.dovetail_edge(l, 2, [u1 - k for k in keys], male=False)
    add("HN-R", "Pod_Top", r, BP.T_HATCH, frn, "balsa_light", [], lbl(r, [], "HN-R\n< FWD", prefer=(70, 25)))
    add("HN-L", "Pod_Top", l, BP.T_HATCH, frn, "balsa_light", [], lbl(l, [], "HN-L\n< FWD", prefer=(70, -25)))
    # front hatch piece (flat, X kink .. -2.5), grain Y
    frf = G.frame((0.0, 0.0, zt(K0)), (1, 0, 0), (0, 1, 0))
    hf = G.rect(K0 + KINK_TRIM, BP.HATCH_X[1], -FP.Y_LIMIT, FP.Y_LIMIT)
    add("HF", "Pod_Top", hf, BP.T_HATCH, frf, "balsa_light", [], lbl(hf, [], "HF  < FWD", h=4.0))
    # aft deck: flat, inside the tail-cone sides, on the bulkhead and end former (their top tabs pass through)
    Ld = math.hypot(XE - K1, zdeck(XE) - zdeck(K1))
    frd = G.frame((K1, 0.0, zdeck(K1)), (XE - K1, 0.0, zdeck(XE) - zdeck(K1)), (0, 1, 0))
    du = lambda x: (x - K1) * Ld / (XE - K1)
    d0 = 0.15
    deck = [(d0, -hi(K1 + d0, 2)), (Ld, -hi(XE, 2)), (Ld, hi(XE, 2)), (d0, hi(K1 + d0, 2))]
    cl = []
    for n in ("BH", "EF"):
        g = GEOM[n]
        a, b = slot_x(g["x0"], g["x1"], K1, XE)
        for y in TOP_TABS[n]:
            sh = T_FL * abs(ZD_SLOPE) + 0.05
            cl.append(G.rect(du(a) - sh, du(b) + sh, y - TAB_W / 2, y + TAB_W / 2))
    add("DECK", "Pod_Top", deck, T_FL, frd, "balsa_med", cl, lbl(deck, cl, "DECK\n< FWD", h=3.5), z0=-T_FL)


def build_small():
    # battery tray: 1.5 lite-ply on the nose formers' cross bars, tabs into notches in the former legs
    tz = FP.TRAY_Z - BP.TRAY_T
    x0, x1 = BP.TRAY_X[0], FP.STOP_X[0] - 0.2
    tray = G.rect(x0, x1, -BP.TRAY_HW, BP.TRAY_HW)
    fx = [GEOM[n]["x0"] + FT / 2 for n in ("N1", "N2")]
    tray = G.tabs_on_edge(tray, 2, [x1 - x for x in fx], FT, 5.0)
    tray = G.tabs_on_edge(tray, 0, [x - x0 for x in fx], FT, 5.0)
    fr = G.frame((0.0, 0.0, tz), (1, 0, 0), (0, 1, 0))
    add("TRAY", "Pod_Parts", tray, BP.TRAY_T, fr, "liteply", [], lbl(tray, [], "TRAY < FWD", h=4.0))
    # tail servo tray
    wi = FP.Y_LIMIT - T_LAM
    tst = G.rect(TST_X[0], TST_X[1], -wi, wi)
    tst = G.tabs_on_edge(tst, 2, [TST_X[1] - x for x in TST_TABS_X], TAB_W, T_LAM)
    tst = G.tabs_on_edge(tst, 0, [x - TST_X[0] for x in TST_TABS_X], TAB_W, T_LAM)
    cl = []
    for s in (1, -1):
        yc = s * FP.TSERVO_YC
        cl.append(G.rect(FP.TSERVO_XC - TSERVO_OPEN[0] / 2, FP.TSERVO_XC + TSERVO_OPEN[0] / 2, yc - TSERVO_OPEN[1] / 2, yc + TSERVO_OPEN[1] / 2))
        for dx in (-13.75, 13.75):
            cl.append(("circle", FP.TSERVO_XC + dx, yc, 0.75))
    fr = G.frame((0.0, 0.0, TST_Z[0]), (1, 0, 0), (0, 1, 0))
    add("TST", "Pod_Parts", tst, TST_Z[1] - TST_Z[0], fr, "liteply", cl, lbl(tst, cl, "TST\n< FWD", h=3.5, prefer=(217, 0)))
    # firewall (3 mm birch ply) in the PETG nose ring
    fw0, fw1 = BP.FIREWALL_X
    hwf = hw(XF)
    zbf, ztf = zb(XF), zt(XF) + BP.T_HATCH
    fwp = G.rect(-hwf + BP.JIG_T, hwf - BP.JIG_T, zbf + BP.JIG_T, ztf - BP.JIG_T)
    yc, zc = FP.MOTOR_C
    cl = [("circle", yc, zc, 5.0)]
    r16, r19 = FP.XMOUNT[0] / 2, FP.XMOUNT[1] / 2
    for dy, dz in ((r16, 0), (-r16, 0), (0, r19), (0, -r19)):
        cl.append(("circle", yc + dy, zc + dz, 1.6))
    for y, z in FP.FW_COOL:
        cl.append(("circle", y, z, 6.0))
    fr = G.frame((fw0, 0.0, 0.0), (0, 1, 0), (0, 0, 1))
    add("FW", "Pod_Parts", fwp, fw1 - fw0, fr, "ply", cl, [("FW  UP ^", 0.0, -30.0, 3.5)])
    # nose ring (PETG print): front lip X -178 .. -176 (the motor pulls the firewall forward against it),
    # collar X -176 .. -170 round the firewall, glue sleeve X -170 .. -165 inside the panels
    nx0 = BP.NOSE_RING_X[0]
    outer = G.rect(-hwf, hwf, zbf, ztf)
    lip_in = G.rect(-hwf + 4.2, hwf - 4.2, zbf + 4.2, ztf - 4.2)
    fr = G.frame((nx0, 0.0, 0.0), (0, 1, 0), (0, 0, 1))
    d = add("NOSE-RING", "Pod_Parts", outer, 2.0, fr, "petg", [lip_in], [])
    t = BP.JIG_T
    collar = ring_bars(-hwf, hwf, zbf, ztf, t)
    xs0 = XF + 5.0
    h5 = min(hi(XF, 0), hi(xs0, 0)) - 0.1
    sleeve = ring_bars(-h5, h5, max(zf(XF, 0), zf(xs0, 0)) + 0.1, min(zt(XF), zt(xs0)) - 0.1, t)
    d["joins"] = [(collar, 2.0, 8.0), (sleeve, 8.0, 8.0 + (xs0 - XF))]
    # flap stop (D-061)
    fs = BP.FLAP_STOP_PLY
    frz = G.frame((0.0, 0.0, FLOOR_TOP), (1, 0, 0), (0, 1, 0))
    fsp = G.rect(fs[0], fs[1], -fs[2], fs[2])
    add("FLAPSTOP", "Pod_Parts", fsp, fs[3], frz, "ply", [], [("FLAP STOP", 0.5 * (fs[0] + fs[1]), 0.0, 2.2)])
    # stub doublers (3 mm ply) inside the sides at the front band stubs
    x0d, x1d, z0d, z1d, td = BP.STUB_DOUBLER
    for s, S in ((1, "R"), (-1, "L")):
        oy = wi if s > 0 else -(wi - td)
        fr = G.frame((0.0, oy, 0.0), (1, 0, 0), (0, 0, 1))
        sd = G.rect(x0d, x1d, z0d, z1d)
        cl = [("circle", FP.STUB_X, FP.STUB_Z, FP.STUB_D / 2 + 0.1)]
        add("SD-%s" % S, "Pod_Parts", sd, td, fr, "ply", cl, [("SD-%s" % S, -6.0, -17.5, 3.0)])
    # tube rings (3 mm birch ply) on the bulkhead aft face and the end former front face
    for j, xr in enumerate((GEOM["BH"]["x1"], GEOM["EF"]["x0"] - BP.TUBE_RING_T)):
        fr = G.frame((xr, 0.0, 0.0), (0, 1, 0), (0, 0, 1))
        for s, S in ((1, "R"), (-1, "L")):
            ring = G.circle_poly(s * TUBE_Y, TUBE_Z, BP.TUBE_RING_OD / 2, 64)
            add("TR%d%s" % (j + 1, S), "Pod_Parts", ring, BP.TUBE_RING_T, fr, "ply", [("circle", s * TUBE_Y, TUBE_Z, TUBE_R)], [])
    # skids (1.5 mm birch ply) under the floor, one per floor plane
    for nm, k, a, b in (("SK1", 0, -100.0, K0 - KINK_TRIM), ("SK2", 1, K0 + KINK_TRIM, 40.0), ("SK3", 1, 120.0, 230.0)):
        frk = floor_frame(k)
        sk = G.rect(floor_u(k, a), floor_u(k, b), -BP.SKID_HW, BP.SKID_HW)
        add(nm, "Pod_Parts", sk, BP.SKID_T, frk, "ply", [], lbl(sk, [], nm + " < FWD", h=3.5), z0=-BP.SKID_T)


def ring_bars(y0, y1, z0, z1, t):
    """A rectangular frame of wall t as 4 bars (no inner profile in the sketch)."""
    return [G.rect(y0, y1, z0, z0 + t), G.rect(y0, y1, z1 - t, z1), G.rect(y0, y0 + t, z0 + t, z1 - t), G.rect(y1 - t, y1, z0 + t, z1 - t)]


def build_hard():
    """Non-laser bought / printed parts of the pod: band stubs, rear dowel, release-servo mount (PETG)."""
    out = []
    for s, S in ((1, "R"), (-1, "L")):
        out.append(("tube", "STUB-%s" % S, (FP.STUB_X, s * (FP.Y_LIMIT - FP.STUB_IN), FP.STUB_Z),
                    (FP.STUB_X, s * (FP.Y_LIMIT + FP.STUB_OUT), FP.STUB_Z), FP.STUB_D / 2, 0.0, "carbon"))
    out.append(("tube", "DOWEL", (FP.DOWEL_X, -39.7, FP.DOWEL_Z), (FP.DOWEL_X, 39.7, FP.DOWEL_Z), FP.DOWEL_D / 2, 0.0, "birch"))
    return out


def build_servo_mount():
    """PETG D-059 arm pocket (through the window in the right ply insert) + release-servo shelves and gussets."""
    (px0, px1), (pz0, pz1) = FP.POCKET_X, FP.POCKET_Z
    w = FP.POCKET_WALL
    fr = G.frame((0.0, 0.0, FLOOR_TOP), (1, 0, 0), (0, 1, 0))
    y_in = FP.Y_LIMIT - T_LAM + 0.1        # 52.6
    cup = G.rect(px0 - w, px1 + w, y_in, FP.POCKET_YIN + w)
    d = add("SERVO-MOUNT", "Pod_Parts", cup, (pz1 + w) - FLOOR_TOP, fr, "petg", [], [])
    d["pockets"] = [([G.rect(px0, px1, y_in - 1.0, FP.POCKET_YIN)], pz0 - FLOOR_TOP, pz1 - FLOOR_TOP)]
    # servo: case X 58.46 .. 81.26 (shaft 5.9 from the front end at X 64.36), tabs 4.85 each end
    m = RP.MG90S
    cx0 = RP.SERVO_X_SHAFT - m["SHAFT_FROM_END"]
    cx1 = cx0 + m["L"]
    tx0, tx1 = cx0 - (m["TAB_L"] - m["L"]) / 2, cx1 + (m["TAB_L"] - m["L"]) / 2
    tz0 = -101.4
    ys0 = RP.SERVO_Y_SHAFT - m["W"] / 2
    wall = FP.Y_LIMIT - T_OUT               # 53.5 inner face of the single ply layer
    shelves = [G.rect(tx0 - 0.5, tx0 + 4.5, ys0, wall), G.rect(tx1 - 4.5, tx1 + 0.5, ys0, wall)]
    gus = [G.rect(0.5 * (tx0 + tx0 + 4.0) - 0.6, 0.5 * (tx0 + tx0 + 4.0) + 0.6, ys0 + m["W"] + 0.5, wall),
           G.rect(0.5 * (tx1 + tx1 - 4.0) - 0.6, 0.5 * (tx1 + tx1 - 4.0) + 0.6, ys0 + m["W"] + 0.5, wall)]
    d["joins"] = [(shelves, tz0 - 3.0 - FLOOR_TOP, tz0 - FLOOR_TOP), (gus, tz0 - FLOOR_TOP, tz0 + 12.0 - FLOOR_TOP)]
    d["note"] = "release servo case X %.2f..%.2f, tabs on the shelves at Z %.1f" % (cx0, cx1, tz0)
    return dict(case=(cx0, cx1, ys0, ys0 + m["W"], tz0 - 3.7, tz0 - 3.7 + m["H"]), tabs=(tx0, tx1, tz0, tz0 + m["TAB_T"]))


def all_parts():
    del PARTS[:]
    build_sides()
    build_floor()
    build_formers()
    build_saddles()
    build_strips()
    build_top()
    build_small()
    servo = build_servo_mount()
    return PARTS, build_hard(), servo


if __name__ == "__main__":
    parts, hard, servo = all_parts()
    for p in parts:
        u0, u1, v0, v1 = G.bbox(p["outline"])
        print("%-12s %-12s %-11s %6.1f x %6.1f t %.1f  cut %2d  lab %s" % (p["name"], p["grp"], p["mat"], u1 - u0, v1 - v0, p["t"],
                                                                     len(p["cutters"]), [l[0].split("\n")[0] for l in p["labels"]]))
    print(len(parts), "parts;", {n: [round(z, 1) for z in SIDE_TABS[n]] for n in SIDE_TABS})
    print({n: {k: round(v, 2) if isinstance(v, float) else v for k, v in g.items()} for n, g in GEOM.items()})
    print("rod cross x", rod_cross_x(1), rod_cross_x(-1))
