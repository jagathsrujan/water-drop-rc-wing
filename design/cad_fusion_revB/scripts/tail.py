"""Tail (booms, built-up cruciform tail), reservoir and electronics for the Fusion rev B model.
Numbers: fus_params (FP) section F-C, res_params (RP). Aircraft frame, mm.

Tail change for laser cutting (balsa sheet 100 x 300): the fin is one continuous 3 mm frame; the stabiliser is two
halves (rev A: one 490 mm piece through a split fin) whose root edges carry 2 tabs each that pass through 4 slots in
the fin (right tabs and left tabs alternate). The fin root has 2 tabs into slots in the PETG tail-block plate.
The elevator joiner wire lies in laser-cut slots in the elevator halves."""
import math
import geo as G
import fus_params as FP
import res_params as RP
import pod as POD

T = FP.T_SURF
ZS0, ZS1 = FP.STAB_Z - T / 2, FP.STAB_Z + T / 2
XH0, XH1 = FP.HINGE_X - 0.25, FP.HINGE_X + 0.25
XLE, XTE, HS = FP.STAB_LE_X, FP.STAB_LE_X + FP.STAB_C, FP.STAB_HS
RIBS_Y = [45.0, 90.0, 135.0, 180.0]
STAB_TABS = {+1: [685.0, 715.0], -1: [700.0, 730.0]}
FIN_ROOT_TABS = [690.0, 725.0]
PARTS = []


def add(name, grp, outline, t, fr, mat, cutters=(), labels=(), z0=0.0, **kw):
    d = dict(name=name, grp=grp, outline=outline, t=t, fr=fr, mat=mat, cutters=list(cutters), labels=list(labels), z0=z0)
    d.update(kw)
    PARTS.append(d)
    return d


def le_x(z):
    return XH0 - 0.65 * (FP.FIN_CR + (FP.FIN_CT - FP.FIN_CR) * (z - FP.FIN_ROOT_Z) / (FP.FIN_TIP_Z - FP.FIN_ROOT_Z))


def te_x(z):
    return FP.HINGE_X + 0.35 * (FP.FIN_CR + (FP.FIN_CT - FP.FIN_CR) * (z - FP.FIN_ROOT_Z) / (FP.FIN_TIP_Z - FP.FIN_ROOT_Z))


def inset_convex(poly, d):
    """Inset of a convex CCW polygon by d (intersection of the offset edge half-planes)."""
    out = list(poly)
    n = len(poly)
    for i in range(n):
        P, Q = poly[i], poly[(i + 1) % n]
        L = math.hypot(Q[0] - P[0], Q[1] - P[1])
        nx, ny = (Q[1] - P[1]) / L, -(Q[0] - P[0]) / L          # outward normal (CCW)
        out = G.clip_half(out, nx, ny, nx * P[0] + ny * P[1] - d)
        if not out:
            return []
    return G.clean(out)


