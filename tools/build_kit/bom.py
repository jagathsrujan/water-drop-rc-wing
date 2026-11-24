"""BOM, material quantities and the download-only build-kit folder, from the rev B part data.
Called by make_build_kit.py. Only the bought items (electronics, glue, film, tools) are typed here; every made part,
every sheet and every length comes from the part data and the nesting."""
import collections
import csv
import json
import math
import os
import shutil
import subprocess
import sys

import kit_data as K

REPO = K.REPO
MODEL = K.MODEL
PAGES_URL = "https://jagathsrujan.github.io/water-drop-rc-wing/"
REPO_URL = "https://github.com/jagathsrujan/water-drop-rc-wing"
DENSITY = {"balsa light": 0.10, "balsa medium": 0.14, "balsa hard": 0.16, "birch ply": 0.65, "lite-ply": 0.45}   # g/cm3, as mass_summary.py
SAW = 2.0            # mm lost per cut when strips are cut from 1000 mm lengths
STOCK_L = 1000.0     # strip / sheet length sold in India (BOM_India.md)
FILM = [("Wing", 29.2, 50.0), ("Pod (outer skin)", 5.04, 30.0), ("Tail (both sides)", 4.85, 30.0)]   # g, g/m2: mass_summary.py


# ---------------------------------------------------------------- helpers
def ceil_div(a, b):
    return int(math.ceil(a / b - 1e-9))


def ffd(lengths, stock=STOCK_L, saw=SAW):
    """First-fit decreasing: how many stock lengths for these pieces."""
    bins = []
    for L in sorted(lengths, reverse=True):
        for i, free in enumerate(bins):
            if free >= L + saw:
                bins[i] -= L + saw
                break
        else:
            bins.append(stock - L - saw)
    return len(bins)


def sheet_pack(pieces, W=100.0, L=STOCK_L, gap=2.0):
    """Pieces (width across the grain, length along the grain) on 100 x 1000 sheets, shelf packing along the grain."""
    sheets = []
    for w, l in sorted(pieces, key=lambda p: (-p[1], -p[0])):
        placed = False
        for sh in sheets:
            for row in sh["rows"]:
                if row["used"] + w + gap <= W and l <= row["len"]:
                    row["used"] += w + gap
                    placed = True
                    break
            if placed:
                break
            if sh["len"] + l + gap <= L:
                sh["rows"].append(dict(len=l, used=w + gap))
                sh["len"] += l + gap
                placed = True
                break
        if not placed:
            sheets.append(dict(rows=[dict(len=l, used=w + gap)], len=l + gap))
    return len(sheets)


def dxf_lengths(path):
    """Cut and engrave path lengths of one of our DXF files (POLYLINE / CIRCLE, layers CUT / ENGRAVE)."""
    lines = open(path).read().split("\n")
    out = collections.Counter()
    i = 0
    while i < len(lines) - 1:
        code, val = lines[i].strip(), lines[i + 1].strip()
        if code == "0" and val == "POLYLINE":
            layer, closed, pts = None, False, []
            i += 2
            while i < len(lines) - 1:
                c, v = lines[i].strip(), lines[i + 1].strip()
                if c == "8" and layer is None:
                    layer = v
                if c == "70" and not pts:
                    closed = v == "1"
                if c == "0" and v == "VERTEX":
                    x = y = 0.0
                    i += 2
                    while i < len(lines) - 1 and not (lines[i].strip() == "0"):
                        cc, vv = lines[i].strip(), lines[i + 1].strip()
                        if cc == "10":
                            x = float(vv)
                        if cc == "20":
                            y = float(vv)
                        i += 2
                    pts.append((x, y))
                    continue
                if c == "0" and v == "SEQEND":
                    break
                i += 2
            L = sum(math.hypot(pts[k + 1][0] - pts[k][0], pts[k + 1][1] - pts[k][1]) for k in range(len(pts) - 1))
            if closed and len(pts) > 2:
                L += math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1])
            out[layer] += L
            continue
        if code == "0" and val == "CIRCLE":
            layer, r = None, 0.0
            i += 2
            while i < len(lines) - 1 and lines[i].strip() != "0":
                c, v = lines[i].strip(), lines[i + 1].strip()
                if c == "8":
                    layer = v
                if c == "40":
                    r = float(v)
                i += 2
            out[layer] += 2 * math.pi * r
            continue
        i += 2
    return out


