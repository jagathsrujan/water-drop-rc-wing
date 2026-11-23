"""Stage F-B: functional features of the pod (stageB_brief.md). exec() inside FreeCAD after build_stageA.py
(uses B.LAST_POD from stage A). No structural ribs, grids, windows or wall-thickness changes (structure session F-S)."""
import sys, os, math
SCRIPTS = globals().get("FUS_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad_fuselage", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import fus_params as P
import fus_build as B
import FreeCAD as App
import Part

V = App.Vector
d = B.doc()
R = B.LAST_POD
OML, INNER = R["oml"], R["inner"]
box = B.box
B.group("Feat")
B.group("Placeholder")


def ok(name, s):
    if s.isNull() or not s.isValid():
        raise RuntimeError(name + ": invalid shape")
    bb = s.BoundBox
    print("%-22s V %9.1f mm3  X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f  solids %d" % (
        name, s.Volume, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax, len(s.Solids)))
    return s


def cyl_x(y, z, r, x0, x1):
    return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))


def cyl_y(x, z, r, y0, y1):
    return Part.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))


def cyl_z(x, y, r, z0, z1):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0), V(0, 0, 1))


def slice_face(shape, x):
    ws = shape.slice(V(1, 0, 0), x)
    ws = sorted(ws, key=lambda w: -Part.Face(w).Area)
    return Part.Face(ws[0])


def ruled_cutter(stations):
    """Loft of rectangles (YZ plane): [(x, half_width)] -> solid |Y| < hw(x), Z -200..100."""
    ws = []
    for x, hw in stations:
        pts = [V(x, -hw, -200), V(x, hw, -200), V(x, hw, 100), V(x, -hw, 100), V(x, -hw, -200)]
        ws.append(Part.makePolygon(pts))
    return Part.makeLoft(ws, True, True)


def w_outer(x):
    if x < P.NOSE_END_X:
        return B.nose_sec(x)["W"]
    if x <= P.AFT_X0:
        return P.CENTRE_W
    return B.side_sec(x)[0]


hatch_reg = B.hatch_region()
parts = {n: d.getObject(n).Shape.copy() for n in ("F1_PodNose", "F2_PodCentre", "F3_PodAft", "F4_NoseHatch")}
add = {"F1_PodNose": [], "F2_PodCentre": [], "F3_PodAft": [], "F4_NoseHatch": []}
cut = {"F1_PodNose": [], "F2_PodCentre": [], "F3_PodAft": [], "F4_NoseHatch": []}

# ---------------- hatch ledge (item 7) ----------------
band = hatch_reg.translated(V(0, 0, -P.LEDGE_T)).cut(hatch_reg)
ledge_cut = ruled_cutter([(x, w_outer(x) - B.t_side(x) - P.LEDGE_W) for x in B.frange(P.HATCH_X[0] - 1, P.HATCH_X[1] + 1, 7.0)])
ledge = ok("ledge", band.common(OML).cut(ledge_cut))
# magnets: pads under the ledge (pocket from the top) and bosses in the hatch (pocket from below)
mag_pads, mag_hboss, mag_pock_l, mag_pock_h = [], [], [], []
OML_IN05 = OML.translated(V(0, 0, -0.5))          # hatch boss tops 0.5 mm under the outer top surface
MAG_WALL = 0.6                                    # min wall outside a magnet pocket (T2; was 0 -> the X -20 pockets cut the skin)
for x in P.MAGNET_X:
    zt = B.top_line(x)
    zb = zt - P.HATCH_DEPTH                       # hatch joint line at x (the nose top line slopes about 15 deg at X -150)
    slope = 0.5 * (B.top_line(x + 1.0) - B.top_line(x - 1.0))
    nrm = V(-slope, 0, 1)
    nrm.normalize()                               # magnet axis normal to the sloped joint face (T2)
    y_out = OML.common(Part.makeLine(V(x, 0, zb), V(x, 150, zb))).Length    # local outer half-width at the joint line
    yc = y_out - B.t_side(x) - P.MAGNET_D / 2 - 0.1 - MAG_WALL
    rp = P.MAGNET_D / 2 + 0.1
    hp = P.MAGNET_H + 0.1
    # the nose top corner is rounded (Rt about 9 mm): move the magnet inboard until the hatch pocket stays
    # >= 0.5 mm under the outer surface (T2)
    while yc > 10.0:
        c_try = V(x, yc, zb)
        if Part.makeCylinder(rp, hp, c_try, nrm).cut(OML_IN05).Volume < 0.01:
            break
        yc -= 0.5
    print("magnet X %.0f: joint Z %.2f slope %.3f, outer |Y| %.2f, magnet |Y| %.2f" % (x, zb, slope, y_out, yc))
    for s in (1, -1):
        y = s * yc
        c0 = V(x, y, zb)
        bracket = box(x - 3.0, x + 3.0, *sorted((y, s * (y_out + 1.0))), zb - 4.0, zb + 3.0)   # pad -> side wall
        mag_pads.append(cyl_z(x, y, 4.5, zb - 4.0, zb + 3.0).fuse(bracket).cut(hatch_reg).common(OML))
        mag_pock_l.append(Part.makeCylinder(rp, hp + 0.3, c0 - nrm * hp, nrm))
        mag_hboss.append(cyl_z(x, y, 4.5, zb - 3.0, zt + 1.0).common(hatch_reg).common(OML_IN05))
        mag_pock_h.append(Part.makeCylinder(rp, hp + 0.3, c0 - nrm * 0.3, nrm))
        for nm_, pk in (("F1 pocket", mag_pock_l[-1]), ("hatch pocket", mag_pock_h[-1])):
            v_out = pk.cut(OML_IN05 if nm_ == "hatch pocket" else OML).Volume
            if v_out > 0.01:
                print("WARNING magnet X %.0f %s: %.3f mm3 outside the skin" % (x, nm_, v_out))
