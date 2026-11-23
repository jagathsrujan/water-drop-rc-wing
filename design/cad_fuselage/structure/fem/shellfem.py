"""Shell FEM helpers for the pod structure study (stage F-S).

gmsh (second-order shells on a BREP of faces, conformal by `Coherence`) -> CalculiX deck (S8R quadrilaterals,
S6 triangles only where gmsh leaves them; thickness by element group) -> run ccx -> read the .frd (expanded 3D
results mapped back to the 2D nodes) and the .dat (buckling factors, reaction totals).
Smoke test (smoke_plate.py): S6 gives buckling factors 2.3-2.8 x too high at any mesh size -> use all-quad S8R.
Pure Python + numpy; no FreeCAD needed here.
Units: N, mm, tonne, s (density t/mm3 = g/cm3 * 1e-9; acceleration mm/s2; stress MPa).
"""
import os
import re
import subprocess
import numpy as np

CCX = "/Applications/FreeCAD.app/Contents/Resources/bin/ccx"
GMSH = "/Applications/FreeCAD.app/Contents/Resources/bin/gmsh"
G = 9810.0  # mm/s2

# expansion of the 2D shell node j into the nodes of the 3D element that ccx writes to the .frd (0-based)
# C3D15 (from S6): 1-3 bottom corners, 4-6 top corners, 7-9 bottom mids, 10-12 mid-surface, 13-15 top mids
# C3D20R (from S8R): 1-4 bottom corners, 5-8 top corners, 9-12 bottom mids, 13-16 mid-surface, 17-20 top mids
# (frd order, checked in the smoke test: after the bottom mids come the mid-surface nodes, then the top mids)
EXP = {6: {0: (0, 3, 9), 1: (1, 4, 10), 2: (2, 5, 11), 3: (6, 12), 4: (7, 13), 5: (8, 14)},
       8: {0: (0, 4, 12), 1: (1, 5, 13), 2: (2, 6, 14), 3: (3, 7, 15), 4: (8, 16), 5: (9, 17), 6: (10, 18), 7: (11, 19)}}
EDGES = {6: ((0, 3, 1), (1, 4, 2), (2, 5, 0)), 8: ((0, 4, 1), (1, 5, 2), (2, 6, 3), (3, 7, 0))}
CTYPE = {6: "S6", 8: "S8R"}

QUAD_OPTS = ("Mesh.RecombineAll = 1;\nMesh.Algorithm = 8;\nMesh.RecombinationAlgorithm = 1;\n"
             "Mesh.SecondOrderIncomplete = 1;\n")
QUAD_SUBDIV = "Mesh.SubdivisionAlgorithm = 1;\n"   # all-quad, but poor quads at curved T-joints (pod model)


# ------------------------------------------------------------------ mesh
def mesh(brep, workdir, name, hmax, hmin=None, extra="", quad=True, subdiv=False, timeout=1800):
    """Mesh all faces of a BREP with gmsh (OCC kernel, Coherence = boolean fragments -> conformal mesh).
    quad=True: all-quad by subdivision (final element size about hmax/2), 8-node serendipity quads.
    Returns dict(nodes {id: (x,y,z)}, elems (ne, 8) int (tri6 padded with 0), nn (ne,) 6 or 8, eid (ne,))."""
    os.makedirs(workdir, exist_ok=True)
    geo = os.path.join(workdir, name + ".geo")
    msh = os.path.join(workdir, name + ".msh")
    with open(geo, "w") as f:
        f.write('SetFactory("OpenCASCADE");\nGeometry.Tolerance = 1e-4;\nGeometry.ToleranceBoolean = 1e-3;\n')
        f.write('Merge "%s";\n' % brep)
        f.write("Coherence;\n")
        f.write("Mesh.CharacteristicLengthMax = %g;\n" % hmax)
        f.write("Mesh.CharacteristicLengthMin = %g;\n" % (hmin or max(hmax / 2.0, 1.5)))
        f.write("Mesh.CharacteristicLengthFromCurvature = 1;\nMesh.MinimumElementsPerTwoPi = 12;\n")
        f.write("Mesh.ElementOrder = 2;\nMesh.Algorithm = 6;\nMesh.MshFileVersion = 2.2;\n")
        if quad:
            f.write(QUAD_OPTS + (QUAD_SUBDIV if subdiv else ""))
        f.write(extra + "\n")
        f.write('Mesh 2;\nSave "%s";\n' % msh)
    r = subprocess.run([GMSH, geo, "-0", "-nopopup"], cwd=workdir, capture_output=True, text=True, timeout=timeout)
    open(os.path.join(workdir, name + ".gmsh.log"), "w").write(r.stdout + r.stderr)
    if not os.path.exists(msh):
        raise RuntimeError("gmsh failed:\n" + r.stdout[-3000:] + r.stderr[-3000:])
    return read_msh(msh)


