"""Full rebuild of Reservoir_revA (stages R-A to R-E): build, checks, pictures, exports, save. exec() inside FreeCAD.
Writes design/cad_reservoir/run_all.log."""
import os, sys, traceback, importlib, io, contextlib
SCRIPTS = globals().get("RES_SCRIPTS") or os.environ.get("RES_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad_reservoir", "scripts")
ROOT = os.path.dirname(SCRIPTS)
LOG = os.path.join(ROOT, "run_all.log")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
buf = io.StringIO()
try:
    with contextlib.redirect_stdout(buf):
        ns = {"__name__": "__main__", "RES_SCRIPTS": SCRIPTS}
        for f in ("build_stageA.py", "build_stageB.py", "build_stageC.py", "build_stageD.py"):
            print("##", f)
            exec(open(os.path.join(SCRIPTS, f)).read(), dict(ns))
        import res_check
        importlib.reload(res_check)
        res_check.OUTDIR = ROOT
        print("## checks (full)")
        res_check.run_full()
        print("## pictures")
        exec(open(os.path.join(SCRIPTS, "make_pictures.py")).read(), dict(ns))
        print("## exports")
        exec(open(os.path.join(SCRIPTS, "export_stageE.py")).read(), dict(ns))
        import res_build as B
        d = B.doc()
        for o in [o for o in d.Objects if o.Name.startswith("TMP_")]:
            d.removeObject(o.Name)
        d.saveAs(os.path.join(ROOT, "Reservoir_revA.FCStd"))
        print("## saved", d.FileName)
    open(LOG, "w").write(buf.getvalue() + "\nDONE\n")
except Exception:
    open(LOG, "w").write(buf.getvalue() + "\nERROR\n" + traceback.format_exc())
