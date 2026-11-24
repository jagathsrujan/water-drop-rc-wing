# Bridge job: the whole rev B aircraft in a fresh Fusion design: pod, wing (+3 deg), tail, reservoir, electronics.
import time
_t0 = time.time()
for _d in list(app.documents):
    _d.close(False)
NEW_DOC = True
exec(open(r"C:\Projects\water-drop-rc-wing\design\cad_fusion_revB\scripts\build_pod.py").read())
exec(open(r"C:\Projects\water-drop-rc-wing\design\cad_fusion_revB\scripts\build_wing.py").read())
exec(open(r"C:\Projects\water-drop-rc-wing\design\cad_fusion_revB\scripts\build_rest.py").read())
exec(open(r"C:\Projects\water-drop-rc-wing\design\cad_fusion_revB\scripts\build_linkage.py").read())
print("ALL DONE in %.0f s" % (time.time() - _t0))
