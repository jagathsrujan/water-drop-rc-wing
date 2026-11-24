"""3D-printed assembly jigs (PLA, removable, not in the aircraft mass) for the Fusion rev B model.
All jigs fit a 256 x 256 x 256 mm bed (Bambu P1S, BP.PRINT_BED), carry their engraved name, have 4.5 mm holes for
wood screws into the building board, and lightening pockets / windows (print at 3 walls, 20-30 % infill).

Pod board  = flat board at Z -117 (the underside of the bay floor), aircraft frame.
Wing board = flat board at Z -16 in the WING frame (chord line Z 0, before the +3 deg incidence); the wing is built
             lower surface down in the cradles, which set the airfoil and zero twist.
Tail       = jigs that sit on the booms / on the stabiliser, used after the booms are glued (J4 cradles)."""
import math
import geo as G
import pod as POD
import tail as TL
import fus_params as FP
import bal_params as BP

BZ = FP.BELLY_Z                       # -117
SCREW_R = 2.25                        # 4.5 mm clearance for 4 mm wood screws
BED = BP.PRINT_BED
MAT = "pla_jig"
PARTS = []


def add(name, grp, outline, t, fr, cutters=(), labels=(), z0=0.0, **kw):
    d = dict(name=name, grp=grp, outline=outline, t=t, fr=fr, mat=MAT, cutters=list(cutters), labels=list(labels), z0=z0)
    d.update(kw)
    PARTS.append(d)
    return d


def lbl(poly, cutters, text, h=4.0, prefer=None, min_h=2.0):
    while h >= min_h:
        p = G.label_spot(poly, cutters, text, h, prefer=prefer)
        if p:
            return [(text, p[0], p[1], h)]
        h -= 0.5
    return []


def windows_under(top, x_ranges, z_bot, inset_top=4.0, n=12, min_h=4.0):
    """Windows between z_bot and a top curve top(x) - inset_top, one per x range (lightening)."""
    out = []
    for a, b in x_ranges:
        xs = [a + (b - a) * i / n for i in range(n + 1)]
        tops = [top(x) - inset_top for x in xs]
        if min(tops) - z_bot < min_h:
            continue
        out.append(G.ccw([(a, z_bot), (b, z_bot)] + [(x, z) for x, z in zip(reversed(xs), reversed(tops))]))
    return out


# ---------------- pod board jigs ----------------
def j1_wedges():
    """J1a / J1b: wedges screwed to the board; the bay floor lies on the board, the wedges hold the nose floor and the
    tail-cone floor at their angles. Width +-26 (inside the narrowest floor), groove for skid SK1."""
    hwid = 26.0
    fr = G.frame((0.0, hwid, 0.0), (1, 0, 0), (0, 0, 1))          # XZ profile, w = -Y  (w = 26 - Y)
    zb = POD.zb
    # J1a: X -169.5 .. where the wedge is 3 mm high
    x_end_a = POD.XF + (BZ + 3.0 - zb(POD.XF)) / (zb(POD.K0) - zb(POD.XF)) * (POD.K0 - POD.XF)
    x_start_b = POD.K1 + 3.0 / (zb(POD.XE) - zb(POD.K1)) * (POD.XE - POD.K1)
    for name, xa, xb, ribs in (("J1a-NOSE-WEDGE", POD.XF + 0.5, x_end_a, [-130.0, -100.0, -70.0]),
                               ("J1b-TAIL-WEDGE", x_start_b, POD.XE - 0.5, [272.0])):
        poly = G.ccw([(xa, BZ), (xb, BZ), (xb, zb(xb)), (xa, zb(xa))])
        edges = [xa + 6] + [r for r in ribs] + [xb - 6]
        rng = []
        for a, b in zip(edges, edges[1:]):
            rng.append((a + (0 if a == xa + 6 else 2.0), b - (0 if b == xb - 6 else 2.0)))
        wins = windows_under(zb, rng, BZ + 4.0, inset_top=4.0)
        holes = []
        for r in ribs:
            if zb(r) - BZ > 6:
                for y in (-18.0, 18.0):
                    holes.append(("circle", (r, 0.0, hwid - y), SCREW_R))
        d = add(name, "Jigs_Pod", poly, 2 * hwid, fr, wins, lbl(poly, wins, name.replace("-", " ", 1) + "\nBOARD SIDE DOWN", h=4.0))
        d["plane_cuts"] = [("xz", holes)] if holes else []
        if name.startswith("J1a"):
            sa, sb = -100.5, xb
            groove = G.ccw([(sa, zb(sa) - 1.7), (sb, zb(sb) - 1.7), (sb, zb(sb) + 1.0), (sa, zb(sa) + 1.0)])
            d["pockets"] = [([groove], hwid - (POD.BP.SKID_HW + 0.5), hwid + (POD.BP.SKID_HW + 0.5))]


