# Bridge job: build the balsa pod in a fresh Fusion design (watch it in the GUI).
import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "boot.py")).read())
import time
G = rl("geo"); F = rl("fxlib"); POD = rl("pod")
t0 = time.time()
NEW = globals().get("NEW_DOC", True)
if NEW:
    F.new_design("WaterDrop_revB")
root = F.design().rootComponent
top = F.group(root, "WaterDrop_revB")
pod = F.group(top, "Pod")
parts, hard, servo = POD.all_parts()
fails = []
F.app.activeViewport.fit()
# build_list re-applies the part material to the extra bodies that joins create (NOSE-RING, SERVO-MOUNT: they were
# left on Fusion's default "Steel" - P2 finding 1) and builds laminated parts as one body per layer piece (lam.py)
F.build_list(pod, parts, fails, fit_every=60)
hg = F.group(pod, "Pod_Hard")
for kind, name, p0, p1, r, ri, mat in hard:
    try:
        F.tube(hg, name, p0, p1, r, ri, mat)
    except Exception as e:
        fails.append((name, str(e)[:160]))
F.app.activeViewport.fit()
print("pod parts built:", F.STATS["parts"], "in %.0f s" % (time.time() - t0))
print("FAILED:", fails)
