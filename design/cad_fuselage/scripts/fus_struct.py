"""Fuselage rev A - pod internal structure (stage F-S): printed ribs, frames, cross bars and skin windows.

Owner: structure side session (study: design/cad_fuselage/structure/structure_study.md, notebook
design/logs/fuselage_structure_log.md, decision D-060). The fuselage session integrates it after review.

Use (FreeCAD, Part workbench, after the F-A / F-B pod parts exist):
    import fus_struct as S
    new_parts, report = S.apply({"F1_PodNose": f1, "F2_PodCentre": f2, "F3_PodAft": f3})
`apply` fuses the rib / frame / bar solids into the part that contains them and cuts the windows from the skin.
It never changes F4 (hatch). All positions come from fus_params (P) and fus_build (B); section 13 values are not
typed here. Keep-outs (task, D-046, D-054, D-059): no member across the top opening X -27..231 (bottle lift-out),
nothing in the battery path of the nose (floor |Y| < 22 over X -165..-35), no window in the belly, the aft-cone
bottom, the grip zone X 35..125, the servo-wall pocket, the band-stub bosses, the flag hole, the socket block,
the split joints and the lip band. Windows: diamonds with edges at +-45 deg (support-free in any print
orientation), corners cut 3 mm; cover with self-adhesive clear film (D-060).
Frame: wing frame, mm (origin wing LE on the centreline, X aft, Y right, Z up)."""
import math
import FreeCAD as App  # noqa: F401
import Part
from FreeCAD import Vector as V
import fus_params as P
import fus_build as B

# ============================ parameters (tier 2 values; reasons in the study, section 6) ============================
PAR = dict(
    RIB_T=0.8,              # rib / frame / stringer thickness (2 lines of a 0.4 nozzle)
    RIB_H=5.0,              # depth of the wall diagrid ribs and the wall stringer (normal to the skin)
    Z_LO=-104.0,            # lower wall stringer (centre); everywhere at least NOSE_LO above the bottom-corner tangent
    NOSE_LO=6.0,
    STR_SLOPE=45.0,         # lower wall stringer slopes down-inward at 45 deg (no flat overhang in any orientation)
    LIP=(8.0, 0.8),         # seat lip (width, thickness) X -2..280 (plan 04 section 3; F-B feature, modelled)
    LEDGE=(6.0, 0.8),       # nose hatch-seat ledge (width, thickness) X -165..-2 (key check 12)
    # ring ribs only in F2 (printed belly down: a ring rib is a vertical wall there). F1 and F3 print on their split
    # faces (layers normal to X), where a flat ring rib would be a 6 mm horizontal overhang.
    FRAMES=[(40.0, 6.0, 0.8), (80.0, 6.0, 0.8), (120.0, 6.0, 0.8)],
    # cross bars at the wall-top level: V-struts in the XY plane (45 deg to X: support-free in F1 / F3)
    BARS=[dict(x=236.0, w=6.0, t=1.2), dict(x=-40.0, w=6.0, t=1.2)],
    # side-wall bays: diagrid lattice and windows sized per bay (p = perpendicular spacing of the +-45 deg ribs)
    BAYS=[dict(x=(-165.0, -27.7), win=(-158.0, -36.0), p=30.0),     # F1 nose
          dict(x=(-27.7, 40.0), win=(-18.0, 34.0), p=30.0),         # F2 front
          dict(x=(40.0, 120.0), win=None, p=30.0),                  # F2 launch grip (ribs, no windows)
          dict(x=(120.0, 175.0), win=(125.0, 167.0), p=30.0),       # F2 rear
          dict(x=(175.0, 233.0), win=(183.0, 228.0), p=30.0)],      # F3 aft
    FLOOR_STR=[(31.0, 3.5)],          # floor stringers at |Y| (height); belly opening edge 20, servo case from Y 38.8
    FLOOR_X=(-27.0, 233.0),
    RIM=(4.0, 3.5),                   # rib round the belly opening: offset from the opening edge, height
    RELIEF_R=4.0,                     # corner reliefs of the belly opening (circle on each corner, outside the opening)
    LAND=7.0,                         # skin land between a window and the rib centre line (2 x 3.5)
    WIN_CUT=3.0,                      # window corner cut
    WIN_TOP_BAND=11.0,                # no window within this distance of the wall top (lip / ledge band)
    WIN_BOT_BAND=5.0,                 # no window within this distance above the lower stringer
    KO_CIRCLES=[(-6.0, -24.0, 15.0), (295.0, -22.0, 12.0), (54.0, -110.5, 12.0)],   # stub bosses, rear dowel, flag hole
    KO_BOXES=[(35.0, 125.0, -200.0, 50.0),       # launch grip X 35..125 (D-054), contains the D-059 pocket X 52..77
              (-36.0, -20.0, -200.0, 50.0),      # front stop slot / joint former band
              (167.0, 183.0, -200.0, 50.0),      # split joint X 175 +- 8
              (228.0, 400.0, -200.0, 50.0),      # socket block
              (-400.0, -158.0, -200.0, 50.0)],   # firewall frame
    WINDOWS=True,
)
DIAGRID_X = (-165.0, 233.0)       # side-wall structure from the firewall frame to the socket bulkhead
SIDES = (-1, 1)


