"""Laser cut files for the rev B Fusion model, from the same part data the Fusion model is built from (pod.py,
wing.py, tail.py). Plain Python, no Fusion needed:  python laser.py
Writes ../dxf/<material>_<t>mm_sheetNN.dxf (DXF R12, mm) with layers
  CUT      part outlines, slots, holes (closed polylines, circles)
  ENGRAVE  part names in a single-stroke font (open polylines: score / low-power line, not a fill)
  SHEET    sheet outline (do not cut)
and ../dxf/nesting.json + ../cut_list.md. Each part is drawn as seen from its labelled face (lay that face up).
Balsa: 100 x 300 sheets, grain along the 300 side; every balsa part is turned so its grain runs along the sheet.
Ply and lite-ply: 300 x 300 sheets, any orientation."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.dirname(os.path.dirname(HERE))
for p in ("cad_fuselage_balsa/scripts", "cad_fuselage/scripts", "cad_reservoir/scripts", "cad/scripts"):
    sys.path.insert(0, os.path.join(DESIGN, p))
sys.path.insert(0, HERE)
import geo as G       # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "dxf")
SHEETS = {"balsa": (300.0, 100.0), "ply": (300.0, 300.0)}
GAP, MARGIN = 3.0, 3.0

# ---------------- single-stroke font (4 x 6 grid) ----------------
_O = [(1, 0), (0, 1), (0, 5), (1, 6), (3, 6), (4, 5), (4, 1), (3, 0), (1, 0)]
_P = [(0, 0), (0, 6), (3, 6), (4, 5), (4, 4), (3, 3), (0, 3)]
FONT = {
    "A": [[(0, 0), (0, 4), (2, 6), (4, 4), (4, 0)], [(0, 3), (4, 3)]],
    "B": [[(0, 0), (0, 6), (3, 6), (4, 5), (4, 4), (3, 3), (0, 3)], [(3, 3), (4, 2), (4, 1), (3, 0), (0, 0)]],
    "C": [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0), (3, 0), (4, 1)]],
    "D": [[(0, 0), (0, 6), (3, 6), (4, 5), (4, 1), (3, 0), (0, 0)]],
    "E": [[(4, 6), (0, 6), (0, 0), (4, 0)], [(0, 3), (3, 3)]],
    "F": [[(4, 6), (0, 6), (0, 0)], [(0, 3), (3, 3)]],
    "G": [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0), (3, 0), (4, 1), (4, 3), (2, 3)]],
    "H": [[(0, 0), (0, 6)], [(4, 0), (4, 6)], [(0, 3), (4, 3)]],
    "I": [[(1, 6), (3, 6)], [(2, 6), (2, 0)], [(1, 0), (3, 0)]],
    "J": [[(4, 6), (4, 1), (3, 0), (1, 0), (0, 1)]],
    "K": [[(0, 0), (0, 6)], [(4, 6), (0, 2)], [(1, 3), (4, 0)]],
    "L": [[(0, 6), (0, 0), (4, 0)]],
    "M": [[(0, 0), (0, 6), (2, 3), (4, 6), (4, 0)]],
    "N": [[(0, 0), (0, 6), (4, 0), (4, 6)]],
    "O": [_O],
    "P": [_P],
    "Q": [_O, [(2, 2), (4, 0)]],
    "R": [_P, [(2, 3), (4, 0)]],
    "S": [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 4), (1, 3), (3, 3), (4, 2), (4, 1), (3, 0), (1, 0), (0, 1)]],
    "T": [[(0, 6), (4, 6)], [(2, 6), (2, 0)]],
    "U": [[(0, 6), (0, 1), (1, 0), (3, 0), (4, 1), (4, 6)]],
    "V": [[(0, 6), (2, 0), (4, 6)]],
    "W": [[(0, 6), (1, 0), (2, 3), (3, 0), (4, 6)]],
    "X": [[(0, 0), (4, 6)], [(0, 6), (4, 0)]],
    "Y": [[(0, 6), (2, 3), (4, 6)], [(2, 3), (2, 0)]],
    "Z": [[(0, 6), (4, 6), (0, 0), (4, 0)]],
    "0": [_O, [(0, 1), (4, 5)]],
    "1": [[(1, 5), (2, 6), (2, 0)], [(1, 0), (3, 0)]],
    "2": [[(0, 5), (1, 6), (3, 6), (4, 5), (4, 4), (0, 0), (4, 0)]],
    "3": [[(0, 5), (1, 6), (3, 6), (4, 5), (4, 4), (3, 3), (4, 2), (4, 1), (3, 0), (1, 0), (0, 1)], [(1, 3), (3, 3)]],
    "4": [[(3, 0), (3, 6), (0, 2), (4, 2)]],
    "5": [[(4, 6), (0, 6), (0, 3), (3, 3), (4, 2), (4, 1), (3, 0), (0, 0)]],
    "6": [[(4, 5), (3, 6), (1, 6), (0, 5), (0, 1), (1, 0), (3, 0), (4, 1), (4, 2), (3, 3), (0, 3)]],
    "7": [[(0, 6), (4, 6), (1, 0)]],
    "8": [[(1, 3), (0, 4), (0, 5), (1, 6), (3, 6), (4, 5), (4, 4), (3, 3), (1, 3), (0, 2), (0, 1), (1, 0), (3, 0), (4, 1), (4, 2), (3, 3)]],
    "9": [[(0, 1), (1, 0), (3, 0), (4, 1), (4, 5), (3, 6), (1, 6), (0, 5), (0, 4), (1, 3), (4, 3)]],
    "-": [[(0.5, 3), (3.5, 3)]],
    "<": [[(3.5, 5), (0.5, 3), (3.5, 1)]],
    ">": [[(0.5, 5), (3.5, 3), (0.5, 1)]],
    "^": [[(0.5, 3), (2, 6), (3.5, 3)]],
    "/": [[(0, 0), (4, 6)]],
}
ADV, LINE = 5.5, 9.0


def stroke_text(text, uc, vc, h):
    """Open polylines for text centred at (uc, vc), cap height h, along +u."""
    k = h / 6.0
    lines = text.split("\n")
    out = []
    total_h = (len(lines) - 1) * LINE * k + h
    for li, line in enumerate(lines):
        w = (len(line) * ADV - 1.5) * k
        u0 = uc - w / 2
        v0 = vc + total_h / 2 - h - li * LINE * k
        for ci, ch in enumerate(line):
            small = ch.islower()
            g = FONT.get(ch.upper())
            if not g:
                continue
            s = 0.7 if small else 1.0
            for stroke in g:
                out.append([(u0 + (ci * ADV + x * s) * k, v0 + y * s * k) for x, y in stroke])
    return out


# ---------------- DXF ----------------
class DXF:
    def __init__(self):
        self.L = ["0", "SECTION", "2", "HEADER", "9", "$ACADVER", "1", "AC1009", "9", "$INSUNITS", "70", "4", "0", "ENDSEC",
                  "0", "SECTION", "2", "TABLES", "0", "TABLE", "2", "LAYER", "70", "3"]
        for name, col in (("CUT", 1), ("ENGRAVE", 5), ("SHEET", 8)):
            self.L += ["0", "LAYER", "2", name, "70", "0", "62", str(col), "6", "CONTINUOUS"]
        self.L += ["0", "ENDTAB", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]

    def poly(self, pts, layer="CUT", closed=True):
        self.L += ["0", "POLYLINE", "8", layer, "66", "1", "70", "1" if closed else "0", "10", "0.0", "20", "0.0", "30", "0.0"]
        for x, y in pts:
            self.L += ["0", "VERTEX", "8", layer, "10", "%.4f" % x, "20", "%.4f" % y, "30", "0.0"]
        self.L += ["0", "SEQEND", "8", layer]

    def circle(self, x, y, r, layer="CUT"):
        self.L += ["0", "CIRCLE", "8", layer, "10", "%.4f" % x, "20", "%.4f" % y, "30", "0.0", "40", "%.4f" % r]

    def save(self, path):
        with open(path, "w") as f:
            f.write("\n".join(self.L + ["0", "ENDSEC", "0", "EOF"]) + "\n")


# ---------------- which parts go to the laser, grain ----------------
LASER_MATS = {"balsa_med": "balsa medium", "balsa_light": "balsa light", "ply": "birch ply", "liteply": "lite-ply"}
NOT_LASER = ("Keel", "Longeron", "Capstrip", "Ledge", "LE", "DBOX", "CAP-", "TE-", "CS-", "CAPS-", "AIL-LE", "AIL-TE",
             "SERVO-", "TB-", "TAILBLOCK", "NOSE-RING")


def grain_axis(name):
    """'u', 'v' or None (ply: any). Balsa grain runs along this local axis of the part outline."""
    n = name
    if n[:3] in ("RO-", "LO-") or n.startswith(("HN-", "FSP-", "W-", "A1", "A2", "A3", "A4", "AH-")):
        return "u"
    if n[:3] in ("RI-", "LI-") or n.startswith(("FL-", "HF", "DECK", "WF-", "WR-", "STAB", "ELEV", "FIN", "RUDDER")):
        return "v"
    return "u"


def laser_parts():
    import pod
    import wing
    import tail
    out = []
    import linkage
    for src in (pod.all_parts()[0], wing.all_parts()[0], tail.all_parts()[0], linkage.wing_parts()[0]):
        for p in src:
            if p["mat"] not in LASER_MATS or p["name"].startswith(NOT_LASER):
                continue
            out.append(p)
    return out


LOOPS = {}


def load_loops():
    """Exact cut loops exported from the Fusion bodies (laser_loops.py). Without them the DXF would draw the raw
    cutter shapes, which are wrong where a cutter crosses the part edge - so the loops are required."""
    path = os.path.join(OUT, "loops.json")
    if os.path.exists(path):
        LOOPS.update(json.load(open(path)))
    return len(LOOPS)


def transform(p, rot):
    """Part geometry in its local (u, v), rotated by rot (0 / 90 deg) and moved to start at (0, 0)."""
    def r(pt):
        return (pt[0], pt[1]) if not rot else (-pt[1], pt[0])
    lp = LOOPS.get(p["name"])
    if lp:
        outer = [l for l in lp if l["outer"]][0]["pts"]
        outline = [r(q) for q in outer]
    else:
        outline = [r(q) for q in p["outline"]]
    u0, u1, v0, v1 = G.bbox(outline)
    sh = lambda pt: (pt[0] - u0, pt[1] - v0)
    geo = dict(outline=[sh(q) for q in outline], polys=[], circles=[], text=[])
    if lp:
        geo["polys"] = [[sh(r(q)) for q in l["pts"]] for l in lp if not l["outer"]]
        for txt, u, v, h in p["labels"]:
            for st in stroke_text(txt, u, v, h):
                geo["text"].append([sh(r(q)) for q in st])
        return geo, (u1 - u0, v1 - v0)
    for c in p["cutters"]:
        if isinstance(c, tuple) and c[0] == "circle":
            cx, cy = sh(r((c[1], c[2])))
            geo["circles"].append((cx, cy, c[3]))
        else:
            geo["polys"].append([sh(r(q)) for q in c])
    for txt, u, v, h in p["labels"]:
        for st in stroke_text(txt, u, v, h):
            geo["text"].append([sh(r(q)) for q in st])
    return geo, (u1 - u0, v1 - v0)


def clip_cutters_to_outline(geo):
    """Cutters that reach outside the outline are already part of the outline cut (open slots): keep only those
    fully inside, others are merged by the laser as overlapping cuts (harmless) - drop the ones fully outside."""
    u0, u1, v0, v1 = G.bbox(geo["outline"])
    keep = []
    for q in geo["polys"]:
        a, b, c, d = G.bbox(q)
        if b < u0 or a > u1 or d < v0 or c > v1:
            continue
        keep.append(q)
    geo["polys"] = keep


def nest():
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".dxf"):
            os.remove(os.path.join(OUT, f))
    groups = {}
    for p in laser_parts():
        key = (p["mat"], round(p["t"], 2))
        groups.setdefault(key, []).append(p)
    report, sheets_out = [], []
    for (mat, t), parts in sorted(groups.items()):
        kind = "balsa" if mat.startswith("balsa") else "ply"
        SW, SH = SHEETS[kind]
        items = []
        for p in parts:
            ga = grain_axis(p["name"]) if kind == "balsa" else None
            opts = [0, 1] if ga is None else ([0] if ga == "u" else [1])
            best = None
            for rot in opts:
                geo, (w, h) = transform(p, rot)
                if w <= SW - 2 * MARGIN and h <= SH - 2 * MARGIN:
                    if best is None or h < best[2]:
                        best = (geo, w, h, rot)
            if best is None:
                report.append("DOES NOT FIT %s (%s %.1f mm): %.1f x %.1f" % (p["name"], mat, t, *transform(p, opts[0])[1]))
                continue
            if not LOOPS:
                clip_cutters_to_outline(best[0])
            items.append((p["name"], *best))
        # shelf packing, tallest first
        items.sort(key=lambda it: (-it[3], -it[2]))
        sheets = []
        for it in items:
            name, geo, w, h, rot = it
            placed = False
            for sh in sheets:
                for shelf in sh["shelves"]:
                    if h <= shelf["h"] and shelf["x"] + w <= SW - MARGIN:
                        sh["parts"].append((name, geo, shelf["x"], shelf["y"], rot))
                        shelf["x"] += w + GAP
                        placed = True
                        break
                if placed:
                    break
                if sh["top"] + h <= SH - MARGIN:
                    shelf = dict(y=sh["top"], h=h, x=MARGIN + w + GAP)
                    sh["shelves"].append(shelf)
                    sh["parts"].append((name, geo, MARGIN, sh["top"], rot))
                    sh["top"] += h + GAP
                    placed = True
                    break
            if not placed:
                sh = dict(shelves=[dict(y=MARGIN, h=h, x=MARGIN + w + GAP)], parts=[(name, geo, MARGIN, MARGIN, rot)], top=MARGIN + h + GAP)
                sheets.append(sh)
        tag = "%s_%gmm" % (LASER_MATS[mat].replace(" ", "-"), t)
        for k, sh in enumerate(sheets):
            dx = DXF()
            dx.poly([(0, 0), (SW, 0), (SW, SH), (0, SH)], "SHEET")
            for name, geo, x, y, rot in sh["parts"]:
                mv = lambda q: (q[0] + x, q[1] + y)
                dx.poly([mv(q) for q in geo["outline"]], "CUT")
                for q in geo["polys"]:
                    dx.poly([mv(c) for c in q], "CUT")
                for cx, cy, r in geo["circles"]:
                    dx.circle(cx + x, cy + y, r, "CUT")
                for st in geo["text"]:
                    dx.poly([mv(c) for c in st], "ENGRAVE", closed=False)
            fn = "%s_sheet%02d.dxf" % (tag, k + 1)
            dx.save(os.path.join(OUT, fn))
            sheets_out.append(dict(file=fn, material=LASER_MATS[mat], t=t, sheet=[SW, SH],
                                   parts=[dict(name=n, x=round(x, 1), y=round(y, 1), rot90=bool(r)) for n, g, x, y, r in sh["parts"]]))
        report.append("%-13s %4.1f mm: %3d parts on %d sheet(s) of %g x %g" % (LASER_MATS[mat], t, len(items), len(sheets), SW, SH))
    json.dump(sheets_out, open(os.path.join(OUT, "nesting.json"), "w"), indent=1)
    return report, sheets_out


if __name__ == "__main__":
    n = load_loops()
    print("exact loops for %d parts" % n if n else "WARNING: no loops.json - run laser_loops.py in Fusion first")
    rep, sh = nest()
    print("\n".join(rep))
    print(sum(len(s["parts"]) for s in sh), "parts on", len(sh), "sheets ->", OUT)


def strip_stock():
    """Non-laser wooden parts (strip / sheet stock cut to length) from the part data."""
    import pod
    import wing
    import tail
    rows = []
    for src in (pod.all_parts()[0], wing.all_parts()[0], tail.all_parts()[0]):
        for p in src:
            if p["mat"] in LASER_MATS and p["name"].startswith(NOT_LASER):
                u0, u1, v0, v1 = G.bbox(p["outline"])
                rows.append((p["name"], LASER_MATS[p["mat"]], "%.1f x %.1f" % (u1 - u0, v1 - v0), round(p["t"], 1)))
    return rows


def write_cut_list(rep, sheets):
    lines = ["# Rev B (Fusion) - laser cut list", "",
             "Generated by `scripts/laser.py` from the Fusion part data; cut geometry = the exact part loops exported from "
             "the Fusion bodies (`scripts/laser_loops.py`). DXF R12, mm, in `dxf/`: layer **CUT** (through), **ENGRAVE** "
             "(single-stroke names, score at low power), **SHEET** (outline, do not cut). Lay each part's engraved face up.",
             "", "Balsa sheets 100 x 300 mm with the grain along the 300 side (parts are already turned to their grain); "
             "ply / lite-ply 300 x 300. Kerf: the slots are drawn at the nominal stock thickness - set the laser's kerf "
             "offset so the tabs are a push fit.", "", "| Group | Parts | Sheets |", "|---|---|---|"]
    for r in rep:
        if "parts on" in r:
            g, rest = r.split(":")
            n = rest.split("parts")[0].strip()
            k = rest.split("on")[1].split("sheet")[0].strip()
            lines.append("| %s | %s | %s |" % (" ".join(g.split()), n, k))
        else:
            lines.append("| **%s** | | |" % r)
    lines += ["", "## Sheets", "", "| File | Parts |", "|---|---|"]
    for s in sheets:
        lines.append("| `%s` | %s |" % (s["file"], ", ".join(p["name"] for p in s["parts"])))
    lines += ["", "## Strip and sheet stock (not on the laser; cut to length)", "", "| Part | Material | Section (mm) | Length (mm) |",
              "|---|---|---|---|"]
    for n, m, sec, L in strip_stock():
        lines.append("| %s | %s | %s | %s |" % (n, m, sec, L))
    open(os.path.join(os.path.dirname(OUT), "cut_list.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    write_cut_list(rep, sh)