# ---------------------------------------------------------------- printed parts
def print_rows(R):
    rows = []
    jj = json.load(open(os.path.join(MODEL, "jigs", "jigs.json")))
    for n in R.order:
        e = R[n]
        if e["kind"] != "jig":
            continue
        if n == "PIN-6x11":
            rows.append(dict(id=n, name=n, group="Jig base pins", stl="print/jigs/PIN-6x11.stl", material="PLA", qty=e["qty"],
                             note="Print %d + 4 spares at 5.9 mm, or cut 6 mm wooden dowel to 11 mm." % e["qty"], box="5.9 x 11",
                             src="design/cad_fusion_revB/jigs/PIN-6x11.stl"))
            continue
        grp = {"Jigs_Base": "Jig base", "Jigs_Pod": "Pod jigs", "Jigs_Tail": "Tail jigs", "Jigs_Wing": "Wing cradles"}[e["grp"]]
        info = jj.get(n, {})
        if "box_mm" not in info:          # the base segments are not in jigs.json: size from the outline
            us, vs = [p[0] for p in e["outline"]], [p[1] for p in e["outline"]]
            info = dict(box_mm=[round(max(us) - min(us), 1), round(max(vs) - min(vs), 1), e["t"]])
        rows.append(dict(id=n, name=n, group=grp, stl="print/jigs/%s.stl" % n, material="PLA", qty=1,
                         note="", box=" x ".join("%g" % v for v in info.get("box_mm", [])), vol=info.get("vol_cm3"),
                         src="design/cad_fusion_revB/jigs/%s.stl" % n))
    pj = json.load(open(os.path.join(MODEL, "print", "prints.json")))
    notes = {"NOSE-RING": "Front lip, firewall collar and glue sleeve, in one piece.",
             "SERVO-MOUNT": "Release-servo arm pocket + 2 shelves + 2 gussets: 3 separate pieces in one file (in Bambu Studio: Split to objects, lay each flat).",
             "TAIL-BLOCK": "Plate with the fin slots, 2 boom collars and 2 webs (TAILBLOCK, TB-COLLAR-R/L, TB-WEB-R/L).",
             "SERVO-FRAME-R": "Aileron-servo bay frame, right.", "SERVO-FRAME-L": "Aileron-servo bay frame, left.",
             "SERVO-HATCH-R": "Servo hatch, right (M2 x 4 screws).", "SERVO-HATCH-L": "Servo hatch, left.",
             "AIL-HORN-R": "Aileron horn, glued to AH-R and the aileron LE.", "AIL-HORN-L": "Aileron horn, left."}
    for n, info in pj.items():
        rows.append(dict(id=n, name=n, group="Aircraft (PETG)", stl="print/aircraft/%s.stl" % n, material="PETG", qty=1,
                         note=notes.get(n, ""), box=" x ".join("%g" % v for v in info["box_mm"]), vol=info["vol_cm3"],
                         src="design/cad_fusion_revB/print/%s.stl" % n))
    # reservoir (rev A.2) and the wing band rub plates (wing rev A): printed parts that the Fusion model keeps as envelopes
    res = os.path.join(REPO, "design", "cad_reservoir", "stl")
    orient = {}
    po = os.path.join(res, "print_orientation.txt")
    if os.path.exists(po):
        for line in open(po, encoding="utf-8"):
            if ":" in line:
                a, b = line.split(":", 1)
                orient[a.strip()] = b.strip()
    for f in sorted(os.listdir(res)):
        if not f.endswith(".stl") or f.startswith("P12"):        # P12 saddles: replaced by the laser saddles S1a..S2d
            continue
        rows.append(dict(id=f[:-4], name=f[:-4], group="Reservoir (PETG)", stl="print/reservoir/" + f, material="PETG", qty=1,
                         note=("Ground support, not on the aircraft. " if f.startswith("P15") else "") + orient.get(f, ""), box="",
                         src="design/cad_reservoir/stl/" + f))
    for f in ("RubPlate_LE.stl", "RubPlate_TE.stl"):
        rows.append(dict(id=f[:-4], name=f[:-4], group="Wing (PETG)", stl="print/wing/" + f, material="PETG", qty=1,
                         note="Band rub plate (wing rev A, D-005): stops the rubber bands cutting the film at the centre LE / TE.",
                         box="", src="design/cad/stl/" + f))
    return rows


# ---------------------------------------------------------------- strip and sheet stock purchase
def stock_summary(strips):
    """Group strip parts into what you buy: (description, section) -> pieces, total length, stock lengths."""
    groups = collections.OrderedDict()
    for s in strips:
        n = s["name"]
        mat = ("%s %s" % (s["material"], s["grade"])).strip()
        if s["stock"].startswith("sheet") or s["stock"] == "cap strip":
            key = ("%s sheet %g mm" % (mat, s["t"]), "sheet")
        elif n.startswith("CAP-C"):
            key = ("carbon strip 3 x 0.5 mm (2 side by side per cap)", "carbon")
        else:
            key = ("%s %s %g x %g mm" % (mat, s["stock"], s["t"], s["w"]), "strip")
        groups.setdefault(key, []).append(s)
    out = []
    for (desc, kind), rows in groups.items():
        if kind == "carbon":
            lengths = [r["length"] for r in rows for _ in range(2)]
            n = ffd(lengths)
            buy = "%d x %g mm" % (n, STOCK_L)
            area = None
        elif kind == "sheet":
            pieces = []
            for r in rows:
                if r["stock"] == "cap strip":
                    pieces.append((r["w"], r["length"]))          # 6 mm wide, grain along the strip
                elif "chord" in r["stock"]:
                    pieces.append((r["w"], r["length"]))          # grain chord-wise: length along the grain
                else:
                    pieces.append((r["w"], r["length"]))          # D-box: arc width x span
            n = sheet_pack(pieces)
            lengths = [r["length"] for r in rows]
            buy = "%d sheet(s) 100 x %g mm" % (n, STOCK_L)
            area = sum(w * l for w, l in pieces) / 1e6
        else:
            lengths = [r["length"] for r in rows]
            n = ffd(lengths)
            buy = "%d x %g mm" % (n, STOCK_L)
            area = None
        out.append(dict(stock=desc, kind=kind, parts=[r["name"] for r in rows], pieces=len(rows) * (2 if kind == "carbon" else 1),
                        total_mm=round(sum(r["length"] for r in rows) * (2 if kind == "carbon" else 1), 1), buy=buy, n=n,
                        area_m2=round(area, 4) if area else None))
    return out


