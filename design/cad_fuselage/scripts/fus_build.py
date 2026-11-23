"""Fuselage rev A - helpers and geometry (FreeCAD, Part workbench). All numbers from fus_params (P).
This module never touches the document Reservoir_revA: it only reads shapes from it (copy_reservoir)."""
import math
import FreeCAD as App
import Part
from FreeCAD import Vector as V
import fus_params as P


# ---------------- document ----------------
def doc():
    """The fuselage document (created if not open). Never the reservoir document."""
    d = App.listDocuments().get(P.DOC)
    if d is None:
        d = App.newDocument(P.DOC)
    return d


def group(name):
    d = doc()
    g = d.getObject(name)
    if g is None:
        g = d.addObject("App::DocumentObjectGroup", name)
    return g


def clear_doc():
    """Remove every object of the fuselage document (full rebuild from scratch)."""
    d = doc()
    for o in list(d.Objects):
        if d.getObject(o.Name) is not None and o.TypeId != "App::DocumentObjectGroup":
            d.removeObject(o.Name)
    for o in list(d.Objects):
        d.removeObject(o.Name)


def put(name, shape, grp, color=(0.8, 0.8, 0.8), transp=0, props=None, visible=True):
    """One Part::Feature per part / reference body."""
    d = doc()
    if d.getObject(name) is not None:
        d.removeObject(name)
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
            o.ViewObject.Lighting = "Two side"
            o.ViewObject.Visibility = visible
        except Exception:
            pass
    return o


def mesh_bb(s, defl=0.05):
    """Tight extents from a tessellation (BoundBox is loose on B-spline faces). Returns (x0, x1, y0, y1, z0, z1)."""
    pts, _ = s.tessellate(defl)
    if not pts:
        bb = s.BoundBox
        return bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax
    return (min(p.x for p in pts), max(p.x for p in pts), min(p.y for p in pts), max(p.y for p in pts),
            min(p.z for p in pts), max(p.z for p in pts))


def info(name, s):
    b = mesh_bb(s)
    line = ("%-22s valid=%s solids=%d vol=%11.1f mm3  BB(mesh) X %.2f..%.2f Y %.2f..%.2f Z %.2f..%.2f"
            % (name, s.isValid(), len(s.Solids), s.Volume, b[0], b[1], b[2], b[3], b[4], b[5]))
    print(line)
    return line


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def frange(a, b, step):
    n = int(round((b - a) / step))
    return [a + (b - a) * i / n for i in range(n + 1)]


# ---------------- monotone cubic interpolation (Fritsch-Carlson PCHIP) ----------------
def _pchip_slopes(xs, ys):
    n = len(xs)
    h = [xs[i + 1] - xs[i] for i in range(n - 1)]
    d = [(ys[i + 1] - ys[i]) / h[i] for i in range(n - 1)]
    m = [0.0] * n
    for i in range(1, n - 1):
        if d[i - 1] * d[i] <= 0:
            m[i] = 0.0
        else:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])

    def end(h0, h1, d0, d1):
        s = ((2 * h0 + h1) * d0 - h0 * d1) / (h0 + h1)
        if s * d0 <= 0:
            return 0.0
        if d0 * d1 <= 0 and abs(s) > abs(3 * d0):
            return 3 * d0
        return s
    if n > 2:
        m[0] = end(h[0], h[1], d[0], d[1])
        m[-1] = end(h[-1], h[-2], d[-1], d[-2])
    else:
        m[0] = m[-1] = d[0]
    return m


def pchip(xs, ys, x):
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    m = _pchip_slopes(xs, ys)
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            h = xs[i + 1] - xs[i]
            t = (x - xs[i]) / h
            h00, h10, h01, h11 = 2 * t**3 - 3 * t**2 + 1, t**3 - 2 * t**2 + t, -2 * t**3 + 3 * t**2, t**3 - t**2
            return h00 * ys[i] + h10 * h * m[i] + h01 * ys[i + 1] + h11 * h * m[i + 1]
    return ys[-1]


def _knot(table, col, x):
    return pchip([k[0] for k in table], [k[col] for k in table], x)


def nose_sec(x):
    return dict(W=_knot(P.NOSE_KNOTS, 1, x), Zb=_knot(P.NOSE_KNOTS, 2, x), Zt=_knot(P.NOSE_KNOTS, 3, x),
                Rb=_knot(P.NOSE_KNOTS, 4, x), Rt=_knot(P.NOSE_KNOTS, 5, x))


