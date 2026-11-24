# Bridge job: exact cut geometry of every laser part = the loops of its bottom face (the face without the engraving),
# in the part's own flat frame (u, v). Writes ../dxf/loops.json for laser.py.
exec(open(r"C:\Projects\water-drop-rc-wing\design\cad_fusion_revB\scripts\boot.py").read())
import json
import os
import time
F = rl("fxlib"); L = rl("laser")
OUT = r"C:\Projects\water-drop-rc-wing\design\cad_fusion_revB\dxf\loops.json"
t0 = time.time()
want = {p["name"]: p for p in L.laser_parts()}
root = F.design().rootComponent
data, missing = {}, set(want)
TOL = 0.002          # cm (0.02 mm) chord tolerance for curves


def loops_of(face):
    out = []
    for lp in face.loops:
        pts = []
        for ce in lp.coEdges:
            ev = ce.edge.evaluator
            ok, p0, p1 = ev.getParameterExtents()
            ok, strokes = ev.getStrokes(p0, p1, TOL)
            seq = [(round(p.x * 10, 4), round(p.y * 10, 4)) for p in strokes]
            if ce.isOpposedToEdge:
                seq.reverse()
            if pts and seq and abs(pts[-1][0] - seq[0][0]) < 1e-3 and abs(pts[-1][1] - seq[0][1]) < 1e-3:
                seq = seq[1:]
            pts += seq
        if len(pts) > 2 and abs(pts[0][0] - pts[-1][0]) < 1e-3 and abs(pts[0][1] - pts[-1][1]) < 1e-3:
            pts = pts[:-1]
        out.append(dict(outer=lp.isOuter, pts=pts))
    return out


for occ in root.allOccurrences:
    comp = occ.component
    if comp.name not in want or comp.bRepBodies.count == 0:
        continue
    body = comp.bRepBodies.item(0)
    zmin = body.boundingBox.minPoint.z
    best, ba = None, -1.0
    for f in body.faces:
        if f.geometry.surfaceType != 0:          # PlaneSurfaceType
            continue
        if all(abs(v.geometry.z - zmin) < 1e-5 for v in f.vertices) and f.area > ba:
            best, ba = f, f.area
    if best is None:
        continue
    data[comp.name] = loops_of(best)
    missing.discard(comp.name)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump(data, open(OUT, "w"))
print("loops for %d parts in %.1f s; missing: %s" % (len(data), time.time() - t0, sorted(missing)))
