# Bridge job: tail, reservoir and electronics into the open rev B design.
import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "boot.py")).read())
import time
G = rl("geo"); F = rl("fxlib"); POD = rl("pod"); T = rl("tail")
t0 = time.time()
root = F.design().rootComponent
top = F.group(root, "WaterDrop_revB")
fails = []
# tail
tail = F.group(top, "Tail")
parts, rounds = T.all_parts()
F.build_list(tail, parts, fails)
for name, p0, p1, r, ri, mat, grp in rounds:
    try:
        F.tube(F.group(tail, grp), name, p0, p1, r, ri, mat)
    except Exception as e:
        fails.append((name, str(e)[:160]))
# reservoir
res = F.group(top, "Reservoir")
for it in T.reservoir():
    try:
        if it[0] == "revolve":
            F.revolve_part(res, it[1], it[2], it[3], it[4])
        else:
            F.tube(res, it[1], it[2], it[3], it[4], it[5], it[6])
    except Exception as e:
        fails.append((it[1], str(e)[:160]))
# electronics
el = F.group(top, "Electronics")
_, _, servo = POD.all_parts()
for it in T.electronics(servo):
    try:
        if it[0] == "box":
            F.box(el, it[1], *it[2], mat="elec")
        else:
            F.tube(el, it[1], it[2], it[3], it[4], it[5], "elec")
    except Exception as e:
        fails.append((it[1], str(e)[:160]))
F.app.activeViewport.fit()
print("built in %.0f s" % (time.time() - t0))
print("FAILED:", fails)