def side_sec(x):
    """Half-width, bottom Z and bottom corner radius of the outer mould line at X."""
    if x < P.NOSE_END_X:
        s = nose_sec(x)
        return s["W"], s["Zb"], s["Rb"]
    if x <= P.AFT_X0:
        return P.CENTRE_W, P.BELLY_Z, P.CENTRE_RB
    return _knot(P.AFT_KNOTS, 1, x), _knot(P.AFT_KNOTS, 2, x), _knot(P.AFT_KNOTS, 3, x)


def t_side(x):
    return P.T_NOSE if x < P.NOSE_END_X else P.T_SIDE


def t_bottom(x):
    """Bottom-face thickness aft of X -35 (floor; aft-cone bottom from X AFT_X0)."""
    return P.T_FLOOR if x <= P.AFT_X0 else P.T_AFT_BOTTOM


# ---------------- wing (SD7062 x 280, B-spline as in the wing CAD, +3 deg) and the seat line ----------------
_W = {}


def _rot_matrix():
    m = App.Matrix()
    m.rotateY(math.radians(P.WING_INCIDENCE))      # +3 deg about +Y: x' = x cos + z sin, z' = -x sin + z cos
    return m


def airfoil():
    """Returns dict: bs (closed B-spline, chord 280, plane y = 0, not rotated), ule (LE parameter)."""
    if "bs" in _W:
        return _W
    raw = []
    for line in open(P.WING_DAT):
        s = line.split()
        if len(s) != 2:
            continue
        try:
            raw.append((float(s[0]), float(s[1])))
        except ValueError:
            continue
    pts = [V(min(x, 1.0) * P.WING_CHORD, 0, z * P.WING_CHORD) for x, z in raw]
    pts[-1] = V(pts[0])
    bs = Part.BSplineCurve()
    bs.interpolate(pts[:-1] + [pts[0]], PeriodicFlag=False)
    u0, u1 = bs.FirstParameter, bs.LastParameter
    us = [u0 + (u1 - u0) * i / 4000 for i in range(4001)]
    ule = min(us, key=lambda u: bs.value(u).x)
    _W.update(bs=bs, ule=ule, u0=u0, u1=u1)
    return _W


def wing_ref():
    """Ref_Wing: SD7062 x 280 extruded Y -495 .. +495, rotated +3 deg about +Y through the origin."""
    a = airfoil()
    bs = a["bs"]
    w = Part.Wire([bs.toShape(a["u0"], a["ule"]), bs.toShape(a["ule"], a["u1"])])
    f = Part.Face(w)
    f.translate(V(0, -P.WING_HALF_SPAN_REF, 0))
    s = f.extrude(V(0, 2 * P.WING_HALF_SPAN_REF, 0))
    s.rotate(V(0, 0, 0), V(0, 1, 0), P.WING_INCIDENCE)         # +angle about +Y: the TE goes down
    return s


def lower_curve(dz=0.0):
    """Wing lower surface (LE -> TE) after the +3 deg rotation, moved by dz in Z. Returns (curve, u_le, u_te)."""
    a = airfoil()
    c = a["bs"].copy()
    m = _rot_matrix()
    m.move(V(0, 0, dz))
    c.transform(m)
    return c, a["ule"], a["u1"]


def _u_at_x(c, ua, ub, x):
    lo, hi = ua, ub
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if c.value(mid).x < x:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def wing_lower_z(x):
    """Z of the wing lower surface at X (rotated wing)."""
    c, ua, ub = lower_curve(0.0)
    return c.value(_u_at_x(c, ua, ub, x)).z


def te_point():
    c, ua, ub = lower_curve(0.0)
    p = c.value(ub)
    return p.x, p.z


def seat_z(x):
    return wing_lower_z(x) - P.FOAM_T


def deck_z(x):
    xte, zte = te_point()
    return zte - P.FOAM_T + (P.DECK_END_Z - (zte - P.FOAM_T)) * (x - xte) / (P.POD_END_X - xte)


