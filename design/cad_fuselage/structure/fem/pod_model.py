"""Pod shell FEM model for the structure study (stage F-S).

Geometry: outer surface of the F-A pod shell without the hatch F4 (F1 + F2 + F3; built read-only with
scripts/fus_build.build_pod()), plus the members that F-B adds in any case (baseline) and the members of the
design variant (frames, ribs, cross bars, windows from scripts/fus_struct.py). Shell elements on the outer surface
(thickness by zone, offset ignored: <= 0.4 mm).
Run inside the FreeCAD Python: /Applications/FreeCAD.app/Contents/Resources/bin/python run_study.py <variant>
Frame: wing frame, mm. Units N, mm, t, s.
"""
import sys
import os
import math
sys.path.append("/Applications/FreeCAD.app/Contents/Resources/lib")
import FreeCAD as App  # noqa: E402
import Part  # noqa: E402
from FreeCAD import Vector as V  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
STRUCT = os.path.dirname(HERE)
SCRIPTS = os.path.join(os.path.dirname(STRUCT), "scripts")
for p_ in (HERE, SCRIPTS):
    if p_ not in sys.path:
        sys.path.insert(0, p_)
import shellfem as F  # noqa: E402
import fus_params as P  # noqa: E402
import fus_build as B  # noqa: E402

# ---------------------------------------------------------------- materials (interp., notebook section 2.3)
E_ASA = math.sqrt(866.0 * 509.0)          # ASA Aero 0.65: geometric mean of E_XY and E_Z = 664 MPa (orthotropic plate)
E_PLA = math.sqrt(2680.0 * 2160.0)        # PLA Basic: 2406 MPa
SIG = {"ASA Aero 0.65": dict(xy=11.9, z=5.6), "PLA": dict(xy=27.3, z=17.5)}   # allowables (knock-down 0.7 / 0.5)
FOS = 1.5
RHO_INERTIA = 1.24e-9                     # printed parts: PLA density for the self-weight (heavier aircraft)
MATS = {"PR": (E_ASA, 0.35, RHO_INERTIA),   # printed shell, ribs, frames
        "BA": (1000.0, 0.30, 0.16e-9),      # 3 mm balsa front stop (isotropic average, interp.)
        "PL": (5000.0, 0.30, 0.65e-9)}      # 3 mm birch ply firewall (interp.)

# ---------------------------------------------------------------- stations used by the model (interp. where marked)
STOP_XM = 0.5 * (P.STOP_X[0] + P.STOP_X[1])     # -27.72 (as built)
STOP_ZTOP = -25.0                                # reservoir STOP_Z top
STOP_HOLE = (0.0, -60.0, 25.0)                   # Y, Z, radius (bottle axis)
FW_X = P.FIREWALL_X                              # firewall plane (pod front, on the skin front edges)
SOCK_X = (233.0, 300.0)                          # socket bearings (front bulkhead, end wall) (interp., F-B)
SOCK_ZTOP = -28.0                                # top of the socket block (interp.)
TUBE_Y, TUBE_Z = 16.0, -40.0                     # plan T2-3
STUB = (-6.0, -24.0)                             # band stubs X, Z (D-053)
DOWEL = (295.0, -22.0)                           # rear dowel X, Z
SKID_F, SKID_R, SKID_Y = (-30.0, 40.0), (120.0, 195.0), 35.0     # belly skids (interp., F-B)
PALM = (40.0, 120.0, 20.0, 50.0)                 # launch grip palm patch X0, X1, |Y|0, |Y|1 (D-054)
SQUEEZE_N = 20.0                                 # finger squeeze each side (D-064)
FINGERS = (50.0, 110.0, -100.0, -60.0)           # finger patches on both side walls X0, X1, Z0, Z1

BASE = dict(name="base", hmax=4.5, lip=(8.0, 0.8), frames=[(175.0, 6.0, 0.8)], t_over={}, struct=None)


def W_of(x):
    return B.side_sec(x)[0]


def top_skin(x):
    """Z of the skin top edge: the top line, 3 mm lower in the hatch region (hatch F4 removed)."""
    z = B.top_line(x)
    if P.HATCH_X[0] <= x <= P.HATCH_X[1]:
        z -= P.HATCH_DEPTH
    return z


# ---------------------------------------------------------------- geometry
def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


# FEM-only simplifications of the F-A surface (in memory, the file fus_params.py is not changed): the aft ruled loft
# in 20 mm steps (F-A: 5 mm) and the deck top corner R3 at X 280 (F-A: R0.3). The 5 mm strips and the R0.3 corner
# give faces < 0.5 mm wide and elements with a negative Jacobian (first base run). Shape change <= 0.3 mm (aft taper)
# and about 0.8 mm at the deck corner.
FEM_PARAM_PATCH = dict(AFT_LOFT_DX=20.0, DECK_RT=(3.0, 6.0))


