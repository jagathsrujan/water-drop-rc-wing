"""Fuselage rev B (balsa pod): checks and mass table. exec() inside FreeCAD after build_balsa.py.
Writes check_report.txt and mass_table.md in design/cad_fuselage_balsa."""
import os, sys, math, time
SCRIPTS = globals().get("BAL_SCRIPTS") or os.path.dirname(os.path.abspath(__file__))
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import bal_params as BP
FP = BP.FP
import fus_build as FB          # ovl(): overlap volume with the contact handling of rev A
import FreeCAD as App
import Part

V = App.Vector
t_start = time.time()
d = App.getDocument(BP.DOC)


def S(n):
    """shape for the geometric checks: the hole-free proxy PX_* of a hex side layer if it exists (conservative, fast)"""
    p = d.getObject("PX_" + n[3:]) if n.startswith("BS_") else None
    return (p or d.getObject(n)).Shape


SM = lambda n: d.getObject(n).Shape          # real shape (mass)
L = []


def out(s=""):
    print(s)
    L.append(s)


def pf(b):
    return "PASS" if b else "FAIL"


TOL = FP.OVERLAP_TOL
POD = [o.Name for o in d.Objects if o.Name.startswith("BS_")]
EXCL = {"RefRes_P12a_Saddle1", "RefRes_P12b_Saddle2", "RefRes_P12c_FrontStop"}      # now pod parts (BS_Saddles, BS_FrontStop)
RES = [o.Name for o in d.Objects if o.Name.startswith("RefRes_") and getattr(o, "ResState", "closed") == "closed" and o.Name not in EXCL]
PH = [o.Name for o in d.Objects if o.Name.startswith("PH_")]
TAIL = [o.Name for o in d.Objects if o.Name[:3] in ("F10", "F11", "F12", "F13", "F14", "F15", "F16", "F17", "F18", "F19")]
results = {}

out("Fuselage rev B (balsa pod) - check report  (%s)" % time.strftime("%Y-%m-%d %H:%M"))
out("Frame: wing frame, origin wing LE on the centreline, X aft, Y right, Z up, mm. Model: %s" % BP.FCSTD)
out("Reference bodies copied from %s (reservoir, wing rev A, tail, electronics placeholders)." % FP.FCSTD)

out("\n1. Validity")
okv = True
for n in POD:
    s = SM(n)
    okv = okv and s.isValid()
    bb = s.BoundBox
    out("  %-20s valid %s solids %d  X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f" % (n, s.isValid(), len(s.Solids), bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))
results["1 validity"] = okv
out("  " + pf(okv))

out("\n2. Section 13 envelope")
zmin = min(S(n).BoundBox.ZMin for n in POD if n != "BS_Skids")
out("  belly Z min (without skids) %.3f (BELLY_Z %.1f) %s" % (zmin, FP.BELLY_Z, pf(abs(zmin - FP.BELLY_Z) < 0.01)))
pod_all = Part.makeCompound([S(n) for n in POD if n not in ("BS_BandStubs", "BS_RearDowel")])
sl = pod_all.common(FB.box(0, 280, -200, 200, -105, 50))
ymax = max(abs(sl.BoundBox.YMin), abs(sl.BoundBox.YMax))
out("  outer |Y| max at X 0-280 above Z -105 (pocket below) %.3f <= %.1f %s" % (ymax, FP.Y_LIMIT, pf(ymax <= FP.Y_LIMIT + 1e-3)))
fr = FP.FLOOR_HOLE_RECT
vh = sum(S(n).common(FB.box(fr[0], fr[1], fr[2], fr[3], -140, -100)).Volume for n in POD)
out("  material inside the belly-opening prism %.3f mm3 %s" % (vh, pf(vh < TOL)))
rs = Part.makeCompound([S(n) for n in POD if n.startswith("BS_SideR")]).common(FB.box(50, 90, 0, 200, -105, -10))
wi = rs.BoundBox.YMin
out("  right side inner face Y %.2f at X 50-90 (>= %.1f) %s" % (wi, FP.SERVO_WALL_INNER_MIN, pf(wi >= FP.SERVO_WALL_INNER_MIN - 1e-6)))
ftop = S("BS_Floor").common(FB.box(-20, 190, -40, 40, -130, -100)).BoundBox.ZMax      # flat floor between the kinks
out("  floor top under the saddles Z %.3f (FLOOR_Z %.1f) %s" % (ftop, FP.FLOOR_Z, pf(abs(ftop - FP.FLOOR_Z) < 0.01)))
results["2 envelope"] = (abs(zmin - FP.BELLY_Z) < 0.01 and ymax <= FP.Y_LIMIT + 1e-3 and vh < TOL and abs(ftop - FP.FLOOR_Z) < 0.01
                         and wi >= FP.SERVO_WALL_INNER_MIN - 1e-6)