ledge_all = ok("ledge+pads", B.fuse_all([ledge] + mag_pads).removeSplitter())
for n, bx in B.split_boxes().items():
    piece = ledge_all.common(bx)
    if piece.Volume > 1:
        add[n].append(piece)
        cut[n].extend(mag_pock_l)
add["F4_NoseHatch"].extend(mag_hboss)
cut["F4_NoseHatch"].extend(mag_pock_h)
# blister over the fill unit (item 2): +1 mm outside, pocket inside
x0, x1, hw, hb = P.BLISTER
add["F4_NoseHatch"].append(box(x0, x1, -hw, hw, P.HATCH_TOP_Z - 0.05, P.HATCH_TOP_Z + hb))
cut["F4_NoseHatch"].append(box(x0 + 0.8, x1 + 0.5, -hw + 0.8, hw - 0.8, P.HATCH_TOP_Z - P.T_HATCH_TOP - 0.01, P.HATCH_TOP_Z + hb - 0.8))

# ---------------- front stop plate F6 (items 1, 4) and joint sleeves ----------------
sx0, sx1 = P.STOP_X
plate = slice_face(INNER, sx0 + 0.01).extrude(V(sx1 - sx0 - 0.02, 0, 0))
plate = plate.cut(cyl_x(0, -60, P.STOP_HOLE_D / 2, sx0 - 1, sx1 + 1)).cut(hatch_reg).cut(ledge_all)
F6 = ok("F6_FrontStop", plate.removeSplitter())


def u_sleeve(xa, xb, w_in, z_top):
    t = P.SLEEVE_T
    zf = P.BELLY_Z + P.T_FLOOR
    sides = [box(xa, xb, s0, s1, -111.0, z_top) for s0, s1 in ((w_in - t, w_in + 0.4), (-w_in - 0.4, -w_in + t))]
    floor = box(xa, xb, -(w_in - 6.0), w_in - 6.0, zf - 0.4, zf + t)
    return B.fuse_all(sides + [floor]).common(OML)


add["F1_PodNose"].append(u_sleeve(sx0 - P.SLEEVE_L, sx0, P.CENTRE_W - P.T_NOSE, B.top_line(sx0) - P.HATCH_DEPTH - P.LEDGE_T - 0.2))
add["F2_PodCentre"].append(u_sleeve(sx1, sx1 + P.SLEEVE_L, P.CENTRE_W - P.T_SIDE, B.top_line(sx1) - P.HATCH_DEPTH - P.LEDGE_T - 0.2))
xs = P.SPLIT_X[1]
add["F2_PodCentre"].append(u_sleeve(xs, xs + P.SLEEVE_L, P.CENTRE_W - P.T_SIDE, B.seat_z(xs + P.SLEEVE_L) - P.LIP_T - 0.3))

