"""Wing rev B (foam blocks) - parameters; rev A values kept where the geometry does not change (all mm). Frame: origin LE on centreline, X aft, Y right, Z up.
Chord line at Z = 0 along the full span (dihedral 0 deg, D-012)."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # .../design
CAD = os.path.join(ROOT, "cad_revB")
AIRFOIL = os.path.join(ROOT, "aero", "airfoil_coords", "sd7062.dat")

CHORD = 280.0
HALF_SPAN = 495.0          # tip outer face
SKIN_T = 1.5               # sheeting / cap strip thickness = rib inset
INNER_XMAX = 258.0         # inner (rib) outline closed at this x

# chordwise stations
X_LE = 6.0                 # LE stock 0..6
X_DBOX = 80.0              # D-box sheeting 6..80
X_SPAR = (72.6, 78.6)      # spar caps
WEB_T = 1.5
X_FS = (205.0, 208.0)      # false spar
X_TE = 255.0               # TE wedge 255..280
X_HINGE_GAP = 210.0        # aileron LE apex

# spar caps
CAP_BALSA_T = 3.0
CAP_CARBON_T = 0.5

# spanwise stations (right side; mirrored)
RIB_C = (0.0, 2.0)                         # centre rib (y, t)
RIBS = [(55.0, 2.0), (110.0, 3.0), (165.0, 2.0), (220.0, 2.0), (275.0, 2.0),
        (330.0, 2.0), (385.0, 2.0), (439.5, 2.0)]   # D-013: rib 440 in 2 mm at 439.5 (face 438.5 = aileron gap 1 mm)
TIP_RIB = (490.5, 3.0)                      # see D-013 (moved inboard so the cap fits in the span)
TIP_CAP = (492.0, 495.0)
Y_END = 492.0                               # end of continuous spanwise parts (inner face of tip cap)
Y_CSHEET = 56.0                             # centre sheeting to the outer face of rib 55
REAR_WEB_Y = 164.0                          # rear web from centre to the inner face of rib 165

# aileron
AIL_Y = (112.5, 437.5)
AIL_X = (210.0, 280.0)

# densities kg/m3 (g/cm3 * 1000)
RHO = {"xps": 30.0, "pla": 1240.0, "sheet": 90.0, "light": 100.0, "medium": 130.0, "hard": 160.0, "carbon": 1550.0, "petg": 1270.0, "steel": 7850.0}
FILM_GSM = 50.0
GLUE_G = 14.0              # rev B: rev A 8 g + 4 g foam bonds + 2 g film spray adhesive (interp.)

# lightening holes: centre x; d = min(inner depth - 2*HOLE_MARGIN, HOLE_DMAX)  (D-013 item 1, D-018)
HOLE_X = [21.0, 48.0, 98.0, 130.0, 160.0, 186.0]
HOLE_MARGIN = 4.0
HOLE_DMAX = 26.0
HOLE_SKIP = {110.0: [98.0, 130.0, 160.0], 165.0: [98.0, 130.0, 160.0]}   # servo frame zone x 106..160
WIRE_HOLE = (130.0, 8.0)          # rib 110 only (ribs 55 use the 130 lightening hole)
WIRE_EXIT = (130.0, 28.0, 10.0)   # x, |y|, d in the bottom centre sheeting
TIP_RING_W = 10.0                 # tip cap outline ring width (D-013 item 3)

# ---------------- Stage B ----------------
HINGE_X = 209.0                   # centre of the 2 mm gap (false spar 208 / aileron apex 210)
AIL_LE_T = 3.0                    # aileron LE strip x 210..213
AIL_BEVEL = 1.5                   # V-bevel: LE strip narrows to 1.5 mm at the skins
AIL_RIB_T = 2.0
AIL_RIB_Y = [165.0, 220.0, 275.0, 330.0, 385.0]          # wing rib stations
HINGE_Y = [130.0, 247.5, 302.5, 420.0]                    # CA hinge centres (20 mm wide)
HINGE_W, HINGE_SLOT_T, HINGE_HALF = 20.0, 0.8, 9.0
# servo bay (between bottom cap strips of ribs 110 and 165)
BAY_Y = (113.0, 162.0)            # hatch / frame y extent
FRAME_X = (110.0, 156.0)
FRAME_OPEN_X = (114.0, 152.0)
FRAME_OPEN_Y = (117.0, 158.0)
HATCH_T = 0.8                     # D-013 item 5 / D-020 (plan 1.2)
RING_T = 1.0
FRAME_TAB = (6.0, 6.0)            # glue tab length (x), height (z); 2.5 mm thick in y
# MG90S placeholder (standard size; replace with the vendor file)
MG90S = dict(L=22.8, W=12.2, H=22.7, H_TOP=28.5, TAB_L=32.5, TAB_T=2.5, TAB_Z=18.5, SHAFT_FROM_END=5.9,
             SPLINE_D=4.8, SPLINE_H=3.0, TAB_HOLE_PITCH=27.5)
SERVO_Y0 = 118.0                  # case bottom (inboard); shaft points +Y (outboard)
SERVO_SHAFT_X = 138.5
SERVO_GAP = 1.0                   # case to hatch
ARM_T = 1.8
ARM_BELOW_SKIN = 4.0              # pushrod hole below the outer surface
PUSHROD_D = 1.2
HORN_T = 1.5
RUB_W = 30.0                      # band rub plates y +-20 (interp.: fuselage / band width)
RUB_T = 0.5
ARM_SLOT_HALF = 11.0              # hatch slot x half-length (arm +-35 deg with >= 1 mm)
LUG_GAP = 0.3                     # lug to servo case end (slip fit; gives 1.3 mm wall at the servo screw pilot)

# ---------------- rev B (foam blocks) ----------------
YE_B = 492.0
PLATE_T = 1.5                     # light balsa face plates (D-030)
# blocks: name -> (plate inner (y0,y1), plate outer (y0,y1), fixed bay (has TE piece), kind); right side, mirrored
BLOCKS = {
    "S": ((110.0, 111.5), (164.0, 165.5), False),
    "M": ((274.0, 275.5), (329.5, 331.0), False),
    "T": ((438.5, 440.0), (490.5, 492.0), True),
}
C_FOAM = 54.5                     # centre block foam y -54.5..54.5, plates +-(54.5..56)
HALF_RIBS = [220.0, 385.0]        # D-027, 1.5 mm light, x 78.6..205
HALF_RIB_X = (78.6, 205.0)
HALF_RIB_HOLES = [98.0, 130.0, 160.0, 186.0]
WALL = 7.0                        # foam cavity wall (D-025; 45 % removed)
CAV_MINH = 4.0
X_FOAM_F = (6.0, 71.1)            # front piece (inner outline, under the D-box)
X_FOAM_A = (80.1, 205.0)          # aft piece (outer outline)
X_FOAM_TE = (208.0, 250.0)        # TE piece (fixed bays)
X_TE_B = 250.0                    # printed TE x 250..280 (D-028)
TAIL = 3.0                        # plate tail into the TE slot (x 250..253)
SLOT_CLR = 0.05                   # each side, plate slots in keys and TE
LE_JOINTS = [-302.5, -137.75, 137.75, 302.5]   # LE segment joints (block centres)
KEY = dict(x0=6.0, x1=9.0, h=4.0, L=12.0)      # LE locator keys at the plates
JOINER_L = 20.0
WIRE_HOLE_Z_B = 5.0               # plate 110 wire hole centre z: inside the servo pocket (roof z 10.76)
POCKET_X = (108.0, 158.0)         # servo pocket in block S (stage 2)
POCKET_TOP_GAP = 1.5
INFILL_B = {"LE": 0.50, "TE": 0.85}            # printed fill (2 walls + 15 %); keys/joiners 1.0