out("\n3. Overlaps (mm3; glued contacts are 0)")
worst, worst_pair, flagged = 0.0, "", []
groups = [("pod-pod", [(a, b) for i, a in enumerate(POD) for b in POD[i + 1:]]),
          ("pod-reservoir", [(a, b) for a in POD for b in RES]),
          ("pod-placeholders", [(a, b) for a in POD for b in PH]),
          ("pod-tail", [(a, b) for a in POD for b in TAIL]),
          ("pod-wing", [(a, "Ref_WingRevA") for a in POD]),
          ("placeholders-reservoir", [(a, b) for a in PH for b in RES])]
for gname, pairs in groups:
    gw, gp = 0.0, ""
    for a, b in pairs:
        if (a, b) in (("BS_SocketBlock", "F10_Tubes"),):
            pass
        v = FB.ovl(S(a), S(b))
        if v > TOL:
            flagged.append("%s / %s %.3f" % (a, b, v))
        if v > gw:
            gw, gp = v, "%s / %s" % (a, b)
    out("  %-24s worst %.4f %s" % (gname, gw, gp))
    if gw > worst:
        worst, worst_pair = gw, gp
for f in flagged:
    out("    overlap: " + f)
results["3 overlaps"] = worst < TOL
out("  worst overlap %.4f mm3 %s" % (worst, pf(worst < TOL)))

out("\n4. Release-servo arm sweep (+-90 deg about the shaft) to the pod (>= 3 mm)")
arm = S("RefRes_P14_ServoArm")
ax, ay = FP.SERVO_X_SHAFT, FP.SERVO_Y_SHAFT
near = [n for n in ("BS_SideR_Outer", "BS_SideR_Inner", "BS_ServoPocketMount", "BS_Floor", "BS_Longerons", "BS_FlapStop", "BS_Keels")
        if d.getObject(n)]
res4 = {}
for sgn in (1, -1):
    dmin = 1e9
    for a in range(0, 91, 10):
        r = arm.copy()
        r.rotate(V(ax, ay, 0), V(0, 0, 1), sgn * a)
        for n in near:
            dmin = min(dmin, r.distToShape(S(n))[0])
    res4[sgn] = dmin
out("  0..+90: min %.2f mm; 0..-90: min %.2f mm (the real sweep is one of them)" % (res4[1], res4[-1]))
results["4 servo arm"] = max(res4.values()) >= 3.0
out("  " + pf(results["4 servo arm"]))

out("\n5. Release flap: open travel about the hinge pin (first contact with the pod)")
hp = S("RefRes_P8_HingePin").BoundBox
hc = V(hp.Center.x, 0, hp.Center.z)
flap, flap_open = S("RefRes_P6_Flap"), S("RefRes_P6_Flap_open").BoundBox
sgn5 = 1
for sg in (1, -1):
    r = flap.copy()
    r.rotate(hc, V(0, 1, 0), sg * 150)
    if abs(r.BoundBox.ZMin - flap_open.ZMin) < 3 and abs(r.BoundBox.XMax - flap_open.XMax) < 3:
        sgn5 = sg
pod_near = [S(n) for n in ("BS_Floor", "BS_FlapStop", "BS_Skids", "BS_Longerons", "BS_SaddlePly", "BS_SaddleBalsa", "BS_Keels", "BS_FrameB2")
            if d.getObject(n)]
first, d150 = None, None
for a in list(range(0, 140, 10)) + list(range(140, 181)):
    r = flap.copy()
    r.rotate(hc, V(0, 1, 0), sgn5 * a)
    dd = min(r.distToShape(p)[0] for p in pod_near)
    if a == 150:
        d150 = dd
    if dd < 1e-3 and first is None and a > 0:
        first = a
        break
out("  hinge X %.1f Z %.1f; distance at 150 deg %s mm; first contact %s deg" % (hc.x, hc.z, "%.2f" % d150 if d150 is not None else "-", first))
results["5 flap"] = (d150 is not None and d150 > 0.5) or (first is not None and first >= 150)
out("  " + pf(results["5 flap"]) + " (water stream free from 80 deg: reservoir check)")

out("\n6. Reservoir lift-out +Z to %.0f in %.0f mm steps (wing, hatch, straps, safety pin + flag removed: D-058; pod parts and placeholders stay)" % (BP.LIFT_TRAVEL, BP.LIFT_STEP))
moving = [o.Name for o in d.Objects if o.Name.startswith("RefRes_") and getattr(o, "MovingSet", False)
          and getattr(o, "ResState", "closed") == "closed" and o.Name not in EXCL
          and not o.Name.startswith(("RefRes_P10", "RefRes_P13"))]