# ============================ helpers ============================
def W_of(x):
    return B.side_sec(x)[0]


def top_skin(x):
    z = B.top_line(x)
    if P.HATCH_X[0] <= x <= P.HATCH_X[1]:
        z -= P.HATCH_DEPTH
    return z


def z_low(x, par=PAR):
    """Lower edge of the side-wall structure (lower stringer root) at X."""
    W, zb, rb = B.side_sec(x)
    return max(par["Z_LO"], zb + rb + par["NOSE_LO"])


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def oml_solid():
    op = B.oml_pieces()
    return B.fuse_all([op["nose"], op["hatch"], op["open"], op["deck"]])


def _clip_segment(p, d, xmin, xmax, zlo, zhi, n=200):
    """Clip the line p + s d (chart X, Z) to xmin <= X <= xmax, zlo(X) <= Z <= zhi(X); returns [(p0, p1)] pieces."""
    smin = min((xmin - p[0]) / d[0], (xmax - p[0]) / d[0])
    smax = max((xmin - p[0]) / d[0], (xmax - p[0]) / d[0])
    segs, cur = [], None
    for i in range(n + 1):
        s = smin + (smax - smin) * i / n
        x, z = p[0] + s * d[0], p[1] + s * d[1]
        ok = zlo(x) <= z <= zhi(x)
        if ok and cur is None:
            cur = [(x, z), (x, z)]
        elif ok:
            cur[1] = (x, z)
        elif cur is not None:
            segs.append(tuple(cur))
            cur = None
    if cur is not None:
        segs.append(tuple(cur))
    return [s for s in segs if math.hypot(s[1][0] - s[0][0], s[1][1] - s[0][1]) > 4.0]


# ============================ layout (pure geometry, shared by the CAD and the FEM) ============================
def layout(par=PAR):
    """Abstract layout per side-wall bay: diagrid segments and windows in chart coordinates (X, Z), same on both
    sides. Each bay has its own lattice, centred on the window band (or the bay)."""
    segs, wins = [], []
    zlo = lambda x: z_low(x, par)
    for bay in par["BAYS"]:
        p = bay["p"]
        q = p * math.sqrt(2.0)                        # diagonal of a cell (X and Z extent)
        xa, xb = bay["x"]
        wa, wb = bay["win"] if bay["win"] else bay["x"]
        xr = 0.5 * (wa + wb)
        lo = zlo(xr) + par["WIN_BOT_BAND"]
        hi = top_skin(xr) - par["WIN_TOP_BAND"]
        zr = 0.5 * (lo + hi)                          # a row of cell centres on the middle of the window band
        for fam in (1, -1):                           # Z - zr - fam (X - xr) = q/2 + k q
            for k in range(-12, 13):
                c = q / 2.0 + k * q
                for s0, s1 in _clip_segment((xr, zr + c), (1.0, float(fam)), xa, xb, zlo, top_skin):
                    segs.append((s0, s1))
        if par["WINDOWS"] and bay["win"]:
            half = q / 2.0 - par["LAND"] / math.sqrt(2.0)
            for i in range(-12, 13):
                for j in range(-4, 5):
                    if (i + j) % 2:
                        continue
                    cx, cz = xr + i * q / 2.0, zr + j * q / 2.0
                    if _window_ok(cx, cz, half, bay, par):
                        poly = _cut_diamond(cx, cz, half, par["WIN_CUT"])
                        wins.append(dict(cx=cx, cz=cz, half=half, poly=poly, bay=bay["x"]))
    return dict(segs=segs, wins=wins, frames=par["FRAMES"], floor=par["FLOOR_STR"])


