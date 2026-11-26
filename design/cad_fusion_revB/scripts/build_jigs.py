# Bridge job: 3D-printed assembly jigs into the open rev B design, STL export, and a fit check against the aircraft.
import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "boot.py")).read())
import os, time, json
import adsk.core as ac
G = rl("geo"); F = rl("fxlib"); POD = rl("pod"); TL = rl("tail"); J = rl("jigs")
t0 = time.time()
d = F.design()
root = d.rootComponent
top = F.group(root, "WaterDrop_revB")
for occ in list(root.allOccurrences):            # rebuild: remove an older jig set
    if occ.isValid and occ.component.name in ("Jigs", "Jigs_Wing"):
        occ.deleteMe()
jigs = F.group(top, "Jigs")
wing = F.group(top, "Wing")
parts = J.all_parts()
fails = []
F.build_list(jigs, [p for p in parts if p["grp"] != "Jigs_Wing"], fails)
F.build_list(wing, [p for p in parts if p["grp"] == "Jigs_Wing"], fails)
print("jigs built:", len(parts), "in %.0f s; FAILED %s" % (time.time() - t0, fails))
# STL (each jig in its own flat frame: lay it on its largest flat face in the slicer)
out = os.path.join(MODEL, "jigs")
os.makedirs(out, exist_ok=True)
names = {p["name"] for p in parts}
n = 0
vols = {}
for occ in root.allOccurrences:
    nm = occ.component.name
    if nm in names and occ.component.bRepBodies.count:
        F.export_stl(occ, os.path.join(out, nm + ".stl"))
        b = occ.component.bRepBodies.item(0)
        bb = b.boundingBox
        vols[nm] = dict(vol_cm3=round(b.volume, 2), box_mm=[round((bb.maxPoint.x - bb.minPoint.x) * 10, 1),
                        round((bb.maxPoint.y - bb.minPoint.y) * 10, 1), round((bb.maxPoint.z - bb.minPoint.z) * 10, 1)])
        n += 1
json.dump(vols, open(os.path.join(out, "jigs.json"), "w"), indent=1)
print("STL written:", n)
# fit check: interference between every jig and the aircraft parts
ents = ac.ObjectCollection.create()
jig_paths = set()
for occ in root.allOccurrences:
    for b in occ.bRepBodies:
        ents.add(b)
        if occ.component.name in names:
            jig_paths.add(occ.component.name)
ii = d.createInterferenceInput(ents)
ii.areCoincidentFacesIncluded = False
res = d.analyzeInterference(ii)
hits = []
for i in range(res.count):
    r = res.item(i)
    n1 = r.entityOne.assemblyContext.component.name
    n2 = r.entityTwo.assemblyContext.component.name
    if (n1 in names) != (n2 in names) or (n1 in names and n2 in names):
        hits.append((n1, n2, round(r.interferenceBody.volume * 1000, 3)))
hits.sort(key=lambda h: -h[2])
json.dump(hits, open(os.path.join(out, "fit_check.json"), "w"), indent=1)
print("jig interferences:", len(hits))
for h in hits[:40]:
    print("  %-20s %-20s %9.3f mm3" % h)
print("total %.0f s" % (time.time() - t0))
