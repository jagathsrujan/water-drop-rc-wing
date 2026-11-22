"""Render the FreeCAD frames of the build video (run inside the FreeCAD GUI with the Wing_revA document open).
Set SEGS = [...segment ids...] (and optionally MAXF for a test) before exec(). Frames: frames/<id>/raw_0000.png (1920 x 840)."""
import os, json, math, time
import FreeCAD as App, FreeCADGui as Gui, Part
from FreeCAD import Vector as V
VID = globals().get("VIDEO_DIR") or os.path.join(os.path.dirname(App.ActiveDocument.FileName), "..", "video")
VID = os.path.abspath(VID)
FPS = 8
W, H = 1920, 840
HL = (1.0, 0.45, 0.05)
doc = App.ActiveDocument
v = Gui.ActiveDocument.ActiveView
v.setCameraType("Orthographic"); v.setAnimationEnabled(False)
NAR = {s["id"]: s for s in json.load(open(os.path.join(VID, "narration.json")))}
PARTS = [o for o in doc.Objects if o.TypeId == "Part::Feature" and not o.Name.startswith("TMP_")]
ORIG = {o.Name: (o.ViewObject.ShapeColor, o.ViewObject.Transparency, o.ViewObject.Visibility) for o in PARTS}

def pick(*prefixes):
    return [o.Name for o in PARTS if o.Name.startswith(prefixes)]

STEPS = {   # segment id -> (new parts, tilt deg, orbit deg per frame, zoom)
 "01_overview": (None, 58, 360.0 / (NAR["01_overview"]["seg"] * FPS), 0.56),
 "08_spar": (pick("SparBalsa_Bot", "SparCarbon_Bot"), 58, 0.35, 0.56),
 "09_ribs": (pick("Rib_"), 58, 0.35, 0.56),
 "10_le_te": (pick("LE", "FalseSpar", "TE_", "RibAft_"), 58, 0.35, 0.56),
 "11_webs": (pick("SparBalsa_Top", "SparCarbon_Top", "ShearWeb"), 58, 0.35, 0.56),
 "12_top": (pick("DBox_Top", "CSheet_Top", "Caps_"), 58, 0.35, 0.56),
 "13_flip": (pick("DBox_Bot", "CSheet_Bot", "ServoFrame_"), 122, 0.35, 0.56),
 "14_tips": (pick("TipRib", "TipCap"), 58, 0.35, 0.56),
 "15_ailerons": (pick("Ail_"), 58, 0.35, 0.56),
 "17_servo": (pick("Horn_", "Servo_MG90S", "ServoArm", "ServoHatch", "Pushrod"), 122, 0.25, 0.85),
 "18_final": (pick("RubPlate"), 58, 0.45, 0.56),
}
ORDER = ["08_spar", "09_ribs", "10_le_te", "11_webs", "12_top", "13_flip", "14_tips", "15_ailerons", "17_servo", "18_final"]
TILT_PREV = {"08_spar": 58, "09_ribs": 58, "10_le_te": 58, "11_webs": 58, "12_top": 58, "13_flip": 58, "14_tips": 122,
             "15_ailerons": 58, "17_servo": 58, "18_final": 122, "01_overview": 58}
AZ0 = {"01_overview": 20.0}
G0, g = {}, 0
for sid in ORDER:     # global frame counter across the step segments (smooth swing, never end-on)
    G0[sid] = g
    g += int(round(NAR[sid]["seg"] * FPS))

def az_at(sid, i):
    if sid == "01_overview":
        return AZ0[sid] + STEPS[sid][2] * i
    return 50.0 + 15.0 * math.sin(2 * math.pi * (G0[sid] + i) / 360.0)


def zoom(f):
    import re
    cam = v.getCamera()
    m = re.search(r"height\s+([-0-9.eE+]+)", cam)
    v.setCamera(cam[:m.start(1)] + "%.6f" % (float(m.group(1)) * f) + cam[m.end(1):])


