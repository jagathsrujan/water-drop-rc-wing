"""Reservoir rev A - helpers and one function per part (FreeCAD, Part workbench). All numbers from res_params."""
import math
import FreeCAD as App
import Part
from FreeCAD import Vector as V
import res_params as P

DOC = "Reservoir_revA"
COLORS = {
    "PET": (0.65, 0.82, 1.0), "water": (0.15, 0.40, 0.95), "PETG": (0.82, 0.82, 0.82),
    "moving": (0.90, 0.10, 0.10), "gasket": (0.08, 0.08, 0.08), "steel": (0.55, 0.60, 0.70),
    "flag": (0.95, 0.05, 0.05), "ref": (0.80, 0.70, 0.55), "cap": (0.90, 0.90, 0.95),
    "valve": (0.25, 0.55, 0.35), "saddle": (0.30, 0.70, 0.30), "strap": (0.15, 0.30, 0.15), "balsa": (0.85, 0.70, 0.45),
    "servo": (0.25, 0.25, 0.30),
}
TRANSP = {"PET": 70, "water": 50}


def doc():
    d = App.listDocuments().get(DOC)
    if d is None:
        d = App.newDocument(DOC)
    return d


def group(name):
    d = doc()
    g = d.getObject(name)
    if g is None:
        g = d.addObject("App::DocumentObjectGroup", name)
    return g


def clear_group(name):
    d = doc()
    g = d.getObject(name)
    if g is not None:
        for o in list(g.Group):
            d.removeObject(o.Name)


def put(name, shape, color, grp, material="", rule="", note=""):
    """One Part::Feature per part. material = key of P.RHO; rule = 'thin' | 'thick' | 'fixed'."""
    d = doc()
    if d.getObject(name) is not None:
        d.removeObject(name)
    o = d.addObject("Part::Feature", name)
    o.Shape = shape
    for pn, v in (("Material", material), ("MassRule", rule), ("Note", note)):
        o.addProperty("App::PropertyString", pn, "Reservoir")
        setattr(o, pn, v)
    group(grp).addObject(o)
    try:
        o.ViewObject.ShapeColor = COLORS[color]
        o.ViewObject.Transparency = TRANSP.get(color, 0)
        o.ViewObject.Lighting = "Two side"
    except Exception:
        pass
    return o


def com(s):
    """Centre of mass of a shape (also compounds)."""
    sols = s.Solids
    vt = sum(x.Volume for x in sols)
    return V(sum(x.CenterOfMass.x * x.Volume for x in sols) / vt, sum(x.CenterOfMass.y * x.Volume for x in sols) / vt,
             sum(x.CenterOfMass.z * x.Volume for x in sols) / vt)


def info(name, s):
    bb = s.optimalBoundingBox() if hasattr(s, "optimalBoundingBox") else s.BoundBox
    print("%-18s valid=%s vol=%9.1f mm3  BB X %.2f..%.2f Y %.2f..%.2f Z %.2f..%.2f"
          % (name, s.isValid(), s.Volume, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))


# ---------------- primitives ----------------
def ax_cyl(R, x0, x1):
    """Cylinder about the bottle axis."""
    return Part.makeCylinder(R, x1 - x0, V(x0, P.AXIS_Y, P.AXIS_Z), V(1, 0, 0))


def zcyl(R, z0, z1, x, y=0.0):
    return Part.makeCylinder(R, z1 - z0, V(x, y, z0), V(0, 0, 1))


def ycyl(R, y0, y1, x, z):
    return Part.makeCylinder(R, y1 - y0, V(x, y0, z), V(0, 1, 0))


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def obround(L, W, cx, cy, z0, z1):
    s = (L - W) / 2.0
    b = box(cx - s, cx + s, cy - W / 2, cy + W / 2, z0, z1)
    return b.fuse(zcyl(W / 2, z0, z1, cx - s, cy)).fuse(zcyl(W / 2, z0, z1, cx + s, cy)).removeSplitter()


def revolve_profile(pts, x0):
    """pts = [(yu, r)...] starting and ending on the axis (r=0 allowed); revolve about the bottle axis."""
    vs = [V(x0 + yu, r, P.AXIS_Z) for yu, r in pts]
    vs.append(vs[0])
    f = Part.Face(Part.makePolygon(vs))
    return f.revolve(V(x0, 0, P.AXIS_Z), V(1, 0, 0), 360)


