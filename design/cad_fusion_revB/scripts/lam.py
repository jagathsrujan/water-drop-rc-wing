"""Laminated parts made from the one 1.5 mm stock (balsa medium or birch ply) - optimisation P1/P2.

A part dict (pod.py / wing.py / tail.py format) may carry p["layers"]: a list, one entry per 1.5 mm layer from the
part's base face (w = z0) up, each dict(grain='u' | 'v', pieces=[None | (u0, u1, v0, v1), ...]). A piece rectangle
clips the part outline: a layer that does not fit the 100 mm balsa sheet across its grain is made of several pieces,
and the joints are staggered between layers so every joint is bridged by the next layer.

In Fusion the part stays ONE component (its name is unchanged, so the assembly, linkage, joint checks and build steps
keep working) holding one body per piece, named <part>-<layer><piece>, e.g. B1-1a, B1-2, B1-3b. The laser output,
the loops and the mass table work per body."""
import re

import geo as G

STOCK = 1.5
BIG = 1.0e4


def layer(grain, *pieces):
    return dict(grain=grain, pieces=list(pieces) if pieces else [None])


def cross(n, first="u"):
    """n layers, grain alternating (cross-laminated), no splits."""
    other = "v" if first == "u" else "u"
    return [layer(first if i % 2 == 0 else other) for i in range(n)]


def parallel(n, grain="u"):
    return [layer(grain) for _ in range(n)]


def urange(a=-BIG, b=BIG, v0=-BIG, v1=BIG):
    return (a, b, v0, v1)


def apply(parts, spec):
    """Attach the layer specs (name -> layers) and check that every part is n x 1.5 thick."""
    names = {p["name"] for p in parts}
    for n in spec:
        if n not in names:
            raise KeyError("laminate spec for a part that does not exist: " + n)
    for p in parts:
        L = spec.get(p["name"])
        if L is None:
            continue
        if abs(p["t"] - len(L) * STOCK) > 1e-6:
            raise ValueError("%s: %.2f mm is not %d x %.1f" % (p["name"], p["t"], len(L), STOCK))
        p["layers"] = L
    return parts


def piece_name(base, i, j, npieces):
    return "%s-%d%s" % (base, i + 1, "abcdefgh"[j] if npieces > 1 else "")


def base_of(body_name):
    """B1-2a -> (B1, 2); a plain part name -> (name, 0)."""
    m = re.match(r"^(.*)-(\d)([a-h]?)$", body_name)
    return (m.group(1), int(m.group(2))) if m else (body_name, 0)


def _label(poly, cutters, text):
    h = 3.0
    while h >= 1.4:
        p = G.label_spot(poly, cutters, text, h)
        if p:
            return [(text, p[0], p[1], h)]
        h -= 0.4
    return []


def expand(p):
    """The layer pieces of a laminated part, as part dicts on their own (t = 1.5, own z0, own outline and label)."""
    out = []
    for i, L in enumerate(p["layers"]):
        z = p.get("z0", 0.0) + i * STOCK
        rects = L["pieces"]
        for j, r in enumerate(rects):
            poly = p["outline"] if r is None else G.clip_rect(p["outline"], *r)
            if len(poly) < 3 or abs(G.area(poly)) < 1.0:
                continue
            nm = piece_name(p["name"], i, j, len(rects))
            d = dict(p)
            d.pop("layers", None)
            d.update(name=nm, outline=G.ccw(poly), t=STOCK, z0=z, grain=L["grain"], base=p["name"], layer=i + 1,
                     of=len(p["layers"]), labels=_label(poly, p["cutters"], nm))
            out.append(d)
    return out


def flat(parts):
    """Every laser-level part: laminated parts replaced by their pieces."""
    out = []
    for p in parts:
        out.extend(expand(p) if p.get("layers") else [p])
    return out
