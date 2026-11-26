# Bridge job: mass / volume / bounding box of every body, group totals, and (optionally) interference.
import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "boot.py")).read())
import json
import time
import adsk.core as ac
import adsk.fusion as af
F = rl("fxlib")
OUT = os.path.join(MODEL, "check")
import os
os.makedirs(OUT, exist_ok=True)
t0 = time.time()
d = F.design()
root = d.rootComponent
rows = []
for occ in root.allOccurrences:
    comp = occ.component
    if comp.bRepBodies.count == 0:
        continue
    path = occ.fullPathName.split("+")
    grp = [p.split(":")[0] for p in path]
    for b in occ.bRepBodies:          # proxies in assembly context (world positions)
        bb = b.boundingBox
        rows.append(dict(name=comp.name, body=b.name, path="/".join(grp[1:-1]), material=b.material.name if b.material else "",
                         vol_mm3=round(b.volume * 1000.0, 2), mass_g=round(b.physicalProperties.mass * 1000.0, 3),
                         bb=[round(v * 10, 2) for v in (bb.minPoint.x, bb.maxPoint.x, bb.minPoint.y, bb.maxPoint.y,
                                                         bb.minPoint.z, bb.maxPoint.z)]))
json.dump(rows, open(os.path.join(OUT, "bodies.json"), "w"), indent=1)
tot = {}
for r in rows:
    top = r["path"].split("/")[0] if r["path"] else r["name"]
    tot[top] = tot.get(top, 0.0) + r["mass_g"]
print("bodies:", len(rows), " group masses (g, geometric):", {k: round(v, 1) for k, v in tot.items()})
print("time %.1f s" % (time.time() - t0))

if globals().get("DO_INTERFERENCE", False):
    t1 = time.time()
    ents = ac.ObjectCollection.create()
    for occ in root.allOccurrences:
        for b in occ.bRepBodies:
            ents.add(b)
    ii = d.createInterferenceInput(ents)
    ii.areCoincidentFacesIncluded = False
    res = d.analyzeInterference(ii)
    hits = []
    for i in range(res.count):
        r = res.item(i)
        n1 = r.entityOne.assemblyContext.component.name if r.entityOne.assemblyContext else r.entityOne.name
        n2 = r.entityTwo.assemblyContext.component.name if r.entityTwo.assemblyContext else r.entityTwo.name
        v = r.interferenceBody.volume * 1000.0
        hits.append((n1, n2, round(v, 3)))
    hits.sort(key=lambda h: -h[2])
    json.dump(hits, open(os.path.join(OUT, "interference.json"), "w"), indent=1)
    print("interferences:", len(hits), "in %.0f s" % (time.time() - t1))
    for h in hits[:60]:
        print("  %-22s %-22s %10.3f mm3" % h)