def sheet_summary(R, nest):
    g = collections.OrderedDict()
    for s in nest:
        key = (s["material"], s["t"])
        d = g.setdefault(key, dict(material=s["material"], t=s["t"], sheet=s["sheet"], sheets=0, parts=0, used_mm2=0.0, files=[]))
        d["sheets"] += 1
        d["parts"] += len(s["parts"])
        d["used_mm2"] += s["used_mm2"]
        d["files"].append(s["file"])
    out = []
    for (m, t), d in g.items():
        area = d["sheets"] * d["sheet"][0] * d["sheet"][1]
        d["area_m2"] = round(area / 1e6, 4)
        d["used_m2"] = round(d["used_mm2"] / 1e6, 4)
        d["util"] = round(100.0 * d["used_mm2"] / area, 1)
        d["mass_g"] = round(d["used_mm2"] * t / 1000.0 * DENSITY.get(m, 0.5), 1)
        if m.startswith("balsa"):
            d["buy"] = "%d sheet(s) 100 x 1000 mm (each gives 3 laser sheets of 100 x 300)" % ceil_div(d["sheets"], 3)
        else:
            d["buy"] = "%d sheet(s) 300 x 300 mm" % d["sheets"]
        out.append(d)
    return out


# ---------------------------------------------------------------- hardware derived from the part data
def hardware(R):
    P = R.parts
    L = lambda n: math.dist(P[n]["p0"], P[n]["p1"])
    hinges = [n for n in R.order if P[n]["kind"] == "hinge"]
    wire_pushrod = sum(L(n) for n in R.order if n.startswith("PUSHROD-AIL")) + \
        sum(L(n) for n in R.order if n.startswith(("ZBEND-", "ROD-END-")))
    joiner = sum(L(n) for n in R.order if n.startswith("JOINER"))
    carbon_rod = [L(n) for n in ("PUSHROD-ELEV", "PUSHROD-RUD")]
    booms = [L(n) for n in ("BOOM-R", "BOOM-L")]
    stubs = [L(n) for n in ("STUB-R", "STUB-L")]
    dowel = L("DOWEL")
    wc = [n for n in R.order if n.startswith("WC")]
    fw_holes = [h for h in P["FW"]["holes"] if h[0] == "c" and abs(h[3] - 1.6) < 0.05]
    pins = P["PIN-6x11"]["qty"]
    saddle_pins = [h for h in P["S1a"]["holes"] if h[0] == "c" and abs(h[3] - 1.05) < 0.05]
    rows = [
        ("Hinges", "CA hinges, 20 mm wide, 0.5 mm (cut from hinge sheet or bought 20 x 26 mm)", "%d + 5 spare" % len(hinges),
         "%d aileron (18 mm long), %d elevator, %d rudder (10.5 mm long): %s" % (
             sum(1 for h in hinges if "AIL" in h), sum(1 for h in hinges if "ELEV" in h), sum(1 for h in hinges if "RUD" in h), ", ".join(hinges))),
        ("Wire", "Spring-steel (piano) wire 1.2 mm (18 SWG)", "1 x 1000 mm",
         "Aileron pushrods + all Z-bend ends: %.0f mm in the model; Z-bends and handling: buy 1 m" % wire_pushrod),
        ("Wire", "Spring-steel wire 1.5 mm (elevator joiner)", "1 x 300 mm", "JOINER + legs: %.0f mm, bent to a U" % joiner),
        ("Rod", "Carbon rod 2 mm (tail pushrods)", "1 x 1000 mm", "PUSHROD-ELEV %.0f mm, PUSHROD-RUD %.0f mm" % tuple(carbon_rod)),
        ("Tube", "Carbon tube 10 x 8 mm (pultruded)", "2 x %d mm" % (int(max(booms) // 10 + 2) * 10), "BOOM-R / BOOM-L: %.0f mm each" % booms[0]),
        ("Rod", "Carbon rod 4 mm (front band stubs)", "1 x 100 mm", "STUB-R / STUB-L: %.0f mm each" % stubs[0]),
        ("Dowel", "Birch dowel 5 mm (rear band dowel)", "1 x 150 mm", "DOWEL: %.0f mm" % dowel),
        ("Jig", "6 mm wooden dowel (if you do not print the PIN-6x11 pins)", "1 x 300 mm", "%d pins x 11 mm" % pins),
        ("Jig", "Toothpicks 2 mm (saddle stack pins)", "6", "%d per stack x 2 stacks (S1, S2)" % len(saddle_pins)),
        ("Screws", "Wood screws 4 mm x 16 mm (wing cradles to the board)", str(2 * len(wc)), "2 per cradle half x %d halves" % len(wc)),
        ("Screws", "M3 x 8 mm screws + washers (motor to firewall)", str(len(fw_holes)), "X-mount holes in FW"),
        ("Screws", "M2 x 4 mm self-tapping screws (servo hatches)", "8 (+ spares)", "as wing rev A"),
        ("Magnets", "Neodymium magnets 6 x 2 mm (hatch)", "4 pairs", "mass table: 4 pairs D6x2 (seats not modelled: place by hand)"),
        ("Bands", "Rubber bands for the wing (#64 type)", "8-10 *(interp.)*", "over STUB-R/L and DOWEL (D-005)"),
        ("Strap", "Hook-and-loop strap 20 mm", "1 m", "bottle straps (reservoir P13a/b) and the battery"),
    ]
    return [dict(group=g, item=i, qty=q, note=n) for g, i, q, n in rows]


def consumables():
    film = sum(g / gsm for _, g, gsm in FILM)
    rows = [
        ("Glue", "Thin CA (cyanoacrylate), 20 g", "2", "tab/slot joints, hinges"),
        ("Glue", "Medium CA (Fevikwik is fine for tacking)", "1", "tacking"),
        ("Glue", "PVA wood glue, Fevicol SH", "1 x 250 g", "side laminate, webs, saddle stacks"),
        ("Glue", "Epoxy, slow (Araldite Standard)", "1", "booms, spar caps carbon to balsa"),
        ("Glue", "Epoxy, 5-minute", "1", "nose ring, tail block, horns"),
        ("Film", "Iron-on covering film (Oracover / Monokote type)", "about %.1f m2 + 40 %% waste" % film,
         ", ".join("%s %.2f m2" % (n, g / gsm) for n, g, gsm in FILM) + " (from the mass-table film masses)"),
        ("Sanding", "Sandpaper 150 / 220 / 320 + a long sanding block", "1 set", "J5 seat sanding, V-bevels"),
        ("Bench", "Wax paper or cling film", "1 roll", "release sheet for laminating and for the saddle stacks on the bottle"),
        ("Bench", "Petroleum jelly", "1 small tin", "on the hinge pivot before CA"),
        ("Bench", "Masking tape, T-pins, weights (books)", "-", ""),
        ("Bench", "Flat building board 1 m (wing cradles) + a flat table (jig base)", "1", ""),
        ("Tools", "Hobby knife, No. 11 blades, hinge-slotting knife, steel rule, set square, flat-nose pliers (Z-bends)", "-", ""),
        ("Print", "PLA filament (jigs)", "about 0.5 kg", "37 jigs + jig base + pins"),
        ("Print", "PETG filament (aircraft parts)", "about 100 g", "nose ring, mounts, tail block, horns, reservoir parts"),
    ]
    return [dict(group=g, item=i, qty=q, note=n) for g, i, q, n in rows]


def electronics():
    """Bought electronics: design/FIXED_MASSES.md and bom/BOM_Electronics_Robu.md (D-066)."""
    rows = [
        ("Motor", "DYS D2830 1000 KV brushless", 1, "52 g", "MOTOR on FW (4 x M3)"),
        ("Motor", "Prop adapter A2212 collet type, 3.17 mm", 2, "5 g", "COLLET (1 spare)"),
        ("Motor", "Propeller HQProp 10 x 5 thin electric (2-pack)", 2, "14 g", "PROP-DISC (4 props: they break at belly landings)"),
        ("Power", "ESC Hobbywing Skywalker 40A V2 (5 V / 5 A switching BEC)", 1, "36 g", "ESC under the battery tray; brake ON"),
        ("Power", "LiPo 3S 1000 mAh 30C, XT60", 1, "85 g", "BATTERY on TRAY (slides +-30 mm for the CG)"),
        ("Power", "XT60 male plug, 3.5 mm bullets, heat-shrink", 1, "3 g", "wiring"),
        ("Servos", "MG90S metal gear 180 deg (aileron x 2, release x 1, elevator x 1, rudder x 1)", 5, "13.4 g", "SERVO-W-R/L, RELEASE-SERVO, TSERVO-L/R"),
        ("Radio", "Receiver, 6 channels (not selected yet)", 1, "-", "aileron x 2 (or Y-lead), elevator, rudder, throttle, release"),
        ("Radio", "Servo extension lead 30 cm", 2, "-", "wing servos to the receiver"),
        ("Radio", "Servo tester (or the transmitter) for centring", 1, "-", "neutral setting before every Z-bend"),
    ]
    return [dict(group=g, item=i, qty=q, mass=m, note=n) for g, i, q, m, n in rows]


# ---------------------------------------------------------------- the BOM data
def build(R, nest, strips, S, used):
    step_of = {}
    for k, st in enumerate(S):
        for it in st["items"]:
            for p in it.get("parts", []):
                step_of.setdefault(p, (k + 1, st["title"]))
    laser = []
    for s in nest:
        for q in s["parts"]:
            e = R[q["name"]]
            u0 = min(p[0] for p in e["outline"]); u1 = max(p[0] for p in e["outline"])
            v0 = min(p[1] for p in e["outline"]); v1 = max(p[1] for p in e["outline"])
            laser.append(dict(id=q["name"], name=q["name"], assembly=e["assembly"], material=s["material"], t=s["t"],
                              sheet=s["file"], size="%.0f x %.0f" % (u1 - u0, v1 - v0), area=round(e["area_mm2"] / 100.0, 1),
                              mass=e.get("mass_g"), hint=e["hint"]["text"] if e.get("hint") else "",
                              step=step_of.get(q["name"], (0, ""))[0]))
    strip_rows = []
    for s in strips:
        strip_rows.append(dict(id=s["name"], name=s["name"], assembly=s["assembly"], material=("%s %s" % (s["material"], s["grade"])).strip(),
                               stock=s["stock"], section="%g x %g" % (s["t"], s["w"]), length=s["length"],
                               step=step_of.get(s["name"], (0, ""))[0]))
    prints = print_rows(R)
    sheets = sheet_summary(R, nest)
    stock = stock_summary(strips)
    return dict(meta=dict(title="Rev B balsa water-drop aircraft: bill of materials", generated_by="tools/build_kit/make_build_kit.py",
                          laser_parts=len(laser), sheets=len(nest), strips=len(strip_rows), prints=sum(p["qty"] for p in prints),
                          pages=PAGES_URL, repo=REPO_URL),
                sheets=sheets, laser=laser, strips=strip_rows, stock=stock, prints=prints, electronics=electronics(),
                hardware=hardware(R), consumables=consumables(), nesting=[dict(file=s["file"], material=s["material"], t=s["t"],
                                                                                  sheet=s["sheet"], parts=[p["name"] for p in s["parts"]]) for s in nest])


def check(R, nest, strips, bom, problem):
    names = set(R.parts)
    for row in bom["laser"] + bom["strips"]:
        if row["name"] not in names:
            problem("BOM part %s not in the part data" % row["name"])
    for row in bom["prints"]:
        if row["group"] in ("Pod jigs", "Wing cradles", "Tail jigs", "Jig base", "Jig base pins", "Aircraft (PETG)") and row["name"] not in names:
            problem("BOM print %s not in the part data" % row["name"])
        if not os.path.exists(os.path.join(REPO, row["src"])):
            problem("STL missing: " + row["src"])
    laser_names = [n for n in R.order if R[n]["kind"] == "laser"]
    if sorted(r["name"] for r in bom["laser"]) != sorted(laser_names):
        problem("BOM laser list differs from the laser parts in the part data")
    if len(bom["laser"]) != sum(len(s["parts"]) for s in nest):
        problem("BOM laser rows %d != parts on the sheets %d" % (len(bom["laser"]), sum(len(s["parts"]) for s in nest)))
    if sum(g["sheets"] for g in bom["sheets"]) != len(nest):
        problem("sheet totals do not add up to the nesting")
    if sum(g["parts"] for g in bom["sheets"]) != len(bom["laser"]):
        problem("parts per material group do not add up")
    for g in bom["sheets"]:
        a = sum(r["area"] for r in bom["laser"] if r["material"] == g["material"] and r["t"] == g["t"]) / 1e4
        if abs(a - g["used_m2"]) > 0.0005:
            problem("part area of %s %g mm: %.4f m2 vs %.4f m2" % (g["material"], g["t"], a, g["used_m2"]))
        if g["util"] > 100:
            problem("utilisation over 100 %% in %s %g" % (g["material"], g["t"]))
    if sum(len(st["parts"]) for st in bom["stock"]) != len(strips):
        problem("strip stock groups do not cover every strip part")
    for st in bom["stock"]:
        need = st["total_mm"] + SAW * st["pieces"]
        if st["kind"] != "sheet" and st["n"] * STOCK_L < need - 1e-6:
            problem("stock %s: %d lengths too few for %.0f mm" % (st["stock"], st["n"], need))


# ---------------------------------------------------------------- build-kit folder
def kerf_test(path, t):
    import laser as LZ
    LZ.FONT.setdefault(".", [[(1.7, 0), (2.3, 0), (2.3, 0.6), (1.7, 0.6), (1.7, 0)]])
    LZ.FONT.setdefault("+", [[(0.5, 3), (3.5, 3)], [(2, 1.5), (2, 4.5)]])
    d = LZ.DXF()
    W, H = 92.0, 34.0
    d.poly([(0, 0), (120, 0), (120, 50), (0, 50)], "SHEET")
    d.poly([(5, 5), (5 + W, 5), (5 + W, 5 + H), (5, 5 + H)], "CUT")
    offs = [-0.15, -0.10, -0.05, 0.0, 0.05, 0.10]
    for k, o in enumerate(offs):
        x = 12 + k * 14
        w = t + o
        d.poly([(x, 17), (x + w, 17), (x + w, 27), (x, 27)], "CUT")
        for st in LZ.stroke_text(("%+.2f" % o).replace("+0.00", "0"), x + w / 2, 11.5, 2.6):
            d.poly(st, "ENGRAVE", closed=False)
    for st in LZ.stroke_text("KERF TEST %g MM" % t, 5 + W / 2, 33.5, 3.0):
        d.poly(st, "ENGRAVE", closed=False)
    d.poly([(100, 5), (108, 5), (108, 40), (100, 40)], "CUT")      # a tab strip cut from the same stock
    for st in LZ.stroke_text("TAB", 104, 22, 2.5):
        d.poly([(q[1] * 0 + q[0], q[1]) for q in st], "ENGRAVE", closed=False)
    d.save(path)


def write_kit(R, nest, strips, S, bom, KIT, skip_pdf=False, problem=print):
    if os.path.isdir(KIT):
        for sub in ("laser", "print"):
            shutil.rmtree(os.path.join(KIT, sub), ignore_errors=True)
    os.makedirs(os.path.join(KIT, "laser", "kerf-test"), exist_ok=True)
    for s in nest:
        shutil.copy2(os.path.join(MODEL, "dxf", s["file"]), os.path.join(KIT, "laser", s["file"]))
    for t in sorted({s["t"] for s in nest}):
        kerf_test(os.path.join(KIT, "laser", "kerf-test", "kerf_test_%gmm.dxf" % t), t)
    for p in bom["prints"]:
        dst = os.path.join(KIT, p["stl"])
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(REPO, p["src"]), dst)
    write_laser_brief(nest, bom, KIT)
    write_materials(bom, KIT)
    write_print_list(bom, KIT)
    write_guide(R, S, KIT)
    write_kit_readme(bom, KIT)
    if not skip_pdf:
        make_pdf(KIT, problem)
    make_zip(KIT)


def make_zip(KIT):
    """docs/downloads/build-kit.zip: the whole build-kit folder in one download (fixed dates, so it only changes
    when a file in it changes)."""
    import zipfile
    out = os.path.join(REPO, "docs", "downloads", "build-kit.zip")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for root, dirs, files in os.walk(KIT):
            dirs.sort()
            for f in sorted(files):
                p = os.path.join(root, f)
                arc = "build-kit/" + os.path.relpath(p, KIT).replace("\\", "/")
                zi = zipfile.ZipInfo(arc, date_time=(2026, 1, 1, 0, 0, 0))
                zi.compress_type = zipfile.ZIP_DEFLATED
                zi.external_attr = 0o644 << 16
                z.writestr(zi, open(p, "rb").read())
    print("build-kit.zip: %.1f MB" % (os.path.getsize(out) / 1e6))


def mat_words(m):
    return {"balsa light": "Balsa, LIGHT grade (about 100 kg/m3)", "balsa medium": "Balsa, MEDIUM grade (about 140 kg/m3)",
            "birch ply": "Birch plywood (aircraft ply)", "lite-ply": "Lite-ply (poplar ply)"}.get(m, m)


def write_laser_brief(nest, bom, KIT):
    L = ["# Laser brief: sheet by sheet", "",
         "Hand this file and the `laser/` folder to the laser shop. Generated from the nesting of the part data "
         "(`design/cad_fusion_revB/dxf/nesting.json`) by `tools/build_kit/make_build_kit.py`.", "",
         "## Rules for every sheet", "",
         "- **DXF R12, units mm, 1:1.** Do not scale.",
         "- **Layer CUT** (red): cut through. **Layer ENGRAVE** (blue): single-stroke part names and arrows - *score* them at "
         "low power as a line, do not fill. **Layer SHEET** (grey): the sheet outline - do NOT cut, it only shows the sheet.",
         "- **Order:** engrave first, then the inner cuts (holes, slots), then the outer outlines, so parts do not move before "
         "their holes are cut.",
         "- **Grain:** balsa sheets are 100 x 300 mm with the grain along the 300 mm side. Every balsa part is already turned "
         "to its grain on the sheet - do not rotate the parts. Ply and lite-ply: 300 x 300 mm, any direction.",
         "- **Kerf:** slots are drawn at the nominal stock thickness. Measure your sheets with calipers, then cut the kerf test "
         "(`laser/kerf-test/kerf_test_<t>mm.dxf`) from the same sheet and pick the slot where the TAB strip is a firm push fit. "
         "Set that as the kerf offset (or tell the shop). Balsa varies sheet to sheet: test each thickness.",
         "- **Engraved face up:** the engraving is on the face that stays visible while you build. Lay every sheet the same side "
         "up as cut.",
         "- **Power:** balsa burns easily: low power, high speed, air assist on, several light passes rather than one heavy one. "
         "Test on scrap first. Ply needs more power; lite-ply in between.", "",
         "## Material summary", "", "| Material | Thickness | Sheet size | Sheets | Parts | Part area | Use of the sheet | Buy |",
         "|---|---|---|---|---|---|---|---|"]
    for g in bom["sheets"]:
        L.append("| %s | %g mm | %g x %g mm | %d | %d | %.3f m2 | %.0f %% | %s |" % (mat_words(g["material"]), g["t"], g["sheet"][1], g["sheet"][0],
                                                                         g["sheets"], g["parts"], g["used_m2"], g["util"], g["buy"]))
    L += ["", "**%d sheets, %d parts.**" % (len(nest), sum(len(s["parts"]) for s in nest)), "", "## Every sheet", "",
          "| # | File | Material | Thickness | Sheet | Parts | Cut length | Engrave length |", "|---|---|---|---|---|---|---|---|"]
    for k, s in enumerate(nest):
        ln = dxf_lengths(os.path.join(MODEL, "dxf", s["file"]))
        L.append("| %d | `%s` | %s | %g mm | %g x %g | %s | %.2f m | %.2f m |" % (
            k + 1, s["file"], mat_words(s["material"]), s["t"], s["sheet"][1], s["sheet"][0],
            ", ".join(p["name"] for p in s["parts"]), ln["CUT"] / 1000, ln["ENGRAVE"] / 1000))
    L += ["", "Cut and engrave lengths are summed from the DXF files (useful for a quote).", ""]
    open(os.path.join(KIT, "LASER_BRIEF.md"), "w", encoding="utf-8").write("\n".join(L))


def write_materials(bom, KIT):
    L = ["# Material quantities", "",
         "Computed by `tools/build_kit/make_build_kit.py` from the laser nesting and the strip-stock parts in the part data "
         "(not typed by hand). Buy 10-20 % extra balsa: some sheets will be too heavy or have bad grain.", "",
         "## Laser sheets (balsa, birch ply, lite-ply)", "",
         "| Material | Thickness | Laser sheets | Sheet size | Sheet area | Part area | Est. part mass | Buy |", "|---|---|---|---|---|---|---|---|"]
    tot = collections.Counter()
    for g in bom["sheets"]:
        L.append("| %s | %g mm | %d | %g x %g mm | %.3f m2 | %.3f m2 | %.0f g | %s |" % (
            mat_words(g["material"]), g["t"], g["sheets"], g["sheet"][1], g["sheet"][0], g["area_m2"], g["used_m2"], g["mass_g"], g["buy"]))
        tot["sheets"] += g["sheets"]
        tot["area"] += g["area_m2"]
    L += ["| **Total** | | **%d** | | **%.3f m2** | | | |" % (tot["sheets"], tot["area"]), "",
          "## Strip and sheet stock (cut by hand)", "",
          "| Stock | Pieces | Total length | Buy | Used for |", "|---|---|---|---|---|"]
    for st in bom["stock"]:
        L.append("| %s | %d | %.0f mm%s | %s | %s |" % (st["stock"], st["pieces"], st["total_mm"],
                                                     (" (%.3f m2)" % st["area_m2"]) if st["area_m2"] else "", st["buy"], ", ".join(st["parts"])))
    L += ["", "Strip lengths are packed into %g mm lengths with %g mm per saw cut. Sheet stock (D-box, centre sheeting, cap "
          "strips) is packed on 100 x %g mm sheets with the grain along the piece length." % (STOCK_L, SAW, STOCK_L), "",
          "## Every strip part", "", "| Part | Material | Stock | Section (mm) | Length (mm) |", "|---|---|---|---|---|"]
    for r in bom["strips"]:
        L.append("| %s | %s | %s | %s | %.1f |" % (r["name"], r["material"], r["stock"], r["section"], r["length"]))
    L += ["", "## Hardware from the part data", "", "| Item | Qty | Note |", "|---|---|---|"]
    for r in bom["hardware"]:
        L.append("| %s | %s | %s |" % (r["item"], r["qty"], r["note"]))
    open(os.path.join(KIT, "MATERIALS.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    with open(os.path.join(KIT, "materials.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["kind", "material", "thickness_or_section_mm", "count", "unit", "sheet_or_stock_size_mm", "area_m2", "total_length_mm", "buy"])
        for g in bom["sheets"]:
            w.writerow(["laser sheet", g["material"], g["t"], g["sheets"], "sheet", "%gx%g" % (g["sheet"][1], g["sheet"][0]), g["area_m2"], "", g["buy"]])
        for st in bom["stock"]:
            w.writerow(["stock", st["stock"], "", st["pieces"], "piece", "", st["area_m2"] or "", st["total_mm"], st["buy"]])


def write_print_list(bom, KIT):
    L = ["# 3D prints", "", "STL files in `print/`. Every file is one part in its own frame: lay it on its largest flat face in the "
         "slicer. Everything fits a 256 mm bed (Bambu P1S). Jigs: PLA, 3 walls, 20-30 % infill. Aircraft parts: PETG (PLA "
         "softens in the sun), 3-4 walls.", "", "| Group | STL | Material | Qty | Size (mm) | Note |", "|---|---|---|---|---|---|"]
    for p in bom["prints"]:
        L.append("| %s | `%s` | %s | %d | %s | %s |" % (p["group"], p["stl"], p["material"], p["qty"], p.get("box", ""), p["note"]))
    open(os.path.join(KIT, "PRINT_LIST.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")


def write_guide(R, S, KIT):
    P = R.parts
    L = ["# Build guide", "",
         "The whole build in the order of the build game (%sbuild-game/). Generated from the same step data, so the game and "
         "this guide always agree. Tick each box. Every laser part has its name engraved; arrows: `< FWD` to the nose, `UP ^` "
         "up, `< LE` to the leading edge." % PAGES_URL, ""]
    idx = {it["id"]: it for st in S for it in st["items"]}
    for k, st in enumerate(S):
        L += ["## %d. %s" % (k + 1, st["title"]), "", "*%s*" % st["phase"], "", st["intro"], ""]
        for n, iid in enumerate(st["order"]):
            it = idx[iid]
            if it["kind"] in ("action", "neutral"):
                line = it["label"]
            elif it["kind"] == "group":
                line = it["label"]
            else:
                e = P[iid]
                bits = [K.MAT_LABEL.get(e["mat"], (e["mat"], ""))[0]]
                if e.get("sheet"):
                    bits.append("%g mm, `%s`" % (e["t"], e["sheet"]))
                elif e.get("strip"):
                    bits.append("%g x %g x %.0f mm" % (e["strip"]["t"], e["strip"]["w"], e["strip"]["length"]))
                elif e.get("stl"):
                    bits.append("`%s.stl`" % iid)
                line = "`%s` (%s)" % (iid, ", ".join(b for b in bits if b))
                if e.get("hint"):
                    line += ", arrow `%s`" % e["hint"]["text"]
            jig = [x[0] for x in it["needs"] if x[1] in ("jig", "pin")]
            L.append("%d. [ ] %s%s" % (n + 1, line, (" - needs %s" % ", ".join(jig)) if jig else ""))
        if st["traps"]:
            L += ["", "**Do not:**", ""]
            for t in st["traps"]:
                L.append("- *%s* - %s %s" % (t["label"], t["mistake"], t["fix"]))
        if st.get("tip"):
            L += ["", "Tip: " + st["tip"]]
        L.append("")
    open(os.path.join(KIT, "BUILD_GUIDE.md"), "w", encoding="utf-8").write("\n".join(L))


def write_kit_readme(bom, KIT):
    m = bom["meta"]
    L = ["# Build kit: rev B balsa water-drop aircraft", "",
         "Everything a builder needs, and nothing else. Generated from the part data by `tools/build_kit/make_build_kit.py`; "
         "do not edit these files by hand (run the script again after a design change).", "",
         "| File / folder | What it is |", "|---|---|",
         "| [`BOM.pdf`](BOM.pdf) | Bill of materials to print and tick: every laser part, strip, print, electronics, hardware. Online with saved ticks: %sbom/ |" % PAGES_URL,
         "| [`BUILD_GUIDE.md`](BUILD_GUIDE.md) | The build step by step (same steps as the build game: %sbuild-game/) |" % PAGES_URL,
         "| [`LASER_BRIEF.md`](LASER_BRIEF.md) | For the laser shop: material, thickness, sheet size, layers, kerf, sheet by sheet |",
         "| [`MATERIALS.md`](MATERIALS.md), [`materials.csv`](materials.csv) | How much balsa, ply, lite-ply and strip stock to buy |",
         "| [`PRINT_LIST.md`](PRINT_LIST.md) | Every 3D print with material and quantity |",
         "| `laser/` | %d DXF sheets (%d parts) + `kerf-test/` coupons |" % (m["sheets"], m["laser_parts"]),
         "| `print/jigs/` | 37 PLA jigs, 5 jig-base segments, the locating pin |",
         "| `print/aircraft/`, `print/reservoir/`, `print/wing/` | PETG parts of the aircraft |", "",
         "## Order of work", "",
         "1. Buy the materials (`MATERIALS.md`, `BOM.pdf`). Weigh the balsa: light sheets for the light parts.",
         "2. Cut the kerf test, then the sheets (`LASER_BRIEF.md`). Keep each sheet's parts together.",
         "3. Print the jigs and the jig base first, then the PETG parts (`PRINT_LIST.md`).",
         "4. Play the build game once (%sbuild-game/): it shows every part in 3D and catches the usual mistakes." % PAGES_URL,
         "5. Build with `BUILD_GUIDE.md` on the bench.", "",
         "Questions about the design: see [`../ASK_AN_AGENT.md`](../ASK_AN_AGENT.md).", ""]
    open(os.path.join(KIT, "README.md"), "w", encoding="utf-8").write("\n".join(L))


def find_browser():
    for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe", "/usr/bin/google-chrome", "/usr/bin/chromium",
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        if os.path.exists(p):
            return p
    return None


def make_pdf(KIT, problem):
    br = find_browser()
    if not br:
        problem("no Chrome / Edge found: BOM.pdf not made")
        return
    page = os.path.join(REPO, "docs", "bom", "index.html").replace("\\", "/")
    url = "file:///" + page.lstrip("/") + "?print=1"
    out = os.path.join(KIT, "BOM.pdf")
    tmp_profile = os.path.join(os.environ.get("TEMP", "/tmp"), "bom-pdf-profile")
    cmd = [br, "--headless=new", "--disable-gpu", "--no-first-run", "--user-data-dir=" + tmp_profile,
           "--no-pdf-header-footer", "--virtual-time-budget=8000", "--print-to-pdf=" + out, url]
    subprocess.run(cmd, check=False, capture_output=True, timeout=180)
    if not os.path.exists(out) or os.path.getsize(out) < 10000:
        problem("BOM.pdf was not written")
        return
    shutil.copy2(out, os.path.join(REPO, "docs", "bom", "BOM.pdf"))
    print("BOM.pdf: %.0f kB" % (os.path.getsize(out) / 1024))