def top_line(x):
    """Defined top line of the pod (outer): nose top, hatch top, seat line (side-wall tops), aft deck."""
    xte, _ = te_point()
    if x < P.NOSE_END_X:
        return nose_sec(x)["Zt"]
    if x <= P.OPEN_X[0]:
        return P.HATCH_TOP_Z
    if x < P.SEAT_X[0]:
        z2 = seat_z(P.SEAT_X[0])
        return P.HATCH_TOP_Z + (z2 - P.HATCH_TOP_Z) * (x - P.OPEN_X[0]) / (P.SEAT_X[0] - P.OPEN_X[0])
    if x <= xte:
        return seat_z(x)
    return deck_z(x)


def deck_rt(x):
    return P.DECK_RT[0] + (P.DECK_RT[1] - P.DECK_RT[0]) * (x - P.OPEN_X[1]) / (P.POD_END_X - P.OPEN_X[1])


def seat_profile_prism():
    """XZ profile (top edge = side-wall top line from X -2: hatch top, ramp to the seat at X 2, seat curve =
    wing lower surface - FOAM_T, aft deck slope past X 280), extruded Y -100 .. +100. Used to cut the open region."""
    c, ua, ub = lower_curve(-P.FOAM_T)
    u2 = _u_at_x(c, ua, ub, P.SEAT_X[0])
    seat = c.toShape(u2, ub)
    p2, pte = c.value(u2), c.value(ub)
    x1 = P.OPEN_X[1] + 1.0
    pts_a = [V(P.OPEN_X[0] - 1.0, 0, -200), V(P.OPEN_X[0] - 1.0, 0, P.HATCH_TOP_Z), V(P.OPEN_X[0], 0, P.HATCH_TOP_Z), p2]
    edges = [Part.LineSegment(pts_a[i], pts_a[i + 1]).toShape() for i in range(3)]
    edges.append(seat)
    pe = V(x1, 0, deck_z(x1))
    edges += [Part.LineSegment(pte, pe).toShape(), Part.LineSegment(pe, V(x1, 0, -200)).toShape(),
              Part.LineSegment(V(x1, 0, -200), pts_a[0]).toShape()]
    f = Part.Face(Part.Wire(edges))
    f.translate(V(0, -100, 0))
    return f.extrude(V(0, 200, 0))


# ---------------- section wires (plane X = x) ----------------
def _arc(c, r, a0, a1, x):
    """Arc in the YZ plane about centre c = (y, z), from angle a0 to a1 (deg, 0 = +Y, 90 = +Z)."""
    pts = []
    for a in (a0, 0.5 * (a0 + a1), a1):
        t = math.radians(a)
        pts.append(V(x, c[0] + r * math.cos(t), c[1] + r * math.sin(t)))
    return Part.Arc(*pts).toShape()


def _line(p, q, x):
    return Part.LineSegment(V(x, p[0], p[1]), V(x, q[0], q[1])).toShape()


def rr_outer(x, W, Zb, Zt, Rb, Rt):
    """Rounded rectangle, 9 edges (bottom line split at Y 0), counter-clockwise seen from +X."""
    e = [_line((0, Zb), (W - Rb, Zb), x),
         _arc((W - Rb, Zb + Rb), Rb, -90, 0, x),
         _line((W, Zb + Rb), (W, Zt - Rt), x),
         _arc((W - Rt, Zt - Rt), Rt, 0, 90, x),
         _line((W - Rt, Zt), (-(W - Rt), Zt), x),
         _arc((-(W - Rt), Zt - Rt), Rt, 90, 180, x),
         _line((-W, Zt - Rt), (-W, Zb + Rb), x),
         _arc((-(W - Rb), Zb + Rb), Rb, 180, 270, x),
         _line((-(W - Rb), Zb), (0, Zb), x)]
    return Part.Wire(e)


def rr_inner(x, W, Zb, Rb, ts, tf, zt_in, rt_in):
    """Inner section, 11 edges: floor tf with a bottom corner concentric to the outer one (radius Rb - tf, so the
    corner is tf thick everywhere), a transition line (W - tf -> W - ts over TRANS_H), side walls ts, top corner
    radius rt_in with its top at zt_in."""
    rb = Rb - tf
    cy, cz = W - Rb, Zb + Rb
    ztr = cz + P.TRANS_H
    yi = W - ts
    ct = (yi - rt_in, zt_in - rt_in)
    e = [_line((0, Zb + tf), (cy, Zb + tf), x),
         _arc((cy, cz), rb, -90, 0, x),
         _line((W - tf, cz), (yi, ztr), x),
         _line((yi, ztr), (yi, ct[1]), x),
         _arc(ct, rt_in, 0, 90, x),
         _line((ct[0], zt_in), (-ct[0], zt_in), x),
         _arc((-ct[0], ct[1]), rt_in, 90, 180, x),
         _line((-yi, ct[1]), (-yi, ztr), x),
         _line((-yi, ztr), (-(W - tf), cz), x),
         _arc((-cy, cz), rb, 180, 270, x),
         _line((-cy, Zb + tf), (0, Zb + tf), x)]
    return Part.Wire(e)


