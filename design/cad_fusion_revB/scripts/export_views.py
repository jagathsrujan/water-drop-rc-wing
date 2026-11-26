# Bridge job: pictures of the Fusion model, STEP + Fusion archive export.
import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "boot.py")).read())
import os
import time
F = rl("fxlib")
BASE = MODEL
IMG = os.path.join(BASE, "img")
EXP = os.path.join(BASE, "export")
os.makedirs(IMG, exist_ok=True)
os.makedirs(EXP, exist_ok=True)
t0 = time.time()
d = F.design()
root = d.rootComponent
F.hide_label_sketches(root)


def show_all():
    for o in root.allOccurrences:
        o.isLightBulbOn = True


def only(names):
    """Show only the sub-assemblies whose names are given (and everything below them)."""
    keep = set()
    for o in root.allOccurrences:
        if o.component.name in names:
            keep.add(o.fullPathName)
    for o in root.allOccurrences:
        p = o.fullPathName
        o.isLightBulbOn = any(p == k or p.startswith(k + "+") or k.startswith(p + "+") for k in keep) or o.component.name == "WaterDrop_revB"


if globals().get("DO_VIEWS", True):
    show_all()
    F.view(os.path.join(IMG, "aircraft_iso.png"), (-900, -1100, 800), (250, 0, -20))
    F.view(os.path.join(IMG, "aircraft_iso_rear.png"), (1500, 1000, 700), (250, 0, -20))
    F.view(os.path.join(IMG, "aircraft_side.png"), (250, -3000, -20), (250, 0, -20))
    F.view(os.path.join(IMG, "aircraft_top.png"), (250, 0, 3000), (250, 0, -20), up=(-1, 0, 0))
    F.view(os.path.join(IMG, "aircraft_front.png"), (-3000, 0, -20), (250, 0, -20))
    # wing structure without the D-box / centre sheeting and cap strips
    only(["Wing_Ribs", "Wing_Spars", "Wing_Aileron", "Wing_Servo"])
    F.view(os.path.join(IMG, "wing_structure_iso.png"), (-500, -700, 600), (140, 0, 0))
    F.view(os.path.join(IMG, "wing_structure_root.png"), (-150, -260, 160), (110, 60, 5), fit=False)
    vp = F.app.activeViewport
    cam = vp.camera
    cam.viewExtents = 22.0
    vp.camera = cam
    F.refresh()
    vp.saveAsImageFile(os.path.join(IMG, "wing_structure_root.png"), 1600, 1000)
    # tail
    only(["Tail"])
    F.view(os.path.join(IMG, "tail_iso.png"), (400, -300, 300), (710, 0, 40))
    show_all()
    print("views in %.0f s" % (time.time() - t0))

if globals().get("DO_EXPORT", True):
    em = d.exportManager
    t1 = time.time()
    step = os.path.join(EXP, "WaterDrop_revB_fusion.step")
    em.execute(em.createSTEPExportOptions(step, root))
    f3d = os.path.join(EXP, "WaterDrop_revB_fusion.f3d")
    em.execute(em.createFusionArchiveExportOptions(f3d, root))
    import zipfile
    with zipfile.ZipFile(step + ".zip", "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:   # the .step is > 100 MB
        z.write(step, os.path.basename(step))
    print("exported STEP %.1f MB, f3d %.1f MB in %.0f s" % (os.path.getsize(step) / 1e6, os.path.getsize(f3d) / 1e6, time.time() - t1))
