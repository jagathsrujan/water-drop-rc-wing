# Bridge job: delete and rebuild the named pod / wing / tail parts in place (after a change in the part data).
# Set REPLACE = ["FL-M1", ...] in the bridge namespace before running.
exec(open(r"C:\Projects\water-drop-rc-wing\design\cad_fusion_revB\scripts\boot.py").read())
G = rl("geo"); F = rl("fxlib"); POD = rl("pod"); W = rl("wing"); T = rl("tail")
names = set(REPLACE)
root = F.design().rootComponent
top = F.group(root, "WaterDrop_revB")
src = {}
for p in POD.all_parts()[0]:
    src[p["name"]] = ("Pod", p)
for p in W.all_parts()[0]:
    src[p["name"]] = ("Wing", p)
for p in T.all_parts()[0]:
    src[p["name"]] = ("Tail", p)
done, fails = [], []
for occ in list(root.allOccurrences):
    if occ.isValid and occ.component.name in names:
        occ.deleteMe()
for n in names:
    asm, p = src[n]
    parent = F.group(top, asm)
    F.build_list(parent, [p], fails)
    done.append(n)
print("rebuilt", done, "FAILED", fails)