def j2_squares():
    """J2: four L-squares against the outer side faces (sides vertical while the floor / former joints cure)."""
    y0 = FP.Y_LIMIT
    top = BP.JIG_SQUARE_TOP
    for k, (xa, xb) in enumerate(BP.JIG_SQUARE_X):
        for s, S in ((1, "R"), (-1, "L")):
            L = [(y0, BZ), (y0 + 30, BZ), (y0 + 30, BZ + 5), (y0 + 5, BZ + 5), (y0 + 5, top), (y0, top)]
            gus = [(y0 + 5, BZ + 5), (y0 + 28, BZ + 5), (y0 + 5, top - 3)]
            if s < 0:
                L = [(-u, v) for u, v in L]
                gus = [(-u, v) for u, v in gus]
            L, gus = G.ccw(L), G.ccw(gus)
            fr = G.frame((xa, 0.0, 0.0), (0, 1, 0), (0, 0, 1))       # YZ profile, w = +X
            t = xb - xa
            name = "J2-%d%s-SQUARE" % (k + 1, S)
            d = add(name, "Jigs_Pod", L, t, fr, [], [])
            d["joins"] = [([gus], 0.0, 3.0), ([gus], t - 3.0, t)]
            d["plane_cuts"] = [("xz", [("circle", (s * (y0 + 20.0), 0.0, t / 2), SCREW_R)])]
            d["labels"] = [("J2-%d%s" % (k + 1, S), s * (y0 + 2.5), 0.5 * (BZ + 5 + top), 2.2)]


def j3_nose_blocks():
    """J3: blocks against the outer nose sides, hold them at their plan angle between the front stop and the nose ring."""
    xs, xe = BP.JIG_NOSE_X
    ztop = BP.JIG_NOSE_TOP
    t = ztop - BZ
    fr = G.frame((0.0, 0.0, BZ), (1, 0, 0), (0, 1, 0))               # XY footprint, w = Z - BZ
    hw = lambda x: POD.hw(x) + 0.3          # 0.3 clear of the tilted nose floor edge
    for s, S in ((1, "R"), (-1, "L")):
        poly = G.ccw([(xs, s * hw(xs)), (xe, s * hw(xe)), (xe, s * (hw(xe) + 12.0)), (xs, s * (hw(xs) + 12.0))])
        inner = TL.inset_convex(poly, 3.0)
        holes = [("circle", x, s * (hw(x) + 6.0), SCREW_R) for x in (xs + 15.0, 0.5 * (xs + xe), xe - 15.0)]
        name = "J3-%s-NOSE-TAPER" % S
        d = add(name, "Jigs_Pod", poly, t, fr, holes, [])
        d["pockets"] = [([inner], 4.0, t + 1.0)]
        xm = 0.5 * (xs + xe) + 30.0
        d["labels"] = [("J3-" + S, xm, s * (hw(xm) + 6.0), 4.0)]
        d["label_w"] = 4.0


def j4_cradles():
    """J4: boom cradles. Both tubes lie parallel at Y +-16, Z -40; the front face of J4a squares the end former.
    Glue the tubes into the bulkhead and end former with the cradles screwed down: this sets the tail incidence."""
    zt_ = BP.JIG_TAIL_TOP - 4.0
    for k, (xa, xb) in enumerate(BP.JIG_TAIL_BLOCKS):
        hwj = 30.0
        poly = G.rect(-hwj, hwj, BZ, zt_)
        r = FP.TUBE_OD / 2 + 0.2
        cl = []
        for s in (1, -1):
            cl.append(("circle", s * FP.SOCK_Y, FP.SOCK_Z, r))
            cl.append(G.rect(s * FP.SOCK_Y - r, s * FP.SOCK_Y + r, FP.SOCK_Z, zt_ + 1.0))
        cl.append(G.rect(-22.0, 22.0, BZ + 6.0, FP.SOCK_Z - r - 6.0))
        fr = G.frame((xa, 0.0, 0.0), (0, 1, 0), (0, 0, 1))
        t = xb - xa
        name = "J4%s-BOOM-CRADLE" % "ab"[k]
        d = add(name, "Jigs_Pod", poly, t, fr, cl, [])
        d["plane_cuts"] = [("xz", [("circle", (s * 26.0, 0.0, t / 2), SCREW_R) for s in (1, -1)])]
        d["labels"] = [("J4" + "ab"[k] + (" FRONT = EF" if k == 0 else ""), 0.0, FP.SOCK_Z - r - 3.0, 2.5)]


