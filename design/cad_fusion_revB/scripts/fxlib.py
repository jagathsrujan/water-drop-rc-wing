"""Fusion helpers for the rev B model (runs inside Fusion through the ClaudeBridge add-in).
Fusion's API works in cm: every helper here takes mm and converts.
Every part is its own component, built flat in its own frame (sketch on the component XY plane, extruded along +Z by
the stock thickness) and placed by the occurrence transform: this keeps each laser part a true flat pattern
(its top-face outline is the cut file) and puts the engraved label on the top face."""
import math
import adsk.core as ac
import adsk.fusion as af

MM = 0.1
app = ac.Application.get()
ENGRAVE = 0.2          # label engraving depth (mm)
STATS = {"parts": 0}


def P(u, v, w=0.0):
    return ac.Point3D.create(u * MM, v * MM, w * MM)


def Vec(x, y, z):
    return ac.Vector3D.create(x, y, z)


def VI(mm):
    return ac.ValueInput.createByReal(mm * MM)


def design():
    return af.Design.cast(app.activeProduct)


def refresh():
    import adsk
    adsk.doEvents()
    try:
        app.activeViewport.refresh()
    except Exception:
        pass


def new_design(root_name):
    app.preferences.generalPreferences.defaultModelingOrientation = ac.DefaultModelingOrientations.ZUpModelingOrientation
    app.documents.add(ac.DocumentTypes.FusionDesignDocumentType)
    d = design()
    d.designType = af.DesignTypes.ParametricDesignType
    d.fusionUnitsManager.distanceDisplayUnits = af.DistanceUnits.MillimeterDistanceUnits
    return d   # the root component takes the document name (set when the document is saved)


# ---------------- frames ----------------
def _norm(v):
    L = math.sqrt(sum(c * c for c in v))
    return tuple(c / L for c in v)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def frame(origin, xdir, ydir):
    """Right-handed frame: local u along xdir, v along ydir, thickness along xdir x ydir."""
    x = _norm(xdir)
    y = _norm(ydir)
    z = _norm(_cross(x, y))
    y = _cross(z, x)
    return (tuple(origin), x, y, z)


def matrix(fr):
    o, x, y, z = fr
    m = ac.Matrix3D.create()
    m.setWithCoordinateSystem(P(*o), Vec(*x), Vec(*y), Vec(*z))
    return m


def to_world(fr, u, v, w=0.0):
    o, x, y, z = fr
    return tuple(o[i] + x[i] * u + y[i] * v + z[i] * w for i in range(3))


# ---------------- components ----------------
def group(parent, name):
    """An empty sub-assembly component (identity transform)."""
    for occ in parent.occurrences:
        if occ.component.name == name:
            return occ.component
    occ = parent.occurrences.addNewComponent(ac.Matrix3D.create())
    occ.component.name = name
    return occ.component


def _new_comp(parent, name, fr):
    occ = parent.occurrences.addNewComponent(matrix(fr))
    comp = occ.component
    comp.name = name
    return occ, comp


def draw_poly(sk, poly):
    lines = sk.sketchCurves.sketchLines
    pts = [P(u, v) for u, v in poly]
    first = None
    prev = None
    for i in range(len(pts)):
        a = prev.endSketchPoint if prev is not None else pts[i]
        b = first.startSketchPoint if (i == len(pts) - 1 and first is not None) else pts[(i + 1) % len(pts)]
        ln = lines.addByTwoPoints(a, b)
        if first is None:
            first = ln
        prev = ln


def draw_shape(sk, shp):
    """shp: polygon list, or ('circle', u, v, r)."""
    if isinstance(shp, tuple) and shp and shp[0] == "circle":
        sk.sketchCurves.sketchCircles.addByCenterRadius(P(shp[1], shp[2]), shp[3] * MM)
    else:
        draw_poly(sk, shp)


def _largest_profile(sk):
    best, ba = None, -1
    for pr in sk.profiles:
        a = pr.areaProperties(af.CalculationAccuracy.LowCalculationAccuracy).area
        if a > ba:
            best, ba = pr, a
    return best


def _all_profiles(sk):
    oc = ac.ObjectCollection.create()
    for pr in sk.profiles:
        oc.add(pr)
    return oc