# ---------------- firewall F7 and frame ring (item 5) ----------------
fx = P.FIREWALL_X
fw = slice_face(OML, fx + 0.01).extrude(V(-P.FW_T, 0, 0))
yc, zc = P.MOTOR_C
holes = [cyl_x(yc, zc, 5.0, fx - 5, fx + 1)]
r16, r19 = P.XMOUNT[0] / 2, P.XMOUNT[1] / 2
for dy, dz in ((r16, 0), (-r16, 0), (0, r19), (0, -r19)):
    holes.append(cyl_x(yc + dy, zc + dz, 1.6, fx - 5, fx + 1))
for y, z in P.FW_COOL:
    holes.append(cyl_x(y, z, 6.0, fx - 5, fx + 1))
F7 = ok("F7_Firewall", fw.cut(B.fuse_all(holes)))
fo = slice_face(OML, fx + 0.01)
ring = fo.cut(fo.makeOffset2D(-(P.T_NOSE + P.FW_RING_W))).extrude(V(P.FW_RING_L, 0, 0))
add["F1_PodNose"].append(ok("fw_ring", ring.cut(B.fuse_all(holes))))

# ---------------- battery tray (item 6) ----------------
tx0, tx1 = P.TRAY_X
tray = box(tx0, tx1, -P.TRAY_HW, P.TRAY_HW, P.TRAY_Z - P.TRAY_T, P.TRAY_Z)
posts = [box(x - 1.0, x + 1.0, s * 16 - 1.0, s * 16 + 1.0, -130, P.TRAY_Z - P.TRAY_T + 0.01) for x in (-140, -100, -60) for s in (1, -1)]
tray_all = B.fuse_all([tray] + posts).common(OML)
slots = [box(x - 1.25, x + 1.25, -11, 11, P.TRAY_Z - 5, P.TRAY_Z + 1) for x in (-112.0, -80.0)]
add["F1_PodNose"].append(ok("battery_tray", tray_all.cut(B.fuse_all(slots))))

# ---------------- front band stubs (item 8) and rear dowel (item 9) ----------------
stubs = []
for s in (1, -1):
    wi = P.CENTRE_W - P.T_SIDE
    boss = cyl_y(P.STUB_X, P.STUB_Z, P.STUB_BOSS_D / 2, wi - P.STUB_IN, wi + 0.2) if s > 0 else \
        cyl_y(P.STUB_X, P.STUB_Z, P.STUB_BOSS_D / 2, -wi - 0.2, -wi + P.STUB_IN)
    rib = box(P.STUB_X - 0.6, P.STUB_X + 0.6, *(sorted((s * (wi - P.STUB_IN), s * (wi + 0.2)))), -50.0, P.STUB_Z)
    add["F2_PodCentre"].append(boss.fuse(rib))
    y0, y1 = sorted((s * (wi - P.STUB_IN), s * (P.CENTRE_W + P.STUB_OUT)))
    stubs.append(cyl_y(P.STUB_X, P.STUB_Z, P.STUB_D / 2, y0, y1))
    cut["F2_PodCentre"].append(cyl_y(P.STUB_X, P.STUB_Z, P.STUB_D / 2 + 0.1, y0 - 0.1, y1))
STUBS = ok("F9_BandStubs", B.fuse_all(stubs))
wd = w_outer(P.DOWEL_X)
dowel = cyl_y(P.DOWEL_X, P.DOWEL_Z, P.DOWEL_D / 2, -wd - 8, wd + 8)
for s in (1, -1):
    yb = sorted((s * (wd - 0.5 - 4), s * (wd - 0.2)))
    add["F3_PodAft"].append(cyl_y(P.DOWEL_X, P.DOWEL_Z, 4.5, *yb).common(OML))
cut["F3_PodAft"].append(cyl_y(P.DOWEL_X, P.DOWEL_Z, P.DOWEL_D / 2 + 0.1, -wd - 9, wd + 9))
F8 = ok("F8_RearDowel", dowel)

