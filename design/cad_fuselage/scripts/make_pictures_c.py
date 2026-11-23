"""Stage F-C pictures (FreeCAD GUI). 1600 x 1200, white, fitAll. TMP_ objects only inside B.snap."""
import sys, os
SCRIPTS = globals().get("FUS_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad_fuselage", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import fus_params as P, fus_build as B
IMG = P.IMG + "/"
d = B.doc()
Box = B.box
POD = {o.Name for o in d.Objects if o.Name[:2] in ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9") and not o.Name.startswith(("F10", "F11", "F12", "F13", "F14", "F15", "F16", "F17", "F18", "F19"))}
TAIL = {o.Name for o in d.Objects if o.Name.startswith(("F10", "F11", "F12", "F13", "F14", "F15", "F16", "F17", "F18", "F19"))}
PH = {o.Name for o in d.Objects if o.Name.startswith("PH_")}
REFC = {o.Name for o in d.Objects if o.Name.startswith("RefRes_") and getattr(o, "ResState", "") == "closed"}
WING = {o.Name for o in d.Objects if o.Name.startswith("W_")}            # real wing rev A (build_wing_asm.py)

B.snap(IMG + "assembly_iso.png", "iso", only=POD | TAIL | PH | REFC | WING)
B.snap(IMG + "assembly_iso_aft.png", "iso_aft", only=POD | TAIL | PH | REFC | WING)
B.snap(IMG + "stageC_iso.png", "iso", only=POD | TAIL | PH | REFC)
B.snap(IMG + "stageC_side.png", "front", only=POD | TAIL | PH | REFC | WING)
B.snap(IMG + "stageC_top.png", "top", only=POD | TAIL | PH | WING)
B.snap(IMG + "stageC_tail_iso.png", "iso_aft", only=TAIL, section_box=Box(600, 800, -300, 300, -100, 200))
B.snap(IMG + "stageC_tail_rear.png", "from_fwd", only=TAIL, section_box=Box(600, 800, -300, 300, -100, 200))
B.snap(IMG + "stageC_pushrod_exit.png", "iso_aft", only=POD | TAIL | PH, section_box=Box(200, 330, -70, 70, -125, 0))
print("pictures done:", sorted(f for f in os.listdir(IMG) if f.startswith(("stageC_", "assembly_"))))
