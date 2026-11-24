# Bridge job: (re)build the pinned pod jigs, the 5-segment jig base and the locating pins; STL; fit check.
exec(open(r"C:\Projects\water-drop-rc-wing\design\cad_fusion_revB\scripts\boot.py").read())
import os, json, time
import adsk.core as ac
G = rl("geo"); F = rl("fxlib"); POD = rl("pod"); TL = rl("tail"); J = rl("jigs")
t0 = time.time()
d = F.design(); root = d.rootComponent
top = F.group(root, "WaterDrop_revB")
parts = J.all_parts()
pod_jigs = [p for p in parts if p["grp"] in ("Jigs_Pod", "Jigs_Base") and not p["name"].startswith("J5")]
names = {p["name"] for p in pod_jigs}
for o in list(root.allOccurrences):
    if o.isValid and (o.component.name in names or o.component.name.startswith("PIN-") or o.component.name == "Jigs_Base"):
        o.deleteMe()
jg = F.group(top, "Jigs")
fails = []
F.build_list(jg, pod_jigs, fails)
pg = F.group(jg, "Jigs_Base")
for name, p0, p1, r, ri, mat, grp in J.pin_rounds():
    try:
        F.tube(pg, name, p0, p1, r, ri, mat)
    except Exception as e:
        fails.append((name, str(e)[:120]))
print("built %d pod jigs + base + %d pins in %.0f s; FAILED %s" % (len(pod_jigs), len(J.pin_rounds()), time.time() - t0, fails))
out = r"C:\Projects\water-drop-rc-wing\design\cad_fusion_revB\jigs"
for f in os.listdir(out):
    if f.startswith(("J1", "J2", "J3", "J4", "JB-", "PIN")) and f.endswith(".stl"):
        os.remove(os.path.join(out, f))
n = 0
pin_done = False
for o in root.allOccurrences:
    nm = o.component.name
    if nm in names:
        F.export_stl(o, os.path.join(out, nm + ".stl")); n += 1
    elif nm.startswith("PIN-") and not pin_done:
        F.export_stl(o, os.path.join(out, "PIN-6x11.stl")); pin_done = True; n += 1
print("STL:", n)
nmf = lambda e: e.assemblyContext.component.name if e.assemblyContext else e.name
ents = ac.ObjectCollection.create()
for o in root.allOccurrences:
    if o.component.name.startswith(("WC", "TJ", "J5")) or o.component.name in ("Wing", "Jigs_Wing"):
        continue
    for b in o.bRepBodies:
        ents.add(b)
ii = d.createInterferenceInput(ents); ii.areCoincidentFacesIncluded = False
hits = []
for r in d.analyzeInterference(ii):
    a, b = nmf(r.entityOne), nmf(r.entityTwo)
    if a in names or b in names or a.startswith("PIN-") or b.startswith("PIN-"):
        hits.append((a, b, round(r.interferenceBody.volume * 1000, 3)))
hits.sort(key=lambda h: -h[2])
print("base / jig clashes:", len(hits))
for h in hits[:30]:
    print("  ", h)
print("total %.0f s" % (time.time() - t0))
