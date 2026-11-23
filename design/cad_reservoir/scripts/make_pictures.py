"""Pictures (FreeCAD GUI). 1600 x 1200, white background, fitAll first. Temporary objects only for sections and limit lines."""
import sys, os, importlib
SCRIPTS = globals().get("RES_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad_reservoir", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import res_params as P, res_build as B
importlib.reload(B)
IMG = os.path.join(os.path.dirname(SCRIPTS), "img") + "/"
os.makedirs(IMG, exist_ok=True)
d = B.doc()
grp = lambda *g: {o.Name for n in g for o in d.getObject(n).Group}
A_OBJ = {"P1_Bottle", "P1c_Cap", "Water"}
OUTLET = grp("B_Outlet")
OPEN_MOVING = {"P6_Flap_open", "P7_FlapGasket_open", "P9_ReleasePin_open", "P10_SafetyPin_open", "P10_Flag_open"}
CLOSED_MOVING = {"P6_Flap", "P7_FlapGasket", "P9_ReleasePin", "P10_SafetyPin", "P10_Flag"}
FULL = grp("A_Bottle", "B_Outlet", "C_Fill", "D_Mount", "D_Servo")
FULL_OPEN = (FULL - CLOSED_MOVING) | (OPEN_MOVING & {o.Name for o in d.Objects})
Box = B.box
# --- stage A and outlet close-ups
B.snap(IMG + "stageA_iso.png", "iso", only=A_OBJ)
OUT_SET = OUTLET | {"P1_Bottle", "Ref_BellySkin"}
B.snap(IMG + "stageB_outlet_iso_closed.png", "iso_low", only=OUT_SET, section_box=Box(35, 125, -42, 42, -135, -80))
open_set = (OUTLET - CLOSED_MOVING) | OPEN_MOVING | {"P1_Bottle", "Ref_BellySkin"}
B.snap(IMG + "stageB_outlet_iso_open.png", "iso_low", only=open_set, section_box=Box(30, 160, -60, 60, -135, -80))
B.snap(IMG + "stageB_section_Y0.png", "front", only=OUT_SET, section_box=Box(35, 125, 0, 42, -135, -80))
B.snap(IMG + "stageB_section_X80.png", "from_fwd", only=OUT_SET, section_box=Box(80, 125, -42, 42, -135, -80))
# --- full model
B.snap(IMG + "full_iso_closed.png", "iso", only=FULL)
B.snap(IMG + "full_iso_closed_low.png", "iso_low", only=FULL)
B.snap(IMG + "full_iso_open.png", "iso_low", only=FULL_OPEN)
B.snap(IMG + "section_Y0_full.png", "front", only=FULL | {"Ref_BellySkin"}, section_box=Box(-60, 245, 0, 80, -125, 5))
# --- servo link close view (closed state, from below and the side)
link_set = {"P14_Servo_MG90S", "P14_ServoArm", "P14_LinkWire", "P14_QuickSnap", "P9_ReleasePin", "P4_BasePlate", "P6_Flap", "P7_FlapGasket", "P10_SafetyPin"}
B.snap(IMG + "servo_link.png", "iso_low", only=link_set, section_box=Box(38, 100, -6, 62, -122, -72))
# --- fill unit close-up: iso with a section at Y = 0 (keep Y >= 0), wing reference and fuselage fill hole visible
fill_set = grp("C_Fill") | {"P1_Bottle", "Ref_Wing", "Ref_FuselageTop"}
B.snap(IMG + "fill_closeup.png", "iso", only=fill_set, section_box=Box(-36, 12, 0, 22, -34, 4))
# --- funnel above the fill port (wing reference shown to show the conflict)
B.snap(IMG + "fill_with_funnel.png", "iso", only={"P11a_FillFlange", "P11b_FillGasket", "P11c_FillNut"} | {"P1_Bottle", "P15_Funnel", "Ref_Wing", "Ref_FuselageTop"}, section_box=Box(-60, 40, -45, 45, -50, 70))
# --- top view with the Y +-55 limits, the servo limit and the wing LE line
import Part
lines = []
for y, rgb, nm in ((P.Y_LIMIT, (0.9, 0.1, 0.1), "L1"), (-P.Y_LIMIT, (0.9, 0.1, 0.1), "L2"), (P.SERVO_Y_LIMIT, (0.95, 0.55, 0.1), "L3"), (-P.SERVO_Y_LIMIT, (0.95, 0.55, 0.1), "L4")):
    lines.append((nm, Box(-60, 250, y - 0.8, y + 0.8, 0, 0.6), rgb))
lines.append(("LE", Box(-0.8, 0.8, -70, 70, 0, 0.6), (0.1, 0.2, 0.9)))
B.snap(IMG + "top_view_limits.png", "top", only=FULL - {"Water"}, extra=lines)
print("pictures done")