# ---------------- Stage A: bottle ----------------
def bottle_solids(x0):
    """Return dict: outer O, inner I (interior, open at the neck end), shell, cap. x0 = base X. No holes."""
    prof = P.BOTTLE_PROFILE
    w = P.WALL
    outer_pts = [(0, 0)] + [tuple(p) for p in prof] + [(prof[-1][0], 0)]
    inner_pts = [(w, 0), (w, prof[0][1] - w)] + [(yu, r - w) for yu, r in prof[1:]] + [(prof[-1][0], 0)]
    O = revolve_profile(outer_pts, x0)
    I = revolve_profile(inner_pts, x0)
    # punt (base dome): spherical cap, footprint radius PUNT_R, height PUNT_H, pushed into the bottle
    h, a = P.PUNT_H, P.PUNT_R
    Rs = (a * a + h * h) / (2 * h)

    def dome(shift):
        sph = Part.makeSphere(Rs, V(x0 + shift + h - Rs, P.AXIS_Y, P.AXIS_Z))
        return sph.common(ax_cyl(P.R_CYL, x0 + shift - 0.5, x0 + shift + h + 1))
    O = O.cut(dome(0.0))
    I = I.cut(dome(w))
    ext = P.BOTTLE_PROFILE[-1][0]
    I_ext = I.fuse(ax_cyl(P.NECK_BORE_D / 2, x0 + ext - 1, x0 + ext + 1))   # open end for the cut
    shell = O.cut(I_ext)
    tube = ax_cyl(P.NECK_OD / 2, x0 + P.NECK_Y0, x0 + P.NECK_Y1)
    ring = ax_cyl(P.RING_D / 2, x0 + P.RING_Y0, x0 + P.RING_Y1)
    bore = ax_cyl(P.NECK_BORE_D / 2, x0 + P.RING_Y0 - 1, x0 + ext + 1)
    pet = shell.fuse(tube).fuse(ring).cut(bore.fuse(I_ext)).removeSplitter()
    cap = ax_cyl(P.CAP_D / 2, x0 + P.CAP_Y0, x0 + P.CAP_Y1).cut(ax_cyl(P.NECK_OD / 2, x0 + P.CAP_Y0 - 1, x0 + ext))
    return dict(O=O, I=I, pet=pet, cap=cap)


def water_solid(I, x0, vol_ml=None):
    """Interior below a horizontal plane that gives vol_ml. Returns (solid, level_z)."""
    vol_ml = vol_ml or P.WATER_ML
    big = 400.0

    def below(z):
        return I.common(box(x0 - 5, x0 + 300, -big, big, P.AXIS_Z - 100, z))
    lo, hi = P.AXIS_Z - P.R_IN, P.AXIS_Z + P.R_IN
    for _ in range(18):
        mid = 0.5 * (lo + hi)
        v = below(mid).Volume / 1000.0
        if v < vol_ml:
            lo = mid
        else:
            hi = mid
    z = 0.5 * (lo + hi)
    return below(z), z


# ---------------- Stage B: outlet unit ----------------
def build_P2():
    X = P.OUT_X
    zlo, zhi = P.SEAT_Z - 1, P.AXIS_Z - 30
    prism = obround(P.FL_L, P.FL_W, X, 0, zlo, zhi)
    shell = ax_cyl(P.R_IN, X - 30, X + 30).cut(ax_cyl(P.FL_TOP_R, X - 31, X + 31))
    flange = prism.common(shell)
    stem = zcyl(P.STEM_OD / 2, P.SEAT_Z, P.AXIS_Z - 30, X).cut(ax_cyl(P.FL_TOP_R, X - 31, X + 31))
    flange = flange.fuse(stem).removeSplitter()          # fuse first: the top stays one smooth surface, then chamfer
    # rim chamfer on the top-face boundary edges (selected by position, not index): rim 0.4, ramp 1.5 long
    edges = []
    for e in flange.Edges:
        p = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
        r = math.hypot(p.y - P.AXIS_Y, p.z - P.AXIS_Z)
        if abs(r - P.FL_TOP_R) < 1e-3:
            edges.append(e)
    drop = (P.R_IN - P.FL_TOP_R) - P.FL_RIM_H            # 1.2 - 0.4 = 0.8 along the side face
    best = None
    for d1, d2 in ((drop, P.FL_RAMP_LEN), (P.FL_RAMP_LEN, drop)):
        try:
            c = flange.makeChamfer(d1, d2, edges)
        except Exception:
            continue
        if not c.isValid():
            continue
        rs = []
        for v in c.Vertexes:
            r = math.hypot(v.Point.y - P.AXIS_Y, v.Point.z - P.AXIS_Z)
            if P.FL_TOP_R + 0.05 < r < P.R_IN - 0.05:
                rs.append(r)
        if not rs:
            continue
        h = P.R_IN - sum(rs) / len(rs)                    # rim height above the wall (radial)
        if abs(h - P.FL_RIM_H) < 0.1 and (best is None or abs(h - P.FL_RIM_H) < best[0]):
            best = (abs(h - P.FL_RIM_H), c)
    if best is None:
        raise RuntimeError("P2 chamfer failed: no distance order gives a rim of %.1f" % P.FL_RIM_H)
    p2 = best[1].cut(zcyl(P.BORE_D / 2, P.SEAT_Z - 1, P.AXIS_Z - 30, X))
    return p2.removeSplitter()


def build_P3():
    X = P.OUT_X
    sad = ax_cyl(P.GK_R_OUT, X - 20, X + 20).cut(ax_cyl(P.GK_R_IN, X - 21, X + 21))
    g = sad.common(zcyl(P.GK_OD / 2, P.AXIS_Z - 50, P.AXIS_Z - 30, X))
    return g.cut(zcyl(P.GK_ID / 2, P.AXIS_Z - 50, P.AXIS_Z - 30, X)).removeSplitter()


