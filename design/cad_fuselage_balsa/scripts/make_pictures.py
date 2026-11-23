"""Pictures of Fuselage_revB_balsa (GUI only). exec() inside FreeCAD after build_balsa.py."""
import os, sys
SCRIPTS = globals().get("BAL_SCRIPTS") or os.path.dirname(os.path.abspath(__file__))
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import bal_params as BP
import FreeCAD as App
import FreeCADGui as Gui

d = App.getDocument(BP.DOC)
Gui.setActiveDocument(BP.DOC)
v = Gui.getDocument(BP.DOC).activeView()
os.makedirs(BP.IMG, exist_ok=True)
ALL = [o for o in d.Objects if o.TypeId == "Part::Feature"]
base = {o.Name: o.ViewObject.Visibility for o in ALL}


def show(pred):
    for o in ALL:
        o.ViewObject.Visibility = bool(pred(o))


def snap(name, view, w=1600, h=1000):
    getattr(v, view)()
    Gui.SendMsgToActiveView("ViewFit")
    v.saveImage(os.path.join(BP.IMG, name + ".png"), w, h, "White")


pod = lambda o: o.Name.startswith("BS_")
closed_res = lambda o: o.Name.startswith("RefRes_") and getattr(o, "ResState", "closed") == "closed"
ph = lambda o: o.Name.startswith("PH_") and o.Name != "PH_PropDisc"
tail = lambda o: o.Name[:3] in ("F10", "F11", "F12", "F13", "F14", "F15", "F16", "F17", "F18", "F19")
show(lambda o: base[o.Name] and not o.Name.startswith("JIG_"))
snap("assembly_iso", "viewIsometric")
show(lambda o: base[o.Name] and not o.Name.startswith(("JIG_", "PH_PropDisc")))
snap("aircraft_iso", "viewIsometric")
show(lambda o: pod(o) or closed_res(o) or ph(o))
snap("pod_iso", "viewIsometric")
snap("pod_side", "viewFront")
snap("pod_bottom", "viewBottom")
show(lambda o: (pod(o) and o.Name not in ("BS_Hatch", "BS_SideL")) or closed_res(o) or ph(o))
snap("pod_open_iso", "viewIsometric")
snap("pod_open_top", "viewTop")
show(lambda o: pod(o) and o.Name not in ("BS_Hatch", "BS_SideL"))
snap("pod_structure_iso", "viewIsometric")
jig = lambda o: o.Name.startswith("JIG_")
show(lambda o: pod(o) or jig(o) or o.Name == "F10_Tubes")
snap("jigs_on_pod_iso", "viewIsometric")
show(lambda o: jig(o) or o.Name == "BS_Floor")
snap("jigs_layout_iso", "viewIsometric")
show(lambda o: base[o.Name])
v.viewIsometric()
Gui.SendMsgToActiveView("ViewFit")
print("pictures:", sorted(os.listdir(BP.IMG)))
