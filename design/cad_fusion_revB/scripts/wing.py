"""Wing rev A remodelled for Fusion and laser cutting. Numbers: design/cad/scripts/wing_params.py (P).
Wing frame (before the +3 deg incidence): origin LE on the centreline, X aft, Y right (span), Z up; chord line Z 0.

Changes for building (manufacturability / strength), see ../README.md:
- Ribs are one piece LE stock to TE stock (6 .. 255; aileron-span ribs 6 .. 208).
- False spar: 3 mm balsa, grain span-wise, in 3 pieces per side (<= 300 mm) joined by dovetail keys; egg-crate joint
  with every rib (spar slotted from below, rib slotted from above). CA-hinge slots laser-cut in the false spar.
  (rev A: vertical grain pieces between ribs, D-015.)
- Shear webs (vertical grain, between ribs) have end tabs that lock into slots in the ribs (inboard tab high,
  outboard tab low, so the two webs at a rib never clash).
- Spar caps (3 x 6 hard balsa + 0.5 x 6 carbon) run through notches in the ribs, as rev A.
- Every laser part (ribs, aileron ribs, webs, false spar, tip ring) carries its engraved name and an LE arrow."""
import math
import geo as G
import wing_params as P

A = G.Airfoil(P.AIRFOIL, P.CHORD)
SK = P.SKIN_T
YE = P.Y_END
X0S, X1S = P.X_SPAR
CAP_T = P.CAP_BALSA_T + P.CAP_CARBON_T
FS0, FS1 = P.X_FS
WEB_T = P.WEB_T
WF_X = (X0S - WEB_T, X0S)
WR_X = (X1S, X1S + WEB_T)
FULL = {0.0, 55.0, 110.0, 439.5, P.TIP_RIB[0]}
RIB_GAP = 0.05          # ribs 0.05 inside the skin line (sheeting / cap strips are polylines of the same curve)


def zu_in(x):
    return A._off(x, SK, True)


def zl_in(x):
    return A._off(x, SK, False)


def rng(f, x0, x1, n=12, mode=min):
    return mode(f(x0 + (x1 - x0) * i / n) for i in range(n + 1))


ZT = rng(zu_in, X0S, X1S, mode=min)          # top of the top spar cap (carbon outer face)
ZB = rng(zl_in, X0S, X1S, mode=max)
ZH = 0.5 * (A.zu(P.HINGE_X) + A.zl(P.HINGE_X))
FS_ZMID = 0.5 * (rng(zu_in, FS0, FS1, mode=min) + rng(zl_in, FS0, FS1, mode=max))


def zmid_in(x0, x1):
    return 0.5 * (rng(zu_in, x0, x1, mode=min) + rng(zl_in, x0, x1, mode=max))


WEB_ZM = {"F": zmid_in(*WF_X), "R": zmid_in(*WR_X)}
TAB_H = 4.0

STATIONS = [P.RIB_C] + list(P.RIBS) + [P.TIP_RIB]       # (y, t)
NAME = {0.0: "C", P.TIP_RIB[0]: "TIP"}


def rib_name(y):
    return NAME.get(y, "R%03d" % round(y))


PARTS = []


def add(name, grp, outline, t, fr, mat, cutters=(), labels=(), z0=0.0, **kw):
    d = dict(name=name, grp=grp, outline=outline, t=t, fr=fr, mat=mat, cutters=list(cutters), labels=list(labels), z0=z0)
    d.update(kw)
    PARTS.append(d)
    return d


def yprism(name, grp, outline, a, b, mat, cutters=(), labels=()):
    """XZ outline occupying y a..b (b > a): frame w = -Y from y = b."""
    fr = G.frame((0.0, b, 0.0), (1, 0, 0), (0, 0, 1))
    return add(name, grp, outline, b - a, fr, mat, cutters, labels)


def both_y(name, grp, outline, a, b, mat, cutters=(), labels_fn=None):
    for s, S in ((1, "R"), (-1, "L")):
        lo, hi = (a, b) if s > 0 else (-b, -a)
        labs = labels_fn(name + "-" + S) if labels_fn else []
        yprism(name + "-" + S, grp, outline, lo, hi, mat, cutters, labs)


def lbl(poly, cutters, text, h=3.5, prefer=None, min_h=2.0):
    while h >= min_h:
        p = G.label_spot(poly, cutters, text, h, prefer=prefer)
        if p:
            return [(text, p[0], p[1], h)]
        h -= 0.5
    return []


