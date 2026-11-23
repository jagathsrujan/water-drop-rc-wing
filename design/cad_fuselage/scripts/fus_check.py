"""Fuselage rev A - checks, stage F-A. Run inside FreeCAD after build_stageA.py: fus_check.run_stage_a().
Writes design/cad_fuselage/check_report_stageA.txt (numbers and PASS/FAIL)."""
import os, math, time
import FreeCAD as App
import Part
from FreeCAD import Vector as V
import fus_params as P
import fus_build as B

OUTDIR = P.ROOT
LINES = []
PARTS = ["F1_PodNose", "F2_PodCentre", "F3_PodAft", "F4_NoseHatch"]
POD = ["F1_PodNose", "F2_PodCentre", "F3_PodAft"]
RESULT = {}


def out(s=""):
    print(s)
    LINES.append(s)


def S(n):
    return B.doc().getObject(n).Shape


def pf(ok):
    return "PASS" if ok else "FAIL"


def vline_z(shape, x, y, z0=-200.0, z1=60.0):
    """Z values where a vertical line at (x, y) crosses the shape boundary."""
    e = Part.makeLine(V(x, y, z0), V(x, y, z1))
    return sorted(v.Point.z for v in shape.section(e).Vertexes)


def hline_y(shape, x, z, y0=0.0, y1=80.0):
    """Y values where a line along Y at (x, z) crosses the shape boundary."""
    e = Part.makeLine(V(x, y0, z), V(x, y1, z))
    return sorted(v.Point.y for v in shape.section(e).Vertexes)


def mesh_ext(shape, defl=0.02):
    pts, _ = shape.tessellate(defl)
    return (min(p.x for p in pts), max(p.x for p in pts), min(p.y for p in pts), max(p.y for p in pts),
            min(p.z for p in pts), max(p.z for p in pts))


def overlap(a, b):
    return B.ovl(a, b)          # robust (see fus_build.ovl)


def inner_face_y_analytic(Rb, z):
    """Inner face Y of a full section (W 55, Zb BELLY_Z, floor T_FLOOR concentric corner, side T_SIDE) at height z."""
    W, Zb, tf, ts = P.CENTRE_W, P.BELLY_Z, P.T_FLOOR, P.T_SIDE
    cy, cz, r = W - Rb, Zb + Rb, Rb - tf
    if z >= cz + P.TRANS_H:
        return W - ts
    if z >= cz:
        return (W - tf) + (tf - ts) * (z - cz) / P.TRANS_H
    dz = cz - z
    return cy + math.sqrt(max(r * r - dz * dz, 0.0)) if dz < r else float("nan")


def normal_thickness(shape, x, side, half=4.0, n=161):
    """Skin thickness at Y 0: vertical (section plane) and normal (smallest distance in the XZ plane from the outer point
    at X to the inner surface sampled over X +- half). side = 'bottom' or 'top'."""
    def zz(xx):
        zs = vline_z(shape, xx, 0.0)
        if len(zs) < 2:
            return None
        return (zs[0], zs[1]) if side == "bottom" else (zs[-1], zs[-2])     # (outer, inner)
    zo, zi = zz(x)
    best = abs(zi - zo)
    for i in range(n):
        xx = x - half + 2 * half * i / (n - 1)
        r = zz(xx)
        if r:
            best = min(best, math.hypot(xx - x, r[1] - zo))
    return abs(zi - zo), best