# ---------------- wing seat lip (item 10) ----------------
xs_l = B.frange(P.SEAT_X[0], P.OPEN_X[1], 4.0)
top = [V(x, 0, B.seat_z(x)) for x in xs_l]
bot = [V(x, 0, B.seat_z(x) - P.LIP_T) for x in reversed(xs_l)]
lf = Part.Face(Part.makePolygon(top + bot + [top[0]]))
lip_band = lf.extrude(V(0, 120, 0)).translated(V(0, -60, 0))
lip_cut = ruled_cutter([(x, w_outer(x) - P.T_SIDE - P.LIP_W) for x in B.frange(P.SEAT_X[0] - 1, P.OPEN_X[1] + 1, 6.0)])
lip = ok("seat_lip", lip_band.common(OML).cut(lip_cut))
for n, bx in B.split_boxes().items():
    piece = lip.common(bx)
    if piece.Volume > 1:
        add[n].append(piece)

# ---------------- saddles in the floor + strap bridges (item 11) ----------------
zf_top = P.BELLY_Z + P.T_FLOOR
for nm, (sa, sb) in (("RefRes_P12a_Saddle1", P.SADDLE1_X), ("RefRes_P12b_Saddle2", P.SADDLE2_X)):
    sad = d.getObject(nm).Shape.copy()
    bb = sad.BoundBox
    pad = box(bb.XMin, bb.XMax, bb.YMin, bb.YMax, zf_top - 0.05, P.FLOOR_Z + 0.05).common(OML)
    add["F2_PodCentre"].extend([sad, pad])
    xc = 0.5 * (sa + sb)
    for s in (1, -1):
        y0, y1 = sorted((s * 44.0, s * 48.0))
        bridge = box(xc - 12.0, xc + 12.0, y0, y1, zf_top - 0.05, P.FLOOR_Z + 3.0)
        slot = box(xc - 11.0, xc + 11.0, y0 - 1, y1 + 1, zf_top - 0.1, P.FLOOR_Z + 2.0)
        add["F2_PodCentre"].append(bridge.cut(slot))

# ---------------- flap stop: local lip on the aft edge of the belly opening (user, 2026-11-23) ----------------
# The open flap hits the belly skin at about 157 deg (no stop in the reservoir). The 0.8 mm floor edge aft of the opening
# is the flap stop; the lip makes it 1.2 mm over the flap width + margin.
lx, lhw, lt = P.FLAP_STOP_LIP
hx1 = P.FLOOR_HOLE_RECT[1]
zf_in = P.BELLY_Z + P.T_FLOOR
add["F2_PodCentre"].append(box(hx1, hx1 + lx, -lhw, lhw, zf_in - 0.05, zf_in + lt))

# ---------------- release-servo pocket (item 12) and servo mount ----------------
(px0, px1), (pz0, pz1) = P.POCKET_X, P.POCKET_Z
w = P.POCKET_WALL
pocket_out = box(px0 - w, px1 + w, 52.5, P.POCKET_YIN + w, pz0 - w, pz1 + w)
cavity = box(px0, px1, 50.0, P.POCKET_YIN, pz0, pz1)
add["F2_PodCentre"].append(pocket_out)
servo = d.getObject("RefRes_P14_Servo_MG90S").Shape
sb = servo.BoundBox
case_x = (P.SERVO_X_SHAFT - 12.0, P.SERVO_X_SHAFT + 12.0)
# tab bands 4.0 mm at each end (the MG90S tabs are 4.5 mm long; a 4.9 mm band also takes the case and gave the
# case top Z -80.4 instead of the tab level)
TAB_W = 4.0
tabs = servo.common(box(sb.XMin - 1, sb.XMax + 1, sb.YMin - 1, sb.YMax + 1, sb.ZMin - 1, sb.ZMax + 1)
                    .cut(box(sb.XMin + TAB_W, sb.XMax - TAB_W, sb.YMin - 2, sb.YMax + 2, sb.ZMin - 2, sb.ZMax + 2)))
