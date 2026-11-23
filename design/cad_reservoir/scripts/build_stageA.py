"""Stage R-A: bottle, water, holes. exec() inside FreeCAD. Writes results to RESULT_A (dict) and prints."""
import sys, os, importlib
SCRIPTS = globals().get("RES_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad_reservoir", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import res_params as P, res_build as B
for m in (P, B):
    importlib.reload(m)
import Part
from FreeCAD import Vector as V

B.doc()
for g in ("A_Bottle",):
    B.clear_group(g); B.group(g)

x0 = P.BASE_X_NOMINAL
for it in range(3):
    S = B.bottle_solids(x0)
    W, zlvl = B.water_solid(S["I"], x0)
    cx = B.com(W).x
    print("iter %d: base X %.3f, water %.1f mL, centroid X %.3f, level Z %.3f" % (it, x0, W.Volume / 1000, cx, zlvl))
    if abs(cx - P.X_CG) < 0.05:
        break
    x0 += P.X_CG - cx
interior_ml = S["I"].Volume / 1000.0

# holes (fixed in the frame)
pet = S["pet"]
pet = pet.cut(B.zcyl(P.OUT_HOLE_D / 2, P.AXIS_Z - 110, P.AXIS_Z - 30, P.OUT_X))
pet = pet.cut(B.zcyl(P.FILL_HOLE_D / 2, P.AXIS_Z + 30, P.AXIS_Z + 50, P.FILL_X_C)).removeSplitter()
B.info("P1_Bottle", pet)
B.info("P1c_Cap", S["cap"])
B.info("Water", W)
B.put("P1_Bottle", pet, "PET", "A_Bottle", "PET", "fixed", "mass %.1f g (interp.)" % P.BOTTLE_MASS_G)
B.put("P1c_Cap", S["cap"], "cap", "A_Bottle", "PET", "fixed", "included in the bottle mass")
B.put("Water", W, "water", "A_Bottle", "water", "fixed", "996 g")
# keep the ideal interior volume and the numbers for the checks (document properties via a hidden string object)
RESULT_A = dict(base_x=x0, interior_ml=interior_ml, water_ml=W.Volume / 1000.0, water_cx=cx, level_z=zlvl,
                water_com=tuple(B.com(W)), pet_vol=pet.Volume, top_z=pet.BoundBox.ZMax)
print("RESULT_A", RESULT_A)
import json
json.dump(RESULT_A, open(os.path.join(os.path.dirname(SCRIPTS), "result_stageA.json"), "w"), indent=1)
