"""Stage F-C checks (tail). Writes check_report_stageC.txt. Call run_stage_c() inside FreeCAD after build_stageC."""
import os, sys, math, itertools
import FreeCAD as App
import Part
import fus_params as P
import fus_build as B

V = App.Vector
OUTDIR = P.ROOT
CALC = os.path.join(os.path.dirname(P.ROOT), "calc")
if CALC not in sys.path:
    sys.path.insert(0, CALC)
import fuselage_sizing as FS

_lines = []
TAIL = ["F10_Tubes", "F11_TailBlock", "F12_Stab", "F13_Elevator", "F14_Fin", "F15_Rudder", "F16_Joiner", "F17_Horns",
        "F18_Pushrods", "F19_GuideClips"]
POD = ["F1_PodNose", "F2_PodCentre", "F3_PodAft", "F4_NoseHatch", "F5a_SkidFront", "F5b_SkidAft", "F6_FrontStop",
       "F7_Firewall", "F8_RearDowel", "F9_BandStubs"]
# contacts by design (glued, embedded or attached): pairs excluded from the overlap test
CONTACT = {("F13_Elevator", "F16_Joiner"), ("F17_Horns", "F18_Pushrods"), ("F18_Pushrods", "PH_TailServoArms"),
           ("F12_Stab", "F14_Fin"), ("F13_Elevator", "F17_Horns"), ("F15_Rudder", "F17_Horns")}


def out(s=""):
    print(s)
    _lines.append(s)


def pf(c):
    return "PASS" if c else "FAIL"


def S(n):
    return B.doc().getObject(n).Shape


def ovl(a, b):
    return B.ovl(a, b)          # robust (see fus_build.ovl)


def rot(shape, c, ax, deg):
    r = shape.copy()
    r.rotate(c, ax, deg)
    return r


