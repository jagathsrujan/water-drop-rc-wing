"""Fuselage rev B (balsa pod), version 2 - designed for balsa construction. exec() inside FreeCAD (GUI):
    BAL_SCRIPTS = "<project>/design/cad_fuselage_balsa/scripts"; exec(open(BAL_SCRIPTS + "/build_balsa.py").read())
Reads Fuselage_revA.FCStd (opened if needed, never saved) for the reference bodies: reservoir (RefRes_*), wing rev A
(W_* -> one compound), tail F10..F19, rear dowel F8, band stubs F9 and the electronics placeholders.
Panels are flat: each is the common of a side-profile prism (XZ) and a plan prism (XY), straight between the kinks,
and every kink sits on a former (front stop, bulkhead)."""
import os, sys, math
SCRIPTS = globals().get("BAL_SCRIPTS") or os.path.dirname(os.path.abspath(__file__))
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import importlib
import bal_params as BP
importlib.reload(BP)
FP = BP.FP
import FreeCAD as App
import Part

V = App.Vector
XLO, XHI = -400.0, 600.0

# ---------------- documents ----------------
src = App.listDocuments().get(BP.REVA_DOC) or App.openDocument(BP.REVA_FCSTD)
if src.getObject("F10_Tubes") is None:
    raise RuntimeError("Fuselage_revA is not fully loaded: close it and reopen it from disk")
d = App.listDocuments().get(BP.DOC)
if d is None:
    d = App.newDocument(BP.DOC)
for o in list(d.Objects):
    try:
        d.removeObject(o.Name)
    except Exception:
        pass


def group(name):
    g = d.getObject(name)
    if g is None:
        g = d.addObject("App::DocumentObjectGroup", name)
    return g


def put(name, shape, grp, color=(0.8, 0.8, 0.8), transp=0, props=None, visible=True):
    o = d.addObject("Part::Feature", name)
    o.Shape = shape
    for pn, v in (props or {}).items():
        if isinstance(v, bool):
            o.addProperty("App::PropertyBool", pn, "Fuselage")
        else:
            o.addProperty("App::PropertyString", pn, "Fuselage")
            v = str(v)
        setattr(o, pn, v)
    group(grp).addObject(o)
    if App.GuiUp:
        try:
            o.ViewObject.ShapeColor = color
            o.ViewObject.Transparency = int(transp)
            o.ViewObject.Visibility = visible
        except Exception:
            pass
    return o


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(p0, p1, r):
    a, b = V(*p0), V(*p1)
    return Part.makeCylinder(r, (b - a).Length, a, b - a)


