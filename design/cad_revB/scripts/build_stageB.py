"""Rev B Stage 2 (= rev A Stage B, unchanged) + servo pocket in foam block S - aileron, hinges, servo bay (frame, hatch, MG90S placeholder, arm), horn rib, horn, pushrod, rub plates.
Run after build_stageA.py. Re-runnable."""
import os
import sys, math, importlib
SCRIPTS = globals().get("WING_SCRIPTS") or os.environ.get("WING_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad_revB", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import wing_params as P, wing_geom as G, wing_build as B
for m in (P, G, B):
    importlib.reload(m)
import FreeCAD as App
import Part
from FreeCAD import Vector as V

d = B.doc()
GROUPS = ["B_Aileron", "B_Servo", "B_Printed"]
for g in GROUPS:
    B.clear_group(g)
    B.group(g)
OUT = G.OUTER()
S = P.MG90S
INFO = {}

zlo = lambda x: G.surf_z(x, False)
zup = lambda x: G.surf_z(x, True)
ZH = 0.5 * (zup(P.HINGE_X) + zlo(P.HINGE_X))
INFO["hinge z"] = round(ZH, 3)


def both(name, shape, material, grp, note=""):
    B.put(name + "_R", shape, material, grp, note)
    B.put(name + "_L", B.mirror_y(shape), material, grp, note)


def poly(pts):
    pts = [V(x, 0, z) for x, z in pts]
    return Part.Face(Part.makePolygon(pts + [pts[0]]))


def band(x0, x1, t0, t1, n=40):
    """XZ face between z_lo(x)+t0 and z_lo(x)+t1 (lower-surface conforming), x0..x1."""
    xs = [x0 + (x1 - x0) * i / n for i in range(n + 1)]
    a = [(x, zlo(x) + t0) for x in xs]
    b = [(x, zlo(x) + t1) for x in reversed(xs)]
    return poly(a + b)

# ---------------- aileron (right; mirrored) ----------------
y0, y1 = P.AIL_Y
x0 = P.AIL_X[0]
k = (P.AIL_LE_T - P.AIL_BEVEL) / 7.7          # bevel run per mm of z (reaches x0+1.5 at |dz| = 7.7)
le_cut = poly([(x0, ZH), (x0 + k * 25, ZH + 25), (x0 + P.AIL_LE_T, ZH + 25), (x0 + P.AIL_LE_T, ZH - 25), (x0 + k * 25, ZH - 25)])
LEF = OUT.common(le_cut)
xr = x0 + P.AIL_LE_T
RIBF = G.clip(OUT, xr, P.X_TE)
TEF = G.clip(OUT, P.X_TE, P.CHORD + 1)
le = G.extrude(LEF, y0, y1)
# CA hinge slots: through the false spar and into the aileron (x 200..218), 0.8 mm thick
slots = [Part.makeBox(2 * P.HINGE_HALF, P.HINGE_W, P.HINGE_SLOT_T,
                      V(P.HINGE_X - P.HINGE_HALF, yc - P.HINGE_W / 2, ZH - P.HINGE_SLOT_T / 2)) for yc in P.HINGE_Y]
slots_all = slots + [B.mirror_y(s) for s in slots]
for s in slots:
    le = le.cut(s)
both("Ail_LE", le, "medium", "B_Aileron", "3 mm LE, V-bevel, 4 CA hinge slots")
ribs = []
yfaces = [(y0, y0 + P.AIL_RIB_T), (y1 - P.AIL_RIB_T, y1)] + [(y - P.AIL_RIB_T / 2, y + P.AIL_RIB_T / 2) for y in P.AIL_RIB_Y]
for a, b in yfaces:
    ribs.append(G.extrude(RIBF, a, b))
both("Ail_Ribs", Part.makeCompound(ribs), "medium", "B_Aileron", "2 mm ribs: ends + wing stations (D-016)")
both("Ail_TE", G.extrude(TEF, y0, y1), "medium", "B_Aileron", "TE wedge 25 mm, medium (D-020)")
# false spar: cut the hinge slots
fs = d.getObject("FalseSpar")
fsh = fs.Shape
for s in slots_all:
    fsh = fsh.cut(s)
fs.Shape = fsh
# rev B: the hinges at y 130 / 302.5 reach 5 mm forward of the false spar into foam blocks S / M: slot the foam too
for o in [o for o in d.Objects if o.TypeId == "Part::Feature" and o.Name.startswith("Foam_")]:
    sh = o.Shape
    for s_ in slots_all:
        if sh.BoundBox.intersect(s_.BoundBox) and sh.common(s_).Volume > 1e-6:
            sh = sh.cut(s_)
    if sh.Volume < o.Shape.Volume - 1e-6:
        o.Shape = sh
        INFO.setdefault("hinge slots cut in foam", []).append(o.Name)

# ---------------- servo placeholder ----------------
xs_ = P.SERVO_SHAFT_X
cx1 = xs_ + S["SHAFT_FROM_END"]; cx0 = cx1 - S["L"]           # case x range (shaft at the aft end)
ccx = 0.5 * (cx0 + cx1)
tx0, tx1 = ccx - S["TAB_L"] / 2, ccx + S["TAB_L"] / 2
zl_max = max(zlo(tx0 + (tx1 - tx0) * i / 20) for i in range(21))
zl_min_bay = min(zlo(P.FRAME_X[0] + (P.FRAME_X[1] - P.FRAME_X[0]) * i / 20) for i in range(21))
zc0 = zl_max + P.HATCH_T + P.SERVO_GAP
zsh = zc0 + S["W"] / 2
ys0 = P.SERVO_Y0
case = Part.makeBox(S["L"], S["H"], S["W"], V(cx0, ys0, zc0))
tabs = Part.makeBox(S["TAB_L"], S["TAB_T"], S["W"], V(tx0, ys0 + S["TAB_Z"], zc0))
for xh in (ccx - S["TAB_HOLE_PITCH"] / 2, ccx + S["TAB_HOLE_PITCH"] / 2):
    tabs = tabs.cut(B.ycyl(xh, zsh, 2.0, ys0 + S["TAB_Z"] - 1, ys0 + S["TAB_Z"] + S["TAB_T"] + 1))
top = Part.makeCylinder(S["W"] / 2, S["H_TOP"] - S["H"], V(xs_, ys0 + S["H"], zsh), V(0, 1, 0))
top = top.fuse(Part.makeBox(cx1 - S["W"] / 2 - cx0 - 4, S["H_TOP"] - S["H"] - 2, S["W"] - 2, V(cx0 + 2, ys0 + S["H"], zc0 + 1)))
spline = Part.makeCylinder(S["SPLINE_D"] / 2, S["SPLINE_H"], V(xs_, ys0 + S["H_TOP"], zsh), V(0, 1, 0))
servo = case.fuse([tabs, top, spline]).removeSplitter()
both("Servo_MG90S", servo, "servo", "B_Servo", "PLACEHOLDER standard MG90S size - replace with vendor CAD")
# arm: in the XZ plane, pointing down to the pushrod hole below the skin
ya0 = ys0 + S["H_TOP"] + 0.7
ya1 = ya0 + P.ARM_T
YARM = 0.5 * (ya0 + ya1)
za = zlo(xs_) - P.ARM_BELOW_SKIN
r_arm = zsh - za
hub = Part.makeCylinder(3.5, P.ARM_T, V(xs_, ya0, zsh), V(0, 1, 0))
bar = Part.makeBox(4.0, P.ARM_T, r_arm + 2.0, V(xs_ - 2.0, ya0, za - 2.0))
tip = Part.makeCylinder(2.0, P.ARM_T, V(xs_, ya0, za), V(0, 1, 0))
arm = hub.fuse([bar, tip]).removeSplitter().cut(B.ycyl(xs_, za, 1.4, ya0 - 1, ya1 + 1))
arm = arm.cut(B.ycyl(xs_, zsh, S["SPLINE_D"], ya0 - 1, ya1 + 1))          # hub bore on the spline
both("ServoArm", arm, "servo", "B_Servo", "single arm, hole r = %.1f mm" % r_arm)
INFO.update({"servo case x": (round(cx0, 2), round(cx1, 2)), "tabs x": (round(tx0, 2), round(tx1, 2)),
             "servo z": (round(zc0, 2), round(zc0 + S["W"], 2)), "shaft z": round(zsh, 2), "arm y": round(YARM, 2),
             "arm hole z": round(za, 2), "arm r": round(r_arm, 2)})

# ---------------- frame (PETG) ----------------
fx0, fx1 = P.FRAME_X
by0, by1 = P.BAY_Y
ring = G.extrude(band(fx0, fx1, P.HATCH_T, P.HATCH_T + P.RING_T), by0, by1)
ox0, ox1 = P.FRAME_OPEN_X; oy0, oy1 = P.FRAME_OPEN_Y
ring = ring.cut(Part.makeBox(ox1 - ox0, oy1 - oy0, 40, V(ox0, oy0, -30)))
r110 = 110.0 + 1.5; r165 = 165.0 - 1.0          # rib faces
ztab0 = None
tabs_f = []
for (ya, yb) in ((r110, by0 + 1.0), (by1 - 1.0, r165)):
    for (xa, xb) in ((fx0, fx0 + P.FRAME_TAB[0]), (fx1 - P.FRAME_TAB[0], fx1)):
        zb_ = max(zlo(xa), zlo(xb)) + P.SKIN_T + 0.2        # seats on the cap strip top (0.2 mm glue gap)
        tabs_f.append(Part.makeBox(xb - xa, yb - ya, P.FRAME_TAB[1], V(xa, ya, zb_)))
bosses, holes_h = [], []
SCREWS = [(fx0 + 2.5, by0 + 2.0), (fx1 - 2.5, by0 + 2.0), (fx0 + 2.5, by1 - 2.0), (fx1 - 2.5, by1 - 2.0)]
for (x, y) in SCREWS:
    zb_ = max(zlo(x - 2.5), zlo(x + 2.5)) + P.HATCH_T + 0.05   # flat seat above the curved hatch top
    bosses.append(Part.makeCylinder(2.5, P.RING_T + 3.0, V(x, y, zb_), V(0, 0, 1)))
frame = ring.fuse(tabs_f + bosses).removeSplitter()
for (x, y) in SCREWS:
    frame = frame.cut(B.zcyl(x, y, 1.6))
both("ServoFrame", frame, "petg", "B_Printed", "PETG frame, glued to rib faces, 4 x M2 pilot holes")

# ---------------- hatch (PETG) with servo lugs ----------------
hatch = G.extrude(band(fx0, fx1, 0.0, P.HATCH_T), by0, by1)
lug_y0, lug_y1 = ys0 + S["TAB_Z"] - 4.0, ys0 + S["TAB_Z"]
lugs = []
for (xa, xb) in ((tx0 - 1.0, cx0 - P.LUG_GAP), (cx1 + P.LUG_GAP, tx1 + 1.0)):
    zb_ = min(zlo(xa), zlo(xb)) + 0.5
    lugs.append(Part.makeBox(xb - xa, lug_y1 - lug_y0, zc0 + S["W"] - zb_, V(xa, lug_y0, zb_)))
hatch = hatch.fuse(lugs).removeSplitter()
# remove the lug part below the outer surface
lowcut = G.extrude(band(fx0 - 1, fx1 + 1, -30.0, 0.0), by0 - 1, by1 + 1)
hatch = hatch.cut(lowcut)
for xh in (ccx - S["TAB_HOLE_PITCH"] / 2, ccx + S["TAB_HOLE_PITCH"] / 2):
    hatch = hatch.cut(B.ycyl(xh, zsh, 1.5, lug_y0 - 1, lug_y1 + 1))
slot = Part.makeBox(2 * P.ARM_SLOT_HALF, ya1 - ya0 + 2.0, 40, V(xs_ - P.ARM_SLOT_HALF, ya0 - 1.0, -30))
hatch = hatch.cut(slot)
for (x, y) in SCREWS:
    hatch = hatch.cut(B.zcyl(x, y, 2.2))
both("ServoHatch", hatch, "petg", "B_Printed", "PETG hatch 1.0 mm + 2 servo lugs, 4 x M2, arm slot")

# ---------------- horn rib, horn, pushrod ----------------
yh0, yh1 = YARM - P.HORN_T / 2, YARM + P.HORN_T / 2
both("Ail_HornRib", G.extrude(RIBF, yh1, yh1 + P.AIL_RIB_T), "medium", "B_Aileron", "2 mm horn rib (D-016)")
zhh = za
hp = poly([(xr, 6.0), (232.0, 6.0), (232.0, zlo(232.0)), (222.0, zlo(222.0)), (211.5, zhh - 3.0), (206.5, zhh - 3.0),
           (206.5, zhh + 3.0), (xr, zlo(xr))])
horn = G.extrude(hp, yh0, yh1).cut(B.ycyl(P.HINGE_X, zhh, 1.5, yh0 - 1, yh1 + 1))
both("Horn", horn, "petg", "B_Printed", "slot-in horn, glued to horn rib and LE; hole %.1f mm below hinge" % (ZH - zhh))
yr_ = max(ya1, yh1) + 0.1 + P.PUSHROD_D / 2          # rod runs beside the arm and horn plates (Z-bends)
rod = Part.makeCylinder(P.PUSHROD_D / 2, P.HINGE_X - xs_, V(xs_, yr_, za), V(1, 0, 0))
pin_a = B.ycyl(xs_, za, P.PUSHROD_D, ya0 - 0.8, yr_)
pin_h = B.ycyl(P.HINGE_X, zhh, P.PUSHROD_D, yh0 - 0.8, yr_)
rod = rod.fuse([pin_a, pin_h, Part.makeSphere(P.PUSHROD_D / 2, V(xs_, yr_, za)), Part.makeSphere(P.PUSHROD_D / 2, V(P.HINGE_X, yr_, zhh))]).removeSplitter()
both("Pushrod", rod, "steel", "B_Servo", "1.2 mm steel wire, Z-bends not modelled")
INFO.update({"horn y": (round(yh0, 2), round(yh1, 2)), "horn arm": round(ZH - zhh, 2), "pushrod L": round(P.HINGE_X - xs_, 1)})

# ---------------- band rub plates (PETG, outside the film) ----------------
NOSE8 = G.clip(OUT, -5, 25).Faces[0].makeOffset2D(P.RUB_T, join=0, fill=False, openResult=False, intersection=False)
shell = NOSE8.cut(OUT)
lep = shell.common(G.rect(-5, 20)).cut(G.rect(3, 30, -60, 0))
xs_te = [250.0 + 29.0 * i / 40 for i in range(41)]
tep = poly([(x, zup(x)) for x in xs_te] + [(x, zup(x) + P.RUB_T) for x in reversed(xs_te)])
yr = P.RUB_W / 2
B.put("RubPlate_LE", G.extrude(lep, -yr, yr), "petg", "B_Printed", "0.6 mm, y +-20 (interp. band width)")
B.put("RubPlate_TE", G.extrude(tep, -yr, yr), "petg", "B_Printed", "0.6 mm, y +-20 (interp. band width)")

# ---------------- rev B: servo pocket in the foam of block S ----------------
ztop = zc0 + S["W"] + P.POCKET_TOP_GAP
ztop = max(ztop, max(bb.ZMax for bb in [d.getObject("ServoFrame_R").Shape.BoundBox]) + P.POCKET_TOP_GAP)
px0, px1 = P.POCKET_X
sy0, sy1 = P.BLOCKS["S"][0][1], P.BLOCKS["S"][1][0]
pocket = Part.makeBox(px1 - px0, sy1 - sy0, ztop + 40.0, V(px0, sy0, -40.0))
for side, pk in (("R", pocket), ("L", B.mirror_y(pocket))):
    o = d.getObject("Foam_S_Aft_" + side)
    o.Shape = o.Shape.cut(pk)
INFO["servo pocket"] = dict(x=(px0, px1), y=(sy0, sy1), z_top=round(ztop, 2))

d.recompute()
for kk, vv in INFO.items():
    print(kk, vv)
bad = [o.Name for o in d.Objects if o.TypeId == "Part::Feature" and not o.Shape.isValid()]
print("objects", len([o for o in d.Objects if o.TypeId == "Part::Feature"]), "invalid", bad)
