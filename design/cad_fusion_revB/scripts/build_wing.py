# Bridge job: build the wing (at +3 deg incidence) into the open rev B design.
exec(open(r"C:\Projects\water-drop-rc-wing\design\cad_fusion_revB\scripts\boot.py").read())
import time
G = rl("geo"); F = rl("fxlib"); W = rl("wing")
import wing_params as P
t0 = time.time()
root = F.design().rootComponent
top = F.group(root, "WaterDrop_revB")
wing = F.group_tf(top, "Wing", F.rot_y(P.__dict__.get("INCIDENCE", 3.0)))
parts, boxes = W.all_parts()
fails = []
n0 = F.STATS["parts"]
F.build_list(wing, parts, fails)
sv = F.group(wing, "Wing_Servo")
for kind, name, (x0, x1, y0, y1, z0, z1) in boxes:
    try:
        F.box(sv, name, x0, x1, y0, y1, z0, z1, "elec")
    except Exception as e:
        fails.append((name, str(e)[:160]))
F.app.activeViewport.fit()
print("wing parts built:", F.STATS["parts"] - n0, "in %.0f s" % (time.time() - t0))
print("FAILED:", fails)
