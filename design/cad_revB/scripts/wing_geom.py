"""Wing rev A - 2D section geometry in the XZ plane (y = 0). Run inside FreeCAD.
OUTER = SD7062 x 280 outline face. INNER = outline offset 1.5 mm inward (normal), closed at x = 258.
SKIN = OUTER - INNER. Parts = region & x-range, minus notches/holes, extruded along +Y."""
import math
import FreeCAD as App
import Part
from FreeCAD import Vector as V
import wing_params as P


def read_dat(path=P.AIRFOIL):
    pts = []
    for line in open(path):
        s = line.split()
        if len(s) != 2:
            continue
        try:
            x, z = float(s[0]), float(s[1])
        except ValueError:
            continue
        pts.append((x, z))
    return pts


def outer_curve():
    """One B-spline through the Selig points, TE upper -> LE -> TE lower, closed at a sharp TE."""
    raw = read_dat()
    pts = [V(min(x, 1.0) * P.CHORD, 0, z * P.CHORD) for x, z in raw]
    pts[-1] = V(pts[0])
    bs = Part.BSplineCurve()
    bs.interpolate(pts[:-1] + [pts[0]], PeriodicFlag=False)
    return bs


_OUT = {}


def OUTER():
    if "f" not in _OUT:
        bs = outer_curve()
        # two edges (TE->LE, LE->TE): a single closed-spline edge gives wrong area/volume integrals in OCC
        u0, u1 = bs.FirstParameter, bs.LastParameter
        us = [u0 + (u1 - u0) * i / 4000 for i in range(4001)]
        ule = min(us, key=lambda u: bs.value(u).x)
        w = Part.Wire([bs.toShape(u0, ule), bs.toShape(ule, u1)])
        _OUT["f"] = Part.Face(w)
        _OUT["bs"] = bs
    return _OUT["f"]


def surf_z(x, upper=True, shape=None):
    """z of the outer (or given) section boundary at x: max (upper) / min (lower) of a vertical-line cut."""
    f = shape if shape is not None else OUTER()
    line = Part.makeLine(V(x, 0, -100), V(x, 0, 100))
    sec = f.section(line)
    zs = [v.Point.z for v in sec.Vertexes]
    if not zs:
        return None
    return max(zs) if upper else min(zs)


def depth(x, shape=None):
    return surf_z(x, True, shape) - surf_z(x, False, shape)


def _inner_points(n=1500, t=None):
    """Sample the outer spline, offset each point t mm (default 1.5) along the inward normal."""
    t = P.SKIN_T if t is None else t
    OUTER()
    bs = _OUT["bs"]
    u0, u1 = bs.FirstParameter, bs.LastParameter
    up, lo = [], []
    # find LE parameter (min x)
    us = [u0 + (u1 - u0) * i / n for i in range(n + 1)]
    ile = min(range(len(us)), key=lambda i: bs.value(us[i]).x)
    for i, u in enumerate(us):
        p = bs.value(u)
        d = bs.tangent(u)[0]
        # curve runs TE(upper) -> LE -> TE(lower): clockwise in (x,z) seen from +y? inward normal:
        # for upper side tangent points to -x, inward normal is (d.z, -d.x) rotated: use (−dz, dx) test
        nx, nz = -d.z, d.x
        # choose sign so the normal points towards the chord region (test with a small step)
        q = V(p.x + 0.5 * nx, 0, p.z + 0.5 * nz)
        if not OUTER().isInside(q, 1e-6, True):
            nx, nz = -nx, -nz
        o = (p.x + t * nx, p.z + t * nz)
        (up if i <= ile else lo).append(o)
    return up, lo


def _interp_z(seq, x):
    """seq = list of (x,z) monotonic in x (any direction)."""
    s = sorted(seq)
    for (x0, z0), (x1, z1) in zip(s, s[1:]):
        if x0 <= x <= x1:
            return z0 + (z1 - z0) * (x - x0) / (x1 - x0) if x1 > x0 else z0
    return None


_IN = {}


def INNER():
    if "f" not in _IN:
        _IN["f"] = inset_face(P.SKIN_T, 3.0, P.INNER_XMAX)
    return _IN["f"]


def inset_face(t, xa=None, xb=None, min_gap=1.0):
    """Outline offset t mm inward, closed by vertical lines at xa and xb.
    If xa/xb are None they are set where the inset depth falls to min_gap."""
    up, lo = _inner_points(t=t)
    if xa is None or xb is None:
        # limits from the OUTER depth (robust where the offset curves fold): depth_out >= 2t + min_gap
        good = [x * 0.5 for x in range(2, 559) if depth(x * 0.5) >= 2 * t + min_gap]
        xa = float(min(good)) if xa is None else xa
        xb = float(max(good)) if xb is None else xb
    # keep the monotonic parts in x (the nose offset can fold); resample on a common x grid
    def clean(seq):
        s = [(x, z) for x, z in seq if xa - 1 <= x <= xb + 1]
        s.sort()
        out = []
        for x, z in s:
            if not out or x > out[-1][0] + 1e-4:
                out.append((x, z))
        return out
    up, lo = clean(up), clean(lo)
    xs = [xa + (xb - xa) * (1 - math.cos(math.pi * i / 160)) / 2 for i in range(161)]
    zu = [_interp_z(up, x) for x in xs]
    zl = [_interp_z(lo, x) for x in xs]
    bu = Part.BSplineCurve(); bu.interpolate([V(x, 0, z) for x, z in zip(xs, zu)])
    bl = Part.BSplineCurve(); bl.interpolate([V(x, 0, z) for x, z in zip(xs, zl)])
    e1 = bu.toShape()
    e2 = Part.makeLine(V(xb, 0, zu[-1]), V(xb, 0, zl[-1]))
    e3 = bl.toShape()
    e4 = Part.makeLine(V(xa, 0, zl[0]), V(xa, 0, zu[0]))
    w = Part.Wire(Part.__sortEdges__([e1, e2, e3, e4]))
    return Part.Face(w)


def SKIN():
    if "skin" not in _IN:
        _IN["skin"] = OUTER().cut(INNER())
    return _IN["skin"]


def rect(x0, x1, z0=-60.0, z1=60.0):
    return Part.Face(Part.makePolygon([V(x0, 0, z0), V(x1, 0, z0), V(x1, 0, z1), V(x0, 0, z1), V(x0, 0, z0)]))


def circle(xc, zc, d):
    return Part.Face(Part.Wire([Part.makeCircle(d / 2.0, V(xc, 0, zc), V(0, 1, 0))]))


def clip(region, x0, x1, z0=-60.0, z1=60.0):
    return region.common(rect(x0, x1, z0, z1))


def faces_split(shape):
    """Return (top_faces, bottom_faces) by centre-of-mass z relative to the mean camber region."""
    top, bot = [], []
    for f in shape.Faces:
        c = f.CenterOfMass
        zmid = 0.5 * (surf_z(c.x, True) + surf_z(c.x, False))
        (top if c.z > zmid else bot).append(f)
    return top, bot


def extrude(face, y0, y1):
    """Extrude an XZ-plane face from y0 to y1 (y1 > y0)."""
    s = face.extrude(V(0, y1 - y0, 0))
    s.translate(V(0, y0, 0))
    return s


def inner_z_range(x0, x1, upper=True, n=25):
    """min (upper) or max (lower) of the inner outline over [x0,x1]."""
    INNER()
    zs = [surf_z(x0 + (x1 - x0) * i / n, upper, INNER()) for i in range(n + 1)]
    return min(zs) if upper else max(zs)