# ---------------- section helpers ----------------
def outer_clip(x0, x1):
    return G.clip_rect(G.ccw(A.outline()), x0, x1, -100, 100)


def skin_band(x0, x1, upper, n=40):
    xs = [x0 + (x1 - x0) * (1 - math.cos(math.pi * i / n)) / 2 for i in range(n + 1)]
    if upper:
        a = [(x, A.zu(x)) for x in xs]
        b = [(x, zu_in(x)) for x in reversed(xs)]
    else:
        a = [(x, A.zl(x)) for x in xs]
        b = [(x, zl_in(x)) for x in reversed(xs)]
    return G.ccw(G.clean(a + b))


def lower_band(x0, x1, t0, t1, n=30):
    xs = [x0 + (x1 - x0) * i / n for i in range(n + 1)]
    return G.ccw([(x, A.zl(x) + t0) for x in xs] + [(x, A.zl(x) + t1) for x in reversed(xs)])


# ---------------- ribs ----------------
def holes_for(y):
    skip = P.HOLE_SKIP.get(y, [])
    hs = []
    for xc in P.HOLE_X:
        if xc in skip:
            continue
        dd = min(zu_in(xc) - zl_in(xc) - 2 * P.HOLE_MARGIN, P.HOLE_DMAX)
        if dd >= 6.0:
            hs.append(("circle", xc, 0.5 * (zu_in(xc) + zl_in(xc)), dd / 2))
    if y == 110.0:
        xc, dd = P.WIRE_HOLE
        hs.append(("circle", xc, 0.5 * (zu_in(xc) + zl_in(xc)), dd / 2))
    return hs


def rib_cutters(y):
    cl = [G.rect(X0S, X1S, ZT - CAP_T, 60.0), G.rect(X0S, X1S, -60.0, ZB + CAP_T)]       # spar caps
    cl.append(G.rect(FS0, FS1, FS_ZMID, 60.0))                                           # false spar egg-crate
    zf = WEB_ZM["F"]
    cl.append(G.rect(WF_X[0], WF_X[1], zf - TAB_H - 0.5, zf + TAB_H + 0.5))              # front web tabs
    if abs(y) <= P.REAR_WEB_Y + 2.0:
        zr = WEB_ZM["R"]
        cl.append(G.rect(WR_X[0], WR_X[1], zr - TAB_H - 0.5, zr + TAB_H + 0.5))          # rear web tabs
    return cl


def build_ribs():
    for y, t in STATIONS:
        x1 = P.X_TE if y in FULL else FS1
        outline = A.inset(SK + RIB_GAP, P.X_LE, x1)
        nm = rib_name(y)
        mat = "balsa_light" if y == P.TIP_RIB[0] else "balsa_med"
        cl = rib_cutters(y) + ([] if y == P.TIP_RIB[0] else holes_for(y))
        if y == 0.0:
            yprism("W-C", "Wing_Ribs", outline, -t / 2, t / 2, mat, cl, lbl(outline, cl, "W-C  < LE", prefer=(140, 6)))
            continue
        for s, S in ((1, "R"), (-1, "L")):
            n2 = "W-%s-%s" % (nm, S)
            lo, hi = (y - t / 2, y + t / 2) if s > 0 else (-y - t / 2, -y + t / 2)
            yprism(n2, "Wing_Ribs", outline, lo, hi, mat, cl, lbl(outline, cl, n2 + "  < LE", prefer=(140, 6)))
    # tip cap: 3 mm light outline ring, 10 mm wide
    out = G.ccw(A.outline())
    xa = next(x for x in [i * 0.5 for i in range(2, 559)] if A.zu(x) - A.zl(x) >= 2 * P.TIP_RING_W + 2)
    xb = max(x for x in [i * 0.5 for i in range(2, 559)] if A.zu(x) - A.zl(x) >= 2 * P.TIP_RING_W + 2)
    inner = A.inset(P.TIP_RING_W, xa, xb)
    for s, S in ((1, "R"), (-1, "L")):
        lo, hi = (P.TIP_CAP[0], P.TIP_CAP[1]) if s > 0 else (-P.TIP_CAP[1], -P.TIP_CAP[0])
        yprism("W-TIPCAP-" + S, "Wing_Ribs", out, lo, hi, "balsa_light", [inner], [("TIPCAP-" + S, 240.0, 4.2, 2.2)])


# ---------------- false spar, webs ----------------
FSP_SPLITS = [145.0, 357.5]
KEY = dict(w_neck=5.0, w_head=8.0, depth=4.0)


