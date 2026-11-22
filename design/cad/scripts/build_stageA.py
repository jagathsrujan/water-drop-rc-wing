"""Stage A - primary structure. Re-runnable: exec(open(path).read()) inside FreeCAD.
Parts are 2D sections in the XZ plane (wing_geom) extruded along Y; neighbours share faces exactly."""
import sys, os, importlib
SCRIPTS = globals().get("WING_SCRIPTS") or os.environ.get("WING_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import wing_params as P, wing_geom as G, wing_build as B
for m in (P, G, B):
    importlib.reload(m)
from FreeCAD import Vector as V
import Part

d = B.doc()
GROUPS = ["A_Ribs", "A_Sheeting", "A_Spar", "A_CapStrips", "A_TE_Tip"]
for g in GROUPS:
    B.clear_group(g)
    B.group(g)

OUT, IN, SKIN = G.OUTER(), G.INNER(), G.SKIN()
YE = P.Y_END
x0s, x1s = P.X_SPAR
ZT = G.inner_z_range(x0s, x1s, True)     # carbon top face (top cap)
ZB = G.inner_z_range(x0s, x1s, False)    # carbon bottom face (bottom cap)
T = P.CAP_BALSA_T + P.CAP_CARBON_T
log = []


def both(name, face_or_fn, y0, y1, material, grp, note=""):
    """Right part y0..y1 and mirrored left part."""
    s = G.extrude(face_or_fn, y0, y1)
    B.put(name + "_R", s, material, grp, note)
    B.put(name + "_L", B.mirror_y(s), material, grp, note)


# ---------- LE, sheeting ----------
B.put("LE", G.extrude(G.clip(OUT, 0, P.X_LE), -YE, YE), "medium", "A_Sheeting", "6 mm LE stock, carved (D-013: medium)")
db = G.clip(SKIN, P.X_LE, P.X_DBOX)
top, bot = G.faces_split(db)
B.put("DBox_Top", G.extrude(top[0], -YE, YE), "sheet", "A_Sheeting", "1.5 mm light sheet, grain span-wise")
B.put("DBox_Bot", G.extrude(bot[0], -YE, YE), "sheet", "A_Sheeting", "1.5 mm light sheet, grain span-wise")
for tag, (xa, xb) in (("Fwd", (P.X_DBOX, P.X_FS[0])), ("Aft", (P.X_FS[1], P.X_TE))):
    t2, b2 = G.faces_split(G.clip(SKIN, xa, xb))
    for side, f in (("Top", t2[0]), ("Bot", b2[0])):
        s = G.extrude(f, 0.0, P.Y_CSHEET)
        if side == "Bot" and tag == "Fwd":
            wx, wy, wd = P.WIRE_EXIT
            s = s.cut(B.zcyl(wx, wy, wd))
        B.put("CSheet_%s_%s_R" % (side, tag), s, "sheet", "A_Sheeting", "centre sheet, grain chord-wise (D-017)")
        B.put("CSheet_%s_%s_L" % (side, tag), B.mirror_y(s), "sheet", "A_Sheeting", "centre sheet, grain chord-wise (D-017)")

# ---------- spar caps ----------
def ybox(xa, xb, za, zb, y0=-YE, y1=YE):
    return Part.makeBox(xb - xa, y1 - y0, zb - za, V(xa, y0, za))
B.put("SparCarbon_Top", ybox(x0s, x1s, ZT - P.CAP_CARBON_T, ZT), "carbon", "A_Spar", "0.5 x 6 pultruded carbon")
B.put("SparBalsa_Top", ybox(x0s, x1s, ZT - T, ZT - P.CAP_CARBON_T), "hard", "A_Spar", "3 x 6 hard balsa")
B.put("SparCarbon_Bot", ybox(x0s, x1s, ZB, ZB + P.CAP_CARBON_T), "carbon", "A_Spar", "0.5 x 6 pultruded carbon")
B.put("SparBalsa_Bot", ybox(x0s, x1s, ZB + P.CAP_CARBON_T, ZB + T), "hard", "A_Spar", "3 x 6 hard balsa")
B.put("FalseSpar", G.extrude(G.clip(OUT, *P.X_FS), -YE, YE), "medium", "A_Spar", "3 mm, vertical grain, full depth (D-015)")

# ---------- ribs ----------
NOTCH = G.rect(x0s, x1s, ZT - T, 60).fuse(G.rect(x0s, x1s, -60, ZB + T))
RIB_F = G.clip(IN, P.X_LE, P.X_FS[0]).cut(NOTCH)
RIB_A = G.clip(IN, P.X_FS[1], P.X_TE)
hole_log = {}


def holes_for(ystation):
    skip = P.HOLE_SKIP.get(ystation, [])
    hs = []
    for xc in P.HOLE_X:
        if xc in skip:
            continue
        dd = min(G.depth(xc, IN) - 2 * P.HOLE_MARGIN, P.HOLE_DMAX)
        zc = 0.5 * (G.surf_z(xc, True, IN) + G.surf_z(xc, False, IN))
        if dd >= 6.0:
            hs.append((xc, zc, dd))
    if ystation == 110.0:
        xc, dd = P.WIRE_HOLE
        zc = 0.5 * (G.surf_z(xc, True, IN) + G.surf_z(xc, False, IN))
        hs.append((xc, zc, dd))
    return hs


def rib_face(ystation, holes=True):
    f = RIB_F
    if holes:
        hs = holes_for(ystation)
        hole_log[ystation] = [(round(x, 1), round(z, 1), round(dd, 1)) for x, z, dd in hs]
        for xc, zc, dd in hs:
            f = f.cut(G.circle(xc, zc, dd))
    return f

FIXED_AFT = {0.0, 55.0, 110.0, 439.5}
# centre rib
yc, tc = P.RIB_C
B.put("Rib_C000", G.extrude(rib_face(0.0), -tc / 2, tc / 2), "medium", "A_Ribs", "2 mm medium")
B.put("RibAft_C000", G.extrude(RIB_A, -tc / 2, tc / 2), "medium", "A_Ribs", "aft piece x 208-255")
for y, t in P.RIBS:
    nm = "%03d" % round(y)
    both("Rib_" + nm, rib_face(y), y - t / 2, y + t / 2, "medium", "A_Ribs", "%.0f mm medium" % t)
    if y in FIXED_AFT:
        both("RibAft_" + nm, RIB_A, y - t / 2, y + t / 2, "medium", "A_Ribs", "aft piece x 208-255")
yt, tt = P.TIP_RIB
both("TipRib", RIB_F, yt - tt / 2, yt + tt / 2, "light", "A_TE_Tip", "2 x 1.5 mm light, cross-grain, no holes (D-018)")
both("TipRibAft", RIB_A, yt - tt / 2, yt + tt / 2, "light", "A_TE_Tip", "aft piece, 2 x 1.5 mm light")
RING_IN = OUT.makeOffset2D(-P.TIP_RING_W, join=0, fill=False, openResult=False, intersection=False)
RING = OUT.cut(RING_IN)
both("TipCap", RING, P.TIP_CAP[0], P.TIP_CAP[1], "light", "A_TE_Tip", "3 mm light outline ring, 10 mm wide (D-013/D-014)")

# ---------- shear webs (pieces between ribs) ----------
faces_y = [(-tc / 2, tc / 2)] + [(y - t / 2, y + t / 2) for y, t in P.RIBS] + [(yt - tt / 2, yt + tt / 2)]
bays = [(a[1], b[0]) for a, b in zip(faces_y, faces_y[1:])]
WF = G.clip(IN, x0s - P.WEB_T, x0s)
WR = G.clip(IN, x1s, x1s + P.WEB_T)
wf = [G.extrude(WF, a, b) for a, b in bays]
wr = [G.extrude(WR, a, b) for a, b in bays if b <= P.REAR_WEB_Y + 1e-6]
wf += [B.mirror_y(s) for s in wf]
wr += [B.mirror_y(s) for s in wr]
B.put("ShearWebFront", Part.makeCompound(wf), "medium", "A_Spar", "1.5 mm vertical grain, pieces between ribs")
B.put("ShearWebRear", Part.makeCompound(wr), "medium", "A_Spar", "1.5 mm vertical grain, |y| <= 164")

# ---------- cap strips ----------
CF = G.faces_split(G.clip(SKIN, P.X_DBOX, P.X_FS[0]))
CA = G.faces_split(G.clip(SKIN, P.X_FS[1], P.X_TE))
cap_spans = {}   # station -> list of (face list, y0, y1)
W = 6.0
for y, t in P.RIBS + [P.TIP_RIB]:
    if y <= 55.0:
        continue  # under the centre sheeting
    if y == P.TIP_RIB[0]:
        fy = (y + t / 2 - W, y + t / 2)
        ay = fy
    else:
        fy = (y - W / 2, y + W / 2)
        if y == 110.0:
            ay = (y + t / 2 - W, y + t / 2)         # aft strip flush with outer face (aileron gap)
        elif y == 439.5:
            ay = (y - t / 2, y - t / 2 + W)         # aft strip flush with inner face
        else:
            ay = None
    sol = [G.extrude(f, *fy) for f in CF[0] + CF[1]]
    if ay:
        sol += [G.extrude(f, *ay) for f in CA[0] + CA[1]]
    nm = "TipRib" if y == P.TIP_RIB[0] else "%03d" % round(y)
    comp = Part.makeCompound(sol)
    B.put("Caps_%s_R" % nm, comp, "light", "A_CapStrips", "1.5 x 6 light")
    B.put("Caps_%s_L" % nm, B.mirror_y(comp), "light", "A_CapStrips", "1.5 x 6 light")

# ---------- TE wedges ----------
TEF = G.clip(OUT, P.X_TE, P.CHORD + 1)
B.put("TE_Centre", G.extrude(TEF, -111.5, 111.5), "hard", "A_TE_Tip", "hard balsa wedge 25 mm")
both("TE_Outer", TEF, 438.5, YE, "hard", "A_TE_Tip", "hard balsa wedge 25 mm")

d.recompute()
print("ZT", round(ZT, 3), "ZB", round(ZB, 3))
print("holes", hole_log)
print("ring inset bb", RING_IN.BoundBox)
bad = [o.Name for o in d.Objects if o.TypeId == "Part::Feature" and not o.Shape.isValid()]
print("objects", len([o for o in d.Objects if o.TypeId == "Part::Feature"]), "invalid", bad)
