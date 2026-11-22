"""Wing rev A - document helpers (FreeCAD GUI or headless)."""
import FreeCAD as App
import Part
from FreeCAD import Vector as V
import wing_params as P

DOC = "Wing_revA"
COLORS = {
    "sheet": (0.96, 0.88, 0.70), "light": (0.94, 0.84, 0.62), "medium": (0.86, 0.70, 0.48),
    "hard": (0.70, 0.50, 0.30), "carbon": (0.12, 0.12, 0.12), "petg": (0.15, 0.45, 0.85),
    "steel": (0.62, 0.62, 0.68), "servo": (0.25, 0.25, 0.30),
}


def doc():
    d = App.listDocuments().get(DOC)
    if d is None:
        d = App.newDocument(DOC)
    return d


def group(name):
    d = doc()
    g = d.getObject(name)
    if g is None:
        g = d.addObject("App::DocumentObjectGroup", name)
    return g


def clear_group(name):
    d = doc()
    g = d.getObject(name)
    if g is None:
        return
    for o in list(g.Group):
        d.removeObject(o.Name)


def put(name, shape, material, grp, note=""):
    """One Part::Feature per part. material = key of P.RHO (density used by the mass table)."""
    d = doc()
    if d.getObject(name) is not None:
        d.removeObject(name)
    o = d.addObject("Part::Feature", name)
    o.Shape = shape
    o.addProperty("App::PropertyString", "Material", "Wing")
    o.Material = material
    o.addProperty("App::PropertyString", "Note", "Wing")
    o.Note = note
    group(grp).addObject(o)
    try:
        o.ViewObject.ShapeColor = COLORS.get(material, (0.8, 0.8, 0.8))
        if material == "carbon":
            o.ViewObject.LineColor = (0.3, 0.3, 0.3)
        o.ViewObject.Lighting = "Two side"
        if material == "petg" and name.startswith(("ServoHatch", "ServoFrame", "RubPlate")):
            o.ViewObject.DisplayMode = "Shaded"      # dense facet edges of the curved bands show black
    except Exception:
        pass
    return o


def mirror_y(shape):
    return shape.mirror(V(0, 0, 0), V(0, 1, 0))


def zcyl(xc, yc, d, z0=-60.0, z1=60.0):
    c = Part.makeCylinder(d / 2.0, z1 - z0, V(xc, yc, z0), V(0, 0, 1))
    return c


def ycyl(xc, zc, d, y0, y1):
    return Part.makeCylinder(d / 2.0, y1 - y0, V(xc, y0, zc), V(0, 1, 0))


def snap_window(path, view, box, w=1600, h=1100, skip=(), section=False, zoom=1.0):
    """Picture of temporary copies of all parts cut to `box` (Part.makeBox). Temporary objects are deleted after.
    section=True cuts with the box as a half-space (for section views)."""
    import FreeCADGui as Gui
    d = doc()
    vis, tmp = {}, []
    for o in [o for o in d.Objects if o.TypeId == "Part::Feature"]:
        vis[o.Name] = o.ViewObject.Visibility
        o.ViewObject.Visibility = False
        if o.Name in skip or o.Name.startswith("TMP_"):
            continue
        if not o.Shape.BoundBox.intersect(box.BoundBox):
            continue
        c = o.Shape.common(box)
        if c.Volume < 1e-6:
            continue
        t = d.addObject("Part::Feature", "TMP_" + o.Name)
        t.Shape = c
        t.ViewObject.ShapeColor = o.ViewObject.ShapeColor
        tmp.append(t.Name)
    v = Gui.ActiveDocument.ActiveView
    v.setCameraType("Orthographic")
    try:
        v.setAnimationEnabled(False)
    except Exception:
        pass
    set_view(v, view)
    Gui.updateGui(); v.fitAll(); Gui.updateGui()
    _zoom(v, zoom)
    v.saveImage(path, w, h, "White")
    for n in tmp:
        d.removeObject(n)
    for n, s in vis.items():
        if d.getObject(n):
            d.getObject(n).ViewObject.Visibility = s
    Gui.updateGui()


def set_view(v, name):
    """Aircraft views. top: span horizontal, LE up. front: from ahead (looking aft, -X side).
    profile: airfoil section seen from the right tip (+Y). iso: FreeCAD isometric."""
    try:
        v.setAnimationEnabled(False)
    except Exception:
        pass
    if name == "top":
        v.setCameraOrientation(App.Rotation(V(0, 0, 1), 90))
    elif name == "bottom":
        v.setCameraOrientation(App.Rotation(V(0, 0, 1), 90).multiply(App.Rotation(V(1, 0, 0), 180)))
    elif name == "front":
        v.viewLeft()
    elif name == "profile":
        v.viewRear()
    elif name == "iso":
        v.viewIsometric()
    else:
        getattr(v, name)()


def snap_all(path, view, w=1800, h=1000, hide=(), zoom=1.0):
    import FreeCADGui as Gui
    d = doc()
    vis = {}
    for o in [o for o in d.Objects if o.TypeId == "Part::Feature"]:
        vis[o.Name] = o.ViewObject.Visibility
        o.ViewObject.Visibility = o.Name not in hide
    v = Gui.ActiveDocument.ActiveView
    v.setCameraType("Orthographic")
    set_view(v, view)
    Gui.updateGui(); v.fitAll(); Gui.updateGui()
    _zoom(v, zoom)
    v.saveImage(path, w, h, "White")
    for n, s in vis.items():
        d.getObject(n).ViewObject.Visibility = s


def _zoom(v, f):
    """Orthographic zoom after fitAll (f < 1 = closer): scale 'height' in the Inventor camera string."""
    if f == 1.0:
        return
    import re
    import FreeCADGui as Gui
    cam = v.getCamera()
    m = re.search(r"height\s+([-0-9.eE+]+)", cam)
    if m:
        cam = cam[:m.start(1)] + "%.6f" % (float(m.group(1)) * f) + cam[m.end(1):]
        v.setCamera(cam)
    Gui.updateGui()
