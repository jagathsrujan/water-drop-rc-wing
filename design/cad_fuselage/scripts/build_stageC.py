"""Stage F-C: twin tubes, tail block, stabilizer + elevator, fin + rudder (built-up balsa frames, D-055), joiner,
horns, pushrods (straight, outboard of the tubes) and guide clips. exec() inside FreeCAD after build_stageB.py.
Cruciform tail (D-057): stab continuous through the fin at Z +45; lower and upper fin glued on the stab.
Elevator and rudder hinge on one line X HINGE_X; the elevator joiner crosses the rudder axis in a rudder LE notch."""
import sys, os, math
SCRIPTS = globals().get("FUS_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad_fuselage", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import fus_params as P
import fus_build as B
import FreeCAD as App
import Part

V = App.Vector
d = B.doc()
box = B.box
OML = B.LAST_POD["oml"]
B.group("Tail")
t = P.T_SURF
zs0, zs1 = P.STAB_Z - t / 2, P.STAB_Z + t / 2


def ok(name, s):
    if s.isNull() or not s.isValid():
        raise RuntimeError(name + ": invalid shape")
    bb = B.mesh_bb(s)
    print("%-20s V %8.1f mm3  X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f  solids %d" % (name, s.Volume, *bb, len(s.Solids)))
    return s


def prism(pts, plane, off, th):
    """Closed polygon (2D pts) -> solid. plane 'xy': pts (x, y) at z=off, extruded +Z by th; 'xz': pts (x, z) at y=off, +Y by th."""
    if plane == "xy":
        p3 = [V(a, b, off) for a, b in pts]
        vec = V(0, 0, th)
    else:
        p3 = [V(a, off, b) for a, b in pts]
        vec = V(0, th, 0)
    f = Part.Face(Part.makePolygon(p3 + [p3[0]]))
    return f.extrude(vec), f


def strip(p0, p1, w, plane, off, th):
    """Rib/diagonal strip of width w along the 2D segment p0-p1, thicker than the frame (cutting tool from the windows)."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    pts = [(p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny), (p1[0] - nx, p1[1] - ny), (p0[0] - nx, p0[1] - ny)]
    return prism(pts, plane, off - 1.0, th + 2.0)[0]


def frame(pts, plane, off, th, w, strips):
    """Built-up frame: outline solid minus windows; windows = outline offset inward by w, minus the rib/diagonal strips."""
    outer, f = prism(pts, plane, off, th)
    inner_f = f.makeOffset2D(-w, join=2)
    vec = V(0, 0, th) if plane == "xy" else V(0, th, 0)
    inner = inner_f.extrude(vec)
    if strips:
        inner = inner.cut(B.fuse_all(strips))
    return outer.cut(inner).removeSplitter()


def cyl(p0, p1, r):
    a, b = V(*p0), V(*p1)
    return Part.makeCylinder(r, (b - a).Length, a, b - a)


# ---------------- tubes F10 and tail block F11 ----------------
tubes = []
for s in (1, -1):
    y = s * P.SOCK_Y
    o = cyl((P.TUBE_X[0], y, P.SOCK_Z), (P.TUBE_X[1], y, P.SOCK_Z), P.TUBE_OD / 2)
    i = cyl((P.TUBE_X[0] - 1, y, P.SOCK_Z), (P.TUBE_X[1] + 1, y, P.SOCK_Z), P.TUBE_ID / 2)
    tubes.append(o.cut(i))
TUBES = ok("F10_Tubes", B.fuse_all(tubes))

rc = P.TUBE_OD / 2 + 0.15 + P.TB_COLLAR_WALL
cx0, cx1 = P.TB_COLLAR_X
tb = [cyl((cx0, s * P.SOCK_Y, P.SOCK_Z), (cx1 + 1.0, s * P.SOCK_Y, P.SOCK_Z), rc) for s in (1, -1)]
zt = P.TB_TOP_Z
plate = box(P.TB_X[0], P.TB_X[1], -P.SOCK_Y, P.SOCK_Y, zt - P.TB_PLATE_T, zt)                           # top plate
holes_p = [box(xa, xa + 16.0, sy0, sy0 + 8.0, zt - 5, zt + 1) for xa in (672.0, 694.0, 716.0) for sy0 in (4.5, -12.5)]
tb.append(plate.cut(B.fuse_all(holes_p)))                                                                # T2: lightening holes
for s in (1, -1):                                                                                        # rib collar -> plate
    tb.append(box(cx0, cx1 + 1.0, s * P.SOCK_Y - 0.6, s * P.SOCK_Y + 0.6, P.SOCK_Z, zt - P.TB_PLATE_T + 0.01))
for xr in (cx0, 0.5 * (cx0 + cx1), cx1 + 1.0 - 1.2):                                                     # cross ribs
    tb.append(box(xr, xr + 1.2, -P.SOCK_Y, P.SOCK_Y, P.SOCK_Z - 2.0, zt - P.TB_PLATE_T + 0.01))
for sy in (1, -1):                                                                                        # fin socket walls
    y0, y1 = sorted((sy * (t / 2 + 0.1), sy * (t / 2 + 0.1 + P.TB_SOCKET_WALL)))
    tb.append(box(P.TB_X[0], P.TB_X[1], y0, y1, zt - 0.01, zt + P.TB_SOCKET_H))
TBLOCK = B.fuse_all(tb)
bores = [cyl((cx0 - 1, s * P.SOCK_Y, P.SOCK_Z), (cx1 + 0.5, s * P.SOCK_Y, P.SOCK_Z), P.TUBE_OD / 2 + 0.15) for s in (1, -1)]
TBLOCK = ok("F11_TailBlock", TBLOCK.cut(B.fuse_all(bores)).removeSplitter())

# ---------------- stabilizer F12 (fixed, continuous through the fin) and elevator F13 ----------------
xh0, xh1 = P.HINGE_X - 0.25, P.HINGE_X + 0.25           # fixed parts end at xh0, moving parts start at xh1
xle, xte, hs = P.STAB_LE_X, P.STAB_LE_X + P.STAB_C, P.STAB_HS
ribs_y = [45.0, 90.0, 135.0, 180.0]
st = [strip((xle - 2, 0), (xh0 + 2, 0), 10.0, "xy", zs0, t)]               # centre rib under the fin
for y in ribs_y:
    for s in (1, -1):
        st.append(strip((xle - 2, s * y), (xh0 + 2, s * y), 3.0, "xy", zs0, t))
bays = [0.0] + ribs_y + [hs - 6.0]
for k in range(len(bays) - 1):                                               # one diagonal per bay (Warren truss)
    for s in (1, -1):
        y0, y1 = s * bays[k], s * bays[k + 1]
        if k % 2:
            st.append(strip((xle + 6, y0), (xh0 - 6, y1), 3.0, "xy", zs0, t))
        else:
            st.append(strip((xh0 - 6, y0), (xle + 6, y1), 3.0, "xy", zs0, t))
STAB = ok("F12_Stab", frame([(xle, -hs), (xh0, -hs), (xh0, hs), (xle, hs)], "xy", zs0, t, 6.0, st))

ey0, ey1 = P.ELEV_ROOT_Y
elev = []
for s in (1, -1):
    pts = [(xh1, s * ey0), (xh1, s * hs), (xte, s * hs), (xte, s * ey1)]
    if s < 0:
        pts = pts[::-1]
    est = [strip((xh1 - 2, s * y), (xte + 2, s * y), 3.0, "xy", zs0, t) for y in ribs_y]
    elev.append(frame(pts, "xy", zs0, t, 4.0, est))
# V-bevel on the moving LEs (CA hinges, as the wing ailerons): apex on the centre plane at xh1, full thickness at xh1 + BEV
BEV = (t / 2) / math.tan(math.radians(25.0))      # 25 deg each side: clears +-20 deg elevator / +-25 deg rudder with the axis 0.25 ahead


def bevel_cutter(plane, c0):
    k = (t / 2) / BEV
    up = [(xh1 - 1.0, c0 - k * 1.0), (xh1 + BEV, c0 + t / 2), (xh1 + BEV, c0 + t), (xh1 - 1.0, c0 + t)]
    dn = [(xh1 - 1.0, c0 + k * 1.0), (xh1 + BEV, c0 - t / 2), (xh1 + BEV, c0 - t), (xh1 - 1.0, c0 - t)]
    if plane == "xz":                 # elevator: section in XZ, extruded along Y
        return prism(up, "xz", -300, 600)[0].fuse(prism(dn[::-1], "xz", -300, 600)[0])
    return prism(up, "xy", -100, 300)[0].fuse(prism(dn[::-1], "xy", -100, 300)[0])   # rudder: section in XY, along Z


elev = [e.cut(bevel_cutter("xz", P.STAB_Z)) for e in elev]
ELEV = ok("F13_Elevator", Part.makeCompound(elev))

# ---------------- fin F14 (lower + upper, glued on the stab) and rudder F15 ----------------
def le_x(z):
    return P.HINGE_X - 0.25 - 0.65 * (P.FIN_CR + (P.FIN_CT - P.FIN_CR) * (z - P.FIN_ROOT_Z) / (P.FIN_TIP_Z - P.FIN_ROOT_Z))


def te_x(z):
    return P.HINGE_X + 0.35 * (P.FIN_CR + (P.FIN_CT - P.FIN_CR) * (z - P.FIN_ROOT_Z) / (P.FIN_TIP_Z - P.FIN_ROOT_Z))


yf = -t / 2
z0, z1 = P.FIN_ROOT_Z, P.FIN_TIP_Z
lo = [(le_x(z0), z0), (xh0, z0), (xh0, zs0), (le_x(zs0), zs0)]
zm = 0.5 * (z0 + zs0)
lo_st = [strip((le_x(zm) - 2, zm), (xh0 + 2, zm), 3.0, "xz", yf, t),
         strip((xh0 - 5, z0 + 5), (le_x(zm) + 5, zm), 3.0, "xz", yf, t),
         strip((le_x(zm) + 5, zm), (xh0 - 5, zs0 - 5), 3.0, "xz", yf, t)]
up = [(le_x(zs1), zs1), (xh0, zs1), (xh0, z1), (le_x(z1), z1)]
zu = 0.5 * (zs1 + z1)
up_st = [strip((le_x(zu) - 2, zu), (xh0 + 2, zu), 3.0, "xz", yf, t),
         strip((xh0 - 5, zs1 + 5), (le_x(zu) + 5, zu), 3.0, "xz", yf, t),
         strip((le_x(zu) + 5, zu), (xh0 - 5, z1 - 5), 3.0, "xz", yf, t)]
FIN = ok("F14_Fin", Part.makeCompound([frame(lo, "xz", yf, t, 6.0, lo_st), frame(up, "xz", yf, t, 6.0, up_st)]))

zr0 = P.RUD_Z0
rud_pts = [(xh1, zr0), (te_x(zr0), zr0), (te_x(z1), z1), (xh1, z1)]
r_st = [strip((xh1 - 2, z), (te_x(z) + 2, z), 3.0 if abs(z - P.STAB_Z) > 1 else 10.0, "xz", yf, t) for z in (10.0, P.STAB_Z, 90.0)]
rud = frame(rud_pts, "xz", yf, t, 4.0, r_st)
notch = cyl((P.JOINER_X, -5, P.STAB_Z), (P.JOINER_X, 5, P.STAB_Z), P.RUD_NOTCH_D / 2).fuse(
    box(xh1 - 1, P.JOINER_X, -5, 5, P.STAB_Z - P.RUD_NOTCH_D / 2, P.STAB_Z + P.RUD_NOTCH_D / 2))
RUD = ok("F15_Rudder", rud.cut(notch).cut(bevel_cutter("xy", 0.0)).removeSplitter())

# ---------------- joiner, horns ----------------
jr = P.JOINER_D / 2
jx, jy, jl = P.JOINER_X, P.JOINER_HY, P.JOINER_LEG
jn = [cyl((jx, -jy, P.STAB_Z), (jx, jy, P.STAB_Z), jr)]
for s in (1, -1):
    jn.append(cyl((jx, s * jy, P.STAB_Z), (jx + jl, s * jy, P.STAB_Z), jr))
    jn.append(Part.makeSphere(jr, V(jx, s * jy, P.STAB_Z)))
JOINER = ok("F16_Joiner", B.fuse_all(jn))

hx, hy, hz = P.ELEV_HORN_PT
eh, _ = prism([(xh1 + BEV + 0.3, zs0), (xh1 + 14, zs0), (hx + 3.0, hz - 2.5), (hx - 2.0, hz - 2.5)], "xz", hy - P.HORN_T / 2, P.HORN_T)
eh = eh.cut(cyl((hx, hy - 2, hz), (hx, hy + 2, hz), P.HORN_HOLE / 2))
rx, ry, rz = P.RUD_HORN_PT
rh, _ = prism([(xh1 + BEV + 0.3, t / 2), (xh1 + 14, t / 2), (rx + 3.0, ry + 2.5), (rx - 2.0, ry + 2.5)], "xy", rz - P.HORN_T / 2, P.HORN_T)
rh = rh.cut(cyl((rx, ry, rz - 2), (rx, ry, rz + 2), P.HORN_HOLE / 2))
HORNS = ok("F17_Horns", Part.makeCompound([eh, rh]))

# ---------------- servo arms (placeholders), pushrods F18, exits in F3, guide clips F19 ----------------
arms, rods, lines = [], [], {}
for nm, s, end in (("Elevator", -1, P.ELEV_HORN_PT), ("Rudder", 1, P.RUD_HORN_PT)):
    sx, sy = P.TSERVO_SHAFT_X, s * P.TSERVO_YC
    a0, a1 = sorted((sy, s * (P.ARM_HOLE_Y + 2.0)))
    arms.append(box(sx - 2.0, sx + 2.0, a0, a1, P.ARM_Z - 2.5, P.ARM_Z - 1.0).fuse(cyl((sx, sy, P.ARM_Z - 2.5), (sx, sy, P.TSERVO_ZB + P.TSERVO[2]), 3.0)))
    p0 = (sx, s * P.ARM_HOLE_Y, P.ARM_Z)
    lines[nm] = (p0, end)
    rods.append(cyl(p0, end, P.PUSHROD_D / 2))
B.put("PH_TailServoArms", Part.makeCompound(arms), "Placeholder", P.COL_PH, 0, props=dict(Note="servo arm placeholders (8 mm outboard)"))
RODS = ok("F18_Pushrods", Part.makeCompound(rods))

F3 = d.getObject("F3_PodAft").Shape
exits = []
for nm, (p0, p1) in lines.items():
    e = Part.makeLine(V(*p0), V(*p1))
    inside = e.common(OML)
    xe = max(v.Point.x for v in inside.Vertexes)
    vp0, vp1 = V(*p0), V(*p1)
    u = (vp1 - vp0)
    u.normalize()
    pe = vp0 + u * ((xe - p0[0]) / u.x)
    exits.append(Part.makeCylinder(2.0, 30.0, pe - u * 15.0, u))
    print("pushrod %s exits the pod at X %.1f Y %.1f Z %.1f (exit slot D4, +-15 mm along the rod)" % (nm, pe.x, pe.y, pe.z))
o3 = d.getObject("F3_PodAft")
o3.Shape = ok("F3_PodAft", F3.cut(B.fuse_all(exits)).removeSplitter())

clips = []
for gx in P.GUIDE_X:
    for nm, (p0, p1) in lines.items():
        f = (gx - p0[0]) / (p1[0] - p0[0])
        rp = V(p0[0] + f * (p1[0] - p0[0]), p0[1] + f * (p1[1] - p0[1]), p0[2] + f * (p1[2] - p0[2]))
        ty = math.copysign(P.SOCK_Y, rp.y)
        tc = V(gx, ty, P.SOCK_Z)
        collar = cyl((gx - 3, ty, P.SOCK_Z), (gx + 3, ty, P.SOCK_Z), P.TUBE_OD / 2 + 1.2)
        arm = Part.makeCylinder(1.0, (rp - tc).Length, tc, rp - tc)
        eye = cyl((gx - 3, rp.y, rp.z), (gx + 3, rp.y, rp.z), P.PUSHROD_D / 2 + 1.2)
        g = collar.fuse(arm.fuse(eye))
        g = g.cut(cyl((gx - 4, ty, P.SOCK_Z), (gx + 4, ty, P.SOCK_Z), P.TUBE_OD / 2 + 0.1))
        ur = V(*[(c1 - c0) for c0, c1 in zip(p0, p1)])
        ur.normalize()
        g = g.cut(Part.makeCylinder(P.PUSHROD_D / 2 + 0.3, 40, rp - ur * 20, ur))
        clips.append(g)
CLIPS = ok("F19_GuideClips", Part.makeCompound(clips))

for n, s, c, note in (("F10_Tubes", TUBES, P.COL_CARBON, "2 x carbon tube D8/6, glued in the pod sockets and the tail block"),
                      ("F11_TailBlock", TBLOCK, P.COL_PETG, "PETG tail block: collars, plate, fin socket"),
                      ("F12_Stab", STAB, P.COL_BALSA, "built-up balsa 3 mm stabilizer (fixed), continuous through the fin"),
                      ("F13_Elevator", ELEV, (0.95, 0.80, 0.55), "built-up balsa 3 mm elevator halves, joined by F16"),
                      ("F14_Fin", FIN, P.COL_BALSA, "built-up balsa 3 mm fin, lower + upper part on the stab"),
                      ("F15_Rudder", RUD, (0.95, 0.80, 0.55), "built-up balsa 3 mm rudder, LE notch for the joiner"),
                      ("F16_Joiner", JOINER, (0.55, 0.55, 0.6), "steel wire D1.5 elevator joiner"),
                      ("F17_Horns", HORNS, (0.9, 0.9, 0.9), "horns, 1.5 mm G10 or nylon"),
                      ("F18_Pushrods", RODS, P.COL_CARBON, "carbon D2 pushrods, steel Z-bend ends"),
                      ("F19_GuideClips", CLIPS, P.COL_PETG, "PETG guide clips on the tubes")):
    B.put(n, s, "Tail", c, 0, props=dict(Note=note))
d.recompute()
print("stage F-C build done")
