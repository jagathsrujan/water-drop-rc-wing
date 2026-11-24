"""Part registry for the build package of the rev B balsa aircraft (Fusion model, design/cad_fusion_revB).

Everything here is read from the model's own part data (scripts pod.py, wing.py, tail.py, linkage.py, jigs.py),
the laser nesting (dxf/nesting.json), the exact laser loops (dxf/loops.json), the Fusion body list
(check/bodies.json) and the printed-part list (print/prints.json). Nothing is typed in by hand except the
names of bought items (electronics, glue, film) and how they are used.

Plain Python 3, no extra packages:  python tools/build_kit/make_build_kit.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
DESIGN = os.path.join(REPO, "design")
MODEL = os.path.join(DESIGN, "cad_fusion_revB")
SCRIPTS = os.path.join(MODEL, "scripts")
for p in ("cad/scripts", "cad_reservoir/scripts", "cad_fuselage/scripts", "cad_fuselage_balsa/scripts"):
    sys.path.insert(0, os.path.join(DESIGN, p))
sys.path.insert(0, SCRIPTS)

import geo as G          # noqa: E402
import pod               # noqa: E402
import wing              # noqa: E402
import tail              # noqa: E402
import linkage           # noqa: E402
import jigs              # noqa: E402
import laser             # noqa: E402
import wing_params as WP  # noqa: E402
import fus_params as FP   # noqa: E402
import bal_params as BP   # noqa: E402

MAT_LABEL = {
    "balsa_med": ("balsa", "medium"), "balsa_light": ("balsa", "light"), "balsa_hard": ("balsa", "hard"),
    "ply": ("birch ply", ""), "liteply": ("lite-ply", ""), "petg": ("PETG", "print"), "carbon": ("carbon", ""),
    "steel": ("steel wire", ""), "birch": ("birch dowel", ""), "pet": ("CA hinge sheet", ""), "elec": ("servo arm", "bought"),
    "pla_jig": ("PLA", "print"),
}
WING_INCIDENCE = getattr(WP, "INCIDENCE", 3.0)


# ---------------------------------------------------------------- small geometry helpers
def simplify(pts, tol=0.25):
    """Douglas-Peucker on a closed polygon."""
    if len(pts) < 8:
        return [tuple(p) for p in pts]

    def dp(seq):
        if len(seq) < 3:
            return seq
        a, b = seq[0], seq[-1]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1e-9
        best, bi = -1.0, 0
        for i in range(1, len(seq) - 1):
            p = seq[i]
            d = abs(dy * (p[0] - a[0]) - dx * (p[1] - a[1])) / L
            if d > best:
                best, bi = d, i
        if best <= tol:
            return [a, b]
        return dp(seq[:bi + 1])[:-1] + dp(seq[bi:])

    # split at the point farthest from the first
    p0 = pts[0]
    k = max(range(len(pts)), key=lambda i: (pts[i][0] - p0[0]) ** 2 + (pts[i][1] - p0[1]) ** 2)
    a = dp(list(pts[:k + 1]))
    b = dp(list(pts[k:]) + [pts[0]])
    return [tuple(p) for p in (a[:-1] + b[:-1])]


def r1(v):
    return round(v, 1)


def poly_area(p):
    return abs(G.area(p))


def perimeter(p):
    return sum(math.hypot(p[(i + 1) % len(p)][0] - p[i][0], p[(i + 1) % len(p)][1] - p[i][1]) for i in range(len(p)))


def band_dims(p):
    """A thin curved band: (thickness, arc length along its middle)."""
    A, P = poly_area(p), perimeter(p)
    arc = P / 2.0
    for _ in range(20):
        t = A / arc
        arc = P / 2.0 - t
    return A / arc, arc


def rot_y(pt, deg):
    a = math.radians(deg)
    x, y, z = pt
    return (x * math.cos(a) + z * math.sin(a), y, -x * math.sin(a) + z * math.cos(a))


# ---------------------------------------------------------------- hints (engraved arrows)
HINT_KEYS = (("< FWD", "FWD", -1, 0), ("FWD >", "FWD", 1, 0), ("UP ^", "UP", 0, 1), ("< LE", "LE", -1, 0),
             ("<LE", "LE", -1, 0), ("TE >", "TE", 1, 0))
HINT_WORLD = {"FWD": (-1.0, 0.0, 0.0), "UP": (0.0, 0.0, 1.0), "LE": (-1.0, 0.0, 0.0), "TE": (1.0, 0.0, 0.0)}
HINT_WORD = {"FWD": "nose", "UP": "up", "LE": "leading edge", "TE": "trailing edge"}


def part_hint(labels, fr):
    """The engraved arrow of a part, the way it points in the part frame, and how well it matches the model."""
    for txt, u, v, h in labels:
        for key, kind, au, av in HINT_KEYS:
            if key in txt:
                o, X, Y, Z = fr
                d = HINT_WORLD[kind]
                cu, cv = sum(d[i] * X[i] for i in range(3)), sum(d[i] * Y[i] for i in range(3))
                return dict(kind=kind, text=key, arrow=[au, av], cue=[round(cu, 3), round(cv, 3)],
                            ok=(au * cu + av * cv) > 0.5)
    return None


# ---------------------------------------------------------------- registry
class Registry:
    def __init__(self):
        self.parts = {}
        self.order = []

    def add(self, name, **kw):
        if name in self.parts:
            raise ValueError("duplicate part name " + name)
        self.parts[name] = dict(name=name, **kw)
        self.order.append(name)
        return self.parts[name]

    def __contains__(self, n):
        return n in self.parts

    def __getitem__(self, n):
        return self.parts[n]


def frame_list(fr):
    o, x, y, z = fr
    return [[r1(c) for c in o], [round(c, 5) for c in x], [round(c, 5) for c in y], [round(c, 5) for c in z]]


def plate_entry(p, assembly, kind):
    out = simplify(G.ccw(p["outline"]), 0.2)
    holes = []
    for c in p.get("cutters", []):
        if isinstance(c, tuple) and c[0] == "circle":
            holes.append(["c", r1(c[1]), r1(c[2]), r1(c[3])])
        elif len(c) >= 3:
            holes.append(["p", [[r1(a), r1(b)] for a, b in simplify(c, 0.3)]])
    labels = [[t, r1(u), r1(v), h] for t, u, v, h in p.get("labels", [])]
    return dict(assembly=assembly, grp=p["grp"], kind=kind, mat=p["mat"], t=round(p["t"], 2), z0=round(p.get("z0", 0.0), 2),
                frame=frame_list(p["fr"]), outline=[[r1(a), r1(b)] for a, b in out], holes=holes, labels=labels,
                hint=part_hint(p.get("labels", []), p["fr"]))


MIRROR_RULES = [
    r"^(?P<a>)(?P<s>[RL])(?P<b>[OI]-.*)$",                 # RO-NL / LO-NL, RI-N1 / LI-N1
    r"^(?P<a>WC\d)(?P<s>[RL])(?P<b>-[FR])$",               # WC1R-F (the last letter is front / rear)
    r"^(?P<a>J2-\d)(?P<s>[RL])(?P<b>-SQUARE)$",
    r"^(?P<a>J3-)(?P<s>[RL])(?P<b>-NOSE-TAPER)$",
    r"^(?P<a>TJ1-)(?P<s>[RL])(?P<b>[UD]-SQUARE)$",
    r"^(?P<a>(?:WF|WR|FSP)-)(?P<s>[RL])(?P<b>\d*)$",
    r"^(?P<a>(?:TR\d|S\dB))(?P<s>[RL])(?P<b>)$",
    r"^(?P<a>.*-)(?P<s>[RL])(?P<b>\d?)$",                  # ...-R, ...-R1
]


def mirror_name(name, names):
    """The other-side twin of a part (R <-> L) if it exists."""
    import re
    for rule in MIRROR_RULES:
        m = re.match(rule, name)
        if m:
            c = m.group("a") + {"R": "L", "L": "R"}[m.group("s")] + m.group("b")
            return c if c in names else None
    return None


def build_registry():
    R = Registry()
    laser.load_loops()
    # --- pod
    pparts, hard, servo = pod.all_parts()
    for p in pparts:
        kind = "laser" if (p["mat"] in laser.LASER_MATS and not p["name"].startswith(laser.NOT_LASER)) else \
            ("print" if p["mat"] == "petg" else "strip")
        R.add(p["name"], **plate_entry(p, "Pod", kind))
    for _, name, a, b, ro, ri, mat in hard:
        R.add(name, assembly="Pod", grp="Pod_Hard", kind="round", mat=mat, p0=[r1(c) for c in a], p1=[r1(c) for c in b],
              r=ro, ri=ri)
    # --- wing (wing frame; turned to the aircraft frame for the whole-aircraft view)
    wparts, wboxes = wing.all_parts()
    for p in wparts:
        kind = "laser" if (p["mat"] in laser.LASER_MATS and not p["name"].startswith(laser.NOT_LASER)) else \
            ("print" if p["mat"] == "petg" else "strip")
        R.add(p["name"], **plate_entry(p, "Wing", kind))
    lp, lr = linkage.wing_parts()
    for p in lp:
        kind = "laser" if p["mat"] in laser.LASER_MATS else ("print" if p["mat"] == "petg" else "bought")
        R.add(p["name"], **plate_entry(p, "Wing", kind))
    for name, a, b, ro, ri, mat, grp in lr:
        R.add(name, assembly="Wing", grp=grp, kind="round", mat=mat, p0=[r1(c) for c in a], p1=[r1(c) for c in b], r=ro, ri=ri)
    for kind_, name, box in wboxes:
        R.add(name, assembly="Wing", grp="Wing_Servo", kind="box", mat="elec", box=[r1(c) for c in box])
    # --- tail
    tparts, rounds = tail.all_parts()
    for p in tparts:
        kind = "laser" if (p["mat"] in laser.LASER_MATS and not p["name"].startswith(laser.NOT_LASER)) else \
            ("print" if p["mat"] == "petg" else "strip")
        R.add(p["name"], **plate_entry(p, "Tail", kind))
    for name, a, b, ro, ri, mat, grp in rounds:
        kind = "print" if mat == "petg" else "round"
        R.add(name, assembly="Tail", grp=grp, kind=kind, mat=mat, p0=[r1(c) for c in a], p1=[r1(c) for c in b], r=ro, ri=ri)
    tp, tr = linkage.tail_parts()
    for p in tp:
        R.add(p["name"], **plate_entry(p, "Tail", "bought"))
    for name, a, b, ro, ri, mat, grp in tr:
        R.add(name, assembly="Tail", grp=grp, kind="round", mat=mat, p0=[r1(c) for c in a], p1=[r1(c) for c in b], r=ro, ri=ri)
    for asm, p in linkage.hinge_parts():
        R.add(p["name"], **plate_entry(p, asm, "hinge"))
    # --- electronics and reservoir placeholders (boxes / tubes, aircraft frame)
    for it in tail.electronics(servo):
        if it[0] == "box":
            R.add(it[1], assembly="Electronics", grp="Electronics", kind="box", mat="elec", box=[r1(c) for c in it[2]])
        else:
            R.add(it[1], assembly="Electronics", grp="Electronics", kind="round", mat="elec", p0=[r1(c) for c in it[2]],
                  p1=[r1(c) for c in it[3]], r=it[4], ri=it[5])
    for it in tail.reservoir():
        if it[0] == "tube":
            R.add(it[1], assembly="Reservoir", grp="Reservoir", kind="round", mat=it[6], p0=[r1(c) for c in it[2]],
                  p1=[r1(c) for c in it[3]], r=it[4], ri=it[5])
        elif it[0] == "revolve":
            prof = it[2]
            ax0 = max(a for a, r in prof)
            rmax = max(r for a, r in prof)
            o = it[3][0]
            R.add(it[1], assembly="Reservoir", grp="Reservoir", kind="round", mat=it[4], p0=[r1(o[0]), 0.0, r1(o[2])],
                  p1=[r1(o[0] + ax0), 0.0, r1(o[2])], r=rmax, ri=0.0)
    # --- jigs
    for p in jigs.all_parts():
        e = plate_entry(p, {"Jigs_Wing": "Wing jigs", "Jigs_Tail": "Tail jigs"}.get(p["grp"], "Pod jigs"), "jig")
        R.add(p["name"], **e)
    pins = jigs.pin_rounds()
    R.add("PIN-6x11", assembly="Pod jigs", grp="Jigs_Base", kind="jig", mat="pla_jig", qty=len(pins),
          instances=[dict(name=n, p0=[r1(c) for c in a], p1=[r1(c) for c in b]) for n, a, b, *_ in pins],
          pins_by_jig={k: [[r1(x), r1(y)] for x, y in v] for k, v in jigs.PINS.items()})
    # --- printed aircraft parts made of several model bodies (print/prints.json, exported from Fusion)
    pj = os.path.join(MODEL, "print", "prints.json")
    prints = json.load(open(pj)) if os.path.exists(pj) else {}
    for item, info in prints.items():
        if item not in R:
            R.add(item, assembly="Tail", grp="Tail_Block", kind="print", mat="petg", members=info["parts"])
        R[item]["stl"] = item + ".stl"
        R[item]["print_box"] = info["box_mm"]
        R[item]["print_vol_cm3"] = info["vol_cm3"]
    for m in prints.get("TAIL-BLOCK", {}).get("parts", []):
        R[m]["print_in"] = "TAIL-BLOCK"
    # --- mirror twins, masses
    names = set(R.parts)
    bodies = {b["name"]: b for b in json.load(open(os.path.join(MODEL, "check", "bodies.json")))}
    for n, e in R.parts.items():
        e["mirror"] = mirror_name(n, names)
        b = bodies.get(n)
        if b:
            e["mass_g"] = round(b["mass_g"], 2)
            e["bb"] = [r1(c) for c in b["bb"]]
    return R


# ---------------------------------------------------------------- laser data
def laser_sheets(R):
    nest = json.load(open(os.path.join(MODEL, "dxf", "nesting.json")))
    loops = json.load(open(os.path.join(MODEL, "dxf", "loops.json")))
    for s in nest:
        s["area_mm2"] = s["sheet"][0] * s["sheet"][1]
        used = 0.0
        for q in s["parts"]:
            e = R[q["name"]]
            e["sheet"] = s["file"]
            e["sheet_pos"] = [q["x"], q["y"], q["rot90"]]
            e["stock"] = "%s %g mm" % (s["material"], s["t"])
            lp = loops.get(q["name"])
            if lp:
                a = sum(poly_area(l["pts"]) * (1 if l["outer"] else -1) for l in lp)
                e["loops"] = [dict(outer=l["outer"], pts=[[r1(u), r1(v)] for u, v in simplify(l["pts"], 0.15)]) for l in lp]
            else:
                a = poly_area(R[q["name"]]["outline"])
            e["area_mm2"] = round(a, 1)
            used += a
        s["used_mm2"] = round(used, 1)
    return nest


# ---------------------------------------------------------------- strip stock (cut to length, not laser)
STRIP_RULES = [
    # prefix, stock description, how the dimensions are read
    ("Keel", "strip", "keel"), ("Longeron", "triangle strip", "len_t"), ("Capstrip", "strip", "capstrip"),
    ("Ledge", "strip", "ledge"), ("LE", "leading-edge strip (shaped)", "len_t"), ("DBOX", "sheet", "sheet_span"),
    ("CS-", "sheet (grain chord-wise)", "sheet_chord"), ("CAPS-", "cap strip", "capstrip_w"),
    ("CAP-C", "carbon strip", "len_t"), ("CAP-B", "strip", "len_t"), ("TE-", "trailing-edge stock (wedge)", "len_t"),
    ("AIL-LE", "strip (bevelled)", "len_t"), ("AIL-TE", "trailing-edge stock (wedge)", "len_t"),
]


def nominal(t):
    """Sheet and strip stock comes in 0.5 mm steps: the band estimate of a curved piece is rounded to it."""
    return round(t * 2.0) / 2.0


def strip_dims(name, e):
    """(stock kind, thickness, width, length) of a strip part, mm."""
    out = e["outline"]
    u0, u1, v0, v1 = G.bbox(out)
    du, dv, t = u1 - u0, v1 - v0, e["t"]
    for pre, desc, rule in STRIP_RULES:
        if name.startswith(pre) and not (pre == "LE" and not name == "LE"):
            if rule == "keel":
                return desc, t, min(du, dv), max(du, dv)
            if rule == "ledge":
                thk, arc = band_dims(out)
                return desc, nominal(thk), t, arc
            if rule == "len_t":
                a, b = sorted((du, dv))
                return desc, a, b, t
            if rule == "capstrip":
                thk, arc = band_dims(out)
                return desc, nominal(thk), t, arc
            if rule == "capstrip_w":
                thk, arc = band_dims(out)
                return desc, nominal(thk), t, arc
            if rule == "sheet_span":
                thk, arc = band_dims(out)
                return desc, nominal(thk), arc, t
            if rule == "sheet_chord":
                thk, arc = band_dims(out)
                return desc, nominal(thk), t, arc
    raise ValueError("no strip rule for " + name)


def strips(R):
    rows = []
    for n in R.order:
        e = R[n]
        if e["kind"] != "strip":
            continue
        desc, th, w, L = strip_dims(n, e)
        mat, grade = MAT_LABEL[e["mat"]]
        rows.append(dict(name=n, assembly=e["assembly"], material=mat, grade=grade, stock=desc,
                         t=round(th, 1), w=round(w, 1), length=round(L, 1)))
        e["strip"] = rows[-1]
    return rows
