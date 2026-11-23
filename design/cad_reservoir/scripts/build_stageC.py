"""Stage R-C (rev A.1): fill unit P11a-f, fuselage fill-hole reference, funnel P15 (ground support), wing reference. exec() inside FreeCAD."""
import sys, os, importlib
SCRIPTS = globals().get("RES_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad_reservoir", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import res_params as P, res_build as B
for m in (P, B):
    importlib.reload(m)
d = B.doc()
old = d.getObject("C_Vent")                      # rev A vent removed
if old is not None:
    for o in list(old.Group):
        d.removeObject(o.Name)
    d.removeObject("C_Vent")
for g in ("C_Fill", "E_Ground"):
    B.clear_group(g); B.group(g)
f = B.build_fill()
rows = (("P11a_FillFlange", "flange", "PETG", "PETG", "thin", "round flange D16.5, stem D13 / bore D10 to Z -9.5"),
        ("P11b_FillGasket", "gasket", "gasket", "silicone", "fixed", "outer saddle gasket 1.0 mm"),
        ("P11c_FillNut", "nut", "PETG", "PETG", "thin", "D18, top Z -16.5"),
        ("P11d_FillCap", "cap", "PETG", "PETG", "thin", "cap with 6+1 vent holes, 12 flutes"),
        ("P11e_CapSeal", "seal", "gasket", "silicone", "fixed", "cap seal ring"),
        ("P11f_VentFlap", "flap", "gasket", "silicone", "fixed", "silicone umbrella vent flap"))
for name, key, col, mat, rule, note in rows:
    B.info(name, f[key])
    B.put(name, f[key], col, "C_Fill", mat, rule, note)
fun = B.build_funnel(); B.info("P15_Funnel", fun)
B.put("P15_Funnel", fun, "PETG", "E_Ground", "PETG", "info", "ground support, STL only, not in the mass or the STEP")
d.getObject("P15_Funnel").ViewObject.Visibility = False
B.group("Ref")
w = B.wing_ref(); B.info("Ref_Wing", w)
B.put("Ref_Wing", w, "ref", "Ref", "", "fixed", "SD7062 x 280, +3 deg, reference only")
d.getObject("Ref_Wing").ViewObject.Visibility = False
ft = B.fuselage_top_ref(); B.info("Ref_FuselageTop", ft)
B.put("Ref_FuselageTop", ft, "ref", "Ref", "", "fixed", "fuselage top deck with the D25 fill hole, reference only (interp. height)")
d.getObject("Ref_FuselageTop").ViewObject.Visibility = False
d.recompute()
