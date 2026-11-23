"""Stage F-A pictures (FreeCAD GUI). 1600 x 1200, white background, fitAll first. Temporary TMP_ objects only for
sections, the clipped wing and the limit lines; snap() deletes them. Only the document Fuselage_revA is used."""
import sys, os, importlib
SCRIPTS = globals().get("FUS_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad_fuselage", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import fus_params as P, fus_build as B
importlib.reload(B)
IMG = P.IMG + "/"
os.makedirs(IMG, exist_ok=True)
d = B.doc()
POD = {"F1_PodNose", "F2_PodCentre", "F3_PodAft", "F4_NoseHatch"}
REFC = {o.Name for o in d.Objects if o.Name.startswith("RefRes_") and getattr(o, "ResState", "") == "closed"}
Box = B.box
wing = d.getObject("Ref_Wing").Shape
stub = wing.common(Box(-10, 290, -160, 160, -40, 40))          # wing clipped to Y +-160 for the pictures
W_EX = ("WingStub", stub, P.COL_WING, P.TR_WING)

B.snap(IMG + "stageA_iso.png", "iso", only=POD | REFC, extra=[W_EX])
B.snap(IMG + "stageA_iso_nowing.png", "iso", only=POD | REFC)
B.snap(IMG + "stageA_side.png", "front", only=POD | REFC, extra=[W_EX])
half = Box(-260, 360, 0, 200, -250, 120)
B.snap(IMG + "stageA_section_Y0.png", "front", only=POD | REFC, section_box=half,
       extra=[("WingStubY0", stub.common(half), P.COL_WING, 60)])
slab = Box(80, 90, -200, 200, -250, 120)
B.snap(IMG + "stageA_section_X80.png", "from_fwd", only=POD | REFC, section_box=slab,
       extra=[("WingStubX80", stub.common(Box(80, 90, -70, 70, -40, 40)), P.COL_WING, 60)])
lines = []
for y, nm in ((P.Y_LIMIT, "L1"), (-P.Y_LIMIT, "L2")):
    lines.append((nm, Box(P.FIREWALL_X - 40, P.POD_END_X + 30, y - 0.8, y + 0.8, 10, 10.5), (0.9, 0.1, 0.1)))
lines.append(("LE", Box(-0.6, 0.6, -75, 75, 10, 10.5), (0.1, 0.2, 0.9)))
lines.append(("TE", Box(279.0, 280.2, -75, 75, 10, 10.5), (0.1, 0.2, 0.9)))
lines.append(("Servo", Box(P.SERVO_WALL_X[0], P.SERVO_WALL_X[1], P.SERVO_WALL_INNER_MIN - 0.4, P.SERVO_WALL_INNER_MIN, 10, 10.5), (0.95, 0.55, 0.1)))
B.snap(IMG + "stageA_top_limits.png", "top", only=POD | (REFC - {"RefRes_Water"}), extra=lines)
print("pictures done:", sorted(f for f in os.listdir(IMG) if f.startswith("stageA_")))