def read_msh(path):
    lines = open(path).read().split("\n")
    i = lines.index("$Nodes")
    n = int(lines[i + 1])
    nodes = {}
    for k in range(i + 2, i + 2 + n):
        s = lines[k].split()
        nodes[int(s[0])] = (float(s[1]), float(s[2]), float(s[3]))
    i = lines.index("$Elements")
    n = int(lines[i + 1])
    el, nn = [], []
    for k in range(i + 2, i + 2 + n):
        s = lines[k].split()
        t = int(s[1])
        nt = int(s[2])
        if t == 9:        # 6-node triangle
            el.append([int(v) for v in s[3 + nt:3 + nt + 6]] + [0, 0])
            nn.append(6)
        elif t == 16:     # 8-node quadrangle
            el.append([int(v) for v in s[3 + nt:3 + nt + 8]])
            nn.append(8)
        elif t in (2, 3, 10):
            raise RuntimeError("first-order or 9-node element type %d in the mesh" % t)
    el = np.array(el, dtype=int)
    nn = np.array(nn, dtype=int)
    used = np.unique(el[el > 0])
    nodes = {k: nodes[k] for k in used}
    return dict(nodes=nodes, elems=el, nn=nn, eid=np.arange(1, len(el) + 1))


def submesh(m, emask):
    """Mesh with only the elements in emask (keeps node and element numbers)."""
    el = m["elems"][emask]
    used = np.unique(el[el > 0])
    return dict(nodes={k: m["nodes"][k] for k in used}, elems=el, nn=m["nn"][emask], eid=m["eid"][emask])


# ------------------------------------------------------------------ geometry of the mesh
def node_array(m):
    ids = np.array(sorted(m["nodes"]))
    xyz = np.array([m["nodes"][k] for k in ids])
    return ids, xyz


def elem_geom(m):
    """Centroid (of the corners), area (flat corner polygon), unit normal of each element."""
    ids, xyz = node_array(m)
    pos = np.zeros(ids.max() + 1, dtype=int)
    pos[ids] = np.arange(len(ids))
    e = m["elems"]
    P = [xyz[pos[e[:, j]]] for j in range(4)]
    q = m["nn"] == 8
    d = np.where(q[:, None], P[3], P[2])           # 4th corner (= 3rd for triangles)
    n1 = np.cross(P[1] - P[0], P[2] - P[0])
    n2 = np.cross(P[2] - P[0], d - P[0])
    n = n1 + np.where(q[:, None], n2, 0.0)
    ar = 0.5 * np.linalg.norm(n, axis=1)
    cen = np.where(q[:, None], (P[0] + P[1] + P[2] + P[3]) / 4.0, (P[0] + P[1] + P[2]) / 3.0)
    return cen, ar, n / np.maximum(2 * ar[:, None], 1e-30)


