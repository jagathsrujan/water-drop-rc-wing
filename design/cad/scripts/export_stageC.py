"""Stage C - outputs: STEP, laser DXF (balsa flat parts nested on 300 x 100 sheets by thickness/grade),
STL of PETG parts, cut list for strip stock. Run inside FreeCAD after build_stageA/B."""
import sys, os, math, importlib, json
SCRIPTS = globals().get("WING_SCRIPTS") or os.environ.get("WING_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import wing_params as P, wing_geom as G, wing_build as B, dxf_io
for m in (P, G, B, dxf_io):
    importlib.reload(m)
import FreeCAD as App
import Part
from FreeCAD import Vector as V

d = B.doc()
CAD = P.CAD
os.makedirs(os.path.join(CAD, "dxf"), exist_ok=True)
os.makedirs(os.path.join(CAD, "stl"), exist_ok=True)
REPORT = []
pr = lambda *a: (REPORT.append(" ".join(str(x) for x in a)), print(*a))
obj = d.getObject

# ---------------- STEP ----------------
import Import
feats = [o for o in d.Objects if o.TypeId == "Part::Feature"]
step_path = os.path.join(CAD, "Wing_revA.step")
Import.export(feats, step_path)
pr("STEP:", step_path, "(%d parts, MG90S placeholder included)" % len(feats), round(os.path.getsize(step_path) / 1e6, 2), "MB")

# ---------------- flat-part profiles ----------------
AX = {"Y": V(0, 1, 0), "X": V(1, 0, 0)}


def loops(solid, axis):
    """2D loops of the end face normal to axis: [('poly', pts) | ('circle', (u, v, r))], face area, thickness."""
    a = AX[axis]
    cands = [f for f in solid.Faces if f.Surface.__class__.__name__ == "Plane" and abs(f.normalAt(0, 0).dot(a)) > 0.9999]
    key = (lambda f: f.CenterOfMass.y) if axis == "Y" else (lambda f: f.CenterOfMass.x)
    f = min(cands, key=key)
    uv = (lambda p: (p.x, p.z)) if axis == "Y" else (lambda p: (p.y, p.z))
    out = []
    for w in [f.OuterWire] + [w for w in f.Wires if not w.isSame(f.OuterWire)]:
        if len(w.Edges) == 1 and w.Edges[0].Curve.__class__.__name__ == "Circle":
            c = w.Edges[0].Curve
            u, v = uv(c.Center)
            out.append(("circle", (u, v, c.Radius)))
        else:
            pts = [uv(p) for p in w.discretize(Deflection=0.01)]
            if (abs(pts[0][0] - pts[-1][0]) < 1e-6) and (abs(pts[0][1] - pts[-1][1]) < 1e-6):
                pts = pts[:-1]
            out.append(("poly", pts))
    bb = solid.BoundBox
    t = bb.YLength if axis == "Y" else bb.XLength
    return out, f.Area, t


def bbox2(lp):
    xs, ys = [], []
    for k, g in lp:
        if k == "poly":
            xs += [p[0] for p in g]; ys += [p[1] for p in g]
        else:
            xs += [g[0] - g[2], g[0] + g[2]]; ys += [g[1] - g[2], g[1] + g[2]]
    return min(xs), min(ys), max(xs), max(ys)


def xform(lp, rot90):
    """Normalize to the origin; rot90 turns the part so its v axis runs along the sheet X (grain)."""
    if rot90:
        lp = [(k, [(v, -u) for u, v in g]) if k == "poly" else (k, (g[1], -g[0], g[2])) for k, g in lp]
    x0, y0, x1, y1 = bbox2(lp)
    lp = [(k, [(u - x0, v - y0) for u, v in g]) if k == "poly" else (k, (g[0] - x0, g[1] - y0, g[2])) for k, g in lp]
    return lp, x1 - x0, y1 - y0


PARTS = []   # dicts: label, group, loops, w, h, check(area vs vol/t)


def add(label, group, solid, axis, rot90=False, area_check=True):
    lp, area, t = loops(solid, axis)
    lp, w, h = xform(lp, rot90)
    err = abs(area - solid.Volume / t) if area_check else 0.0
    PARTS.append(dict(label=label, group=group, loops=lp, w=w, h=h, err=err))


def ycut(shape, ya, yb):
    bb = shape.BoundBox
    return shape.common(Part.makeBox(bb.XLength + 2, yb - ya, bb.ZLength + 2, V(bb.XMin - 1, ya, bb.ZMin - 1)))


def xcut(shape, xa, xb):
    bb = shape.BoundBox
    return shape.common(Part.makeBox(xb - xa, bb.YLength + 2, bb.ZLength + 2, V(xa, bb.YMin - 1, bb.ZMin - 1)))


# wing ribs (grain chord-wise: u = x along the sheet length)
for o in feats:
    n = o.Name
    if n.startswith(("Rib_", "RibAft_")):
        t = round(o.Shape.BoundBox.YLength, 2)
        add(n.replace("Rib_", "R").replace("RibAft_", "RA"), "%gmm_medium" % t, o.Shape, "Y")
    elif n.startswith(("Ail_Ribs_", "Ail_HornRib_")):
        for i, s in enumerate(o.Shape.Solids):
            add("%s%d" % ("AR" if "Ribs" in n else "AH", i) + n[-2:], "2mm_medium", s, "Y")
    elif n.startswith("TipCap_"):
        add("TC" + n[-2:], "3mm_light", o.Shape, "Y")
    elif n.startswith(("TipRib_", "TipRibAft_")):
        sh = o.Shape
        y0 = sh.BoundBox.YMin
        layer = ycut(sh, y0, y0 + 1.5)
        tag = "TR" if n.startswith("TipRib_") else "TRA"
        add(tag + "a" + n[-2:], "1.5mm_light", layer, "Y")                       # layer A, grain chord-wise
        if n.startswith("TipRib_"):
            for j, (xa, xb) in enumerate(((0, 75.6), (75.6, 140.0), (140.0, 210.0))):  # layer B, grain vertical
                add(tag + "b%d" % j + n[-2:], "1.5mm_light", xcut(layer, xa, xb), "Y", rot90=True)
        else:
            add(tag + "b" + n[-2:], "1.5mm_light", layer, "Y", rot90=True)
    elif n.startswith("ShearWeb"):
        for i, s in enumerate(o.Shape.Solids):
            add("W%s%d" % ("F" if "Front" in n else "B", i), "1.5mm_medium", s, "X", rot90=True)   # vertical grain

# false spar pieces between rib centre lines (vertical grain, <= 100 mm), hinge slots included
br = [0.0] + [y for y, t in P.RIBS] + [P.Y_END]
brk = sorted(set([-b for b in br] + br))
fs = obj("FalseSpar").Shape
for i, (a, b) in enumerate(zip(brk, brk[1:])):
    add("FS%02d" % i, "3mm_medium", ycut(fs, a, b), "X", rot90=True)

# centre sheeting: developed rectangles (grain chord-wise), wire exit hole on the bottom front pieces
def arc_len(x0, x1, upper, n=400):
    pts = [(x0 + (x1 - x0) * i / n) for i in range(n + 1)]
    zs = [G.surf_z(x, upper) for x in pts]
    return sum(math.hypot(pts[i + 1] - pts[i], zs[i + 1] - zs[i]) for i in range(n))
for o in feats:
    if not o.Name.startswith("CSheet_"):
        continue
    up = "_Top_" in o.Name
    xa, xb = (P.X_DBOX, P.X_FS[0]) if "_Fwd_" in o.Name else (P.X_FS[1], P.X_TE)
    L = arc_len(xa, xb, up)
    W = P.Y_CSHEET
    lp = [("poly", [(0, 0), (L, 0), (L, W), (0, W)])]
    if (not up) and "_Fwd_" in o.Name:
        wx, wy, wd = P.WIRE_EXIT
        lp.append(("circle", (arc_len(xa, wx, False), wy, wd / 2)))
    vol_dev = L * W * P.SKIN_T
    PARTS.append(dict(label=o.Name.replace("CSheet_", "CS"), group="1.5mm_selected-light", loops=lp, w=L, h=W,
                      err=0.0, devnote="developed %.1f x %.1f (model volume %.0f, developed %.0f mm3)" % (L, W, o.Shape.Volume, vol_dev)))

bad = [p for p in PARTS if p["err"] > 0.5]
pr("flat parts:", len(PARTS), "; profile area check failures:", [(p["label"], round(p["err"], 2)) for p in bad])

# ---------------- nesting: shelf packing on 300 x 100 sheets ----------------
SW, SH, MARGIN, GAP = 300.0, 100.0, 3.0, 3.0
groups = {}
for p in PARTS:
    groups.setdefault(p["group"], []).append(p)
summary = {}
for gname, plist in sorted(groups.items()):
    plist.sort(key=lambda p: (-p["h"], -p["w"]))
    sheets = []   # each: list of shelves [y, h, x_used, parts]
    for p in plist:
        if p["w"] > SW - 2 * MARGIN + 1e-6 or p["h"] > SH - 2 * MARGIN + 1e-6:
            raise RuntimeError("part %s %.1f x %.1f does not fit a sheet" % (p["label"], p["w"], p["h"]))
        placed = False
        for sh in sheets:
            for shelf in sh:
                if p["h"] <= shelf[1] + 1e-6 and shelf[2] + p["w"] <= SW - MARGIN + 1e-6:
                    p["pos"] = (shelf[2], shelf[0]); shelf[2] += p["w"] + GAP; shelf[3].append(p); placed = True
                    break
            if placed:
                break
            ytop = sh[-1][0] + sh[-1][1] + GAP
            if ytop + p["h"] <= SH - MARGIN + 1e-6:
                sh.append([ytop, p["h"], MARGIN + p["w"] + GAP, [p]]); p["pos"] = (MARGIN, ytop); placed = True
                break
        if not placed:
            sheets.append([[MARGIN, p["h"], MARGIN + p["w"] + GAP, [p]]]); p["pos"] = (MARGIN, MARGIN)
        p["sheet"] = len(sheets) if not placed or True else None
    # assign sheet numbers properly
    for si, sh in enumerate(sheets):
        for shelf in sh:
            for p in shelf[3]:
                p["sheet"] = si + 1
    summary[gname] = len(sheets)
    # write one DXF per sheet
    for si in range(len(sheets)):
        dx = dxf_io.DXF()
        dx.poly([(0, 0), (SW, 0), (SW, SH), (0, SH)], layer="SHEET")
        dx.text(2, SH - 4, 2.5, "%s sheet %d/%d  300x100, grain along X" % (gname, si + 1, len(sheets)))
        for p in [q for q in plist if q["sheet"] == si + 1]:
            ox, oy = p["pos"]
            for k, g in p["loops"]:
                if k == "poly":
                    dx.poly([(u + ox, v + oy) for u, v in g])
                else:
                    dx.circle(g[0] + ox, g[1] + oy, g[2])
            dx.text(ox + 1, oy + p["h"] / 2, 2.0, p["label"])
        path = os.path.join(CAD, "dxf", "laser_%s_sheet%02d.dxf" % (gname, si + 1))
        dx.save(path)
pr("sheets by group (300 x 100):", summary)

# ---------------- DXF read-back check ----------------
fails, nloop = [], 0
for gname, plist in groups.items():
    for si in range(1, summary[gname] + 1):
        path = os.path.join(CAD, "dxf", "laser_%s_sheet%02d.dxf" % (gname, si))
        ents = dxf_io.read(path)
        got = sorted([(round(min(x for x, y in e[2]), 2), round(min(y for x, y in e[2]), 2),
                       round(max(x for x, y in e[2]), 2), round(max(y for x, y in e[2]), 2)) for e in ents if e[0] == "poly" and e[1] == "CUT"]
                     + [(round(e[2][0] - e[2][2], 2), round(e[2][1] - e[2][2], 2), round(e[2][0] + e[2][2], 2), round(e[2][1] + e[2][2], 2))
                        for e in ents if e[0] == "circle" and e[1] == "CUT"])
        exp = []
        for p in [q for q in plist if q["sheet"] == si]:
            ox, oy = p["pos"]
            for k, g in p["loops"]:
                if k == "poly":
                    exp.append((round(min(u for u, v in g) + ox, 2), round(min(v for u, v in g) + oy, 2),
                                round(max(u for u, v in g) + ox, 2), round(max(v for u, v in g) + oy, 2)))
                else:
                    exp.append((round(g[0] - g[2] + ox, 2), round(g[1] - g[2] + oy, 2), round(g[0] + g[2] + ox, 2), round(g[1] + g[2] + oy, 2)))
                # inside the sheet margin?
            if ox < MARGIN - 1e-6 or oy < MARGIN - 1e-6 or ox + p["w"] > SW - MARGIN + 1e-6 or oy + p["h"] > SH - MARGIN + 1e-6:
                fails.append(("outside margin", p["label"]))
        exp.sort()
        nloop += len(got)
        if len(got) != len(exp) or any(max(abs(a - b) for a, b in zip(g1, g2)) > 0.02 for g1, g2 in zip(got, exp)):
            fails.append((os.path.basename(path), len(got), len(exp)))
pr("DXF read-back: %d cut loops compared with the model profiles; failures: %s" % (nloop, fails if fails else "none"))
# overlap of parts on a sheet (bbox test)
ov = []
for gname, plist in groups.items():
    for a in plist:
        for b in plist:
            if a is b or a["sheet"] != b["sheet"] or a["label"] >= b["label"]:
                continue
            ax, ay = a["pos"]; bx, by = b["pos"]
            if ax < bx + b["w"] and bx < ax + a["w"] and ay < by + b["h"] and by < ay + a["h"]:
                ov.append((a["label"], b["label"]))
pr("nesting bbox overlaps:", ov if ov else "none")
json.dump({g: [(p["label"], p["sheet"], round(p["w"], 1), round(p["h"], 1)) for p in pl] for g, pl in groups.items()},
          open(os.path.join(CAD, "dxf", "nesting.json"), "w"), indent=1)

# ---------------- STL of PETG parts (print orientation) ----------------
import MeshPart
for n in ("ServoFrame_R", "ServoFrame_L", "ServoHatch_R", "ServoHatch_L", "Horn_R", "Horn_L", "RubPlate_LE", "RubPlate_TE"):
    s = obj(n).Shape.copy()
    if n.startswith("Horn"):
        s.rotate(V(0, 0, 0), V(1, 0, 0), 90)       # plate flat on the bed
    bb = s.BoundBox
    s.translate(V(-bb.XMin, -bb.YMin, -bb.ZMin))
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.2, Relative=False)
    path = os.path.join(CAD, "stl", n + ".stl")
    m.write(path)
    pr("STL %-14s %6d facets, solid %s, bbox %.1f x %.1f x %.1f, volume %.0f mm3 (shape %.0f)" % (
        n, m.CountFacets, m.isSolid(), m.BoundBox.XLength, m.BoundBox.YLength, m.BoundBox.ZLength, m.Volume, s.Volume))

