"""Render laser DXF sheets to PNG previews (5 px/mm). Usage: python3 dxf_preview.py <out.png> <dxf>..."""
import sys
from PIL import Image, ImageDraw
import dxf_io
out, files = sys.argv[1], sys.argv[2:]
S = 4
tiles = []
for f in files:
    im = Image.new("RGB", (300 * S + 2, 100 * S + 2), "white")
    dr = ImageDraw.Draw(im)
    for e in dxf_io.read(f):
        col = {"CUT": (200, 0, 0), "SHEET": (150, 150, 150), "LABEL": (0, 120, 0)}.get(e[1], (0, 0, 0))
        if e[0] == "poly":
            pts = [(x * S, (100 - y) * S) for x, y in e[2]]
            dr.line(pts + [pts[0]], fill=col, width=1)
        elif e[0] == "circle":
            x, y, r = e[2]
            dr.ellipse([(x - r) * S, (100 - y - r) * S, (x + r) * S, (100 - y + r) * S], outline=col)
        else:
            x, y, s = e[2]
            dr.text((x * S, (100 - y) * S - 10), s, fill=col)
    tiles.append(im)
W = tiles[0].width
cols = 2
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (W + 10), rows * (tiles[0].height + 10)), (230, 230, 230))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % cols) * (W + 10), (i // cols) * (t.height + 10)))
sheet.save(out)
print(out, sheet.size)