def yz_plate(name, grp, poly_right, x0, t, mat, cutters, labels, s):
    """A plate in the YZ plane at x0 .. x0 + t. poly_right in (Y, Z); s = -1 mirrors it to the left side."""
    fr = G.frame((x0, 0.0, 0.0), (0, 1, 0), (0, 0, 1))
    if s < 0:
        poly = G.ccw([(-u, v) for u, v in poly_right])
        cl = []
        for c in cutters:
            cl.append(("circle", -c[1], c[2], c[3]) if isinstance(c, tuple) else G.ccw([(-u, v) for u, v in c]))
        labs = [(tx, -u, v, h) for tx, u, v, h in labels]
        return add(name, grp, poly, t, fr, mat, cl, labs)
    return add(name, grp, poly_right, t, fr, mat, cutters, labels)


def build_false_spar():
    zl = rng(A.zl, FS0, FS1, mode=max)
    zu = rng(A.zu, FS0, FS1, mode=min)
    pieces = [(-FSP_SPLITS[0], FSP_SPLITS[0], "C")] + [(a, b, "R%d" % (i + 1)) for i, (a, b) in
                                                       enumerate(zip(FSP_SPLITS, FSP_SPLITS[1:] + [YE]))]
    for a, b, tag in pieces:
        poly = G.rect(a, b, zl, zu)
        # keys: male on the outboard end of the inner piece, female on the inboard end of the next piece
        if b < YE - 1:
            poly = G.dovetail_edge(poly, 1, [0.5 * (zu - zl)], male=True, **KEY)
        if tag != "C" and a > 0:
            i = G.find_edge(poly, lambda u, v: abs(u - a) < 1e-6)
            poly = G.dovetail_edge(poly, i, [0.5 * (zu - zl)], male=False, **KEY)
        cl = []
        for y, t in STATIONS:
            for yy in ((y,) if y == 0 else (y, -y)):
                if a - 1 < yy < b + 1:
                    cl.append(G.rect(yy - t / 2, yy + t / 2, zl - 1.0, FS_ZMID))
        for yc in P.HINGE_Y:
            for yy in (yc, -yc):
                if a < yy - P.HINGE_W / 2 and yy + P.HINGE_W / 2 < b:
                    cl.append(G.rect(yy - P.HINGE_W / 2, yy + P.HINGE_W / 2, ZH - P.HINGE_SLOT_T / 2, ZH + P.HINGE_SLOT_T / 2))
        if tag == "C":
            yz_plate("FSP-C", "Wing_Spars", poly, FS0, FS1 - FS0, "balsa_med", cl, lbl(poly, cl, "FSP-C", h=3.0, prefer=(30, ZH + 4)), 1)
        else:
            for s, S in ((1, "R"), (-1, "L")):
                nm = "FSP-%s%s" % (S, tag[1:])
                yz_plate(nm, "Wing_Spars", poly, FS0, FS1 - FS0, "balsa_med", cl,
                         lbl(poly, cl, nm, h=3.0, prefer=(0.5 * (a + b), ZH + 4)), s)


def build_webs():
    faces = [(y - t / 2, y + t / 2, t) for y, t in STATIONS]
    for kind, xr in (("F", WF_X), ("R", WR_X)):
        zm = WEB_ZM[kind]
        zl = rng(zl_in, *xr, mode=max)
        zu = rng(zu_in, *xr, mode=min)
        for j, (fa, fb) in enumerate(zip(faces, faces[1:])):
            ya, yb = fa[1], fb[0]
            if kind == "R" and yb > P.REAR_WEB_Y + 1e-6:
                continue
            if ya < 0:            # centre rib: the bay starts at its right face
                ya = fa[1]
            poly = G.rect(ya, yb, zl, zu)
            # right edge (outboard, edge 1): low tab into the outboard rib; left edge (edge 3): high tab into the inboard rib
            t_in = fa[2] / 2 if j == 0 else fa[2]          # centre rib: right web high half, left web the other half
            poly = G.tabs_on_edge(poly, 3, [zu - (zm + TAB_H / 2 + 0.5)], TAB_H, t_in)
            poly = G.tabs_on_edge(poly, 1, [(zm - TAB_H / 2 - 0.5) - zl], TAB_H, fb[2])
            for s, S in ((1, "R"), (-1, "L")):
                nm = "W%s-%s%d" % (kind, S, j + 1)
                labs = [(nm, 0.5 * (ya + yb), zm + (8.0 if zu - zm > 12 else 0.0), 2.5)] if yb - ya > 20 else []
                yz_plate(nm, "Wing_Spars", poly, xr[0], WEB_T, "balsa_med", [], labs, s)