stay = [n for n in POD if n != "BS_Hatch"] + PH
out("  moving set: " + ", ".join(m.replace("RefRes_", "") for m in moving))
mv = [S(m) for m in moving]
contact = None
dz = BP.LIFT_STEP
while dz <= BP.LIFT_TRAVEL + 1e-6 and contact is None:
    for m, s in zip(moving, mv):
        sm = s.translated(V(0, 0, dz))
        for n in stay:
            if FB.ovl(sm, S(n)) > TOL:
                contact = (dz, m, n)
                break
        if contact:
            break
    dz += BP.LIFT_STEP
out("  first contact: %s" % ("none up to %.0f" % BP.LIFT_TRAVEL if contact is None else "dz %.0f %s / %s" % contact))
results["6 lift-out"] = contact is None
out("  " + pf(contact is None))

out("\n7. Hatch lift-off +Z 0..60 (3 mm steps) with the wing on")
hat = S("BS_Hatch")
others = [n for n in POD if n != "BS_Hatch"] + RES + PH + ["Ref_WingRevA"]
hc_ = None
for k in range(1, 21):
    hs = hat.translated(V(0, 0, 3.0 * k))
    for n in others:
        if FB.ovl(hs, S(n)) > TOL:
            hc_ = (3.0 * k, n)
            break
    if hc_:
        break
dw = hat.distToShape(S("Ref_WingRevA"))[0]
dcap = hat.distToShape(S("RefRes_P11d_FillCap"))[0]
out("  first contact: %s; hatch - wing %.2f mm; hatch - fill cap %.2f mm (>= 1)" % ("none" if hc_ is None else "dz %.0f %s" % hc_, dw, dcap))
results["7 hatch"] = hc_ is None and dw >= 1.0 and dcap >= 1.0
out("  " + pf(results["7 hatch"]))

out("\n8. Wing seat (1.0 mm foam tape by design)")
wing = S("Ref_WingRevA")
for n in ("BS_SideR_Outer", "BS_SideL_Outer", "BS_SideR_Inner", "BS_SeatCapstrip", "BS_AftDeck", "BS_SaddlePly", "BS_FrontStop", "BS_FrameB1"):
    out("  wing - %-16s %.2f mm" % (n, wing.distToShape(S(n))[0]))

out("\n9. Ground: skid plane and the lowest valve part (section 13 check 11: >= 3 mm)")
zsk = S("BS_Skids").BoundBox.ZMin
zv = min(S(n).BoundBox.ZMin for n in ("RefRes_P4_BasePlate", "RefRes_P6_Flap", "RefRes_P7_FlapGasket"))
out("  skid plane Z %.2f; lowest valve part Z %.2f; clearance %.2f %s" % (zsk, zv, zv - zsk, pf(zv - zsk >= 3.0)))
results["9 ground"] = zv - zsk >= 3.0
pz_ = S("PH_PropDisc").BoundBox.ZMin
out("  prop disc lowest Z %.1f: %.1f mm below the skid plane (fixed prop, D-066)" % (pz_, zsk - pz_))

out("\n10. Pushrods to the pod (>= 2 mm; exit slots D4 in the aft side panels by design)")
rods = S("F18_Pushrods")
pm = 1e9
for n in POD:
    dd = rods.distToShape(S(n))[0]
    tag = " (exit slot)" if (n.startswith("BS_Side") or n == "BS_TailNode") else ""
    out("  pushrods - %-20s %.2f mm%s" % (n, dd, tag))
    if not tag:
        pm = min(pm, dd)
results["10 pushrods"] = pm >= 2.0
out("  minimum without the exit slots %.2f %s" % (pm, pf(pm >= 2.0)))

tb_ = S("F10_Tubes").BoundBox
x_sup0, x_sup1 = BP.AFT_KINK, BP.END_X[1]
out("  tubes X %.1f..%.1f; glued in the bulkhead (X %.1f) and the end former (to X %.1f): support span %.1f mm (rev A socket 70)" % (
    tb_.XMin, tb_.XMax, x_sup0, x_sup1, x_sup1 - x_sup0))

out("\n11. Part sizes (laser bed / print volume)")
for n in POD:
    bb = S(n).BoundBox
    out("  %-20s %.0f x %.0f x %.0f" % (n, bb.XLength, bb.YLength, bb.ZLength))