def build_P4():
    X = P.OUT_X
    ztop = P.AXIS_Z - 30
    body = zcyl(P.PL_BODY_D / 2, P.SEAT_Z, ztop, X)
    wy = P.WEB_Y
    web_f = box(P.WEB_X[0], X, -wy, wy, P.SEAT_Z, P.SEAT_Z + P.WEB_T)
    web_r = box(X, P.WEB_X[1], -wy, wy, P.SEAT_Z, P.SEAT_Z + P.WEB_T)
    plate = body.cut(ax_cyl(P.PL_SADDLE_R, X - 40, X + 40)).fuse(web_f).fuse(web_r)
    # front latch lugs
    for y0, y1 in P.LUG_Y:
        plate = plate.fuse(box(P.LUG_X[0], P.LUG_X[1], y0, y1, P.LUG_BOTTOM_Z, P.SEAT_Z))
    # rear hinge knuckles (cylinder + web up to the plate web)
    hx, hz, r = P.HINGE_X, P.HINGE_Z, P.KNUCKLE_D / 2
    for y0, y1 in P.KNUCKLE_Y:
        plate = plate.fuse(ycyl(r, y0, y1, hx, hz)).fuse(box(hx - r, hx + r, y0, y1, hz, P.SEAT_Z + 0.5))
    # holes
    plate = plate.cut(zcyl(P.PL_HOLE_D / 2, P.SEAT_Z - 1, ztop, X))
    plate = plate.cut(zcyl(P.POCKET_D / 2, P.SEAT_Z - 1, P.SEAT_Z + P.POCKET_DEPTH, X))
    for (px, pz) in (P.REL_PIN_POS, P.SAF_PIN_POS):
        plate = plate.cut(ycyl(P.PIN_HOLE_D / 2, -12, 12, px, pz))
    plate = plate.cut(ycyl(P.HINGE_HOLE_D / 2, -12, 12, hx, hz))
    return plate.removeSplitter()


def build_P5():
    X = P.OUT_X
    z0 = P.SEAT_Z + P.NUT_GAP
    return zcyl(P.NUT_OD / 2, z0, z0 + P.NUT_T, X).cut(zcyl(P.NUT_ID / 2, z0 - 1, z0 + P.NUT_T + 1, X))


