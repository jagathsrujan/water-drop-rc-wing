"""P1 single-stock study: table of every wooden part of the rev B Fusion model, from the part data.

Reads the build-kit registry (tools/build_kit/kit_data.py -> pod.py / wing.py / tail.py part data, masses from
design/cad_fusion_revB/check/bodies.json) and writes
  p1_parts.csv          one row per wooden part (balsa, birch ply, lite-ply)
  p1_groups.csv         the same summed by assembly / group / material / thickness
and prints a summary. Plain Python:  python design/optimisation/p1_parts.py
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools", "build_kit"))
import kit_data as K  # noqa: E402

WOOD = ("balsa_med", "balsa_light", "balsa_hard", "ply", "liteply")
RHO = {"balsa_med": 0.14, "balsa_light": 0.10, "balsa_hard": 0.16, "ply": 0.65, "liteply": 0.45}  # g/cm3, mass_summary.py

# Load class (P1 judgement, see P1_single_stock.md section 2): P = primary flight / landing / water load path,
# S = secondary (shape, stiffening, covering support), L = locating only (saddle layers, tip caps, keys).
LOAD = [
    ("FS", "P", "front stop: 1 L water nose-in decel (10 g) + launch grip"),
    ("BH", "P", "bulkhead: boom root bending/torsion, tail loads"),
    ("EF", "P", "end former: boom second support"),
    ("FW", "P", "firewall: motor thrust + torque, nose-in impact"),
    ("NOSE", "P", "nose ring"),
    ("B1", "P", "former: wing band loads, side shear"), ("B2", "P", "former: hatch / wing seat"),
    ("B4", "P", "former: saddle 2 / bottle"), ("N1", "S", "nose former"), ("N2", "S", "nose former"),
    ("RO-MP", "P", "side grip zone ply insert (hand launch)"), ("RS-", "P", "servo-zone ply insert"),
    ("FL-", "P", "floor: water bottle bearing, landing"), ("RO-", "P", "outer side laminate: pod bending shear"),
    ("LO-", "P", "outer side laminate"), ("RI-", "P", "inner side laminate"), ("LI-", "P", "inner side laminate"),
    ("Keel", "P", "keel strips: pod bending flange"), ("Longeron", "P", "longerons: pod bending flange"),
    ("Capstrip", "P", "side top flange / wing seat"), ("Ledge", "S", "floor ledge"),
    ("DECK", "S", "aft deck"), ("HN", "S", "hatch"), ("HF", "S", "hatch frame"), ("HA", "S", "hatch"),
    ("BT", "S", "battery tray"), ("TST", "S", "tail-servo tray"), ("SK", "S", "skid"),
    ("S1", "L", "saddle layer (bottle cradle; bottle mass in bearing)"), ("S2", "L", "saddle layer"),
    ("SB", "S", "strap bridge"),
    ("W-R", "P", "wing rib"), ("FSP", "P", "false spar (hinge line, aileron loads)"),
    ("WEB", "P", "spar shear web"), ("SW", "P", "spar shear web"),
    ("CAP-", "P", "spar cap (wing bending)"), ("DBOX", "P", "D-box skin (wing torsion)"), ("LE", "P", "leading edge"),
    ("CS-", "S", "centre-section sheeting (band bearing)"), ("CAPS-", "S", "rib cap strip"),
    ("TE-", "S", "trailing edge"), ("AIL", "S", "aileron"), ("AH-", "S", "aileron horn rib"),
    ("W-TIP", "L", "wing tip block"), ("ELEV", "S", "elevator"), ("RUDDER", "S", "rudder"),
    ("TRAY", "S", "battery tray"), ("FLAPSTOP", "P", "release-flap stop (water load on flap)"),
    ("SD-", "P", "stub doubler: front wing-band stub bearing"), ("TR", "P", "boom tube ring (boom bearing)"),
    ("W-C", "P", "centre rib (band seat)"), ("WF-", "P", "front spar shear web"), ("WR-", "P", "rear shear web"),
    ("A1", "S", "aileron rib"), ("A2", "S", "aileron rib"), ("A3", "S", "aileron rib"), ("A4", "S", "aileron rib"),
    ("HORN", "S", "tail horn"),
    ("STAB", "P", "stabiliser (tail load)"), ("FIN", "P", "fin"), ("SERVO", "S", "servo bay"),
]


def load_of(name):
    best = None
    for pre, c, why in LOAD:
        if name.startswith(pre) and (best is None or len(pre) > len(best[0])):
            best = (pre, c, why)
    return (best[1], best[2]) if best else ("?", "")


def stock(e, n):
    if e["kind"] == "strip":
        desc, th, w, L = K.strip_dims(n, e)
        return desc, round(th, 2), round(w, 1), round(L, 1)
    return "laser sheet", e["t"], "", ""


def main():
    R = K.build_registry()
    rows = []
    for n in R.order:
        e = R[n]
        if e["mat"] not in WOOD or e["kind"] not in ("laser", "strip"):
            continue
        desc, th, w, L = stock(e, n)
        c, why = load_of(n)
        m = e.get("mass_g") or 0.0
        area_cm2 = m / RHO[e["mat"]] / (th / 10.0) if th else 0.0     # planform (one face) area
        rows.append(dict(name=n, assembly=e["assembly"], grp=e["grp"], kind=e["kind"], mat=e["mat"], t_mm=th,
                         w_mm=w, len_mm=L, stock=desc, mass_g=round(m, 2), area_cm2=round(area_cm2, 1), load=c, role=why))
    with open(os.path.join(HERE, "p1_parts.csv"), "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    groups = {}
    for r in rows:
        k = (r["assembly"], r["mat"], r["t_mm"], r["kind"])
        g = groups.setdefault(k, dict(assembly=k[0], mat=k[1], t_mm=k[2], kind=k[3], n=0, mass_g=0.0, area_cm2=0.0, names=[]))
        g["n"] += 1
        g["mass_g"] += r["mass_g"]
        g["area_cm2"] += r["area_cm2"]
        g["names"].append(r["name"])
    with open(os.path.join(HERE, "p1_groups.csv"), "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["assembly", "mat", "t_mm", "kind", "n", "mass_g", "area_cm2", "parts"])
        for k in sorted(groups):
            g = groups[k]
            wr.writerow([g["assembly"], g["mat"], g["t_mm"], g["kind"], g["n"], round(g["mass_g"], 1),
                         round(g["area_cm2"], 0), " ".join(g["names"])])
    for k in sorted(groups):
        g = groups[k]
        print("%-5s %-11s %5.2f %-6s n=%3d  %6.1f g  %6.0f cm2  %s" % (g["assembly"], g["mat"], g["t_mm"], g["kind"], g["n"],
              g["mass_g"], g["area_cm2"], " ".join(g["names"])[:140]))
    unk = [r["name"] for r in rows if r["load"] == "?"]
    print("total wood parts", len(rows), "mass %.1f g" % sum(r["mass_g"] for r in rows), "unclassified:", unk)


if __name__ == "__main__":
    main()
