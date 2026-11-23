"""Full rebuild of Fuselage_revB_balsa: build, checks + mass table, pictures, save. exec() inside FreeCAD:
    BAL_SCRIPTS = "<project>/design/cad_fuselage_balsa/scripts"; exec(open(BAL_SCRIPTS + "/run_all.py").read())
Fuselage_revA.FCStd is only read (opened if needed, never saved)."""
import os, sys, io, contextlib, traceback
SCRIPTS = globals().get("BAL_SCRIPTS") or os.path.dirname(os.path.abspath(__file__))
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
ROOT = os.path.dirname(SCRIPTS)
LOG = os.path.join(ROOT, "run_all.log")
buf = io.StringIO()
try:
    with contextlib.redirect_stdout(buf):
        import FreeCAD as App
        ns = {"__name__": "__main__", "BAL_SCRIPTS": SCRIPTS}
        for f in ("build_balsa.py", "check_balsa.py", "export_jigs.py") + (("make_pictures.py",) if App.GuiUp else ()):
            print("##", f)
            exec(open(os.path.join(SCRIPTS, f)).read(), dict(ns))
        import bal_params as BP
        d = App.getDocument(BP.DOC)
        d.recompute()
        d.saveAs(BP.FCSTD)
        print("## saved", d.FileName)
    open(LOG, "w", encoding="utf-8").write(buf.getvalue() + "\nDONE\n")
except Exception:
    open(LOG, "w", encoding="utf-8").write(buf.getvalue() + "\nERROR\n" + traceback.format_exc())
    raise