def _profiles_inside(sk, shapes):
    """Only the sketch profiles that lie inside one of the drawn shapes (a closed frame of bars also encloses its
    window, which must not be extruded)."""
    import geo as G
    polys = [s if not (isinstance(s, tuple) and s and s[0] == "circle") else G.circle_poly(s[1], s[2], s[3], 48) for s in shapes]
    oc = ac.ObjectCollection.create()
    for pr in sk.profiles:
        c = pr.areaProperties(af.CalculationAccuracy.LowCalculationAccuracy).centroid
        pt = (c.x / MM, c.y / MM)
        if any(G.point_in_poly(pt, q) for q in polys):
            oc.add(pr)
    return oc if oc.count else _all_profiles(sk)


def _shape_bbox(shp):
    if isinstance(shp, tuple) and shp and shp[0] == "circle":
        _, u, v, r = shp
        return u - r, u + r, v - r, v + r
    us, vs = [q[0] for q in shp], [q[1] for q in shp]
    return min(us), max(us), min(vs), max(vs)


def _overlap(b1, b2):
    return b1[0] < b2[1] and b2[0] < b1[1] and b1[2] < b2[3] and b2[2] < b1[3]


def _plane(comp, w):
    if abs(w) < 1e-9:
        return comp.xYConstructionPlane
    pi = comp.constructionPlanes.createInput()
    pi.setByOffset(comp.xYConstructionPlane, VI(w))
    pl = comp.constructionPlanes.add(pi)
    pl.isLightBulbOn = False
    return pl


def _prism_feature(comp, shapes, w0, w1, op, body):
    sk = comp.sketches.add(_plane(comp, w0))
    sk.isComputeDeferred = True
    for s in shapes:
        draw_shape(sk, s)
    sk.isComputeDeferred = False
    ei = comp.features.extrudeFeatures.createInput(_profiles_inside(sk, shapes), op)
    ei.setDistanceExtent(False, VI(w1 - w0))
    if body is not None:
        ei.participantBodies = [body]
    f = comp.features.extrudeFeatures.add(ei)
    sk.isVisible = False
    return f


def add_join(occ_body, shapes, w0, w1):
    """Join an extra prism (local w0..w1) to the part body."""
    occ, body = occ_body
    _prism_feature(occ.component, shapes, w0, w1, af.FeatureOperations.JoinFeatureOperation, body)


def add_pocket(occ_body, shapes, w0, w1):
    """Cut a blind pocket (local w0..w1) into the part body."""
    occ, body = occ_body
    _prism_feature(occ.component, shapes, w0, w1, af.FeatureOperations.CutFeatureOperation, body)


def part(parent, name, outline, t, fr, cutters=(), mat=None, labels=(), z0=0.0, note=""):
    """A prism part: outline (local u, v polygon, mm) extruded from local w = z0 to z0 + t, minus the cutters
    (polygons or ('circle', u, v, r), through). labels: [(text, u, v, height)] engraved ENGRAVE deep into the top
    face (w = z0 + t), text along +u. Returns (occurrence, body)."""
    occ, comp = _new_comp(parent, name, fr)
    feats = comp.features
    base = comp.xYConstructionPlane
    if abs(z0) > 1e-9:
        pi = comp.constructionPlanes.createInput()
        pi.setByOffset(base, VI(z0))
        base = comp.constructionPlanes.add(pi)
        base.isLightBulbOn = False
    sk = comp.sketches.add(base)
    sk.name = "outline"
    sk.isComputeDeferred = True
    draw_poly(sk, outline)
    sk.isComputeDeferred = False
    prof = _largest_profile(sk)
    ext = feats.extrudeFeatures.addSimple(prof, VI(t), af.FeatureOperations.NewBodyFeatureOperation)
    body = ext.bodies.item(0)
    body.name = name
    sk.isVisible = False
    ob = _shape_bbox(outline)
    cl = [c for c in cutters if _overlap(_shape_bbox(c), ob)]
    if cl:
        sk2 = comp.sketches.add(base)
        sk2.name = "cutouts"
        sk2.isComputeDeferred = True
        for c in cl:
            draw_shape(sk2, c)
        sk2.isComputeDeferred = False
        ei = feats.extrudeFeatures.createInput(_all_profiles(sk2), af.FeatureOperations.CutFeatureOperation)
        ei.setSymmetricExtent(VI(4 * t + 20), True)
        ei.participantBodies = [body]
        feats.extrudeFeatures.add(ei)
        sk2.isVisible = False
    if labels:
        engrave(comp, body, labels, z0 + t)
    if mat:
        set_material(body, mat)
    STATS["parts"] += 1
    if STATS["parts"] % 3 == 0:
        refresh()
    return occ, body


