"""Check every laminate layer piece (lam.py) before it goes to Fusion. Plain Python (numpy):  python lam_check.py
- each piece, after its cutters, is ONE connected region (a split must not leave loose bits);
- balsa pieces are <= 100 mm across the grain (100 mm sheet) and <= 294 mm along it (300 mm laser sheet, 3 mm margins);
- birch pieces fit the 300 x 300 sheet;
- the layers of a part cover the same outline (no piece missing).
Exit code 1 on any problem."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.dirname(os.path.dirname(HERE))
for p in ("cad_fuselage_balsa/scripts", "cad_fuselage/scripts", "cad_reservoir/scripts", "cad/scripts"):
    sys.path.insert(0, os.path.join(DESIGN, p))
sys.path.insert(0, HERE)
import geo as G     # noqa: E402
import lam          # noqa: E402

RES = 0.25


def poly_mask(poly, U, V):
    x = np.asarray([p[0] for p in poly]); y = np.asarray([p[1] for p in poly])
    inside = np.zeros(U.shape, bool)
    j = len(x) - 1
    for i in range(len(x)):
        cond = (y[i] > V) != (y[j] > V)
        with np.errstate(divide="ignore", invalid="ignore"):
            xint = (x[j] - x[i]) * (V - y[i]) / (y[j] - y[i] + 1e-300) + x[i]
        inside ^= cond & (U < xint)
        j = i
    return inside


def region(p):
    u0, u1, v0, v1 = G.bbox(p["outline"])
    U, V = np.meshgrid(np.arange(u0 - 1, u1 + 1, RES), np.arange(v0 - 1, v1 + 1, RES))
    m = poly_mask(p["outline"], U, V)
    for c in p["cutters"]:
        if isinstance(c, tuple) and c and c[0] == "circle":
            m &= (U - c[1]) ** 2 + (V - c[2]) ** 2 > c[3] ** 2
        elif len(c) >= 3:
            m &= ~poly_mask(c, U, V)
    return m


def components(m):
    """number of 4-connected components (label propagation)."""
    lab = np.where(m, np.arange(m.size).reshape(m.shape) + 1, 0)
    big = m.size + 10
    while True:
        l2 = np.where(m, lab, big)
        p = np.pad(l2, 1, constant_values=big)
        nb = np.minimum.reduce([p[1:-1, 1:-1], p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]])
        new = np.where(m, nb, 0)
        if np.array_equal(new, lab):
            break
        lab = new
    return len(np.unique(lab[m]))


def main():
    import pod
    import tail
    import wing
    import linkage
    srcs = (pod.all_parts()[0], wing.all_parts()[0], tail.all_parts()[0], linkage.wing_parts()[0])
    bad, n = [], 0
    for src in srcs:
        for p in src:
            if not p.get("layers"):
                continue
            pieces = lam.expand(p)
            full = region(p).sum()
            per_layer = {}
            for q in pieces:
                n += 1
                m = region(q)
                k = components(m)
                per_layer[q["layer"]] = per_layer.get(q["layer"], 0) + m.sum()
                u0, u1, v0, v1 = G.bbox(q["outline"])
                across = (v1 - v0) if q["grain"] == "u" else (u1 - u0)
                along = (u1 - u0) if q["grain"] == "u" else (v1 - v0)
                if k != 1:
                    bad.append("%s: %d separate regions after the cutters" % (q["name"], k))
                if q["mat"].startswith("balsa") and (across > 100.0 + 1e-6 or along > 294.0):
                    bad.append("%s: %.1f across / %.1f along the grain (sheet 100 x 300)" % (q["name"], across, along))
                if q["mat"] == "ply" and max(u1 - u0, v1 - v0) > 294.0:
                    bad.append("%s: does not fit 300 x 300" % q["name"])
            for L, a in per_layer.items():
                if abs(a - full) > 0.02 * full + 50:
                    bad.append("%s layer %d covers %.0f of %.0f px" % (p["name"], L, a, full))
    print("laminate pieces checked:", n)
    for b in bad:
        print("PROBLEM", b)
    print("OK" if not bad else "%d problem(s)" % len(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