def _cut_diamond(cx, cz, h, c):
    """Diamond (half diagonal h) with each corner cut by c along both edges (octagon)."""
    pts = []
    corners = [(cx + h, cz), (cx, cz - h), (cx - h, cz), (cx, cz + h)]
    for i, (x, z) in enumerate(corners):
        a = corners[i - 1]
        b = corners[(i + 1) % 4]
        for (u, w) in (a, b):
            L = math.hypot(u - x, w - z)
            pts.append((x + (u - x) * c / L, z + (w - z) * c / L))
    # order: for each corner: towards previous, towards next
    return pts


def _window_ok(cx, cz, half, bay, par):
    wa, wb = bay["win"]
    if cx - half < wa or cx + half > wb:
        return False
    for x, zz in ((cx, (cz - half, cz + half)), (cx - half, (cz, cz)), (cx + half, (cz, cz)),
                  (cx - half / 2, (cz - half / 2, cz + half / 2)), (cx + half / 2, (cz - half / 2, cz + half / 2))):
        if zz[0] < z_low(x, par) + par["WIN_BOT_BAND"] or zz[1] > top_skin(x) - par["WIN_TOP_BAND"]:
            return False
    for x, z, r in par["KO_CIRCLES"]:
        if abs(cx - x) + abs(cz - z) < half + r * math.sqrt(2.0):       # diamond (L1 ball) against the circle
            return False
    for x0, x1, z0, z1 in par["KO_BOXES"]:
        if cx + half > x0 and cx - half < x1 and cz + half > z0 and cz - half < z1:
            return False
    return True


# ============================ member faces (mid-surfaces) ============================
def _ruled_wall(seg, side, depth, out=2.0, n=12):
    """Rib surface on a side wall: between the chart segment pushed out of the skin and pulled in by `depth`
    (later trimmed by the OML, so its outer edge lies exactly on the skin)."""
    (x0, z0), (x1, z1) = seg
    po, pi = [], []
    for i in range(n + 1):
        t = i / n
        x, z = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t
        W = W_of(x)
        po.append(V(x, side * (W + out), z))
        pi.append(V(x, side * (W - depth), z))
    e1 = Part.BSplineCurve()
    e1.interpolate(po)
    e2 = Part.BSplineCurve()
    e2.interpolate(pi)
    return Part.makeRuledSurface(e1.toShape(), e2.toShape())


def diagrid_faces(oml, lay, par=PAR):
    out = []
    for s in SIDES:
        for seg in lay["segs"]:
            f = _ruled_wall(seg, s, par["RIB_H"]).common(oml)
            if f.Area > 1.0:
                out.append(f)
    return out


def stringer_faces(oml, par=PAR):
    """Lower wall stringers on both walls: root on the skin at z_low(X), sloping down-inward at STR_SLOPE."""
    out = []
    xa, xb = DIAGRID_X
    xs = [xa + (xb - xa) * i / 160 for i in range(161)]
    for s in SIDES:
        a = math.radians(par["STR_SLOPE"])
        h = par["RIB_H"]
        po = [V(x, s * (W_of(x) + 2.0), z_low(x, par) + 2.0 * math.tan(a)) for x in xs]
        pi = [V(x, s * (W_of(x) - h * math.cos(a)), z_low(x, par) - h * math.sin(a)) for x in xs]
        e1 = Part.BSplineCurve()
        e1.interpolate(po)
        e2 = Part.BSplineCurve()
        e2.interpolate(pi)
        f = Part.makeRuledSurface(e1.toShape(), e2.toShape()).common(oml)
        out.append(f)
    return out


