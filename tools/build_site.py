"""Build the GitHub Pages site (docs/) and the Indian BOM files (bom/) from one data source.
Usage: python3 tools/build_site.py   (run from anywhere)."""
import csv, html, json, os, shutil, subprocess, sys
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bom_data as B
DOCS, CAD, VID = os.path.join(ROOT, "docs"), os.path.join(ROOT, "design", "cad"), os.path.join(ROOT, "design", "video")
REPO = "https://github.com/jagathsrujan/water-drop-rc-wing"
TREE, BLOB = REPO + "/tree/main/", REPO + "/blob/main/"
for d in ("img", "media"):
    os.makedirs(os.path.join(DOCS, d), exist_ok=True)
os.makedirs(os.path.join(ROOT, "bom"), exist_ok=True)
e = html.escape

def jpg(src, name, maxw=1600):
    im = Image.open(src).convert("RGB")
    if im.width > maxw:
        im = im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS)
    im.save(os.path.join(DOCS, "img", name), "JPEG", quality=84, optimize=True, progressive=True)
    return "img/" + name

# ---------- images ----------
I = {}
for n in ("wing_iso", "wing_iso_open", "wing_top", "wing_bottom", "wing_section_y140", "wing_section_y148", "wing_servo_bay_iso"):
    I[n] = jpg(os.path.join(CAD, "img", n + ".png"), n + ".jpg")
I["dxf"] = jpg(os.path.join(CAD, "img", "dxf_preview_2mm.png"), "dxf_preview_2mm.jpg", 1400)
I["dxf2"] = jpg(os.path.join(CAD, "img", "dxf_preview_other.png"), "dxf_preview_other.jpg", 1400)
NAR = json.load(open(os.path.join(VID, "narration.json")))
t0, START = 0.0, {}
for s in NAR:
    START[s["id"]] = t0; t0 += s["seg"]
def still(sid, frac, name):
    t = START[sid] + frac * [s for s in NAR if s["id"] == sid][0]["seg"]
    out = os.path.join(DOCS, "img", name)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "%.2f" % t, "-i", os.path.join(VID, "wing_build.mp4"), "-frames:v", "1",
                    "-vf", "crop=1920:840:0:100,scale=1280:-1", "-q:v", "3", out], check=True)
    return "img/" + name
for sid, f in (("08_spar", .9), ("09_ribs", .9), ("10_le_te", .9), ("11_webs", .9), ("12_top", .9), ("13_flip", .9), ("14_tips", .9),
               ("15_ailerons", .9), ("17_servo", .9), ("18_final", .9), ("05_laser", .55), ("07_glue", .5), ("16_cover", .7), ("04_weigh", .8),
               ("06_strips", .85), ("02_materials", .95)):
    I[sid] = still(sid, f, sid + ".jpg")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "12", "-i", os.path.join(VID, "wing_build.mp4"), "-frames:v", "1", "-vf", "scale=1280:-1", "-q:v", "3",
                os.path.join(DOCS, "media", "poster.jpg")], check=True)
shutil.copy(os.path.join(VID, "wing_build.mp4"), os.path.join(DOCS, "media", "wing_build.mp4"))
shutil.copy(os.path.join(VID, "wing_build.en.vtt"), os.path.join(DOCS, "media", "wing_build.en.vtt"))

# ---------- BOM files ----------
def price(r):
    return "₹%d" % r[4] if r[4] else "varies"
