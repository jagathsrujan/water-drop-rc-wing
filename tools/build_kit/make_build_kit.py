"""Make the build package of the rev B balsa aircraft from the model's part data.

    python tools/build_kit/make_build_kit.py          (plain Python 3; Chrome or Edge for the BOM PDF)

Writes
  docs/build-game/data.js     game data: parts with their real outlines, steps, needs (generated, not typed)
  docs/bom/data.js            BOM checklist data
  build-kit/                  the download-only folder for builders (laser DXF, STL, PDF, guides, quantities)
and prints a check report: every part named in the steps and the BOM exists in the part data, every laser part is
built in some step, and the material quantities add up to the nesting."""
import collections
import json
import math
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit_data as K   # noqa: E402
import steps as ST     # noqa: E402
import bom as BOM      # noqa: E402

REPO = K.REPO
MODEL = K.MODEL
GAME = os.path.join(REPO, "docs", "build-game")
BOMDIR = os.path.join(REPO, "docs", "bom")
KIT = os.path.join(REPO, "build-kit")
PROBLEMS = []


def problem(msg):
    PROBLEMS.append(msg)


# ---------------------------------------------------------------- geometry helpers
def world_pts(e):
    """World points of a part (its own assembly frame: aircraft frame, or wing frame for the wing)."""
    if "frame" in e:
        o, X, Y, Z = e["frame"]
        out = []
        for w in (e["z0"], e["z0"] + e["t"]):
            for u, v in e["outline"]:
                out.append(tuple(o[i] + X[i] * u + Y[i] * v + Z[i] * w for i in range(3)))
        return out
    if "p0" in e:
        return [tuple(e["p0"]), tuple(e["p1"])]
    if "box" in e:
        b = e["box"]
        return [(b[0], b[2], b[4]), (b[1], b[3], b[5])]
    if "members" in e:
        return []
    return []


def rng(e, axis):
    p = world_pts(e)
    return (min(q[axis] for q in p), max(q[axis] for q in p)) if p else (0.0, 0.0)


def side_of(name):
    m = re.search(r"(?:^|-)([RL])(?:\d*|O|I)", name)
    if name[:2] in ("RO", "RI"):
        return "R"
    if name[:2] in ("LO", "LI"):
        return "L"
    if name.endswith("-R") or re.search(r"-R\d*$", name):
        return "R"
    if name.endswith("-L") or re.search(r"-L\d*$", name):
        return "L"
    return None


# ---------------------------------------------------------------- geometry-based needs
def add_geometry_needs(R, S):
    idx = {it["id"]: it for st in S for it in st["items"]}
    formers = ST.FORMERS
    fx = {f: R[f]["frame"][0][0] + 1.5 for f in formers}
    floors = [n for n in R.order if n.startswith("FL-")]
    for f in formers:
        hit = [fl for fl in floors if rng(R[fl], 0)[0] + 0.5 < fx[f] < rng(R[fl], 0)[1] - 0.5]
        if len(hit) != 1:
            problem("former %s: floor piece not found (%s)" % (f, hit))
            continue
        idx[f]["needs"].insert(0, (hit[0], "order", "%s's floor tabs drop into the slots marked '%s' in %s: lay %s first."
                                   % (f, f.split("-")[0], hit[0], hit[0])))
        R[f]["floor_piece"] = hit[0]
    # side panels: formers whose side tabs go through them, longerons inside them
    for it in idx.values():
        if not it["id"].startswith("LAM-"):
            continue
        s = it["id"][4]
        x0 = min(rng(R[m], 0)[0] for m in it["parts"])
        x1 = max(rng(R[m], 0)[1] for m in it["parts"])
        through = [f for f in formers if x0 + 0.5 < fx[f] < x1 - 0.5 and side_of(f) in (None, s)]
        it["needs"] = [(f, "order", "The side tabs of %s go through this panel's slots (marked '%s' on it): the formers "
                                    "go in before the sides." % (f, f.split("-")[0])) for f in through] + it["needs"]
        it["formers"] = through
        if it["id"][5] == "M":
            for lg in ("Longeron-%s1" % s, "Longeron-%s2" % s):
                it["needs"].append((lg, "order", "%s sits in the floor/side corner: it must be in before the side closes." % lg))
    # keels and longerons pass through notches in the formers
    for n in ("Keel-R", "Keel-L", "Longeron-R1", "Longeron-R2", "Longeron-L1", "Longeron-L2"):
        a, b = rng(R[n], 0)
        s = n.split("-")[1][0]
        thru = [f for f in formers if a - 1 < fx[f] < b + 1 and side_of(f) in (None, s)]
        idx[n]["needs"] = [(f, "order", "%s runs through the notches in %s: drop the former in first." % (n, f)) for f in thru]
    # wing: ribs bounding each web, ribs crossing each false-spar piece, ribs at the servo frames
    ribs = [n for n in ST.RIBS]
    ry = {n: R[n]["frame"][0][1] - R[n]["t"] / 2 for n in ribs}
    for n in ST.WEBS:
        a, b = rng(R[n], 1)
        bound = [r for r in ribs if abs(ry[r] - a) < 2.6 or abs(ry[r] - b) < 2.6]
        if len(bound) != 2:
            problem("web %s: bounding ribs %s" % (n, bound))
        idx[n]["needs"] = [(r, "order", "%s's end tabs lock into slots in %s: the ribs go in before the webs." % (n, r)) for r in bound]
    for n in ("FSP-C", "FSP-R1", "FSP-L1", "FSP-R2", "FSP-L2"):
        a, b = rng(R[n], 1)
        crossing = [r for r in ribs if a - 1 < ry[r] < b + 1]
        idx[n]["needs"] = [(r, "order", "The false spar locks into the slot in %s from below (egg-crate): ribs first." % r)
                           for r in crossing] + idx[n]["needs"]
    for n in ("SERVO-FRAME-R", "SERVO-FRAME-L"):
        a, b = rng(R[n], 1)
        bound = [r for r in ribs if a - 3 < ry[r] < b + 3]
        idx[n]["needs"] = [(r, "order", "The servo frame sits in the bay between ribs 110 and 165: ribs first.") for r in bound]
    return idx


