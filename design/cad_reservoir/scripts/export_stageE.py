"""Stage R-E exports: Reservoir_revA.step (assembly, closed) and STL of each printed part in print orientation. exec() inside FreeCAD."""
import sys, os, importlib
SCRIPTS = globals().get("RES_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad_reservoir", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import res_params as P, res_build as B
import Part, MeshPart, Import
from FreeCAD import Vector as V
ROOT = os.path.dirname(SCRIPTS)
STL = os.path.join(ROOT, "stl")
os.makedirs(STL, exist_ok=True)
d = B.doc()
objs = [o for g in ("A_Bottle", "B_Outlet", "C_Fill", "D_Mount", "D_Servo") for o in d.getObject(g).Group if o.Name != "Water"]
step = os.path.join(ROOT, "Reservoir_revA.step")
Import.export(objs, step)
print("STEP", step, len(objs), "parts", round(os.path.getsize(step) / 1e6, 2), "MB")
# print orientation: flip = rotate 180 deg about X (so the face named in the note is on the bed)
PRINT = [
    ("P2_InnerFlange", "P2_inner_flange", True, "stem up, convex flange underside on the bed (1.0 mm edge sag: raft or brim)"),
    ("P4_BasePlate", "P4_base_plate", False, "as modelled: lug and knuckle feet on the bed, supports under the seat face (sand the seat face)"),
    ("P5_Nut", "P5_nut", False, "flat ring on the bed"),
    ("P6_Flap", "P6_flap", True, "skin face on the bed, ribs and pockets up, tab and knuckle up"),
    ("P11a_FillFlange", "P11a_fill_flange", True, "stem down on the bed, flange up"),
    ("P11c_FillNut", "P11c_fill_nut", True, "flat top on the bed, saddle side up"),
    ("P11d_FillCap", "P11d_fill_cap", True, "cap top wall on the bed, open end up (vent holes and flutes vertical)"),
    ("P15_Funnel", "P15_funnel", True, "rim on the bed, spout up (ground support, not on the aircraft)"),
    ("P12a_Saddle1", "P12a_saddle1", False, "foot on the bed, supports under the outer wings of the cradle"),
    ("P12b_Saddle2", "P12b_saddle2", False, "foot on the bed, supports under the outer wings of the cradle"),
    ("P14_ServoArm", "P14_servo_arm", False, "flat on the bed (already in the horizontal plane)"),
]
for name, fn, flip, note in PRINT:
    s = d.getObject(name).Shape.copy()
    c = s.BoundBox.Center
    if flip == "y90":
        s.rotate(c, V(0, 1, 0), 90)
    elif flip:
        s.rotate(c, V(1, 0, 0), 180)
    bb = s.BoundBox
    s.translate(V(-bb.Center.x, -bb.Center.y, -bb.ZMin))
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.2)
    p = os.path.join(STL, fn + ".stl")
    m.write(p)
    bb = s.BoundBox
    print("STL %-22s %6d facets  %.1f x %.1f x %.1f mm  %s" % (fn + ".stl", m.CountFacets, bb.XLength, bb.YLength, bb.ZLength, note))
open(os.path.join(STL, "print_orientation.txt"), "w").write("\n".join("%s.stl : %s" % (fn, note) for _, fn, _, note in PRINT) + "\n")
