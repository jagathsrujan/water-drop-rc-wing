"""Stage R-B: outlet unit P2..P10 (closed) + open-state copy (group B_Open, hidden) + belly reference. exec() inside FreeCAD."""
import sys, os, importlib
SCRIPTS = globals().get("RES_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad_reservoir", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import res_params as P, res_build as B
for m in (P, B):
    importlib.reload(m)
import Part
from FreeCAD import Vector as V

d = B.doc()
for g in ("B_Outlet", "B_Open", "Ref"):
    B.clear_group(g); B.group(g)

p2 = B.build_P2();  B.info("P2_InnerFlange", p2)
p3 = B.build_P3();  B.info("P3_OuterGasket", p3)
p4 = B.build_P4();  B.info("P4_BasePlate", p4)
p5 = B.build_P5();  B.info("P5_Nut", p5)
p6 = B.build_P6();  B.info("P6_Flap", p6)
p7 = B.build_P7();  B.info("P7_FlapGasket", p7)
p8 = B.build_P8();  B.info("P8_HingePin", p8)
p9 = B.build_P9();  B.info("P9_ReleasePin", p9)
p10 = B.build_P10(); B.info("P10_SafetyPin", p10)
p10f = B.build_P10_flag(); B.info("P10_Flag", p10f)

B.put("P2_InnerFlange", p2, "PETG", "B_Outlet", "PETG", "thin", "oval saddle flange + stem")
B.put("P3_OuterGasket", p3, "gasket", "B_Outlet", "silicone", "fixed", "main seal")
B.put("P4_BasePlate", p4, "PETG", "B_Outlet", "PETG", "thick", "saddle, seat face, lugs, knuckles")
B.put("P5_Nut", p5, "PETG", "B_Outlet", "PETG", "thin", "M17x1 cosmetic")
B.put("P6_Flap", p6, "moving", "B_Outlet", "PETG", "thin", "flap with hook tab and knuckle")
B.put("P7_FlapGasket", p7, "gasket", "B_Outlet", "EVA", "fixed", "EVA closed-cell foam 2.0 mm, 0.10 g/cm3 (interp.)")
B.put("P8_HingePin", p8, "steel", "B_Outlet", "steel", "fixed", "")
B.put("P9_ReleasePin", p9, "steel", "B_Outlet", "steel", "fixed", "")
B.put("P10_SafetyPin", p10, "steel", "B_Outlet", "steel", "fixed", "")
B.put("P10_Flag", p10f, "flag", "B_Outlet", "tape", "fixed", "red flag tape")

# water: remove the flange volume (flange sits inside the interior)
W = d.getObject("Water")
if W is not None:
    w0 = W.Shape.Volume
    wnet = W.Shape.cut(p2)
    W.Shape = wnet
    print("Water after flange cut: %.1f mL (was %.1f)" % (wnet.Volume / 1000, w0 / 1000))

# open state copies (hidden): flap, flap gasket rotated; release pin retracted +Y; safety pin pulled out -Y
ang = P.OPEN_ANGLE
o6 = B.rotate_open(p6, ang); o7 = B.rotate_open(p7, ang)
o9 = B.build_P9(P.RP_RETRACT); o10 = B.build_P10(-P.SP_REMOVE); o10f = B.build_P10_flag(-P.SP_REMOVE)
B.put("P6_Flap_open", o6, "moving", "B_Open", "PETG", "thin", "open %.0f deg" % ang)
B.put("P7_FlapGasket_open", o7, "gasket", "B_Open", "EVA", "fixed")
B.put("P9_ReleasePin_open", o9, "steel", "B_Open", "steel", "fixed", "retracted 12 mm")
B.put("P10_SafetyPin_open", o10, "steel", "B_Open", "steel", "fixed", "removed")
B.put("P10_Flag_open", o10f, "flag", "B_Open", "tape", "fixed")
for n in ("P6_Flap_open", "P7_FlapGasket_open", "P9_ReleasePin_open", "P10_SafetyPin_open", "P10_Flag_open"):
    d.getObject(n).ViewObject.Visibility = False
B.put("Ref_BellySkin", B.belly_ref(), "ref", "Ref", "", "fixed", "reference only, not a part")
d.getObject("Ref_BellySkin").ViewObject.Visibility = False
d.recompute()