tb = B.mesh_bb(tabs) if tabs.Volume > 0.1 else None          # (x0, x1, y0, y1, z0, z1)
mount = []
if tb is not None:
    tz0 = tb[4]
    if tb[5] - tz0 > 5.0:
        raise RuntimeError("servo tab detection: Z range %.2f .. %.2f is not a tab" % (tz0, tb[5]))
    # shelf UNDER each tab (T2): the servo drops in from the top and rests on its tabs, M2 screws from above;
    # gusset above the shelf beside the tab (Y > case), clear of the D-059 pocket wall below
    for xa, xb in ((sb.XMin - 0.5, sb.XMin + 4.5), (sb.XMax - 4.5, sb.XMax + 0.5)):
        shelf = box(xa, xb, sb.YMin, P.CENTRE_W - 0.2, tz0 - 3.0, tz0)
        gus = box(0.5 * (xa + xb) - 0.6, 0.5 * (xa + xb) + 0.6, sb.YMax + 0.5, P.CENTRE_W - 0.2, tz0, tz0 + 12.0)
        mount.append(shelf.fuse(gus).cut(cyl_z(0.5 * (xa + xb), 0.5 * (sb.YMin + sb.YMax), 0.8, tz0 - 4.0, tz0 + 1.0)))
    print("servo tabs Z %.2f .. %.2f, shelves Z %.2f .. %.2f, case Y %.2f .. %.2f" % (tz0, tb[5], tz0 - 3.0, tz0, sb.YMin, sb.YMax))
add["F2_PodCentre"].extend(mount)
cut["F2_PodCentre"].append(cavity)

# ---------------- safety-pin flag hole (item 13) ----------------
fx_, fz_ = P.SAF_PIN_POS
flag_cut = [cyl_y(fx_, fz_, P.FLAG_HOLE_D / 2, -60, -50)]
fb = d.getObject("RefRes_P10_Flag").Shape.BoundBox
if fb.YMin < -50:
    flag_cut.append(box(fb.XMin - 1, fb.XMax + 1, -60, -50, fb.ZMin - 1, fb.ZMax + 1))
cut["F2_PodCentre"].extend(flag_cut)

# ---------------- tail servo posts, receiver (item 15) ----------------
L, W_, H, TL = P.TSERVO
ph = {}
for s, nm in ((1, "R"), (-1, "L")):
    yc = s * P.TSERVO_YC
    case = box(P.TSERVO_XC - L / 2, P.TSERVO_XC + L / 2, yc - W_ / 2, yc + W_ / 2, P.TSERVO_ZB, P.TSERVO_ZB + H)
    tab = box(P.TSERVO_XC - TL / 2, P.TSERVO_XC + TL / 2, yc - W_ / 2, yc + W_ / 2, P.TSERVO_ZB + 20.0, P.TSERVO_ZB + 22.5)
    ph["PH_TailServo_" + nm] = case.fuse(tab)
    for xa in (P.TSERVO_XC - TL / 2, P.TSERVO_XC + L / 2):     # tab shelves cantilevered from the side wall (T2: light)
        xm = xa + (TL - L) / 4
        y_in, y_out = (yc - W_ / 2, 70.0) if s > 0 else (-70.0, yc + W_ / 2)
        shelf = box(xa, xa + (TL - L) / 2, y_in, y_out, P.TSERVO_ZB + 17.5, P.TSERVO_ZB + 20.0)
        y_g0, y_g1 = (yc + W_ / 2 + 0.5, 70.0) if s > 0 else (-70.0, yc - W_ / 2 - 0.5)
        gus = box(xm - 0.6, xm + 0.6, y_g0, y_g1, P.TSERVO_ZB + 6.0, P.TSERVO_ZB + 20.0)
        add["F3_PodAft"].append(shelf.fuse(gus).common(OML).cut(cyl_z(xm, yc, 0.8, P.TSERVO_ZB + 10, P.TSERVO_ZB + 21)))
ph["PH_Receiver"] = box(P.RX_X0, P.RX_X0 + P.RX[0], -P.RX[1] / 2, P.RX[1] / 2, P.RX_ZB, P.RX_ZB + P.RX[2])