def engrave(comp, body, labels, w_top):
    pi = comp.constructionPlanes.createInput()
    pi.setByOffset(comp.xYConstructionPlane, VI(w_top))
    pl = comp.constructionPlanes.add(pi)
    pl.isLightBulbOn = False
    sk = comp.sketches.add(pl)
    sk.name = "label"
    texts = []
    for lab in labels:
        txt, u, v, h = lab[:4]
        n_lines = txt.count("\n") + 1
        wbox = max(len(s) for s in txt.split("\n")) * h * 0.75 + h
        hbox = n_lines * h * 1.45 + 0.5 * h
        ti = sk.sketchTexts.createInput2(txt, h * MM)
        ti.setAsMultiLine(P(u - wbox / 2, v - hbox / 2), P(u + wbox / 2, v + hbox / 2),
                          ac.HorizontalAlignments.CenterHorizontalAlignment,
                          ac.VerticalAlignments.MiddleVerticalAlignment, 0)
        try:
            ti.fontName = "Arial"
        except Exception:
            pass
        texts.append(sk.sketchTexts.add(ti))
    for st in texts:
        try:
            ei = comp.features.extrudeFeatures.createInput(st, af.FeatureOperations.CutFeatureOperation)
            ei.setOneSideExtent(af.DistanceExtentDefinition.create(VI(ENGRAVE)), af.ExtentDirections.NegativeExtentDirection)
            ei.participantBodies = [body]
            comp.features.extrudeFeatures.add(ei)
        except Exception as e:  # text outside the face: keep the sketch text only
            print("  label not engraved on %s: %s" % (comp.name, str(e).splitlines()[0][:80]))
    sk.isVisible = False


def revolve_part(parent, name, profile_vu, fr, mat=None):
    """Solid of revolution: profile in local (u = axial, v = radius >= 0) revolved about the local u axis."""
    occ, comp = _new_comp(parent, name, fr)
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.isComputeDeferred = True
    draw_poly(sk, profile_vu)
    axis = sk.sketchCurves.sketchLines.addByTwoPoints(P(-1000, 0), P(1000, 0))
    axis.isConstruction = True
    sk.isComputeDeferred = False
    prof = _largest_profile(sk)
    ri = comp.features.revolveFeatures.createInput(prof, axis, af.FeatureOperations.NewBodyFeatureOperation)
    ri.setAngleExtent(False, ac.ValueInput.createByReal(2 * math.pi))
    rf = comp.features.revolveFeatures.add(ri)
    body = rf.bodies.item(0)
    body.name = name
    sk.isVisible = False
    if mat:
        set_material(body, mat)
    STATS["parts"] += 1
    refresh()
    return occ, body


def tube(parent, name, p0, p1, r_out, r_in=0.0, mat=None):
    """Cylinder / tube between two world points."""
    d = tuple(b - a for a, b in zip(p0, p1))
    L = math.sqrt(sum(c * c for c in d))
    ref = (0, 0, 1) if abs(d[2]) < 0.9 * L else (1, 0, 0)
    x = _norm(_cross(ref, d))
    y = _norm(_cross(d, x))
    fr = (tuple(p0), x, y, _norm(d))
    cut = [("circle", 0, 0, r_in)] if r_in > 0 else []
    return part(parent, name, [(r_out * math.cos(2 * math.pi * k / 64), r_out * math.sin(2 * math.pi * k / 64)) for k in range(64)],
                L, fr, cutters=cut, mat=mat)


# ---------------- materials ----------------
MATS = {   # key: (name, density g/cm3, colour RGB 0-255)
    "balsa_med": ("Balsa medium", 0.14, (222, 190, 130)),
    "balsa_light": ("Balsa light", 0.10, (240, 218, 165)),
    "balsa_hard": ("Balsa hard", 0.16, (196, 152, 96)),
    "ply": ("Birch ply", 0.65, (190, 145, 92)),
    "liteply": ("Lite-ply", 0.45, (205, 170, 115)),
    "petg": ("PETG", 1.27, (60, 125, 215)),
    "pla_jig": ("PLA jig", 1.24 * 0.30, (240, 120, 40)),
    "carbon": ("Carbon", 1.55, (35, 35, 38)),
    "birch": ("Birch dowel", 0.70, (200, 160, 110)),
    "steel": ("Steel", 7.85, (160, 160, 170)),
    "pet": ("PET bottle", 1.38, (170, 210, 240)),
    "water": ("Water", 1.00, (90, 150, 255)),
    "rubber": ("EVA gasket", 0.10, (30, 30, 30)),
    "elec": ("Electronics (lumped)", 1.00, (70, 70, 80)),
}
_MCACHE, _ACACHE = {}, {}