def j5_seat_gauges():
    """J5: wing-seat gauges = the wing lower surface (+3 deg) + 1 mm foam. Sand the side tops and the capstrip until
    the gauge sits without rocking. Rails over the side tops, cross bars between them."""
    r0, r1 = 44.0, 58.0
    for k, (xa, xb) in enumerate(BP.JIG_SEAT_X):
        xs = [xa] + [x for x, _ in BP.TOP if xa < x < xb] + [xb]
        band = G.ccw([(x, POD.zt(x)) for x in xs] + [(x, POD.zt(x) + BP.JIG_SEAT_H) for x in reversed(xs)])
        fr = G.frame((0.0, r1, 0.0), (1, 0, 0), (0, 0, 1))             # XZ profile, w = 58 - Y
        name = "J5%s-SEAT-GAUGE" % "ab"[k]
        d = add(name, "Jigs_Pod", band, 2 * r1, fr, [], [])
        bars = [xa, xa + 0.5 * (xb - xa) - 3, xb]
        wins = []
        for a, b in zip(bars, bars[1:]):
            a2, b2 = a + (5.0 if a == xa else 6.0), b - 5.0
            wins.append([(a2, 0.0, r1 - r0), (b2, 0.0, r1 - r0), (b2, 0.0, r1 + r0), (a2, 0.0, r1 + r0)])
        d["plane_cuts"] = [("xz", wins)]
        xm = 0.5 * (xa + xb)
        d["labels"] = [("J5" + "ab"[k] + " SEAT", xm, POD.zt(xm) + BP.JIG_SEAT_H / 2 + 0.5, 3.5)]


# ---------------- tail jigs ----------------
def tj_tail():
    zs0, zs1 = TL.ZS0, TL.ZS1
    T = TL.T
    # TJ1: four 90-degree corner squares between the fin and the stabiliser halves (glue the stab tabs square)
    base = [(T / 2 + 2.0, zs1), (T / 2 + 25.0, zs1), (T / 2, zs1 + 25.0), (T / 2, zs1 + 2.0)]
    fr = G.frame((680.0, 0.0, 0.0), (0, 1, 0), (0, 0, 1))
    for sy, SY in ((1, "R"), (-1, "L")):
        for sz, SZ in ((1, "U"), (-1, "D")):
            pts = [(sy * u, v if sz > 0 else 2 * FP.STAB_Z - v) for u, v in base]
            poly = G.ccw(pts)
            c = ("circle", sy * (T / 2 + 7.5), (zs1 + 7.0) if sz > 0 else (zs0 - 7.0), 3.5)
            name = "TJ1-%s%s-SQUARE" % (SY, SZ)
            add(name, "Jigs_Tail", poly, 50.0, fr, [c], [("TJ1-%s%s" % (SY, SZ), sy * (T / 2 + 14.0), (zs1 + 3.0) if sz > 0 else (zs0 - 3.0), 2.2)])
    # TJ2: stabiliser level gauge standing on both booms ahead of the fin: stab underside parallel to the booms
    xa, t = 650.0, 15.0
    top = zs0
    trap = G.ccw([(-26.0, FP.SOCK_Z - 6.0), (26.0, FP.SOCK_Z - 6.0), (120.0, top - 6.0), (120.0, top), (-120.0, top), (-120.0, top - 6.0)])
    r = FP.TUBE_OD / 2 + 0.15
    cl = []
    for s in (1, -1):
        cl.append(("circle", s * FP.SOCK_Y, FP.SOCK_Z, r))
        cl.append(G.rect(s * FP.SOCK_Y - r, s * FP.SOCK_Y + r, FP.SOCK_Z - 20.0, FP.SOCK_Z))
    inner = TL.inset_convex(G.ccw([(-26.0, FP.SOCK_Z - 6.0), (26.0, FP.SOCK_Z - 6.0), (120.0, top - 6.0), (-120.0, top - 6.0)]), 6.0)
    inner = G.clean(G.clip_half(inner, 0, -1, -(FP.SOCK_Z + r + 6.0)))
    for half in TL.bands(inner, "u", [0.0], 8.0):
        u0, u1, v0, v1 = G.bbox(half)
        p0, p1 = ((u0, v1), (u1, v0)) if u0 >= 0 else ((u1, v1), (u0, v0))
        cl += TL.split_by_strip(half, p0, p1, 6.0)
    # pushrods pass through the gauge: clearance slots
    for s in (1, -1):
        p = POD.rod_at_x(s, xa + t / 2)
        cl.append(G.rect(p[1] - 4.5, p[1] + 4.5, p[2] - 6.0, p[2] + 6.0))
    fr = G.frame((xa, 0.0, 0.0), (0, 1, 0), (0, 0, 1))
    add("TJ2-STAB-LEVEL", "Jigs_Tail", trap, t, fr, cl, [("TJ2 STAB LEVEL", 0.0, top - 3.0, 3.0)])


