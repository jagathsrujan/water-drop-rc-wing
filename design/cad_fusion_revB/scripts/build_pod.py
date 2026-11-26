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
for i, p in enumerate(parts):
    try:
        grp = F.group(pod, p["grp"])
        ob = F.part(grp, p["name"], p["outline"], p["t"], p["fr"], cutters=p["cutters"], mat=p["mat"], labels=p["labels"], z0=p["z0"])
        for shapes, w0, w1 in p.get("joins", []):
            F.add_join(ob, shapes, w0, w1)
        for shapes, w0, w1 in p.get("pockets", []):
            F.add_pocket(ob, shapes, w0, w1)
        if i % 10 == 0:
            F.app.activeViewport.fit()
    except Exception as e:
        fails.append((p["name"], str(e).splitlines()[-1][:160]))
hg = F.group(pod, "Pod_Hard")
for kind, name, p0, p1, r, ri, mat in hard:
    try:
        F.tube(hg, name, p0, p1, r, ri, mat)
    except Exception as e:
        fails.append((name, str(e)[:160]))
F.app.activeViewport.fit()
print("pod parts built:", F.STATS["parts"], "in %.0f s" % (time.time() - t0))
print("FAILED:", fails)