# ---------------- strip stock, sheeting, TE, ailerons ----------------
def build_strips():
    yprism("LE", "Wing_Sheeting", outer_clip(0.0, P.X_LE), -YE, YE, "balsa_med")
    yprism("DBOX-TOP", "Wing_Sheeting", skin_band(P.X_LE, P.X_DBOX, True), -YE, YE, "balsa_light")
    yprism("DBOX-BOT", "Wing_Sheeting", skin_band(P.X_LE, P.X_DBOX, False), -YE, YE, "balsa_light")
    yprism("CAP-C-TOP", "Wing_Spars", G.rect(X0S, X1S, ZT - P.CAP_CARBON_T, ZT), -YE, YE, "carbon")
    yprism("CAP-B-TOP", "Wing_Spars", G.rect(X0S, X1S, ZT - CAP_T, ZT - P.CAP_CARBON_T), -YE, YE, "balsa_hard")
    yprism("CAP-C-BOT", "Wing_Spars", G.rect(X0S, X1S, ZB, ZB + P.CAP_CARBON_T), -YE, YE, "carbon")
    yprism("CAP-B-BOT", "Wing_Spars", G.rect(X0S, X1S, ZB + P.CAP_CARBON_T, ZB + CAP_T), -YE, YE, "balsa_hard")
    te = outer_clip(P.X_TE, P.CHORD)
    yprism("TE-C", "Wing_Sheeting", te, -111.5, 111.5, "balsa_hard")
    both_y("TE-O", "Wing_Sheeting", te, 438.5, YE, "balsa_hard")
    # centre sheeting (y 0 .. 56 each side), chord-wise grain
    for tag, (xa, xb) in (("F", (P.X_DBOX, FS0)), ("A", (FS1, P.X_TE))):
        for up, U in ((True, "T"), (False, "B")):
            both_y("CS-%s%s" % (U, tag), "Wing_Sheeting", skin_band(xa, xb, up), 0.0, P.Y_CSHEET, "balsa_light")
    # cap strips 1.5 x 6 on the rib edges outboard of the centre sheeting
    for y, t in list(P.RIBS) + [P.TIP_RIB]:
        if y <= 55.0:
            continue
        if y == P.TIP_RIB[0]:
            fy = (y + t / 2 - 6.0, y + t / 2)
            ay = fy
        else:
            fy = (y - 3.0, y + 3.0)
            ay = (y + t / 2 - 6.0, y + t / 2) if y == 110.0 else ((y - t / 2, y - t / 2 + 6.0) if y == 439.5 else None)
        nm = rib_name(y)
        for up, U in ((True, "T"), (False, "B")):
            both_y("CAPS-%s-%sF" % (nm, U), "Wing_Caps", skin_band(P.X_DBOX, FS0, up, 24), fy[0], fy[1], "balsa_light")
            if ay:
                both_y("CAPS-%s-%sA" % (nm, U), "Wing_Caps", skin_band(FS1, P.X_TE, up, 16), ay[0], ay[1], "balsa_light")


def build_ailerons():
    y0, y1 = P.AIL_Y
    x0 = P.AIL_X[0]
    k = (P.AIL_LE_T - P.AIL_BEVEL) / 7.7
    le = outer_clip(x0, x0 + P.AIL_LE_T)
    for (pa, pb) in (((x0, ZH), (x0 + k * 25, ZH + 25)), ((x0 + k * 25, ZH - 25), (x0, ZH))):
        # keep the side of the line pa -> pb that contains the strip (x > line)
        a, b = pb[1] - pa[1], -(pb[0] - pa[0])
        c = a * pa[0] + b * pa[1]
        if a * (x0 + 2.5) + b * ZH > c:
            a, b, c = -a, -b, -c
        le = G.clip_half(le, a, b, c)
    le = G.ccw(G.clean(le))
    both_y("AIL-LE", "Wing_Aileron", le, y0, y1, "balsa_med")
    both_y("AIL-TE", "Wing_Aileron", outer_clip(P.X_TE, P.CHORD), y0, y1, "balsa_med")
    rib = outer_clip(x0 + P.AIL_LE_T, P.X_TE)
    ys = [(y0, y0 + P.AIL_RIB_T, "A112")] + [(y - P.AIL_RIB_T / 2, y + P.AIL_RIB_T / 2, "A%03d" % y) for y in P.AIL_RIB_Y] + \
         [(y1 - P.AIL_RIB_T, y1, "A437")]
    for a, b, nm in ys:
        for s, S in ((1, "R"), (-1, "L")):
            lo, hi = (a, b) if s > 0 else (-b, -a)
            n2 = "%s-%s" % (nm, S)
            yprism(n2, "Wing_Aileron", rib, lo, hi, "balsa_med", [], lbl(rib, [], n2 + " <LE", h=2.5, min_h=1.8))


