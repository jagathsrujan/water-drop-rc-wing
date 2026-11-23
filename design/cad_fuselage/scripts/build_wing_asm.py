"""Wing rev A in the fuselage assembly: copies every Part::Feature of design/cad/Wing_revA.FCStd into group "Wing"
(names W_<name>, colours kept), turned +WING_INCIDENCE deg about +Y through the origin (wing frame = fuselage frame:
LE on the centreline, chord line Z 0; plan 04 section 2). Wing_revA.FCStd is opened read-only and closed unsaved.
exec() inside FreeCAD after build_stageC.py. Ref_Wing (simplified B-spline) stays for the fast checks."""
import sys, os
SCRIPTS = globals().get("FUS_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad_fuselage", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import fus_params as P
import fus_build as B
import FreeCAD as App

V = App.Vector
WING_FCSTD = os.path.join(os.path.dirname(P.ROOT), "cad", "Wing_revA.FCStd")
d = B.doc()
B.group("Wing")
was_open = [x for x in App.listDocuments().values() if x.FileName == WING_FCSTD]
wd = was_open[0] if was_open else App.openDocument(WING_FCSTD, True)      # hidden, read-only use
n = 0
vol = 0.0
for o in wd.Objects:
    if o.TypeId != "Part::Feature" or o.Shape.isNull():
        continue
    s = o.Shape.copy()
    s.rotate(V(0, 0, 0), V(0, 1, 0), P.WING_INCIDENCE)
    col = tuple(o.ViewObject.ShapeColor[:3]) if (App.GuiUp and o.ViewObject) else (0.85, 0.72, 0.5)
    grp = o.getParentGroup().Label if o.getParentGroup() else "-"
    B.put("W_" + o.Name, s, "Wing", col, 0, props=dict(Note="wing rev A part (%s), +%.1f deg" % (grp, P.WING_INCIDENCE)))
    n += 1
    vol += s.Volume
if not was_open:
    App.closeDocument(wd.Name)                                                  # never saved
App.setActiveDocument(d.Name)
ref = d.getObject("Ref_Wing")
if ref is not None and App.GuiUp:
    ref.ViewObject.Visibility = False                                           # the real wing is shown
d.recompute()
print("wing rev A in the assembly: %d parts, %.1f cm3, +%.1f deg" % (n, vol / 1000, P.WING_INCIDENCE))