def run_stage_c():
    del _lines[:]
    d = B.doc()
    out("Fuselage rev A - stage F-C check report (tail)")
    out("=" * 60)
    out("\n1. Validity")
    allok = True
    for n in TAIL:
        s = S(n)
        bb = B.mesh_bb(s)
        allok &= s.isValid()
        out("  %-16s valid %s solids %d  X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f" % (n, s.isValid(), len(s.Solids), *bb))
    out("  all valid %s" % pf(allok))

    out("\n2. Overlaps (mm3): tail parts with each other, with the pod parts, the reservoir (closed), the wing and the placeholders")
    others = POD + [o.Name for o in d.Objects if (o.Name.startswith("RefRes_") and getattr(o, "ResState", "closed") == "closed")
                    or o.Name.startswith("PH_") or o.Name == "Ref_Wing"]
    worst = 0.0
    for a, b in list(itertools.combinations(TAIL, 2)) + [(a, b) for a in TAIL for b in others]:
        if (a, b) in CONTACT or (b, a) in CONTACT:
            continue
        v = ovl(S(a), S(b))
        if v > P.OVERLAP_TOL:
            out("  OVERLAP %-16s x %-26s %.3f" % (a, b, v))
        worst = max(worst, v)
    out("  worst overlap %.4f mm3 %s (contacts by design not tested: %s)" % (worst, pf(worst < P.OVERLAP_TOL),
        ", ".join("%s/%s" % p for p in sorted(CONTACT))))

    out("\n3. Pushrods: clearance to the structure (key check 9: >= 2 mm; exit slots in F3 by design)")
    rods = S("F18_Pushrods")
    pmin = 1e9
    for n in ("F10_Tubes", "F11_TailBlock", "F12_Stab", "F14_Fin", "F15_Rudder", "F13_Elevator", "F8_RearDowel", "F3_PodAft",
              "PH_TailServo_R", "PH_TailServo_L", "RefRes_P1c_Cap", "RefRes_P1_Bottle"):
        if d.getObject(n) is None:
            continue
        dd = rods.distToShape(S(n))
        p = dd[1][0][0]
        lim = n not in ("F3_PodAft",)
        if lim:
            pmin = min(pmin, dd[0])
        out("  pushrods - %-18s %6.2f mm at X %.1f Y %.1f Z %.1f%s" % (n, dd[0], p.x, p.y, p.z, "" if lim else " (exit slot r 2.0 round the r 1.0 rod)"))
    out("  minimum (without the F3 exit slots) %.2f mm %s" % (pmin, pf(pmin >= 2.0)))
    out("  pushrod lengths: " + ", ".join("%.0f mm" % (so.Volume / (math.pi * (P.PUSHROD_D / 2) ** 2)) for so in rods.Solids)
        + "; guides at X " + ", ".join("%.0f" % g for g in P.GUIDE_X))

    out("\n4. Control surface travel (elevator +-20 deg, rudder +-25 deg, and the 4 combinations)")
    hx, hz = P.HINGE_X, P.STAB_Z
    el, ru, hn, jn = S("F13_Elevator"), S("F15_Rudder"), S("F17_Horns"), S("F16_Joiner")
    eh = hn.Solids[0] if hn.Solids[0].BoundBox.YMax < 0 else hn.Solids[1]
    rh = hn.Solids[0] if hn.Solids[0].BoundBox.YMax > 0 else hn.Solids[1]     # (Solids gives new objects: no 'is')
    fixed = []
    for n in ("F12_Stab", "F14_Fin", "F11_TailBlock", "F10_Tubes"):
        fixed += list(S(n).Solids)
    worst_t = 1e9
    for ae in (-20, 0, 20):
        for ar in (-25, 0, 25):
            # single solids only (booleans and distances on nested compounds gave false contacts)
            e_m = [rot(x, V(hx, 0, hz), V(0, 1, 0), ae) for x in list(el.Solids) + [eh] + list(jn.Solids)]
            r_m = [rot(x, V(hx, 0, 0), V(0, 0, 1), ar) for x in list(ru.Solids) + [rh]]
            v = sum(ovl(a, b) for a in e_m + r_m for b in fixed) + sum(ovl(a, b) for a in e_m for b in r_m)
            d_er = min(a.distToShape(b)[0] for a in e_m for b in r_m)
            d_ef = min(a.distToShape(b)[0] for a in e_m for b in fixed if a.BoundBox.intersect(b.BoundBox) or True)
            d_rf = min(a.distToShape(b)[0] for a in r_m for b in fixed)
            worst_t = min(worst_t, -v if v > P.OVERLAP_TOL else 0.0)
            out("  elevator %+3d, rudder %+3d: overlap %.3f mm3; elevator-rudder %.2f mm, elevator-fixed %.2f mm, rudder-fixed %.2f mm" % (
                ae, ar, v, d_er, d_ef, d_rf))
    rj = ru.distToShape(jn)[0]
    out("  joiner in the rudder LE notch: %.2f mm (neutral) %s" % (rj, pf(rj >= 0.5)))
    out("  travel without contact %s" % pf(worst_t >= 0))

    out("\n5. Tail volumes and static margin (wing S %.4f m2, c %.3f m, b %.3f m; CG X %.0f)" % (FS.S, FS.c, FS.b, FS.X_CG_TARGET))
    Sh = P.STAB_C * 2 * P.STAB_HS / 1e6
    ARh = (2 * P.STAB_HS) ** 2 / (Sh * 1e6)
    xac_h = P.STAB_LE_X + 0.25 * P.STAB_C
    cr, ct, h = P.FIN_CR, P.FIN_CT, P.FIN_TIP_Z - P.FIN_ROOT_Z
    Sv = 0.5 * (cr + ct) * h / 1e6
    mac = 2.0 / 3.0 * (cr + ct - cr * ct / (cr + ct))
    zmac = h / 3.0 * (cr + 2 * ct) / (cr + ct)
    le_root = P.HINGE_X - 0.25 - 0.65 * cr
    le_tip = P.HINGE_X - 0.25 - 0.65 * ct
    xac_v = le_root + (le_tip - le_root) * zmac / h + 0.25 * mac
    lh, lv = (xac_h - FS.X_CG_TARGET) / 1000, (xac_v - FS.X_CG_TARGET) / 1000
    Vh = Sh * lh / (FS.S * FS.c)
    Vv = Sv * lv / (FS.S * FS.b)
    out("  Sh %.3f dm2 (incl. elevator), AR %.2f, tail AC X %.1f, l_h %.0f mm -> Vh %.3f (>= 0.50) %s" % (Sh * 100, ARh, xac_h, lh * 1000, Vh, pf(Vh >= 0.4995)))
    out("  Sv %.3f dm2 (fin above the plate, incl. rudder), fin AC X %.1f, l_v %.0f mm -> Vv %.4f (>= 0.035) %s" % (Sv * 100, xac_v, lv * 1000, Vv, pf(Vv >= 0.035)))
    sm_min = 1e9
    for de in (0.45, 0.55, 0.65):
        np_, _ = FS.neutral_point(lh * 1000, Vh, AR_h=ARh, deps=de)
        sm = (np_ - FS.X_CG_TARGET) / (FS.c * 10)
        sm_min = min(sm_min, sm)
        out("  downwash gradient %.2f: NP X %.1f, SM %.1f %%" % (de, np_, sm))
    out("  SM at downwash 0.65 >= 7 %% %s (final CG from F-D)" % pf(sm_min >= 7.0))

    out("\n6. Stabilizer and the wing wake (key check 13: >= 15 mm; wake centre-line at X 680, fuselage_sizing.wake_z)")
    cases = [("loaded 10 m/s", 12.7), ("loaded 12", 7.6), ("loaded 15", 3.6), ("empty 12", 0.7), ("empty 18", -1.8), ("wing stall", 20.0)]
    zs0, zs1 = P.STAB_Z - P.T_SURF / 2, P.STAB_Z + P.T_SURF / 2
    wmin = 1e9
    for nm, a in cases:
        row = []
        for de in (0.45, 0.55, 0.65):
            zw = FS.wake_z(a, de)
            dist = zs0 - zw if zw < zs0 else (zw - zs1 if zw > zs1 else 0.0)
            wmin = min(wmin, dist)
            row.append("%6.1f (%.0f)" % (zw, dist))
        out("  %-14s alpha %5.1f: wake Z (stab distance) %s" % (nm, a, " | ".join(row)))
    out("  minimum distance stab - wake centre-line %.1f mm %s" % (wmin, pf(wmin >= 15.0)))

    out("\n7. Tubes")
    tb = S("F10_Tubes").BoundBox
    out("  tube X %.1f..%.1f (length %.1f); in the pod sockets %.1f mm (>= 70) %s; in the tail-block collars %.1f mm (>= 40) %s" % (
        tb.XMin, tb.XMax, tb.XLength, P.SOCK_X0 + P.SOCK_WALL + P.SOCK_DEPTH - P.TUBE_X[0], pf(P.SOCK_X0 + P.SOCK_WALL + P.SOCK_DEPTH - P.TUBE_X[0] >= 69.99),
        P.TUBE_X[1] - P.TB_COLLAR_X[0], pf(P.TUBE_X[1] - P.TB_COLLAR_X[0] >= 40.0)))

    out("\n8. Ground at a nose-up touchdown on the aft belly corner (X 200, Z -117)")
    tail_c = Part.makeCompound([S(n) for n in TAIL if n not in ("F18_Pushrods",)])
    for th in (6, 8, 10, 12):
        a = math.radians(th)
        n = V(-math.sin(a), 0, math.cos(a))                     # ground plane normal (body frame), through (200, 0, -117)
        pts, _ = tail_c.tessellate(0.5)
        dmin = min((p - V(200, 0, -117)).dot(n) for p in pts if p.x > 300)
        out("  %2d deg nose-up: lowest tail point %.1f mm above the ground %s" % (th, dmin, "(contact)" if dmin < 0 else ""))

    out("\n10. Wing rev A in the assembly (W_* parts, +%.1f deg): overlap with every fuselage and tail part, the placeholders and the reservoir (closed)" % P.WING_INCIDENCE)
    wparts = [o for o in d.Objects if o.Name.startswith("W_")]
    if not wparts:
        out("  no W_ parts (build_wing_asm.py not run)")
    else:
        W = Part.makeCompound([o.Shape for o in wparts])
        wb = W.BoundBox
        out("  %d parts, X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f" % (len(wparts), wb.XMin, wb.XMax, wb.YMin, wb.YMax, wb.ZMin, wb.ZMax))
        tgt = POD + TAIL + [o.Name for o in d.Objects if o.Name.startswith("PH_") or (o.Name.startswith("RefRes_") and getattr(o, "ResState", "closed") == "closed")]
        wworst = 0.0
        for n in tgt:
            sh = S(n)
            if not sh.BoundBox.intersect(wb):
                continue
            v = sum(B.ovl(sh, w.Shape) for w in wparts if sh.BoundBox.intersect(w.Shape.BoundBox))
            if v > P.OVERLAP_TOL:
                out("  OVERLAP wing x %-22s %.3f mm3" % (n, v))
            wworst = max(wworst, v)
        out("  worst overlap %.4f mm3 %s" % (wworst, pf(wworst < P.OVERLAP_TOL)))
        for n in ("F2_PodCentre", "F3_PodAft", "F4_NoseHatch", "F9_BandStubs", "F8_RearDowel", "RefRes_P11d_FillCap", "F12_Stab", "F14_Fin"):
            dd = W.distToShape(S(n))
            p = dd[1][0][0]
            out("  min distance wing - %-20s %6.2f mm at X %.1f Y %.1f Z %.1f" % (n, dd[0], p.x, p.y, p.z))
        out("  (wing seat: 1.0 mm foam tape between the side-wall tops and the wing lower surface by design)")

    out("\n9. Masses (g)")
    rho = {"F10_Tubes": ("carbon", P.RHO_CARBON), "F11_TailBlock": ("PETG", P.RHO_PETG), "F12_Stab": ("balsa", P.RHO_BALSA),
           "F13_Elevator": ("balsa", P.RHO_BALSA), "F14_Fin": ("balsa", P.RHO_BALSA), "F15_Rudder": ("balsa", P.RHO_BALSA),
           "F16_Joiner": ("steel", P.RHO_STEEL), "F17_Horns": ("G10 1.85", 1.85), "F18_Pushrods": ("carbon", P.RHO_CARBON),
           "F19_GuideClips": ("PETG", P.RHO_PETG)}
    tot = 0.0
    for n, (mat, r) in rho.items():
        m = S(n).Volume / 1000 * r
        tot += m
        out("  %-16s %7.2f cm3  %-8s %6.2f" % (n, S(n).Volume / 1000, mat, m))
    film = P.FILM_G_M2 * 2 * (Sh + Sv)
    ends = 4 * 0.4
    out("  covering film %.0f g/m2 x 2 sides x (Sh + Sv) %.2f; pushrod steel ends 4 x 0.4 = %.1f (interp.)" % (P.FILM_G_M2, film, ends))
    tot += film + ends
    out("  TOTAL tail (F10-F19 + film + rod ends): %.1f g (plan: tubes 33 + surfaces 25.5 + block 8 + pushrods 7 = 73.5 g)" % tot)
    out("  without the tubes and the pushrods (surfaces, joiner, horns, film): %.1f g (D-055 estimate 14 g)" % (
        sum(S(n).Volume / 1000 * rho[n][1] for n in ("F12_Stab", "F13_Elevator", "F14_Fin", "F15_Rudder", "F16_Joiner", "F17_Horns")) + film))
    open(os.path.join(OUTDIR, "check_report_stageC.txt"), "w").write("\n".join(_lines) + "\n")