# ---------------- boom socket block (item 16) ----------------
rb = P.SOCK_BORE / 2
ro = rb + P.SOCK_WALL
xa, xb = P.SOCK_X0, P.SOCK_X0 + P.SOCK_WALL + P.SOCK_DEPTH
blk = [cyl_x(s * P.SOCK_Y, P.SOCK_Z, ro, xa, xb) for s in (1, -1)]
xbh = xa + 6.0                                   # bulkhead frame (T2: replaces a full-width web plate, -7 cm3)
fo2 = slice_face(OML, xbh)
bh_ring = fo2.cut(fo2.makeOffset2D(-(P.T_SIDE + 5.0))).extrude(V(1.6, 0, 0)).common(OML)
bar = box(xbh, xbh + 1.6, -60, 60, P.SOCK_Z - 4.0, P.SOCK_Z + 4.0).common(OML)
block = B.fuse_all(blk + [bh_ring, bar])
bores = [cyl_x(s * P.SOCK_Y, P.SOCK_Z, rb, xa + P.SOCK_WALL, xb + 1) for s in (1, -1)]
add["F3_PodAft"].append(block)
cut["F3_PodAft"].extend(bores)
cut["F3_PodAft"].extend(cyl_x(y, z, 1.5, P.POD_END_X - 5, P.POD_END_X + 2) for y, z in P.PUSHROD_EXIT)

# ---------------- skids F5 (item 14) ----------------
skids = []
for xa_, xb_ in P.SKID_X:
    layer = OML.translated(V(0, 0, -P.SKID_T)).cut(OML)
    skids.append(layer.common(box(xa_, xb_, -P.SKID_HW, P.SKID_HW, -200, -50)))

# ---------------- assemble ----------------
for n in parts:
    s = parts[n]
    for i, pc in enumerate(add[n]):
        if pc.isNull() or pc.Volume < 1e-6:
            continue
        t = s.fuse(pc)
        if not t.isValid():
            t2 = s.fuse(pc.removeSplitter()).removeSplitter()
            if not t2.isValid():
                bb = pc.BoundBox
                raise RuntimeError("%s add #%d invalid fuse (piece X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f valid %s)" % (
                    n, i, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax, pc.isValid()))
            t = t2
        s = t
    if cut[n]:
        s = s.cut(B.fuse_all(cut[n]))
    s = s.removeSplitter()
    if len(s.Solids) > 1:
        big = max(s.Solids, key=lambda q: q.Volume)
        print("WARNING %s: %d solids, keeping all (largest %.0f mm3)" % (n, len(s.Solids), big.Volume))
    parts[n] = ok(n, s)

for n, s in parts.items():
    o = d.getObject(n)
    o.Shape = s
objs = [("F5a_SkidFront", skids[0], P.COL_PETG, "PETG skid, replaceable"),
        ("F5b_SkidAft", skids[1], P.COL_PETG, "PETG skid, replaceable"),
        ("F6_FrontStop", F6, P.COL_BALSA, "3 mm balsa front stop = F1/F2 joint former"),
        ("F7_Firewall", F7, P.COL_PLY, "3 mm ply firewall"),
        ("F8_RearDowel", F8, P.COL_PLY, "D5 rear band dowel (birch or carbon)"),
        ("F9_BandStubs", STUBS, P.COL_CARBON, "D4 carbon front band stubs (D-053)")]
for n, s, c, note in objs:
    ok(n, s)
    B.put(n, s, "Feat", c, 0, props=dict(Note=note))
for n, s in ph.items():
    B.put(n, s, "Placeholder", P.COL_PH, 0, props=dict(Note="placeholder (bought part), not printed"))
B.put("PH_Battery", box(P.BATT_XC - P.BATT[0] / 2, P.BATT_XC + P.BATT[0] / 2, -P.BATT[1] / 2, P.BATT[1] / 2, P.TRAY_Z, P.TRAY_Z + P.BATT[2]),
      "Placeholder", (0.2, 0.5, 0.2), 0, props=dict(Note="3S 1000 mAh placeholder; slide X %.0f .. %.0f" % P.BATT_XC_RANGE))
B.put("PH_ESC", box(-80.0, -80.0 + P.ESC[0], -P.ESC[1] / 2, P.ESC[1] / 2, P.TRAY_Z - P.TRAY_T - 2 - P.ESC[2], P.TRAY_Z - P.TRAY_T - 2),
      "Placeholder", (0.2, 0.2, 0.6), 0, props=dict(Note="ESC 30 A placeholder under the tray"))
d.recompute()
print("stage F-B build done")
