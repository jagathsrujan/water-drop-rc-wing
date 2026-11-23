"""Stage F-B checks (stageB_brief.md). Writes check_report_stageB.txt. Call run_stage_b() inside FreeCAD after build_stageB."""
import os, math
import FreeCAD as App
import Part
import fus_params as P
import fus_build as B

V = App.Vector
OUTDIR = P.ROOT
_lines = []


def out(s=""):
    print(s)
    _lines.append(s)


def pf(c):
    return "PASS" if c else "FAIL"


def S(n):
    return B.doc().getObject(n).Shape


PRINTED = ["F1_PodNose", "F2_PodCentre", "F3_PodAft", "F4_NoseHatch", "F5a_SkidFront", "F5b_SkidAft"]
FUSE_PARTS = ["F1_PodNose", "F2_PodCentre", "F3_PodAft", "F5a_SkidFront", "F5b_SkidAft", "F6_FrontStop",
              "F7_Firewall", "F8_RearDowel", "F9_BandStubs"]
SKIP_RES = ("P12a_Saddle1", "P12b_Saddle2", "P12c_FrontStop")     # integrated / replaced by fuselage parts


def ovl(a, b):
    return B.ovl(a, b)          # robust (see fus_build.ovl)


def run_stage_b():
    del _lines[:]
    d = B.doc()
    out("Fuselage rev A - stage F-B check report")
    out("=" * 60)
    # validity, build volume
    out("\n1. Validity and build volume (printed parts <= %.0f mm each side)" % P.BUILD_VOL)
    for n in FUSE_PARTS + ["F4_NoseHatch"]:
        s = S(n); bb = s.BoundBox
        dims = sorted([bb.XLength, bb.YLength, bb.ZLength])
        fit = (n not in PRINTED) or dims[-1] <= P.BUILD_VOL
        out("  %-15s valid %s solids %d  size %.1f x %.1f x %.1f  %s" % (n, s.isValid(), len(s.Solids), *dims, pf(s.isValid() and fit)))
    # section 13 envelope
    out("\n2. Section 13 envelope")
    allp = Part.makeCompound([S(n) for n in ("F1_PodNose", "F2_PodCentre", "F3_PodAft")])
    zmin = min(S(n).BoundBox.ZMin for n in ("F1_PodNose", "F2_PodCentre", "F3_PodAft"))
    out("  pod Z min (without skids) %.3f (BELLY_Z %.1f) %s" % (zmin, P.BELLY_Z, pf(abs(zmin - P.BELLY_Z) < 0.01)))
    ymax = 0.0
    for n in ("F1_PodNose", "F2_PodCentre", "F3_PodAft"):
        c = B.common_robust(S(n), B.box(0, 280, -100, 100, -105.0, 50))
        if c.Volume > 1e-6:
            bb = B.mesh_bb(c)
            ymax = max(ymax, abs(bb[2]), bb[3])
    out("  outer |Y| max at X 0-280 above Z -105 (pocket region excluded) %.3f <= 55 %s" % (ymax, pf(ymax <= 55.001)))
    pk = B.common_robust(S("F2_PodCentre"), B.box(0, 175, -100, 100, -200, -105.0))
    pb = B.mesh_bb(pk)
    pkx = B.common_robust(S("F2_PodCentre"), B.box(0, 175, 55.001, 100, -200, -100.0))
    xb = B.mesh_bb(pkx) if pkx.Volume > 1e-6 else None
    out("  outer |Y| max at X 0-175 below Z -105 (D-059 pocket) %.3f; material outside |Y| 55 at X %s, Z %s (allowed bulge, wing seat unaffected)" % (
        max(abs(pb[2]), pb[3]), "%.1f..%.1f" % xb[:2] if xb else "-", "%.1f..%.1f" % xb[4:] if xb else "-"))
    hole = B.box(*P.FLOOR_HOLE_RECT[:2], *P.FLOOR_HOLE_RECT[2:], -130, -100)
    v = sum(ovl(S(n), hole) for n in FUSE_PARTS)
    out("  material inside the belly-opening prism %.3f mm3 %s" % (v, pf(v < P.OVERLAP_TOL)))
    # overlaps with the reservoir and the wing
    out("\n3. Overlap with reservoir parts (closed + open) and the wing (mm3); min distance for features")
    refs = [o for o in d.Objects if o.Name.startswith("RefRes_") and not o.Name[7:].startswith(SKIP_RES)]
    refs.append(d.getObject("Ref_Wing"))
    worst = 0.0
    for o in refs:
        tot = 0.0
        for n in FUSE_PARTS + ["F4_NoseHatch"]:
            v = ovl(S(n), o.Shape)
            if v > P.OVERLAP_TOL:
                out("  OVERLAP %-15s x %-28s %.3f mm3" % (n, o.Name, v))
            tot += v
        worst = max(worst, tot)
    out("  worst total overlap %.4f mm3 %s" % (worst, pf(worst < P.OVERLAP_TOL)))
    for n, ref in (("F2_PodCentre", "RefRes_P14_ServoArm"), ("F2_PodCentre", "RefRes_P14_Servo_MG90S"), ("F2_PodCentre", "RefRes_P1_Bottle"),
                   ("F2_PodCentre", "RefRes_P6_Flap_open"), ("F6_FrontStop", "RefRes_P1_Bottle"), ("F4_NoseHatch", "RefRes_P11f_VentFlap"),
                   ("F4_NoseHatch", "RefRes_P11d_FillCap"), ("F4_NoseHatch", "Ref_Wing"), ("F3_PodAft", "RefRes_P1c_Cap"),
                   ("F2_PodCentre", "RefRes_P13a_Strap1"), ("F2_PodCentre", "RefRes_P13b_Strap2")):
        if d.getObject(ref) is None:
            continue
        dist = S(n).distToShape(S(ref))[0]
        out("  min distance %-13s - %-26s %.2f mm" % (n, ref, dist))
    out("\n3b. Placeholders (bought parts): overlap with the pod parts and the reservoir (mm3), min distance to the reservoir")
    phs = [o for o in d.Objects if o.Name.startswith("PH_")]
    resc = [o for o in refs if o.Name.startswith("RefRes_") and getattr(o, "ResState", "closed") == "closed"]
    ph_ok = True
    for o in phs:
        v_pod = sum(ovl(o.Shape, S(n)) for n in FUSE_PARTS + ["F4_NoseHatch"])
        v_res = sum(ovl(o.Shape, r.Shape) for r in refs)
        dmin, near = 1e9, ""
        for r in resc:
            dd = o.Shape.distToShape(r.Shape)[0]
            if dd < dmin:
                dmin, near = dd, r.Name
        ok_ = v_pod < P.OVERLAP_TOL and v_res < P.OVERLAP_TOL
        ph_ok = ph_ok and ok_
        out("  %-18s overlap pod %.3f, reservoir %.3f; min distance to reservoir %.2f mm (%s) %s" % (o.Name, v_pod, v_res, dmin, near, pf(ok_)))
    out("  placeholders: %s" % pf(ph_ok))
    # arm sweep
    out("\n4. Release-servo arm sweep (+-45 deg) to the structure (>= 3 mm)")
    arm = S("RefRes_P14_ServoArm")
    ax, ay = P.SERVO_X_SHAFT, P.SERVO_Y_SHAFT
    res = {}
    for sgn in (1, -1):
        dmin = 1e9
        for a in range(0, 91, 10):
            r = arm.copy(); r.rotate(V(ax, ay, 0), V(0, 0, 1), sgn * a)
            dmin = min(dmin, r.distToShape(S("F2_PodCentre"))[0])
        res[sgn] = dmin
    out("  arm closed pose rotated 0..+90: min %.2f mm; 0..-90: min %.2f mm (the real sweep is one of them) %s" % (res[1], res[-1], pf(min(res.values()) >= 3.0)))
    # flap stop
    fc = S("RefRes_P6_Flap")
    hc = V(P.RP.HINGE_X, 0, P.RP.HINGE_Z)
    sg = -1.0          # sign of the open rotation about +Y (matches RefRes_P6_Flap_open at 150 deg)
    stop = None
    for a in range(140, 181):
        r = fc.copy(); r.rotate(hc, V(0, 1, 0), sg * a)
        if ovl(r, S("F2_PodCentre")) > P.OVERLAP_TOL:
            stop = a
            break
    r = fc.copy(); r.rotate(hc, V(0, 1, 0), sg * 150)
    out("  flap open travel: first contact with F2 at %s deg (flap stop = aft edge of the belly opening with the 1.2 mm lip); distance at 150 deg %.2f mm; water stream free from 80 deg (reservoir check) %s" % (
        stop, r.distToShape(S("F2_PodCentre"))[0], pf(stop is None or stop >= 150)))
    # lift-out sweep
    out("\n5. Reservoir lift-out +Z to %.0f in 2 mm steps (wing, hatch, straps, safety pin removed; pod parts and placeholders stay)" % P.LIFT_TRAVEL)
    mov = [S("RefRes_" + n) for n in P.MOVING_SET if n not in ("P10_SafetyPin", "P10_Flag")]
    movc = Part.makeCompound(mov)
    stay = FUSE_PARTS + [o.Name for o in d.Objects if o.Name.startswith("PH_")]
    first = None
    z = 0.0
    while z <= P.LIFT_TRAVEL and first is None:
        m = movc.translated(V(0, 0, z))
        for n in stay:
            if ovl(S(n), m) > P.OVERLAP_TOL:
                first = (z, n)
                break
        z += 2.0
    out("  first contact: %s %s" % (first if first else "none up to %.0f" % P.LIFT_TRAVEL, pf(first is None)))
    # hatch lift-off with the wing on
    out("\n6. Hatch lift-off +Z 60 with the wing on; band paths")
    wd = abs(S("F8_RearDowel").BoundBox.YMax)
    bands = []
    for s in (1, -1):
        p0 = V(P.STUB_X, s * (P.CENTRE_W + P.STUB_OUT - 2), P.STUB_Z)
        p1 = V(20.0, s * 60.0, 24.0)
        p2 = V(P.DOWEL_X, s * (wd - 2), P.DOWEL_Z)
        bands += [Part.makeLine(p0, p1), Part.makeLine(p1, V(200, s * 60, 18)), Part.makeLine(V(200, s * 60, 18), p2)]
        bands += [Part.makeLine(p0, V(60, -s * 30, 27)), Part.makeLine(V(60, -s * 30, 27), V(240, -s * 40, 8)),
                  Part.makeLine(V(240, -s * 40, 8), V(P.DOWEL_X, -s * (wd - 2), P.DOWEL_Z))]
    bc = Part.makeCompound(bands)
    h = S("F4_NoseHatch")
    hit = None
    dpath = 1e9
    for z in range(0, 61, 3):
        hz = h.translated(V(0, 0, z))
        dpath = min(dpath, bc.distToShape(hz)[0] - 1.0)
        for n in FUSE_PARTS + ["Ref_Wing"]:
            if ovl(hz, S(n)) > P.OVERLAP_TOL:
                hit = (z, n); break
        if hit:
            break
    out("  hatch first contact: %s %s" % (hit if hit else "none", pf(hit is None)))
    out("  band paths to the hatch lift path (hatch at +0..+60, 3 mm steps) %.2f mm (>= 3) %s" % (dpath, pf(dpath >= 3.0)))

    for n in ("F4_NoseHatch", "RefRes_P11d_FillCap", "F3_PodAft"):
        dd = bc.distToShape(S(n))
        pt = dd[1][0][0]
        lim = "(>= 3) " + pf(dd[0] - 1.0 >= 3.0) if n != "F3_PodAft" else "(brief item 9: aft deck to report, no limit given)"
        out("  band paths (lines; band radius 1 mm) to %-20s %.2f mm at X %.1f Y %.1f Z %.1f %s" % (n, dd[0] - 1.0, pt.x, pt.y, pt.z, lim))
    # ground
    out("\n7. Ground plane at the skids")
    zg = min(S("F5a_SkidFront").BoundBox.ZMin, S("F5b_SkidAft").BoundBox.ZMin)
    valve = [o for o in d.Objects if o.Name.startswith("RefRes_P") and not o.Name.endswith("_open") and o.Name[7:9] in ("P4", "P6", "P9", "P1")]
    vz = min(S("RefRes_" + n).BoundBox.ZMin for n in ("P4_BasePlate", "P6_Flap", "P9_ReleasePin", "P10_SafetyPin"))
    out("  skid plane Z %.2f; lowest valve part Z %.2f; clearance %.2f mm (>= 3) %s" % (zg, vz, vz - zg, pf(vz - zg >= 3.0)))
    # masses
    out("\n8. Masses (g)")
    rho_extra = {"F5a_SkidFront": ("PETG", 1.27), "F5b_SkidAft": ("PETG", 1.27), "F6_FrontStop": ("balsa", 0.12),
                 "F7_Firewall": ("ply", 0.60), "F8_RearDowel": ("birch", 0.70), "F9_BandStubs": ("carbon", 1.55)}
    tot = {k: 0.0 for k in P.RHO}
    fixed = 0.0
    for n in ("F1_PodNose", "F2_PodCentre", "F3_PodAft", "F4_NoseHatch"):
        vcm = S(n).Volume / 1000
        out("  %-15s %7.2f cm3  " % (n, vcm) + "  ".join("%s %.1f" % (k, vcm * r) for k, r in P.RHO.items()))
        for k, r in P.RHO.items():
            tot[k] += vcm * r
    for n, (mat, r) in rho_extra.items():
        m = S(n).Volume / 1000 * r
        fixed += m
        out("  %-15s %7.2f cm3  %s %.2f" % (n, S(n).Volume / 1000, mat, m))
    out("  magnets 8 x 0.42 g = 3.4 g (N35 D6x2, interp.)")
    fixed += 3.4
    for k in P.RHO:
        out("  TOTAL pod (%s) + skids, stop, firewall, dowel, stubs, magnets: %.1f g" % (k, tot[k] + fixed))
    out("  Note: the saddles are now in F2 (reservoir table P12a/b 8.78 g PETG moves to the pod).")
    open(os.path.join(OUTDIR, "check_report_stageB.txt"), "w").write("\n".join(_lines) + "\n")