def nose_xs():
    return frange(P.FIREWALL_X, P.NOSE_END_X, P.NOSE_LOFT_DX)


def open_xs():
    return [P.OPEN_X[0]] + frange(P.AFT_X0, P.OPEN_X[1], P.AFT_LOFT_DX)


def deck_xs(x_end):
    return frange(P.OPEN_X[1], x_end, (x_end - P.OPEN_X[1]) / 4.0)


# ---------------- outer mould line and shell ----------------
def oml_pieces():
    """Outer mould line pieces: nose loft, hatch prism, open region (ruled loft cut by the seat profile), aft deck."""
    nose = Part.makeLoft([rr_outer(x, **nose_sec(x)) for x in nose_xs()], True, False)
    x0, x1 = P.NOSE_END_X, P.OPEN_X[0]
    hatch = Part.Face(rr_outer(x0, P.CENTRE_W, P.BELLY_Z, P.HATCH_TOP_Z, P.CENTRE_RB, P.NOSE_KNOTS[-1][5])).extrude(V(x1 - x0, 0, 0))
    secs = []
    for x in open_xs():
        W, Zb, Rb = side_sec(x)
        secs.append(rr_outer(x, W, Zb, P.HIGH_ZT, Rb, P.HIGH_RT))
    open_raw = Part.makeLoft(secs, True, True)
    open_cut = open_raw.common(seat_profile_prism())
    dsecs = []
    for x in deck_xs(P.POD_END_X):
        W, Zb, Rb = side_sec(x)
        dsecs.append(rr_outer(x, W, Zb, deck_z(x), Rb, deck_rt(x)))
    deck = Part.makeLoft(dsecs, True, True)
    return dict(nose=nose, hatch=hatch, open=open_cut, deck=deck)


def inner_pieces():
    t = P.T_NOSE
    ns = []
    for x in nose_xs():
        s = nose_sec(x)
        ns.append(rr_outer(x, s["W"] - t, s["Zb"] + t, s["Zt"] - t, s["Rb"] - t, s["Rt"] - t))
    nose = Part.makeLoft(ns, True, False)
    front = Part.Face(ns[0]).extrude(V(-1.0, 0, 0))            # open front at the firewall (insert in F-B)
    x0, x1 = P.NOSE_END_X, P.OPEN_X[0]
    rt_h = P.NOSE_KNOTS[-1][5] - P.T_HATCH_TOP
    hatch = Part.Face(rr_inner(x0, P.CENTRE_W, P.BELLY_Z, P.CENTRE_RB, P.T_SIDE, P.T_FLOOR,
                               P.HATCH_TOP_Z - P.T_HATCH_TOP, rt_h)).extrude(V(x1 - x0, 0, 0))
    secs = []
    for x in open_xs():
        W, Zb, Rb = side_sec(x)
        secs.append(rr_inner(x, W, Zb, Rb, P.T_SIDE, t_bottom(x), P.INNER_HIGH_ZT, P.INNER_HIGH_RT))
    open_in = Part.makeLoft(secs, True, True)
    dsecs = []
    for x in deck_xs(P.POD_END_X - P.T_END):
        W, Zb, Rb = side_sec(x)
        dsecs.append(rr_inner(x, W, Zb, Rb, P.T_SIDE, t_bottom(x), deck_z(x) - P.T_SIDE, max(deck_rt(x) - P.T_SIDE, 0.3)))
    deck = Part.makeLoft(dsecs, True, True)
    return dict(nose=nose, front=front, hatch=hatch, open=open_in, deck=deck)


def common_robust(a, b):
    """a ∩ b. OCC 'common' returns an empty result without an error for some loft solids (F3: BOP TooSmallEdge / C0
    edges), while 'cut' works. If 'common' gives nothing but the shapes touch, use a - (a - b)."""
    if not a.BoundBox.intersect(b.BoundBox):
        return Part.makeCompound([])
    c = a.common(b)
    if (c.isNull() or c.Volume < 1e-6) and a.distToShape(b)[0] < 1e-7:
        c = a.cut(a.cut(b))
    return c


