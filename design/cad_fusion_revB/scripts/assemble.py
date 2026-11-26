# Bridge job: make the Fusion model an assembly that moves like the aircraft.
# - every control surface (aileron R / L, elevator = both halves + joiner + horn, rudder + horn) becomes one component
# - the fixed airframe (pod, wing, tail, reservoir, electronics) is one rigid group: drag any part, the aircraft moves
# - each surface has an as-built revolute joint on its hinge line, limited to +-25 deg: drag it and it swings
import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "boot.py")).read())
import math
import adsk.core as ac
import adsk.fusion as af
F = rl("fxlib")
d = F.design()
root = d.rootComponent
LIMIT = math.radians(25.0)

SURFACES = {
    "Aileron-R": ["AIL-LE-R", "AIL-TE-R", "A112-R", "A165-R", "A220-R", "A275-R", "A330-R", "A385-R", "A437-R", "AIL-HORN-R", "AH-R"],
    "Aileron-L": ["AIL-LE-L", "AIL-TE-L", "A112-L", "A165-L", "A220-L", "A275-L", "A330-L", "A385-L", "A437-L", "AIL-HORN-L", "AH-L"],
    "Elevator": ["ELEV-R", "ELEV-L", "JOINER", "JOINER-LEG-R", "JOINER-LEG-L", "HORN-E"],
    "Rudder": ["RUDDER", "HORN-R"],
}
# hinge axis: an edge of this part that lies on the hinge line, in the part's own (native) frame
AXIS_PART = {"Aileron-R": "AIL-LE-R", "Aileron-L": "AIL-LE-L", "Elevator": "ELEV-R", "Rudder": "RUDDER"}


def occ_by_name(name):
    for o in root.allOccurrences:
        if o.component.name == name:
            return o
    return None


# 0. clear an earlier set-up (joints, rigid groups)
for c in [root] + [o.component for o in root.allOccurrences]:     # joints live in the lowest common parent
    for j in list(c.asBuiltJoints):
        j.deleteMe()
    for g in list(c.rigidGroups):
        g.deleteMe()

top_occ = occ_by_name("WaterDrop_revB")
top = top_occ.component
log = []

# 1. one component per moving surface (identity transform, under WaterDrop_revB), parts moved in (world position kept)
for sname, parts in SURFACES.items():
    so = occ_by_name(sname)
    if so is None:
        so = top.occurrences.addNewComponent(ac.Matrix3D.create())
        so.component.name = sname
        so = occ_by_name(sname)
    for pn in parts:
        o = occ_by_name(pn)
        if o is None:
            log.append("missing " + pn)
            continue
        if o.assemblyContext and o.assemblyContext.component.name == sname:
            continue
        o.moveToComponent(so)
print("surfaces grouped", log)


# 2. hinge-axis edges (native frames: AIL-LE u=X v=Z, apex (210, ZH); ELEV u=X v=Y, LE edge u=739.9 w=0;
#    RUDDER u=X v=Z, LE edge u=739.9 w=0)
import wing as W
import tail as TL
targets = {"AIL-LE-R": (W.P.AIL_X[0], W.ZH, None), "AIL-LE-L": (W.P.AIL_X[0], W.ZH, None),
           "ELEV-R": (TL.XH1, None, 0.0), "RUDDER": (TL.XH1, None, 0.0)}


def axis_edge(part_name):
    o = occ_by_name(part_name)
    body = o.bRepBodies.item(0)                       # proxy in assembly context
    nat = o.component.bRepBodies.item(0)
    ux, vv, ww = targets[part_name]
    best, bl = None, -1
    for i in range(nat.edges.count):
        e = nat.edges.item(i)
        if e.geometry.curveType != 0:                 # Line3DCurveType
            continue
        a, b = e.startVertex.geometry, e.endVertex.geometry
        pts = [(a.x * 10, a.y * 10, a.z * 10), (b.x * 10, b.y * 10, b.z * 10)]
        if any(abs(p[0] - ux) > 0.05 for p in pts):
            continue
        if vv is not None and any(abs(p[1] - vv) > 0.05 for p in pts):
            continue
        if ww is not None and any(abs(p[2] - ww) > 0.05 for p in pts):
            continue
        L = math.dist(pts[0], pts[1])
        if L > bl:
            best, bl = i, L
    return body.edges.item(best), bl


# 3. rigid groups: the airframe, and the jig set (pod jigs + base + pins + tail jigs + seat gauges) as a second one.
#    Fusion fixes a rigid group's members when it is made, so this step runs after every rebuild of parts.
groups = {"Airframe": ("Pod", "Wing", "Tail", "Reservoir", "Electronics"), "Jig set": ("Jigs",)}
moving = set(SURFACES)
for gname, members in groups.items():
    occs = ac.ObjectCollection.create()
    for nm in members:
        o = occ_by_name(nm)
        if o:
            occs.add(o)
    if occs.count < 1:
        print("rigid group %s: no members in the design (not built yet) - skipped" % gname)
        continue
    rg = root.rigidGroups.add(occs, True)
    rg.name = gname
# every part must be either in a rigid group or inside a moving surface
leaf = [o for o in root.allOccurrences if o.component.bRepBodies.count > 0]
in_groups = set()
for c in [root] + [o.component for o in root.allOccurrences]:
    for g in c.rigidGroups:
        for o in g.occurrences:
            in_groups.add(o.fullPathName)
free = [o.component.name for o in leaf if not any(o.fullPathName == p or o.fullPathName.startswith(p + "+") for p in in_groups)
        and not any(("+" + m + ":") in ("+" + o.fullPathName) for m in moving)]
print("rigid groups: %s; parts not held: %d %s" % (list(groups), len(free), free[:10]))

# 4. revolute joints
FIX = {"Aileron-R": "Wing", "Aileron-L": "Wing", "Elevator": "Tail", "Rudder": "Tail"}
joints = {}
for sname, pn in AXIS_PART.items():
    edge, L = axis_edge(pn)
    geo = af.JointGeometry.createByCurve(edge, af.JointKeyPointTypes.MiddleKeyPoint)
    inp = root.asBuiltJoints.createInput(occ_by_name(sname), occ_by_name(FIX[sname]), geo)
    inp.setAsRevoluteJointMotion(af.JointDirections.CustomJointDirection, edge)
    j = root.asBuiltJoints.add(inp)
    j.name = "Hinge " + sname
    lim = j.jointMotion.rotationLimits
    lim.isMinimumValueEnabled = True
    lim.minimumValue = -LIMIT
    lim.isMaximumValueEnabled = True
    lim.maximumValue = LIMIT
    lim.isRestValueEnabled = True
    lim.restValue = 0.0
    joints[sname] = j
    print("joint %-10s axis edge %.1f mm" % (sname, L))
F.refresh()
