"""Export the removable assembly jigs (JIG_*) of Fuselage_revB_balsa as STL to design/cad_fuselage_balsa/jigs/.
Model orientation (wing frame); print orientation notes in design/cad_fuselage_balsa/README.md. exec() inside FreeCAD."""
import os, sys
SCRIPTS = globals().get("BAL_SCRIPTS") or os.path.dirname(os.path.abspath(__file__))
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import bal_params as BP
import FreeCAD as App
import MeshPart

d = App.getDocument(BP.DOC)
out_dir = os.path.join(BP.ROOT, "jigs")
os.makedirs(out_dir, exist_ok=True)
for o in d.Objects:
    if o.Name.startswith("JIG_"):
        m = MeshPart.meshFromShape(Shape=o.Shape, LinearDeflection=0.05, AngularDeflection=0.3, Relative=False)
        p = os.path.join(out_dir, o.Name[4:] + ".stl")
        m.write(p)
        print("STL", os.path.basename(p), m.CountFacets, "facets")
