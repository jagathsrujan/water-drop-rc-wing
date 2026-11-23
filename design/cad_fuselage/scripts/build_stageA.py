"""Stage F-A: reference bodies (reservoir copy, wing at +3 deg), pod outer mould line and shell, nose hatch F4,
print split F1..F3. exec() inside FreeCAD. Rebuilds the document Fuselage_revA from scratch; never changes Reservoir_revA."""
import sys, os, importlib
SCRIPTS = globals().get("FUS_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad_fuselage", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import fus_params as P
importlib.reload(P.RP)
importlib.reload(P)
import fus_build as B
importlib.reload(B)
import FreeCAD as App

d = B.doc()
B.clear_doc()
for g in ("Pod", "Ref"):
    B.group(g)

# ---------------- reference bodies (group Ref; not parts: no mass, no export) ----------------
res = B.copy_reservoir()
n_mov = 0
for name in sorted(res):
    shp, rgb, is_open = res[name]
    mov = (name in P.MOVING_SET) and not is_open
    n_mov += mov
    tr = P.TR_BOTTLE if name == "P1_Bottle" else P.TR_RES
    B.put("RefRes_" + name, shp, "Ref", rgb or (0.6, 0.6, 0.6), tr, visible=not is_open,
          props=dict(Role="reference body: reservoir rev A.2 copy (not a part)", ResState="open" if is_open else "closed",
                     MovingSet=bool(mov)))
print("RefRes objects: %d (moving set %d, open state %d)" % (len(res), n_mov, sum(1 for v in res.values() if v[2])))
missing = [n for n in P.MOVING_SET if n not in res]
if missing:
    raise RuntimeError("moving-set objects missing in the reservoir model: %s" % missing)
wing = B.wing_ref()
B.info("Ref_Wing", wing)
B.put("Ref_Wing", wing, "Ref", P.COL_WING, P.TR_WING,
      props=dict(Role="reference body: SD7062 x 280, +3 deg, Y +-495 (simplified wing, not a part)"))

# ---------------- pod (group Pod) ----------------
R = B.build_pod()
B.LAST_POD = R          # used by build_stageB.py (same module object, no reload there)
notes = {
    "F1_PodNose": "pod nose section X %.0f .. %.0f (print); firewall slot, battery rails, ESC mount in F-B" % (P.FIREWALL_X, P.SPLIT_X[0]),
    "F2_PodCentre": "pod centre section X %.0f .. %.0f (print); belly opening cut; inner features in F-B" % P.SPLIT_X,
    "F3_PodAft": "pod aft section X %.0f .. %.0f (print); aft end closed 0.8 mm; sockets in F-B" % (P.SPLIT_X[1], P.POD_END_X),
    "F4_NoseHatch": "nose hatch X %.0f .. %.0f, top skin within %.0f mm of the top line; magnets and ledge in F-B" % (P.HATCH_X[0], P.HATCH_X[1], P.HATCH_DEPTH),
}
cols = {"F1_PodNose": (0.80, 0.80, 0.82), "F2_PodCentre": P.COL_POD, "F3_PodAft": (0.86, 0.86, 0.88), "F4_NoseHatch": P.COL_HATCH}
for n in ("F1_PodNose", "F2_PodCentre", "F3_PodAft", "F4_NoseHatch"):
    B.put(n, R["parts"][n], "Pod", cols[n], 0,
          props=dict(Material="PLA (tests) / ASA Aero", MassRule="volume x density", Note=notes[n]))
d.recompute()
os.makedirs(P.ROOT, exist_ok=True)
d.saveAs(P.FCSTD) if App.GuiUp else None
print("stage F-A build done")