def floor_faces(oml, par=PAR):
    out = []
    x0, x1 = par["FLOOR_X"]
    for yv, h in par["FLOOR_STR"]:
        for s in SIDES:
            r = Part.Face(Part.Wire(Part.makePolygon([V(x0, s * yv, P.BELLY_Z - 3), V(x1, s * yv, P.BELLY_Z - 3),
                                                      V(x1, s * yv, P.BELLY_Z + 0.8 + h), V(x0, s * yv, P.BELLY_Z + 0.8 + h),
                                                      V(x0, s * yv, P.BELLY_Z - 3)])))
            out.append(r.common(oml))
    # rim round the belly opening
    hx0, hx1, hy0, hy1 = P.FLOOR_HOLE_RECT
    o, h = par["RIM"]
    pts = [(hx0 - o, hy0 - o), (hx1 + o, hy0 - o), (hx1 + o, hy1 + o), (hx0 - o, hy1 + o), (hx0 - o, hy0 - o)]
    for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
        r = Part.Face(Part.Wire(Part.makePolygon([V(xa, ya, P.BELLY_Z - 3), V(xb, yb, P.BELLY_Z - 3), V(xb, yb, P.BELLY_Z + 0.8 + h),
                                                  V(xa, ya, P.BELLY_Z + 0.8 + h), V(xa, ya, P.BELLY_Z - 3)])))
        out.append(r.common(oml))
    return out


def section_face(oml, x):
    ws = oml.slice(V(1, 0, 0), x)
    fs = [Part.Face(w) for w in ws if w.isClosed()]
    fs.sort(key=lambda f: -f.Area)
    return fs[0]


def frame_faces(oml, par=PAR):
    """Ring ribs (open top, D-046) at the F2 stations."""
    out = []
    for x, d, t in par["FRAMES"]:
        sf = section_face(oml, x)
        rib = sf.cut(sf.makeOffset2D(-d))
        zt = top_skin(x)
        W = W_of(x)
        rib = rib.cut(box(x - 1, x + 1, -(W - d - 0.05), W - d - 0.05, zt - d - 0.05, 50))
        rib = rib.cut(box(x - 1, x + 1, -100, 100, zt, 100))
        out.append((x, t, rib))
    return out


def bar_faces(oml, par=PAR):
    """Cross bars at the wall-top level, as V-struts in the horizontal plane: from each wall top at X = x to the
    centreline at X = x + W/2 (aft bar) or x - W/2 (nose bar, pointing away from the battery bay). Mid-surface
    3 mm below the wall top; width w in Z, thickness t."""
    out = []
    for b in par["BARS"]:
        x, w = b["x"], b["w"]
        zt = top_skin(x)
        W = W_of(x)
        sgn = 1.0 if x > 0 else -1.0
        tip = V(x + sgn * 0.5 * W, 0, zt - 3.0)
        for s in SIDES:
            root = V(x, s * (W + 2.0), zt - 3.0)
            f = Part.Face(Part.Wire(Part.makePolygon([root + V(0, 0, w / 2), tip + V(0, 0, w / 2), tip + V(0, 0, -w / 2),
                                                      root + V(0, 0, -w / 2), root + V(0, 0, w / 2)])))
            out.append((b["t"], f.common(oml)))
    return out