OVL_FLAGS = []          # pairs where 'common' gave 0 but the point test found penetration (see ovl)


def _pts_in_box(s, bb, defl=2.0, nmax=300):
    pts, _ = s.tessellate(defl)
    pts = [p for p in pts if bb.isInside(p)]
    pts += [v.Point for v in s.Vertexes if bb.isInside(v.Point)]
    if len(pts) > nmax:
        k = len(pts) / float(nmax)
        pts = [pts[int(i * k)] for i in range(nmax)]
    return pts


def ovl(a, b):
    """Overlap volume (mm3). 0 for a real gap (distToShape > 0). For contact: 'common'; if 'common' gives 0
    (touching faces, or a silent OCC failure: F3 between X 175 and 200), a point test looks for surface points of
    either shape strictly inside the other (touching faces give none). A penetration found only by the point test
    returns 1.0 mm3 (flag) and is listed in OVL_FLAGS."""
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    if a.distToShape(b)[0] > 1e-6:
        return 0.0
    c = a.common(b)
    v = 0.0 if c.isNull() else c.Volume
    if v > 1e-3:
        return v
    bb = App.BoundBox(a.BoundBox)
    bb = bb.intersected(b.BoundBox)
    bb.enlarge(0.01)
    for p in _pts_in_box(b, bb):
        if a.isInside(p, 1e-3, False):
            OVL_FLAGS.append((a.BoundBox, b.BoundBox, p))
            return 1.0
    for p in _pts_in_box(a, bb):
        if b.isInside(p, 1e-3, False):
            OVL_FLAGS.append((a.BoundBox, b.BoundBox, p))
            return 1.0
    return v


def fuse_all(shapes):
    s = shapes[0].fuse(shapes[1:])
    return s.removeSplitter()


def belly_hole():
    r = P.FLOOR_HOLE_RECT
    return box(r[0], r[1], r[2], r[3], P.BELLY_Z - 10, 30)


def hatch_region():
    """Region of the hatch F4: X HATCH_X, from HATCH_DEPTH below the top line up to Z +30, Y -100 .. +100."""
    xa, xb = P.HATCH_X
    xs = frange(xa, P.NOSE_END_X, 2.5)
    bpts = [V(x, 0, top_line(x) - P.HATCH_DEPTH) for x in xs]
    bs = Part.BSplineCurve()
    bs.interpolate(bpts)
    zf = P.HATCH_TOP_Z - P.HATCH_DEPTH
    e = [bs.toShape(), Part.LineSegment(bpts[-1], V(xb, 0, zf)).toShape(),
         Part.LineSegment(V(xb, 0, zf), V(xb, 0, 30)).toShape(), Part.LineSegment(V(xb, 0, 30), V(xa, 0, 30)).toShape(),
         Part.LineSegment(V(xa, 0, 30), bpts[0]).toShape()]
    f = Part.Face(Part.Wire(e))
    f.translate(V(0, -100, 0))
    return f.extrude(V(0, 200, 0))


def split_boxes():
    a, b = P.SPLIT_X
    return dict(F1_PodNose=box(-400, a, -150, 150, -200, 100), F2_PodCentre=box(a, b, -150, 150, -200, 100),
                F3_PodAft=box(b, 500, -150, 150, -200, 100))


def _ok(name, s):
    """Each step: valid, one solid (raise if not)."""
    info(name, s)
    if not s.isValid() or len(s.Solids) != 1:
        raise RuntimeError("%s: valid=%s, %d solids (expected 1 valid solid)" % (name, s.isValid(), len(s.Solids)))
    return s


def build_pod():
    """Returns dict of shapes: OML, inner, shell, parts F1..F4 and the pieces. Prints info lines."""
    import time
    t0 = time.time()
    op = oml_pieces()
    for k, s in op.items():
        _ok("oml_" + k, s)
    oml = _ok("OML", fuse_all([op["nose"], op["hatch"], op["open"], op["deck"]]))
    ip = inner_pieces()
    for k, s in ip.items():
        _ok("inner_" + k, s)
    inner = _ok("Inner", fuse_all([ip["nose"], ip["front"], ip["hatch"], ip["open"], ip["deck"]]))
    shell = _ok("shell", oml.cut(inner).removeSplitter())
    shell = _ok("shell_belly_hole", shell.cut(belly_hole()).removeSplitter())
    hr = hatch_region()
    f4 = _ok("F4_NoseHatch", shell.common(hr).removeSplitter())
    rest = _ok("pod_rest", shell.cut(hr).removeSplitter())
    parts = {"F4_NoseHatch": f4}
    for n, bx in split_boxes().items():
        parts[n] = _ok(n, rest.common(bx).removeSplitter())
    print("pod build time %.1f s" % (time.time() - t0))
    return dict(oml=oml, inner=inner, shell=shell, parts=parts, oml_pieces=op, inner_pieces=ip)


