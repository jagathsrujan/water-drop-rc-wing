"""Crop white margins of the CAD pictures (keeps a 30 px border). Usage: python3 crop_images.py <png>..."""
import sys
from PIL import Image, ImageChops
for p in sys.argv[1:]:
    im = Image.open(p).convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    bb = ImageChops.difference(im, bg).getbbox()
    if bb:
        b = 30
        bb = (max(bb[0] - b, 0), max(bb[1] - b, 0), min(bb[2] + b, im.width), min(bb[3] + b, im.height))
        im.crop(bb).save(p)
        print(p.split("/")[-1], im.crop(bb).size)