def ledge_faces(skin_faces, par=PAR):
    """Nose hatch-seat ledge: horizontal ribbon along the nose wall tops (Z = top line - hatch depth)."""
    w = par["LEDGE"][0]
    edges = []
    for f in skin_faces:
        for e in f.Edges:
            ps = e.discretize(7)
            if not all(P.HATCH_X[0] - 0.5 <= p.x <= P.HATCH_X[1] + 0.5 for p in ps):
                continue
            if all(abs(p.z - top_skin(p.x)) < 0.05 for p in ps) and all(abs(p.y) > 10 for p in ps):
                if not any(e.isSame(q) for q in edges):
                    edges.append(e)
    out = []
    for e in edges:
        s = 1.0 if e.discretize(3)[1].y > 0 else -1.0
        e2 = e.copy()
        e2.translate(V(0, -s * w, 0))
        out.append(Part.makeRuledSurface(e, e2))
    return out


def window_prisms(lay, par=PAR, depth_in=1.5, out=1.0):
    pr = []
    for w in lay["wins"]:
        xs = [p[0] for p in w["poly"]]
        Wmin = min(W_of(x) for x in xs)
        Wmax = max(W_of(x) for x in xs)
        for s in SIDES:
            y0 = s * (Wmin - depth_in)
            pts = [V(x, y0, z) for x, z in w["poly"]] + [V(w["poly"][0][0], y0, w["poly"][0][1])]
            f = Part.Face(Part.Wire(Part.makePolygon(pts)))
            pr.append(f.extrude(V(0, s * (Wmax - Wmin + depth_in + out), 0)))
    return pr


def relief_prisms(par=PAR):
    hx0, hx1, hy0, hy1 = P.FLOOR_HOLE_RECT
    r = par["RELIEF_R"]
    return [Part.makeCylinder(r, 6.0, V(x, y, P.BELLY_Z - 3.0), V(0, 0, 1)) for x in (hx0, hx1) for y in (hy0, hy1)]


# ============================ CAD: apply to the pod parts ============================
def _thicken(face, t, normal=None):
    if normal is None:
        u0, u1, v0, v1 = face.ParameterRange
        normal = face.normalAt(0.5 * (u0 + u1), 0.5 * (v0 + v1))
    n = V(normal)
    n.normalize()
    f = face.copy()
    f.translate(n * (-t / 2.0))
    return f.extrude(n * t)


def member_solids(oml, skin_faces, par=PAR):
    """All structure members as solids (fused later with the parts)."""
    lay = layout(par)
    sol = []
    t = par["RIB_T"]
    for f in diagrid_faces(oml, lay, par) + floor_faces(oml, par):
        sol.append(_thicken(f, t))
    for f in stringer_faces(oml, par):
        sol.append(f.extrude(V(0, 0, t)))
    for x, tt, f in frame_faces(oml, par):
        s_ = f.extrude(V(tt, 0, 0))
        s_.translate(V(-tt / 2, 0, 0))
        sol.append(s_)
    for tt, f in bar_faces(oml, par):
        sol.append(_thicken(f, tt))
    for f in ledge_faces(skin_faces, par):
        sol.append(f.extrude(V(0, 0, -par["LEDGE"][1])))
    return [s.common(oml) for s in sol], lay


def apply(parts, par=PAR, skin_faces=None, verbose=True):
    """parts: {name: Part.Shape} for F1_PodNose, F2_PodCentre, F3_PodAft (F-A or after F-B). Returns
    ({name: new shape}, report). Members are split at the part boundaries (X extent of each part)."""
    oml = oml_solid()
    if skin_faces is None:
        skin_faces = [f for s in parts.values() for f in s.Faces]
    sols, lay = member_solids(oml, skin_faces, par)
    cutters = window_prisms(lay, par) + relief_prisms(par)
    out, rep = {}, dict(windows=len(lay["wins"]) * 2, diagrid_segments=len(lay["segs"]) * 2, parts={})
    for name, shp in parts.items():
        bb = shp.BoundBox
        slab = box(bb.XMin, bb.XMax, -200, 200, -300, 200)
        add = [s.common(slab) for s in sols if s.BoundBox.XMax > bb.XMin and s.BoundBox.XMin < bb.XMax]
        add = [a for a in add if a.Volume > 1e-3]
        new = shp.fuse(add).removeSplitter() if add else shp.copy()
        cut = [c for c in cutters if c.BoundBox.XMax > bb.XMin and c.BoundBox.XMin < bb.XMax]
        if cut:
            new = new.cut(cut).removeSplitter()
        rep["parts"][name] = dict(vol_before=shp.Volume, vol_after=new.Volume, valid=new.isValid(), solids=len(new.Solids))
        if verbose:
            print("fus_struct %-14s vol %.2f -> %.2f cm3 valid %s solids %d" % (name, shp.Volume / 1000, new.Volume / 1000,
                                                                               new.isValid(), len(new.Solids)))
        out[name] = new
    return out, rep