def run_stage_a():
    del LINES[:]
    t0 = time.time()
    d = B.doc()
    allpod = Part.makeCompound([S(n) for n in PARTS])
    pod3 = Part.makeCompound([S(n) for n in POD])
    wing = S("Ref_Wing")
    refres = sorted(o.Name for o in d.Objects if o.Name.startswith("RefRes_"))
    out("Fuselage rev A - check report, stage F-A  (%s)" % time.strftime("%Y-%m-%d %H:%M"))
    out("Frame: wing frame, origin wing LE on the centreline, X aft, Y right, Z up, mm. Wing +3 deg about +Y.")
    out("Model: %s ; parameters: scripts/fus_params.py (section 13 values read from res_params.py + result_stageA.json)" % P.FCSTD)
    out("")

    # ---------------- 0. inputs from the reservoir model and differences to section 13 ----------------
    out("== 0. Reservoir link (section 13 values read from the reservoir model; the model wins) ==")
    out("bottle base X %.3f ; BELLY_Z %.1f ; FLOOR_Z %.1f ; FLOOR_HOLE_RECT %s ; FILL_X_C %.1f ; cap top Z %.1f"
        % (P.BOTTLE_BASE_X, P.BELLY_Z, P.FLOOR_Z, P.FLOOR_HOLE_RECT, P.FILL_X_C, P.CAP_TOP_Z))
    s1 = S("RefRes_P12a_Saddle1").BoundBox; s2 = S("RefRes_P12b_Saddle2").BoundBox; st = S("RefRes_P12c_FrontStop").BoundBox
    ref = P.SECTION13_REF
    out("saddle 1: sleeve X %.2f .. %.2f, feet + strap pads X %.2f .. %.2f (section 13: X %.0f .. %.0f) -> difference %.2f mm"
        % (P.SADDLE1_X[0], P.SADDLE1_X[1], s1.XMin, s1.XMax, ref["saddle1"][0], ref["saddle1"][1], P.SADDLE1_X[0] - ref["saddle1"][0]))
    out("saddle 2: sleeve X %.2f .. %.2f, feet + strap pads X %.2f .. %.2f (section 13: X %.0f .. %.0f) -> difference %.2f mm"
        % (P.SADDLE2_X[0], P.SADDLE2_X[1], s2.XMin, s2.XMax, ref["saddle2"][0], ref["saddle2"][1], P.SADDLE2_X[0] - ref["saddle2"][0]))
    out("front stop: X %.2f .. %.2f (section 13: X %.1f .. %.1f) -> difference %.2f mm ; it lies in F1 (split X %.0f), %.2f mm ahead of the split"
        % (st.XMin, st.XMax, ref["stop"][0], ref["stop"][1], st.XMin - ref["stop"][0], P.SPLIT_X[0], P.SPLIT_X[0] - st.XMax))
    sv = B.mesh_bb(S("RefRes_P14_Servo_MG90S"), 0.01)
    out("release servo (RefRes mesh) Y %.2f .. %.2f, Z %.2f .. %.2f ; res_params case Y %.2f .. %.2f (SERVO_Y_SHAFT +- W/2)"
        % (sv[2], sv[3], sv[4], sv[5], P.SERVO_Y_SHAFT - P.RP.MG90S["W"] / 2, P.SERVO_CASE_YMAX))
    out("")

    # ---------------- a. belly ----------------
    out("== a. Belly: outer Z = BELLY_Z over X %.0f .. %.0f ==" % (P.NOSE_END_X, P.AFT_X0))
    zb, zi = [], []
    for x in B.frange(P.NOSE_END_X + 0.5, P.AFT_X0, 2.5):
        for y in (0.0, 30.0, -30.0, 45.0):
            zs = vline_z(pod3, x, y)
            if len(zs) >= 2:
                zb.append(zs[0]); zi.append(zs[1])
    sec = B.common_robust(pod3, B.box(P.NOSE_END_X, P.AFT_X0, -100, 100, -200, 100))
    ok_a = abs(min(zb) - P.BELLY_Z) < 1e-4 and abs(max(zb) - P.BELLY_Z) < 1e-4 and abs(sec.BoundBox.ZMin - P.BELLY_Z) < 1e-4
    out("outer bottom Z at %d samples (X step 2.5, Y 0/+-30/45): min %.4f max %.4f ; shell Z min in X %.0f..%.0f: %.4f -> %s"
        % (len(zb), min(zb), max(zb), P.NOSE_END_X, P.AFT_X0, sec.BoundBox.ZMin, pf(ok_a)))
    out("floor skin inner face Z: %.3f .. %.3f (skin %.1f mm). FLOOR_Z %.1f: the floor grid up to FLOOR_Z comes in F-B (%.2f mm)"
        % (min(zi), max(zi), P.T_FLOOR, P.FLOOR_Z, P.FLOOR_Z - max(zi)))
    RESULT["a"] = ok_a
    out("")

    # ---------------- b. width and servo wall ----------------
    out("== b. Width and servo wall ==")
    c = B.common_robust(allpod, B.box(0, 280, -150, 150, -200, 100))
    ymax = max(abs(c.BoundBox.YMin), abs(c.BoundBox.YMax))
    ok_b1 = ymax <= P.Y_LIMIT + 1e-6
    out("outer |Y| max at X 0 .. 280: %.4f (limit <= %.1f) -> %s" % (ymax, P.Y_LIMIT, pf(ok_b1)))
    me = mesh_ext(allpod)
    out("whole pod (mesh): X %.2f .. %.2f, |Y| max %.3f, Z %.2f .. %.2f" % (me[0], me[1], max(-me[2], me[3]), me[4], me[5]))
    f2 = S("F2_PodCentre")
    svb = B.mesh_bb(S("RefRes_P14_Servo_MG90S"), 0.01)
    z_sv0, z_sv1 = svb[4], svb[5]                                   # servo bottom / top (from the model)
    z_arm0, z_arm = P.ARM_Z_CENTER - P.ARM_T / 2, P.ARM_Z_CENTER    # arm bottom face, arm plane (res_params)
    zlev = [z_sv0 + 0.1 * i for i in range(0, 11)] + [z_arm0, z_arm, z_arm + 0.5, z_arm + 1.0, z_arm + 2.5, z_arm + 4.5] + list(B.frange(z_sv0 + 11.9, z_sv1, 6.0))
    worst = (99.0, None, None)
    for x in B.frange(P.SERVO_WALL_X[0], P.SERVO_WALL_X[1], 5.0):
        for z in zlev:
            ys = [y for y in hline_y(f2, x, z) if y > 30]
            if ys and ys[0] < worst[0]:
                worst = (ys[0], x, z)
    ok_b2 = worst[0] >= P.SERVO_WALL_INNER_MIN - 1e-6
    out("right side-wall inner face, X %.0f..%.0f step 5, Z %.2f (servo bottom) .. %.2f (servo top), %d levels: min Y %.3f at X %.0f Z %.2f (limit >= %.1f) -> %s"
        % (P.SERVO_WALL_X[0], P.SERVO_WALL_X[1], z_sv0, z_sv1, len(zlev), worst[0], worst[1], worst[2], P.SERVO_WALL_INNER_MIN, pf(ok_b2)))
    for z in (z_sv0, z_arm0, z_arm, -100.0):
        ys = [y for y in hline_y(f2, 70.0, z) if y > 30]
        out("  inner face at X 70, Z %.1f: Y %.3f" % (z, ys[0] if ys else float("nan")))
    out("  alternatives for the bottom corner radius Rb (inner face Y, analytic, same walls):")
    for rb in (15.0, 10.0, 9.0, 8.0, 6.0):
        out("    Rb %4.1f: at Z %.2f (servo bottom) %.2f ; at Z %.2f (arm bottom) %.2f ; at Z %.2f (arm plane) %.2f -> %s"
            % (rb, z_sv0, inner_face_y_analytic(rb, z_sv0), z_arm0, inner_face_y_analytic(rb, z_arm0), z_arm, inner_face_y_analytic(rb, z_arm),
               "meets %.1f" % P.SERVO_WALL_INNER_MIN if inner_face_y_analytic(rb, z_sv0) >= P.SERVO_WALL_INNER_MIN else "below %.1f" % P.SERVO_WALL_INNER_MIN))
    # arm sweep (tip disc, -45 .. +45 deg, as the reservoir check) to the wall
    xs_, ys_ = P.SERVO_X_SHAFT, P.SERVO_Y_SHAFT
    discs = []
    for dg in range(int(P.ARM_SWEEP_DEG[0]), int(P.ARM_SWEEP_DEG[1]) + 1, 5):
        a = math.radians(dg)
        tx, ty = xs_ - P.ARM_R * math.cos(a), ys_ + P.ARM_R * math.sin(a)
        discs.append(Part.makeCylinder(P.ARM_W / 2, P.ARM_T, V(tx, ty, P.ARM_Z_CENTER - P.ARM_T / 2), V(0, 0, 1)))
    env = Part.makeCompound(discs)
    d_arm = env.distToShape(f2)[0]
    out("  release-servo arm tip sweep -45..+45 deg (Y max %.2f): distance to F2 %.2f mm (plan 9.2 asks >= 2 mm elsewhere; moving parts T2-8 >= 3 mm) -> INFO (limited by section 13: wall inner face Y 54.5 gives at most %.2f)"
        % (env.BoundBox.YMax, d_arm, P.CENTRE_W - P.T_SIDE - env.BoundBox.YMax))
    d_sp = S("RefRes_P10_SafetyPin_open").distToShape(f2)[0]
    out("  left side: safety pin pulled out (open state, Y min %.2f) to F2: %.2f mm" % (B.mesh_bb(S("RefRes_P10_SafetyPin_open"), 0.01)[2], d_sp))
    RESULT["b"] = ok_b1 and ok_b2
    out("")

    # ---------------- c. belly opening ----------------
    out("== c. Belly opening free ==")
    r = P.FLOOR_HOLE_RECT
    v = B.common_robust(allpod, B.box(r[0], r[1], r[2], r[3], -300, 200)).Volume
    ok_c = v < P.OVERLAP_TOL
    out("shell volume inside the prism X %.0f..%.0f, Y %.0f..%.0f, all Z: %.6f mm3 -> %s" % (r[0], r[1], r[2], r[3], v, pf(ok_c)))
    RESULT["c"] = ok_c
    out("")

    # ---------------- d. overlaps and distances ----------------
    out("== d. Overlap (tol %.0e mm3) and minimum distance: pod parts / hatch <-> reservoir references and the wing ==" % P.OVERLAP_TOL)
    fails = []
    for rn in refres + ["Ref_Wing"]:
        rs = S(rn)
        vols = {pn: overlap(S(pn), rs) for pn in PARTS}
        vmax = max(vols.values())
        dmin, near = min((S(pn).distToShape(rs)[0], pn) for pn in PARTS)
        ok = vmax < P.OVERLAP_TOL
        if not ok:
            fails.append(rn)
        st = getattr(d.getObject(rn), "ResState", "-")
        out("  %-30s %-6s overlap %s ; min distance %.3f mm (nearest %s) -> %s"
            % (rn, st, ", ".join("%s %.3f" % (k[:2], vv) for k, vv in vols.items() if vv > 0) or "0", dmin, near, pf(ok)))
    RESULT["d"] = not fails
    out("overlap check: %s%s" % (pf(not fails), "" if not fails else " (overlaps: %s)" % ", ".join(fails)))
    if fails:
        out("  note: P10_Flag (and its open copy) crosses the left wall by design (section 13: flag through a hole in the left wall at"
            " X %.0f, Z %.1f); the flag hole is an F-B feature." % P.SAF_PIN_POS)
    out("")

    # ---------------- e. wing seat, LE, hatch over the cap ----------------
    out("== e. Wing seat, wing LE and hatch ==")
    out("station: the side-wall top at mid-thickness, Y = W(x) - %.2f (no shell at |Y| 50 in F-A: the 8 mm seat lip comes in F-B;"
        " aft of X ~226 the walls are inboard of |Y| 50); gap = vertical, normal gap = vertical x cos(slope)" % (P.T_SIDE / 2))
    xte, _ = B.te_point()
    xs = B.frange(P.SEAT_X[0], 272.0, P.SEAT_DX) + [xte - 0.1]
    gaps = []
    for x in xs:
        W, _, _ = B.side_sec(x)
        y = W - P.T_SIDE / 2
        part = S("F2_PodCentre") if x <= P.SPLIT_X[1] else S("F3_PodAft")
        zw = vline_z(part, x, y)
        zl = vline_z(wing, x, y)
        if not zw or not zl:
            out("  X %6.1f: no wall or wing at Y %.2f" % (x, y)); gaps.append(None); continue
        g = zl[0] - zw[-1]
        h = 0.5
        slope = (B.wing_lower_z(min(x + h, xte)) - B.wing_lower_z(max(x - h, 0.05))) / (min(x + h, xte) - max(x - h, 0.05))
        gn = g * math.cos(math.atan(slope))
        gaps.append((x, y, zw[-1], zl[0], g, gn))
    okg = all(gg is not None and abs(gg[4] - P.FOAM_T) <= P.GAP_TOL and abs(gg[5] - P.FOAM_T) <= P.GAP_TOL for gg in gaps)
    for gg in gaps:
        if gg:
            out("  X %6.1f Y %5.2f: wall top Z %8.3f, wing lower Z %8.3f, gap %.3f (normal %.3f)" % gg)
    gv = [gg[4] for gg in gaps if gg]; gnv = [gg[5] for gg in gaps if gg]
    out("seat gap: vertical %.3f .. %.3f, normal %.3f .. %.3f (limit %.1f +- %.1f) -> %s" % (min(gv), max(gv), min(gnv), max(gnv), P.FOAM_T, P.GAP_TOL, pf(okg)))
    f4 = S("F4_NoseHatch")
    d_le = f4.distToShape(wing)[0]
    ok_le = d_le >= P.LE_CLEAR_MIN
    out("wing LE <-> hatch F4: %.3f mm (limit >= %.1f) -> %s" % (d_le, P.LE_CLEAR_MIN, pf(ok_le)))
    d_wf2 = S("F2_PodCentre").distToShape(wing)[0]
    out("wing <-> F2 (seat): %.3f mm (normal gap near X 2, information)" % d_wf2)
    cap = S("RefRes_P11d_FillCap").BoundBox
    zin = []
    for x in (cap.XMin + 0.5, P.FILL_X_C, cap.XMax - 0.5):
        for y in (0.0, cap.YMin + 0.5, cap.YMax - 0.5):
            zs = vline_z(f4, x, y)
            if zs:
                zin.append(zs[0])
    hc = min(zin) - P.CAP_TOP_Z
    ok_hc = hc >= P.HATCH_CAP_MIN - 1e-6
    out("hatch inner face over the fill cap (X %.1f..%.1f, Y %.1f..%.1f): Z min %.3f ; cap top Z %.1f -> clearance %.3f mm (limit >= %.1f) -> %s"
        % (cap.XMin, cap.XMax, cap.YMin, cap.YMax, min(zin), P.CAP_TOP_Z, hc, P.HATCH_CAP_MIN, pf(ok_hc)))
    kn = S("RefRes_P11f_VentFlap")
    out("  nearest fill-unit part: vent-flap knob P11f top Z %.3f -> hatch inner face %.3f mm above it ; distance F4 <-> P11f %.3f mm, F4 <-> P11d cap %.3f mm (information)"
        % (kn.BoundBox.ZMax, min(zin) - kn.BoundBox.ZMax, f4.distToShape(kn)[0], f4.distToShape(S("RefRes_P11d_FillCap"))[0]))
    RESULT["e"] = okg and ok_le and ok_hc
    out("")

    # ---------------- f. lift-out sweep ----------------
    out("== f. Lift-out sweep: moving set +Z in %.0f mm steps to +%.0f, F4 and Ref_Wing removed; obstacles F1..F3 ==" % (P.LIFT_STEP, P.LIFT_TRAVEL))
    moving = [o.Name for o in d.Objects if o.Name.startswith("RefRes_") and getattr(o, "MovingSet", False)]
    out("moving set (%d): %s" % (len(moving), ", ".join(n[7:] for n in moving)))

    def sweep(names):
        obst = [(n, S(n)) for n in POD]
        first = None
        steps = int(round(P.LIFT_TRAVEL / P.LIFT_STEP))
        for mn in names:
            ms = S(mn)
            bb = ms.BoundBox
            for on, osh in obst:
                ob = osh.BoundBox
                if bb.XMax < ob.XMin or bb.XMin > ob.XMax or bb.YMax < ob.YMin or bb.YMin > ob.YMax or bb.ZMin + P.LIFT_TRAVEL < ob.ZMin or bb.ZMin > ob.ZMax:
                    continue
                for i in range(steps + 1):
                    dz = i * P.LIFT_STEP
                    if first is not None and dz >= first[0]:
                        break
                    m2 = ms.copy(); m2.translate(V(0, 0, dz))
                    vv = overlap(m2, osh)
                    if vv > P.OVERLAP_TOL:
                        first = (dz, mn, on, vv)
                        break
        return first
    f_all = sweep(moving)
    if f_all:
        out("full moving set: first contact at dz %.0f mm: %s <-> %s, overlap %.3f mm3 -> FAIL" % (f_all[0], f_all[1][7:], f_all[2], f_all[3]))
    else:
        out("full moving set: no contact up to +%.0f -> PASS" % P.LIFT_TRAVEL)
    no_flag = [n for n in moving if n != "RefRes_P10_Flag"]
    f_nf = sweep(no_flag)
    if f_nf:
        out("without P10_Flag (pin and flag pulled first): first contact at dz %.0f mm: %s <-> %s, overlap %.3f mm3 -> FAIL" % (f_nf[0], f_nf[1][7:], f_nf[2], f_nf[3]))
    else:
        out("without P10_Flag (safety pin + flag pulled before the lift-out): no contact up to +%.0f -> PASS" % P.LIFT_TRAVEL)
    RESULT["f"] = f_all is None
    RESULT["f_noflag"] = f_nf is None
    out("")

    # ---------------- g. validity, volumes, masses, build volume ----------------
    out("== g. Validity, volumes, masses, build volume ==")
    bad = [o.Name for o in d.Objects if o.TypeId == "Part::Feature" and not o.Shape.isValid()]
    out("all solids isValid(): %s%s" % (pf(not bad), "" if not bad else " (invalid: %s)" % bad))
    hdr = "  %-14s %10s  %s  %s" % ("part", "vol cm3", "  ".join("%13s" % k for k in P.RHO), "build-volume (sorted BB sizes)")
    out(hdr)
    tot = {k: 0.0 for k in P.RHO}
    vtot = 0.0
    okbv = True
    masses = {}
    for pn in PARTS:
        s = S(pn)
        vol = s.Volume / 1000.0
        vtot += vol
        mb = B.mesh_bb(s)
        dims = sorted((mb[1] - mb[0], mb[3] - mb[2], mb[5] - mb[4]))
        ok = all(x <= P.BUILD_VOL for x in dims)
        okbv &= ok
        ms = {k: vol * rho for k, rho in P.RHO.items()}
        masses[pn] = ms
        for k in tot:
            tot[k] += ms[k]
        out("  %-14s %10.2f  %s  %.1f x %.1f x %.1f -> %s" % (pn, vol, "  ".join("%11.1f g" % ms[k] for k in P.RHO), dims[0], dims[1], dims[2], pf(ok)))
    out("  %-14s %10.2f  %s" % ("total F1..F4", vtot, "  ".join("%11.1f g" % tot[k] for k in P.RHO)))
    out("build volume %.0f mm cube: %s" % (P.BUILD_VOL, pf(okbv)))
    L = P.POD_END_X - P.FIREWALL_X
    for k, pm in P.PLAN_MASS.items():
        out("plan section 5 (%s, 0.5/0.8 walls, %.0f mm, incl. ribs, floor grid, hatch rim, socket block): %.0f g -> scaled to %.0f mm: %.0f g ; model shell only: %.1f g (%.0f %% of the scaled plan value)"
            % (k, P.PLAN_LEN, pm, L, pm * L / P.PLAN_LEN, tot[k], 100 * tot[k] / (pm * L / P.PLAN_LEN)))
    out("skin thickness normal to the surface on sloped skin (section plane value 0.8; measured at Y 0 in the XZ plane, information):")
    for x, part, side in ((290.0, "F3_PodAft", "bottom"), (260.0, "F3_PodAft", "bottom"), (230.0, "F3_PodAft", "bottom"),
                          (-165.0, "F1_PodNose", "bottom"), (-130.0, "F1_PodNose", "bottom"), (-160.0, "F4_NoseHatch", "top")):
        tn = normal_thickness(S(part), x, side)
        out("  X %7.1f %-6s (%s): vertical %.3f, normal %.3f mm" % (x, side, part, tn[0], tn[1]))
    RESULT["g"] = (not bad) and okbv
    RESULT["masses"] = masses
    RESULT["mass_total"] = tot
    out("")
    out("== Summary ==")
    for k, label in (("a", "belly Z"), ("b", "width and servo wall"), ("c", "belly opening free"), ("d", "no overlap with the reservoir / wing"),
                     ("e", "wing seat, LE, hatch over the cap"), ("f", "lift-out sweep (full moving set)"), ("f_noflag", "lift-out without the safety-pin flag"),
                     ("g", "validity and build volume")):
        out("  %-9s %-42s %s" % (k, label, pf(RESULT[k])))
    out("check time %.0f s" % (time.time() - t0))
    if OUTDIR:
        open(os.path.join(OUTDIR, "check_report_stageA.txt"), "w").write("\n".join(LINES) + "\n")
    return RESULT
