"""Pure-Python 2D geometry for the Fusion rev B model (no Fusion, no FreeCAD). Units mm.
Polygons are lists of (u, v) tuples, counter-clockwise, not closed (last != first)."""
import math


def interp(tab, x):
    """Linear interpolation in a [(x, y), ...] table sorted by x (clamped at the ends)."""
    if x <= tab[0][0]:
        return tab[0][1]
    for (x0, y0), (x1, y1) in zip(tab, tab[1:]):
        if x0 <= x <= x1:
            return y0 if x1 == x0 else y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return tab[-1][1]


def area(p):
    return 0.5 * sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))


def ccw(p):
    return p if area(p) > 0 else list(reversed(p))


def bbox(p):
    us, vs = [q[0] for q in p], [q[1] for q in p]
    return min(us), max(us), min(vs), max(vs)


def clean(p, tol=1e-6):
    """Drop repeated points and collinear points."""
    out = []
    for q in p:
        if not out or abs(q[0] - out[-1][0]) > tol or abs(q[1] - out[-1][1]) > tol:
            out.append(q)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < tol and abs(out[0][1] - out[-1][1]) < tol:
        out.pop()
    changed = True
    while changed and len(out) > 3:
        changed = False
        for i in range(len(out)):
            a, b, c = out[i - 1], out[i], out[(i + 1) % len(out)]
            cr = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
            if abs(cr) < 1e-9:
                out.pop(i)
                changed = True
                break
    return out


def clip_half(p, a, b, c):
    """Keep the part of polygon p where a*u + b*v <= c (Sutherland-Hodgman, one edge)."""
    out = []
    n = len(p)
    for i in range(n):
        P, Q = p[i], p[(i + 1) % n]
        fp, fq = a * P[0] + b * P[1] - c, a * Q[0] + b * Q[1] - c
        if fp <= 0:
            out.append(P)
        if (fp < 0 < fq) or (fq < 0 < fp):
            t = fp / (fp - fq)
            out.append((P[0] + t * (Q[0] - P[0]), P[1] + t * (Q[1] - P[1])))
    return out


def clip_rect(p, u0, u1, v0, v1):
    for a, b, c in ((-1, 0, -u0), (1, 0, u1), (0, -1, -v0), (0, 1, v1)):
        p = clip_half(p, a, b, c)
        if not p:
            return []
    return clean(p)


def rect(u0, u1, v0, v1):
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]