with open(os.path.join(ROOT, "bom", "BOM_India.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["group", "item", "spec", "qty", "unit_price_inr_nov2026", "line_total_inr", "online_links", "what_to_ask_for", "where_offline"])
    for r in B.BOM:
        w.writerow([r[0], r[1], r[2], r[3], r[4] or "", (r[4] or 0) * r[3] or "", " | ".join("%s: %s" % l for l in r[5]), r[6], r[7]])
total = sum((r[4] or 0) * r[3] for r in B.BOM)
md = ["# Indian bill of materials — balsa wing rev A", "",
      "Quantities for one wing plus spares. Prices are those listed online in November 2026 (INR) — check before you order. "
      "No affiliation with any shop. Machine-readable copy: [`BOM_India.csv`](BOM_India.csv). Webpage: https://jagathsrujan.github.io/water-drop-rc-wing/#bom", "",
      "Estimated total of the priced items: **₹%s** (plus glue, screws, board and small tools)." % format(total, ","), "",
      "| Group | Item | Spec | Qty | Unit ₹ | Buy online | What to ask for | Where offline |", "|---|---|---|---|---|---|---|---|"]
for r in B.BOM:
    links = "<br>".join("[%s](%s)" % (a, u) for a, u in r[5]) or "—"
    md.append("| %s | %s | %s | %d | %s | %s | %s | %s |" % (r[0], r[1], r[2], r[3], price(r), links, r[6].replace("|", "/"), r[7]))
md += ["", "## Target sheet masses (weigh before you buy)", "", "| Sheet 100 × 1000 | Volume | Light (90 kg/m³) | Medium (130 kg/m³) |", "|---|---|---|---|"]
md += ["| %s | %d cm³ | ≤ %.1f g | ≈ %.1f g |" % t for t in B.TARGET_SHEET_MASS]
md += ["", "## Shopping offline", "",
       "- Take the cut list (`design/cad/cut_list.md`) and a pocket scale. Weigh balsa in the shop and choose by weight, not by look.",
       "- Electronics markets (" + B.MARKETS + ") have servos, leads, M2 screws and often carbon parts.",
       "- Hardware shops: Fevicol SH, Araldite, Fevikwik, emery paper, 18 SWG spring-steel wire, heat gun, steel rule.",
       "- Plywood shops cut a flat 12 mm MDF building board to size.",
       "- 3D-printing shops and college maker spaces can print the PETG parts; laser sign-board shops can often cut 2–3 mm balsa from the DXF files at low power."]
open(os.path.join(ROOT, "bom", "BOM_India.md"), "w").write("\n".join(md) + "\n")

# ---------- HTML ----------
def bom_html():
    rows, g0 = [], None
    for r in B.BOM:
        if r[0] != g0:
            rows.append('<tr class="grp"><td colspan="7">%s</td></tr>' % e(r[0])); g0 = r[0]
        links = "".join('<a href="%s" target="_blank" rel="noopener">%s ↗</a>' % (e(u), e(a)) for a, u in r[5]) or "—"
        rows.append("<tr><td><b>%s</b><br><span class='muted'>%s</span></td><td class='links'>%s</td><td>%d</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                    % (e(r[1]), e(r[2]), links, r[3], price(r), e(r[6]), e(r[7])))
    return ('<div class="tablewrap"><table class="bom"><tr><th>Item</th><th>Buy online</th><th>Qty</th><th>Unit ₹</th><th>What to ask for</th><th>Where offline</th></tr>'
            + "".join(rows).replace('colspan="7"', 'colspan="6"') + "</table></div>")

STEPS = [
 ("08_spar", "Spar caps", "Epoxy (Araldite Standard), thin layer",
  ["Cut two 3 × 6 × 984 mm strips from the hardest 3 mm sheet.", "Glue two 3 × 0.5 mm carbon strips side by side on one 6 mm face of each strip.",
   "Lay them on a flat board covered with plastic film, put a steel rule and weights on top, cure 24 h.", "Sand off squeezed-out epoxy; mark the carbon face."]),
 ("09_ribs", "Ribs on the bottom spar cap", "Thin CA at each joint",
  ["Pin the plan (or mark rib stations every 55 mm from the centre) on the board.", "Pin the bottom spar cap carbon-face-down over its line.",
   "Pack the rib noses on a 3.5 mm strip (at x = 6 mm) and the rib tails on a 7.8 mm strip (at x = 205 mm): this sets the airfoil angle.",
   "Slide every rib on, square it with a set square, wick thin CA into the notch. 3 mm ribs at y = ±110; the centre rib at y = 0."]),
 ("10_le_te", "Leading edge, false spar, trailing edge", "CA or PVA; pins on both sides",
  ["Glue the 6 × 17 mm LE to the rib noses (x = 0–6 mm), carve it later.", "Glue the 3 mm false spar (vertical grain pieces, joints on ribs) at x = 205–208 mm.",
   "Add the aft rib pieces (x = 208–255) in the fixed bays and the hard TE wedges (x = 255–280).", "Sight along the TE: it must be straight; pin it."]),
 ("11_webs", "Top spar cap and shear webs", "CA; vertical grain",
  ["Glue the top spar cap carbon-face-up into the rib notches.", "Fit the 1.5 mm vertical-grain webs between the ribs on the front face of the spar (full span) and on the rear face up to y = ±164 mm.",
   "The webs must touch both caps: this makes the spar a box that carries the bending load."]),
 ("12_top", "Top sheeting and cap strips", "PVA on the ribs; CA tacks at the edges",
  ["Sand ribs, spar and LE flush with a long block.", "Glue the 78 mm wide top D-box sheet (x = 6–80); wet the outer face lightly so it bends round the nose.",
   "Add the four top centre-sheet pieces (grain chord-wise) and the 1.5 × 6 mm cap strips on each rib."]),
 ("13_flip", "Turn over: bottom sheeting and servo frames", "PVA sheeting; epoxy for the PETG frames",
  ["Unpin, turn the wing over and support it on the top surface.", "Glue the bottom D-box sheet (74 mm wide), the bottom centre sheets (with the Ø10 mm wire exit holes) and the bottom cap strips.",
   "Epoxy the printed servo frames between ribs 110 and 165 (glue tabs on the rib faces). Pull the servo leads through the rib holes now."]),
 ("14_tips", "Tip ribs and tip caps", "PVA laminate, grain crossed",
  ["Laminate each tip rib from layer a (grain chord-wise) and layer b (3 vertical-grain pieces); press flat.", "Glue the tip rib at y = 489–492 mm, then the 3 mm ring tip cap at 492–495 mm.",
   "Sand the whole wing; round the LE to the airfoil nose with a sanding block."]),
 ("15_ailerons", "Ailerons", "CA; V-bevel 1.5 mm each side",
  ["Build each aileron on the board: 3 mm LE, end ribs, station ribs, horn rib at y = 148.85–150.85, TE wedge.", "Sand the LE to a V (apex on the hinge line) so it can move ±20°.",
   "Cut the four 20 mm hinge slots at y = 130, 247.5, 302.5 and 420 mm in the false spar and the aileron LE."]),
 ("17_servo", "Hinges, horns and servos", "Thin CA hinges; epoxy horns; M2 × 4 screws",
  ["Cover first (see Covering), then push the CA hinges in, align, and wick thin CA into both sides.", "Epoxy the slot-in horn to the horn rib and the aileron LE; the hole is 16.5 mm below the hinge line.",
   "Screw each MG90S to its hatch lugs, connect the 1.2 mm pushrod with Z-bends (70.5 mm between holes), fix the hatch with 4 × M2 × 4."]),
 ("18_final", "Finish and check", "Epoxy rub plates",
  ["Glue the band rub plates at the centre LE and TE.", "Centre the servos, set ±15° aileron throw (≈ ±20° servo).", "Weigh it without servos (model 156.6 g). Record it in the mass table."]),
]

def steps_html():
    out = []
    for k, (sid, title, glue, items) in enumerate(STEPS, 1):
        li = "".join("<li>%s</li>" % e(x) for x in items)
        out.append('<div class="step"><div><h3><span class="num">%d</span>%s</h3><ul>%s</ul><p class="glue"><span class="tag user">GLUE</span>%s</p></div>'
                   '<figure class="figure"><img loading="lazy" src="%s" alt="Step %d: %s"><figcaption>Orange = parts added in this step.</figcaption></figure></div>'
                   % (k, e(title), li, e(glue), I[sid], k, e(title)))
    return "\n".join(out)

GLUES = [("Thin CA", "Seconds", "Rib to spar caps, cap strips, aileron parts, CA hinges (wick in).", "Tight joints only; does not fill gaps. Keep debonder near; eye protection."),
         ("PVA (Fevicol SH)", "30–60 min to handle", "Sheeting, tip-rib laminate, edge-joining sheets, LE stock.", "Gives time to adjust; sands easily; light. Pin or tape while it sets."),
         ("Epoxy (Araldite)", "5 min – 24 h", "Carbon to balsa, PETG frames, horns, rub plates.", "Mix 1:1 by volume, thin layer, wipe the excess: epoxy is heavy.")]
glue_rows = "".join("<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td></tr>" % tuple(map(e, g)) for g in GLUES)
sheet_rows = "".join("<tr><td>%s</td><td>%d cm³</td><td>≤ %.1f g</td><td>≈ %.1f g</td></tr>" % t for t in B.TARGET_SHEET_MASS)
CHECKS = [("Span", "990.00 mm", "≤ 1000 mm (rule)"), ("Chord", "280.0 mm", "280 mm"), ("Airfoil depth at the spar (x = 75.6)", "39.20 mm", "39.1 mm (plan)"),
          ("Overlapping parts (> 1 mm³)", "0 of 276 neighbour pairs", "0"), ("Servo clearance to structure", "≥ 1.00 mm (arm ±35°)", "≥ 1 mm"),
          ("Aileron at ±20°", "no contact, 0.74 mm gap", "no contact"), ("Aileron length / end gaps", "325.00 / 1.00 mm", "325 / 1 mm"),
          ("Mass without servos", "156.6 g", "report (no fixed limit)"), ("Mass with 2 × MG90S", "184.0 g", "—")]
check_rows = "".join("<tr><td>%s</td><td><b>%s</b></td><td class='muted'>%s</td><td class='ok'>✔</td></tr>" % tuple(map(e, c)) for c in CHECKS)
MASS = []
for r in csv.DictReader(open(os.path.join(CAD, "mass_table.csv"))):
    MASS.append(r)
def mass_groups():
    import re, collections
    rules = [("^LE$", "Leading edge"), ("^DBox|^CSheet", "Sheeting (D-box + centre)"), ("^Spar", "Spar caps (balsa + carbon)"), ("^ShearWeb", "Shear webs"),
             ("^FalseSpar", "False spar"), ("^Rib|^TipRib", "Ribs (incl. tip ribs)"), ("^TipCap", "Tip caps"), ("^Caps_", "Cap strips"), ("^TE_", "TE wedges"),
             ("^Ail_", "Ailerons"), ("^Servo|^Horn|^RubPlate", "Printed PETG parts"), ("^Pushrod|screws|hinges", "Pushrods, screws, hinges"),
             ("^Film", "Film covering"), ("^Glue", "Glue (estimate)")]
    g = collections.OrderedDict()
    for r in MASS:
        if r["part"] == "TOTAL":
            continue
        k = next((n for p, n in rules if re.search(p, r["part"])), r["part"]); g[k] = g.get(k, 0) + float(r["mass_g"])
    return "".join("<tr><td>%s</td><td>%.1f g</td></tr>" % (e(k), v) for k, v in g.items())
TOTAL = [r for r in MASS if r["part"] == "TOTAL"][0]["mass_g"]

DOWNLOADS = [("Laser DXF files (21 sheets, 300 × 100 mm)", TREE + "design/cad/dxf", "design/cad/dxf/"),
             ("PETG STL files (frames, hatches, horns, rub plates)", TREE + "design/cad/stl", "design/cad/stl/"),
             ("STEP model of the wing", BLOB + "design/cad/Wing_revA.step", "Wing_revA.step · 14 MB"),
             ("FreeCAD model", BLOB + "design/cad/Wing_revA.FCStd", "Wing_revA.FCStd · FreeCAD 1.1"),
             ("Cut list (strip stock and laser groups)", BLOB + "design/cad/cut_list.md", "cut_list.md"),
             ("Mass table", BLOB + "design/cad/mass_table.md", "mass_table.md"),
             ("Indian BOM (CSV)", BLOB + "bom/BOM_India.csv", "BOM_India.csv"),
             ("Full design report", BLOB + "docs/REPORT.md", "REPORT.md"),
             ("Decision record (D-001 … D-023)", BLOB + "design/DECISIONS.md", "DECISIONS.md"),
             ("Re-runnable FreeCAD scripts", TREE + "design/cad/scripts", "run_all.py and modules"),
             ("Video (MP4, 1080p, 6:35)", "media/wing_build.mp4", "47 MB")]
dl = "".join('<a href="%s">%s<span>%s</span></a>' % (e(u), e(a), e(b)) for a, u, b in DOWNLOADS)

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Balsa Wing Build</title>
<meta name="description" content="Build and assembly tutorial for a 990 mm laser-cut balsa wing (SD7062, 157 g) for a water-drop RC aircraft: video, Indian BOM with shop links, DXF, STL, STEP and FreeCAD files.">
<link rel="stylesheet" href="style.css"></head><body>
<nav class="top"><b>water-drop-rc-wing</b><a href="#video">Video</a><a href="#design">Design</a><a href="#bom">Indian BOM</a><a href="#shopping">Shopping offline</a><a href="#tools">Tools</a><a href="#laser">Laser cutting</a><a href="#glues">Glues</a><a href="#build">Build steps</a><a href="#covering">Covering</a><a href="#servo">Servo</a><a href="#checks">Checks</a><a href="#downloads">Downloads</a><a href="{REPO}">GitHub ↗</a></nav>
<header class="hero"><div class="wrap grid"><div>
<div class="kicker">Boeing National Aeromodelling Competition 2026-27 · IIT Madras zone</div>
<h1>A 157 g balsa wing for a water-drop RC aircraft</h1>
<p class="lead">Laser-cut ribs, carbon-capped spar, sheeted D-box and printed PETG servo mounts. This page is the complete build tutorial: video, Indian bill of materials with shop links, what to ask for in local shops, and every file you need.</p>
<div class="stats"><div class="stat"><b>990 mm</b><span>span</span></div><div class="stat"><b>280 mm</b><span>chord · SD7062</span></div><div class="stat"><b>156.6 g</b><span>without servos</span></div><div class="stat"><b>±15°</b><span>ailerons · MG90S</span></div></div>
<a class="btn" href="#video">▶ Watch the build video</a><a class="btn ghost" href="#bom">Indian BOM</a><a class="btn ghost" href="{REPO}">Files on GitHub</a>
</div><div><img src="{I['wing_iso']}" alt="Isometric view of the wing"></div></div></header>

<section id="video"><div class="wrap"><h2>Build and assembly video<small>6 min 35 s · narration with burned-in captions · the links mentioned in the video are in the <a href="#bom">BOM below</a> and on <a href="{REPO}">GitHub</a></small></h2>
<div class="video"><video controls preload="metadata" poster="media/poster.jpg"><source src="media/wing_build.mp4" type="video/mp4"><track kind="captions" srclang="en" label="English" src="media/wing_build.en.vtt"></video></div>
<p class="muted">Chapters: intro 0:00 · wing overview 0:32 · materials 0:55 · tools 1:19 · weighing balsa 1:35 · laser cutting 1:55 · strip stock 2:17 · glues 2:34 · steps 1–8 3:00 · covering 5:13 · servos 5:31 · checks and links 6:04</p>
</div></section>

<section id="design"><div class="wrap"><h2>Design at a glance<small>What the wing must do, and why it looks like this</small></h2>
<div class="split"><div>
<p>Score = water mass ÷ empty mass, so every gram counts — but the same aircraft must survive every flight and hand launch. The wing is a classic built-up balsa structure, sized and checked in FreeCAD with re-runnable scripts.</p>
<table><tr><th>Item</th><th>Value</th></tr>
<tr><td>Span / chord / area</td><td>990 mm / 280 mm / 0.277 m²</td></tr><tr><td>Airfoil</td><td>SD7062 (14 %), gentle stall, low drag</td></tr>
<tr><td>Dihedral / position</td><td>0°, high wing, rubber-band mount</td></tr><tr><td>Spar</td><td>3 × 6 hard balsa + 0.5 × 6 carbon caps, 1.5 mm webs; margin ≈ 4 at n = 6</td></tr>
<tr><td>Torsion</td><td>1.5 mm D-box sheeting to 29 % chord</td></tr><tr><td>Ailerons</td><td>70 × 325 mm, CA hinges, MG90S on its side</td></tr></table>
</div><figure class="figure"><img loading="lazy" src="{I['wing_iso_open']}" alt="Wing structure with the top skins removed"><figcaption>Structure with the top skins hidden.</figcaption></figure></div>
<div class="cards">
<div class="card"><h4>SD7062 airfoil</h4><p>Lower drag at loaded cruise and after the drop than high-lift sections (E423, S1223), small pitching moment. <span class="tag user">D-001</span></p></div>
<div class="card"><h4>Balsa built-up</h4><p>137–157 g against ≈ 176 g LW-PLA and ≈ 208 g foam. Repairable at the venue. <span class="tag user">D-003</span></p></div>
<div class="card"><h4>0° dihedral</h4><p>One flat piece, continuous spar and sheeting, no joiner. The high wing gives some effective dihedral. <span class="tag user">D-012</span></p></div>
<div class="card"><h4>Mass reduction set</h4><p>Bigger lightening holes, lighter grades where loads are low, ring tip caps: 172 g → 157 g. <span class="tag user">D-013</span></p></div>
</div>
<p class="muted">Full reasoning, numbers and every decision: <a href="{BLOB}docs/REPORT.md">design report</a> and <a href="{BLOB}design/DECISIONS.md">decision record</a>.</p>
</div></section>

<section id="bom"><div class="wrap"><h2>Indian bill of materials<small>Quantities for one wing + spares · prices as listed online in November 2026 · estimated total ≈ ₹{total:,} for the priced items</small></h2>
<div class="note">Prices and stock change — check before you order. No affiliation with any shop. The same list is in <a href="{BLOB}bom/BOM_India.md">BOM_India.md</a> and <a href="{BLOB}bom/BOM_India.csv">BOM_India.csv</a>.</div>
{bom_html()}
</div></section>

<section id="shopping"><div class="wrap"><h2>Shopping offline<small>What to ask for, and where</small></h2>
<div class="split"><div>
<ul>
<li><b>Take the cut list and a pocket scale.</b> Weigh balsa in the shop and choose by weight (table on the right), not by look. Straight grain, no hard streaks.</li>
<li><b>Electronics markets</b> — {e(B.MARKETS)}: MG90S servos (ask for the 180° version), servo leads, M2 × 4 screws, often carbon rods and strips.</li>
<li><b>Hardware shops:</b> Fevicol SH, Araldite, Fevikwik, emery paper, 18 SWG spring-steel wire (pushrods), heat gun, 1 m steel rule, masking tape.</li>
<li><b>Plywood shops:</b> 12 mm MDF building board cut to 1200 × 400 mm (check it is flat) and soft board to pin into.</li>
<li><b>3D-printing shops / maker spaces:</b> print the 8 PETG parts from the STL files.</li>
<li><b>Laser sign-board shops:</b> many can cut 2–3 mm balsa from the DXF files at low power — ask for a test cut first.</li>
<li><b>RC hobby shops only:</b> iron-on covering film and CA hinges.</li>
</ul></div><div>
<table><tr><th>Sheet 100 × 1000</th><th>Volume</th><th>Light 90 kg/m³</th><th>Medium 130 kg/m³</th></tr>{sheet_rows}</table>
<figure class="figure" style="margin-top:14px"><img loading="lazy" src="{I['04_weigh']}" alt="Weighing a balsa sheet"></figure>
</div></div></div></section>

<section id="tools"><div class="wrap"><h2>Tools and safety</h2>
<div class="cards">
<div class="card"><h4>Cutting</h4><p>Laser cutter (we plan a Bambu H2D laser module, work area ≈ 310 × 270 mm) or a sharp knife with No. 11 blades; self-healing mat; 1 m steel rule.</p></div>
<div class="card"><h4>Building</h4><p>Flat 1.2 m board, T-pins, set square, clothes pegs, masking tape, weights.</p></div>
<div class="card"><h4>Shaping</h4><p>Long sanding block (≥ 300 mm), 150/220/320 grit, razor plane optional.</p></div>
<div class="card"><h4>Covering</h4><p>Sealing iron (or small dry iron with a sock) and a heat gun.</p></div>
<div class="card"><h4>Measuring</h4><p>0.01–0.1 g scale, vernier caliper, throw gauge (a ruler and a protractor work).</p></div>
<div class="card"><h4>Safety</h4><p>Fresh air for CA and epoxy, eye protection, CA debonder, gloves for epoxy, a fire extinguisher next to the laser — never leave it running alone.</p></div>
</div></div></section>

<section id="laser"><div class="wrap"><h2>Laser cutting<small>21 DXF sheets of 300 × 100 mm, grouped by thickness and grade</small></h2>
<div class="split"><div>
<ul><li>Cut a 100 × 1000 sheet into three 300 mm pieces <b>along the grain</b>; in every DXF the grain runs along X (the 300 mm side).</li>
<li>Cut only layer <code>CUT</code>. Layer <code>LABEL</code> has part names (do not cut), layer <code>SHEET</code> is the sheet outline (check the scale = 300 × 100 mm on import).</li>
<li>Inner holes first, outlines last, so parts do not move.</li>
<li>Balsa needs low power and high speed: make test cuts on scrap, with air assist, and check the kerf (≈ 0.1–0.2 mm, not compensated in the files).</li>
<li>Groups: 2 mm medium (8 sheets: ribs, aileron ribs), 3 mm medium (3: ribs 110, false spar pieces), 1.5 mm medium (4: shear webs), 1.5 mm light (2: tip-rib layers), 1.5 mm selected light (3: centre sheeting), 3 mm light (1: tip caps).</li></ul>
<figure class="figure"><img loading="lazy" src="{I['05_laser']}" alt="Laser cutting animation"></figure>
</div><div><figure class="figure"><img loading="lazy" src="{I['dxf']}" alt="Preview of the 2 mm laser sheets"><figcaption>All eight 2 mm sheets.</figcaption></figure>
<figure class="figure" style="margin-top:12px"><img loading="lazy" src="{I['dxf2']}" alt="Preview of the other laser sheets"><figcaption>Tip-rib layers, tip caps, false-spar pieces, centre sheeting and webs.</figcaption></figure></div></div>
<h3>Strip stock (knife and steel rule)</h3>
<div class="split"><div><p>Spar caps 3 × 6 × 984 (hard), LE 6 × 17 × 984, TE stock 25 × 4.6 (wing 330 mm, ailerons 2 × 325), aileron LE 3 × 15.5 × 325, D-box sheets 78 and 74 mm wide × 984, cap strips 1.5 × 6 (32 × 126 mm, 12 × 48 mm). Every length is in the <a href="{BLOB}design/cad/cut_list.md">cut list</a>.</p></div>
<figure class="figure"><img loading="lazy" src="{I['06_strips']}" alt="Cutting strips"></figure></div>
</div></section>

<section id="glues"><div class="wrap"><h2>Which glue goes where</h2>
<div class="tablewrap"><table><tr><th>Glue</th><th>Set time</th><th>Use for</th><th>Notes</th></tr>{glue_rows}</table></div>
<figure class="figure"><img loading="lazy" src="{I['07_glue']}" alt="Glue guide animation"></figure>
</div></section>

<section id="build"><div class="wrap"><h2>Build steps<small>Build on a flat board, right side up: the bottom spar cap is pinned down and packing strips set the rib angle</small></h2>
{steps_html()}
</div></section>

<section id="covering"><div class="wrap"><h2>Covering</h2><div class="split"><div>
<ol><li>Sand smooth, vacuum the dust.</li><li>Cover the ailerons separately from the wing.</li>
<li>Iron the film down on the edges and glue lines first, at about 110–120 °C (follow the film maker).</li>
<li>Shrink the open bays with the heat gun on its low setting; keep it moving.</li>
<li>Cut the film away over the hinge slots, the servo hatches and the wire exits.</li>
<li>Light film ≈ 50 g/m² → about 29 g for this wing: do not overlap more than 5 mm.</li></ol>
</div><figure class="figure"><img loading="lazy" src="{I['16_cover']}" alt="Covering animation"></figure></div></div></section>

<section id="servo"><div class="wrap"><h2>Servo installation and linkage</h2><div class="split"><div>
<ul><li>MG90S lies on its side between ribs 110 and 165, shaft outboard; it screws to two lugs on the 0.8 mm PETG hatch, so the servo comes out with the hatch.</li>
<li>Servo arm 12.65 mm, horn 16.47 mm below the hinge line, pushrod 70.5 mm between holes, 4 mm below the skin.</li>
<li>±15° aileron needs ≈ ±20° servo; the V-bevel allows ±20° with no contact.</li>
<li>Clearances checked in CAD: servo ≥ 1.00 mm to frame and hatch plate, arm ≥ 1.00 mm to the hatch slot at ±35°.</li>
<li>The servo in the model is a placeholder with standard MG90S dimensions — measure your servos before printing.</li></ul>
</div><div><figure class="figure"><img loading="lazy" src="{I['wing_section_y148']}" alt="Section through the pushrod plane"><figcaption>Section at y = 148 mm: arm, pushrod, horn.</figcaption></figure>
<figure class="figure" style="margin-top:12px"><img loading="lazy" src="{I['wing_servo_bay_iso']}" alt="Servo bay"><figcaption>Servo bay (top skin removed).</figcaption></figure></div></div></div></section>

<section id="checks"><div class="wrap"><h2>Checks and mass</h2><div class="split"><div>
<div class="tablewrap"><table><tr><th>Check</th><th>Result</th><th>Required</th><th></th></tr>{check_rows}</table></div></div>
<div><div class="tablewrap"><table><tr><th>Mass group</th><th>Mass</th></tr>{mass_groups()}<tr><td><b>Wing without servos</b></td><td><b>{TOTAL} g</b></td></tr></table></div>
<p class="muted">Volume × density from the CAD model. Film and glue ± 5 g, balsa ± 20 % between sheets: weigh your parts.</p></div></div>
<h3>Known limits</h3><ul><li>Hinge gap 2 mm (false spar to aileron apex); smallest gap at ±20° is 0.74 mm.</li>
<li>Band rub plate width (± 15 mm) and the wire exit (y = ± 28 mm) depend on the fuselage, not designed yet.</li>
<li>No structural FEA; the spar was sized by hand (margin ≈ 4 at load factor 6).</li><li>The DXF files are not tested on a laser yet.</li></ul>
</div></section>

<section id="downloads"><div class="wrap"><h2>Downloads</h2><div class="dl">{dl}</div></div></section>
<footer><div class="wrap">Designed in FreeCAD 1.1 with re-runnable Python scripts. Video narration: macOS text-to-speech. Repository: <a href="{REPO}">{REPO}</a>.</div></footer>
</body></html>"""
open(os.path.join(DOCS, "index.html"), "w").write(page)
shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site_style.css"), os.path.join(DOCS, "style.css"))
open(os.path.join(DOCS, ".nojekyll"), "w").write("")
print("site written:", os.path.join(DOCS, "index.html"), "BOM total ₹", total)
