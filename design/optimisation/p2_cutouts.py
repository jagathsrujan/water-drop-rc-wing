"""P2 lightening study: mass removable by lightening holes, computed from the rev B part outlines.

Every part is rasterised (0.25 mm) from the build-kit registry (tools/build_kit/kit_data.py -> pod.py / wing.py /
tail.py). The material that must stay solid is kept by eroding the part (edge margin), its cutters (slots, holes) and
named keep-solid zones; hexagonal cells are then placed on a lattice and kept only where a whole cell fits. Mass is
taken at the P1 decision (1.5 mm medium balsa, 0.14 g/cm3, laminate per p1_schedule_1p5.csv).

    python design/optimisation/p2_cutouts.py        (about 2 minutes: the registry build is slow)

Writes p2_cutouts.csv (one row per candidate group) and p2_cells.json (cell centres, for P3 and the figures), and
p2_fig/*.png (each candidate part with its cells).
Rules (inputs at the top): pod side laminate = the FreeCAD rev B rule set (bal_params.py HEX_*): cells 8 mm across
flats, 2.5 mm webs, 8 mm solid bands at every piece edge, +-5 mm at every former, solid launch-grip zone, servo zone,
pin-flag hole and band-stub zone; holes go through both layers and are filmed on the inner face (30 g/m2).
"""
import csv
import json
import math
import os
import pickle
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
DESIGN = os.path.join(REPO, "design")
for p in ("cad_fuselage_balsa/scripts", "cad_fuselage/scripts", "cad_reservoir/scripts", "cad/scripts",
          "cad_fusion_revB/scripts"):
    sys.path.insert(0, os.path.join(DESIGN, p))
sys.path.insert(0, os.path.join(REPO, "tools", "build_kit"))
import bal_params as BP  # noqa: E402
import fus_params as FP  # noqa: E402

RES = 0.4                       # mm per pixel
RHO = 0.14                      # g/cm3, P1 decision (generic medium)
FILM_IN = 30.0                  # g/m2, film on the inner face over side holes (bal_params FILM_G_M2)
GLUE_FRAC_POD = 0.10            # mass_summary.py: pod glue 10 % of the wood -> removed wood also removes its glue share
FORMERS = {"N1": (-130.0, -127.0), "N2": (-100.0, -97.0), "FS": (-29.2, -26.2), "B1": (38.0, 41.0),
           "B2": (105.0, 108.0), "B4": (170.0, 173.0), "BH": (236.0, 239.0), "EF": (302.0, 305.0)}
JOINT_MARGIN = 3.0              # mm, solid band at the butt joints between side pieces of one layer (estimate)
FORMER_T_NEW = 4.5             # P1: formers 3 x 1.5 -> the solid band follows the thicker former
CACHE = os.path.join(os.environ.get("TEMP", HERE), "p2_registry.pkl")
FIG = os.path.join(HERE, "p2_fig")

# candidate groups: name, part-name test, cell across-flats, web, edge margin, laminate thickness (mm), note
GROUPS = [
    ("Pod side laminate (hex, both layers)", None, 8.0, 2.5, 8.0, None, "rev B rule set"),
    ("Floor (between formers, outside saddles and skids)", lambda n: n.startswith("FL-"), 10.0, 3.0, 8.0, 1.5, ""),
    ("Aft deck", lambda n: n == "DECK", 10.0, 3.0, 6.0, 1.5, ""),
    ("Formers N1 N2 B1 B2 B4 EF (3 x 1.5)", lambda n: n in ("N1", "N2", "B1", "B2-R", "B2-L", "B4", "EF"), 8.0, 3.0, 6.0, 4.5, ""),
    ("Bulkhead BH (4 x 1.5)", lambda n: n == "BH", 10.0, 3.0, 6.0, 6.0, "tube rings and tabs solid"),
    ("Saddle layers and bridges", lambda n: n[:2] in ("S1", "S2"), 8.0, 3.0, 5.0, 3.0, "already windowed"),
    ("Tail-servo tray and battery tray", lambda n: n in ("TST", "TRAY"), 10.0, 3.0, 6.0, 3.0, ""),
    ("Hatch HN-R/L, HF", lambda n: n in ("HN-R", "HN-L", "HF"), 8.0, 2.5, 5.0, 1.5, ""),
    ("Stab, fin (2 x 1.5): open frame", lambda n: n in ("STAB-R", "STAB-L", "FIN"), 20.0, 4.0, 6.0, 3.0, "frame 6 mm + 4 mm lattice"),
    ("Elevators, rudder (2 x 1.5): open frame", lambda n: n in ("ELEV-R", "ELEV-L", "RUDDER"), 20.0, 4.0, 6.0, 3.0, ""),
    ("Wing tips and tip caps (2 x 1.5)", lambda n: n.startswith("W-TIP"), 12.0, 3.0, 5.0, 3.0, ""),
    ("Wing ribs 1.5 (W-R055..W-R440): extra cells", lambda n: n.startswith("W-R") and not n.startswith("W-R110"), 10.0, 3.0, 4.0, 1.5, "beside the existing holes"),
]


