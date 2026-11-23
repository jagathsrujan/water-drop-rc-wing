"""Stage R-D: saddles, straps, front stop, MG90S placeholder, arm, link. exec() inside FreeCAD."""
import sys, os, importlib, json
SCRIPTS = globals().get("RES_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad_reservoir", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import res_params as P, res_build as B
for m in (P, B):
    importlib.reload(m)
d = B.doc()
for g in ("D_Mount", "D_Servo"):
    B.clear_group(g); B.group(g)
A = json.load(open(os.path.join(os.path.dirname(SCRIPTS), "result_stageA.json")))
base = A["base_x"]
s1 = B.build_saddle(base, P.S1_YU, P.STRAP1_YU); s2 = B.build_saddle(base, P.S2_YU, P.STRAP2_YU)
t1 = B.build_strap(base, P.STRAP1_YU); t2 = B.build_strap(base, P.STRAP2_YU)
stop = B.build_stop(base)
for n, s in (("P12a_Saddle1", s1), ("P12b_Saddle2", s2), ("P13a_Strap1", t1), ("P13b_Strap2", t2), ("P12c_FrontStop", stop)):
    B.info(n, s)
B.put("P12a_Saddle1", s1, "saddle", "D_Mount", "PETG", "thin", "saddle 1, cylinder")
B.put("P12b_Saddle2", s2, "saddle", "D_Mount", "PETG", "thin", "saddle 2, shoulder (aft stop)")
B.put("P13a_Strap1", t1, "strap", "D_Mount", "", "given:%g" % P.STRAP_MASS_G, "hook-and-loop 20 mm (bought)")
B.put("P13b_Strap2", t2, "strap", "D_Mount", "", "given:%g" % P.STRAP_MASS_G, "hook-and-loop 20 mm (bought)")
B.put("P12c_FrontStop", stop, "balsa", "D_Mount", "balsa", "info", "fuselage bulkhead, balsa 3 mm (not in the reservoir total)")
servo = B.servo_body(); B.info("P14_Servo_MG90S", servo)
snap, wire, wlen = B.build_link(); B.info("P14_QuickSnap", snap); B.info("P14_LinkWire", wire)
arm = B.build_arm().cut(wire); B.info("P14_ServoArm", arm)
print("shaft (X,Y)", B.servo_shaft(), "arm tip closed", B.arm_tip(P.ARM_CLOSED_DEG), "wire length", round(wlen, 2))
B.put("P14_Servo_MG90S", servo, "servo", "D_Servo", "", "servo:%g" % P.SERVO_MASS_G, "PLACEHOLDER standard MG90S size, upright, shaft down")
B.put("P14_ServoArm", arm, "PETG", "D_Servo", "PETG", "thin", "arm R10 in the horizontal plane, closed at -45 deg")
B.put("P14_QuickSnap", snap, "steel", "D_Servo", "steel", "fixed", "fishing snap placeholder 2 x 12")
B.put("P14_LinkWire", wire, "steel", "D_Servo", "steel", "fixed", "wire D0.8, straight along Y")
d.recompute()
