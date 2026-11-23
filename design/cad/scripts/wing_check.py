"""Wing rev A - key checks, overlap test, mass table. Run inside FreeCAD after the build scripts.
Writes design/cad/check_report.txt and design/cad/mass_table.csv."""
import sys, os, itertools, importlib
SCRIPTS = globals().get("WING_SCRIPTS") or os.environ.get("WING_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import wing_params as P, wing_geom as G, wing_build as B
import FreeCAD as App

EXTRA_G = {}      # name -> grams for parts not modelled as solids (filled by stage scripts if needed)
INFILL = {}       # name -> infill factor for petg parts (set by build_stageB)


def parts(d):
    return [o for o in d.Objects if o.TypeId == "Part::Feature" and hasattr(o, "Material")]


def overlap_check(objs, tol_mm3=1.0, skip_pairs=()):
    sol = []
    for o in objs:
        for i, s in enumerate(o.Shape.Solids):
            bb = s.BoundBox
            bb.enlarge(-0.01)
            sol.append((o.Name, i, s, bb))
    bad, n = [], 0
    for (na, ia, sa, ba), (nb, ib, sb, bbx) in itertools.combinations(sol, 2):
        if na == nb or not ba.intersect(bbx):
            continue
        if (na, nb) in skip_pairs or (nb, na) in skip_pairs:
            continue
        n += 1
        v = sa.common(sb).Volume
        if v > tol_mm3:
            bad.append((na, ia, nb, ib, round(v, 2)))
    return bad, n


def film_area_m2():
    per = G.OUTER().Wires[0].Length          # mm
    return (per * 2 * P.HALF_SPAN + 2 * G.OUTER().Area) * 1e-6


def mass_table(objs):
    rows = []
    for o in objs:
        if o.Material in ("servo",):
            continue
        rho = P.RHO[o.Material]
        f = INFILL.get(o.Name, 1.0) if o.Material == "petg" else 1.0
        v = o.Shape.Volume
        rows.append((o.Name, o.Material, rho, f, v / 1000.0, v * rho * f * 1e-6))
    film = film_area_m2() * P.FILM_GSM
    rows.append(("Film (covering)", "film", P.FILM_GSM, 1.0, 0.0, film))
    rows.append(("Glue (estimate)", "glue", 0, 1.0, 0.0, P.GLUE_G))
    for k, g in EXTRA_G.items():
        rows.append((k, "extra", 0, 1.0, 0.0, g))
    return rows


def run(stage="A"):
    d = B.doc()
    objs = parts(d)
    out = []
    pr = lambda *a: out.append(" ".join(str(x) for x in a))
    wing = [o for o in objs if o.Material != "servo"]
    bb = wing[0].Shape.BoundBox
    for o in wing[1:]:
        bb.add(o.Shape.BoundBox)
    pr("=== Wing rev A check, stage", stage, "===")
    pr("parts:", len(objs), " solids:", sum(len(o.Shape.Solids) for o in objs))
    inv = [o.Name for o in objs if not o.Shape.isValid()]
    pr("1 span (Y extent) = %.2f mm  [req 990.0, <= 1000]" % bb.YLength)
    st = [o for o in wing if not o.Name.startswith("RubPlate")]
    bs = st[0].Shape.BoundBox
    for o in st[1:]:
        bs.add(o.Shape.BoundBox)
    pr("  chord (X extent of structure, rub plates excluded) = %.2f mm  [req 280.0]  XMin %.3f XMax %.3f" % (bs.XLength, bs.XMin, bs.XMax))
    if bb.XLength > bs.XLength + 0.01:
        pr("  with the band rub plates (outside the film): X extent %.2f mm" % bb.XLength)
    pr("  dihedral 0: all parts symmetric about y = 0, chord line z = 0 along span (by construction)")
    pr("2 depth at x = 75.6 (outer) = %.2f mm  [plan 39.1]" % G.depth(75.6))
    zt = G.inner_z_range(*P.X_SPAR, True); zb = G.inner_z_range(*P.X_SPAR, False)
    gt = max(G.surf_z(x, True, G.INNER()) - zt for x in (72.6, 74.1, 75.6, 77.1, 78.6))
    gb = max(zb - G.surf_z(x, False, G.INNER()) for x in (72.6, 74.1, 75.6, 77.1, 78.6))
    pr("3 spar: carbon top face z = %.3f, bottom face z = %.3f; max gap to sheeting top %.2f mm, bottom %.2f mm" % (zt, zb, gt, gb))
    pr("  spar cap outer-to-outer depth = %.2f mm" % (zt - zb))
    pr("6 invalid solids:", inv if inv else "none")
    bad, n = overlap_check(objs)
    pr("  overlap test: %d solid pairs with touching/overlapping boxes tested; overlaps > 1 mm3: %d" % (n, len(bad)))
    for b in bad:
        pr("   OVERLAP", b)
    rows = mass_table(objs)
    tot = sum(r[5] for r in rows)
    pr("7 wing mass without servos = %.1f g  [no fixed limit, D-047]" % tot)
    by = {}
    for r in rows:
        by[r[1]] = by.get(r[1], 0.0) + r[5]
    for k, v in sorted(by.items(), key=lambda kv: -kv[1]):
        pr("   %-8s %6.1f g" % (k, v))
    txt = "\n".join(out)
    open(os.path.join(P.CAD, "check_report_stage%s.txt" % stage), "w").write(txt)
    with open(os.path.join(P.CAD, "mass_table_stage%s.csv" % stage), "w") as f:
        f.write("part,material,density_kg_m3_or_gsm,infill,volume_cm3,mass_g\n")
        for r in rows:
            f.write("%s,%s,%.0f,%.2f,%.3f,%.2f\n" % r)
        f.write("TOTAL,,,,,%.1f\n" % tot)
    print(txt)
    return bad, tot


def stage_b_checks():
    """Servo clearance (>= 1 mm), arm at full travel, aileron at +-20 deg, aileron length and gaps."""
    import Part
    from FreeCAD import Vector as V
    d = B.doc()
    out = []
    pr = lambda *a: out.append(" ".join(str(x) for x in a))
    g = lambda n: d.getObject(n).Shape
    S = P.MG90S
    pr("=== Stage B checks ===")
    for side in ("R", "L"):
        sv = g("Servo_MG90S_" + side)
        sgn = 1 if side == "R" else -1
        # servo body without the tabs (the tabs bear on the hatch lugs by design)
        bb = sv.BoundBox
        ytab0 = P.SERVO_Y0 + S["TAB_Z"]
        tabbox = Part.makeBox(60, S["TAB_T"] + 0.02, 40, V(bb.XMin - 10, ytab0 - 0.01, bb.ZMin - 10))
        if side == "L":
            tabbox = B.mirror_y(tabbox)
        body = sv.cut(tabbox)
        res = []
        for o in parts(d):
            if o.Name.startswith(("Servo_MG90S", "ServoArm", "Pushrod")):
                continue
            ob = o.Shape.BoundBox
            if ob.YMin > bb.YMax + 20 or ob.YMax < bb.YMin - 20:
                continue
            if o.Name.startswith("ServoHatch"):
                # hatch plate only (the lugs are the servo mount, slip fit P.LUG_GAP)
                cx1 = P.SERVO_SHAFT_X + S["SHAFT_FROM_END"]; cx0 = cx1 - S["L"]
                ly0, ly1 = P.SERVO_Y0 + S["TAB_Z"] - 4.0, P.SERVO_Y0 + S["TAB_Z"]
                lugzone = Part.makeBox(cx0 - 100.0, ly1 - ly0 + 0.02, 60, V(100.0, ly0 - 0.01, -30)).fuse(
                    Part.makeBox(30.0, ly1 - ly0 + 0.02, 60, V(cx1, ly0 - 0.01, -30)))
                if side == "L":
                    lugzone = B.mirror_y(lugzone)
                plate = o.Shape.cut(lugzone)
                res.append((round(body.distToShape(plate)[0], 2), o.Name + " (plate)"))
                res.append((round(body.distToShape(o.Shape)[0], 2), o.Name + " (lugs, mount)"))
                continue
            dist = sv.distToShape(o.Shape)[0]
            res.append((round(dist, 2), o.Name))
        res.sort()
        pr("servo %s: nearest parts (mm):" % side, res[:6])
        # tabs vs everything except the hatch (lugs)
        tabs = sv.common(tabbox)
        tres = sorted((round(tabs.distToShape(o.Shape)[0], 2), o.Name) for o in parts(d)
                      if not o.Name.startswith(("Servo", "Pushrod")) and abs(o.Shape.BoundBox.Center.y - sgn * 140) < 200)
        pr("servo %s tabs: nearest except hatch:" % side, [t for t in tres if not t[1].startswith("ServoHatch")][:3])
        # arm at full travel +-35 deg about the shaft axis
        arm = g("ServoArm_" + side)
        hub = [e for e in arm.Edges if hasattr(e.Curve, "Radius") and abs(e.Curve.Radius - 3.5) < 1e-6][0]
        axis_p = hub.Curve.Center
        for ang in (-35, 0, 35):
            a2 = arm.copy()
            a2.rotate(axis_p, V(0, 1, 0), ang)
            dmin = min((a2.distToShape(g(n))[0], n) for n in ("ServoHatch_" + side, "ServoFrame_" + side,
                                                                 "Rib_110_" + side, "Rib_165_" + side, "Caps_165_" + side))
            pr("  arm %s at %+d deg: min distance %.2f mm to %s" % (side, ang, dmin[0], dmin[1]))
    # aileron +-20 deg about the hinge line
    for side in ("R", "L"):
        ail = [g(n + "_" + side) for n in ("Ail_LE", "Ail_Ribs", "Ail_TE", "Ail_HornRib", "Horn")]
        ail = Part.makeCompound(ail)
        zh = 0.5 * (G.surf_z(P.HINGE_X, True) + G.surf_z(P.HINGE_X, False))
        fixed = [o for o in parts(d) if o.Name in ("FalseSpar", "TE_Centre", "TE_Outer_" + side, "RibAft_110_" + side,
                                                     "RibAft_440_" + side, "Caps_110_" + side, "Caps_440_" + side,
                                                     "Rib_110_" + side, "Rib_440_" + side)]
        for ang in (-20, -15, 0, 15, 20):
            a2 = ail.copy()
            a2.rotate(V(P.HINGE_X, 0, zh), V(0, 1, 0), ang)
            hit = sum(a2.common(o.Shape).Volume for o in fixed)
            dmin = min((a2.distToShape(o.Shape)[0], o.Name) for o in fixed)
            pr("  aileron %s at %+d deg: interference %.3f mm3, min gap %.2f mm (%s)" % (side, ang, hit, dmin[0], dmin[1]))
        bb = ail.BoundBox
        pr("aileron %s: x %.2f..%.2f, |y| %.2f..%.2f, length %.2f mm" % (side, bb.XMin, bb.XMax, min(abs(bb.YMin), abs(bb.YMax)),
                                                                       max(abs(bb.YMin), abs(bb.YMax)), bb.YLength))
    pr("end gaps: inner %.2f mm (rib 110 face 111.5), outer %.2f mm (rib 440 face 438.5)" % (P.AIL_Y[0] - 111.5, 438.5 - P.AIL_Y[1]))
    txt = "\n".join(out)
    open(os.path.join(P.CAD, "check_report_stageB_extra.txt"), "w").write(txt)
    print(txt)


def write_mass_md():
    """design/cad/mass_table.md + mass_table.csv from the latest stage C csv."""
    import csv, re, collections, shutil
    src = os.path.join(P.CAD, "mass_table_stageC.csv")
    shutil.copy(src, os.path.join(P.CAD, "mass_table.csv"))
    rows = list(csv.DictReader(open(src)))
    total = [float(r["mass_g"]) for r in rows if r["part"] == "TOTAL"][0]
    rows = [r for r in rows if r["part"] != "TOTAL"]
    rules = [("^LE$", "Leading edge (6 mm)"), ("^DBox", "D-box sheeting 1.5 mm"), ("^CSheet", "Centre sheeting 1.5 mm"),
             ("^SparCarbon", "Spar caps, carbon 0.5 x 6"), ("^SparBalsa", "Spar caps, balsa 3 x 6"), ("^ShearWeb", "Shear webs 1.5 mm"),
             ("^FalseSpar", "False spar 3 mm"), ("^Rib_110", "Ribs 3 mm at y = 110"), ("^Rib_", "Ribs 2 mm (y = 0, 55, 165 ... 385, 439.5)"),
             ("^RibAft", "Aft rib pieces (x 208-255)"), ("^TipRib", "Tip ribs 2 x 1.5 mm"), ("^TipCap", "Tip cap rings 3 mm"),
             ("^Caps_", "Cap strips 1.5 x 6"), ("^TE_", "TE wedges (wing)"), ("^Ail_LE", "Aileron LE"),
             ("^Ail_Ribs|^Ail_HornRib", "Aileron ribs + horn ribs"), ("^Ail_TE", "Aileron TE wedges"),
             ("^ServoFrame", "Servo frames (PETG)"), ("^ServoHatch", "Servo hatches + lugs (PETG)"), ("^Horn", "Horns (PETG)"),
             ("^RubPlate", "Band rub plates (PETG)"), ("^Pushrod", "Pushrods 1.2 mm steel"), ("^Film", "Film covering"),
             ("^Glue", "Glue (estimate)"), ("screws", "M2 hatch screws"), ("hinges", "CA hinges")]
    grp = collections.OrderedDict()
    for r in rows:
        g = next((g for pat, g in rules if re.search(pat, r["part"])), r["part"])
        e = grp.setdefault(g, [0, 0.0, set()])
        e[0] += 1; e[1] += float(r["mass_g"]); e[2].add("%s %s" % (r["material"], r["density_kg_m3_or_gsm"]))
    servo = 2 * 13.4 + 0.6
    L = ["# Wing rev A - mass table", "",
         "Generated by `design/cad/scripts/wing_check.py` (volume x density for each modelled part). Raw rows: `mass_table.csv`.",
         "Densities (kg/m3): selected light sheet 90, light 100, medium 130, hard 160, carbon 1550, PETG 1270 (infill factor 1.0: thin parts print solid), "
         "steel 7850. Film 50 g/m2 on %.3f m2. Glue 8 g estimate." % film_area_m2(), "",
         "| Group | Parts | Material (density) | Mass g |", "|---|---|---|---|"]
    for g, (n, m, mat) in grp.items():
        L.append("| %s | %d | %s | %.1f |" % (g, n, ", ".join(sorted(mat)), m))
    L += ["| **Wing without servos** | | | **%.1f** |" % total,
          "| MG90S servos (2 x 13.4 g, datasheet value *(interp.)*) + arms | | | %.1f |" % servo,
          "| **Wing with servos** | | | **%.1f** |" % (total + servo), "",
          "No fixed mass limit (D-047). History: 145 g in the plan, 155 g after D-013, 160 g after D-023.",
          "Uncertainty: film and glue +-5 g; balsa density +-20 % between sheets. Weigh the sheets, correct `RHO` in `wing_params.py`, "
          "then run `run_all.py` again (this file is written again)."]
    open(os.path.join(P.CAD, "mass_table.md"), "w").write("\n".join(L) + "\n")
    return total