# ------------------------------------------------------------------ loads
def patch_load(m, emask, total):
    """Consistent nodal forces for a uniform traction over the elements in emask, total force vector.
    tri6: corners 0, mids A/3. quad8: corners -A/12, mids A/3. Returns {node: np.array(3)}."""
    _, ar, _ = elem_geom(m)
    A = ar[emask].sum()
    if A <= 0:
        raise ValueError("empty load patch")
    q = np.asarray(total, float) / A
    out = {}
    for e, a, k in zip(m["elems"][emask], ar[emask], m["nn"][emask]):
        if k == 6:
            w = [(e[j], a / 3.0) for j in (3, 4, 5)]
        else:
            w = [(e[j], -a / 12.0) for j in (0, 1, 2, 3)] + [(e[j], a / 3.0) for j in (4, 5, 6, 7)]
        for nd, ww in w:
            out[nd] = out.get(nd, np.zeros(3)) + q * ww
    return out


def edge_load(m, on_line, total):
    """Consistent nodal forces for a uniform line load along element edges whose 3 nodes satisfy on_line(xyz).
    Quadratic edge: ends 1/6, mid 4/6 of q*L."""
    nd = m["nodes"]
    edges, seen = [], set()
    for e, k in zip(m["elems"], m["nn"]):
        for (i, j, l) in EDGES[k]:
            key = tuple(sorted((e[i], e[l]))) + (e[j],)
            if key in seen:
                continue
            if on_line(nd[e[i]]) and on_line(nd[e[j]]) and on_line(nd[e[l]]):
                seen.add(key)
                edges.append((e[i], e[j], e[l], np.linalg.norm(np.subtract(nd[e[l]], nd[e[i]]))))
    Lt = sum(x[3] for x in edges)
    if Lt <= 0:
        raise ValueError("no edge on the line")
    q = np.asarray(total, float) / Lt
    out = {}
    for a, mid, b, L in edges:
        for n_, w in ((a, 1 / 6.0), (mid, 4 / 6.0), (b, 1 / 6.0)):
            out[n_] = out.get(n_, np.zeros(3)) + q * L * w
    return out


def couple_load(m, emask, about, moment):
    """Nodal forces on the nodes of the elements in emask that give the moment vector `moment` about `about` and
    zero net force: rigid-rotation field f_i = (M x r_i) / J, r_i from the patch centroid, area weighted."""
    w = patch_load(m, emask, (1.0, 0, 0))          # x-component = area weight of each node (sums to 1)
    ids = list(w)
    wt = np.array([w[k][0] for k in ids])
    r = np.array([m["nodes"][k] for k in ids])
    c = (wt[:, None] * r).sum(axis=0) / wt.sum()
    r = r - c
    M = np.asarray(moment, float)
    Mh = M / max(np.linalg.norm(M), 1e-30)
    J = np.sum(wt * (np.sum(r * r, axis=1) - (r @ Mh) ** 2))
    f = wt[:, None] * np.cross(M, r) / J
    return {k: f[i] for i, k in enumerate(ids)}


def add_loads(*dicts):
    out = {}
    for d in dicts:
        for k, v in d.items():
            out[k] = out.get(k, np.zeros(3)) + np.asarray(v, float)
    return out


def scale_loads(d, s):
    return {k: np.asarray(v) * s for k, v in d.items()}


def resultant(m, loads, about=(0, 0, 0)):
    F = np.zeros(3)
    Mo = np.zeros(3)
    for k, v in loads.items():
        F += v
        Mo += np.cross(np.subtract(m["nodes"][k], about), v)
    return F, Mo


# ------------------------------------------------------------------ deck
def _wr_ids(f, ids):
    ids = list(ids)
    for i in range(0, len(ids), 12):
        f.write(", ".join(str(int(v)) for v in ids[i:i + 12]) + ",\n")