def registry():
    if os.path.exists(CACHE):
        return pickle.load(open(CACHE, "rb"))
    import kit_data as K
    R = K.build_registry().parts
    pickle.dump(R, open(CACHE, "wb"))
    return R


# ---------------- raster tools ----------------
def poly_mask(poly, U, V):
    """even-odd point-in-polygon on a grid."""
    x = np.asarray([p[0] for p in poly]); y = np.asarray([p[1] for p in poly])
    inside = np.zeros(U.shape, bool)
    j = len(x) - 1
    for i in range(len(x)):
        cond = ((y[i] > V) != (y[j] > V))
        with np.errstate(divide="ignore", invalid="ignore"):
            xint = (x[j] - x[i]) * (V - y[i]) / (y[j] - y[i] + 1e-300) + x[i]
        inside ^= cond & (U < xint)
        j = i
    return inside


def part_mask(e, U, V):
    m = poly_mask(e["outline"], U, V)
    for h in e.get("holes", []):
        if h[0] == "c":
            m &= (U - h[1]) ** 2 + (V - h[2]) ** 2 > h[3] ** 2
        else:
            m &= ~poly_mask(h[1], U, V)
    return m


def erode(m, r):
    """binary erosion by an octagon of 'radius' r (mm): alternating 4- and 8-neighbour steps (close to a disc)."""
    out = m.copy()
    for k in range(int(round(r / RES))):
        p = np.pad(out, 1, constant_values=False)
        e = out & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
        if k % 2:
            e &= p[:-2, :-2] & p[:-2, 2:] & p[2:, :-2] & p[2:, 2:]
        out = e
    return out


def grid(bb, pad=2.0):
    u = np.arange(bb[0] - pad, bb[1] + pad, RES)
    v = np.arange(bb[2] - pad, bb[3] + pad, RES)
    return np.meshgrid(u, v)


def bbox(polys):
    us = [p[0] for poly in polys for p in poly]
    vs = [p[1] for poly in polys for p in poly]
    return min(us), max(us), min(vs), max(vs)


def hex_fill(allowed, U, V, af, web):
    """flat-sided hex lattice (rev B pattern); keep a cell when its circumscribed disc is inside 'allowed'."""
    R = af / math.sqrt(3.0)
    ok = erode(allowed, R)
    px = 1.5 * (af + web) / math.sqrt(3.0)
    pz = af + web
    u0, v0 = U[0, 0], V[0, 0]
    cells = []
    u = U.min() + R
    col = 0
    while u < U.max() - R:
        v = V.min() + R + (0.5 * pz if col % 2 else 0.0)
        while v < V.max() - R:
            i = int(round((v - v0) / RES)); j = int(round((u - u0) / RES))
            if 0 <= i < ok.shape[0] and 0 <= j < ok.shape[1] and ok[i, j]:
                cells.append((round(u, 2), round(v, 2)))
            v += pz
        u += px
        col += 1
    return cells, 1.5 * math.sqrt(3.0) * R * R


