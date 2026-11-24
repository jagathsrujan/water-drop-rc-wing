"""Check every dovetail joint between mating pieces: sample points along the joint line and report places where
neither piece has material (gap) or both do (overlap). Plain Python on the part data.  python check_joints.py"""
import math
import geo as G
import pod as POD
import wing as W
import jigs as J

STEP = 0.1


def sample(pa, pb, axis, c, band, depth=12.0):
    """axis 'u': joint line u = c, band = (v0, v1); axis 'v': joint line v = c, band = (u0, u1)."""
    gaps, over = [], []
    n_t = int((band[1] - band[0]) / STEP)
    n_d = int(2 * depth / STEP)
    for i in range(n_t + 1):
        t = band[0] + i * STEP
        g = o = 0
        for j in range(n_d + 1):
            d = c - depth + j * STEP + STEP / 2
            pt = (d, t) if axis == "u" else (t, d)
            ia, ib = G.point_in_poly(pt, pa), G.point_in_poly(pt, pb)
            if ia and ib:
                o += 1
            elif not ia and not ib:
                g += 1
        if g:
            gaps.append((round(t, 1), round(g * STEP, 2)))
        if o:
            over.append((round(t, 1), round(o * STEP, 2)))
    return gaps, over


def runs(lst):
    """Group consecutive positions into (from, to, max width) runs."""
    out = []
    for t, w in lst:
        if out and abs(t - out[-1][1]) <= STEP * 1.5:
            out[-1] = (out[-1][0], t, max(out[-1][2], w))
        else:
            out.append((t, t, w))
    return [(a, b, w) for a, b, w in out if b - a >= 0.25]


def main():
    pod_parts = {p["name"]: p for p in POD.all_parts()[0]}
    wing_parts = {p["name"]: p for p in W.all_parts()[0]}
    jig_parts = {p["name"]: p for p in J.all_parts()}
    checks = []
    # floor joints (same floor frame per segment)
    for k, seg in enumerate(POD.SEGN):
        xa, xb = POD.SEGS[k]
        cuts = [xa] + POD.FLOOR_SPLITS[seg] + [xb]
        names = ["FL-%s%d" % (seg, j + 1) for j in range(len(cuts) - 1)]
        for j, x in enumerate(cuts[1:-1]):
            u = POD.floor_u(k, x)
            hwj = POD.hw(x)
            checks.append(("%s / %s" % (names[j], names[j + 1]), pod_parts[names[j]]["outline"], pod_parts[names[j + 1]]["outline"],
                           "u", u, (-hwj + 4, hwj - 4)))
    # hatch halves (centre line v = 0)
    hn = pod_parts["HN-R"]["outline"]
    checks.append(("HN-R / HN-L", hn, pod_parts["HN-L"]["outline"], "v", 0.0, (2.0, G.bbox(hn)[1] - 2.0)))
    # false spar pieces (frame u = Y)
    fs = {n: p["outline"] for n, p in wing_parts.items() if n.startswith("FSP-")}
    zl, zu = G.bbox(fs["FSP-C"])[2:]
    for a, b, y in (("FSP-C", "FSP-R1", 142.0), ("FSP-R1", "FSP-R2", 357.5), ("FSP-L1", "FSP-C", -142.0), ("FSP-L2", "FSP-L1", -357.5)):
        checks.append(("%s / %s" % (a, b), fs[a], fs[b], "u", y, (zl + 0.5, zu - 0.5)))
    # jig base segments
    for i, c in enumerate(J.SEG_CUTS[1:-1]):
        a, b = J.SEG_NAMES[i], J.SEG_NAMES[i + 1]
        hwj = J.BASE_HW if c < J.POD_END_X else J.BOOM_HW
        checks.append(("%s / %s" % (a, b), jig_parts[a]["outline"], jig_parts[b]["outline"], "u", c, (-hwj + 3, hwj - 3)))
    # wing cradles (front / rear halves)
    wcf, wcr = jig_parts["WC1R-F"]["outline"], jig_parts["WC1R-R"]["outline"]
    top = min(v for u, v in wcf if abs(u - J.SPLIT_X) < 1e-6)
    checks.append(("WC-F / WC-R", wcf, wcr, "u", J.SPLIT_X, (J.WB + 0.5, max(v for u, v in wcf if abs(u - J.SPLIT_X) < 1e-6) - 1.5), 6.0))
    bad = 0
    for chk in checks:
        name, pa, pb, axis, c, band = chk[:6]
        gaps, over = sample(pa, pb, axis, c, band, *chk[6:])
        g, o = runs(gaps), runs(over)
        status = "OK" if not g and not o else "MISMATCH"
        bad += status != "OK"
        print("%-18s %-8s gaps %s  overlaps %s" % (name, status, [(a, b, w) for a, b, w in g][:6], [(a, b, w) for a, b, w in o][:6]))
    print("joints checked: %d, mismatched: %d" % (len(checks), bad))


if __name__ == "__main__":
    main()