# ---------------- mass table ----------------
out("\n12. Mass table")
rows = []
wood = 0.0
film_area = 0.0
for n in POD:
    o = d.getObject(n)
    mat = o.Material
    v = SM(n).Volume / 1000.0
    m = v * BP.RHO[mat]
    if mat.startswith("balsa") or mat in ("ply", "liteply", "birch"):
        wood += m
    if n in ("BS_SideR_Outer", "BS_SideL_Outer", "BS_Floor", "BS_Hatch", "BS_AftDeck"):
        film_area += SM(n).Volume / {"BS_Hatch": BP.T_HATCH, "BS_AftDeck": BP.T_DECK, "BS_Floor": BP.T_FLOOR}.get(n, BP.T_SIDE_OUT) / 1e6
    rows.append((n, mat, v, m, o.Note))
hex_area = float(d.getObject("BS_SideR_Outer").HexArea_mm2) / 1e6
film_area += 2 * hex_area          # outer film over the holes + inner film over the holes (spill water stays out)
film = film_area * BP.FILM_G_M2
out("  hex holes: %.4f m2 of side panel removed (both sides)" % hex_area)
glue = wood * BP.GLUE_FRAC
total = sum(r[3] for r in rows) + film + glue + BP.MAGNETS_G
for r in rows:
    out("  %-20s %-11s %7.2f cm3 %7.2f g  %s" % r)
out("  covering film %.3f m2 x %.0f g/m2 = %.2f g; glue + CA sealing %.0f %% of wood %.2f g = %.2f g; magnets %.2f g" % (
    film_area, BP.FILM_G_M2, film, BP.GLUE_FRAC * 100, wood, glue, BP.MAGNETS_G))
out("  TOTAL balsa pod (same scope as the rev A pod total: skin, formers, hard points, saddles, sockets, skids, stubs, dowel, magnets): %.1f g" % total)
REVA_ASA, REVA_PLA, EMPTY_ASA = 120.9, 211.3, 676.9     # rev A stage F-B report and the empty-mass roll-up (2026-11-23)
empty = EMPTY_ASA - REVA_ASA + total
loaded = empty + 996.0
vs = math.sqrt(2 * loaded / 1000 * 9.81 / (1.05 * 0.2772 * 1.35))
out("  rev A pod: %.1f g ASA Aero 0.65 / %.1f g PLA -> balsa saves %.1f g / %.1f g" % (REVA_ASA, REVA_PLA, REVA_ASA - total, REVA_PLA - total))
out("  empty aircraft %.0f g (rev A ASA Aero %.0f g); loaded %.0f g; score %.1f; loaded stall at rho 1.05, CLmax 1.35: %.2f m/s (R6 <= 9.0)" % (
    empty, EMPTY_ASA, loaded, 99600.0 / empty, vs))
out("  (receiver 8 g and wiring 15 g are estimates; tail, wing, reservoir and electronics as rev A / D-066)")

out("\nSummary")
for k, v in results.items():
    out("  %-14s %s" % (k, pf(v)))
out("check time %.0f s" % (time.time() - t_start))
open(os.path.join(BP.ROOT, "check_report.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")

md = ["# Fuselage rev B (balsa pod) — mass table", "",
      "Generated by `scripts/check_balsa.py`. Densities *(interp.)*: medium balsa %.2f, light balsa %.2f, birch ply %.2f, lite-ply %.2f, PETG %.2f, carbon %.2f, birch dowel %.2f g/cm³. Weigh the sheets and update `bal_params.RHO`." % (
          BP.RHO["balsa_med"], BP.RHO["balsa_light"], BP.RHO["ply"], BP.RHO["liteply"], BP.RHO["petg"], BP.RHO["carbon"], BP.RHO["birch"]), "",
      "| Part | Material | Volume cm³ | Mass g | Note |", "|---|---|---|---|---|"]
for n, mat, v, m, note in rows:
    md.append("| %s | %s | %.2f | %.2f | %s |" % (n, mat, v, m, note))
md += ["| Covering film | %.0f g/m² | — | %.2f | %.3f m² outer skin |" % (BP.FILM_G_M2, film, film_area),
       "| Glue + CA sealing | %.0f %% of wood | — | %.2f | |" % (BP.GLUE_FRAC * 100, glue),
       "| Magnets | 4 pairs D6×2 | — | %.2f | |" % BP.MAGNETS_G,
       "| **Total balsa pod** | | | **%.1f** | rev A pod: %.1f g ASA Aero / %.1f g PLA |" % (total, REVA_ASA, REVA_PLA), "",
       "Empty aircraft ≈ **%.0f g**, loaded ≈ **%.0f g**, score ≈ **%.1f**, loaded stall (Bengaluru) ≈ %.2f m/s." % (empty, loaded, 99600.0 / empty, vs)]
open(os.path.join(BP.ROOT, "mass_table.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
print("check done")
