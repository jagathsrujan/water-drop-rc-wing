"""Stage F-B pictures (FreeCAD GUI). 1600 x 1200, white, fitAll. TMP_ objects only inside B.snap (deleted there)."""
import sys, os, importlib
SCRIPTS = globals().get("FUS_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad_fuselage", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import fus_params as P, fus_build as B
IMG = P.IMG + "/"
os.makedirs(IMG, exist_ok=True)
d = B.doc()
Box = B.box
POD = {"F1_PodNose", "F2_PodCentre", "F3_PodAft", "F4_NoseHatch"}
FEAT = {o.Name for o in d.Objects if o.Name[:2] in ("F5", "F6", "F7", "F8", "F9")}
PH = {o.Name for o in d.Objects if o.Name.startswith("PH_")}
REFC = {o.Name for o in d.Objects if o.Name.startswith("RefRes_") and getattr(o, "ResState", "") == "closed"}
ALL = POD | FEAT | PH | REFC
wing = d.getObject("Ref_Wing").Shape
stub = wing.common(Box(-10, 290, -160, 160, -40, 40))
W_EX = ("WingStub", stub, P.COL_WING, P.TR_WING)

B.snap(IMG + "stageB_iso.png", "iso", only=ALL, extra=[W_EX])
B.snap(IMG + "stageB_iso_below.png", "iso_low", only=POD | FEAT)
half = Box(-260, 360, 0, 200, -250, 120)
B.snap(IMG + "stageB_section_Y0.png", "front", only=ALL, section_box=half,
       extra=[("WingY0", stub.common(half), P.COL_WING, 60)])
for nm, x0, x1 in (("X80", 64.0, 66.0), ("Xm6", -7.0, -5.0), ("X260", 200.0, 262.0)):
    slab = Box(x0, x1, -200, 200, -250, 120)
    B.snap(IMG + "stageB_section_%s.png" % nm, "from_fwd", only=ALL, section_box=slab,
           extra=[("Wing" + nm, stub.common(Box(x0, x1, -90, 90, -40, 40)), P.COL_WING, 60)])
B.snap(IMG + "stageB_top.png", "top", only=POD | FEAT | PH | (REFC - {"RefRes_Water"}))
hb = Box(-175, 0, -70, 70, -45, 10)
B.snap(IMG + "stageB_hatch_closeup.png", "iso", only=POD | FEAT, section_box=hb.cut(Box(-175, 0, -70, 0, -45, 10)))
sb = Box(35, 95, 20, 70, -125, -70)
B.snap(IMG + "stageB_servo_pocket_closeup.png", "iso_aft", only=POD | (REFC - {"RefRes_P1_Bottle", "RefRes_Water"}), section_box=sb)
print("pictures done:", sorted(f for f in os.listdir(IMG) if f.startswith("stageB_")))