def _base_material():
    for libname in ("Fusion Material Library", "Fusion 360 Material Library"):
        lib = app.materialLibraries.itemByName(libname)
        if lib:
            for nm in ("ABS Plastic", "Plastic", "Steel"):
                m = lib.materials.itemByName(nm)
                if m:
                    return m
            return lib.materials.item(0)
    return None


def _base_appearance():
    for libname in ("Fusion Appearance Library", "Fusion 360 Appearance Library"):
        lib = app.materialLibraries.itemByName(libname)
        if lib:
            for nm in ("Plastic - Matte (White)", "Paint - Enamel Glossy (White)", "Plastic - Glossy (White)"):
                a = lib.appearances.itemByName(nm)
                if a:
                    return a
    return None


def get_material(key):
    if key in _MCACHE:
        return _MCACHE[key]
    d = design()
    name, rho, rgb = MATS[key]
    m = d.materials.itemByName(name)
    if m is None:
        m = d.materials.addByCopy(_base_material(), name)
        dp = m.materialProperties.itemById("structural_Density")
        dp.value = rho * 1000.0          # kg/m3
    a = d.appearances.itemByName(name)
    if a is None:
        a = d.appearances.addByCopy(_base_appearance(), name)
        for i in range(a.appearanceProperties.count):
            pr = a.appearanceProperties.item(i)
            if pr.objectType == ac.ColorProperty.classType():
                try:
                    pr.value = ac.Color.create(rgb[0], rgb[1], rgb[2], 0)
                except Exception:
                    pass
                break
    _MCACHE[key] = (m, a)
    return m, a


def set_material(body, key):
    m, a = get_material(key)
    body.material = m
    body.appearance = a


# ---------------- views ----------------
def view(path, eye, target=(0, 0, 0), up=(0, 0, 1), w=1600, h=1000, fit=True):
    vp = app.activeViewport
    cam = vp.camera
    cam.isSmoothTransition = False
    cam.eye = P(*eye)
    cam.target = P(*target)
    cam.upVector = Vec(*up)
    cam.cameraType = ac.CameraTypes.OrthographicCameraType
    vp.camera = cam
    if fit:
        vp.fit()
    refresh()
    vp.saveAsImageFile(path, w, h)


def iso(path, dist=2000, w=1600, h=1000):
    view(path, (-dist, -dist, dist * 0.8), w=w, h=h)


def show_groups(top, names, visible):
    """Light-bulb on/off for the sub-assemblies named (searched recursively below top)."""
    for occ in top.allOccurrences:
        if occ.component.name in names:
            occ.isLightBulbOn = visible


def hide_label_sketches(top):
    for comp in [top] + [o.component for o in top.allOccurrences]:
        for sk in comp.sketches:
            if sk.name == "label":
                sk.isVisible = False


def group_tf(parent, name, mat3d):
    """A sub-assembly component placed by a transform (e.g. the wing at its incidence)."""
    for occ in parent.occurrences:
        if occ.component.name == name:
            return occ.component
    occ = parent.occurrences.addNewComponent(mat3d)
    occ.component.name = name
    return occ.component


def rot_y(deg):
    m = ac.Matrix3D.create()
    m.setToRotation(math.radians(deg), Vec(0, 1, 0), P(0, 0, 0))
    return m


def box(parent, name, x0, x1, y0, y1, z0, z1, mat=None):
    import geo as G
    fr = G.frame((0.0, 0.0, z0), (1, 0, 0), (0, 1, 0))
    return part(parent, name, G.rect(x0, x1, y0, y1), z1 - z0, fr, mat=mat)


def build_list(parent, parts, fails, fit_every=15):
    """Build a list of part dicts (pod.py / wing.py format) under parent, one sub-group per p['grp']."""
    for i, p in enumerate(parts):
        try:
            grp = group(parent, p["grp"])
            ob = part(grp, p["name"], p["outline"], p["t"], p["fr"], cutters=p["cutters"], mat=p["mat"],
                      labels=p["labels"], z0=p["z0"])
            for shapes, w0, w1 in p.get("joins", []):
                add_join(ob, shapes, w0, w1)
            for shapes, w0, w1 in p.get("pockets", []):
                add_pocket(ob, shapes, w0, w1)
            if p.get("joins") and p.get("mat"):
                for b in ob[0].component.bRepBodies:      # a join that does not touch makes a new body: same material
                    set_material(b, p["mat"])
            if i % fit_every == 0:
                app.activeViewport.fit()
        except Exception as e:
            fails.append((p["name"], str(e).splitlines()[-1][:200]))