# ---------------- reservoir reference bodies ----------------
def copy_reservoir():
    """Copies of the reservoir shapes: {name: (shape, rgb or None, open_state)}. Reads Reservoir_revA (open in the
    GUI) without any change; if it is not open, opens the FCStd hidden and closes it again without saving."""
    rd = App.listDocuments().get(P.RES_DOC)
    opened = False
    if rd is None:
        try:
            rd = App.openDocument(P.RES_FCSTD, hidden=True)
        except TypeError:
            rd = App.openDocument(P.RES_FCSTD)
        opened = True
    out = {}
    try:
        for o in rd.Objects:
            if o.TypeId != "Part::Feature" or o.Name.startswith(P.RES_SKIP_PREFIX):
                continue
            rgb = None
            if App.GuiUp:
                try:
                    rgb = tuple(o.ViewObject.ShapeColor[:3])
                except Exception:
                    rgb = None
            out[o.Name] = (o.Shape.copy(), rgb, o.Name.endswith("_open"))
    finally:
        if opened:
            App.closeDocument(rd.Name)
    return out


# ---------------- pictures ----------------
VIEW_DIR = {   # look direction of the camera (up = +Z)
    "iso": (-1, 1, -1), "iso_low": (0.6, 0.7, 0.5), "iso_aft": (1, 1, -1),
    "front": (0, 1, 0), "rear": (0, -1, 0), "from_fwd": (1, 0, 0), "top": (0, 0.0001, -1), "bottom": (0, 0.0001, 1),
}


def _set_view(v, name):
    D = V(*VIEW_DIR[name]); D.normalize()
    up = V(0, 0, 1)
    right = D.cross(up); right.normalize()
    u = right.cross(D); u.normalize()
    v.setCameraOrientation(App.Rotation(right, u, D * -1, "ZXY"))


def snap(path, view, only, section_box=None, extra=(), w=1600, h=1200, zoom=1.0):
    """Picture of the fuselage document. only = names to show; section_box = solid: temporary TMP_ copies of the shown
    objects intersected with it are shown instead (deleted afterwards). extra = [(name, shape, rgb)] temporary bodies."""
    import FreeCADGui as Gui
    d = doc()
    App.setActiveDocument(d.Name)
    gd = Gui.getDocument(d.Name)
    feats = [o for o in d.Objects if o.TypeId == "Part::Feature"]
    vis = {o.Name: o.ViewObject.Visibility for o in feats}
    tmp = []
    for o in feats:
        o.ViewObject.Visibility = False
    for ex in extra:
        nm, shp, rgb = ex[:3]
        t = d.addObject("Part::Feature", "TMP_" + nm)
        t.Shape = shp
        t.ViewObject.ShapeColor = rgb
        t.ViewObject.Transparency = int(ex[3]) if len(ex) > 3 else 0
        if t.ViewObject.Transparency == 0:
            t.ViewObject.LineColor = rgb          # limit lines: no black edges (transparent bodies keep their outline)
        t.ViewObject.Lighting = "Two side"
        tmp.append(t.Name)
    for o in feats:
        if o.Name not in only:
            continue
        if section_box is None:
            o.ViewObject.Visibility = True
            continue
        if not o.Shape.BoundBox.intersect(section_box.BoundBox):
            continue
        c = common_robust(o.Shape, section_box)
        if c.isNull() or c.Volume < 1e-6:
            continue
        t = d.addObject("Part::Feature", "TMP_" + o.Name)
        t.Shape = c
        t.ViewObject.ShapeColor = o.ViewObject.ShapeColor
        t.ViewObject.Transparency = o.ViewObject.Transparency
        t.ViewObject.Lighting = "Two side"
        tmp.append(t.Name)
    v = gd.ActiveView
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