def build_servo_bay():
    """PETG servo frame (4 rails) and hatch on the lower skin between ribs 110 and 165; MG90S placeholder."""
    S = P.MG90S
    fx0, fx1 = P.FRAME_X
    ox0, ox1 = P.FRAME_OPEN_X
    by0, by1 = P.BAY_Y
    oy0, oy1 = P.FRAME_OPEN_Y
    for s, Sd in ((1, "R"), (-1, "L")):
        def yr(a, b):
            return (a, b) if s > 0 else (-b, -a)
        d = yprism("SERVO-HATCH-" + Sd, "Wing_Servo", lower_band(fx0, fx1, 0.0, P.HATCH_T), *yr(by0, by1), "petg")
        import linkage
        sx0, sx1, sy0, sy1 = linkage.hatch_slot()
        hi_ = yr(by0, by1)[1]
        wa, wb = sorted((hi_ - s * sy0, hi_ - s * sy1))
        d["plane_cuts"] = [("xz", [[(sx0, 0.0, wa), (sx1, 0.0, wa), (sx1, 0.0, wb), (sx0, 0.0, wb)]])]   # arm slot
        # frame: front and rear rails over the full bay width, side rails between them
        a, b = yr(by0, by1)
        d = yprism("SERVO-FRAME-" + Sd, "Wing_Servo", lower_band(fx0, ox0, P.HATCH_T, P.HATCH_T + P.RING_T), a, b, "petg")
        rails = [(lower_band(ox1, fx1, P.HATCH_T, P.HATCH_T + P.RING_T), a, b),
                 (lower_band(ox0, ox1, P.HATCH_T, P.HATCH_T + P.RING_T), *yr(by0, oy0)),
                 (lower_band(ox0, ox1, P.HATCH_T, P.HATCH_T + P.RING_T), *yr(oy1, by1))]
        d["joins"] = [([poly], b - y1_, b - y0_) for poly, y0_, y1_ in rails]     # frame w = b - y
    # servo placeholder box (case lies flat, shaft +Y outboard)
    xs_ = P.SERVO_SHAFT_X
    cx1 = xs_ + S["SHAFT_FROM_END"]
    cx0 = cx1 - S["L"]
    zl_max = max(A.zl(cx0 - 5 + i) for i in range(int(S["TAB_L"]) + 1))
    zc0 = zl_max + P.HATCH_T + P.SERVO_GAP
    return [("box", "SERVO-W-%s" % Sd, (cx0, cx1, *( (P.SERVO_Y0, P.SERVO_Y0 + S["H"]) if s > 0 else (-P.SERVO_Y0 - S["H"], -P.SERVO_Y0)), zc0, zc0 + S["W"]))
            for s, Sd in ((1, "R"), (-1, "L"))]


def all_parts():
    del PARTS[:]
    build_ribs()
    build_false_spar()
    build_webs()
    build_strips()
    build_ailerons()
    boxes = build_servo_bay()
    import linkage
    pk = linkage.hinge_pockets()
    for p in PARTS:
        if p["name"] in pk:
            p["pockets"] = pk[p["name"]]
    return PARTS, boxes


if __name__ == "__main__":
    parts, boxes = all_parts()
    for p in parts:
        u0, u1, v0, v1 = G.bbox(p["outline"])
        print("%-16s %-14s %-11s %6.1f x %6.1f t %6.1f cut %2d lab %s" % (p["name"], p["grp"], p["mat"], u1 - u0, v1 - v0, p["t"],
                                                                     len(p["cutters"]), [l[0] for l in p["labels"]]))
    print(len(parts), "parts", boxes)
    print("ZT %.2f ZB %.2f ZH %.2f FS_ZMID %.2f WEB_ZM %s" % (ZT, ZB, ZH, FS_ZMID, WEB_ZM))
