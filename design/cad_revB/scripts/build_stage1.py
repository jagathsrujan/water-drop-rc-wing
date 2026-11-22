"""Rev B Stage 1 - foam-block structure. Re-runnable: exec(open(path).read()) inside FreeCAD.
Replaces rev A build_stageA.py. Reused rev A parts: D-box sheeting, spar caps, webs (pieces between plates), false spar,
tip ring caps, bottom centre sheeting. New: XPS blocks (hollow), stepped balsa face plates, half ribs + caps,
printed PLA LE (5 segments, locator keys, joiners) and TE (fixed bays, plate slots). See design/cad_revB/REVB_PLAN.md."""
import sys, os, importlib
SCRIPTS = globals().get("WING_SCRIPTS") or os.environ.get("WING_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad_revB", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import wing_params as P, wing_geom as G, wing_build as B, wing_check as C
for m in (P, G, B, C):
    importlib.reload(m)
from FreeCAD import Vector as V
import Part

d = B.doc()
GROUPS = ["S1_Foam", "S1_Plates", "S1_Ribs", "S1_Sheeting", "S1_Spar", "S1_Printed", "S1_Tip"]
for g in GROUPS:
    B.clear_group(g)
    B.group(g)

OUT, IN, SKIN = G.OUTER(), G.INNER(), G.SKIN()
YE = P.YE_B
x0s, x1s = P.X_SPAR
ZT = G.inner_z_range(x0s, x1s, True)
ZB = G.inner_z_range(x0s, x1s, False)
T = P.CAP_BALSA_T + P.CAP_CARBON_T
INFO = {}
INFILL = {}


def mirror_pair(name, s, mat, grp, note=""):
    B.put(name + "_R", s, mat, grp, note)
    B.put(name + "_L", B.mirror_y(s), mat, grp, note)


def one_face(sh):
    """Fuse faces of a shape into one planar face (or a compound of faces)."""
    sh = sh.removeSplitter() if hasattr(sh, "removeSplitter") else sh
    return sh.Faces[0] if len(sh.Faces) == 1 else sh


def cavity(xa, xb, off_top, off_bot, minh=P.CAV_MINH, n=80):
    """Cavity section: vertical offset from the OUTER surface, x range xa..xb, cut where height < minh."""
    xs = [xa + (xb - xa) * i / n for i in range(n + 1)]
    up = [(x, G.surf_z(x, True) - off_top) for x in xs]
    lo = [(x, G.surf_z(x, False) + off_bot) for x in xs]
    keep = [i for i in range(len(xs)) if up[i][1] - lo[i][1] >= minh]
    i0, i1 = keep[0], keep[-1]
    ub = Part.BSplineCurve(); ub.interpolate([V(x, 0, z) for x, z in up[i0:i1 + 1]])
    lb = Part.BSplineCurve(); lb.interpolate([V(x, 0, z) for x, z in lo[i0:i1 + 1]])
    e = [ub.toShape(), Part.makeLine(V(up[i1][0], 0, up[i1][1]), V(lo[i1][0], 0, lo[i1][1])),
         lb.toShape(), Part.makeLine(V(lo[i0][0], 0, lo[i0][1]), V(up[i0][0], 0, up[i0][1]))]
    return Part.Face(Part.Wire(Part.__sortEdges__(e)))


# ---------------- 2D sections ----------------
SK_TOP_A, SK_BOT_A = G.faces_split(G.clip(SKIN, P.X_DBOX, P.X_FS[0]))     # skin bands x 80..205
SK_TOP_T, SK_BOT_T = G.faces_split(G.clip(SKIN, P.X_FS[1], P.X_TE_B))     # skin bands x 208..250
NOTCH = G.rect(x0s, x1s, ZT - T, 60).fuse(G.rect(x0s, x1s, -60, ZB + T))

# foam piece sections
F_FRONT = G.clip(IN, *P.X_FOAM_F)
F_AFT = G.clip(OUT, *P.X_FOAM_A)
F_AFT_C = F_AFT.cut(SK_BOT_A[0])                     # centre: bottom inset under the kept bottom sheeting
F_TE = G.clip(OUT, *P.X_FOAM_TE)
F_TE_C = F_TE.cut(SK_BOT_T[0])
W = P.WALL
CAV_F = cavity(P.X_FOAM_F[0] + W, P.X_FOAM_F[1] - W, P.SKIN_T + W, P.SKIN_T + W)
CAV_A = cavity(P.X_FOAM_A[0] + W, P.X_FOAM_A[1] - W, W, W)
CAV_A_C = cavity(P.X_FOAM_A[0] + W, P.X_FOAM_A[1] - W, W, P.SKIN_T + W)
INFO["cavity fraction front / aft / aft centre"] = (round(CAV_F.Area / F_FRONT.Area, 3), round(CAV_A.Area / F_AFT.Area, 3),
                                                   round(CAV_A_C.Area / F_AFT_C.Area, 3))
INFO["section areas cm2 front/aft/te"] = (round(F_FRONT.Area / 100, 2), round(F_AFT.Area / 100, 2), round(F_TE.Area / 100, 2))

# plate sections (stepped template: inner outline x < 80, outer outline x >= 80)
PL_MAIN = G.clip(IN, P.X_LE, P.X_DBOX).fuse(G.clip(OUT, P.X_DBOX, P.X_FS[0])).removeSplitter().cut(NOTCH)
PL_MAIN_C = G.clip(IN, P.X_LE, P.X_DBOX).fuse(G.clip(OUT, P.X_DBOX, P.X_FS[0]).cut(SK_BOT_A[0])).removeSplitter().cut(NOTCH)
PL_TAIL = G.clip(OUT, P.X_FS[1], P.X_TE_B + P.TAIL)
PL_TAIL_C = PL_TAIL.cut(SK_BOT_T[0])

# LE key position
XK = 0.5 * (P.KEY["x0"] + P.KEY["x1"])
ZK = 0.5 * (G.surf_z(XK, True, IN) + G.surf_z(XK, False, IN))
KEY_F = G.rect(P.KEY["x0"], P.KEY["x1"], ZK - P.KEY["h"] / 2, ZK + P.KEY["h"] / 2)
INFO["LE key z centre"] = round(ZK, 2)


def plate_solid(y0, y1, centre=False, fixed=False, holes=("F", "A"), wire=False, solid=False):
    f = PL_MAIN_C if centre else PL_MAIN
    if not solid:
        if "F" in holes:
            f = f.cut(CAV_F)
        if "A" in holes:
            f = f.cut(CAV_A_C if centre else CAV_A)
        if wire:
            xc, dd = P.WIRE_HOLE
            f = f.cut(G.circle(xc, P.WIRE_HOLE_Z_B, dd))      # lowered into the servo pocket (rev A: mid-depth)
    s = G.extrude(f, y0, y1)
    if fixed:
        s = Part.makeCompound([s, G.extrude(PL_TAIL_C if centre else PL_TAIL, y0, y1)])
    return s


# ---------------- stations (right side) ----------------
PLATES = []          # (name, y0, y1, kwargs)
PLATES.append(("Plate_055", P.C_FOAM, P.C_FOAM + P.PLATE_T, dict(centre=True, fixed=True)))
S_in, S_out, _ = P.BLOCKS["S"]
M_in, M_out, _ = P.BLOCKS["M"]
T_in, T_out, _ = P.BLOCKS["T"]
PLATES += [("Plate_110", S_in[0], S_in[1], dict(fixed=True, holes=("F",), wire=True)),
           ("Plate_165", S_out[0], S_out[1], dict(holes=("F",))),
           ("Plate_275", M_in[0], M_in[1], dict()),
           ("Plate_330", M_out[0], M_out[1], dict()),
           ("Plate_439", T_in[0], T_in[1], dict(fixed=True)),
           ("Plate_491", T_out[0], T_out[1], dict(fixed=True, solid=True))]
for nm, y0, y1, kw in PLATES:
    mirror_pair(nm, plate_solid(y0, y1, **kw), "light", "S1_Plates", "1.5 mm light balsa face plate = hot-wire template (stepped outline)")

# ---------------- LE (printed PLA, 5 segments) + keys + joiners ----------------
plate_y = [(-P.C_FOAM - P.PLATE_T, -P.C_FOAM), (P.C_FOAM, P.C_FOAM + P.PLATE_T)]
for nm, y0, y1, kw in PLATES[1:]:
    plate_y += [(y0, y1), (-y1, -y0)]
keys = []
for (y0, y1) in plate_y:
    yc = 0.5 * (y0 + y1)
    ka, kb = max(yc - P.KEY["L"] / 2, -YE), min(yc + P.KEY["L"] / 2, YE)
    k = G.extrude(KEY_F, ka, kb).cut(Part.makeBox(10, (y1 - y0) + 2 * P.SLOT_CLR, 40, V(P.KEY["x0"] - 1, y0 - P.SLOT_CLR, -20)))
    keys.append(k)
B.put("LE_Keys", Part.makeCompound(keys), "pla", "S1_Printed", "14 locator keys 3 x 4 x 12 mm with plate slots (D-032)")
joiners = [G.extrude(KEY_F, j - P.JOINER_L / 2, j + P.JOINER_L / 2) for j in P.LE_JOINTS]
B.put("LE_Joiners", Part.makeCompound(joiners), "pla", "S1_Printed", "4 joiners across the LE butt joints, in the block groove")
LEF = G.clip(OUT, 0, P.X_LE)
ys = [-YE] + P.LE_JOINTS + [YE]
for i, (a, b) in enumerate(zip(ys, ys[1:])):
    nm = "LE_%d" % (i + 1)
    B.put(nm, G.extrude(LEF, a, b), "pla", "S1_Printed", "printed LE segment %.2f mm (D-028)" % (b - a))
    INFILL[nm] = P.INFILL_B["LE"]
INFO["LE segments mm"] = [round(b - a, 2) for a, b in zip(ys, ys[1:])]

# ---------------- TE (printed PLA, fixed bays) with plate slots ----------------
TEF = G.clip(OUT, P.X_TE_B, P.CHORD + 1)


def te_slots(y_list):
    return [Part.makeBox(P.TAIL + 0.5, (y1 - y0) + 2 * P.SLOT_CLR, 40, V(P.X_TE_B - 0.5, y0 - P.SLOT_CLR, -20)) for y0, y1 in y_list]


te_c = G.extrude(TEF, -S_in[1], S_in[1])
for s in te_slots([(P.C_FOAM, P.C_FOAM + P.PLATE_T), (-P.C_FOAM - P.PLATE_T, -P.C_FOAM), S_in, (-S_in[1], -S_in[0])]):
    te_c = te_c.cut(s)
B.put("TE_Centre", te_c, "pla", "S1_Printed", "printed TE x 250-280, y +-111.5, 4 plate slots (D-028)")
INFILL["TE_Centre"] = P.INFILL_B["TE"]
te_o = G.extrude(TEF, T_in[0], YE)
for s in te_slots([T_in, T_out]):
    te_o = te_o.cut(s)
mirror_pair("TE_Outer", te_o, "pla", "S1_Printed", "printed TE x 250-280, y 438.5-492, 2 plate slots")
INFILL["TE_Outer_R"] = INFILL["TE_Outer_L"] = P.INFILL_B["TE"]

# ---------------- foam blocks ----------------
keycomp = Part.makeCompound(keys + joiners)


def foam(name, y0, y1, centre=False, fixed=False, aft_cavity=True, mirror=True):
    fr = G.extrude(F_FRONT.cut(CAV_F), y0, y1).cut(keycomp)
    af_face = F_AFT_C if centre else F_AFT
    if aft_cavity:
        af_face = af_face.cut(CAV_A_C if centre else CAV_A)
    af = G.extrude(af_face, y0, y1)
    parts = [("Front", fr), ("Aft", af)]
    if fixed:
        parts.append(("TE", G.extrude(F_TE_C if centre else F_TE, y0, y1)))
    for tag, s in parts:
        if centre and tag == "Aft":
            wx, wy, wd = P.WIRE_EXIT
            for sg in (1, -1):
                s = s.cut(B.zcyl(wx, sg * wy, wd))
        nm = "Foam_%s_%s" % (name, tag)
        if mirror:
            mirror_pair(nm, s, "xps", "S1_Foam", "XPS 30, hollow, 7 mm walls (D-025)")
        else:
            B.put(nm, s, "xps", "S1_Foam", "XPS 30, hollow, 7 mm walls (D-025)")


foam("C", -P.C_FOAM, P.C_FOAM, centre=True, fixed=True, mirror=False)
foam("S", S_in[1], S_out[0], aft_cavity=False)        # servo pocket cut in stage 2
foam("M", M_in[1], M_out[0])
foam("T", T_in[1], T_out[0], fixed=True)

# ---------------- D-box, bottom centre sheeting ----------------
db = G.clip(SKIN, P.X_LE, P.X_DBOX)
top, bot = G.faces_split(db)
B.put("DBox_Top", G.extrude(top[0], -YE, YE), "sheet", "S1_Sheeting", "1.5 mm light sheet, grain span-wise (rev A)")
B.put("DBox_Bot", G.extrude(bot[0], -YE, YE), "sheet", "S1_Sheeting", "1.5 mm light sheet, grain span-wise (rev A)")
for tag, face in (("Fwd", SK_BOT_A[0]), ("Aft", SK_BOT_T[0])):
    s = G.extrude(face, 0.0, P.Y_CSHEET)
    if tag == "Fwd":
        wx, wy, wd = P.WIRE_EXIT
        s = s.cut(B.zcyl(wx, wy, wd))
    mirror_pair("CSheet_Bot_%s" % tag, s, "sheet", "S1_Sheeting", "bottom centre sheet kept (D-031), grain chord-wise")

# ---------------- spar, false spar, webs ----------------
def ybox(xa, xb, za, zb, y0=-YE, y1=YE):
    return Part.makeBox(xb - xa, y1 - y0, zb - za, V(xa, y0, za))


B.put("SparCarbon_Top", ybox(x0s, x1s, ZT - P.CAP_CARBON_T, ZT), "carbon", "S1_Spar", "0.5 x 6 pultruded carbon")
B.put("SparBalsa_Top", ybox(x0s, x1s, ZT - T, ZT - P.CAP_CARBON_T), "hard", "S1_Spar", "3 x 6 hard balsa")
B.put("SparCarbon_Bot", ybox(x0s, x1s, ZB, ZB + P.CAP_CARBON_T), "carbon", "S1_Spar", "0.5 x 6 pultruded carbon")
B.put("SparBalsa_Bot", ybox(x0s, x1s, ZB + P.CAP_CARBON_T, ZB + T), "hard", "S1_Spar", "3 x 6 hard balsa")
B.put("FalseSpar", G.extrude(G.clip(OUT, *P.X_FS), -YE, YE), "medium", "S1_Spar", "3 mm, span-wise grain, full depth (rev B note)")
# stations that cross the spar: plates only (right side, sorted)
st = sorted([(-P.C_FOAM - P.PLATE_T, -P.C_FOAM), (P.C_FOAM, P.C_FOAM + P.PLATE_T)] + [(y0, y1) for _, y0, y1, _ in PLATES[1:]])
st = [s_ for s_ in st if s_[1] > 0]
bays = [(-P.C_FOAM, P.C_FOAM)] + [(a[1], b[0]) for a, b in zip(st, st[1:])]
WF = G.clip(IN, x0s - P.WEB_T, x0s)
WR = G.clip(IN, x1s, x1s + P.WEB_T)
wf = [G.extrude(WF, a, b) for a, b in bays]
wr = [G.extrude(WR, a, b) for a, b in bays if b <= P.REAR_WEB_Y + 1e-6]
wf += [B.mirror_y(s) for s in wf[1:]]
wr += [B.mirror_y(s) for s in wr[1:]]
B.put("ShearWebFront", Part.makeCompound(wf), "medium", "S1_Spar", "1.5 mm, pieces between the plates")
B.put("ShearWebRear", Part.makeCompound(wr), "medium", "S1_Spar", "1.5 mm, |y| <= 164")
INFO["web bays"] = [(round(a, 1), round(b, 1)) for a, b in bays]

# ---------------- half ribs + cap strips ----------------
HR = G.clip(IN, *P.HALF_RIB_X)
for xc in P.HALF_RIB_HOLES:
    dd = min(G.depth(xc, IN) - 2 * P.HOLE_MARGIN, P.HOLE_DMAX)
    zc = 0.5 * (G.surf_z(xc, True, IN) + G.surf_z(xc, False, IN))
    HR = HR.cut(G.circle(xc, zc, dd))
for y in P.HALF_RIBS:
    nm = "%03d" % round(y)
    mirror_pair("HalfRib_" + nm, G.extrude(HR, y - P.PLATE_T / 2, y + P.PLATE_T / 2), "light", "S1_Ribs", "1.5 mm light half rib x 78.6-205 (D-027)")
    caps = Part.makeCompound([G.extrude(f, y - 3.0, y + 3.0) for f in SK_TOP_A + SK_BOT_A])
    mirror_pair("Caps_" + nm, caps, "light", "S1_Ribs", "1.5 x 6 light cap strips")

# ---------------- tip ring caps (rev A) ----------------
RING_IN = OUT.makeOffset2D(-P.TIP_RING_W, join=0, fill=False, openResult=False, intersection=False)
mirror_pair("TipCap", G.extrude(OUT.cut(RING_IN), P.TIP_CAP[0], P.TIP_CAP[1]), "light", "S1_Tip", "3 mm light ring cap (rev A)")

d.recompute()
C.INFILL.update(INFILL)
STAGE1_INFILL = INFILL
for k, v in INFO.items():
    print(k, v)
bad = [o.Name for o in d.Objects if o.TypeId == "Part::Feature" and not o.Shape.isValid()]
print("objects", len([o for o in d.Objects if o.TypeId == "Part::Feature"]), "invalid", bad)