# ---------------- wing cradles (wing frame) ----------------
WB = -16.0
CRADLE_Y = [27.5, 137.5, 247.5, 357.5, 465.0]
CRADLE_T = 12.0
SPLIT_X = 140.0


def wing_cradles():
    import wing as W
    A = W.A
    zl = lambda x: A.zl(x) - 0.1
    n = 48
    xf = [SPLIT_X * (1 - math.cos(math.pi / 2 * i / n)) for i in range(n + 1)]                 # dense at the LE
    xr = [SPLIT_X + (W.P.CHORD - SPLIT_X) * i / 32 for i in range(33)]
    front = [(-8.0, WB), (SPLIT_X, WB)] + [(x, zl(x)) for x in reversed(xf)] + [(0.0, 2.0), (-8.0, 2.0)]
    rear = [(SPLIT_X, WB), (W.P.CHORD, WB)] + [(x, zl(x)) for x in reversed(xr)]
    front, rear = G.ccw(G.clean(front)), G.ccw(G.clean(rear))
    key_c = 4.75
    i = G.find_edge(front, lambda u, v: abs(u - SPLIT_X) < 1e-6)
    P0 = front[i]
    front = G.dovetail_edge(front, i, [key_c if P0[1] < WB + 1 else (P0[1] - WB - key_c)], w_neck=5.0, w_head=8.0, depth=6.0, male=True)
    i = G.find_edge(rear, lambda u, v: abs(u - SPLIT_X) < 1e-6)
    P0 = rear[i]
    rear = G.dovetail_edge(rear, i, [key_c if P0[1] < WB + 1 else (P0[1] - WB - key_c)], w_neck=5.0, w_head=8.0, depth=6.0, male=False)
    wf = windows_under(zl, [(6.0, 38.0), (46.0, 78.0), (86.0, 128.0)], WB + 4.0)
    wr = windows_under(zl, [(152.0, 190.0), (198.0, 232.0), (240.0, 272.0)], WB + 4.0)
    holes_f = [42.0, 82.0]
    holes_r = [194.0, 236.0]
    k = 0
    for y in CRADLE_Y:
        for s, S in ((1, "R"), (-1, "L")):
            k += 1
            yc = s * y
            fr = G.frame((0.0, yc + CRADLE_T / 2, 0.0), (1, 0, 0), (0, 0, 1))       # XZ profile, w = -Y
            for part, poly, wins, hx, tag in (("F", front, wf, holes_f, "< LE"), ("R", rear, wr, holes_r, "TE >")):
                name = "WC%d%s-%s" % (CRADLE_Y.index(y) + 1, S, part)
                d = add(name, "Jigs_Wing", poly, CRADLE_T, fr, wins,
                        lbl(poly, wins, "%s %s" % (name, tag), h=3.0, prefer=(70.0 if part == "F" else 210.0, WB + 2.5)))
                d["plane_cuts"] = [("xz", [("circle", (x, 0.0, CRADLE_T / 2), SCREW_R) for x in hx])]


def all_parts():
    del PARTS[:]
    j1_wedges()
    j2_squares()
    j3_nose_blocks()
    j4_cradles()
    j5_seat_gauges()
    tj_tail()
    wing_cradles()
    return PARTS


if __name__ == "__main__":
    for p in all_parts():
        u0, u1, v0, v1 = G.bbox(p["outline"])
        dims = sorted([u1 - u0, v1 - v0, p["t"]])
        print("%-20s %-10s %6.1f x %6.1f x %6.1f  %s  cut %d  lab %s" % (p["name"], p["grp"], *dims,
              "OK" if dims[-1] <= BED and dims[1] <= BED else "TOO BIG", len(p["cutters"]), [l[0] for l in p["labels"]]))
    print(len(PARTS), "jigs")