def hex_poly(u, v, af):
    R = af / math.sqrt(3.0)
    return [(u + R * math.cos(math.radians(60 * k)), v + R * math.sin(math.radians(60 * k))) for k in range(6)]


# ---------------- pod side laminate ----------------
def side_groups(R):
    g = {}
    for n, e in R.items():
        if e.get("kind") != "laser" or not n[:3] in ("RO-", "LO-", "RI-", "LI-"):
            continue
        side = n[0]
        layer = "out" if n[1] == "O" else "in"
        seg = n[3]
        g.setdefault((side, seg), {"out": [], "in": []})[layer].append(n)
    return g


def world_x(e, U):
    o, x, y, z = e["frame"]
    return o[0] + U * x[0]


def side_allowed(R, names_out, names_in, side):
    es = [R[n] for n in names_out + names_in]
    U, V = grid(bbox([e["outline"] for e in es]))
    # 8 mm solid band at the panel's outer boundary (floor, top: rev B HEX_MARGIN); 3 mm at the butt joints between
    # pieces of one layer (each joint is bridged by the other layer) and round the slots in a piece
    a_out = np.zeros(U.shape, bool)
    a_in = np.zeros(U.shape, bool)
    u_out = np.zeros(U.shape, bool)
    for n in names_out + names_in:
        e = R[n]
        pm = part_mask(e, U, V)
        if n in names_out:
            u_out |= poly_mask(e["outline"], U, V)
        if e["mat"] != "balsa_med":
            continue                                         # ply grip / servo pieces stay solid
        m = erode(pm, JOINT_MARGIN)
        if n in names_out:
            a_out |= m
        else:
            a_in |= m
    allowed = a_out & a_in & erode(u_out, BP.HEX_MARGIN)
    X = world_x(es[0], U)
    Z = V                                                     # frame y axis is world +Z for every side piece
    allowed &= (X >= BP.HEX_X[0]) & (X <= BP.HEX_X[1])
    for a, b in FORMERS.values():
        allowed &= ~((X > a - BP.HEX_FRAME_CLEAR - 0.75) & (X < b + 0.75 + BP.HEX_FRAME_CLEAR))   # +0.75: 4.5 mm formers
    s = +1 if side == "R" else -1
    for x0, x1, z0, z1, sd in BP.HEX_SOLID:
        if sd in (0, s):
            allowed &= ~((X >= x0) & (X <= x1) & (Z >= z0) & (Z <= z1))
    return U, V, allowed


# ---------------- floor keep-solid zones ----------------
def floor_keep(e, U, V):
    X = world_x(e, U)
    keep = np.zeros(U.shape, bool)
    for a, b in (FP.SADDLE1_X, FP.SADDLE2_X):                 # saddle feet and their bearing (P1 finding)
        keep |= (X > a - 6) & (X < b + 6)
    keep |= np.abs(V) < BP.SKID_HW + 6                         # skid line
    for a, b in FORMERS.values():
        keep |= (X > a - 6) & (X < b + 6)
    return keep


def bh_keep(e, U, V):
    keep = np.zeros(U.shape, bool)
    for y in (-FP.SOCK_Y, FP.SOCK_Y):                          # boom tubes: tube ring OD 22 + 8 mm
        keep |= (U - y) ** 2 + (V - FP.SOCK_Z) ** 2 < (BP.TUBE_RING_OD / 2 + 8.0) ** 2
    return keep


