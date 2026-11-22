"""Full rebuild and all outputs: Stage A, Stage B, checks, Stage C exports. exec() inside FreeCAD.
Writes design/cad/run_all.log; the FCStd is saved at the end."""
import os, sys, traceback, importlib, io, contextlib
SCRIPTS = globals().get("WING_SCRIPTS") or os.environ.get("WING_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad_revB", "scripts")
LOG = os.path.join(os.path.dirname(SCRIPTS), "run_all.log")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
buf = io.StringIO()
try:
    with contextlib.redirect_stdout(buf):
        for f in ("build_stageA.py", "build_stageB.py"):
            print("##", f)
            exec(open(os.path.join(SCRIPTS, f)).read(), {"__name__": "__main__", "WING_SCRIPTS": SCRIPTS})
        import wing_check
        importlib.reload(wing_check)
        wing_check.EXTRA_G = {"M2 hatch screws 8 x 0.15 g": 1.2, "CA hinges 8 x 0.1 g": 0.8}
        print("## checks")
        wing_check.stage_b_checks()
        wing_check.run("C")
        print("## exports")
        exec(open(os.path.join(SCRIPTS, "export_stageC.py")).read(), {"__name__": "__main__", "WING_SCRIPTS": SCRIPTS})
        print("## mass table:", wing_check.write_mass_md(), "g")
        print("## pictures")
        exec(open(os.path.join(SCRIPTS, "make_pictures.py")).read(), {"__name__": "__main__", "WING_SCRIPTS": SCRIPTS})
        import wing_build as B
        B.doc().save()
        print("## saved", B.doc().FileName)
    open(LOG, "w").write(buf.getvalue() + "\nDONE\n")
except Exception:
    open(LOG, "w").write(buf.getvalue() + "\nERROR\n" + traceback.format_exc())
