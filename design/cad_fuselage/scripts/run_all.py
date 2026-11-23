"""Full rebuild of Fuselage_revA (stage F-A for now): build, checks, pictures, save. exec() inside FreeCAD:
    exec(open("<project>/design/cad_fuselage/scripts/run_all.py").read())
Writes design/cad_fuselage/run_all.log (last line DONE, or ERROR with the traceback). Reservoir_revA is read only."""
import os, sys, traceback, importlib, io, contextlib
SCRIPTS = globals().get("FUS_SCRIPTS") or os.environ.get("FUS_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad_fuselage", "scripts")
ROOT = os.path.dirname(SCRIPTS)
LOG = os.path.join(ROOT, "run_all.log")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
buf = io.StringIO()
try:
    with contextlib.redirect_stdout(buf):
        import FreeCAD as App
        ns = {"__name__": "__main__", "FUS_SCRIPTS": SCRIPTS}
        print("## build_stageA.py")
        exec(open(os.path.join(SCRIPTS, "build_stageA.py")).read(), dict(ns))
        import fus_check
        importlib.reload(fus_check)
        fus_check.OUTDIR = ROOT
        print("## checks (stage F-A)")
        fus_check.run_stage_a()
        if App.GuiUp:
            print("## pictures (stage F-A)")
            exec(open(os.path.join(SCRIPTS, "make_pictures.py")).read(), dict(ns))
        print("## build_stageB.py")
        exec(open(os.path.join(SCRIPTS, "build_stageB.py")).read(), dict(ns))
        import fus_check_b
        importlib.reload(fus_check_b)
        fus_check_b.OUTDIR = ROOT
        print("## checks (stage F-B)")
        fus_check_b.run_stage_b()
        if App.GuiUp:
            print("## pictures (stage F-B)")
            exec(open(os.path.join(SCRIPTS, "make_pictures_b.py")).read(), dict(ns))
        print("## build_stageC.py")
        exec(open(os.path.join(SCRIPTS, "build_stageC.py")).read(), dict(ns))
        print("## build_wing_asm.py")
        exec(open(os.path.join(SCRIPTS, "build_wing_asm.py")).read(), dict(ns))
        import fus_check_c
        importlib.reload(fus_check_c)
        fus_check_c.OUTDIR = ROOT
        print("## checks (stage F-C)")
        fus_check_c.run_stage_c()
        if App.GuiUp:
            print("## pictures (stage F-C)")
            exec(open(os.path.join(SCRIPTS, "make_pictures_c.py")).read(), dict(ns))
        else:
            print("## pictures skipped (no GUI)")
        import fus_params as P, fus_build as B
        d = B.doc()
        for o in [o for o in d.Objects if o.Name.startswith("TMP_")]:
            d.removeObject(o.Name)
        d.recompute()
        d.saveAs(P.FCSTD)
        print("## saved", d.FileName)
    open(LOG, "w").write(buf.getvalue() + "\nDONE\n")
except Exception:
    open(LOG, "w").write(buf.getvalue() + "\nERROR\n" + traceback.format_exc())