def write_deck(path, m, groups, materials, steps, nsets=None):
    """groups: list of (name, elem_index_array, thickness, material_name).
    materials: {name: (E, nu, rho_t_per_mm3)}.
    steps: list of dict(kind='static'|'buckle', nmodes, bc=[(nset, dof_a, dof_b)], loads={node: vec},
           grav=(acc_mm_s2, (dx,dy,dz)) or None)."""
    with open(path, "w") as f:
        f.write("*HEADING\npod structure study shell model\n*NODE, NSET=NALL\n")
        for k in sorted(m["nodes"]):
            x, y, z = m["nodes"][k]
            f.write("%d, %.6f, %.6f, %.6f\n" % (k, x, y, z))
        live = []
        for name, idx, t, mat in groups:
            idx = np.asarray(idx, dtype=int)
            if len(idx) == 0:
                continue
            live.append((name, t, mat))
            subs = []
            for k in (8, 6):
                sel = idx[m["nn"][idx] == k]
                if len(sel) == 0:
                    continue
                sub = "%s_%d" % (name, k)
                subs.append(sub)
                f.write("*ELEMENT, TYPE=%s, ELSET=%s\n" % (CTYPE[k], sub))
                for i in sel:
                    e = m["elems"][i][:k]
                    f.write("%d, %s\n" % (m["eid"][i], ", ".join(str(int(v)) for v in e)))
            f.write("*ELSET, ELSET=%s\n%s,\n" % (name, ", ".join(subs)))
        f.write("*ELSET, ELSET=EALL\n")
        names = [g[0] for g in live]
        for i in range(0, len(names), 8):
            f.write(", ".join(names[i:i + 8]) + ",\n")
        for name, (E, nu, rho) in materials.items():
            f.write("*MATERIAL, NAME=%s\n*ELASTIC\n%g, %g\n*DENSITY\n%g\n" % (name, E, nu, rho))
        for name, t, mat in live:
            f.write("*SHELL SECTION, ELSET=%s, MATERIAL=%s\n%g\n" % (name, mat, t))
        for name, ids in (nsets or {}).items():
            f.write("*NSET, NSET=%s\n" % name)
            _wr_ids(f, ids)
        for st in steps:
            f.write("*STEP\n")
            if st["kind"] == "static":
                f.write("*STATIC\n*BOUNDARY, OP=NEW\n")
            else:
                f.write("*BUCKLE\n%d, 0.001\n*BOUNDARY\n" % st.get("nmodes", 6))
            for ns, a, b in st["bc"]:
                f.write("%s, %d, %d\n" % (ns, a, b))
            f.write("*CLOAD, OP=NEW\n" if st["kind"] == "static" else "*CLOAD\n")
            for k, v in st.get("loads", {}).items():
                for d in range(3):
                    if abs(v[d]) > 1e-12:
                        f.write("%d, %d, %.8g\n" % (k, d + 1, v[d]))
            if st.get("grav"):
                acc, dvec = st["grav"]
                f.write("*DLOAD, OP=NEW\n" if st["kind"] == "static" else "*DLOAD\n")
                f.write("EALL, GRAV, %g, %g, %g, %g\n" % (acc, dvec[0], dvec[1], dvec[2]))
            elif st["kind"] == "static":
                f.write("*DLOAD, OP=NEW\n")
            f.write("*NODE FILE, OUTPUT=3D\nU\n")
            if st["kind"] == "static":
                f.write("*EL FILE, OUTPUT=3D\nS, ENER\n")
                for ns in st.get("rf_sets", []):
                    f.write("*NODE PRINT, NSET=%s, TOTALS=ONLY\nRF\n" % ns)
            f.write("*END STEP\n")


def run_ccx(workdir, job, threads=2, timeout=3600):
    env = dict(os.environ, OMP_NUM_THREADS=str(threads), CCX_NPROC_EQUATION_SOLVER=str(threads))
    r = subprocess.run([CCX, "-i", job], cwd=workdir, capture_output=True, text=True, timeout=timeout, env=env)
    log = r.stdout + r.stderr
    open(os.path.join(workdir, job + ".log"), "w").write(log)
    if "*ERROR" in log or r.returncode != 0 or not os.path.exists(os.path.join(workdir, job + ".frd")):
        raise RuntimeError("ccx failed (%s): %s" % (job, log[-2500:]))
    return log