# ---------------- strip-stock cut list ----------------
def arcs(xa, xb):
    return arc_len(xa, xb, True), arc_len(xa, xb, False)
cl = []
L = 2 * P.Y_END
cl.append(("LE stock", "medium balsa", "6 x 17 mm (carve to the nose)", 1, "%.0f" % L, "x 0-6"))
t, b = arcs(P.X_LE, P.X_DBOX)
cl.append(("D-box sheet, top", "1.5 mm selected light", "developed width %.1f mm" % t, 1, "%.0f" % L, "grain span-wise"))
cl.append(("D-box sheet, bottom", "1.5 mm selected light", "developed width %.1f mm" % b, 1, "%.0f" % L, "grain span-wise"))
cl.append(("Spar cap balsa", "hard balsa", "3 x 6 mm", 2, "%.0f" % L, "top and bottom"))
cl.append(("Spar cap carbon", "pultruded carbon strip", "0.5 x 6 mm", 2, "%.0f" % L, "on the outer faces"))
cl.append(("TE wedge, wing", "hard balsa", "25 x 4.6 mm TE stock", 1, "223 + 2 x 53.5", "sand to the airfoil"))
cl.append(("Aileron TE wedge", "medium balsa", "25 x 4.6 mm TE stock", 2, "325", ""))
cl.append(("Aileron LE", "medium balsa", "3 x 15.5 mm (V-bevel 1.5 mm each side)", 2, "325", "4 hinge slots each"))
tf, bf = arcs(P.X_DBOX, P.X_FS[0]); ta, ba = arcs(P.X_FS[1], P.X_TE)
ncf = 2 * (5 + 2 + 1) * 1        # front strips per surface: ribs 110,165..385,440, tip each side
cl.append(("Cap strip front, top", "1.5 mm light", "1.5 x 6 mm", 16, "%.0f" % tf, "ribs 110-440 + tip, both sides"))
cl.append(("Cap strip front, bottom", "1.5 mm light", "1.5 x 6 mm", 16, "%.0f" % bf, ""))
cl.append(("Cap strip aft, top", "1.5 mm light", "1.5 x 6 mm", 6, "%.0f" % ta, "ribs 110, 440, tip"))
cl.append(("Cap strip aft, bottom", "1.5 mm light", "1.5 x 6 mm", 6, "%.0f" % ba, ""))
cl.append(("Pushrod", "1.2 mm steel wire", "Z-bend both ends", 2, "70.5 between holes", ""))
cl.append(("CA hinges", "CA hinge sheet", "20 mm wide", 8, "18", ""))
cl.append(("Screws", "M2 x 4 pan head, self-tapping", "hatch to frame bosses (pilot 1.6 mm)", 8, "", "servo screws come with the servo"))
with open(os.path.join(CAD, "cut_list.md"), "w") as f:
    f.write("# Wing rev A - cut list\n\nGenerated by `design/cad/scripts/export_stageC.py`. Lengths in mm.\n\n")
    f.write("## Laser-cut balsa (DXF in `design/cad/dxf/`, sheets 300 x 100 mm, grain along the 300 mm side)\n\n")
    f.write("| Group (thickness, grade) | Parts | Sheets |\n|---|---|---|\n")
    for g in sorted(groups):
        f.write("| %s | %d | %d |\n" % (g, len(groups[g]), summary[g]))
    f.write("\nTip rib = 2 layers of 1.5 mm: layer a grain chord-wise (one piece), layer b grain vertical (3 pieces + aft piece). "
            "Shear webs and false spar pieces have vertical grain. Centre sheeting pieces are developed rectangles (arc length x 56).\n\n")
    f.write("## Strip stock and hardware (not on the laser)\n\n| Item | Material | Section | Qty | Length | Note |\n|---|---|---|---|---|---|\n")
    for r in cl:
        f.write("| %s | %s | %s | %s | %s | %s |\n" % r)
pr("cut list written; D-box developed widths top %.1f / bottom %.1f mm" % (t, b))
open(os.path.join(CAD, "export_report.txt"), "w").write("\n".join(REPORT))