def circle_poly(uc, vc, r, n=48):
    return [(uc + r * math.cos(2 * math.pi * k / n), vc + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def hexagon(uc, vc, af):
    r = af / math.sqrt(3.0)
    return [(uc + r * math.cos(math.radians(60 * k)), vc + r * math.sin(math.radians(60 * k))) for k in range(6)]


def tabs_on_edge(p, i, centres, width, depth, kind="tab"):
    """Insert rectangular tabs (outward, kind='tab') or notches (inward, kind='notch') on edge i (p[i] -> p[i+1]) of a
    CCW polygon. centres = distances along the edge from p[i]."""
    P, Q = p[i], p[(i + 1) % len(p)]
    L = math.hypot(Q[0] - P[0], Q[1] - P[1])
    du, dv = (Q[0] - P[0]) / L, (Q[1] - P[1]) / L
    nu, nv = dv, -du                                    # outward normal of a CCW polygon
    s = depth if kind == "tab" else -depth
    ins = []
    for c in sorted(centres):
        a, b = c - width / 2.0, c + width / 2.0
        if a < 0.5 or b > L - 0.5:
            continue
        for d, off in ((a, 0.0), (a, s), (b, s), (b, 0.0)):
            ins.append((P[0] + du * d + nu * off, P[1] + dv * d + nv * off))
    return p[:i + 1] + ins + p[i + 1:]


def dovetail_edge(p, i, centres, w_neck=8.0, w_head=12.0, depth=6.0, male=True):
    """Puzzle (dovetail) keys on edge i of a CCW polygon: male keys stick out, female keys are cut in (same shape)."""
    P, Q = p[i], p[(i + 1) % len(p)]
    L = math.hypot(Q[0] - P[0], Q[1] - P[1])
    du, dv = (Q[0] - P[0]) / L, (Q[1] - P[1]) / L
    nu, nv = dv, -du
    s = depth if male else -depth
    ins = []
    for c in sorted(centres):
        pts = ((c - w_neck / 2, 0), (c - w_head / 2, s), (c + w_head / 2, s), (c + w_neck / 2, 0))
        for d, off in pts:
            ins.append((P[0] + du * d + nu * off, P[1] + dv * d + nv * off))
    return p[:i + 1] + ins + p[i + 1:]


def find_edge(p, pred):
    """Index of the first edge (p[i] -> p[i+1]) whose midpoint satisfies pred(u, v)."""
    for i in range(len(p)):
        P, Q = p[i], p[(i + 1) % len(p)]
        if pred(0.5 * (P[0] + Q[0]), 0.5 * (P[1] + Q[1])):
            return i
    raise ValueError("edge not found")


def offset_polyline(pts, d):
    """Offset an open polyline by d to the left (positive) using miter joins."""
    out = []
    n = len(pts)
    for i in range(n):
        if i == 0:
            a, b = pts[0], pts[1]
        elif i == n - 1:
            a, b = pts[-2], pts[-1]
        if 0 < i < n - 1:
            a0, b0, c0 = pts[i - 1], pts[i], pts[i + 1]
            t1 = _unit(a0, b0)
            t2 = _unit(b0, c0)
            n1, n2 = (-t1[1], t1[0]), (-t2[1], t2[0])
            m = (n1[0] + n2[0], n1[1] + n2[1])
            ml = math.hypot(*m)
            m = (m[0] / ml, m[1] / ml)
            cosh = m[0] * n1[0] + m[1] * n1[1]
            out.append((b0[0] + m[0] * d / cosh, b0[1] + m[1] * d / cosh))
        else:
            t = _unit(a, b)
            nn = (-t[1], t[0])
            q = pts[i]
            out.append((q[0] + nn[0] * d, q[1] + nn[1] * d))
    return out


def _unit(a, b):
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    return ((b[0] - a[0]) / L, (b[1] - a[1]) / L)


# ---------------- airfoil ----------------
def read_dat(path):
    pts = []
    for line in open(path):
        s = line.split()
        if len(s) != 2:
            continue
        try:
            pts.append((float(s[0]), float(s[1])))
        except ValueError:
            pass
    return pts


def densify(pts, n):
    """Centripetal Catmull-Rom through the points, n sub-steps per segment (smooth resample of a .dat file)."""
    out = []
    m = len(pts)
    for i in range(m - 1):
        p0 = pts[max(i - 1, 0)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(i + 2, m - 1)]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 +
                                    (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1])
    return out


class Airfoil:
    """Selig .dat airfoil scaled to chord c. upper(x), lower(x) by linear interpolation of a dense resample."""

    def __init__(self, path, chord):
        raw = densify(read_dat(path), 8)
        ile = min(range(len(raw)), key=lambda i: raw[i][0])
        up = sorted([(min(x, 1.0) * chord, z * chord) for x, z in raw[:ile + 1]])
        lo = sorted([(min(x, 1.0) * chord, z * chord) for x, z in raw[ile:]])
        self.c = chord
        self.up, self.lo = up, lo
        self.raw = [(min(x, 1.0) * chord, z * chord) for x, z in raw]

    def zu(self, x):
        return interp(self.up, x)

    def zl(self, x):
        return interp(self.lo, x)

    def outline(self):
        """Closed outline TE upper -> LE -> TE lower (Selig order), mm."""
        return list(self.raw[:-1]) if self.raw[0] == self.raw[-1] else list(self.raw)

    def inset(self, t, x0, x1, n=120):
        """Outline offset t mm inward (normal offset approximated by sampling), closed by vertical lines at x0, x1.
        Returns a CCW polygon in (x, z)."""
        xs = [x0 + (x1 - x0) * (1 - math.cos(math.pi * i / n)) / 2 for i in range(n + 1)]
        upper = [(x, self._off(x, t, True)) for x in xs]
        lower = [(x, self._off(x, t, False)) for x in xs]
        poly = list(reversed(upper)) + lower      # x1 top -> x0 top -> x0 bottom -> x1 bottom  (CW in x-z) -> fix
        return ccw(clean(poly))

    def _off(self, x, t, upper):
        """z of the inward offset curve at x: min over nearby surface points of (z -/+ distance) (exact for convex)."""
        f = self.zu if upper else self.zl
        best = None
        for k in range(-30, 31):
            xs = x + k * t / 10.0
            if xs < 0 or xs > self.c:
                continue
            zs = f(xs)
            dx = x - xs
            if abs(dx) >= t:
                continue
            dz = math.sqrt(t * t - dx * dx)
            z = zs - dz if upper else zs + dz
            if best is None or (upper and z < best) or (not upper and z > best):
                best = z
        return best


def poly_minus_disk(poly, c, r, n=40):
    """Convex polygon minus a disk whose circle crosses the polygon boundary in exactly 2 points.
    Returns the remaining region as one polygon (CCW)."""
    poly = ccw(poly)
    cu, cv = c

    def inside(q):
        return (q[0] - cu) ** 2 + (q[1] - cv) ** 2 < r * r

    m = len(poly)
    out_chain, hits = [], []
    # walk edges, collect points outside, record crossing points with direction
    start = next(i for i in range(m) if not inside(poly[i]))
    for k in range(m):
        i = (start + k) % m
        P, Q = poly[i], poly[(i + 1) % m]
        out_chain.append(P) if not inside(P) else None
        # circle-segment intersections
        dx, dy = Q[0] - P[0], Q[1] - P[1]
        fx, fy = P[0] - cu, P[1] - cv
        a = dx * dx + dy * dy
        b = 2 * (fx * dx + fy * dy)
        cc = fx * fx + fy * fy - r * r
        disc = b * b - 4 * a * cc
        if disc > 0:
            sq = math.sqrt(disc)
            for t in sorted(((-b - sq) / (2 * a), (-b + sq) / (2 * a))):
                if 1e-9 < t < 1 - 1e-9:
                    pt = (P[0] + t * dx, P[1] + t * dy)
                    entering = inside((P[0] + (t + 1e-6) * dx, P[1] + (t + 1e-6) * dy))
                    out_chain.append(("ENTER" if entering else "EXIT", pt))
    # replace the ENTER ... EXIT part by an arc (the arc runs inside the polygon)
    res, k = [], 0
    while k < len(out_chain):
        e = out_chain[k]
        if isinstance(e[0], str):
            if e[0] == "ENTER":
                j = next(jj for jj in range(k + 1, len(out_chain)) if isinstance(out_chain[jj][0], str))
                p_in, p_out = e[1], out_chain[j][1]
                a0 = math.atan2(p_in[1] - cv, p_in[0] - cu)
                a1 = math.atan2(p_out[1] - cv, p_out[0] - cu)
                # going around the polygon CCW, the arc that bounds the remaining region runs clockwise
                while a1 > a0:
                    a1 -= 2 * math.pi
                res.append(p_in)
                for s in range(1, n):
                    ang = a0 + (a1 - a0) * s / n
                    res.append((cu + r * math.cos(ang), cv + r * math.sin(ang)))
                res.append(p_out)
                k = j + 1
                continue
            res.append(e[1])
        else:
            res.append(e)
        k += 1
    return clean(res)


# ---------------- frames (pure python; fxlib turns them into matrices) ----------------
def vnorm(v):
    L = math.sqrt(sum(c * c for c in v))
    return tuple(c / L for c in v)


def vcross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def vdot(a, b):
    return sum(x * y for x, y in zip(a, b))


def frame(origin, xdir, ydir):
    """Right-handed frame: local u along xdir, v along ydir, w (thickness) along xdir x ydir."""
    x = vnorm(xdir)
    z = vnorm(vcross(x, ydir))
    y = vcross(z, x)
    return (tuple(origin), x, y, z)


def to_world(fr, u, v, w=0.0):
    o, x, y, z = fr
    return tuple(o[i] + x[i] * u + y[i] * v + z[i] * w for i in range(3))


def to_local(fr, p):
    o, x, y, z = fr
    d = tuple(p[i] - o[i] for i in range(3))
    return vdot(d, x), vdot(d, y), vdot(d, z)


def point_in_poly(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if xi > x:
                inside = not inside
    return inside


def text_box(text, h):
    lines = text.split("\n")
    return max(len(s) for s in lines) * 0.62 * h + 1.0, len(lines) * 1.3 * h + 0.6


def label_spot(poly, cutters, text, h, step=2.0, prefer=None):
    """A point where the text box (centred) lies inside poly and clear of all cutter bounding boxes."""
    w, hh = text_box(text, h)
    u0, u1, v0, v1 = bbox(poly)
    cu, cv = prefer if prefer else (0.5 * (u0 + u1), 0.5 * (v0 + v1))
    cands = []
    nu, nv = int((u1 - u0) / step) + 1, int((v1 - v0) / step) + 1
    for i in range(nu):
        for j in range(nv):
            cands.append((u0 + i * step, v0 + j * step))
    cands.sort(key=lambda p: (p[0] - cu) ** 2 + (p[1] - cv) ** 2)
    cbs = []
    for c in cutters:
        if isinstance(c, tuple) and c and c[0] == "circle":
            cbs.append((c[1] - c[3], c[1] + c[3], c[2] - c[3], c[2] + c[3]))
        else:
            cbs.append(bbox(c))
    for (u, v) in cands:
        corners = [(u - w / 2, v - hh / 2), (u + w / 2, v - hh / 2), (u + w / 2, v + hh / 2), (u - w / 2, v + hh / 2),
                   (u, v - hh / 2), (u, v + hh / 2), (u - w / 2, v), (u + w / 2, v)]
        if not all(point_in_poly(c, poly) for c in corners):
            continue
        tb = (u - w / 2 - 0.5, u + w / 2 + 0.5, v - hh / 2 - 0.5, v + hh / 2 + 0.5)
        if any(tb[0] < b[1] and b[0] < tb[1] and tb[2] < b[3] and b[2] < tb[3] for b in cbs):
            continue
        # keep the text off the polygon edges by 0.8 mm
        return (u, v)
    return None