def build_P6():
    X = P.OUT_X
    zt, zb = P.FLAP_ZTOP, P.FLAP_ZBOT
    f = zcyl(P.FLAP_D / 2, zb, zt, X)
    f = f.fuse(box(P.TAB_X[0], P.TAB_X[1], -P.TAB_HALF_Y, P.TAB_HALF_Y, P.TAB_BOTTOM_Z, zt))
    hx, hz, r = P.HINGE_X, P.HINGE_Z, P.KNUCKLE_D / 2
    ky = P.FLAP_KNUCKLE_HALF_Y
    f = f.fuse(box(X + P.FLAP_D / 2 - 2, hx, -ky, ky, zb, zt)).fuse(ycyl(r, -ky, ky, hx, hz))
    # lightening: grid of pockets in the lower face, solid skin on top, rim ring, hook tab and knuckle zones kept
    pit = P.FLAP_RIB_PITCH
    side = pit - P.FLAP_RIB_W
    depth = P.FLAP_T - P.FLAP_SKIN
    n = int((P.FLAP_D / 2) // pit) + 1
    cells = [box(X + i * pit - side / 2, X + i * pit + side / 2, j * pit - side / 2, j * pit + side / 2, zb - 0.5, zb + depth)
             for i in range(-n, n + 1) for j in range(-n, n + 1)]
    pock = Part.makeCompound(cells).common(zcyl(P.FLAP_D / 2 - P.FLAP_RIM_W, zb - 1, zt, X))
    for (x0, x1, y0, y1) in P.FLAP_KEEP:
        pock = pock.cut(box(x0, x1, y0, y1, zb - 1, zt + 1))
    f = f.cut(pock)
    f = f.cut(box(X - 20, hx + 5, -20, 20, zt, zt + 5))        # knuckle top trimmed flat to the flap top (skin face prints flat on the bed)
    for (px, pz) in (P.REL_PIN_POS, P.SAF_PIN_POS):
        f = f.cut(ycyl(P.PIN_HOLE_D / 2, -6, 6, px, pz))
    f = f.cut(ycyl(P.HINGE_HOLE_D / 2, -6, 6, hx, hz))
    return f.removeSplitter()


def build_P7():
    X = P.OUT_X
    return zcyl(P.FGK_D / 2, P.FLAP_ZTOP, P.FLAP_ZTOP + P.FGK_T, X)


def build_P8():
    return ycyl(P.HP_D / 2, P.HP_Y[0], P.HP_Y[1], P.HINGE_X, P.HINGE_Z)


def _ring(cx, cy, cz, dia):
    return Part.makeTorus(dia / 2 - P.WIRE_D / 2, P.WIRE_D / 2, V(cx, cy, cz), V(0, 0, 1))


def build_P9(shift=0.0):
    px, pz = P.REL_PIN_POS
    y_ring_c = (P.RP_EYE_Y0 + P.RP_EYE_Y1) / 2
    pin = ycyl(P.RP_D / 2, P.RP_TIP_Y, P.RP_EYE_Y0 + P.WIRE_D / 2, px, pz)
    eye = _ring(px, y_ring_c, pz, P.RP_EYE_D)
    s = pin.fuse(eye).removeSplitter()
    s.translate(V(0, shift, 0))
    return s


def build_P10(shift=0.0):
    """Safety pin (steel). shift < 0 pulls it out to -Y."""
    px, pz = P.SAF_PIN_POS
    y_ring_c = (P.SP_RING_Y0 + P.SP_RING_Y1) / 2
    pin = ycyl(P.SP_D / 2, P.SP_STRAIGHT_END_Y - P.WIRE_D / 2, P.SP_TIP_Y, px, pz)
    ring = _ring(px, y_ring_c, pz, P.SP_RING_D)
    s = pin.fuse(ring).removeSplitter()
    s.translate(V(0, shift, 0))
    return s


def build_P10_flag(shift=0.0):
    px, pz = P.SAF_PIN_POS
    ly, wx, t = P.FLAG
    y1 = P.SP_RING_Y1
    s = box(px - wx / 2, px + wx / 2, y1 - ly, y1, pz - t / 2, pz + t / 2)
    s.translate(V(0, shift, 0))
    return s


def rotate_open(shape, angle):
    """Rotate about the hinge axis so that the flap front edge goes down and aft by `angle`."""
    s = shape.copy()
    s.rotate(V(P.HINGE_X, 0, P.HINGE_Z), V(0, 1, 0), -angle)
    return s


def belly_ref():
    """Floor / belly skin reference (pictures only): Z BELLY_Z .. +1.5, with the opening round P4/P6 and the pin slot."""
    slab = box(P.FLOOR_X[0], P.FLOOR_X[1], -P.FLOOR_HALF_Y, P.FLOOR_HALF_Y, P.BELLY_Z, P.BELLY_Z + P.BELLY_T)
    zz0, zz1 = P.BELLY_Z - 1, P.BELLY_Z + P.BELLY_T + 1
    r = P.FLOOR_HOLE_RECT
    slab = slab.cut(box(r[0], r[1], r[2], r[3], zz0, zz1))
    return slab.cut(zcyl(P.FLAP_D / 2 + 3.0, zz0, zz1, P.OUT_X)).removeSplitter()


def wing_ref():
    """SD7062 x 280, +3 deg nose up about the LE (TE goes down), extruded Y +-60. Reference only (check 6, pictures)."""
    pts = []
    for line in open(P.WING_DAT).read().splitlines()[1:]:
        t = line.split()
        if len(t) == 2:
            pts.append((float(t[0]), float(t[1])))
    vs = [V(x * P.WING_CHORD, -P.WING_HALF_SPAN, z * P.WING_CHORD) for x, z in pts]
    if (vs[0] - vs[-1]).Length > 0.05:
        vs.append(vs[0])
    else:
        vs[-1] = vs[0]
    face = Part.Face(Part.makePolygon(vs))
    s = face.extrude(V(0, 2 * P.WING_HALF_SPAN, 0))
    s.rotate(V(0, 0, 0), V(0, 1, 0), P.WING_INCIDENCE)       # +angle about +Y: x>0 goes down
    return s


# ---------------- R-C: fill unit (rev A.1) ----------------
def _rim_chamfer(body, face_r, wall_r):
    """Chamfer the boundary edges of the water-side face (cylinder radius face_r): rim 0.4, ramp 1.5 long. Edges chosen by position."""
    edges = []
    for e in body.Edges:
        p = e.valueAt((e.FirstParameter + e.LastParameter) / 2)
        if abs(math.hypot(p.y - P.AXIS_Y, p.z - P.AXIS_Z) - face_r) < 1e-3:
            edges.append(e)
    drop = (wall_r - face_r) - P.FL_RIM_H
    best = None
    for d1, d2 in ((drop, P.FL_RAMP_LEN), (P.FL_RAMP_LEN, drop)):
        try:
            c = body.makeChamfer(d1, d2, edges)
        except Exception:
            continue
        if not c.isValid():
            continue
        rs = [math.hypot(v.Point.y - P.AXIS_Y, v.Point.z - P.AXIS_Z) for v in c.Vertexes]
        rs = [r for r in rs if face_r + 0.05 < r < wall_r - 0.05]
        if rs:
            h = wall_r - sum(rs) / len(rs)
            if abs(h - P.FL_RIM_H) < 0.1 and (best is None or abs(h - P.FL_RIM_H) < best[0]):
                best = (abs(h - P.FL_RIM_H), c)
    if best is None:
        raise RuntimeError("fill flange chamfer failed")
    return best[1]


def build_fill():
    """Returns dict name -> shape (P11a..P11f)."""
    X = P.FILL_X_C
    Zc = P.AXIS_Z
    top = zcyl(P.F_FL_D / 2, Zc + 30, Zc + 45, X)
    shell = ax_cyl(P.R_IN, X - 30, X + 30).cut(ax_cyl(P.FL_TOP_R, X - 31, X + 31))
    flange = shell.common(top)
    stem = zcyl(P.F_STEM_OD / 2, Zc + 37, P.F_STEM_TOP_Z, X).cut(ax_cyl(P.FL_TOP_R, X - 31, X + 31))
    flange = flange.fuse(stem).removeSplitter()
    flange = _rim_chamfer(flange, P.FL_TOP_R, P.R_IN)
    flange = flange.cut(zcyl(P.F_BORE / 2, Zc + 30, P.F_STEM_TOP_Z + 1, X)).removeSplitter()
    gk = ax_cyl(P.GK_R_OUT, X - 20, X + 20).cut(ax_cyl(P.GK_R_IN, X - 21, X + 21))
    gk = gk.common(zcyl(P.F_GK_OD / 2, Zc + 30, Zc + 45, X)).cut(zcyl(P.F_GK_ID / 2, Zc + 30, Zc + 45, X)).removeSplitter()
    nut = zcyl(P.F_NUT_D / 2, Zc + 39, P.F_NUT_TOP_Z, X).cut(ax_cyl(P.GK_R_OUT, X - 20, X + 20))
    nut = nut.cut(zcyl(P.F_NUT_ID / 2, Zc + 30, Zc + 45, X)).removeSplitter()
    z0, z1, wall = P.F_CAP_Z0, P.F_CAP_Z1, P.F_CAP_WALL
    cap = zcyl(P.F_CAP_D / 2, z0, z1, X).cut(zcyl(P.F_CAP_ID / 2, z0 - 1, z1 - wall, X))
    holes = [zcyl(P.F_VHOLE_D / 2, z1 - wall - 0.5, z1 + 0.5, X)]
    for i in range(P.F_VHOLES):
        a = 2 * math.pi * i / P.F_VHOLES
        holes.append(zcyl(P.F_VHOLE_D / 2, z1 - wall - 0.5, z1 + 0.5, X + 0.5 * P.F_VHOLE_PCD * math.cos(a), 0.5 * P.F_VHOLE_PCD * math.sin(a)))
    for i in range(P.F_FLUTES):
        a = 2 * math.pi * i / P.F_FLUTES
        holes.append(zcyl(P.F_FLUTE_R, z0 + 0.5, z1 - 0.5, X + P.F_FLUTE_AT * math.cos(a), P.F_FLUTE_AT * math.sin(a)))
    cap = cap.cut(Part.makeCompound(holes)).removeSplitter()
    zs = P.F_STEM_TOP_Z
    seal = zcyl(P.F_SEAL_OD / 2, zs, zs + P.F_SEAL_T, X).cut(zcyl(P.F_SEAL_ID / 2, zs - 1, zs + P.F_SEAL_T + 1, X))
    zt = z1 - wall                                  # cap top wall underside
    flap = zcyl(P.F_FLAP_D / 2, zt - P.F_FLAP_T, zt, X)
    flap = flap.fuse(zcyl(P.F_FLAP_STEM_D / 2, zt - 0.1, z1 + 0.2, X)).fuse(zcyl(P.F_KNOB_D / 2, z1, z1 + P.F_KNOB_T, X)).removeSplitter()
    return dict(flange=flange, gasket=gk, nut=nut, cap=cap, seal=seal, flap=flap)


def build_funnel():
    """P15 funnel, neck at Z = FUN_NECK_Z above the fill stem, axis at X = FILL_X_C (picture position)."""
    X = P.FILL_X_C
    w = P.FUN_WALL
    ro = P.FUN_TOP_D / 2
    rs = P.FUN_SPOUT_OD / 2
    z0 = P.FUN_NECK_Z
    outer = Part.makeCone(rs, ro, P.FUN_H, V(X, 0, z0), V(0, 0, 1)).fuse(zcyl(rs, z0 - P.FUN_SPOUT_L, z0 + 0.5, X))
    inner = Part.makeCone(rs - w, ro - w, P.FUN_H, V(X, 0, z0), V(0, 0, 1)).fuse(zcyl(ro - w, z0 + P.FUN_H - 0.01, z0 + P.FUN_H + 1, X))
    inner = inner.fuse(zcyl(rs - w, z0 - P.FUN_SPOUT_L - 1, z0 + 0.5, X))
    f = outer.cut(inner)
    for sg in (1, -1):                                  # 2 external ribs on the spout so air leaves through the Ø10 bore
        rib = box(X + (rs - 0.01 if sg > 0 else -rs - P.FUN_RIB + 0.01), X + (rs + P.FUN_RIB if sg > 0 else -rs + 0.01), -0.75, 0.75, z0 - P.FUN_SPOUT_L, z0 - 1.0)
        f = f.fuse(rib)
    return f.removeSplitter()


def fuselage_top_ref():
    """Fuselage top deck with the Ø25 fill hole (picture only)."""
    s = box(P.FUSE_TOP_X[0], P.FUSE_TOP_X[1], -40, 40, P.FUSE_TOP_Z[0], P.FUSE_TOP_Z[1])
    return s.cut(zcyl(P.FUSE_HOLE_D / 2, P.FUSE_TOP_Z[0] - 1, P.FUSE_TOP_Z[1] + 1, P.FILL_X_C)).removeSplitter()


# ---------------- R-D: mount ----------------
def r_out_at(yu):
    """Outer radius of the bottle at yu from the base (interp. profile)."""
    prof = P.BOTTLE_PROFILE
    for a, b in zip(prof, prof[1:]):
        if yu <= b[0]:
            return a[1] + (b[1] - a[1]) * (yu - a[0]) / (b[0] - a[0])
    return prof[-1][1]


def _wedge(x0, x1, half_deg):
    R = 220.0
    t = math.tan(math.radians(half_deg))
    pts = [V(x0, 0, P.AXIS_Z), V(x0, R * math.sin(math.radians(half_deg)), P.AXIS_Z - R * math.cos(math.radians(half_deg))),
           V(x0, -R * math.sin(math.radians(half_deg)), P.AXIS_Z - R * math.cos(math.radians(half_deg)))]
    f = Part.Face(Part.makePolygon(pts + [pts[0]]))
    return f.extrude(V(x1 - x0, 0, 0))


def _sleeve_profile(base, yu0, yu1, off, thick):
    ys = [yu0] + [p[0] for p in P.BOTTLE_PROFILE if yu0 < p[0] < yu1] + [yu1]
    inner = [(y, r_out_at(y) + off) for y in ys]
    outer = [(y, r_out_at(y) + off + thick) for y in reversed(ys)]
    return inner + outer


def build_saddle(base, yu_rng, strap_rng):
    x0, x1 = base + yu_rng[0], base + yu_rng[1]
    xc = 0.5 * (x0 + x1)
    ring = revolve_profile(_sleeve_profile(base, yu_rng[0], yu_rng[1], P.SADDLE_GAP, P.SADDLE_WALL), base)
    sleeve = ring.common(_wedge(x0 - 1, x1 + 1, P.SADDLE_WRAP_DEG / 2))
    cav = revolve_profile([(y, 0) for y in (yu_rng[0],)] + [(y, r_out_at(y) + P.SADDLE_GAP) for y in
                          [yu_rng[0]] + [p[0] for p in P.BOTTLE_PROFILE if yu_rng[0] < p[0] < yu_rng[1]] + [yu_rng[1]]] + [(yu_rng[1], 0)], base)
    zf0, zf1 = P.FLOOR_Z, P.FLOOR_Z + P.FOOT_T
    web = box(x0, x1, -1.0, 1.0, zf1 - 0.01, P.AXIS_Z - 20).cut(cav)
    px0 = min(x0, base + strap_rng[0]); px1 = max(x1, base + strap_rng[1])
    beam = box(xc - P.FOOT_BEAM_W / 2, xc + P.FOOT_BEAM_W / 2, -P.FOOT_HALF_Y, P.FOOT_HALF_Y, zf0, zf1)
    pads = [box(px0, px1, P.FOOT_PAD_Y[0], P.FOOT_PAD_Y[1], zf0, zf1), box(px0, px1, -P.FOOT_PAD_Y[1], -P.FOOT_PAD_Y[0], zf0, zf1)]
    s = sleeve.fuse(web).fuse(beam).fuse(pads[0]).fuse(pads[1]).removeSplitter()
    return s


def build_strap(base, strap_rng):
    x0, x1 = base + strap_rng[0], base + strap_rng[1]
    ring = revolve_profile([(strap_rng[0], P.R_CYL), (strap_rng[1], P.R_CYL), (strap_rng[1], P.R_CYL + P.STRAP_T), (strap_rng[0], P.R_CYL + P.STRAP_T)], base)
    ring = ring.cut(_wedge(x0 - 1, x1 + 1, P.STRAP_END_DEG))
    s = ring
    ztop = P.FLOOR_Z + P.FOOT_T
    ty0, ty1 = P.STRAP_TAIL_Y
    for sg in (1, -1):
        ya, yb = sorted((sg * 36.5, sg * ty1))
        conn = box(x0, x1, ya, yb, -78.0, -76.9)
        ya2, yb2 = sorted((sg * ty0, sg * ty1))
        tail = box(x0, x1, ya2, yb2, ztop, -77.0)
        s = s.fuse(conn).fuse(tail)
    return s.removeSplitter()


def build_stop(base):
    x1 = base - P.STOP_GAP
    x0 = x1 - P.STOP_T
    s = box(x0, x1, -P.STOP_Y, P.STOP_Y, P.STOP_Z[0], P.STOP_Z[1])
    return s.cut(ax_cyl(P.STOP_HOLE_D / 2, x0 - 1, x1 + 1))


# ---------------- R-D: servo (T2-30: upright, inverted, shaft vertical pointing down) ----------------
def servo_shaft():
    return (P.SERVO_X_SHAFT, P.SERVO_Y_SHAFT)


def servo_body():
    S = P.MG90S
    L, W, H, HT = S["L"], S["W"], S["H"], S["H_TOP"]
    sx, sz = S["SHAFT_FROM_END"], W / 2
    case = box(0, L, 0, H, 0, W)
    ex = (S["TAB_L"] - L) / 2
    tabs = box(-ex, L + ex, S["TAB_Z"], S["TAB_Z"] + S["TAB_T"], 0, W)
    for xh in (L / 2 - S["TAB_HOLE_PITCH"] / 2, L / 2 + S["TAB_HOLE_PITCH"] / 2):
        tabs = tabs.cut(ycyl(2.0, S["TAB_Z"] - 1, S["TAB_Z"] + S["TAB_T"] + 1, xh, sz))
    boss = Part.makeCylinder(W / 2, HT - H, V(sx, H, sz), V(0, 1, 0)).fuse(box(sx, sx + 9, H, HT - 2.0, 1.0, W - 1.0))
    spline = Part.makeCylinder(S["SPLINE_D"] / 2, S["SPLINE_H"], V(sx, HT, sz), V(0, 1, 0))
    s = case.fuse([tabs, boss, spline]).removeSplitter()
    # local (lx along L, ly along the shaft, lz along W) -> global: X = lx + Xs - sx, Y = lz + Ys - sz, Z = Z_top - ly
    Z_top = P.ARM_Z_CENTER + HT + 0.7 + P.ARM_T / 2          # arm slab 0.7 beyond the boss top, as in the wing
    m = App.Matrix(1, 0, 0, P.SERVO_X_SHAFT - sx, 0, 0, 1, P.SERVO_Y_SHAFT - sz, 0, -1, 0, Z_top, 0, 0, 0, 1)
    return s.copy().transformGeometry(m)


def arm_tip(deg):
    a = math.radians(deg)
    return (P.SERVO_X_SHAFT - P.ARM_R * math.cos(a), P.SERVO_Y_SHAFT + P.ARM_R * math.sin(a))


def build_arm(deg=None):
    """Arm in the horizontal XY plane, slab centred at Z ARM_Z_CENTER."""
    deg = P.ARM_CLOSED_DEG if deg is None else deg
    xs, ys = servo_shaft()
    tx, ty = arm_tip(deg)
    z0 = P.ARM_Z_CENTER - P.ARM_T / 2
    hub = Part.makeCylinder(3.0, P.ARM_T, V(xs, ys, z0), V(0, 0, 1))
    tipc = Part.makeCylinder(P.ARM_W / 2, P.ARM_T, V(tx, ty, z0), V(0, 0, 1))
    d = V(tx - xs, ty - ys, 0); d.normalize()
    n = V(-d.y, d.x, 0)
    w = P.ARM_W / 2
    c = [V(xs, ys, z0) + n * w, V(tx, ty, z0) + n * w, V(tx, ty, z0) - n * w, V(xs, ys, z0) - n * w]
    bar = Part.Face(Part.makePolygon(c + [c[0]])).extrude(V(0, 0, P.ARM_T))
    arm = hub.fuse(bar).fuse(tipc)
    spl = Part.makeCylinder(P.MG90S["SPLINE_D"] / 2, 6.0, V(xs, ys, z0 - 2), V(0, 0, 1))
    return arm.cut(spl).removeSplitter()


def link_geometry(deg, L):
    """Snap-end Y for an arm angle with a wire of constant length L (wire in the plane Z = pin plane, snap end X = pin X)."""
    tx, ty = arm_tip(deg)
    dx = tx - P.REL_PIN_POS[0]
    return ty - math.sqrt(max(L * L - dx * dx, 0.0)), tx, ty


def build_link(deg=None, pull=0.0):
    """Snap (Y0..Y0+12 at the pin line, shifted by `pull`) and the wire from the snap end to the arm tip centre. Returns (snap, wire, length)."""
    px, pz = P.REL_PIN_POS
    y0 = P.SNAP_Y0 + pull
    snap = Part.makeCylinder(P.SNAP_D / 2, P.SNAP_L, V(px, y0, pz), V(0, 1, 0))
    tx, ty = arm_tip(P.ARM_CLOSED_DEG if deg is None else deg)
    e = V(px, y0 + P.SNAP_L, pz)
    t = V(tx, ty, pz)
    d = t - e
    L = d.Length
    d.normalize()
    wire = Part.makeCylinder(P.LINK_WIRE_D / 2, L, e, d)
    return snap, wire, L


# ---------------- pictures ----------------
VIEW_DIR = {   # look direction D of the camera (camera looks along D, up = +Z)
    "iso": (-1, 1, -1), "iso_low": (0.6, 0.7, 0.5), "iso_low_aft": (-0.6, 0.7, 0.5),
    "front": (0, 1, 0), "rear": (0, -1, 0), "from_fwd": (1, 0, 0), "top": (0, 0.0001, -1), "bottom": (0, 0.0001, 1),
}


def _set_view(v, name):
    import FreeCADGui as Gui
    D = V(*VIEW_DIR[name]); D.normalize()
    up = V(0, 0, 1)
    right = D.cross(up); right.normalize()
    u = right.cross(D); u.normalize()
    v.setCameraOrientation(App.Rotation(right, u, D * -1, "ZXY"))


SEC = {   # name -> (rgb, transparency %) for the pictures: each part its own colour, also on the cut faces
    "P1_Bottle": ((0.65, 0.82, 1.0), 70), "P1c_Cap": ((0.85, 0.85, 0.95), 0), "Water": ((0.15, 0.40, 0.95), 80),
    "P2_InnerFlange": ((0.95, 0.55, 0.10), 0), "P3_OuterGasket": ((0.10, 0.10, 0.10), 0), "P4_BasePlate": ((0.78, 0.78, 0.80), 0),
    "P5_Nut": ((0.20, 0.70, 0.30), 0), "P6_Flap": ((0.90, 0.10, 0.10), 0), "P7_FlapGasket": ((0.95, 0.85, 0.20), 0),
    "P8_HingePin": ((0.35, 0.45, 0.70), 0), "P9_ReleasePin": ((0.35, 0.45, 0.70), 0), "P10_SafetyPin": ((0.35, 0.45, 0.70), 0),
    "P10_Flag": ((0.95, 0.05, 0.05), 0), "P11a_FillFlange": ((0.95, 0.55, 0.10), 0), "P11b_FillGasket": ((0.10, 0.10, 0.10), 0),
    "P11c_FillNut": ((0.20, 0.70, 0.30), 0), "P11d_FillCap": ((0.60, 0.35, 0.80), 0), "P11e_CapSeal": ((0.95, 0.45, 0.65), 0),
    "P11f_VentFlap": ((0.10, 0.60, 0.60), 0), "P15_Funnel": ((0.75, 0.90, 0.75), 30), "Ref_FuselageTop": ((0.85, 0.85, 0.90), 50),
    "P12a_Saddle1": ((0.30, 0.70, 0.30), 0), "P12b_Saddle2": ((0.30, 0.70, 0.30), 0), "P13a_Strap1": ((0.10, 0.30, 0.15), 0),
    "P13b_Strap2": ((0.10, 0.30, 0.15), 0), "P12c_FrontStop": ((0.85, 0.70, 0.45), 0), "P14_Servo_MG90S": ((0.30, 0.30, 0.35), 0),
    "P14_ServoArm": ((0.85, 0.30, 0.65), 0), "P14_QuickSnap": ((0.35, 0.45, 0.70), 0), "P14_LinkWire": ((0.35, 0.45, 0.70), 0),
    "Ref_Wing": ((0.88, 0.88, 0.90), 60), "Ref_BellySkin": ((0.80, 0.70, 0.55), 40),
}


def snap(path, view, w=1600, h=1200, hide=(), only=None, section_box=None, zoom=1.0, extra=()):
    """Picture. only = set of object names to show (default all Part::Feature not hidden by `hide`).
    section_box = Part solid: temporary copies of the shown objects intersected with it are shown instead."""
    import FreeCADGui as Gui
    d = doc()
    App.setActiveDocument(d.Name)
    Gui.ActiveDocument = Gui.getDocument(d.Name)
    vis, tmp = {}, []
    feats = [o for o in d.Objects if o.TypeId == "Part::Feature"]
    for o in feats:
        vis[o.Name] = o.ViewObject.Visibility
    show = [o for o in feats if o.Name not in hide and (only is None or o.Name in only)]
    for o in feats:
        o.ViewObject.Visibility = False
        key = o.Name[:-5] if o.Name.endswith("_open") else o.Name
        if key in SEC:
            o.ViewObject.ShapeColor, o.ViewObject.Transparency = SEC[key][0], SEC[key][1]
    for nm, shp, rgb in extra:
        t = d.addObject("Part::Feature", "TMP_" + nm)
        t.Shape = shp
        t.ViewObject.ShapeColor = rgb
        t.ViewObject.Lighting = "Two side"
        tmp.append(t.Name)
    for o in show:
        if section_box is None:
            o.ViewObject.Visibility = True
            continue
        if not o.Shape.BoundBox.intersect(section_box.BoundBox):
            continue
        c = o.Shape.common(section_box)
        if c.isNull() or c.Volume < 1e-6:
            continue
        t = d.addObject("Part::Feature", "TMP_" + o.Name)
        t.Shape = c
        t.ViewObject.ShapeColor = o.ViewObject.ShapeColor
        t.ViewObject.Transparency = o.ViewObject.Transparency
        t.ViewObject.Lighting = "Two side"
        tmp.append(t.Name)
    v = Gui.ActiveDocument.ActiveView
    v.setCameraType("Orthographic")
    try:
        v.setAnimationEnabled(False)
    except Exception:
        pass
    _set_view(v, view)
    Gui.updateGui(); v.fitAll(); Gui.updateGui()
    if zoom != 1.0:
        import re
        cam = v.getCamera()
        m = re.search(r"height\s+([-0-9.eE+]+)", cam)
        if m:
            cam = cam[:m.start(1)] + "%.6f" % (float(m.group(1)) * zoom) + cam[m.end(1):]
            v.setCamera(cam)
        Gui.updateGui()
    v.saveImage(path, w, h, "White")
    for n in tmp:
        d.removeObject(n)
    for n, s in vis.items():
        if d.getObject(n):
            d.getObject(n).ViewObject.Visibility = s
    Gui.updateGui()