# ------------------------------------------------------------------ results
def read_frd(path):
    """Returns dict(coords {nid: xyz}, elems {eid: [nodes]}, blocks [dict(step, name, ids, vals)])."""
    coords, elems, blocks = {}, {}, []
    with open(path) as f:
        lines = f.read().split("\n")
    i, n = 0, len(lines)
    while i < n:
        L = lines[i]
        if L.startswith("    2C"):
            i += 1
            while not lines[i].startswith(" -3"):
                s = lines[i]
                coords[int(s[3:13])] = (float(s[13:25]), float(s[25:37]), float(s[37:49]))
                i += 1
        elif L.startswith("    3C"):
            i += 1
            cur = None
            while not lines[i].startswith(" -3"):
                s = lines[i]
                if s.startswith(" -1"):
                    cur = int(s[3:13])
                    elems[cur] = []
                elif s.startswith(" -2"):
                    elems[cur] += [int(s[k:k + 10]) for k in range(3, len(s.rstrip()), 10)]
                i += 1
        elif L.startswith("  100C"):
            stepno = len([b for b in blocks if b["name"].startswith("DISP")]) + (1 if "DISP" not in lines[i + 1] else 1)
            i += 1
            hdr = lines[i].split()
            name = hdr[1]
            ncomp = int(hdr[2])
            i += 1
            while lines[i].startswith(" -5"):
                i += 1
            ids, vals = [], []
            while not lines[i].startswith(" -3"):
                s = lines[i]
                if s.startswith(" -1"):
                    ids.append(int(s[3:13]))
                    nv = max(0, (len(s.rstrip()) - 13) // 12)
                    vals.append([float(s[13 + 12 * k:25 + 12 * k]) for k in range(min(ncomp, 6, nv))])
                elif s.startswith(" -2"):
                    nv = max(0, (len(s.rstrip()) - 13) // 12)
                    vals[-1] += [float(s[13 + 12 * k:25 + 12 * k]) for k in range(nv)]
                i += 1
            nc = min(len(v) for v in vals) if vals else 0
            blocks.append(dict(name=name, ids=np.array(ids), vals=np.array([v[:nc] for v in vals])))
        i += 1
    # number the result sets: each DISP block opens a new set
    k = 0
    for b in blocks:
        if b["name"].startswith("DISP"):
            k += 1
        b["set"] = k
    return dict(coords=coords, elems=elems, blocks=blocks)


def read_buckle(datpath):
    txt = open(datpath).read()
    out = []
    for blk in re.split(r"B U C K L I N G   F A C T O R   O U T P U T", txt)[1:]:
        fac = []
        for line in blk.split("\n")[1:]:
            s = line.split()
            if len(s) == 2 and s[0].isdigit():
                fac.append(float(s[1]))
            elif fac and s:
                break
        out.append(fac)
    return out


def read_rf(datpath):
    """Total reaction forces (fx, fy, fz) of each NODE PRINT TOTALS=ONLY block, in order."""
    txt = open(datpath).read()
    out = []
    for m_ in re.finditer(r"total force \(fx,fy,fz\) for set (\S+) and time\s+\S+\s*\n\s*\n?\s*([-\d.E+ ]+)", txt):
        out.append((m_.group(1), [float(v) for v in m_.group(2).split()[:3]]))
    return out


def vm_principal(S):
    """S: (n,6) sxx syy szz sxy syz szx -> von Mises, max principal, min principal."""
    S = np.atleast_2d(S)
    sxx, syy, szz, sxy, syz, szx = S.T
    vm = np.sqrt(0.5 * ((sxx - syy) ** 2 + (syy - szz) ** 2 + (szz - sxx) ** 2) + 3 * (sxy ** 2 + syz ** 2 + szx ** 2))
    T = np.zeros((len(S), 3, 3))
    T[:, 0, 0], T[:, 1, 1], T[:, 2, 2] = sxx, syy, szz
    T[:, 0, 1] = T[:, 1, 0] = sxy
    T[:, 1, 2] = T[:, 2, 1] = syz
    T[:, 0, 2] = T[:, 2, 0] = szx
    ev = np.linalg.eigvalsh(T)
    return vm, ev[:, 2], ev[:, 0]


def map_to_2d(m, frd, block):
    """Map an expanded-node result block back to the 2D mesh.
    Returns per_node {nid: array (k, ncomp)} and per_elem {elem index: array (k, ncomp)} of the values at all
    expanded nodes (top, bottom and mid surfaces)."""
    val = dict(zip(block["ids"].tolist(), block["vals"]))
    per_elem, per_node = {}, {}
    for i, eid in enumerate(m["eid"]):
        ex = frd["elems"].get(int(eid))
        if ex is None:
            continue
        k = m["nn"][i]
        rows = []
        for j in range(k):
            nd = int(m["elems"][i][j])
            for p in EXP[k][j]:
                v = val.get(ex[p])
                if v is not None:
                    rows.append(v)
                    per_node.setdefault(nd, []).append(v)
        per_elem[i] = np.array(rows)
    return {k: np.array(v) for k, v in per_node.items()}, per_elem


def disp_2d(m, frd, block):
    """Displacement of each 2D node = mean of its expanded nodes (mid-surface)."""
    pn, _ = map_to_2d(m, frd, block)
    return {k: v.mean(axis=0) for k, v in pn.items()}


def elem_stress(m, frd, block):
    """Per element: max von Mises, max principal and min principal over all its expanded nodes."""
    _, pe = map_to_2d(m, frd, block)
    ne = len(m["elems"])
    vm, p1, p3 = np.zeros(ne), np.zeros(ne), np.zeros(ne)
    for i, arr in pe.items():
        a, b, c = vm_principal(arr)
        vm[i], p1[i], p3[i] = a.max(), b.max(), c.min()
    return vm, p1, p3


# ------------------------------------------------------------------ buckling with a load-scale sweep
# Smoke test result: this ccx build (2.23, SPOOLES/ARPACK) returns the buckling factors nearest to 1.0 (shift 1).
# A factor below about 0.5 is not found (cantilever column at 2.0 N: mode 1 at 0.2 missing). Remedy: run the
# buckling step with the reference load scaled by s (each s at most 2 x the previous) and take the lowest
# factor * s over all runs (factor in units of the unscaled load).
BUCKLE_SCALES = (0.03, 0.06, 0.12, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0)


def buckle_sweep(workdir, job, m, groups, materials, bc, loads, nsets, grav=None, scales=BUCKLE_SCALES,
                 nmodes=6, threads=1, parallel=4):
    """Returns (lambda_min, all factors [(lambda * s, s)] sorted). lambda is relative to the given loads."""
    import concurrent.futures as cf
    jobs = []
    for s in scales:
        name = "%s_b%03d" % (job, int(round(s * 100)))
        st = dict(kind="buckle", nmodes=nmodes, bc=bc, loads=scale_loads(loads, s),
                  grav=(grav[0] * s, grav[1]) if grav else None)
        write_deck(os.path.join(workdir, name + ".inp"), m, groups, materials, [st], nsets=nsets)
        jobs.append((name, s))

    def one(js):
        name, s = js
        try:
            run_ccx(workdir, name, threads=threads)
            f = read_buckle(os.path.join(workdir, name + ".dat"))
            return [(v * s, s) for v in (f[0] if f else []) if v > 0]
        except Exception as e:                       # noqa: BLE001
            return [("ERR", str(e)[:200])]
    res = []
    with cf.ThreadPoolExecutor(max_workers=parallel) as ex:
        for r in ex.map(one, jobs):
            res += r
    good = sorted([r for r in res if r[0] != "ERR"])
    if not good:
        raise RuntimeError("buckling sweep failed: %s" % res[:3])
    return good[0][0], good