# ---------------------------------------------------------------- validation
def validate(R, S, idx):
    names = set(R.parts)
    seen = {}
    for k, st in enumerate(S):
        for it in st["items"]:
            if it["id"] in seen:
                problem("duplicate item id %s (steps %d and %d)" % (it["id"], seen[it["id"]], k))
            seen[it["id"]] = k
            for p in it.get("parts", []):
                if p not in names:
                    problem("step %s item %s: part %s not in the part data" % (st["id"], it["id"], p))
            if it["kind"] == "group" and not it["parts"]:
                problem("empty group " + it["id"])
    for k, st in enumerate(S):
        for it in st["items"]:
            for need in it["needs"]:
                if need[0] not in seen:
                    problem("step %s item %s needs unknown %s" % (st["id"], it["id"], need[0]))
                elif seen[need[0]] > k:
                    problem("step %s item %s needs %s from a LATER step" % (st["id"], it["id"], need[0]))
            if it.get("needs_any"):
                for n in it["needs_any"][0]:
                    if n not in seen:
                        problem("needs_any unknown " + n)
    # coverage: every made part is built somewhere
    used = collections.Counter(p for st in S for it in st["items"] for p in it.get("parts", []))
    import jigs as J
    for st in S:
        for it in st["items"]:
            m = re.match(r"pins-(J\w+)", it["id"])
            if not m:
                continue
            used["PIN-6x11"] += 1
            segs = set(re.findall(r"JB-\w+", it["label"]))
            for jn, pts in R["PIN-6x11"]["pins_by_jig"].items():
                if not jn.startswith(m.group(1)):
                    continue
                for x, y in pts:
                    k = max(i for i, c in enumerate(J.SEG_CUTS[:-1]) if x >= c)
                    if J.SEG_NAMES[k] not in segs:
                        problem("%s: pin of %s at X %.0f is in %s, label says %s" % (it["id"], jn, x, J.SEG_NAMES[k], segs))
    for n in R.order:
        e = R[n]
        if e["kind"] in ("laser", "laminate", "strip", "jig", "hinge") and n not in used and                 not (e.get("piece_of") and e["piece_of"] in used):        # a layer piece is built with its laminate
            problem("part %s (%s) is never built in the steps" % (n, e["kind"]))
        if e["kind"] == "print" and n not in used and not e.get("print_in"):
            problem("printed part %s is never built in the steps" % n)
    return used


def topo_order(st):
    """A valid build order of a step's items (needs inside the step, dovetail chains), list order as tie-break."""
    items = st["items"]
    ids = [it["id"] for it in items]
    done, order = set(), []
    chain = {}
    for it in items:
        if it.get("needs_any"):
            chain[it["id"]] = it["needs_any"][0]
    while len(order) < len(items):
        progress = False
        for it in items:
            if it["id"] in done:
                continue
            ok = all(n[0] in done or n[0] not in ids for n in it["needs"])
            if ok and it["id"] in chain:
                chained = [c for c in chain if c in done]
                ok = any(a in done for a in chain[it["id"]]) or (it.get("first_ok") and not chained)
            if ok:
                done.add(it["id"])
                order.append(it["id"])
                progress = True
                break
        if not progress:
            problem("step %s: needs form a cycle among %s" % (st["id"], [i for i in ids if i not in done]))
            order += [i for i in ids if i not in done]
            break
    return order