def interp(tab, x):
    if x <= tab[0][0]:
        return tab[0][1]
    for (x0, y0), (x1, y1) in zip(tab, tab[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return tab[-1][1]


def ext(tab):
    return [(XLO, tab[0][1])] + list(tab) + [(XHI, tab[-1][1])]


def face_xz(pts):
    vs = [V(x, 0, z) for x, z in pts]
    return Part.Face(Part.makePolygon(vs + [vs[0]]))


def below(tab):
    return face_xz(ext(tab) + [(XHI, -400.0), (XLO, -400.0)])


def above(tab):
    return face_xz(ext(tab) + [(XHI, 400.0), (XLO, 400.0)])


def prism_y(face, hw=150.0):
    return face.translated(V(0, -hw, 0)).extrude(V(0, 2 * hw, 0))


def plan_face(tab):
    t = ext(tab)
    vs = [V(x, h, 0) for x, h in t] + [V(x, -h, 0) for x, h in reversed(t)]
    return Part.Face(Part.makePolygon(vs + [vs[0]]))


def prism_z(face):
    return face.translated(V(0, 0, -400)).extrude(V(0, 0, 800))


def off(face, t):
    return face.makeOffset2D(t, join=2)


def ok(name, s):
    if s.isNull() or not s.isValid() or s.Volume < 1e-3:
        raise RuntimeError("%s: invalid or empty shape" % name)
    bb = s.BoundBox
    print("%-20s V %8.0f mm3 X %7.1f..%6.1f Y %6.1f..%5.1f Z %6.1f..%6.1f solids %d" % (
        name, s.Volume, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax, len(s.Solids)))
    return s


def fuse_all(shapes):
    shapes = [s for s in shapes if not s.isNull() and s.Volume > 1e-6]
    return shapes[0].fuse(shapes[1:]).removeSplitter() if len(shapes) > 1 else shapes[0]


def xslab(x0, x1):
    return box(x0, x1, -200, 200, -300, 100)


ZCLIP = box(XLO + 50, XHI - 50, -200, 200, -300, 100)

# ---------------- base regions ----------------
PLAN_F = plan_face(BP.PLAN)
PLAN = prism_z(PLAN_F)
PLAN_IN1 = prism_z(off(PLAN_F, -BP.T_SIDE_OUT))
PLAN_IN2 = prism_z(off(PLAN_F, -BP.T_SIDE_OUT - BP.T_SIDE_IN))
OUT = prism_y(below(BP.TOP)).common(prism_y(above(BP.BOTTOM))).common(PLAN).common(xslab(BP.X_FRONT, BP.X_END))
FLOOR_REG = prism_y(off(below(BP.BOTTOM), BP.T_FLOOR))
ABOVE_TOP = prism_y(above(BP.TOP))
INNER = OUT.common(PLAN_IN2).cut(FLOOR_REG)          # free interior (inside the 3 mm sides, above the floor)


def band_under_top(t):
    return prism_y(off(above(BP.TOP), t)).cut(ABOVE_TOP).common(ZCLIP)


def band_over_top(t):
    return ABOVE_TOP.cut(prism_y(off(above(BP.TOP), -t))).common(ZCLIP)


def inner_ring(w):
    return PLAN_IN2.cut(prism_z(off(PLAN_F, -BP.T_SIDE_OUT - BP.T_SIDE_IN - w)))


# ---------------- reference bodies from rev A (read only) ----------------
C_BALSA, C_INNER, C_LIGHT, C_PLY, C_PETG, C_CARB, C_PH = (0.86, 0.73, 0.50), (0.78, 0.63, 0.42), (0.93, 0.84, 0.62), \
    (0.70, 0.55, 0.35), (0.30, 0.55, 0.85), (0.15, 0.15, 0.15), (0.35, 0.35, 0.38)
for o in src.Objects:
    if o.Name.startswith("RefRes_"):
        put(o.Name, o.Shape.copy(), "Reservoir", tuple(o.ViewObject.ShapeColor[:3]) if App.GuiUp else C_PH,
            o.ViewObject.Transparency if App.GuiUp else 0,
            props=dict(ResState=getattr(o, "ResState", "closed"), MovingSet=bool(getattr(o, "MovingSet", False))),
            visible=o.Visibility)
wing = Part.makeCompound([o.Shape.copy() for o in src.Objects if o.Name.startswith("W_")])
put("Ref_WingRevA", wing, "CheckProxies", (0.70, 0.78, 0.90), 60,
    props=dict(Note="wing rev A as one compound for the clearance checks (hidden)"), visible=False)
# the real wing rev A: every part on its own (89 parts, +3 deg about Y through the origin, as in Fuselage_revA)
for o in src.Objects:
    if o.Name.startswith("W_"):
        col = tuple(o.ViewObject.ShapeColor[:3]) if App.GuiUp else (0.85, 0.75, 0.55)
        put(o.Name, o.Shape.copy(), "Wing", col, 0, props=dict(Note=getattr(o, "Label", o.Name)))
for n in ("F10_Tubes", "F11_TailBlock", "F12_Stab", "F13_Elevator", "F14_Fin", "F15_Rudder", "F16_Joiner", "F17_Horns",
          "F18_Pushrods", "F19_GuideClips"):
    o = src.getObject(n)
    put(n, o.Shape.copy(), "Tail", tuple(o.ViewObject.ShapeColor[:3]) if App.GuiUp else C_CARB, 0, props=dict(Note="as rev A"))
for o in src.Objects:
    if o.Name.startswith("PH_") and o.Name != "PH_Receiver":
        put(o.Name, o.Shape.copy(), "Placeholder", tuple(o.ViewObject.ShapeColor[:3]) if App.GuiUp else C_PH,
            o.ViewObject.Transparency if App.GuiUp else 0,
            props=dict(Note=getattr(o, "Note", "placeholder"), Mass_g=getattr(o, "Mass_g", "")))
rx = FP.RX
put("PH_Receiver", box(BP.RX_X0, BP.RX_X0 + rx[0], -rx[1] / 2, rx[1] / 2, FP.FLOOR_Z, FP.FLOOR_Z + rx[2]), "Placeholder", C_PH, 0,
    props=dict(Note="receiver placeholder (not selected), on the floor", Mass_g="8"))

rods = src.getObject("F18_Pushrods").Shape
ROD_AXES = []
for sol in rods.Solids:
    f = max([f for f in sol.Faces if f.Surface.TypeId == "Part::GeomCylinder"], key=lambda f: f.Area)
    u0, u1, v0, v1 = f.ParameterRange
    c, ax = f.Surface.Center, f.Surface.Axis
    ROD_AXES.append((c + ax * v0, c + ax * v1))
rod_clear = fuse_all([Part.makeCylinder(BP.ROD_CLEAR_R, (b - a).Length, a, b - a) for a, b in ROD_AXES])
rod_slot = fuse_all([Part.makeCylinder(2.0, (b - a).Length, a, b - a) for a, b in ROD_AXES]).common(xslab(240, 320))
tube_holes = fuse_all([cyl((200, s * FP.SOCK_Y, FP.SOCK_Z), (320, s * FP.SOCK_Y, FP.SOCK_Z), FP.SOCK_BORE / 2) for s in (1, -1)])
sock_r_out = FP.SOCK_BORE / 2 + FP.SOCK_WALL
zf = FP.FLOOR_Z
wi2 = FP.Y_LIMIT - BP.T_SIDE_OUT - BP.T_SIDE_IN     # 52.0 inner face of the laminated side
parts = {}          # name -> (shape, material, colour, note)

# ---------------- strips first (formers are notched round them) ----------------
lon = []
t = BP.LONGERON
for s, segs in BP.LONGERON_SEGS.items():
    for a, b in segs:
        wl = (wi2 if not (s > 0 and BP.SERVO_ZONE_R[0] < 0.5 * (a + b) < BP.SERVO_ZONE_R[1]) else wi2) - 0.01
        tri = Part.Face(Part.makePolygon([V(0, s * wl, zf + 0.01), V(0, s * (wl - t), zf + 0.01), V(0, s * wl, zf + 0.01 + t),
                                          V(0, s * wl, zf + 0.01)]))
        lon.append(tri.translated(V(a, 0, 0)).extrude(V(b - a, 0, 0)))
LONG = fuse_all(lon).cut(xslab(FP.STOP_X[0] - 0.05, FP.STOP_X[1] + 0.05))
lx0, lx1 = BP.LIP_X
LIP = band_under_top(BP.LIP_T).common(inner_ring(BP.LIP_W)).common(xslab(lx0, lx1))
ledx0, ledx1 = BP.LEDGE_X
LEDG = band_under_top(BP.LEDGE).common(inner_ring(BP.LEDGE)).common(xslab(ledx0, ledx1)).cut(xslab(FP.STOP_X[0] - 0.05, FP.STOP_X[1] + 0.05))
kx0, kx1 = BP.KEEL_X
KEEL = fuse_all([box(kx0 + 0.05, kx1 - 1.5, *sorted((s * BP.KEEL_Y, s * (BP.KEEL_Y + BP.KEEL_W))), zf + 0.01, zf + BP.KEEL_H) for s in (1, -1)])
# saddles (PETG, reservoir P12a/b) + strap bridges: needed early, the formers are notched round them
sad = []
for nm, (sa, sb_) in (("RefRes_P12a_Saddle1", FP.SADDLE1_X), ("RefRes_P12b_Saddle2", FP.SADDLE2_X)):
    sad.append(src.getObject(nm).Shape.copy())
    xc = 0.5 * (sa + sb_)
    for s in (1, -1):
        y0, y1 = sorted((s * 43.5, s * 46.0))
        sad.append(box(xc - 12.0, xc + 12.0, y0, y1, zf, zf + 3.0).cut(box(xc - 11.0, xc + 11.0, y0 - 1, y1 + 1, zf - 0.1, zf + 2.0)))
SAD = fuse_all(sad)
STRIPS = fuse_all([LONG, LIP, LEDG, KEEL, SAD])

# ---------------- skins ----------------
SIDE_O = OUT.cut(PLAN_IN1).cut(FLOOR_REG)
SIDE_I = OUT.common(PLAN_IN1).cut(PLAN_IN2).cut(FLOOR_REG)
sz0, sz1 = BP.SERVO_ZONE_R
SIDE_I = SIDE_I.cut(box(sz0, sz1, 0, 200, -300, 100))          # right side single layer at the release servo
FLOOR = OUT.common(FLOOR_REG)
fr = FP.FLOOR_HOLE_RECT
FLOOR = FLOOR.cut(box(fr[0], fr[1], fr[2], fr[3], -200, 0))
hx0, hx1 = BP.HATCH_X
HATCH = band_over_top(BP.T_HATCH).common(PLAN).common(xslab(hx0, hx1))
dx0, dx1 = BP.DECK_X
DECK = band_under_top(BP.T_DECK).common(PLAN_IN2).common(xslab(dx0 + BP.FRAME_T, dx1))

# holes through both side layers
(px0, px1), (pz0, pz1) = FP.POCKET_X, FP.POCKET_Z
w = FP.POCKET_WALL
cuts = [box(px0 - w, px1 + w, 50, 60, max(pz0 - w, zf), pz1 + w)]                       # D-059 pocket window (right)
fx_, fz_ = FP.SAF_PIN_POS
cuts.append(cyl((fx_, -60, fz_), (fx_, -40, fz_), FP.FLAG_HOLE_D / 2))                   # safety-pin flag hole (left)
fb = src.getObject("RefRes_P10_Flag").Shape.BoundBox
cuts.append(box(fb.XMin - 1, fb.XMax + 1, -60, -45, fb.ZMin - 1, fb.ZMax + 1))
for s in (1, -1):
    cuts.append(cyl((FP.STUB_X, s * 40, FP.STUB_Z), (FP.STUB_X, s * 60, FP.STUB_Z), FP.STUB_D / 2 + 0.1))
cuts.append(cyl((FP.DOWEL_X, -60, FP.DOWEL_Z), (FP.DOWEL_X, 60, FP.DOWEL_Z), FP.DOWEL_D / 2 + 0.1))
cuts.append(rod_slot)
CUTS = fuse_all(cuts)
SIDE_O = SIDE_O.cut(CUTS)
SIDE_I = SIDE_I.cut(CUTS)

# ---------------- self-locating tabs: every former has 2 floor tabs and 2 side tabs through the skins ----------------
WALL = OUT.cut(PLAN_IN2).cut(FLOOR_REG)
FORMERS = [(n, x, k) for n, x, k in BP.FRAMES] + [("BS_FrontStop", FP.STOP_X[0], "stop"), ("BS_Bulkhead", BP.AFT_KINK, "bulkhead"),
                                                   ("BS_EndFormer", BP.END_X[0], "end")]
TABS = {}
for n, x0, kind in FORMERS:
    tw, yc_f, zc_s = BP.TAB_W / 2, BP.FLOOR_TAB_Y[kind], BP.SIDE_TAB_ZC[kind]
    tl = []
    for s in (1, -1):
        tl.append(box(x0, x0 + BP.FRAME_T, s * yc_f - tw, s * yc_f + tw, -300, 100).common(OUT).common(FLOOR_REG))
        tl.append(box(x0, x0 + BP.FRAME_T, *sorted((s * 20.0, s * 80.0)), zc_s - tw, zc_s + tw).common(WALL))
    TABS[n] = fuse_all(tl)
TAB_ALL = fuse_all(list(TABS.values()))
SIDE_O = SIDE_O.cut(TAB_ALL)
SIDE_I = SIDE_I.cut(TAB_ALL)
FLOOR = FLOOR.cut(TAB_ALL)

# ---------------- hex lightening (through both layers) ----------------
R_hex = BP.HEX_AF / math.sqrt(3.0)                 # circumradius
pitch_x = 1.5 * (BP.HEX_AF + BP.HEX_WEB) / math.sqrt(3.0)
pitch_z = BP.HEX_AF + BP.HEX_WEB
frame_x = [x for _, x, _ in BP.FRAMES] + [FP.STOP_X[0], BP.AFT_KINK]
frame_x2 = [(x, x + BP.FRAME_T) for x in frame_x]


def zfloor_top(x):
    return interp(BP.BOTTOM, x) + BP.T_FLOOR


def cell_ok(x, z, s):
    r = R_hex
    if not (BP.HEX_X[0] + r <= x <= BP.HEX_X[1] - r):
        return False
    for a, b in frame_x2:
        if a - BP.HEX_FRAME_CLEAR - r < x < b + BP.HEX_FRAME_CLEAR + r:
            return False
    for xx in (x - r, x, x + r):
        if z - r < zfloor_top(xx) + BP.HEX_MARGIN or z + r > interp(BP.TOP, xx) - BP.HEX_MARGIN:
            return False
    for x0, x1, z0, z1, sd in BP.HEX_SOLID:
        if (sd == 0 or sd == s) and x0 - r < x < x1 + r and z0 - r < z < z1 + r:
            return False
    return True


def segments(s):
    pts = [(x, s * h) for x, h in BP.PLAN]
    return list(zip(pts, pts[1:]))


hexes = {1: [], -1: []}
n_cells = {1: 0, -1: 0}
for s in (1, -1):
    for (xa, ya), (xb, yb) in segments(s):
        dvec = V(xb - xa, yb - ya, 0)
        L = dvec.Length
        dvec.normalize()
        nvec = V(-dvec.y, dvec.x, 0) * (1 if s > 0 else -1)
        nvec.normalize()
        u = R_hex + 1.0
        col = 0
        while u < L - R_hex - 1.0:
            p = V(xa, ya, 0) + dvec * u
            z = -118.0 + (pitch_z / 2 if col % 2 else 0.0)
            while z < 0:
                if cell_ok(p.x, z, s):
                    c = V(p.x, p.y, z)
                    vs = [c + dvec * (R_hex * math.cos(math.radians(60 * k))) + V(0, 0, R_hex * math.sin(math.radians(60 * k))) for k in range(6)]
                    f = Part.Face(Part.makePolygon(vs + [vs[0]]))
                    hexes[s].append(f.translated(nvec * 5.0).extrude(nvec * -10.0))
                    n_cells[s] += 1
                z += pitch_z
            u += pitch_x
            col += 1
print("hex cells: right %d, left %d" % (n_cells[1], n_cells[-1]))
# check proxies: the side layers without the hex holes (holes only remove material, so clearance checks on the proxies
# are conservative and about 50x faster than on panels with hundreds of hole faces)
PROXY = {}
for s, nm in ((1, "R"), (-1, "L")):
    half = box(-400, 600, 0, 200, -300, 100) if s > 0 else box(-400, 600, -200, 0, -300, 100)
    PROXY["BS_Side%s_Outer" % nm] = SIDE_O.common(half).cut(box(sz0, sz1, 0, 200, -300, 100)) if s > 0 else SIDE_O.common(half)
    PROXY["BS_Side%s_Inner" % nm] = SIDE_I.common(half).cut(box(BP.GRIP_PLY[0], BP.GRIP_PLY[1], -200, 200, -300, BP.GRIP_PLY[2]))
HEX_AREA = 0.0
for s in (1, -1):
    if hexes[s]:
        comp = Part.makeCompound(hexes[s])
        half = box(-400, 600, 0, 200, -300, 100) if s > 0 else box(-400, 600, -200, 0, -300, 100)
        HEX_AREA += len(hexes[s]) * (1.5 * math.sqrt(3.0) * R_hex ** 2)
        so = SIDE_O.common(half).cut(comp)
        si = SIDE_I.common(half).cut(comp)
        nm = "R" if s > 0 else "L"
        if s > 0:      # servo zone: single layer -> 1.5 mm birch ply insert spliced into the outer layer (strength_estimate.m)
            zone = box(sz0, sz1, 0, 200, -300, 100)
            parts["BS_SideR_PlyInsert"] = (so.common(zone), "ply", C_PLY, "1.5 mm birch ply insert in the outer layer, X 44 .. 96 (grip on the single layer)")
            so = so.cut(zone)
        grip = box(BP.GRIP_PLY[0], BP.GRIP_PLY[1], -200, 200, -300, BP.GRIP_PLY[2])
        parts["BS_Side%s_Outer" % nm] = (so, "balsa_med", C_BALSA, "1.5 mm medium balsa, grain X, hex lightening under film")
        parts["BS_Side%s_Inner" % nm] = (si.cut(grip), "balsa_med", C_INNER, "1.0 mm medium balsa, grain vertical, laminated inside the outer layer")
        parts["BS_Side%s_InnerGrip" % nm] = (si.common(grip), "ply", C_PLY, "1.0 mm birch ply inner layer in the launch-grip zone")
parts["BS_Floor"] = (FLOOR, "balsa_med", C_BALSA, "1.5 mm medium balsa, grain across (Y)")
parts["BS_Hatch"] = (HATCH, "balsa_light", C_LIGHT, "1.5 mm light balsa hatch, 2 flat pieces glued at the front-stop line, 4 magnet pairs")
parts["BS_AftDeck"] = (DECK, "balsa_med", C_BALSA, "1.5 mm aft deck, bulkhead to the tail node")
parts["BS_Longerons"] = (LONG, "balsa_med", C_BALSA, "6 x 6 balsa triangle stock, floor-side corners")
parts["BS_SeatCapstrip"] = (LIP, "balsa_med", C_BALSA, "6 x 3 balsa wing-seat capstrip (top longeron)")
parts["BS_HatchLedges"] = (LEDG, "balsa_med", C_BALSA, "3 x 3 balsa hatch ledges")

# ---------------- formers ----------------
U_CUT = cyl((-400, 0, BP.U_ZC), (600, 0, BP.U_ZC), BP.U_R).fuse(box(-400, 600, -BP.U_R, BP.U_R, BP.U_ZC, 200))
ws_ = wi2 - BP.FRAME_STRIP
CORNER_CUT = box(-400, 600, -ws_, ws_, zf + BP.FRAME_STRIP, BP.U_ZC).cut(cyl((-400, 0, BP.U_ZC), (600, 0, BP.U_ZC), BP.FRAME_BAND_R))
for name, x0, kind in BP.FRAMES:
    sec = INNER.common(xslab(x0, x0 + BP.FRAME_T))
    if kind in ("U", "split"):
        sec = sec.cut(U_CUT).cut(CORNER_CUT)
        if kind == "split":
            sec = sec.cut(box(-400, 600, -BP.SPLIT_HW, BP.SPLIT_HW, -300, 100))
    else:                                            # nose: cross bar under the tray, legs outboard of the battery
        sec = sec.cut(box(-400, 600, -BP.NOSE_HW, BP.NOSE_HW, FP.TRAY_Z - BP.TRAY_T, 200))
    sec = sec.cut(STRIPS)
    parts[name] = (sec, "liteply", C_PLY, "3 mm lite-ply %s former" % {"U": "U (open top)", "split": "split U (belly opening)", "nose": "nose U, tray seat"}[kind])
sx0, sx1 = FP.STOP_X
stop = INNER.common(xslab(sx0, sx1)).cut(cyl((sx0 - 1, 0, -60), (sx1 + 1, 0, -60), BP.STOP_ANNULUS[0]))
rim = BP.STOP_RIM
zt_s = interp(BP.TOP, sx0)
light = box(sx0 - 1, sx1 + 1, -(wi2 - rim), wi2 - rim, zf + rim, zt_s - rim).cut(cyl((sx0 - 2, 0, -60), (sx1 + 2, 0, -60), BP.STOP_ANNULUS[1]))
light = light.cut(box(sx0 - 2, sx1 + 2, -BP.STOP_SPOKE / 2, BP.STOP_SPOKE / 2, -300, 100))           # top / bottom spokes
light = light.cut(box(sx0 - 2, sx1 + 2, -300, 300, -60 - BP.STOP_SPOKE / 2, -60 + BP.STOP_SPOKE / 2))  # side spokes
stop = stop.cut(light).cut(STRIPS)
parts["BS_FrontStop"] = (stop, "liteply", C_PLY, "3 mm lite-ply front stop: bearing ring r 25-42 + rim + 4 spokes (10 g nose-in), nose kink")
bx = BP.AFT_KINK
secb = INNER.cut(band_under_top(BP.T_DECK)).common(xslab(bx, bx + BP.FRAME_T))
sec_in = (secb.common(prism_z(off(PLAN_F, -BP.T_SIDE_OUT - BP.T_SIDE_IN - BP.BULKHEAD_RING)))
          .cut(prism_y(off(below(BP.BOTTOM), BP.T_FLOOR + BP.BULKHEAD_RING)))
          .cut(prism_y(off(above(BP.TOP), BP.T_DECK + BP.BULKHEAD_RING))))
bar = secb.common(box(bx - 1, bx + BP.FRAME_T + 1, -200, 200, FP.SOCK_Z - 5.0, FP.SOCK_Z + 5.0))
bulk = secb.cut(sec_in).fuse(bar).removeSplitter().cut(tube_holes).cut(rod_clear).cut(STRIPS)
parts["BS_Bulkhead"] = (bulk, "ply", C_PLY, "3 mm birch ply bulkhead ring + bar at the aft kink, tubes glued through")

# ---------------- printed permanent jigs ----------------
nx0, nx1 = BP.NOSE_RING_X
fw0, fw1 = BP.FIREWALL_X
hw_f = interp(BP.PLAN, BP.X_FRONT)
zb_f, zt_f = interp(BP.BOTTOM, BP.X_FRONT), interp(BP.TOP, BP.X_FRONT) + BP.T_HATCH
collar_o = box(nx0, BP.X_FRONT, -hw_f, hw_f, zb_f, zt_f)
collar_i = box(nx0 - 1, BP.X_FRONT + 1, -hw_f + BP.JIG_T, hw_f - BP.JIG_T, zb_f + BP.JIG_T, zt_f - BP.JIG_T)
sleeve_o = INNER.common(xslab(BP.X_FRONT, nx1))
sleeve_i = sleeve_o.common(box(BP.X_FRONT - 1, nx1 + 1, -hw_f + BP.T_SIDE_OUT + BP.T_SIDE_IN + BP.JIG_T, hw_f - BP.T_SIDE_OUT - BP.T_SIDE_IN - BP.JIG_T,
                               zb_f + 4.0, zt_f - 3.0))
ring = collar_o.cut(collar_i).fuse(sleeve_o.cut(box(BP.X_FRONT - 1, nx1 + 1, -hw_f + 4.2, hw_f - 4.2, zb_f + 4.2, 100)))
fw_plate = box(fw0, fw1, -hw_f + BP.JIG_T, hw_f - BP.JIG_T, zb_f + BP.JIG_T, zt_f - BP.JIG_T)
yc, zc = FP.MOTOR_C
holes = [cyl((fw0 - 1, yc, zc), (fw1 + 1, yc, zc), 5.0)]
r16, r19 = FP.XMOUNT[0] / 2, FP.XMOUNT[1] / 2
for dy, dz in ((r16, 0), (-r16, 0), (0, r19), (0, -r19)):
    holes.append(cyl((fw0 - 1, yc + dy, zc + dz), (fw1 + 1, yc + dy, zc + dz), 1.6))
for y, z in FP.FW_COOL:
    holes.append(cyl((fw0 - 1, y, z), (fw1 + 1, y, z), 6.0))
parts["BS_Firewall"] = (fw_plate.cut(fuse_all(holes)), "ply", C_PLY, "3 mm birch ply firewall seated in the nose ring")
parts["BS_NoseRing"] = (ring.cut(fw_plate).cut(STRIPS), "petg", C_PETG, "PETG permanent jig: collar round the firewall + glue sleeve; thrust wedge in F-D")
ex0, ex1 = BP.END_X
endp = INNER.cut(band_under_top(BP.T_DECK)).common(xslab(ex0, ex1)).cut(tube_holes).cut(rod_clear)
parts["BS_EndFormer"] = (endp, "liteply", C_PLY, "3 mm lite-ply end former, tubes glued through D10.3 holes (D-068: replaces the PETG tail node)")
rings = []
for xa in (bx + BP.FRAME_T, ex0 - BP.TUBE_RING_T):
    for s in (1, -1):
        rings.append(cyl((xa, s * FP.SOCK_Y, FP.SOCK_Z), (xa + BP.TUBE_RING_T, s * FP.SOCK_Y, FP.SOCK_Z), BP.TUBE_RING_OD / 2))
parts["BS_TubeRings"] = (fuse_all(rings).cut(tube_holes), "ply", C_PLY, "3 mm birch-ply rings round the tube holes (4)")

# ---------------- doublers, tray, flap stop, pads ----------------
a, b_, z0, z1, td = BP.STUB_DOUBLER
dbl = fuse_all([box(a, b_, *sorted((s * wi2, s * (wi2 - td))), z0, z1) for s in (1, -1)])
dbl = dbl.cut(fuse_all([cyl((FP.STUB_X, s * 40, FP.STUB_Z), (FP.STUB_X, s * 60, FP.STUB_Z), FP.STUB_D / 2 + 0.1) for s in (1, -1)])).cut(STRIPS)
parts["BS_StubDoublers"] = (dbl, "ply", C_PLY, "3 mm birch ply doublers at the band stubs")
tx0, tx1 = BP.TRAY_X
tray = box(tx0, tx1, -BP.TRAY_HW, BP.TRAY_HW, FP.TRAY_Z - BP.TRAY_T, FP.TRAY_Z)
tray = tray.cut(fuse_all([box(x - 1.25, x + 1.25, -11, 11, FP.TRAY_Z - 5, FP.TRAY_Z + 1) for x in (-112.0, -80.0)]))
parts["BS_BatteryTray"] = (tray, "liteply", C_PLY, "1.5 mm lite-ply tray |Y| 20 on the nose frames and the front stop")
fs0, fs1, fshw, fst = BP.FLAP_STOP_PLY
parts["BS_FlapStop"] = (box(fs0, fs1, -fshw, fshw, zf, zf + fst).cut(STRIPS), "ply", C_PLY, "1.5 mm birch ply flap stop (D-061)")
L_, W_, H_, TL_ = FP.TSERVO
pads = []
for s in (1, -1):
    ycs = s * FP.TSERVO_YC
    for xa in (FP.TSERVO_XC - TL_ / 2, FP.TSERVO_XC + L_ / 2):
        y0, y1 = sorted((ycs - s * W_ / 2, s * 80.0))
        pads.append(box(xa, xa + (TL_ - L_) / 2, y0, y1, FP.TSERVO_ZB + 17.5, FP.TSERVO_ZB + 20.0).common(INNER))
parts["BS_TailServoPads"] = (fuse_all(pads), "liteply", C_PLY, "2.5 mm lite-ply tail-servo pads")

# ---------------- PETG hard points ----------------
# saddles: the reservoir P12a/b outline (thin cradle arc + base with the strap tunnel between them) as laser-cut
# 3 mm lite-ply layers glued face to face; the layers are stacked and glued on the bottle wrapped in cling film
# (the bottle is the alignment jig). D-068 trim, was PETG.
parts["BS_Saddles"] = (SAD, "liteply", C_PLY, "3 mm lite-ply layers of the P12a/b outline + strap bridges, glued on the cling-wrapped bottle")
cup = box(px0 - w, px1 + w, FP.Y_LIMIT - BP.T_SIDE_OUT, FP.POCKET_YIN + w, max(pz0 - w, zf), pz1 + w).cut(box(px0, px1, 50.0, FP.POCKET_YIN, pz0, pz1))
servo = src.getObject("RefRes_P14_Servo_MG90S").Shape
sb = servo.BoundBox
tabs = servo.common(box(sb.XMin - 1, sb.XMax + 1, sb.YMin - 1, sb.YMax + 1, sb.ZMin - 1, sb.ZMax + 1)
                    .cut(box(sb.XMin + 4.0, sb.XMax - 4.0, sb.YMin - 2, sb.YMax + 2, sb.ZMin - 2, sb.ZMax + 2)))
tz0 = min(v.Point.z for v in tabs.Vertexes)
wi_servo = FP.Y_LIMIT - BP.T_SIDE_OUT
mount = []
for xa, xb in ((sb.XMin - 0.5, sb.XMin + 4.5), (sb.XMax - 4.5, sb.XMax + 0.5)):
    shelf = box(xa, xb, sb.YMin, wi_servo, tz0 - 3.0, tz0)
    gus = box(0.5 * (xa + xb) - 0.6, 0.5 * (xa + xb) + 0.6, sb.YMax + 0.5, wi_servo, tz0, tz0 + 12.0)
    mount.append(shelf.fuse(gus).cut(cyl((0.5 * (xa + xb), 0.5 * (sb.YMin + sb.YMax), tz0 - 4.0), (0.5 * (xa + xb), 0.5 * (sb.YMin + sb.YMax), tz0 + 1.0), 0.8)))
parts["BS_ServoPocketMount"] = (fuse_all([cup] + mount), "petg", C_PETG, "PETG D-059 arm pocket + release-servo shelves")
skid_band = prism_y(below(BP.BOTTOM)).cut(prism_y(off(below(BP.BOTTOM), -BP.SKID_T))).common(ZCLIP)
parts["BS_Skids"] = (fuse_all([skid_band.common(box(a_, b2, -BP.SKID_HW, BP.SKID_HW, -400, 400)) for a_, b2 in BP.SKIDS]), "ply", C_PLY, "1.5 mm birch ply skids, replaceable (D-068 trim, was PETG)")
parts["BS_Keels"] = (KEEL.cut(SAD), "balsa_med", C_BALSA, "2 floor keels 5 x 3 balsa grain X, through the formers")
parts["BS_RearDowel"] = (src.getObject("F8_RearDowel").Shape.copy(), "birch", C_PLY, "D5 rear band dowel")
parts["BS_BandStubs"] = (src.getObject("F9_BandStubs").Shape.copy(), "carbon", C_CARB, "D4 carbon front band stubs (D-053)")

# tabs join their formers
for n, tb in TABS.items():
    s_, mat, col, note = parts[n]
    parts[n] = (s_.fuse(tb).removeSplitter(), mat, col, note + "; 2 floor + 2 side tabs")

# ---------------- removable printed assembly jigs (PLA, bench only) ----------------
jigs = {}          # name -> (shape, note, checked_against_wing, bench_only)
BZ = BP.BOARD_Z
skids_shape = parts["BS_Skids"][0]
for nm_, (xa, xb) in (("JIG_J1a_NoseWedge", BP.JIG_NOSE_WEDGE_X), ("JIG_J1b_TailWedge", BP.JIG_TAIL_WEDGE_X)):
    wdg = prism_y(below(BP.BOTTOM)).common(PLAN).common(xslab(xa, xb)).common(box(-400, 600, -200, 200, BZ, 100)).cut(skids_shape)
    hollow = prism_y(off(below(BP.BOTTOM), -3.0)).common(prism_z(off(PLAN_F, -4.0))).common(xslab(xa + 4, xb - 4))
    wdg = wdg.cut(hollow.common(box(-400, 600, -200, 200, BZ - 1, 100)).cut(box(0.5 * (xa + xb) - 2, 0.5 * (xa + xb) + 2, -200, 200, -300, 100)))
    xm = 0.5 * (xa + xb)
    wdg = wdg.cut(fuse_all([cyl((xm, s * 12.0, BZ - 1), (xm, s * 12.0, 0), 2.0) for s in (1, -1)]))      # 2 screw holes to the board
    jigs[nm_] = (wdg, "J1 building board: supports the sloped %s floor at its angle; screw to the board" % ("nose" if "Nose" in nm_ else "tail-cone"), True, False)
for k, (xa, xb) in enumerate(BP.JIG_SQUARE_X):
    for s, nm in ((1, "R"), (-1, "L")):
        sq = box(xa, xb, *sorted((s * FP.Y_LIMIT, s * (FP.Y_LIMIT + BP.JIG_SQUARE_OUT))), BZ, BP.JIG_SQUARE_TOP)
        sq = sq.cut(box(xa + 4, xb - 4, *sorted((s * (FP.Y_LIMIT + 4), s * (FP.Y_LIMIT + BP.JIG_SQUARE_OUT + 1))), BZ + 4, BP.JIG_SQUARE_TOP + 1))
        jigs["JIG_J2_Square%d%s" % (k + 1, nm)] = (sq, "J2 side square: holds the side vertical to the floor (L-section)", True, False)
nx0, nx1 = BP.JIG_NOSE_X
nose_blk = prism_z(off(PLAN_F, BP.JIG_NOSE_OUT)).cut(PLAN).common(xslab(nx0, nx1)).common(box(-400, 600, -200, 200, BZ, BP.JIG_NOSE_TOP))
nose_in = prism_z(off(PLAN_F, BP.JIG_NOSE_OUT - 3.0)).cut(prism_z(off(PLAN_F, 4.0))).common(xslab(nx0 + 4, nx1 - 4)).common(
    box(-400, 600, -200, 200, BZ + 4, BP.JIG_NOSE_TOP + 1))
nose_blk = nose_blk.cut(nose_in.cut(xslab(0.5 * (nx0 + nx1) - 2, 0.5 * (nx0 + nx1) + 2)))        # open box: face 4, wall 3, base 4, rib
for s, nm in ((1, "R"), (-1, "L")):
    half = box(-400, 600, 0, 200, -300, 100) if s > 0 else box(-400, 600, -200, 0, -300, 100)
    jigs["JIG_J3_NoseTaper" + nm] = (nose_blk.common(half), "J3 nose taper block: holds the nose side at its plan angle", True, False)
chan = []
for s in (1, -1):
    chan.append(cyl((200, s * FP.SOCK_Y, FP.SOCK_Z), (800, s * FP.SOCK_Y, FP.SOCK_Z), FP.TUBE_OD / 2 + 0.15))
    chan.append(box(200, 800, s * FP.SOCK_Y - FP.TUBE_OD / 2 - 0.15, s * FP.SOCK_Y + FP.TUBE_OD / 2 + 0.15, FP.SOCK_Z, 100))
CHAN = fuse_all(chan)
for k, (xa, xb) in enumerate(BP.JIG_TAIL_BLOCKS):
    blk = box(xa, xb, -BP.JIG_TAIL_HW, BP.JIG_TAIL_HW, BZ, BP.JIG_TAIL_TOP).cut(CHAN)
    blk = blk.cut(box(xa + 5, xb - 5, -BP.JIG_TAIL_HW + 5, BP.JIG_TAIL_HW - 5, BZ - 1, FP.SOCK_Z - FP.TUBE_OD / 2 - 6))   # lighten
    note = ("J4 tail jig: front face squares the end former; U-cradles hold both tubes parallel at Y +-16, Z -40" if k == 0
            else "J4 tail jig: second tube cradle near the tail block")
    jigs["JIG_J4_TubeCradle%d" % (k + 1)] = (blk, note, True, False)
r0, r1 = BP.JIG_SEAT_RAIL
for k, (xa, xb) in enumerate(BP.JIG_SEAT_X):
    band = band_over_top(BP.JIG_SEAT_H).common(xslab(xa, xb))
    rails = fuse_all([box(-400, 600, *sorted((s * r0, s * r1)), -300, 100) for s in (1, -1)] +
                     [box(xc - 4, xc + 4, -r1, r1, -300, 100) for xc in (xa + 6, 0.5 * (xa + xb), xb - 6)])
    jigs["JIG_J5_SeatGauge%d" % (k + 1)] = (band.common(rails), "J5 wing-seat gauge: wing lower surface + 1 mm foam, sand the side tops / capstrip to it", False, False)
C_JIG = (0.95, 0.45, 0.70)
for nm_, (sh, note, wing_chk, bench) in jigs.items():
    put(nm_, ok(nm_, sh.removeSplitter()), "Jigs", C_JIG, 30, props=dict(Material="PLA_jig", Note=note, CheckWing=wing_chk, Bench=bench),
        visible=False)                                    # hidden by default: the document opens on the aircraft

# formers are notched for the keels; keels are cut at the saddles (the saddles sit on the floor)
for n, (s_, mat, col, note) in parts.items():
    s_ = ok(n, s_.removeSplitter())
    put(n, s_, "BalsaPod", col, 0, props=dict(Material=mat, Note=note))
for n, s_ in PROXY.items():
    put("PX_" + n[3:], s_.removeSplitter(), "CheckProxies", C_BALSA, 0, props=dict(Note="check proxy of %s without the hex holes" % n), visible=False)
o = d.getObject("BS_SideR_Outer")
o.addProperty("App::PropertyString", "HexArea_mm2", "Fuselage")
o.HexArea_mm2 = "%.0f" % HEX_AREA
d.recompute()
if App.GuiUp:
    import FreeCADGui as Gui
    Gui.getDocument(BP.DOC).activeView().viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
print("balsa pod v2 build done: %d parts, hex holes %d, hex area %.0f mm2" % (len(parts), n_cells[1] + n_cells[-1], HEX_AREA))
