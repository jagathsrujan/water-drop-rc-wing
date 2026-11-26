# Bridge job: control linkages (aileron arms, horns, horn ribs, pushrods; tail arms, pushrods, Z-bends).
import os; exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "boot.py")).read())
G = rl("geo"); F = rl("fxlib"); W = rl("wing"); LK = rl("linkage")
root = F.design().rootComponent
top = F.group(root, "WaterDrop_revB")
OLD = ("PUSHROD-", "ZBEND-", "ROD-END-", "SERVO-ARM-", "AIL-HORN-", "AH-", "HINGE-")
for occ in list(root.allOccurrences):
    if occ.isValid and occ.component.name.startswith(OLD):
        occ.deleteMe()
fails = []
for asm, (parts, rounds) in (("Wing", LK.wing_parts()), ("Tail", LK.tail_parts())):
    parent = F.group(top, asm)
    F.build_list(parent, parts, fails)
    for name, p0, p1, r, ri, mat, grp in rounds:
        try:
            F.tube(F.group(parent, grp), name, p0, p1, r, ri, mat)
        except Exception as e:
            fails.append((name, str(e)[:160]))
for asm, p in LK.hinge_parts():
    F.build_list(F.group(top, asm), [p], fails)
print("linkages and hinges built; FAILED", fails)
