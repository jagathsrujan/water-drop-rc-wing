"""Compose the build video: 2D animated segments (PIL) + FreeCAD frames + narration + captions -> wing_build.mp4.
Usage: python3 make_video.py [segment ids...]   (no ids = all; clips cached in clips/)."""
import json, math, os, random, subprocess, sys, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.dirname(HERE)
CAD = os.path.join(DESIGN, "cad")
sys.path.insert(0, os.path.join(CAD, "scripts"))
import dxf_io
W, H = 1920, 1080
HDR, CAP = 100, 140
CY0, CY1 = HDR, H - CAP                       # content area 840 px
FPS2D, FPSFC = 30, 8
NAV, ORANGE, INK, MUTED, PAPER = (16, 32, 58), (240, 120, 20), (25, 30, 40), (95, 105, 120), (250, 248, 243)
BALSA, BALSA_D = (233, 205, 150), (205, 170, 110)
F = "/System/Library/Fonts/Supplemental/"
def font(sz, bold=False):
    return ImageFont.truetype(F + ("Arial Bold.ttf" if bold else "Arial.ttf"), sz)
FT = {k: font(*k) for k in [(28, False), (30, False), (34, False), (36, True), (40, False), (44, True), (52, True), (64, True), (80, True), (26, False), (24, False), (30, True), (34, True), (40, True), (22, False)]}
NAR = json.load(open(os.path.join(HERE, "narration.json")))
STEPNO = {"08_spar": 1, "09_ribs": 2, "10_le_te": 3, "11_webs": 4, "12_top": 5, "13_flip": 6, "14_tips": 7, "15_ailerons": 8, "17_servo": 9, "18_final": 10}
GLUE = {"08_spar": "Epoxy (thin layer), weight on top", "09_ribs": "Thin CA at each rib/spar joint", "10_le_te": "CA or PVA; pins both sides",
        "11_webs": "CA; webs with vertical grain", "12_top": "PVA on the ribs; wet the nose lightly", "13_flip": "PVA sheeting; epoxy for the PETG frames",
        "14_tips": "PVA laminate, crossed grain", "15_ailerons": "CA; V-bevel 1.5 mm each side", "17_servo": "Thin CA hinges; epoxy horns; M2 x 4 screws",
        "18_final": "Epoxy rub plates; throws ±15°"}

# ---------------- captions ----------------
def sentences(text):
    import re
    s = re.split(r"(?<=[.!?])\s+", text.strip())
    return [x for x in s if x]

def caption_track(seg):
    """[(t0, t1, sentence)] from the character count; audio starts at 0.3 s."""
    ss = sentences(seg["text"])
    tot = sum(len(x) for x in ss)
    t, out = 0.3, []
    for x in ss:
        d = seg["dur"] * len(x) / tot
        out.append((t, t + d, x)); t += d
    return out

def spoken(x):   # captions: show normal text instead of the spelled-out letters
    rep = {"S D 7062": "SD7062", "P E T G": "PETG", "M G 90 S": "MG90S", "C A": "CA", "P V A": "PVA", "Fevicol S H": "Fevicol SH",
           "D X F": "DXF", "M 2": "M2", "github dot com, slash jagath srujan, slash water-drop R C wing": "github.com/jagathsrujan/water-drop-rc-wing"}
    for a, b in rep.items():
        x = x.replace(a, b)
    return x