# ============================ FEM hooks (used by structure/fem/run_study.py only) ============================
def fem_variant(name, PM, par=None):
    """FEM configuration for the structure study. Variants: D1 (F-A skins + structure), D2 (nose, floor and aft-cone
    bottom 0.5 mm + structure); suffix _nowin: same without windows."""
    import numpy as np
    par = dict(PAR if par is None else par)
    if name.endswith("_nowin"):
        par["WINDOWS"] = False
    lay = layout(par)
    frames = [(x, d, t) for x, d, t in par["FRAMES"]] + [(175.0, 6.0, 0.8)]     # + split-joint sleeve (baseline member)
    bars = par["BARS"]

    def cut_skin(skin):
        cutters = window_prisms(lay, par) + relief_prisms(par)
        out = []
        for f in skin:
            hit = [c for c in cutters if f.BoundBox.intersect(c.BoundBox)]
            out += (f.cut(hit).Faces if hit else [f])
        return out

    def member_faces(oml):
        fs = diagrid_faces(oml, lay, par) + stringer_faces(oml, par) + floor_faces(oml, par)
        fs += [f for x, t, f in frame_faces(oml, dict(par, FRAMES=frames))]
        fs += [f for t, f in bar_faces(oml, par)]
        R, rest = PM.pod_shapes()
        fs += ledge_faces(PM.outer_faces(rest, R["inner"]), par)
        return fs

    def skin_dist(cen):
        d = np.zeros(len(cen))
        for i, (x, y, z) in enumerate(cen):
            W, zb, rb = B.side_sec(x)
            ay = abs(y)
            if z >= zb + rb:
                d[i] = W - ay
            elif ay <= W - rb:
                d[i] = z - zb
            else:
                d[i] = rb - math.hypot(ay - (W - rb), z - (zb + rb))
        return d

    def tag(tg, cen, nrm, Wx, topx):
        d = skin_dist(cen)
        X, Z = cen[:, 0], cen[:, 2]
        for x, dd, t in frames:
            tg[(np.abs(X - x) < 0.06) & (np.abs(nrm[:, 0]) > 0.95) & (tg == "skin")] = "frame"
        for b in bars:
            zt = top_skin(b["x"]) - 3.0
            sgn = 1.0 if b["x"] > 0 else -1.0
            inb = (np.abs(Z - zt) <= b["w"] / 2 + 0.1) & (np.abs(nrm[:, 2]) < 0.2) & (sgn * (X - b["x"]) > -0.2) & \
                  (sgn * (X - b["x"]) < 0.5 * W_of(b["x"]) + 0.5) & (tg == "skin") & (d > 0.3)
            tg[inb] = "bar"
        tg[(tg == "skin") & (d > 0.3)] = "rib"

    def thick(t, tg, zone, cen, nrm):
        t[tg == "rib"] = par["RIB_T"]
        t[tg == "bar"] = bars[0]["t"]
        X = cen[:, 0]
        for x, dd, tt in frames:
            t[(tg == "frame") & (np.abs(X - x) < 0.06)] = tt

    base = name.split("_")[0]
    t_over = {} if base == "D1" else dict(nose=0.5, floor=0.5, aft_bottom=0.5)
    cfg = dict(PM.BASE)
    cfg.update(name=name, frames=frames, t_over=t_over,
               struct=dict(cut_skin=cut_skin, member_faces=member_faces, tag=tag, thick=thick),
               layout=dict(windows=len(lay["wins"]) * 2, segments=len(lay["segs"]) * 2))
    return cfg
