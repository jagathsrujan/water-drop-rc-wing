"""Final pictures (FreeCAD GUI): iso, iso without the top skins, top, bottom, front, sections at y = 140 and 148.1, servo bay.
Then crop the white margins (crop_images.py logic inline, PIL from FreeCAD's python if present; else run crop_images.py)."""
import sys, os, importlib
SCRIPTS = globals().get("WING_SCRIPTS") or os.environ.get("WING_SCRIPTS") or os.path.join(os.path.expanduser("~"), "Documents", "iit madras boeing v2", "design", "cad_revB", "scripts")
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import wing_build as B
importlib.reload(B)
import Part
from FreeCAD import Vector as V
IMG = os.path.join(os.path.dirname(SCRIPTS), "img") + "/"
os.makedirs(IMG, exist_ok=True)
openTop = ["DBox_Top", "CSheet_Top_Fwd_R", "CSheet_Top_Aft_R", "CSheet_Top_Fwd_L", "CSheet_Top_Aft_L"]
B.snap_all(IMG + "wing_iso.png", "iso", 3000, 1800, zoom=0.62)
B.snap_all(IMG + "wing_iso_open.png", "iso", 3000, 1800, hide=openTop, zoom=0.62)
B.snap_all(IMG + "wing_top.png", "top", 3200, 1000, zoom=0.42)
B.snap_all(IMG + "wing_bottom.png", "bottom", 3200, 1000, zoom=0.42)
B.snap_all(IMG + "wing_front.png", "front", 3200, 400, zoom=0.125)
B.snap_window(IMG + "wing_section_y140.png", "viewFront", Part.makeBox(300, 80, 80, V(-10, 140, -40)), w=3200, h=900, zoom=0.33)
B.snap_window(IMG + "wing_section_y148.png", "viewFront", Part.makeBox(300, 80, 80, V(-10, 148.1, -40)), w=3200, h=900, zoom=0.33)
B.snap_window(IMG + "wing_servo_bay_iso.png", "iso", Part.makeBox(300, 110, 80, V(60, 95, -40)), w=2400, h=1600, skip=openTop)
PICS = ["wing_iso", "wing_iso_open", "wing_top", "wing_bottom", "wing_front", "wing_section_y140", "wing_section_y148", "wing_servo_bay_iso"]
print("pictures:", PICS, "(crop with: python3 scripts/crop_images.py img/wing_*.png)")
