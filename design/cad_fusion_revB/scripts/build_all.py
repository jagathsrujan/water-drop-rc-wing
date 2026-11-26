# Bridge job: the whole rev B aircraft in a fresh Fusion design: pod, wing (+3 deg), tail, reservoir, electronics,
# control linkages and hinges, then the assembly set-up (rigid airframe + hinge joints on the control surfaces).
import time
_t0 = time.time()
for _d in list(app.documents):
    _d.close(False)
NEW_DOC = True
import os
_S = os.path.dirname(os.path.abspath(__file__))
for _job in ("build_pod.py", "build_wing.py", "build_rest.py", "build_linkage.py", "assemble.py"):
    exec(open(_S + "\\" + _job).read())
print("ALL DONE in %.0f s" % (time.time() - _t0))