def split_by_strip(poly, p0, p1, w):
    """The two parts of a convex polygon either side of a strip of width w along p0 -> p1."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    c = nx * p0[0] + ny * p0[1]
    a = G.clip_half(poly, nx, ny, c - w / 2)
    b = G.clip_half(poly, -nx, -ny, -(c + w / 2))
    return [G.clean(q) for q in (a, b) if len(q) >= 3 and abs(G.area(q)) > 4.0]


def bands(poly, axis, cuts, w):
    """Split a convex polygon by strips of width w across axis ('u' or 'v') at the given positions."""
    out = [poly]
    for c in cuts:
        nxt = []
        for q in out:
            if axis == "v":
                a = G.clip_half(q, 0, 1, c - w / 2)
                b = G.clip_half(q, 0, -1, -(c + w / 2))
            else:
                a = G.clip_half(q, 1, 0, c - w / 2)
                b = G.clip_half(q, -1, 0, -(c + w / 2))
            nxt += [G.clean(x) for x in (a, b) if len(x) >= 3 and abs(G.area(x)) > 4.0]
        out = nxt
    return out


def lbl(poly, cutters, text, h=3.5, prefer=None, min_h=2.0):
    while h >= min_h:
        p = G.label_spot(poly, cutters, text, h, prefer=prefer)
        if p:
            return [(text, p[0], p[1], h)]
        h -= 0.5
    return []


def build_tail():
    # ---- stabiliser halves (XY plates at Z 43.5 .. 46.5) ----
    fr = G.frame((0.0, 0.0, ZS0), (1, 0, 0), (0, 1, 0))
    for s, S in ((1, "R"), (-1, "L")):
        y_root = T / 2
        poly = G.rect(XLE, XH0, y_root, HS) if s > 0 else G.rect(XLE, XH0, -HS, -y_root)
        edge = 0 if s > 0 else 2
        P0 = poly[edge]
        cents = [x - P0[0] for x in STAB_TABS[s]] if s > 0 else [P0[0] - x for x in STAB_TABS[s]]
        out = G.tabs_on_edge(poly, edge, cents, 10.0, T)
        win_base = inset_convex(poly, 6.0)
        ys = [s * y for y in RIBS_Y]
        wins = bands(win_base, "v", ys, 3.0)
        cl = []
        for k, q in enumerate(sorted(wins, key=lambda q: abs(G.bbox(q)[2]))):
            u0, u1, v0, v1 = G.bbox(q)
            p0, p1 = ((u0, v0), (u1, v1)) if k % 2 == 0 else ((u1, v0), (u0, v1))
            cl += split_by_strip(q, p0, p1, 3.0)
        nm = "STAB-" + S
        add(nm, "Tail_Surfaces", out, T, fr, "balsa_med", cl, lbl(out, cl, nm, h=3.0, prefer=(XLE + 3.5, s * 120)))
    # ---- elevator halves ----
    ey0, ey1 = FP.ELEV_ROOT_Y
    jx = FP.JOINER_X
    for s, S in ((1, "R"), (-1, "L")):
        poly = G.ccw([(XH1, s * ey0), (XH1, s * HS), (XTE, s * HS), (XTE, s * ey1)])
        base = inset_convex(poly, 4.0)
        wins = bands(base, "v", [s * y for y in RIBS_Y], 3.0)
        cl = [w for w in wins if min(abs(G.bbox(w)[2]), abs(G.bbox(w)[3])) > RIBS_Y[0] - 5]   # root bay solid (joiner)
        # joiner slot: along Y at the joiner X, then the leg along X at |Y| 50
        a, b = sorted((s * (ey0 - 1.0), s * (FP.JOINER_HY + 0.8)))
        cl.append(G.rect(jx - 0.8, jx + 0.8, a, b))
        a, b = sorted((s * (FP.JOINER_HY - 0.8), s * (FP.JOINER_HY + 0.8)))
        cl.append(G.rect(jx - 0.8, jx + FP.JOINER_LEG + 0.5, a, b))
        nm = "ELEV-" + S
        add(nm, "Tail_Surfaces", poly, T, fr, "balsa_light", cl, lbl(poly, cl, nm, h=3.0, prefer=(XTE - 12, s * 30)))
    # ---- fin (XZ plate, Y -1.5 .. 1.5) ----
    frf = G.frame((0.0, T / 2, 0.0), (1, 0, 0), (0, 0, 1))         # w = -Y
    z0, z1 = FP.FIN_ROOT_Z, FP.FIN_TIP_Z
    fin = G.ccw([(le_x(z0), z0), (XH0, z0), (XH0, z1), (le_x(z1), z1)])
    i = G.find_edge(fin, lambda u, v: abs(v - z0) < 1e-6)
    P0 = fin[i]
    fin = G.tabs_on_edge(fin, i, [x - P0[0] for x in FIN_ROOT_TABS], 10.0, FP.TB_PLATE_T)
    cl = [G.rect(x - 5.0, x + 5.0, ZS0, ZS1) for x in STAB_TABS[1] + STAB_TABS[-1]]
    base = inset_convex(G.ccw([(le_x(z0), z0), (XH0, z0), (XH0, z1), (le_x(z1), z1)]), 6.0)
    lower = G.clip_half(base, 0, 1, ZS0 - 6.0)
    upper = G.clip_half(base, 0, -1, -(ZS1 + 6.0))
    for q in (lower, upper):
        q = G.clean(q)
        if len(q) >= 3:
            u0, u1, v0, v1 = G.bbox(q)
            cl += split_by_strip(q, (u1, v0), (u0 + 3, v1), 3.0)
    add("FIN", "Tail_Surfaces", fin, T, frf, "balsa_med", cl, lbl(fin, cl, "FIN  UP ^", h=3.0, prefer=(XH0 - 25, ZS1 + 6)))
    # ---- rudder ----
    zr0 = FP.RUD_Z0
    rud = G.ccw([(XH1, zr0), (te_x(zr0), zr0), (te_x(z1), z1), (XH1, z1)])
    base = inset_convex(rud, 4.0)
    wins = bands(base, "v", [10.0, FP.STAB_Z, 90.0], 3.0)
    cl = [w for w in wins if G.bbox(w)[2] > 5.0]          # bottom bay solid (label, horn side)
    cl.append(("circle", jx, FP.STAB_Z, FP.RUD_NOTCH_D / 2))
    cl.append(G.rect(XH1 - 1.0, jx, FP.STAB_Z - FP.RUD_NOTCH_D / 2, FP.STAB_Z + FP.RUD_NOTCH_D / 2))
    add("RUDDER", "Tail_Surfaces", rud, T, frf, "balsa_light", cl, lbl(rud, cl, "RUDDER", h=3.0, prefer=(XH1 + 18, -10)))
    # ---- PETG tail block: plate with the fin root slots + fin socket walls; tube collars and webs ----
    tz = FP.TB_TOP_Z
    frp = G.frame((0.0, 0.0, tz - FP.TB_PLATE_T), (1, 0, 0), (0, 1, 0))
    plate = G.rect(FP.TB_X[0], FP.TB_X[1], -FP.SOCK_Y, FP.SOCK_Y)
    cl = [G.rect(x - 5.0, x + 5.0, -T / 2, T / 2) for x in FIN_ROOT_TABS]
    d = add("TAILBLOCK", "Tail_Block", plate, FP.TB_PLATE_T, frp, "petg", cl, [])
    walls = []
    for sy in (1, -1):
        a, b = sorted((sy * (T / 2 + 0.1), sy * (T / 2 + 0.1 + FP.TB_SOCKET_WALL)))
        walls.append(G.rect(FP.TB_X[0], FP.TB_X[1], a, b))
    d["joins"] = [(walls, FP.TB_PLATE_T, FP.TB_PLATE_T + FP.TB_SOCKET_H)]
    cx0, cx1 = FP.TB_COLLAR_X
    for s, S in ((1, "R"), (-1, "L")):
        y = s * FP.SOCK_Y
        frw = G.frame((0.0, y + 0.6, 0.0), (1, 0, 0), (0, 0, 1))
        add("TB-WEB-" + S, "Tail_Block", G.rect(cx0, cx1, FP.SOCK_Z + FP.TUBE_OD / 2 + 0.15 + FP.TB_COLLAR_WALL, tz - FP.TB_PLATE_T), 1.2, frw, "petg")
    # ---- horns (1.5 mm G10 / ply) ----
    hx, hy, hz = FP.ELEV_HORN_PT
    frh = G.frame((0.0, hy + FP.HORN_T / 2, 0.0), (1, 0, 0), (0, 0, 1))
    eh = G.ccw([(XH1 + 2.0, ZS0), (XH1 + 14, ZS0), (hx + 3.0, hz - 2.5), (hx - 2.0, hz - 2.5)])
    add("HORN-E", "Tail_Hardware", eh, FP.HORN_T, frh, "ply", [("circle", hx, hz, FP.HORN_HOLE / 2)], [])
    rx, ry, rz = FP.RUD_HORN_PT
    frr = G.frame((0.0, 0.0, rz - FP.HORN_T / 2), (1, 0, 0), (0, 1, 0))
    rh = G.ccw([(XH1 + 2.0, T / 2), (XH1 + 14, T / 2), (rx + 3.0, ry + 2.5), (rx - 2.0, ry + 2.5)])
    add("HORN-R", "Tail_Hardware", rh, FP.HORN_T, frr, "ply", [("circle", rx, ry, FP.HORN_HOLE / 2)], [])
    # ---- tubes, collars, pushrods, joiner (round parts) ----
    rounds = []
    for s, S in ((1, "R"), (-1, "L")):
        y = s * FP.SOCK_Y
        rounds.append(("BOOM-" + S, (FP.TUBE_X[0], y, FP.SOCK_Z), (FP.TUBE_X[1], y, FP.SOCK_Z), FP.TUBE_OD / 2, FP.TUBE_ID / 2, "carbon", "Tail_Booms"))
        rc = FP.TUBE_OD / 2 + 0.15
        rounds.append(("TB-COLLAR-" + S, (cx0, y, FP.SOCK_Z), (cx1 + 1.0, y, FP.SOCK_Z), rc + FP.TB_COLLAR_WALL, rc, "petg", "Tail_Block"))
    # pushrods, servo arms and Z-bends: linkage.py
    jr = FP.JOINER_D / 2
    jy, zj = FP.JOINER_HY, FP.STAB_Z
    rounds.append(("JOINER", (jx, -jy, zj), (jx, jy, zj), jr, 0.0, "steel", "Tail_Hardware"))
    for s, S in ((1, "R"), (-1, "L")):
        rounds.append(("JOINER-LEG-" + S, (jx + jr, s * jy, zj), (jx + FP.JOINER_LEG, s * jy, zj), jr, 0.0, "steel", "Tail_Hardware"))
    return rounds


# ---------------- reservoir (bought bottle + printed outlet; simplified) ----------------
def reservoir():
    bx = FP.BOTTLE_BASE_X
    prof = RP.BOTTLE_PROFILE
    outer = [(0.0, 0.0)] + [(float(a), float(r)) for a, r in prof]
    w = RP.WALL
    inner = [(float(a), float(r) - w) for a, r in reversed(prof)]
    inner[-1] = (w, inner[-1][1])
    bottle = outer + inner + [(w, 0.0)]
    items = [("revolve", "BOTTLE", G.ccw(G.clean(bottle)), G.frame((bx, 0.0, RP.AXIS_Z), (1, 0, 0), (0, 0, 1)), "pet")]
    items.append(("tube", "BOTTLE-CAP", (bx + RP.CAP_Y0, 0, RP.AXIS_Z), (bx + RP.CAP_Y1, 0, RP.AXIS_Z), RP.CAP_D / 2, prof[-1][1] + 0.05, "petg"))
    # outlet: base plate + flap at X 80 (vertical axis), fill unit on the top at X -11
    xo = RP.OUT_X
    items.append(("tube", "OUTLET-PLATE", (xo, 0, -107.0), (xo, 0, RP.AXIS_Z - RP.R_CYL - 0.2), RP.PL_BODY_D / 2, RP.PL_HOLE_D / 2, "petg"))
    items.append(("tube", "FLAP", (xo, 0, RP.FLAP_ZBOT), (xo, 0, RP.FLAP_ZTOP), RP.FLAP_D / 2, 0.0, "petg"))
    xf = RP.FILL_X_C
    items.append(("tube", "FILL-UNIT", (xf, 0, RP.AXIS_Z + RP.R_CYL + 0.1), (xf, 0, RP.F_CAP_Z1), RP.F_CAP_D / 2, 0.0, "petg"))
    return items


# ---------------- electronics placeholders ----------------
def electronics(servo_rel):
    yc, zc = FP.MOTOR_C
    fw0 = POD.BP.FIREWALL_X[0]
    items = [("tube", "MOTOR", (fw0, yc, zc), (fw0 - FP.MOTOR_L, yc, zc), FP.MOTOR_D / 2, 0.0),
             ("tube", "COLLET", (fw0 - FP.MOTOR_L, yc, zc), (fw0 - FP.MOTOR_L - FP.COLLET[1], yc, zc), FP.COLLET[0] / 2, 0.0),
             ("tube", "PROP-DISC", (FP.PROP_X + 0.5, yc, zc), (FP.PROP_X - 0.5, yc, zc), FP.PROP_D / 2, FP.COLLET[0] / 2)]
    L, Wd, H = FP.BATT
    items.append(("box", "BATTERY", (FP.BATT_XC - L / 2, FP.BATT_XC + L / 2, -Wd / 2, Wd / 2, FP.TRAY_Z, FP.TRAY_Z + H)))
    l, w, h = FP.ESC
    tz = FP.TRAY_Z - POD.BP.TRAY_T
    items.append(("box", "ESC", (FP.ESC_X0, FP.ESC_X0 + l, -w / 2, w / 2, tz - h, tz)))
    rx = FP.RX
    items.append(("box", "RECEIVER", (POD.BP.RX_X0, POD.BP.RX_X0 + rx[0], -rx[1] / 2, rx[1] / 2, FP.FLOOR_Z, FP.FLOOR_Z + rx[2])))
    L, W, H, TL = FP.TSERVO
    for s, S in ((1, "R"), (-1, "L")):
        yc_ = s * FP.TSERVO_YC
        items.append(("box", "TSERVO-" + S, (FP.TSERVO_XC - L / 2, FP.TSERVO_XC + L / 2, yc_ - W / 2, yc_ + W / 2, FP.TSERVO_ZB, FP.TSERVO_ZB + H)))
        for j, (xa_, xb_) in enumerate(((FP.TSERVO_XC - TL / 2, FP.TSERVO_XC - L / 2), (FP.TSERVO_XC + L / 2, FP.TSERVO_XC + TL / 2))):
            items.append(("box", "TSERVO-TAB%d-%s" % (j + 1, S), (xa_, xb_, yc_ - W / 2, yc_ + W / 2, POD.TST_Z[1], POD.TST_Z[1] + 2.5)))
    c = servo_rel["case"]
    t = servo_rel["tabs"]
    items.append(("box", "RELEASE-SERVO", c))
    items.append(("box", "RELEASE-SERVO-TAB1", (t[0], c[0], c[2], c[3], t[2], t[3])))
    items.append(("box", "RELEASE-SERVO-TAB2", (c[1], t[1], c[2], c[3], t[2], t[3])))
    return items


def all_parts():
    del PARTS[:]
    rounds = build_tail()
    return PARTS, rounds
