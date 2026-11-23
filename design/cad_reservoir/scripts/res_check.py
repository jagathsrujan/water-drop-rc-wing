"""Stage R-A / R-B checks. Run inside FreeCAD: res_check.run_stage_ab(). Writes check_report_stageAB.txt and mass_table_stageAB.csv."""
import os, sys, math, json, random, importlib, itertools
import res_params as P, res_build as B
import Part
from FreeCAD import Vector as V

OUTDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "__file__" in globals() else None
LINES = []


def out(s=""):
    print(s)
    LINES.append(s)


def enclosing_circle(pts):
    """Smallest enclosing circle of 2D points (Welzl, iterative). Returns (cx, cy, r)."""
    pts = list(pts)
    random.Random(1).shuffle(pts)

    def circ2(a, b):
        cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        return cx, cy, math.hypot(a[0] - cx, a[1] - cy)

    def circ3(a, b, c):
        ax, ay = a; bx, by = b; cx_, cy_ = c
        d = 2 * (ax * (by - cy_) + bx * (cy_ - ay) + cx_ * (ay - by))
        if abs(d) < 1e-12:
            return None
        ux = ((ax**2 + ay**2) * (by - cy_) + (bx**2 + by**2) * (cy_ - ay) + (cx_**2 + cy_**2) * (ay - by)) / d
        uy = ((ax**2 + ay**2) * (cx_ - bx) + (bx**2 + by**2) * (ax - cx_) + (cx_**2 + cy_**2) * (bx - ax)) / d
        return ux, uy, math.hypot(ax - ux, ay - uy)

    def inside(c, p):
        return c is not None and math.hypot(p[0] - c[0], p[1] - c[1]) <= c[2] + 1e-9
    c = None
    for i, p in enumerate(pts):
        if c is None or not inside(c, p):
            c = (p[0], p[1], 0.0)
            for j in range(i):
                q = pts[j]
                if not inside(c, q):
                    c = circ2(p, q)
                    for k in range(j):
                        r = pts[k]
                        if not inside(c, r):
                            c3 = circ3(p, q, r)
                            if c3:
                                c = c3
    return c


def com_x(s):
    return B.com(s).x


def load_a():
    f = os.path.join(OUTDIR, "result_stageA.json")
    return json.load(open(f)) if os.path.exists(f) else {}


def shape(n):
    return B.doc().getObject(n).Shape