def plot(name, e_list, U, V, allowed, cells, af, fn):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 8 * (V.max() - V.min()) / max(1, (U.max() - U.min())) + 1))
    for e in e_list:
        o = e["outline"] + [e["outline"][0]]
        ax.plot([p[0] for p in o], [p[1] for p in o], "k-", lw=0.6)
        for h in e.get("holes", []):
            if h[0] == "p":
                hh = h[1] + [h[1][0]]
                ax.plot([p[0] for p in hh], [p[1] for p in hh], "k-", lw=0.4)
            else:
                t = np.linspace(0, 2 * np.pi, 40)
                ax.plot(h[1] + h[3] * np.cos(t), h[2] + h[3] * np.sin(t), "k-", lw=0.4)
    ax.contourf(U, V, allowed.astype(float), levels=[0.5, 1.5], colors=["#cfe3f5"], alpha=0.6)
    for u, v in cells:
        hp = hex_poly(u, v, af) + [hex_poly(u, v, af)[0]]
        ax.fill([p[0] for p in hp], [p[1] for p in hp], color="#d6604d", lw=0)
    ax.set_aspect("equal")
    ax.set_title(name, fontsize=9)
    ax.set_xlabel("u (mm)"); ax.set_ylabel("v (mm)")
    fig.tight_layout()
    fig.savefig(fn, dpi=110)
    plt.close(fig)


def main():
    R = registry()
    os.makedirs(FIG, exist_ok=True)
    rows, cells_out = [], {}
    # pod sides
    g = side_groups(R)
    tot_area = 0.0
    n_cells = 0
    side_cells = {}
    for (side, seg), d in sorted(g.items()):
        U, V, allowed = side_allowed(R, d["out"], d["in"], side)
        cells, a1 = hex_fill(allowed, U, V, BP.HEX_AF, BP.HEX_WEB)
        side_cells["%s-%s" % (side, seg)] = cells
        tot_area += len(cells) * a1
        n_cells += len(cells)
        plot("Pod side %s, segment %s: %d cells" % (side, seg, len(cells)), [R[n] for n in d["out"] + d["in"]], U, V,
             allowed, cells, BP.HEX_AF, os.path.join(FIG, "side_%s_%s.png" % (side, seg)))
    t_lam = 1.5 + 1.5
    dm = tot_area * t_lam * RHO * 1e-3 * (1 + GLUE_FRAC_POD) - tot_area * 1e-6 * FILM_IN
    rows.append(dict(group=GROUPS[0][0], parts="RO-/LO-/RI-/LI-", cells=n_cells, area_cm2=round(tot_area / 100, 1),
                     saved_g=round(dm, 2), cell="8 / 2.5", note="both layers 1.5 + 1.5 (P1); film inner face 30 g/m2 counted"))
    cells_out["sides"] = side_cells
    # other groups
    for name, test, af, web, marg, t, note in GROUPS[1:]:
        names = [n for n, e in R.items() if e.get("kind") == "laser" and test(n)]
        area = 0.0
        nc = 0
        for n in names:
            e = R[n]
            U, V = grid(bbox([e["outline"]]))
            m = erode(part_mask(e, U, V), marg)
            if n.startswith("FL-"):
                m &= ~floor_keep(e, U, V)
            if n == "BH":
                m &= ~bh_keep(e, U, V)
            cells, a1 = hex_fill(m, U, V, af, web)
            cells_out[n] = cells
            area += len(cells) * a1
            nc += len(cells)
            if cells:
                plot("%s: %d cells %g/%g" % (n, len(cells), af, web), [e], U, V, m, cells, af, os.path.join(FIG, "%s.png" % n))
        pod = names and R[names[0]]["assembly"] == "Pod"
        dm = area * t * RHO * 1e-3 * ((1 + GLUE_FRAC_POD) if pod else 1.0)
        rows.append(dict(group=name, parts=" ".join(names), cells=nc, area_cm2=round(area / 100, 1), saved_g=round(dm, 2),
                         cell="%g / %g" % (af, web), note=note + ("" if pod else "; film over the holes is already on the surface")))
    with open(os.path.join(HERE, "p2_cutouts.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    json.dump(cells_out, open(os.path.join(HERE, "p2_cells.json"), "w"), indent=0)
    for r in rows:
        print("%-52s cells %4d  area %6.1f cm2  saved %6.2f g  (%s) %s" % (r["group"], r["cells"], r["area_cm2"],
              r["saved_g"], r["cell"], r["note"]))
    print("total %.1f g" % sum(r["saved_g"] for r in rows))


if __name__ == "__main__":
    main()
