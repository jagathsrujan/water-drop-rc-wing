"""STEP assembly export of Fuselage_revB_balsa for Onshape / SolidWorks (GUI; exec() inside FreeCAD).
Writes design/cad_fuselage_balsa/export/:
  WaterDrop_revB_assembly.step  top assembly WaterDrop_Aircraft_revB with the subassemblies Fuselage_BalsaPod,
                                Reservoir, Wing_revA, Tail, Electronics; every part a named, coloured solid body
  Jigs_revB.step                the removable assembly jigs (separate file, not part of the aircraft)
Not exported: the check proxies (PX_*, Ref_WingRevA), the open-state reservoir poses (*_open) and the water volume.
Frame: wing frame, mm (origin wing LE on the centreline, X aft, Y right, Z up)."""
import os, sys
SCRIPTS = globals().get("BAL_SCRIPTS") or os.path.dirname(os.path.abspath(__file__))
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import bal_params as BP
import FreeCAD as App
import FreeCADGui as Gui
import ImportGui

src = App.getDocument(BP.DOC)
out_dir = os.path.join(BP.ROOT, "export")
os.makedirs(out_dir, exist_ok=True)
TAIL = ("F10", "F11", "F12", "F13", "F14", "F15", "F16", "F17", "F18", "F19")


def is_closed_res(o):
    return (o.Name.startswith("RefRes_") and getattr(o, "ResState", "closed") == "closed"
            and not o.Name.endswith("_open") and o.Name != "RefRes_Water")


GROUPS = [("Fuselage_BalsaPod", lambda o: o.Name.startswith("BS_")),
          ("Reservoir", is_closed_res),
          ("Wing_revA", lambda o: o.Name.startswith("W_")),
          ("Tail", lambda o: o.Name[:3] in TAIL),
          ("Electronics", lambda o: o.Name.startswith("PH_"))]


def export(fname, top_name, groups):
    tmp = App.newDocument("STEP_export_tmp")
    top = tmp.addObject("App::Part", top_name)
    counts = {}
    for gname, pred in groups:
        sub = tmp.addObject("App::Part", gname)
        top.addObject(sub)
        n = 0
        for o in src.Objects:
            if o.TypeId != "Part::Feature" or not pred(o):
                continue
            f = tmp.addObject("Part::Feature", o.Name)
            f.Label = o.Name
            f.Shape = o.Shape.copy()
            if App.GuiUp:
                f.ViewObject.ShapeColor = o.ViewObject.ShapeColor
                f.ViewObject.Transparency = 0
            sub.addObject(f)
            n += 1
        counts[gname] = n
    tmp.recompute()
    path = os.path.join(out_dir, fname)
    ImportGui.export([top], path)
    App.closeDocument(tmp.Name)
    print("STEP %s: %s, %.1f MB" % (fname, counts, os.path.getsize(path) / 1e6))
    return path


export("WaterDrop_revB_assembly.step", "WaterDrop_Aircraft_revB", GROUPS)
export("Jigs_revB.step", "Assembly_Jigs_revB", [("Jigs", lambda o: o.Name.startswith("JIG_"))])
App.setActiveDocument(BP.DOC)