def frame_base(seg, t, content):
    im = Image.new("RGB", (W, H), PAPER)
    im.paste(content, (0, CY0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, HDR], fill=NAV)
    d.text((40, 26), seg["title"], font=FT[(44, True)], fill="white")
    d.text((W - 40, 34), "water-drop-rc-wing · rev A", font=FT[(28, False)], fill=(170, 185, 210), anchor="ra")
    if seg["id"] in STEPNO:                        # step progress bar
        n = STEPNO[seg["id"]]
        for k in range(10):
            x0 = 40 + k * 60
            d.rounded_rectangle([x0, HDR - 14, x0 + 50, HDR - 6], 4, fill=ORANGE if k < n else (60, 80, 110))
    d.rectangle([0, CY1, W, H], fill=(20, 24, 32))
    cur = [c for c in caption_track(seg) if c[0] <= t < c[1] + 0.25]
    if cur:
        lines = textwrap.wrap(spoken(cur[-1][2]), 78)[:3]
        y = CY1 + (CAP - 44 * len(lines)) // 2
        for ln in lines:
            d.text((W // 2, y), ln, font=FT[(36, True)] if False else FT[(34, False)], fill="white", anchor="ma"); y += 44
    return im

# ---------------- helpers ----------------
def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

def content_canvas():
    return Image.new("RGB", (W, CY1 - CY0), PAPER)

def paste_fit(dst, src, box, scale_extra=1.0):
    x0, y0, x1, y1 = box
    s = min((x1 - x0) / src.width, (y1 - y0) / src.height) * scale_extra
    im = src.resize((max(1, int(src.width * s)), max(1, int(src.height * s))), Image.LANCZOS)
    dst.paste(im, (x0 + (x1 - x0 - im.width) // 2, y0 + (y1 - y0 - im.height) // 2))

IMG = {}
def img(name):
    if name not in IMG:
        IMG[name] = Image.open(os.path.join(CAD, "img", name)).convert("RGB")
    return IMG[name]

def chip(d, x, y, txt, fill=(255, 255, 255), fg=INK, f=(30, False)):
    w = d.textlength(txt, font=FT[f]) + 36
    d.rounded_rectangle([x, y, x + w, y + 56], 28, fill=fill, outline=(220, 215, 205), width=2)
    d.text((x + 18, y + 12), txt, font=FT[f], fill=fg)
    return x + w + 16

# ---------------- 2D segment painters: f(seg, t) -> content image ----------------
def p_intro(seg, t):
    c = content_canvas(); d = ImageDraw.Draw(c)
    s = 1.0 + 0.04 * t / seg["seg"]
    src = img("wing_iso.png")
    a = ease(t / 1.5)
    big = Image.new("RGB", c.size, PAPER); paste_fit(big, src, (760, 40, 1880, 800), s)
    c = Image.blend(c, big, a); d = ImageDraw.Draw(c)
    d.text((70, 90), "Balsa wing", font=FT[(80, True)], fill=NAV)
    d.text((70, 190), "Build and assembly tutorial", font=FT[(52, True)], fill=ORANGE)
    d.text((70, 280), "Boeing National Aeromodelling Competition 2026-27", font=FT[(34, False)], fill=MUTED)
    d.text((70, 326), "IIT Madras zone · water-drop task", font=FT[(34, False)], fill=MUTED)
    y = 430
    specs = ["Span 990 mm", "Chord 280 mm", "SD7062", "Dihedral 0°", "157 g (no servos)", "Ailerons + MG90S"]
    x = 70
    for i, sp in enumerate(specs):
        if t > 2 + i * 0.8:
            x = chip(d, x, y, sp)
            if x > 680:
                x, y = 70, y + 76
    if t > 9:
        d.text((70, 680), "Files, Indian BOM and links:", font=FT[(30, True)], fill=INK)
        d.text((70, 720), "jagathsrujan.github.io/water-drop-rc-wing", font=FT[(34, False)], fill=NAV)
    return c

MATS = [("Balsa 1.5 mm sheets", "8 × (100 × 1000)", BALSA), ("Balsa 2 mm sheets", "4 × (100 × 1000)", BALSA_D), ("Balsa 3 mm sheets", "4 × (100 × 1000)", (190, 150, 95)),
        ("Balsa 6 mm sheet", "1 × (100 × 1000)", (175, 135, 80)), ("Carbon strip 3 × 0.5 mm", "4 × 1000 mm", (30, 30, 30)), ("Covering film", "1 roll, 3 m", (250, 215, 40)),
        ("CA hinges 20 mm", "8 (+4 spare)", (235, 235, 225)), ("Steel pushrod 1.2 mm", "2", (160, 165, 175)), ("PETG filament", "≈ 30 g", (40, 110, 210)),
        ("MG90S servo", "2", (60, 60, 70)), ("M2 × 4 screws", "8", (150, 150, 150)), ("Glues: thin CA, PVA, epoxy", "", (230, 90, 60))]
def p_list(items, seg, t, title2):
    c = content_canvas(); d = ImageDraw.Draw(c)
    d.text((70, 40), title2, font=FT[(40, True)], fill=NAV)
    n = len(items); per = max(0.5, (0.7 * seg["dur"]) / n)
    for i, (a, b, col) in enumerate(items):
        k = ease((t - 0.5 - i * per) / 0.5)
        if k <= 0:
            continue
        colx = 70 + (i % 2) * 900; row = i // 2
        y = 120 + row * 110 + int(20 * (1 - k))
        d.rounded_rectangle([colx, y, colx + 840, y + 90], 18, fill=(255, 255, 255), outline=(225, 220, 210), width=2)
        d.rounded_rectangle([colx + 18, y + 18, colx + 72, y + 72], 10, fill=col)
        d.text((colx + 96, y + 14), a, font=FT[(34, True)], fill=INK)
        if b:
            d.text((colx + 96, y + 52), b, font=FT[(26, False)], fill=MUTED)
    return c

TOOLS = [("Laser cutter (or hobby knife)", "parts from the DXF files", (200, 60, 50)), ("Flat building board ≥ 1.2 m", "MDF + soft pin board", (190, 160, 120)),
         ("T-pins, set square, steel rule", "keep everything square", (150, 150, 160)), ("Sanding blocks 120 / 220 / 400", "long block for the skins", (210, 190, 150)),
         ("Covering iron + heat gun", "seal, then shrink", (90, 90, 100)), ("Scale 0.1 g", "weigh every sheet and part", (60, 140, 90)),
         ("3D printer (PETG)", "frames, hatches, horns", (40, 110, 210)), ("Fresh air, glasses, fire extinguisher", "safety first", (230, 60, 60))]

def p_weigh(seg, t):
    c = content_canvas(); d = ImageDraw.Draw(c)
    # scale
    d.rounded_rectangle([140, 520, 760, 640], 20, fill=(70, 75, 85))
    d.rounded_rectangle([360, 560, 560, 615], 8, fill=(20, 40, 25))
    m = 26.0 * ease((t - 1.5) / 2.5)
    d.text((460, 565), "%.1f g" % m, font=FT[(40, True)], fill=(120, 255, 140), anchor="ma")
    drop = ease((t - 0.3) / 1.2)
    y = int(240 + 230 * drop)
    d.rectangle([100, y, 800, y + 30], fill=BALSA, outline=BALSA_D, width=3)
    for gx in range(110, 800, 26):
        d.line([gx, y + 4, gx + 14, y + 26], fill=BALSA_D, width=1)
    d.text((450, y - 50), "2 mm × 100 × 1000 sheet", font=FT[(30, False)], fill=MUTED, anchor="ma")
    if t > 4.5:
        d.text((900, 120), "density = mass / volume", font=FT[(44, True)], fill=NAV)
        d.text((900, 190), "26 g / (0.2 × 10 × 100 cm³) = 0.13 g/cm³ = 130 kg/m³", font=FT[(34, False)], fill=INK)
    bins = [("LIGHT  < 100", "D-box + centre sheeting, cap strips, tip caps", (120, 190, 120)),
            ("MEDIUM 100–150", "ribs, webs, false spar, LE, ailerons", (240, 180, 60)),
            ("HARD   > 150", "spar caps, wing TE wedges", (220, 110, 70))]
    for i, (a, b, col) in enumerate(bins):
        k = ease((t - 7 - i * 1.6) / 0.6)
        if k <= 0:
            continue
        y0 = 300 + i * 150
        d.rounded_rectangle([900, y0, 1840, y0 + 120], 18, fill=(255, 255, 255), outline=col, width=5)
        d.text((930, y0 + 16), a + " kg/m³", font=FT[(36, True)] if False else FT[(34, True)], fill=INK)
        d.text((930, y0 + 66), b, font=FT[(30, False)], fill=MUTED)
        if seg_hl(t, 1.0, 7 + i * 1.6):
            d.rounded_rectangle([900, y0, 1840, y0 + 120], 18, outline=ORANGE, width=6)
    return c

def seg_hl(t, dur, t0):
    return t0 <= t < t0 + dur

# laser: draw the real DXF paths progressively
LASER = {}
def laser_setup():
    ents = dxf_io.read(os.path.join(CAD, "dxf", "laser_2mm_medium_sheet01.dxf"))
    sc, ox, oy = 5.4, 160, 50
    tr = lambda x, y: (ox + x * sc, oy + (100 - y) * sc)
    paths = []
    for e in ents:
        if e[1] != "CUT":
            continue
        if e[0] == "poly":
            pts = [tr(*p) for p in e[2]]; pts.append(pts[0])
        else:
            x, y, r = e[2]; pts = [tr(x + r * math.cos(a / 48 * 2 * math.pi), y + r * math.sin(a / 48 * 2 * math.pi)) for a in range(49)]
        paths.append(pts)
    # cut inner features (holes, small loops) before the outer outlines
    paths.sort(key=lambda p: (max(q[0] for q in p) - min(q[0] for q in p)) * (max(q[1] for q in p) - min(q[1] for q in p)))
    seq, L = [], 0.0
    for p in paths:
        for a, b in zip(p, p[1:]):
            l = math.dist(a, b); seq.append((a, b, L, l)); L += l
    LASER.update(seq=seq, L=L, sheet=(tr(0, 100), tr(300, 0)))

def p_laser(seg, t):
    if not LASER:
        laser_setup()
    c = content_canvas(); d = ImageDraw.Draw(c)
    (x0, y0), (x1, y1) = LASER["sheet"]
    d.rectangle([x0 - 30, y0 - 30, x1 + 30, y1 + 30], fill=(60, 60, 64))          # honeycomb bed
    for gx in range(int(x0 - 30), int(x1 + 30), 18):
        d.line([gx, y0 - 30, gx, y1 + 30], fill=(75, 75, 80))
    d.rectangle([x0, y0, x1, y1], fill=BALSA)
    for gy in range(int(y0) + 6, int(y1), 9):
        d.line([x0, gy, x1, gy + random.Random(gy).randint(-2, 2)], fill=(222, 192, 135))
    T = seg["seg"] - 1.5
    done = LASER["L"] * ease(t / T) if t < T else LASER["L"]
    head = None
    for a, b, l0, l in LASER["seq"]:
        if l0 > done:
            break
        if l0 + l <= done:
            d.line([a, b], fill=(70, 40, 20), width=3)
        else:
            f = (done - l0) / l; p = (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
            d.line([a, p], fill=(70, 40, 20), width=3); head = p
    if head and t < T:
        hx, hy = head
        d.rectangle([x0 - 40, hy - 14, x1 + 40, hy + 14], fill=(110, 115, 125))            # gantry
        d.rounded_rectangle([hx - 34, hy - 46, hx + 34, hy + 20], 10, fill=(40, 42, 48))     # head
        glow = Image.new("RGBA", c.size, (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
        for r, a in ((26, 40), (14, 90), (6, 255)):
            g.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(255, 80, 40, a))
        rnd = random.Random(int(t * 30))
        for k in range(10):                                                                  # smoke
            sx, sy = hx + rnd.uniform(-12, 12), hy - 20 - rnd.uniform(0, 70)
            rr = rnd.uniform(4, 12); g.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], fill=(200, 200, 200, 60))
        c = Image.alpha_composite(c.convert("RGBA"), glow).convert("RGB"); d = ImageDraw.Draw(c)
    # side panel
    d.rounded_rectangle([900, 680, 1800, 826], 18, fill=(255, 255, 255), outline=(220, 215, 205), width=2)
    tips = ["Grain along the 300 mm side", "Cut layer CUT only", "Holes first, outlines last", "Test cuts on scrap first", "Air assist on", "Never leave it unattended"]
    for i, s in enumerate(tips):
        d.text((930 + (i % 2) * 440, 700 + (i // 2) * 40), "• " + s, font=FT[(28, False)], fill=INK)
    d.text((120, 690), "laser_2mm_medium_sheet01.dxf — ribs and aileron ribs", font=FT[(30, False)], fill=MUTED)
    pct = 100 * min(1.0, t / T)
    d.text((120, 740), "cut %3.0f %%" % pct, font=FT[(40, True)], fill=NAV)
    return c

def p_strips(seg, t):
    c = content_canvas(); d = ImageDraw.Draw(c)
    x0, y0, x1, y1 = 120, 120, 1000, 520
    n_cut = int(min(7, t / 1.6))
    w = (y1 - y0) / 12
    for k in range(12):
        off = 26 * (k < n_cut)
        col = BALSA if k % 2 else (228, 198, 140)
        d.rectangle([x0, y0 + k * w + k * (6 if k < n_cut else 0), x1 + off, y0 + (k + 1) * w + k * (6 if k < n_cut else 0)], fill=col, outline=BALSA_D)
    ky = y0 + (n_cut + (t % 1.6) / 1.6) * w + n_cut * 6
    d.rectangle([x0 - 30, ky - 6, x1 + 60, ky + 6], fill=(160, 165, 175))                     # steel rule
    kx = x0 + (x1 - x0) * ((t % 1.6) / 1.6)
    d.polygon([(kx, ky + 8), (kx + 60, ky - 30), (kx + 74, ky - 20), (kx + 14, ky + 16)], fill=(230, 230, 235), outline=(90, 90, 100))
    d.rectangle([kx + 60, ky - 70, kx + 120, ky - 26], fill=(240, 160, 40))
    rows = [("Spar caps", "3 × 6 hard balsa", "2 × 984 mm"), ("Leading edge", "6 × 17 medium", "1 × 984 mm"),
            ("TE stock", "25 × 4.6 mm", "wing 330 + ailerons 2 × 325"), ("Aileron LE", "3 × 15.5 mm", "2 × 325 mm"),
            ("Cap strips", "1.5 × 6 light", "32 × 126, 12 × 48 mm"), ("D-box sheets", "1.5 mm, 78 / 74 mm wide", "2 × 984 mm")]
    for i, (a, b, cc) in enumerate(rows):
        if t < 1 + i * 1.6:
            continue
        y = 110 + i * 92
        d.rounded_rectangle([1080, y, 1860, y + 78], 14, fill=(255, 255, 255), outline=(225, 220, 210), width=2)
        d.text((1104, y + 10), a, font=FT[(30, True)], fill=INK)
        d.text((1104, y + 44), b + " · " + cc, font=FT[(26, False)], fill=MUTED)
    d.text((120, 600), "Full list with every length: cad/cut_list.md", font=FT[(30, False)], fill=MUTED)
    return c

def bottle(d, x, y, col, label, sub):
    d.rounded_rectangle([x - 20, y + 70, x + 140, y + 300], 24, fill=col)
    d.polygon([(x + 30, y + 70), (x + 90, y + 70), (x + 70, y + 10), (x + 50, y + 10)], fill=col)
    d.rectangle([x + 55, y - 10, x + 65, y + 12], fill=(240, 240, 240))
    d.rounded_rectangle([x - 8, y + 140, x + 128, y + 230], 10, fill=(255, 255, 255))
    d.text((x + 60, y + 158), label, font=FT[(30, True)], fill=INK, anchor="ma")
    d.text((x + 60, y + 196), sub, font=FT[(22, False)], fill=MUTED, anchor="ma")

def p_glue(seg, t):
    c = content_canvas(); d = ImageDraw.Draw(c)
    tr = caption_track(seg)
    cols = [("Thin CA", "seconds", (220, 70, 60), ["ribs to spar caps", "cap strips", "CA hinges (wick)", "quick tacks"], tr[0][0], tr[1][1]),
            ("PVA", "Fevicol SH", (245, 245, 245), ["tip-rib laminate", "D-box + centre sheeting", "edge-joining sheets", "sands easily"], tr[2][0], tr[3][1]),
            ("Epoxy", "1 : 1 mix", (240, 190, 50), ["carbon to balsa caps", "PETG frames + horns", "rub plates", "thin layer only"], tr[4][0], tr[5][1])]
    for i, (name, sub, col, uses, t0, t1) in enumerate(cols):
        x = 120 + i * 600
        on = t0 <= t < t1 + 0.4
        d.rounded_rectangle([x - 30, 30, x + 520, 640], 24, fill=(255, 255, 255), outline=ORANGE if on else (225, 220, 210), width=6 if on else 2)
        bottle(d, x, 90, col if name != "PVA" else (250, 250, 250), name, sub)
        if name == "PVA":
            d.rounded_rectangle([x - 20, 160, x + 140, 390], 24, outline=(200, 200, 200), width=3)
        # joint: rib on spar
        jx, jy = x + 200, 380
        d.rectangle([jx, jy, jx + 280, jy + 26], fill=BALSA, outline=BALSA_D)       # spar / sheet
        d.rectangle([jx + 120, jy - 140, jx + 140, jy], fill=BALSA_D)                # rib
        if on:
            k = (t - t0) % 1.4 / 1.4
            if name != "Epoxy":
                dy = 120 + k * (jy - 120 - 30)
                d.ellipse([jx + 126 - 8, dy - 8, jx + 126 + 8, dy + 8], fill=col if name != "PVA" else (235, 235, 230), outline=(150, 150, 150))
                d.line([x + 60, 80, jx + 120, 110], fill=(200, 200, 200), width=2)
            else:
                cx, cy = jx + 140, 200
                for a in range(0, 360, 30):
                    r = 50 * (1 - k * 0.6)
                    ang = math.radians(a + k * 360)
                    d.ellipse([cx + r * math.cos(ang) - 10, cy + r * math.sin(ang) - 10, cx + r * math.cos(ang) + 10, cy + r * math.sin(ang) + 10],
                              fill=(240, 190, 50) if a % 60 else (250, 245, 230))
                d.text((cx, cy + 70), "resin + hardener", font=FT[(22, False)], fill=MUTED, anchor="ma")
            d.ellipse([jx + 112, jy - 10, jx + 148, jy + 10], fill=(255, 230, 200) if name != "Epoxy" else (240, 200, 90))
        for k2, u in enumerate(uses):
            d.text((x, 450 + k2 * 44), "• " + u, font=FT[(30, False)], fill=INK)
    if t >= tr[-1][0]:
        d.rounded_rectangle([120, 680, 1800, 790], 20, fill=(255, 238, 225), outline=(230, 120, 60), width=3)
        d.text((150, 712), "Safety: fresh air, glasses, keep CA off skin (debonder ready), epoxy gloves", font=FT[(34, True)], fill=(150, 60, 20))
    return c

AIRF = []
def airfoil_pts():
    if not AIRF:
        for line in open(os.path.join(DESIGN, "aero", "airfoil_coords", "sd7062.dat")):
            s = line.split()
            try:
                AIRF.append((float(s[0]), float(s[1])))
            except (ValueError, IndexError):
                pass
    return AIRF

def p_cover(seg, t):
    c = content_canvas(); d = ImageDraw.Draw(c)
    sc, ox, oy = 1500, 200, 430
    P = [(ox + x * sc, oy - z * sc) for x, z in airfoil_pts()]
    d.polygon(P, fill=(245, 235, 210), outline=BALSA_D)
    for xr in (0.2, 0.39, 0.59, 0.79):                       # ribs seen through
        d.line([ox + xr * sc, oy - 0.10 * sc, ox + xr * sc, oy + 0.03 * sc], fill=BALSA_D, width=4)
    T = seg["seg"]
    ix = ox + sc * ease(t / (0.45 * T))                       # iron sweeps first
    hx = ox + sc * ease((t - 0.5 * T) / (0.4 * T))            # heat gun second
    up = [p for p in P if p[1] <= oy]
    up = [(x, y) for x, y in P[:len(P) // 2 + 1]]
    up = sorted(up)
    film = []
    for x, y in up:
        wr = 0 if x < hx else 6 * math.sin(x / 9.0)            # wrinkles until shrunk
        film.append((x, y - 4 - wr))
    d.line(film, fill=(250, 210, 30), width=6)
    if t < 0.47 * T:
        d.polygon([(ix - 60, 150), (ix + 60, 150), (ix + 80, 210), (ix - 80, 210)], fill=(80, 80, 90))
        d.rounded_rectangle([ix - 40, 100, ix + 40, 150], 12, fill=(30, 30, 35))
        d.text((ix, 230), "iron 110–120 °C", font=FT[(28, False)], fill=MUTED, anchor="ma")
    elif t < 0.92 * T:
        d.rectangle([hx - 20, 70, hx + 20, 180], fill=(230, 120, 30))
        d.polygon([(hx - 30, 180), (hx + 30, 180), (hx + 14, 210), (hx - 14, 210)], fill=(60, 60, 60))
        for k in range(5):
            d.line([hx - 14 + 7 * k, 215, hx - 30 + 15 * k, 300], fill=(255, 150, 80), width=2)
        d.text((hx, 40), "heat gun: shrink open bays", font=FT[(28, False)], fill=MUTED, anchor="ma")
    tips = ["1. Edges and glue lines first (iron)", "2. Then shrink the open bays (heat gun)", "3. Ailerons covered separately",
            "4. Cut film off hinge slots + hatch", "Light film ≈ 50 g/m² → ≈ 29 g for this wing"]
    for i, s in enumerate(tips):
        d.text((200, 580 + i * 44), s, font=FT[(30, False)], fill=INK)
    return c

def p_checks(seg, t):
    c = content_canvas(); d = ImageDraw.Draw(c)
    rows = [("Span", "990.00 mm", "≤ 1000 mm"), ("Chord", "280.0 mm", "280 mm"), ("Depth at spar (x = 75.6)", "39.20 mm", "39.1 mm"),
            ("Overlaps between parts", "0", "0"), ("Servo clearance", "≥ 1.00 mm", "≥ 1 mm"), ("Aileron at ±20°", "no contact", "no contact"),
            ("Mass without servos", "156.6 g", "≤ 160 g")]
    d.text((120, 40), "Measured in the FreeCAD model", font=FT[(40, True)], fill=NAV)
    for i, (a, b, r) in enumerate(rows):
        if t < 0.8 + i * 1.6:
            continue
        y = 120 + i * 88
        d.rounded_rectangle([120, y, 1800, y + 74], 14, fill=(255, 255, 255), outline=(225, 220, 210), width=2)
        d.text((150, y + 18), a, font=FT[(34, False)], fill=INK)
        d.text((1150, y + 18), b, font=FT[(34, True)], fill=NAV)
        d.text((1450, y + 18), r, font=FT[(30, False)], fill=MUTED)
        d.ellipse([1720, y + 14, 1766, y + 60], fill=(60, 170, 90))
        d.line([1730, y + 38, 1742, y + 50, 1758, y + 24], fill="white", width=6)
    return c

def p_outro(seg, t):
    c = content_canvas(); d = ImageDraw.Draw(c)
    paste_fit(c, img("wing_iso_open.png"), (1000, 60, 1880, 560))
    d.text((90, 90), "All links, BOM and files", font=FT[(64, True)], fill=NAV)
    d.text((90, 200), "Webpage", font=FT[(34, True)], fill=ORANGE)
    d.text((90, 246), "jagathsrujan.github.io/water-drop-rc-wing", font=FT[(44, True)], fill=INK)
    d.text((90, 330), "GitHub", font=FT[(34, True)], fill=ORANGE)
    d.text((90, 376), "github.com/jagathsrujan/water-drop-rc-wing", font=FT[(44, True)], fill=INK)
    for i, s in enumerate(["Indian BOM with shop links + what to ask for offline", "Laser DXF · PETG STL · STEP · FreeCAD model", "Full design report and build steps"]):
        yy = 480 + i * 52
        d.line([92, yy + 20, 104, yy + 32, 124, yy + 6], fill=(60, 170, 90), width=6)
        d.text((140, yy), s, font=FT[(34, False)], fill=INK)
    d.text((90, 700), "Thank you for watching — happy building!", font=FT[(40, True)], fill=NAV)
    return c

PAINT = {"card": p_intro, "materials": lambda s, t: p_list(MATS, s, t, "What you need (quantities for one wing + spares)"),
         "tools": lambda s, t: p_list(TOOLS, s, t, "Tools and safety"), "weigh": p_weigh, "laser": p_laser, "strips": p_strips,
         "glue": p_glue, "cover": p_cover, "checks": p_checks, "outro": p_outro}

# ---------------- FreeCAD segments ----------------
def fc_frame(seg, i):
    p = os.path.join(HERE, "frames", seg["id"], "raw_%04d.png" % i)
    return Image.open(p).convert("RGB") if os.path.exists(p) else None

def overlay_step(seg, im):
    d = ImageDraw.Draw(im)
    if seg["id"] in GLUE:
        txt = GLUE[seg["id"]]
        w = d.textlength(txt, font=FT[(30, False)]) + 120
        d.rounded_rectangle([W - 40 - w, CY0 + 24, W - 40, CY0 + 90], 16, fill=(255, 255, 255), outline=ORANGE, width=3)
        d.text((W - 40 - w + 24, CY0 + 40), "GLUE", font=FT[(30, True)], fill=ORANGE)
        d.text((W - 40 - w + 110, CY0 + 40), txt, font=FT[(30, False)], fill=INK)
        d.rounded_rectangle([40, CY0 + 24, 330, CY0 + 90], 16, fill=(255, 255, 255), outline=(220, 215, 205), width=2)
        d.rectangle([62, CY0 + 44, 90, CY0 + 70], fill=(255, 115, 13))
        d.text((104, CY0 + 40), "new parts", font=FT[(30, False)], fill=INK)
    return im

# ---------------- encode ----------------
def encode(seg):
    os.makedirs(os.path.join(HERE, "clips"), exist_ok=True)
    out = os.path.join(HERE, "clips", seg["id"] + ".mp4")
    fc = seg["kind"] in ("orbit", "step", "servo")
    fps = FPSFC if fc else FPS2D
    n = int(round(seg["seg"] * fps))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(fps), "-i", "-",
           "-i", os.path.join(HERE, seg["audio"]),
           "-filter_complex", "[0:v]fps=30,format=yuv420p,fade=t=in:st=0:d=0.3,fade=t=out:st=%.2f:d=0.3[v];[1:a]adelay=300|300,apad,afade=t=out:st=%.2f:d=0.3[a]" % (seg["seg"] - 0.3, seg["seg"] - 0.3),
           "-map", "[v]", "-map", "[a]", "-t", "%.3f" % seg["seg"], "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-r", "30",
           "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-ac", "2", out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    last = None
    for i in range(n):
        t = i / fps
        if fc:
            raw = fc_frame(seg, i) or last
            last = raw
            content = raw if raw is not None else content_canvas()
            im = overlay_step(seg, frame_base(seg, t, content))
        else:
            im = frame_base(seg, t, PAINT[seg["kind"]](seg, t))
        pr.stdin.write(im.tobytes())
    pr.stdin.close(); pr.wait()
    return out

def vtt():
    def ts(x):
        h, r = divmod(x, 3600); m, s = divmod(r, 60); return "%02d:%02d:%06.3f" % (h, m, s)
    t0, L = 0.0, ["WEBVTT", ""]
    for seg in NAR:
        for a, b, s in caption_track(seg):
            L += [ts(t0 + a) + " --> " + ts(t0 + b), spoken(s), ""]
        t0 += seg["seg"]
    open(os.path.join(HERE, "wing_build.en.vtt"), "w").write("\n".join(L))

def concat():
    lst = os.path.join(HERE, "clips", "list.txt")
    open(lst, "w").write("".join("file '%s.mp4'\n" % s["id"] for s in NAR))
    out = os.path.join(HERE, "wing_build.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", out], check=True)
    return out

if __name__ == "__main__":
    ids = sys.argv[1:]
    for seg in NAR:
        if ids and seg["id"] not in ids and ids != ["concat"]:
            continue
        if ids == ["concat"]:
            break
        print("encoding", seg["id"], flush=True)
        encode(seg)
    vtt()
    if not ids or ids == ["concat"]:
        print(concat())