def orient(azd, tilt):
    v.setCameraOrientation(App.Rotation(V(0, 0, 1), azd).multiply(App.Rotation(V(1, 0, 0), tilt)))


def restore():
    for o in PARTS:
        c, t, vis = ORIG[o.Name]
        o.ViewObject.ShapeColor = c; o.ViewObject.Transparency = t; o.ViewObject.Visibility = True
    for o in [o for o in doc.Objects if o.Name.startswith("TMP_")]:
        doc.removeObject(o.Name)
    Gui.updateGui()


def render(sid, maxf=None):
    new, tilt, step, zf = STEPS[sid]
    out = os.path.join(VID, "frames", sid)
    os.makedirs(out, exist_ok=True)
    n = int(round(NAR[sid]["seg"] * FPS))
    if maxf:
        n = min(n, maxf)
    restore()
    # parts visible in this segment = all parts of earlier steps + new
    if sid == "01_overview":
        shown, new = [o.Name for o in PARTS], []
    else:
        idx = ORDER.index(sid)
        shown = sum([STEPS[s][0] for s in ORDER[:idx + 1]], [])
    objs = {o.Name: o for o in PARTS}
    closeup = sid == "17_servo"
    # fit once with the whole wing (constant scale between steps)
    for o in PARTS:
        o.ViewObject.Visibility = True
    orient(az_at(sid, 0), tilt); Gui.updateGui()
    if closeup:
        box = Part.makeBox(260, 110, 80, V(60, 95, -40))
        tmp = {}
        for nme in shown:
            o = objs[nme]
            if not o.Shape.BoundBox.intersect(box.BoundBox):
                continue
            c = o.Shape.common(box)
            if c.Volume < 1e-6:
                continue
            t = doc.addObject("Part::Feature", "TMP_" + nme); t.Shape = c
            t.ViewObject.ShapeColor = ORIG[nme][0]; t.ViewObject.Lighting = "Two side"
            if nme.startswith(("ServoHatch", "ServoFrame")):
                t.ViewObject.DisplayMode = "Shaded"
            tmp[nme] = t
        for o in PARTS:
            o.ViewObject.Visibility = False
        objs = tmp
        shown = [s for s in shown if s in tmp]
        new = [s for s in new if s in tmp]
    # bounds markers: two tiny white spheres at the box corners, so fitAll gives the same centre and scale every frame
    bb = box.BoundBox if closeup else App.BoundBox(-5, -500, -15, 285, 500, 35)
    mk = doc.addObject("Part::Feature", "TMP_BOUNDS")
    mk.Shape = Part.makeCompound([Part.makeSphere(0.05, V(bb.XMin, bb.YMin, bb.ZMin)), Part.makeSphere(0.05, V(bb.XMax, bb.YMax, bb.ZMax))])
    mk.ViewObject.ShapeColor = (1.0, 1.0, 1.0); mk.ViewObject.DisplayMode = "Shaded"
    Gui.updateGui()
    for nme, o in objs.items():
        o.ViewObject.Visibility = nme in shown
        if nme in new:
            o.ViewObject.ShapeColor = HL
    t0 = time.time()
    for i in range(n):
        a = min(1.0, i / (1.5 * FPS))              # fade-in over 1.5 s
        for nme in new:
            objs[nme].ViewObject.Transparency = int(round(100 * (1 - a)))
        tl = TILT_PREV[sid] + (tilt - TILT_PREV[sid]) * min(1.0, i / (2.0 * FPS))
        orient(az_at(sid, i), tl)
        Gui.updateGui(); v.fitAll(); zoom(zf); Gui.updateGui()
        v.saveImage(os.path.join(out, "raw_%04d.png" % i), W, H, "White")
    restore()
    open(os.path.join(out, "DONE"), "w").write("%d frames %.0f s\n" % (n, time.time() - t0))
    return n

for sid in globals().get("SEGS", []):
    render(sid, globals().get("MAXF"))