def pod_shapes():
    for k, v in FEM_PARAM_PATCH.items():
        setattr(P, k, v)
    R = B.build_pod()
    rest = R["shell"].cut(B.hatch_region()).removeSplitter()
    return R, rest


def outer_faces(rest, inner):
    out = []
    for f in rest.Faces:
        pts, _ = f.tessellate(1.0)
        if pts and not any(inner.isInside(p, 0.05, True) for p in pts[:: max(1, len(pts) // 40)]):
            out.append(f)
    return out


def section_face(oml, x):
    ws = oml.slice(V(1, 0, 0), x)
    fs = [Part.Face(w) for w in ws if w.isClosed()]
    fs.sort(key=lambda f: -f.Area)
    return fs[0]


def frame_ribbon(oml, x, depth, top=None):
    """Planar ring rib at station x: OML section minus its inward offset by `depth`, without the top band
    (open top: no cross member above the bottle, D-046). top = Z of the skin top edge at x."""
    sf = section_face(oml, x)
    inner = sf.makeOffset2D(-depth)
    rib = sf.cut(inner)
    zt = top_skin(x) if top is None else top
    W = W_of(x)
    rib = rib.cut(box(x - 1, x + 1, -(W - depth - 0.05), W - depth - 0.05, zt - depth - 0.05, 50))
    rib = rib.cut(box(x - 1, x + 1, -100, 100, zt, 100))
    return rib


def lip_faces(skin_faces, width):
    edges = []
    for f in skin_faces:
        for e in f.Edges:
            ps = e.discretize(7)
            if not all(-2.5 <= p.x <= 280.5 for p in ps):
                continue
            if all(abs(p.z - B.top_line(p.x)) < 0.05 and abs(abs(p.y) - W_of(p.x)) < 0.05 for p in ps):
                if not any(e.isSame(q) for q in edges):
                    edges.append(e)
    out = []
    for e in edges:
        s = 1.0 if e.discretize(3)[1].y > 0 else -1.0
        e2 = e.copy()
        e2.translate(V(0, -s * width, 0))
        out.append(Part.makeRuledSurface(e, e2))
    return out


def baseline_members(oml, cfg):
    mem = {}
    # front stop former (3 mm balsa in a printed slot), Z <= -25, hole D50 on the bottle axis
    sf = section_face(oml, STOP_XM).common(box(STOP_XM - 1, STOP_XM + 1, -100, 100, -200, STOP_ZTOP))
    hole = Part.Face(Part.Wire(Part.makeCircle(STOP_HOLE[2], V(STOP_XM, STOP_HOLE[0], STOP_HOLE[1]), V(1, 0, 0))))
    mem["stop"] = sf.cut(hole)
    # firewall (3 mm ply), closed frame at the pod front: face on the exact front edges of the skin (X -170)
    mem["firewall"] = None
    # ring ribs at the formers / joints
    mem["frames"] = [] if cfg.get("struct") else [frame_ribbon(oml, x, d) for x, d, t in cfg["frames"]]
    # socket block (interp.): front bulkhead + two webs along the tubes, below Z -28; the end wall X 300 is skin
    x0, x1 = SOCK_X
    mem["sock_bulk"] = section_face(oml, x0).common(box(x0 - 1, x0 + 1, -100, 100, -200, SOCK_ZTOP))
    webs = []
    for s in (-1, 1):
        ws = oml.slice(V(0, 1, 0), s * TUBE_Y)
        fw = [Part.Face(w) for w in ws if w.isClosed()]
        fw.sort(key=lambda f: -f.Area)
        webs.append(fw[0].common(box(x0, x1 - 0.8, s * TUBE_Y - 1, s * TUBE_Y + 1, -200, SOCK_ZTOP)))
    mem["sock_webs"] = webs
    return mem


def build_geometry(cfg, workdir):
    """Writes <workdir>/<name>.brep (compound of faces). Returns dict(info...)."""
    R, rest = pod_shapes()
    oml, inner = R["oml"], R["inner"]
    skin = outer_faces(rest, inner)
    struct = cfg.get("struct")
    if struct is not None:                     # design variant: windows cut from the skin, extra members
        skin = struct["cut_skin"](skin)
    mem = baseline_members(oml, cfg)
    fe = [e for f in skin for e in f.Edges if all(abs(p.x - P.FIREWALL_X) < 1e-3 for p in e.discretize(5))]
    uniq = []
    for e in fe:
        if not any(e.isSame(q) for q in uniq):
            uniq.append(e)
    mem["firewall"] = Part.Face(Part.Wire(Part.__sortEdges__(uniq)))
    faces = list(skin)
    faces += lip_faces(skin if struct is None else outer_faces(rest, inner), cfg["lip"][0]) if cfg.get("lip") else []
    faces += [mem["stop"], mem["firewall"], mem["sock_bulk"]] + mem["frames"] + mem["sock_webs"]
    if struct is not None:
        faces += struct["member_faces"](oml)
    comp = Part.makeCompound([f for f in faces if f is not None and f.Area > 1e-3])
    os.makedirs(workdir, exist_ok=True)
    path = os.path.join(workdir, cfg["name"] + ".brep")
    comp.exportBrep(path)
    area_skin = sum(f.Area for f in skin)
    return dict(brep=path, n_faces=len(comp.Faces), skin_area=area_skin)


# ---------------------------------------------------------------- classification of the mesh
def classify(m, cfg):
    """Returns ctx with element arrays: cen, nrm, area, tag (str), t (thickness), mat."""
    cen, area, nrm = F.elem_geom(m)
    X, Y, Z = cen.T
    nx, ny, nz = np.abs(nrm).T
    ne = len(X)
    tag = np.array(["skin"] * ne, dtype=object)
    Wx = np.array([W_of(x) for x in X])
    topx = np.array([B.top_line(x) for x in X])
    zb = np.array([B.side_sec(x)[1] for x in X])
    rb = np.array([B.side_sec(x)[2] for x in X])
    on = lambda x0: (np.abs(X - x0) < 0.06) & (nx > 0.95)
    tag[on(STOP_XM)] = "stop"
    tag[on(FW_X)] = "firewall"
    for x, d, t in cfg["frames"]:
        tag[on(x) & (tag == "skin")] = "frame"
    tag[on(SOCK_X[0]) & (Z < SOCK_ZTOP + 0.1)] = "sock_bulk"
    tag[(np.abs(np.abs(Y) - TUBE_Y) < 0.06) & (ny > 0.95) & (X > SOCK_X[0] - 0.1)] = "sock_web"
    if cfg.get("lip"):
        lw = cfg["lip"][0]
        lip = (nz > 0.85) & (Z > topx - 0.8) & (X < 280.3) & (X > -2.6) & (np.abs(Y) > Wx - lw - 0.6)
        tag[lip & (tag == "skin")] = "lip"
    struct = cfg.get("struct")
    if struct is not None:
        struct["tag"](tag, cen, nrm, Wx, topx)
    t = np.zeros(ne)
    mat = np.array(["PR"] * ne, dtype=object)
    sk = tag == "skin"
    to = dict(nose=P.T_NOSE, floor=P.T_FLOOR, side=P.T_SIDE, aft_bottom=P.T_AFT_BOTTOM, end=P.T_END, deck=P.T_SIDE)
    to.update(cfg.get("t_over", {}))
    zone = np.array([""] * ne, dtype=object)
    bottom = (Z < zb + rb + 0.3) | (nrm[:, 2] < -0.35)
    zone[sk & (X < P.NOSE_END_X)] = "nose"
    zone[sk & (X >= P.NOSE_END_X) & bottom] = "floor"
    zone[sk & (X >= P.NOSE_END_X) & ~bottom] = "side"
    zone[sk & (X > P.AFT_X0) & bottom] = "aft_bottom"
    zone[sk & (X > P.OPEN_X[1]) & (nrm[:, 2] > 0.35)] = "deck"
    zone[sk & (X > P.POD_END_X - 0.05)] = "end"
    for zn, tv in to.items():
        t[zone == zn] = tv
    # local reinforcements (interp., F-B features)
    bos = sk & (np.abs(Y) > Wx - 1.0) & (np.hypot(X - STUB[0], Z - STUB[1]) < 7.0)
    t[bos] = 2.0
    zone[bos] = "boss"
    dw = sk & (np.abs(Y) > Wx - 1.5) & (np.hypot(X - DOWEL[0], Z - DOWEL[1]) < 6.0)
    t[dw] = 2.0
    zone[dw] = "boss"
    pocket = sk & (Y > 0) & (X > 52) & (X < 77) & (Z > -113) & (Z < -107)
    t[pocket] = 1.2
    zone[pocket] = "pocket"
    sockskin = sk & (X > SOCK_X[0]) & (Z < SOCK_ZTOP) & (zone != "boss")
    t[sockskin] = np.maximum(t[sockskin], 1.5)
    zone[sockskin & (zone != "end")] = "sock_skin"
    t[zone == "end"] = 2.0
    for tg, tv, mt in (("stop", 3.0, "BA"), ("firewall", 3.0, "PL"), ("sock_bulk", 2.0, "PR"), ("sock_web", 1.5, "PR"),
                       ("lip", cfg["lip"][1] if cfg.get("lip") else 0.8, "PR")):
        t[tag == tg] = tv
        mat[tag == tg] = mt
    for x, d, tt in cfg["frames"]:
        t[(tag == "frame") & (np.abs(X - x) < 0.06)] = tt
    if struct is not None:
        struct["thick"](t, tag, zone, cen, nrm)
    zone[tag != "skin"] = tag[tag != "skin"]
    if (t <= 0).any():
        bad = np.where(t <= 0)[0][:5]
        raise RuntimeError("elements without thickness: %s" % [(tag[i], zone[i], cen[i].round(1)) for i in bad])
    return dict(cen=cen, nrm=nrm, area=area, tag=tag, zone=zone, t=t, mat=mat, W=Wx, top=topx)


def groups(ctx):
    """Element groups for the deck: one per (thickness, material)."""
    keys = sorted(set(zip(np.round(ctx["t"], 3), ctx["mat"])))
    out = []
    for i, (tv, mt) in enumerate(keys):
        idx = np.where((np.round(ctx["t"], 3) == tv) & (ctx["mat"] == mt))[0]
        out.append(("G%02d" % i, idx, float(tv), mt))
    return out


def mass_g(ctx, rho_g_cm3):
    """Mass of the printed elements (PR) for a density in g/cm3."""
    pr = ctx["mat"] == "PR"
    return float(np.sum(ctx["area"][pr] * ctx["t"][pr]) * rho_g_cm3 / 1000.0)


# ---------------------------------------------------------------- load cases
KG = 9.81  # N/kg


def _nodes(m, mask):
    e = m["elems"][mask]
    return sorted(set(int(v) for v in e.ravel() if v > 0))


def selectors(m, ctx):
    X, Y, Z = ctx["cen"].T
    tag, zone = ctx["tag"], ctx["zone"]
    S = {}
    floor = (zone == "floor") & (Z < P.BELLY_Z + 0.2)
    S["sad1"] = floor & (X > P.SADDLE1_X[0] - 4) & (X < P.SADDLE1_X[1] + 4) & (np.abs(Y) > 5) & (np.abs(Y) < 40)
    S["sad2"] = floor & (X > 139.28) & (X < P.SADDLE2_X[1]) & (np.abs(Y) > 5) & (np.abs(Y) < 40)
    S["stop_ring"] = (tag == "stop") & (np.hypot(Y - STOP_HOLE[0], Z - STOP_HOLE[1]) < STOP_HOLE[2] + 10)
    S["fw_c"] = (tag == "firewall") & (np.hypot(Y, Z + 50.0) < 15.0)
    S["fw"] = tag == "firewall"
    S["esc"] = (zone == "nose") & (X > -160) & (X < -130) & (ctx["nrm"][:, 2] < -0.5)
    S["bat"] = (zone == "nose") & (X > -122) & (X < -62) & (np.abs(Y) < 17.5) & (ctx["nrm"][:, 2] < -0.5)
    S["servo"] = (Y > 0) & (X > 55) & (X < 75) & (Z > -110) & (Z < -85) & np.isin(zone, ["side", "pocket"])
    S["lips"] = tag == "lip"
    S["lip_f"] = S["lips"] & (X < 60)
    S["lip_r"] = S["lips"] & (X > 220)
    S["tservo"] = np.isin(zone, ["floor", "aft_bottom"]) & (X > 195) & (X < 232)
    S["wiring"] = floor & (X > -30) & (X < 150) & (np.abs(Y) < 45)
    S["stubL"] = (zone == "boss") & (Y < 0) & (X < 100)
    S["stubR"] = (zone == "boss") & (Y > 0) & (X < 100)
    S["dowL"] = (zone == "boss") & (Y < 0) & (X > 100)
    S["dowR"] = (zone == "boss") & (Y > 0) & (X > 100)
    for s, nm in ((-1, "L"), (1, "R")):
        S["brgF" + nm] = (tag == "sock_bulk") & (np.hypot(Y - s * TUBE_Y, Z - TUBE_Z) < 6.5)
        # end-wall plane by position (in a design variant the rib tagging can take end-wall elements: zone test fails)
        S["brgR" + nm] = (np.abs(X - SOCK_X[1]) < 1.0) & (np.abs(ctx["nrm"][:, 0]) > 0.9) & (np.hypot(Y - s * TUBE_Y, Z - TUBE_Z) < 6.5)
    belly = np.isin(zone, ["floor"]) & (Z < P.BELLY_Z + 0.05)
    S["skidF"] = belly & (X > SKID_F[0]) & (X < SKID_F[1]) & (np.abs(Y) < SKID_Y)
    S["skidR"] = belly & (X > SKID_R[0]) & (X < SKID_R[1]) & (np.abs(Y) < SKID_Y)
    S["aftbot"] = np.isin(zone, ["aft_bottom", "sock_skin"]) & (ctx["nrm"][:, 2] < -0.35) & (X > 225) & (X < 290) & (np.abs(Y) < 15)
    S["palm"] = belly & (X > PALM[0]) & (X < PALM[1]) & (np.abs(Y) > PALM[2]) & (np.abs(Y) < PALM[3])
    side = np.isin(zone, ["side", "pocket"])
    S["fingL"] = side & (Y < 0) & (X > FINGERS[0]) & (X < FINGERS[1]) & (Z > FINGERS[2]) & (Z < FINGERS[3])
    S["fingR"] = side & (Y > 0) & (X > FINGERS[0]) & (X < FINGERS[1]) & (Z > FINGERS[2]) & (Z < FINGERS[3])
    for k, v in S.items():
        if not v.any():
            raise RuntimeError("empty selector %s" % k)
    return S


def inertia(m, S, n_vec, wing=True, wing_to="lips"):
    """Inertia loads of the carried items for an acceleration field n_vec (in g, direction of the inertia force).
    Returns (loads, grav) ; grav applies to the pod structure."""
    n = np.asarray(n_vec, float)
    L = []
    res = 1.0475
    f1 = (154.6 - 80.0) / (154.6 - 12.0)
    if abs(n[2]) > 0 or abs(n[1]) > 0:      # vertical / lateral share on the saddles
        nv = n.copy()
        nv[0] = 0.0
        L.append(F.patch_load(m, S["sad1"], res * KG * nv * f1))
        L.append(F.patch_load(m, S["sad2"], res * KG * nv * (1 - f1)))
    if n[0] < 0:                            # forward inertia (-X): bottle base on the front stop
        L.append(F.patch_load(m, S["stop_ring"], (res * KG * n[0], 0, 0)))
    elif n[0] > 0:                          # aft inertia (+X): straps and saddle 2 shoulder
        L.append(F.patch_load(m, S["sad2"], (res * KG * n[0], 0, 0)))
    L.append(F.patch_load(m, S["servo"], 0.0134 * KG * n))
    L.append(F.patch_load(m, S["fw_c"], 0.070 * KG * n))
    L.append(F.patch_load(m, S["esc"], 0.025 * KG * n))
    L.append(F.patch_load(m, S["bat"], 0.085 * KG * n))
    L.append(F.patch_load(m, S["tservo"], 0.026 * KG * n))
    L.append(F.patch_load(m, S["wiring"], 0.015 * KG * n))
    if wing:
        fw = 0.184 * KG * n
        if wing_to == "lips":
            if fw[2] != 0 or fw[1] != 0:
                L.append(F.patch_load(m, S["lips"], (0, fw[1], fw[2])))
            if fw[0] != 0:
                for k in ("stubL", "stubR"):
                    L.append(F.patch_load(m, S[k], (fw[0] / 2, 0, 0)))
    # tail: tubes 33 g at X 475 + tail 33 g at X 650 -> bearing forces (front X 233, rear X 300)
    L.append(tail_loads(m, S, 0.066 * KG * n, 562.5))
    grav = (float(np.linalg.norm(n)) * F.G, tuple(n / max(np.linalg.norm(n), 1e-12))) if np.linalg.norm(n) > 0 else None
    return F.add_loads(*L), grav


def tail_loads(m, S, Fv, x_t, per_tube=None):
    """Force Fv (vector, N) acting on the twin tubes at X x_t, shared equally (or per_tube=(FL, FR)); returns the
    bearing forces on the front bulkhead (X 233) and the end wall (X 300)."""
    x0, x1 = SOCK_X
    kr = (x_t - x0) / (x1 - x0)
    kf = -(x_t - x1) / (x1 - x0)
    FL, FR = per_tube if per_tube is not None else (np.asarray(Fv) / 2, np.asarray(Fv) / 2)
    L = []
    for f, nm in ((FL, "L"), (FR, "R")):
        f = np.asarray(f, float)
        L.append(F.patch_load(m, S["brgR" + nm], f * kr))
        L.append(F.patch_load(m, S["brgF" + nm], f * kf))
    return F.add_loads(*L)


# carried items for the rigid-body (inertia-relief) cases: (selector or special, mass kg, point mm)
ITEMS = [("sad", 1.0475, (80.0, 0.0, -60.0)), ("servo", 0.0134, (64.0, 45.0, -96.0)), ("fw_c", 0.070, (-190.0, 0.0, -50.0)),
         ("esc", 0.025, (-145.0, 0.0, -95.0)), ("bat", 0.085, (-92.0, 0.0, -95.0)), ("tservo", 0.026, (215.0, 0.0, -100.0)),
         ("wiring", 0.015, (60.0, 0.0, -110.0)), ("lips", 0.184, (110.0, 0.0, 0.0)), ("tail", 0.066, (562.5, 0.0, -25.0))]
OWN_IYY = {"sad": 1.0475 * (0.256 ** 2 / 12 + 0.04 ** 2 / 4), "lips": 0.184 * 0.28 ** 2 / 12, "tail": 0.033 * 0.49 ** 2 / 12}


def rigid_body(ctx):
    """Mass, CG (mm) and pitch inertia Iyy (kg m2) of the loaded aircraft: items + modelled pod structure."""
    rho = {"PR": 1.24, "BA": 0.16, "PL": 0.65}
    me = ctx["area"] * ctx["t"] * np.array([rho[k] for k in ctx["mat"]]) * 1e-6          # kg per element
    pts = [np.asarray(p) for _, _, p in ITEMS] + list(ctx["cen"])
    ms = np.array([mm for _, mm, _ in ITEMS] + list(me))
    pts = np.array(pts)
    M = ms.sum()
    cg = (ms[:, None] * pts).sum(axis=0) / M
    d = (pts - cg) / 1000.0
    Iyy = float(np.sum(ms * (d[:, 0] ** 2 + d[:, 2] ** 2)) + sum(OWN_IYY.values()))
    return dict(M=float(M), cg=cg, Iyy=Iyy, me=me, m_struct=float(me.sum()))


def relief(m, ctx, S, rb, Fc, patch):
    """Self-balanced load set: contact force Fc (N) on the patch; every mass gets the inertia force -m a(r) of the
    rigid aircraft, a = Fc/M + alpha x (r - cg), alpha_y = [(rc - cg) x Fc]_y / Iyy. Returns loads."""
    Fc = np.asarray(Fc, float)
    _, ar, _ = F.elem_geom(m)
    w = ar[S[patch]]
    rc = (ctx["cen"][S[patch]] * w[:, None]).sum(axis=0) / w.sum()
    cg = rb["cg"]
    a0 = Fc / rb["M"]                                         # m/s2 (N/kg)

    def pc(key):                                              # area centroid of a load patch
        ww = ar[S[key]]
        return (ctx["cen"][S[key]] * ww[:, None]).sum(axis=0) / ww.sum()
    arm = (rc - cg) / 1000.0
    al = (arm[2] * Fc[0] - arm[0] * Fc[2]) / rb["Iyy"]        # (r x F)_y
    acc = lambda r: a0 + np.array([al * (r[2] - cg[2]) / 1000.0, 0.0, -al * (r[0] - cg[0]) / 1000.0])
    L = [F.patch_load(m, S[patch], Fc)]
    for key, mass, p in ITEMS:
        if key == "sad":
            f1 = (154.6 - 80.0) / (154.6 - 12.0)
            q = f1 * pc("sad1") + (1 - f1) * pc("sad2")
            p = (q[0], q[1], p[2])                                # X force acts on the stop ring at the bottle axis Z
        elif key != "tail":
            p = pc(key)
        f = -mass * acc(np.asarray(p))
        if key == "sad":
            f1 = (154.6 - 80.0) / (154.6 - 12.0)
            L.append(F.patch_load(m, S["sad1"], (0, f[1] * f1, f[2] * f1)))
            L.append(F.patch_load(m, S["sad2"], (0, f[1] * (1 - f1), f[2] * (1 - f1))))
            L.append(F.patch_load(m, S["stop_ring"] if f[0] < 0 else S["sad2"], (f[0], 0, 0)))
        elif key == "tail":
            L.append(tail_loads(m, S, f, 562.5))
        elif key == "lips":
            L.append(F.patch_load(m, S["lips"], (0, f[1], f[2])))
            if f[0] != 0:
                for k in ("stubL", "stubR"):
                    L.append(F.patch_load(m, S[k], (f[0] / 2, 0, 0)))
        else:
            L.append(F.patch_load(m, S[key], f))
    st = {}
    for i in range(len(ar)):                                  # structure inertia, lumped on the element nodes
        f = -rb["me"][i] * acc(ctx["cen"][i])
        nds = [v for v in m["elems"][i] if v > 0]
        for nd in nds:
            st[nd] = st.get(nd, np.zeros(3)) + f / len(nds)
    L.append(st)
    info = dict(a0_g=(a0 / KG).round(2).tolist(), alpha=al, n_nose=float((acc((-190, 0, -50)) / KG)[2]),
                n_tail=float((acc((562.5, 0, -25)) / KG)[2]), n_contact=float((acc(rc) / KG)[2]), rc=rc.round(1).tolist())
    return F.add_loads(*L), info


def load_cases(m, ctx):
    """Returns (cases, nsets). Each case: dict(name, desc, bc, loads, grav, buckle(bool), rf_sets)."""
    S = selectors(m, ctx)
    ns = {}
    for k in ("stubL", "stubR", "dowL", "dowR", "skidF", "skidR", "aftbot", "palm"):
        ns["N" + k.upper()] = _nodes(m, S[k])
    ids, xyz = F.node_array(m)

    def near(p):
        return int(ids[np.argmin(np.sum((xyz - np.asarray(p)) ** 2, axis=1))])
    WL = W_of(STUB[0])
    ns["NA"] = [near((STUB[0], -WL, STUB[1]))]
    ns["NB"] = [near((DOWEL[0], -W_of(DOWEL[0]), DOWEL[1]))]
    ns["NC"] = [near((STUB[0], WL, STUB[1]))]
    ns["NSKX"] = [near((0.0, 0.0, P.BELLY_Z))]
    ns["NSKY"] = [near((160.0, 0.0, P.BELLY_Z))]
    wing_bc = [("NSTUBL", 1, 3), ("NSTUBR", 1, 3), ("NDOWL", 2, 3), ("NDOWR", 2, 3)]
    b321 = [("NA", 1, 3), ("NB", 2, 3), ("NC", 3, 3)]
    C = []
    # LC1 belly landing 10 g
    ld, gr = inertia(m, S, (0, 0, -10))
    C.append(dict(name="LC1a", desc="belly landing 10 g, both skids", loads=ld, grav=gr,
                  bc=[("NSKIDF", 3, 3), ("NSKIDR", 3, 3), ("NSKX", 1, 2), ("NSKY", 2, 2)], rf=["NSKIDF", "NSKIDR"]))
    rb = rigid_body(ctx)
    for nm, patch, desc in (("LC1b", "skidF", "front skid first"), ("LC1c", "skidR", "rear skid first")):
        w = F.elem_geom(m)[1][S[patch]]
        xc = (ctx["cen"][S[patch], 0] * w).sum() / w.sum()
        meff = 1.0 / (1.0 / rb["M"] + ((xc - rb["cg"][0]) / 1000.0) ** 2 / rb["Iyy"])
        ld, inf = relief(m, ctx, S, rb, (0, 0, 10 * KG * meff), patch)
        C.append(dict(name=nm, desc="belly landing, %s: 10 g at the contact, rigid pitch (m_eff %.2f kg)" % (desc, meff),
                      loads=ld, grav=None, bc=b321, rf=["NA", "NB", "NC"], info=inf))
    # LC2 nose-in: contact force on the front skid = M x (10 g aft-pointing friction, 5 g up), rigid pitch
    ld, inf = relief(m, ctx, S, rb, (10 * KG * rb["M"], 0, 5 * KG * rb["M"]), "skidF")
    C.append(dict(name="LC2", desc="nose-in: front skid force M x (10 g, 0, 5 g), rigid pitch", loads=ld, grav=None,
                  bc=b321, rf=["NA", "NB", "NC"], info=inf))
    # LC3 hand launch: 5 g aft (+X) + 1 g down, palm fixed, finger squeeze 20 N each side (D-064; was 40 N)
    ld, gr = inertia(m, S, (5, 0, -1), wing_to="lips")
    sq = F.add_loads(F.patch_load(m, S["fingL"], (0, SQUEEZE_N, 0)), F.patch_load(m, S["fingR"], (0, -SQUEEZE_N, 0)))
    C.append(dict(name="LC3", desc="hand launch 5 g + 1 g, palm fixed, squeeze 2 x %.0f N" % SQUEEZE_N, loads=F.add_loads(ld, sq),
                  grav=gr, bc=[("NPALM", 1, 3)], rf=["NPALM"]))
    # LC4 motor: thrust 12 N forward, torque 0.3 N m about X, hatch off; wing supports
    th = F.patch_load(m, S["fw_c"], (-12.0, 0, 0))
    tq = F.couple_load(m, S["fw"], (FW_X, 0, -50), (0.3e3, 0, 0))
    C.append(dict(name="LC4", desc="motor thrust 12 N + torque 0.3 N m, hatch off", loads=F.add_loads(th, tq),
                  grav=None, bc=wing_bc, rf=["NSTUBL", "NSTUBR", "NDOWL", "NDOWR"]))
    # LC5 band preload 50 N: stubs 2 x 12.5 N up (20 % inboard), dowel 2 x 12.5 N up; wing on the lips near the bands
    L5 = [F.patch_load(m, S["stubL"], (0, 2.5, 12.5)), F.patch_load(m, S["stubR"], (0, -2.5, 12.5)),
          F.patch_load(m, S["dowL"], (0, 2.5, 12.5)), F.patch_load(m, S["dowR"], (0, -2.5, 12.5)),
          F.patch_load(m, S["lip_f"], (0, 0, -25.0)), F.patch_load(m, S["lip_r"], (0, 0, -25.0))]
    C.append(dict(name="LC5", desc="band preload 50 N, self-balanced", loads=F.add_loads(*L5), grav=None, bc=b321,
                  rf=["NA", "NB", "NC"]))
    # LC6 flight 3 g: pod hangs from the wing (stubs + dowel), wing inertia not on the pod
    ld, gr = inertia(m, S, (0, 0, -3), wing=False)
    C.append(dict(name="LC6", desc="flight 3 g, pod hangs from the band stubs and dowel", loads=ld, grav=gr,
                  bc=wing_bc, rf=["NSTUBL", "NSTUBR", "NDOWL", "NDOWR"]))
    # LC7 tail: a vertical 7.5 N m at X 300 (19.7 N at X 680); b lateral 9 N at the fin + 0.72 N m torsion;
    # c asymmetric stab 0.9 N m torsion
    C.append(dict(name="LC7a", desc="tail vertical 19.7 N at X 680 (7.5 N m at the socket exit)",
                  loads=tail_loads(m, S, (0, 0, -19.7), 680.0), grav=None, bc=wing_bc, rf=["NSTUBL", "NSTUBR", "NDOWL", "NDOWR"]))
    fz = 0.72 / (2 * TUBE_Y / 1000.0)
    C.append(dict(name="LC7b", desc="tail lateral 9 N at the fin (X 690, Z +40) + 0.72 N m torsion",
                  loads=tail_loads(m, S, None, 690.0, per_tube=((0, 4.5, -fz), (0, 4.5, fz))), grav=None, bc=wing_bc,
                  rf=["NSTUBL", "NSTUBR", "NDOWL", "NDOWR"]))
    fz = 0.9 / (2 * TUBE_Y / 1000.0)
    C.append(dict(name="LC7c", desc="asymmetric stab 0.9 N m torsion", loads=tail_loads(m, S, None, 680.0,
                  per_tube=((0, 0, -fz), (0, 0, fz))), grav=None, bc=wing_bc, rf=["NSTUBL", "NSTUBR", "NDOWL", "NDOWR"]))
    for c in C:
        c["buckle"] = True
    for c in C:
        c.setdefault("info", {})
    C[0]["info"]["rigid_body"] = dict(M=rb["M"], cg=rb["cg"].round(1).tolist(), Iyy=rb["Iyy"], m_struct=rb["m_struct"])
    return C, ns, S


def thumb_cases(m, ctx, points):
    """LC8: 10 N on a D15 patch normal to the skin at each point (X, side, Z or 'floor'); wing supports."""
    X, Y, Z = ctx["cen"].T
    out = []
    for nm, (x, ysgn, z) in points.items():
        if z == "floor":
            msk = (np.hypot(X - x, Y - ysgn) < 7.5) & (ctx["nrm"][:, 2] < -0.9) & np.isin(ctx["zone"], ["floor"])
            f = (0, 0, 10.0)
        elif z == "lip":
            msk = (ctx["tag"] == "lip") & (np.abs(X - x) < 7.5) & (np.sign(Y) == ysgn)
            f = (0, 0, -10.0)
        else:
            msk = (np.hypot(X - x, Z - z) < 7.5) & (np.sign(Y) == ysgn) & (np.abs(np.abs(Y) - ctx["W"]) < 1.5) & (ctx["tag"] != "lip")
            f = (0, -10.0 * ysgn, 0)
        if not msk.any():
            continue
        out.append(dict(name="LC8_" + nm, desc="thumb 10 N at %s" % nm, loads=F.patch_load(m, msk, f), grav=None,
                        bc=[("NSTUBL", 1, 3), ("NSTUBR", 1, 3), ("NDOWL", 2, 3), ("NDOWR", 2, 3)], rf=[], buckle=False,
                        patch=msk))
    return out