def run_stage_ab(full=False):
    LINES.clear()
    d = B.doc()
    A = load_a()
    out("RESERVOIR rev A - check report stage R-A / R-B")
    out("Bottle numbers are estimates (interp.) from res_params.py. Units mm, mm3, g.")
    out("")
    # ---------------- validity ----------------
    out("== 0. Solids ==")
    bad = []
    for o in d.Objects:
        if o.TypeId == "Part::Feature" and not o.Name.startswith("TMP_"):
            ok = o.Shape.isValid() and len(o.Shape.Solids) >= 1
            if not ok:
                bad.append(o.Name)
    out("isValid() all parts: %s %s" % ("PASS" if not bad else "FAIL", bad))
    # ---------------- bottle ----------------
    out("")
    out("== A. Bottle and water ==")
    pet = shape("P1_Bottle"); wat = shape("Water")
    out("Bottle base X (shifted so that the water centroid = %.0f): %.3f  (nominal %.1f, shift %.3f)"
        % (P.X_CG, A.get("base_x", float("nan")), P.BASE_X_NOMINAL, A.get("base_x", 0) - P.BASE_X_NOMINAL))
    out("Interior volume (open neck to the cap, with punt): %.1f mL   (brim estimate in the plan 1032 to 1040 mL, interp.)" % A.get("interior_ml", float("nan")))
    out("Water volume modelled (before flange cut): %.2f mL; after the P2 flange cut: %.2f mL; mass at 0.996 g/mL: %.1f g"
        % (A.get("water_ml", float("nan")), wat.Volume / 1000, wat.Volume / 1000 * 0.996))
    cx = A.get("water_cx", com_x(wat))
    out("Water centroid X (before flange cut): %.3f   target 80 +/- 1: %s ; after the flange cut: %.3f"
        % (cx, "PASS" if abs(cx - P.X_CG) <= P.X_CG_TOL else "FAIL", com_x(wat)))
    out("Water free surface Z = %.2f; air under the top inner wall (Z %.2f): %.2f mm deep"
        % (A.get("level_z", float("nan")), P.AXIS_Z + P.R_IN, P.AXIS_Z + P.R_IN - A.get("level_z", 0)))
    top = pet.BoundBox.ZMax
    lim = P.WING_UNDERSIDE_Z - P.BOTTLE_TOP_MARGIN
    out("Bottle top Z = %.2f; limit <= %.1f (5 mm under the wing underside -13): %s" % (top, lim, "PASS" if top <= lim + 1e-6 else "FAIL"))
    out("Bottle X range %.2f .. %.2f (neck lip), cap to %.2f; PET volume %.0f mm3 -> %.1f g at %.2f g/cm3 vs %.1f g given (interp.)"
        % (pet.BoundBox.XMin, pet.BoundBox.XMax, shape("P1c_Cap").BoundBox.XMax, pet.Volume, pet.Volume / 1000 * P.RHO_PET, P.RHO_PET, P.BOTTLE_MASS_G))
    # ---------------- key check 1 ----------------
    p2 = shape("P2_InnerFlange")
    out("")
    out("== Key check 1: insertion profile of P2 (end-on, long axis X, projected on the YZ plane) ==")
    verts, _ = p2.tessellate(0.01)
    pts = [(v.y, v.z) for v in verts]
    cx_, cy_, r = enclosing_circle(pts)
    nb = P.NECK_BORE_D
    out("smallest enclosing circle of the projection: diameter %.3f mm (centre y %.2f, z %.2f); limit <= %.1f (neck bore %.1f - 0.5): %s"
        % (2 * r, cx_, cy_, nb - 0.5, nb, "PASS" if 2 * r <= nb - 0.5 + 1e-6 else "FAIL"))
    out("clearance to the neck bore: %.2f mm on the diameter" % (nb - 2 * r))
    # ---------------- key check 2 ----------------
    out("")
    out("== Key check 2: flow passage from the flange top to the seat face ==")
    zs = [-98.9, -99.5, -100.5, -102.0, -104.0, -106.0, -106.9]
    dmin = 1e9; prev = None; mono = True
    for z in zs:
        ws = p2.slice(V(0, 0, 1), z)
        cand = [w for w in ws if w.isClosed()]
        if not cand:
            out("  Z %.1f: no section" % z); continue
        bore = min(cand, key=lambda w: w.Length)           # the bore wire has the smallest length
        dia = bore.Length / math.pi
        bb = bore.BoundBox
        out("  Z %7.1f: bore diameter %.3f (BB %.3f x %.3f)" % (z, dia, bb.XLength, bb.YLength))
        dmin = min(dmin, dia)
        if prev is not None and dia < prev - 1e-6:
            mono = False
        prev = dia
    out("  nut pocket D %.1f, plate hole D %.1f (outside the stem, not in the flow); flap seat D = bore at the stem end"
        % (P.POCKET_D, P.PL_HOLE_D))
    out("minimum passage diameter %.3f, limit >= 14.0: %s ; never smaller downstream: %s"
        % (dmin, "PASS" if dmin >= 14.0 - 1e-6 else "FAIL", "PASS" if mono else "FAIL"))
    out("stem end Z %.3f vs seat face %.3f: %s" % (p2.BoundBox.ZMin, P.SEAT_Z, "flush PASS" if abs(p2.BoundBox.ZMin - P.SEAT_Z) < 1e-6 else "FAIL"))
    # ---------------- key check 3 ----------------
    out("")
    out("== Key check 3: lip and residual water ==")
    rs = []
    for v in p2.Vertexes:
        r_ = math.hypot(v.Point.y - P.AXIS_Y, v.Point.z - P.AXIS_Z)
        if P.FL_TOP_R - 0.02 < r_ < P.R_IN - 0.05:
            rs.append(r_)
    heights = sorted(P.R_IN - r_ for r_ in rs)
    top_h = max(heights); rim_vals = [h for h in heights if h < top_h - 0.1]
    # underside check: flange underside radius on the vertices of the underside
    out("flange top above the inner wall (radial): %.3f mm (limit <= 1.2); vertex heights seen: %s" % (top_h, sorted(set(round(h, 2) for h in heights))))
    rim_h = max(rim_vals) if rim_vals else float("nan")
    out("flange rim above the inner wall: %.3f mm (limit <= 0.5): %s" % (rim_h, "PASS" if rim_h <= 0.5 + 1e-6 else "FAIL"))
    out("ramp: %.2f mm rise over %.1f mm = %.1f deg (limit <= 30): %s"
        % (top_h - rim_h, P.FL_RAMP_LEN, math.degrees(math.atan((top_h - rim_h) / P.FL_RAMP_LEN)),
           "PASS" if math.degrees(math.atan((top_h - rim_h) / P.FL_RAMP_LEN)) <= 30 else "FAIL"))
    import numpy as np
    sys.path.insert(0, os.path.join(os.path.dirname(OUTDIR), "calc"))
    import reservoir_cad_calc as C
    importlib.reload(C)
    pitches = [0, 1, 2, 3, 5]
    out("residual water (g) vs pitch, nose up, with the modelled lip top height %.2f mm:" % top_h)
    out("  calc defaults (profile as in the calc, wall radius 40.0): " + ", ".join("%d deg %.1f" % (p, C.residual_g(top_h, p)) for p in pitches))
    # same calc with the modelled geometry: inner radius = outer - wall, bottle base at the modelled X
    prof = P.BOTTLE_PROFILE
    def ri(yu):
        for a, b in zip(prof, prof[1:]):
            if yu <= b[0]:
                return a[1] + (b[1] - a[1]) * (yu - a[0]) / (b[0] - a[0]) - P.WALL
        return prof[-1][1] - P.WALL
    C.RS = np.array([ri(y) for y in C.YU])
    C.R_OUT = P.R_IN
    C.X_SLICE = A.get("base_x", P.BASE_X_NOMINAL) + C.YU
    res = {p: C.residual_g(top_h, p, x_out=P.OUT_X) for p in pitches}
    out("  modelled inner radii (wall radius %.1f, base X %.2f): " % (P.R_IN, A.get("base_x", 0)) + ", ".join("%d deg %.1f" % (p, res[p]) for p in pitches))
    ok = all(res[p] <= 10.0 for p in (0, 1, 2, 3))
    out("  limit <= 10 g at 0 to 3 deg: %s" % ("PASS" if ok else "FAIL"))
    # ---------------- key check 4 ----------------
    out("")
    out("== Key check 4: open state ==")
    o6 = shape("P6_Flap_open"); o7 = shape("P7_FlapGasket_open")
    tube = B.zcyl(7.0, P.SEAT_Z - 60, P.SEAT_Z, P.OUT_X)
    v6 = o6.common(tube).Volume; v7 = o7.common(tube).Volume
    out("open angle %.0f deg; flap in the cylinder D14 from the seat face down 60 mm: %.3f mm3; flap gasket: %.3f mm3: %s"
        % (P.OPEN_ANGLE, v6, v7, "PASS" if v6 < 0.01 and v7 < 0.01 else "FAIL"))
    bb6 = o6.BoundBox
    out("open flap BB X %.1f..%.1f, Z %.1f..%.1f (hinge X %.0f Z %.0f)" % (bb6.XMin, bb6.XMax, bb6.ZMin, bb6.ZMax, P.HINGE_X, P.HINGE_Z))
    slab = B.belly_ref()
    p6 = shape("P6_Flap"); p7 = shape("P7_FlapGasket")
    def hit_vol(a):
        f6 = B.rotate_open(p6, a); f7 = B.rotate_open(p7, a)
        return f6.common(slab).Volume + f7.common(slab).Volume

    def tube_vol(a):
        f6 = B.rotate_open(p6, a); f7 = B.rotate_open(p7, a)
        return f6.common(tube).Volume + f7.common(tube).Volume
    rows = [(a, hit_vol(a), tube_vol(a)) for a in range(0, 361, 5)]
    out("sweep in 5 deg steps. Skin slab: Z %.1f..%.1f, opening = rectangle X %.0f..%.0f, Y %.0f..%.0f, a D%.0f circle at the flap (flap + 3 mm) :"
        % (P.BELLY_Z, P.BELLY_Z + P.BELLY_T, P.FLOOR_HOLE_RECT[0], P.FLOOR_HOLE_RECT[1], P.FLOOR_HOLE_RECT[2], P.FLOOR_HOLE_RECT[3], P.FLAP_D + 6))
    out("  angle : flap+gasket in the skin slab (mm3) | in the bore tube D14 x 60 (mm3)")
    for a, vol, vt in rows:
        if a % 20 == 0 or a in (170, 175):
            out("  %3d   : %8.2f | %8.2f" % (a, vol, vt))
    first = next((a for a, v, t_ in rows if a > 0 and v > 0.01), None)
    if first is not None:
        fine = next((a for a in range(first - 5, first + 1) if a >= 0 and hit_vol(a) > 0.01), first)
    else:
        fine = None
    clear_from = next((a for a in range(0, 181, 5) if all(r[2] < 0.01 for r in rows if a <= r[0] <= 180)), None)
    out("closed (0 deg): slab overlap %.3f mm3 -> %s" % (rows[0][1], "contact only PASS" if rows[0][1] < 0.01 else "FAIL"))
    out("first angle where the flap or gasket touches the belly skin slab: %s deg (1 deg refinement); largest clear open angle %s deg" % (fine, None if fine is None else fine - 1))
    out("bore tube D14 x 60 is free for every angle from %s deg up to 180 deg (limit: free at 150 deg and above): %s"
        % (clear_from, "PASS" if clear_from is not None and clear_from <= 150 else "FAIL"))
    # ---------------- key check 5 ----------------
    out("")
    out("== Key check 5: release pin ==")
    p9 = shape("P9_ReleasePin"); o9 = shape("P9_ReleasePin_open")
    tab_hy = P.TAB_HALF_Y
    need = tab_hy - P.RP_TIP_Y
    out("closed: pin tip Y %.2f; hook tab face at Y +%.1f -> travel to free the hook %.2f mm (plan 9.5 incl. 0.2 margin); limit <= 14.1 (10 mm arm): %s"
        % (p9.BoundBox.YMin, tab_hy, need, "PASS" if need + 0.2 <= 14.1 else "FAIL"))
    tabbox = B.box(P.TAB_X[0], P.TAB_X[1], -tab_hy, tab_hy, P.TAB_BOTTOM_Z, P.FLAP_ZTOP)
    eng = p9.common(B.box(P.REL_PIN_POS[0] - 3, P.REL_PIN_POS[0] + 3, -tab_hy, tab_hy, -112, -108))
    out("engagement of the pin in the hook tab (Y extent of pin inside the tab): %.2f mm (limit >= 6): %s"
        % (eng.BoundBox.YLength, "PASS" if eng.BoundBox.YLength >= 6 - 1e-6 else "FAIL"))
    rl = P.LUG_Y[1]
    rbox = B.box(P.REL_PIN_POS[0] - 3, P.REL_PIN_POS[0] + 3, rl[0], rl[1], -114, -106)
    lug_in = o9.common(rbox)
    out("retracted pin (%.0f mm): tip Y %.2f; free of the tab (Y %.1f): %s; Y extent inside the right lug (Y %.0f..%.0f): %.2f mm: %s"
        % (P.RP_RETRACT, o9.BoundBox.YMin, tab_hy, "yes" if o9.BoundBox.YMin > tab_hy else "NO", rl[0], rl[1], lug_in.BoundBox.YLength if lug_in.Solids else 0.0,
           "PASS" if (o9.BoundBox.YMin > tab_hy and lug_in.Solids and lug_in.BoundBox.YLength >= 1.0) else "FAIL"))
    o10 = shape("P10_SafetyPin_open")
    out("safety pin: closed tip Y %.1f (right lug ends Y %.1f); open state: pulled out %.0f mm, tip Y %.1f (clear of the left lug Y %.1f)"
        % (shape("P10_SafetyPin").BoundBox.YMax, rl[1], P.SP_REMOVE, o10.BoundBox.YMax, P.LUG_Y[0][0]))
    # ---------------- overlaps ----------------
    out("")
    out("== Overlaps (closed state, pairwise common volume > 0.5 mm3 is reported) ==")
    names = [o.Name for g in (("A_Bottle", "B_Outlet", "C_Fill", "D_Mount", "D_Servo") if full else ("A_Bottle", "B_Outlet")) for o in d.getObject(g).Group]
    hits = []; n = 0
    for a_, b_ in itertools.combinations(names, 2):
        sa, sb = shape(a_), shape(b_)
        if not sa.BoundBox.intersect(sb.BoundBox):
            continue
        n += 1
        v = sa.common(sb).Volume
        if v > 0.5:
            hits.append((a_, b_, v))
    out("pairs with overlapping bounding boxes tested: %d" % n)
    if hits:
        for a_, b_, v in hits:
            out("  OVERLAP %s / %s: %.2f mm3" % (a_, b_, v))
    else:
        out("  no pair above 0.5 mm3: PASS")
    p4 = shape("P4_BasePlate")
    dist = p4.distToShape(pet)[0]
    out("base plate (lug block, tongues, body) to the bottle shell: minimum distance %.3f mm (gasket gap %.1f): %s"
        % (dist, P.GK_R_OUT - P.GK_R_IN, "PASS" if dist >= 0.9 else "FAIL"))
    pr = min(math.hypot(v.Point.y - P.AXIS_Y, v.Point.z - P.AXIS_Z) for v in p4.Vertexes if v.Point.z < P.AXIS_Z)
    out("base plate minimum vertex radius from the bottle axis %.2f (bottle outer %.1f, saddle %.1f)" % (pr, P.R_CYL, P.PL_SADDLE_R))
    if full:
        return LINES
    # ---------------- masses ----------------
    out("")
    out("== Masses (rule: printed >4 mm thick: volume x 1.27 x 0.45; thinner: volume x 1.27; gaskets 1.15; steel 7.85) ==")
    rows = []
    for o in d.Objects:
        if o.TypeId != "Part::Feature" or o.Name.startswith(("TMP_", "Ref_")) or o.Name.endswith("_open"):
            continue
        if o.Name in ("Water",):
            continue
        vol = o.Shape.Volume
        mat = o.Material
        if o.Name == "P1_Bottle":
            rows.append((o.Name, "PET (given)", vol, P.BOTTLE_MASS_G, "mass given (interp.); modelled %.1f g" % (vol / 1000 * P.RHO_PET))); continue
        if o.Name == "P1c_Cap":
            rows.append((o.Name, "PET", vol, 0.0, "included in the bottle 22 g")); continue
        rho = P.RHO[mat]
        f = P.INFILL_FACTOR if o.MassRule == "thick" else 1.0
        rows.append((o.Name, mat, vol, vol / 1000 * rho * f, ("x%.2f infill rule" % f) if f != 1 else ""))
    rows.append(("P8_KickSpring", "steel (bought)", 0.0, P.SPRING_G, "not modelled, catalogue estimate"))
    tot = sum(r[3] for r in rows)
    out("%-18s %-14s %10s %8s  %s" % ("part", "material", "vol mm3", "g", "note"))
    for r in rows:
        out("%-18s %-14s %10.1f %8.2f  %s" % r)
    out("TOTAL (bottle + outlet unit + pins + flag, no vent, saddles, straps, servo): %.2f g  (no fixed limit, D-047)" % tot)
    out("water (not in the budget): %.0f g" % P.WATER_G)
    import csv
    with open(os.path.join(OUTDIR, "mass_table_stageAB.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["part", "material", "volume_mm3", "mass_g", "note"])
        for r in rows:
            w.writerow([r[0], r[1], round(r[2], 1), round(r[3], 3), r[4]])
        w.writerow(["TOTAL", "", "", round(tot, 3), "stage A+B subtotal"])
    open(os.path.join(OUTDIR, "check_report_stageAB.txt"), "w").write("\n".join(LINES) + "\n")
    return LINES


# ======================================================================================
# R-C / R-D / R-E checks
# ======================================================================================
def dist(a, b):
    return a.distToShape(b)[0]


def run_full():
    """All checks 1 to 10 on the full model. Writes check_report.txt, mass_table.md, mass_table.csv."""
    import numpy as np
    d = B.doc()
    run_stage_ab(full=True)          # checks 0, A, 1 to 5 and the overlaps of all groups; LINES holds the text
    S = shape
    # ---------------- fill unit ----------------
    out("")
    out("== Key check 1b: fill flange, end-on insertion through the neck ==")
    vf = S("P11a_FillFlange")
    verts, _ = vf.tessellate(0.01)
    cx_, cy_, r = enclosing_circle([(v.y, v.z) for v in verts])
    out("enclosing circle of P11a (projection on YZ): diameter %.3f mm (limit <= %.1f, plan estimate 19.2): %s" % (2 * r, P.NECK_BORE_D - 0.5, "PASS" if 2 * r <= P.NECK_BORE_D - 0.5 + 1e-6 else "FAIL"))
    out("")
    out("== Key check 6: fill unit parts and the wing ==")
    wing = S("Ref_Wing")
    vparts = [o.Name for o in d.getObject("C_Fill").Group]
    zb = P.V_RULE_Z
    allok = True
    for n in vparts:
        sh = S(n)
        above = sh.common(B.box(-300, 300, -100, 100, zb, 100))
        xm = above.BoundBox.XMax if above.Solids else None
        dw = dist(sh, wing)
        ok = (xm is None or xm <= P.V_RULE_X_MAX + 1e-6) and dw >= P.V_WING_CLEAR
        allok &= ok
        out("  %-16s above Z %.0f: XMax %s ; distance to the wing %.2f mm: %s" % (n, zb, "none" if xm is None else "%.3f" % xm, dw, "PASS" if ok else "FAIL"))
    out("fill unit rule (X <= %.1f above Z %.0f, >= %.0f mm from the wing): %s" % (P.V_RULE_X_MAX, zb, P.V_WING_CLEAR, "PASS" if allok else "FAIL"))
    out("wing reference: lowest Z of the wing lower surface at X 60..260 = %.2f (plan -13); LE at X 0 Z 0" % min(
        w.BoundBox.ZMin for w in [wing.common(B.box(x, x + 1, -60, 60, -60, 60)) for x in range(60, 260, 20)]))
    # flange on the straight cylinder
    base = A_base()
    cyl0 = base + P.BOTTLE_PROFILE[1][0]
    out("")
    out("== Fill flange on the straight cylinder ==")
    out("cylinder starts at X %.2f (base %.2f + %.0f); flange front edge X %.2f: margin %.2f mm: %s"
        % (cyl0, base, P.BOTTLE_PROFILE[1][0], vf.BoundBox.XMin, vf.BoundBox.XMin - cyl0, "PASS" if vf.BoundBox.XMin >= cyl0 else "FAIL"))
    for n in ("P11b_FillGasket", "P11c_FillNut", "P11d_FillCap"):
        xm = S(n).BoundBox.XMin
        out("  %-16s front edge X %.2f: %s the cylinder start by %.2f mm" % (n, xm, "behind" if xm >= cyl0 else "ahead of", abs(xm - cyl0)))
    out("fill hole in the fuselage top: D%.0f at X %.1f spans X %.1f .. %.1f; wing LE at X 0 (the hole reaches %.1f mm aft of the LE)" % (
        P.FUSE_HOLE_D, P.FILL_X_C, P.FILL_X_C - P.FUSE_HOLE_D / 2, P.FILL_X_C + P.FUSE_HOLE_D / 2, max(0, P.FILL_X_C + P.FUSE_HOLE_D / 2)))
    # standing check
    out("")
    out("== Standing check: bottle on its base plane (base down, neck up) ==")
    out("base plane X = %.2f; lowest X of each group (must be >= base plane; outlet unit, fill unit, pins, flag excluded by the plan, shown for information):" % base)
    for g in ("A_Bottle",):
        mx = min(o.Shape.BoundBox.XMin for o in d.getObject(g).Group if o.Name != "Water")
        out("  bottle and neck cap: %.2f : %s" % (mx, "PASS" if mx >= base - 1e-6 else "FAIL"))
    out("  outlet unit (info): %.2f ; fill unit (info): %.2f ; saddles %.2f ; straps %.2f ; front stop %.2f (fuselage bulkhead, bears on the base, excluded)" % (
        min(o.Shape.BoundBox.XMin for o in d.getObject("B_Outlet").Group), min(S(n).BoundBox.XMin for n in vparts),
        min(S("P12a_Saddle1").BoundBox.XMin, S("P12b_Saddle2").BoundBox.XMin), min(S("P13a_Strap1").BoundBox.XMin, S("P13b_Strap2").BoundBox.XMin), S("P12c_FrontStop").BoundBox.XMin))
    out("  fill unit and outlet unit sit on the side wall: nothing under the base plane. Old rev A vent valve reached X -54: gone.")
    # capacity
    out("")
    out("== Capacity: water that can be poured in place ==")
    import res_build as RB
    I = RB.bottle_solids(base)["I"]
    ml = lambda v: v / 1000.0
    full = ml(I.Volume)
    bore_a = math.pi * (P.F_BORE / 2) ** 2
    z_lip = vf.BoundBox.ZMin
    # entrance of the bore in the flange face (highest point of the entrance circle)
    z_ent = P.AXIS_Z + math.sqrt(P.FL_TOP_R ** 2 - 0.0)
    out("interior volume %.1f mL; fill flange lowest point (lip level) Z %.2f; top of the bore entrance Z %.2f; stem top / cap seal Z %.1f" % (full, z_lip, z_ent, P.F_STEM_TOP_Z))
    for pitch in (0.0, 5.0):
        Ir = I.copy()
        c = V(P.OUT_X, 0, P.AXIS_Z)
        Ir.rotate(c, V(0, 1, 0), pitch)                # nose up: x < pivot rises
        fr = vf.copy(); fr.rotate(c, V(0, 1, 0), pitch)
        zl = fr.BoundBox.ZMin
        # bore entrance top after the pitch: entrance centre point
        ent = V(P.FILL_X_C, 0, P.AXIS_Z + P.FL_TOP_R); ent = c + (V(ent.x - c.x, ent.y, ent.z - c.z))
        import FreeCAD as _A
        rot = _A.Rotation(V(0, 1, 0), pitch)
        entr = c + rot.multVec(V(P.FILL_X_C - c.x, 0, (P.AXIS_Z + P.FL_TOP_R) - c.z))
        res = {}
        for lab, zz in (("lip level (flange lowest point)", zl), ("top of the bore entrance", entr.z)):
            below = ml(Ir.common(B.box(-100, 400, -100, 100, -300, zz)).Volume)
            stem_v = ml(bore_a * max(0.0, (P.F_STEM_TOP_Z - (P.AXIS_Z + P.FL_TOP_R)) / math.cos(math.radians(pitch))))
            res[lab] = (zz, below, full - below, stem_v)
        for lab, (zz, below, air, stem_v) in res.items():
            out("  pitch %.0f deg, %s: plane Z %.2f; water below it %.1f mL; trapped air above it %.1f mL; water that can rise in the bore up to the cap seal +%.1f mL" % (pitch, lab, zz, below, air, stem_v))
        zz, below, air, stem_v = res["lip level (flange lowest point)"]
        mx = below + stem_v
        out("  pitch %.0f deg: max fill (conservative: lip lowest point, plus the bore column) %.1f mL vs 1000 mL: %s" % (pitch, mx, "PASS" if mx >= 1000 else "FAIL"))
        mx2 = res["top of the bore entrance"][1] + res["top of the bore entrance"][3]
        out("  pitch %.0f deg: max fill (bore entrance top, plus the bore column) %.1f mL" % (pitch, mx2))
    # ---------------- check 7 ----------------
    out("")
    out("== Key check 7: widths ==")
    groups = [("A_Bottle", P.Y_LIMIT), ("C_Fill", P.Y_LIMIT), ("D_Mount", P.Y_LIMIT)]
    ok7 = True
    for g, lim in groups:
        for o in d.getObject(g).Group:
            bb = o.Shape.BoundBox
            y = max(abs(bb.YMin), abs(bb.YMax))
            ok = y <= lim + 1e-6
            ok7 &= ok
            out("  %-16s |Y| max %.2f (limit %.0f): %s" % (o.Name, y, lim, "PASS" if ok else "FAIL"))
    out("  outlet unit (P2..P10) |Y| max, excluding the flag tape: %.2f ; safety pin ring Y min %.1f ; release pin eye Y max %.1f"
        % (max(max(abs(S(n).BoundBox.YMin), abs(S(n).BoundBox.YMax)) for n in ("P2_InnerFlange", "P3_OuterGasket", "P4_BasePlate", "P5_Nut", "P6_Flap", "P7_FlapGasket", "P8_HingePin")),
           S("P10_SafetyPin").BoundBox.YMin, S("P9_ReleasePin").BoundBox.YMax))
    out("  safety-pin flag (removable tape, hangs out of the side before flight): Y min %.1f" % S("P10_Flag").BoundBox.YMin)
    sv = S("P14_Servo_MG90S")
    ok_s = sv.BoundBox.YMax <= P.SERVO_Y_LIMIT + 1e-6
    out("  servo case with tabs and boss: Y %.2f .. %.2f (limit <= %.0f): %s ; Z %.2f .. %.2f (limit >= %.1f): %s"
        % (sv.BoundBox.YMin, sv.BoundBox.YMax, P.SERVO_Y_LIMIT, "PASS" if ok_s else "FAIL", sv.BoundBox.ZMin, sv.BoundBox.ZMax, P.FLOOR_Z, "PASS" if sv.BoundBox.ZMin >= P.FLOOR_Z - 1e-6 else "FAIL"))
    degs = (-45, -30, -15, 0, 15, 30, 45)
    arms = {dg: B.build_arm(dg) for dg in degs}
    sweep_y = max(a_.BoundBox.YMax for a_ in arms.values())
    out("  arm swept envelope at -45..+45 deg (outer rim of the tip disc): Y max %.2f ; servo inside Y 52 -> %s (plan section 13 asks the fuselage for an inner wall >= Y 54 or a 9 mm arm)"
        % (sweep_y, "inside 52" if sweep_y <= 52 else "%.2f mm beyond 52, %.2f mm beyond 54" % (sweep_y - 52, max(0, sweep_y - 54))))
    # ---------------- servo kinematics and clearances (T2-30) ----------------
    out("")
    out("== R-D servo (upright, shaft down), arm and link ==")
    xs, ys = B.servo_shaft()
    t0 = B.arm_tip(P.ARM_CLOSED_DEG); t1 = B.arm_tip(P.ARM_CLOSED_DEG + 90)
    out("shaft (X %.2f, Y %.2f); arm R %.0f in the plane Z %.1f; tip closed (X %.2f, Y %.2f), after the 90 deg turn (X %.2f, Y %.2f): tip travel in Y %.2f"
        % (xs, ys, P.ARM_R, P.ARM_Z_CENTER, t0[0], t0[1], t1[0], t1[1], t1[1] - t0[1]))
    snap_, wire_, L0 = B.build_link()
    out("wire (snap end to tip centre) length %.2f mm (limit >= 5): %s" % (L0, "PASS" if L0 >= 5 else "FAIL"))
    ang = lambda deg: math.degrees(math.asin(min(1.0, abs(B.arm_tip(deg)[0] - P.REL_PIN_POS[0]) / L0)))
    out("wire angle to the pin axis (Y): closed %.1f deg, end of travel %.1f deg (limit <= 20): %s ; mid travel (arm along -X) %.1f deg (information)"
        % (ang(P.ARM_CLOSED_DEG), ang(P.ARM_CLOSED_DEG + 90), "PASS" if max(ang(P.ARM_CLOSED_DEG), ang(P.ARM_CLOSED_DEG + 90)) <= 20 else "FAIL", ang(P.ARM_CLOSED_DEG + 45)))
    sy0 = link_y = B.link_geometry(P.ARM_CLOSED_DEG, L0)[0]
    out("snap end closed Y %.2f (design %.2f)" % (sy0, P.SNAP_Y0 + P.SNAP_L))
    pull_end = B.link_geometry(P.ARM_CLOSED_DEG + 90, L0)[0] - sy0
    need = P.TAB_HALF_Y - P.RP_TIP_Y + 0.2
    best = None
    for k in range(0, 901):
        dg = P.ARM_CLOSED_DEG + k * 0.1
        pull = B.link_geometry(dg, L0)[0] - sy0
        if best is None and pull >= need:
            best = (dg - P.ARM_CLOSED_DEG, pull)
    out("eye travel at the end of the 90 deg turn %.2f mm (limit >= 12): %s ; mid travel %.2f mm" % (pull_end, "PASS" if pull_end >= 12 else "FAIL", B.link_geometry(P.ARM_CLOSED_DEG + 45, L0)[0] - sy0))
    if best:
        out("servo turn needed to free the hook (eye pulled %.1f mm): %.1f deg of 90" % (need, best[0]))
    # torque for 2.5 N pull on the eye
    def torque(dg):
        tx, ty = B.arm_tip(dg)
        ex, ey = P.REL_PIN_POS[0], B.link_geometry(dg, L0)[0]
        ux, uy = tx - ex, ty - ey
        ln = math.hypot(ux, uy); ux /= ln; uy /= ln
        T = 2.5 / abs(uy)
        lever = abs((tx - xs) * uy - (ty - ys) * ux)
        return T, lever, T * lever
    tq = [torque(P.ARM_CLOSED_DEG + k * 3) for k in range(0, 31)]
    worst_t = max(tq, key=lambda t: t[2])
    out("pull force on the eye 2.5 N (plan, interp.): at closed wire tension %.2f N, lever %.2f mm, servo torque %.1f N mm = %.1f %% of 177 N mm; worst over the turn %.1f N mm = %.1f %% (limit 50 %%): %s"
        % (tq[0][0], tq[0][1], tq[0][2], tq[0][2] / 177 * 100, worst_t[2], worst_t[2] / 177 * 100, "PASS" if worst_t[2] <= 88.5 else "FAIL"))
    out("clearances of the servo group (>= %.0f mm):" % P.SERVO_CLEAR)
    targets = ["P1_Bottle", "P12a_Saddle1", "P12b_Saddle2", "P13a_Strap1", "P13b_Strap2", "P12c_FrontStop", "P2_InnerFlange", "P3_OuterGasket", "P4_BasePlate",
               "P5_Nut", "P6_Flap", "P7_FlapGasket", "P8_HingePin", "P10_SafetyPin", "P10_Flag", "P11d_FillCap", "P11a_FillFlange", "Ref_BellySkin"]
    worst = (1e9, "")
    for sn in ("P14_Servo_MG90S", "P14_ServoArm", "P14_LinkWire", "P14_QuickSnap"):
        for tn in targets + ["P9_ReleasePin"]:
            if sn in ("P14_LinkWire", "P14_QuickSnap") and tn == "P9_ReleasePin":
                continue
            dd = dist(S(sn), S(tn))
            if dd < worst[0]:
                worst = (dd, "%s / %s" % (sn, tn))
    out("  minimum over all servo-group / reservoir pairs incl. the floor (excluding the link contacts snap-eye, wire-arm, wire-snap, arm-spline): %.2f mm at %s: %s" % (worst[0], worst[1], "PASS" if worst[0] >= P.SERVO_CLEAR else "FAIL"))
    for tn in ("P1_Bottle", "P4_BasePlate", "P6_Flap", "P13a_Strap1", "P12a_Saddle1", "Ref_BellySkin"):
        out("  servo case to %-14s %.2f mm ; arm %.2f ; wire %.2f" % (tn, dist(S("P14_Servo_MG90S"), S(tn)), dist(S("P14_ServoArm"), S(tn)), dist(S("P14_LinkWire"), S(tn))))
    arm_bottle = min(dist(a_, S("P1_Bottle")) for a_ in arms.values())
    arm_floor = min(dist(a_, S("Ref_BellySkin")) for a_ in arms.values())
    arm_case = min(dist(a_, S("P14_Servo_MG90S")) for a_ in arms.values())
    out("  swept arm (7 positions) to the bottle %.2f mm, to the floor reference %.2f mm: %s ; to the servo case %.2f (spline contact at the hub)" % (arm_bottle, arm_floor, "PASS" if min(arm_bottle, arm_floor) >= 2 else "FAIL", arm_case))
    out("saddle to bottle: radial gap %.1f mm foam tape (by design); strap on the bottle (contact); saddles in X: S1 %.1f..%.1f, S2 %.1f..%.1f" % (
        P.SADDLE_GAP, S("P12a_Saddle1").BoundBox.XMin, S("P12a_Saddle1").BoundBox.XMax, S("P12b_Saddle2").BoundBox.XMin, S("P12b_Saddle2").BoundBox.XMax))
    out("front stop X %.2f .. %.2f (base X %.2f, gap %.1f); fill cap to the stop plate: %.2f mm" % (S("P12c_FrontStop").BoundBox.XMin, S("P12c_FrontStop").BoundBox.XMax, A_base(), P.STOP_GAP, dist(S("P11d_FillCap"), S("P12c_FrontStop"))))
    # ---------------- check 11 ----------------
    out("")
    out("== Key check 11: lowest points in the closed state (ground plane Z %.1f, limit: nothing below Z %.1f) ==" % (P.BELLY_Z, -114.0))
    zl = []
    for g in ("A_Bottle", "B_Outlet", "C_Fill", "D_Mount", "D_Servo"):
        for o in d.getObject(g).Group:
            if o.Name != "Water":
                zl.append((o.Shape.BoundBox.ZMin, o.Name))
    zl.sort()
    exempt = ("P12a_Saddle1", "P12b_Saddle2")
    worst11 = min(z for z, n in zl if n not in exempt)
    out("  lowest parts: " + ", ".join("%s %.2f" % (n, z) for z, n in zl[:6]))
    out("  saddle feet stand on the floor (Z %.1f, structure that bears on the floor, exempt): %s" % (P.FLOOR_Z, ", ".join("%s %.2f" % (n, z) for z, n in zl if n in exempt)))
    out("  lowest reservoir or servo part (saddle feet excluded): Z %.2f (limit >= -114.0): %s ; margin to the ground plane %.2f mm" % (worst11, "PASS" if worst11 >= -114.0 - 1e-6 else "FAIL", worst11 - P.BELLY_Z))
    out("  the 3 mm gap under the valve: lug / knuckle bottom Z %.2f to the skin outer face %.1f = %.2f mm; belly opening X %.0f..%.0f" % (
        min(S("P4_BasePlate").BoundBox.ZMin, S("P6_Flap").BoundBox.ZMin), P.BELLY_Z, min(S("P4_BasePlate").BoundBox.ZMin, S("P6_Flap").BoundBox.ZMin) - P.BELLY_Z, P.FLOOR_HOLE_RECT[0], P.FLOOR_HOLE_RECT[1]))
    # ---------------- check 9 extras ----------------
    out("")
    out("== Key check 9 extras ==")
    pet = S("P1_Bottle")
    out("bottle to the wing: 3D distance %.2f mm; bottle top Z %.2f vs wing lowest Z at X 60..260 -13.1: margin %.1f mm (limit >= 5): %s"
        % (dist(pet, wing), pet.BoundBox.ZMax, -13.1 - pet.BoundBox.ZMax, "PASS" if dist(pet, wing) >= 5 else "FAIL"))
    for n in ("P13a_Strap1", "P13b_Strap2", "P12a_Saddle1", "P12b_Saddle2"):
        out("  %-14s to the wing %.2f mm" % (n, dist(S(n), wing)))
    # ---------------- masses ----------------
    out("")
    out("== Key check 8: masses ==")
    rows = []
    for g in ("A_Bottle", "B_Outlet", "C_Fill", "D_Mount", "D_Servo"):
        for o in d.getObject(g).Group:
            n = o.Name
            if n == "Water":
                continue
            vol = o.Shape.Volume
            rule = o.MassRule
            if n == "P1_Bottle":
                rows.append((n, g, "PET (given)", vol, P.BOTTLE_MASS_G, True, "mass given 22 g (interp.); the modelled shell is only a picture body (%.1f g at %.2f g/cm3)" % (vol / 1000 * P.RHO_PET, P.RHO_PET))); continue
            if n == "P1c_Cap":
                rows.append((n, g, "PET", vol, 0.0, True, "included in the bottle 22 g")); continue
            if rule.startswith("given:"):
                rows.append((n, g, "bought", vol, float(rule.split(":")[1]), True, o.Note)); continue
            if rule.startswith("servo:"):
                rows.append((n, g, "bought", vol, float(rule.split(":")[1]), False, "MG90S, excluded from the reservoir total")); continue
            rho = P.RHO[o.Material]
            if rule == "info":
                rows.append((n, g, o.Material, vol, vol / 1000 * rho, False, o.Note)); continue
            f = P.INFILL_FACTOR if rule == "thick" else 1.0
            rows.append((n, g, o.Material, vol, vol / 1000 * rho * f, True, ("x%.2f infill rule; " % f if f != 1 else "") + o.Note))
    rows.append(("P8_KickSpring", "B_Outlet", "steel (bought)", 0.0, P.SPRING_G, True, "not modelled, estimate"))
    tot = sum(r[4] for r in rows if r[5])
    out("%-18s %-9s %-14s %10s %8s %5s" % ("part", "group", "material", "vol mm3", "g", "count"))
    for r in rows:
        out("%-18s %-9s %-14s %10.1f %8.2f %5s  %s" % (r[0], r[1], r[2], r[3], r[4], "yes" if r[5] else "no", r[6]))
    sub = {}
    for r in rows:
        if r[5]:
            sub[r[1]] = sub.get(r[1], 0) + r[4]
    out("subtotals (g): " + ", ".join("%s %.2f" % (k, v) for k, v in sub.items()))
    out("TOTAL reservoir without the MG90S body and without the balsa front stop: %.2f g  (no fixed limit, D-047)" % tot)
    stop_m = [r[4] for r in rows if r[0] == "P12c_FrontStop"][0]
    out("with the balsa front stop %.2f g: %.2f g ; with the MG90S %.1f g as well: %.2f g ; water %.0f g (not in the budget)" % (stop_m, tot + stop_m, P.SERVO_MASS_G, tot + stop_m + P.SERVO_MASS_G, P.WATER_G))
    out("change from rev A (vent, 47.75 g): %+.2f g (fill unit %.2f g)" % (tot - 47.75, sub.get("C_Fill", 0)))
    f6 = [r[4] for r in rows if r[0] == "P6_Flap"][0]
    out("flap P6 mass %.2f g (target <= 1.8 g): %s" % (f6, "PASS" if f6 <= 1.8 else "NOT MET (see report)"))
    import csv
    with open(os.path.join(OUTDIR, "mass_table.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["part", "group", "material", "volume_mm3", "mass_g", "counted_in_total", "note"])
        for r in rows:
            w.writerow([r[0], r[1], r[2], round(r[3], 1), round(r[4], 3), "yes" if r[5] else "no", r[6]])
        w.writerow(["TOTAL", "", "", "", round(tot, 3), "", "without MG90S and without the front stop; no fixed limit (D-047)"])
    with open(os.path.join(OUTDIR, "mass_table.md"), "w") as f:
        f.write("# Reservoir rev A mass table\n\nMass rule: printed parts thicker than 4 mm: volume x 1.27 g/cm3 x 0.45 (2 walls, 15 % infill, interp.); thinner printed parts: volume x density; gaskets silicone 1.15 (outer) and EVA 0.10 (flap gasket, interp.); steel 7.85; bought parts by estimate; bottle 22 g (interp., weigh).\n\n")
        f.write("| part | group | material | volume mm3 | mass g | counted | note |\n|---|---|---|---|---|---|---|\n")
        for r in rows:
            f.write("| %s | %s | %s | %.1f | %.2f | %s | %s |\n" % (r[0], r[1], r[2], r[3], r[4], "yes" if r[5] else "no", r[6]))
        f.write("\n**Total (without the MG90S body and without the balsa front stop): %.2f g (no fixed limit, D-047).**\n\n" % tot)
        f.write("With the front stop (%.2f g): %.2f g. With the MG90S (%.1f g): %.2f g. Water: %.0f g (not in the budget).\n" % (stop_m, tot + stop_m, P.SERVO_MASS_G, tot + stop_m + P.SERVO_MASS_G, P.WATER_G))
    # ---------------- check 10 and summary ----------------
    out("")
    out("== Key check 10 ==")
    A = load_a()
    out("water centroid X %.3f (target 80 +/- 1), water %.1f mL" % (A.get("water_cx", float("nan")), A.get("water_ml", float("nan"))))
    open(os.path.join(OUTDIR, "check_report.txt"), "w").write("\n".join(LINES) + "\n")
    return LINES


def A_base():
    return load_a().get("base_x", float("nan"))
