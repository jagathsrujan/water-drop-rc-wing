"""Smoke test of the shell FEM chain (gmsh -> ccx -> frd/dat reader), S8R (all-quad) and S6.
1. Simply supported plate 200 x 100 x 1, uniaxial compression, self-balanced edge loads, point supports:
   buckling factor against k = 4 (a/b = 2).
2. Cantilever strip 100 x 20 x 1, clamped, tip line load 1 N: root bending stress against 6PL/(b t^2),
   tip deflection against beam / plate theory, reaction total against the applied load.
Run: /Applications/FreeCAD.app/Contents/Resources/bin/python smoke_plate.py <workdir>"""
import sys, os, math
sys.path.append("/Applications/FreeCAD.app/Contents/Resources/lib")
import FreeCAD, Part
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import shellfem as F

W = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "_smoke")
os.makedirs(W, exist_ok=True)
E, NU, T = 1000.0, 0.35, 1.0
mats = {"M": (E, NU, 1e-9)}
out = []

# ---------- 1. buckling
a, b = 200.0, 100.0
Part.makePlane(a, b).exportBrep(os.path.join(W, "plate.brep"))
D = E * T ** 3 / (12 * (1 - NU ** 2))
lam_th = 4 * math.pi ** 2 * D / (b ** 2 * T) * b * T / 100.0
out.append("plate buckling theory (k = 4, P 100 N): factor %.4f" % lam_th)
for quad, h in ((True, 10.0), (True, 5.0), (False, 5.0)):
    m = F.mesh(os.path.join(W, "plate.brep"), W, "plate", h, quad=quad, subdiv=True)
    ids, xyz = F.node_array(m)
    near = lambda x, y: ids[np.argmin((xyz[:, 0] - x) ** 2 + (xyz[:, 1] - y) ** 2)]
    edge = [k for k, p in zip(ids, xyz) if p[0] < 1e-6 or p[0] > a - 1e-6 or p[1] < 1e-6 or p[1] > b - 1e-6]
    loads = F.add_loads(F.edge_load(m, lambda p: p[0] > a - 1e-6, (-100, 0, 0)), F.edge_load(m, lambda p: p[0] < 1e-6, (100, 0, 0)))
    bc = [("NEDGE", 3, 3), ("NA", 1, 2), ("NB", 2, 2)]       # w = 0 on the edges; in-plane rigid-body supports only
    lmin, allf = F.buckle_sweep(W, "pb", m, [("G", np.arange(len(m["elems"])), T, "M")], mats, bc, loads,
                                dict(NEDGE=edge, NA=[near(0, b / 2)], NB=[near(a, b / 2)]), nmodes=4)
    out.append("  %s h %.1f (%d elems): sweep lowest factor %.4f ; ratio to theory %.4f ; next %s"
               % ("S8R" if quad else "S6 ", h, len(m["elems"]), lmin, lmin / lam_th, [round(v[0], 4) for v in allf[1:4]]))
# Euler column check (clamped strip 100 x 20 x 1, axial tip load 1 N)
L, bw = 100.0, 20.0
Part.makePlane(L, bw).exportBrep(os.path.join(W, "strip.brep"))
m = F.mesh(os.path.join(W, "strip.brep"), W, "strip", 5.0, quad=True, subdiv=True)
ids, xyz = F.node_array(m)
root = [k for k, p in zip(ids, xyz) if p[0] < 1e-6]
lmin, allf = F.buckle_sweep(W, "eb", m, [("G", np.arange(len(m["elems"])), T, "M")], mats, [("NROOT", 1, 6)],
                            F.edge_load(m, lambda p: p[0] > L - 1e-6, (-1.0, 0, 0)), dict(NROOT=root), nmodes=3)
I = bw * T ** 3 / 12
out.append("Euler column S8R: sweep lowest %.4f ; theory beam %.4f, plate strip %.4f" % (lmin, math.pi ** 2 * E * I / (4 * L ** 2), math.pi ** 2 * E * I / (4 * L ** 2) / (1 - NU ** 2)))

# ---------- 2. bending
L, bw = 100.0, 20.0
Part.makePlane(L, bw).exportBrep(os.path.join(W, "strip.brep"))
for quad, h in ((True, 5.0), (False, 2.5)):
    m = F.mesh(os.path.join(W, "strip.brep"), W, "strip", h, quad=quad, subdiv=True)
    ids, xyz = F.node_array(m)
    root = [k for k, p in zip(ids, xyz) if p[0] < 1e-6]
    loads = F.edge_load(m, lambda p: p[0] > L - 1e-6, (0, 0, -1.0))
    steps = [dict(kind="static", bc=[("NROOT", 1, 6)], loads=loads, rf_sets=["NROOT"])]
    F.write_deck(os.path.join(W, "cb.inp"), m, [("G", np.arange(len(m["elems"])), T, "M")], mats, steps, nsets=dict(NROOT=root))
    F.run_ccx(W, "cb")
    frd = F.read_frd(os.path.join(W, "cb.frd"))
    sb = [blk for blk in frd["blocks"] if blk["name"].startswith("STRESS")][0]
    db = [blk for blk in frd["blocks"] if blk["name"].startswith("DISP")][0]
    pn, pe = F.map_to_2d(m, frd, sb)
    ex = frd["elems"][int(m["eid"][0])]
    k0 = m["nn"][0]
    dmax = max(np.linalg.norm(np.subtract(frd["coords"][ex[p]], m["nodes"][m["elems"][0][j]])) for j in range(k0) for p in F.EXP[k0][j])
    sx_mid = [np.max(np.abs(pn[k][:, 0])) for k, p in zip(ids, xyz) if abs(p[0] - L / 2) < 1.3 and abs(p[1] - bw / 2) < 5]
    sx_root = [np.max(np.abs(pn[k][:, 0])) for k, p in zip(ids, xyz) if p[0] < 1e-6 and abs(p[1] - bw / 2) < 5]
    d2 = F.disp_2d(m, frd, db)
    tip = np.mean([d2[k][2] for k, p in zip(ids, xyz) if p[0] > L - 1e-6])
    dth = L ** 3 / (3 * E * bw * T ** 3 / 12)
    rf = F.read_rf(os.path.join(W, "cb.dat"))
    out.append("bending %s: frd elem nodes %d, mapping distance max %.3f (t/2 %.2f)" % ("S8R" if quad else "S6 ", len(ex), dmax, T / 2))
    out.append("  sxx at X 50 (mid-width) %.2f MPa, theory 6P(L/2)/bt^2 = %.2f ; at the root %.2f, theory %.2f"
               % (max(sx_mid), 6 * (L / 2) / (bw * T ** 2), max(sx_root), 6 * L / (bw * T ** 2)))
    out.append("  tip deflection %.2f mm ; beam %.2f ; plate (1-nu^2) %.2f ; reaction %s" % (-tip, dth, dth * (1 - NU ** 2), rf))
print("\n".join(out))
open(os.path.join(HERE, "smoke_result.txt"), "w").write("\n".join(out) + "\n")