# ---------------------------------------------------------------- game data
def distractors(S, k, R):
    st = S[k]
    here = {p for it in st["items"] for p in it.get("parts", [])}
    ids = {it["id"] for it in st["items"]}
    out = []
    for it in st["items"]:
        for p in it.get("parts", []):
            m = R[p].get("mirror")
            if m and m not in here and m not in out:
                out.append(m)
    out = out[:3]
    later = [it["id"] for st2 in S[k + 1:k + 3] for it in st2["items"] if it["kind"] in ("part", "group")]
    pick = later[:2] + later[len(later) // 2:len(later) // 2 + 1] + later[-1:]
    for p in pick:
        if p not in ids and p not in out:
            out.append(p)
    return out


def game_part(R, n):
    e = R[n]
    keep = ("assembly", "grp", "kind", "mat", "t", "z0", "frame", "outline", "holes", "labels", "hint", "loops", "p0", "p1",
            "r", "ri", "box", "mirror", "sheet", "stl", "strip", "mass_g", "members", "print_in", "floor_piece")
    d = {k: e[k] for k in keep if k in e}
    if "loops" in d:
        d.pop("holes", None)
    if d.get("strip"):
        d["strip"] = {k: d["strip"][k] for k in ("stock", "t", "w", "length", "grade", "material")}
    d["matlabel"] = " ".join(x for x in K.MAT_LABEL.get(e["mat"], (e["mat"], ""))[::-1] if x).strip()
    return d


def build_game(R, S, idx):
    parts = {}
    for st in S:
        for it in st["items"]:
            for p in it.get("parts", []):
                parts[p] = game_part(R, p)
                for m in R[p].get("members", []):
                    parts[m] = game_part(R, m)
    for st in S:
        for d in st["distractors"]:
            if d in R.parts:
                parts[d] = game_part(R, d)
    for n in ("PIN-6x11",):
        parts[n] = game_part(R, n)
        parts[n]["instances"] = R[n]["instances"]
        parts[n]["pins_by_jig"] = R[n]["pins_by_jig"]
    steps = []
    for st in S:
        items = []
        for it in st["items"]:
            d = {k: it[k] for k in ("kind", "id", "parts", "why", "slot", "orient", "label", "surface", "hint_from", "formers")
                 if k in it and it[k] not in (None, "")}
            d["needs"] = [dict(id=a, type=b, msg=c) for a, b, c in it["needs"]]
            if it.get("needs_any"):
                d["needs_any"] = dict(ids=it["needs_any"][0], type=it["needs_any"][1], msg=it["needs_any"][2])
                d["first_ok"] = it.get("first_ok", False)
            m = re.match(r"pins-(J\w+)", it["id"])
            if m:
                d["pins_for"] = [j for j in R["PIN-6x11"]["pins_by_jig"] if j.startswith(m.group(1))]
            items.append(d)
        steps.append(dict(id=st["id"], phase=st["phase"], title=st["title"], view=st["view"], mode=st["mode"],
                          intro=st["intro"], tip=st.get("tip", ""), items=items, traps=st["traps"],
                          distractors=st["distractors"], order=st["order"]))
    return dict(meta=dict(model="Rev B balsa water-drop aircraft (design/cad_fusion_revB)", incidence=K.WING_INCIDENCE,
                          generated_by="tools/build_kit/make_build_kit.py", parts=len(parts), steps=len(steps)),
                parts=parts, steps=steps)


def write_js(path, var, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    txt = json.dumps(data, separators=(",", ":"))
    with open(path, "w", encoding="utf-8") as f:
        f.write("// Generated by tools/build_kit/make_build_kit.py from the rev B part data. Do not edit by hand.\n")
        f.write("window.%s = %s;\n" % (var, txt))
    return len(txt)


# ---------------------------------------------------------------- main
def main(skip_pdf=False):
    R = K.build_registry()
    nest = K.laser_sheets(R)
    strips = K.strips(R)
    S = ST.steps(set(R.parts))
    idx = add_geometry_needs(R, S)
    used = validate(R, S, idx)
    for k, st in enumerate(S):
        st["distractors"] = distractors(S, k, R)
        st["order"] = topo_order(st)
    game = build_game(R, S, idx)
    n = write_js(os.path.join(GAME, "data.js"), "KIT", game)
    print("game data: %d parts, %d steps, %d items, %.0f kB" % (len(game["parts"]), len(game["steps"]),
          sum(len(s["items"]) for s in game["steps"]), n / 1024))
    bom = BOM.build(R, nest, strips, S, used)
    write_js(os.path.join(BOMDIR, "data.js"), "BOM", bom)
    BOM.check(R, nest, strips, bom, problem)
    BOM.write_kit(R, nest, strips, S, bom, KIT, skip_pdf=skip_pdf, problem=problem)
    print("\nCHECKS: %d problem(s)" % len(PROBLEMS))
    for p in PROBLEMS:
        print("  - " + p)
    return 1 if PROBLEMS else 0


if __name__ == "__main__":
    sys.exit(main(skip_pdf="--no-pdf" in sys.argv))
