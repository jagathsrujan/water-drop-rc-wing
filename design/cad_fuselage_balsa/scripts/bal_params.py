"""Fuselage rev B (balsa pod), version 2: designed for balsa construction. Units mm, g. Frame: wing frame (origin wing
LE on the centreline, X aft, Y right, Z up).
Construction: flat panels only, every kink on a former; laminated cross-grain sides with small hex lightening under film;
lite-ply U-frames open at the top (bottle lift-out) as cross members; floor keels and corner longerons through the frames;
printed PETG permanent jigs: nose ring (firewall seat) and tail node (tube bores).
Rev A numbers (reservoir interface section 13, tail, electronics) come from design/cad_fuselage/scripts/fus_params.py
(FP): not typed again here. (interp.) = estimate / first value."""
import os as _os
import sys as _sys

HERE = _os.path.dirname(_os.path.abspath(__file__))
ROOT = _os.path.dirname(HERE)                                     # design/cad_fuselage_balsa
DESIGN = _os.path.dirname(ROOT)
REVA_SCRIPTS = _os.path.join(DESIGN, "cad_fuselage", "scripts")
if REVA_SCRIPTS not in _sys.path:
    _sys.path.insert(0, REVA_SCRIPTS)
import fus_params as FP                                           # noqa: E402

DOC = "Fuselage_revB_balsa"
FCSTD = _os.path.join(ROOT, "Fuselage_revB_balsa.FCStd")
REVA_DOC, REVA_FCSTD = FP.DOC, FP.FCSTD
IMG = _os.path.join(ROOT, "img")

# ---------------- outer shape: flat panels, kinks only on formers ----------------
NOSE_KINK = FP.STOP_X[0]          # -29.22: front face of the front stop (sides and floor bend here)
AFT_KINK = 236.0                  # bulkhead: sides and floor bend here (tail cone)
PLAN = [(-170.0, 28.0), (NOSE_KINK, FP.Y_LIMIT), (AFT_KINK, FP.Y_LIMIT), (305.0, 30.0)]          # outer half-width
BOTTOM = [(-170.0, -78.0), (NOSE_KINK, FP.BELLY_Z), (AFT_KINK, FP.BELLY_Z), (305.0, -62.0)]       # outer bottom line
SEAT_GAP = 1.0
WING_LOWER = [(2, -3.8), (5, -5.5), (10, -7.1), (20, -9.2), (40, -11.4), (60, -12.5), (80, -13.0), (100, -13.1),
              (130, -12.9), (160, -12.4), (200, -11.9), (240, -12.2), (260, -13.0), (280, -14.7)]
TOP = [(-170.0, -22.0), (NOSE_KINK, -5.0), (2.0, -5.0)] + [(x, z - SEAT_GAP) for x, z in WING_LOWER[1:]] + [(305.0, -16.5)]
X_FRONT, X_END = -170.0, 305.0

# ---------------- skins ----------------
T_SIDE_OUT, T_SIDE_IN = 1.5, 1.0  # sides: outer 1.5 balsa grain X + inner 1.0 grain Z (cross-laminated, 2.5 mm; D-068 trim)
GRIP_PLY = (30.0, 130.0, -70.0)   # launch-grip zone (X0, X1, Z max): inner layer in 1.0 mm birch ply instead of balsa
SERVO_ZONE_R = (44.0, 96.0)       # right side: inner layer left out -> inner face 53.5 (section 13 servo wall) at X 50 .. 90
T_FLOOR = 1.5                     # floor grain across (Y): outer -117 / inner -115.5 fixed by section 13
T_HATCH = 1.5                     # light balsa
T_DECK = 1.5
HATCH_X = (-170.0, -2.5)
DECK_X = (AFT_KINK, 302.0)

# ---------------- strips ----------------
LEDGE = 3.0                       # 3 x 3 hatch ledges
LEDGE_X = (-165.0, -2.5)
LIP_W, LIP_T, LIP_X = 6.0, 3.0, (0.0, AFT_KINK)        # wing-seat capstrip (top longeron)
LONGERON = 6.0                                          # 6 x 6 triangle, floor-side corners
LONGERON_SEGS = {+1: [(NOSE_KINK + 1.0, 44.0), (96.0, AFT_KINK - 1.0)],    # right: none at the servo zone (arm sweep)
                 -1: [(NOSE_KINK + 1.0, 40.0), (70.0, AFT_KINK - 1.0)]}    # left: none round the safety-pin flag hole
KEEL_Y, KEEL_W, KEEL_H = 24.0, 5.0, 3.0                 # 2 floor keels 5 x 3 balsa grain X at |Y| 24 .. 29 (release pin
KEEL_X = (FP.STOP_X[1], AFT_KINK)                       # and quick-snap at Z -111.5 pass 1 mm above)

# ---------------- formers (3 mm lite-ply unless noted) ----------------
FRAME_T = 3.0
FRAMES = [("BS_FrameN1", -130.0, "nose"), ("BS_FrameN2", -100.0, "nose"),
          ("BS_FrameB1", 38.0, "U"), ("BS_FrameB2", 105.0, "split"),
          ("BS_FrameB4", FP.SADDLE2_X[1] + 0.02, "U")]          # B3 (X 135) dropped for mass (v2 iteration 2)
U_R, U_ZC = 43.0, -60.0           # bay frames: inner edge 3 mm off the bottle (R 40, axis Z -60); open above the axis
FRAME_BAND_R = 56.0               # bay frames: lower corners cut outside a 13 mm band round the bottle ...
FRAME_STRIP = 6.0                 # ... keeping a 6 mm floor strip and 6 mm side strip (glue lines)
STOP_ANNULUS = (25.0, 42.0)       # front stop: bearing ring round the D50 hole (bottle base contact r <= 40)
STOP_RIM, STOP_SPOKE = 6.0, 10.0  # rim (glue line) and spoke width (top / bottom spokes join the ring to the rim)
SPLIT_HW = 21.0                   # frame B2: no material at |Y| < 21 (belly opening, open flap)
NOSE_HW = 22.0                    # nose frames: open above the tray bottom at |Y| < 22 (battery, ESC)
BULKHEAD_RING = 5.0               # bulkhead at AFT_KINK: full ring + bar, tubes glued through
ROD_CLEAR_R = 3.5                 # pushrod clearance in formers and the node (rod r 1)

# ---------------- printed permanent jigs (PETG) ----------------
NOSE_RING_X = (-178.0, -165.0)    # collar ahead of the panels (to -170) + glue sleeve inside the panels
JIG_T = 1.2
FIREWALL_X = (-173.0, -170.0)     # 3 mm birch ply plate inside the collar
# tail-end jig: a removable printed fixture holds the end former square to the tubes during the glue-up (not in the model)
END_X = (302.0, 305.0)            # 3 mm lite-ply end former (D-068 trim: replaces the PETG tail node), tubes glued through
TUBE_RING_OD, TUBE_RING_T = 22.0, 3.0   # birch-ply rings round each tube hole: bulkhead aft face, end former front face
SADDLE_LAYER = 3.0                # saddles: laser-cut 3 mm lite-ply layers along X (P12a/b outline), glued face to face

# ---------------- other parts ----------------
TRAY_X, TRAY_T, TRAY_HW = (-150.0, NOSE_KINK - 0.03), 1.5, 20.0
STUB_DOUBLER = (-16.0, 4.0, -34.0, -14.0, 3.0)
FLAP_STOP_PLY = (115.0, 125.0, 24.0, 1.5)
SKIDS = [(-100.0, 40.0), (120.0, 230.0)]
SKID_T, SKID_HW = FP.SKID_T, FP.SKID_HW
RX_X0 = 174.0
BATT_XC_RANGE = (-120.0, -68.5)

# ---------------- hex lightening in the side laminate (through both layers, film both faces) ----------------
HEX_AF, HEX_WEB = 8.0, 2.5        # across flats, web
HEX_MARGIN = 8.0                  # solid band at the floor (6 mm longeron) and the top (3 mm capstrip / ledges)
HEX_FRAME_CLEAR = 5.0             # solid band each side of a former glue line
HEX_X = (-163.0, 278.0)
HEX_SOLID = [  # (x0, x1, z0, z1, side) side: +1 right, -1 left, 0 both  -> keep solid
    (30.0, 130.0, -200.0, -70.0, 0),       # launch-grip zone (D-054), lower half
    (SERVO_ZONE_R[0] - 4, SERVO_ZONE_R[1] + 4, -200.0, 50.0, +1),   # release servo / pocket (single layer there)
    (40.0, 70.0, -200.0, -95.0, -1),       # safety-pin flag hole
    (-22.0, 10.0, -45.0, 50.0, 0),         # band stubs + doublers
]

# ---------------- densities (g/cm3) and covering (interp.) ----------------
RHO = dict(balsa_med=0.14, balsa_light=0.10, ply=0.65, liteply=0.45, petg=1.27, carbon=1.55, birch=0.70, steel=7.85)
FILM_G_M2 = 30.0                  # film on the outer skin; also on the inner face over the hex holes
GLUE_FRAC = 0.10                 # glue (laminating the sides too) + CA sealing, fraction of the wood mass
MAGNETS_G = 8 * 0.42

LIFT_TRAVEL, LIFT_STEP = 120.0, 4.0

# ---------------- self-locating laser-cut joints (stay in flight) ----------------
TAB_W = 8.0                       # tab width; tab length = former thickness; tabs pass through the floor / side laminate
SIDE_TAB_ZC = {"nose": -55.0, "U": -62.0, "split": -62.0, "stop": -62.0, "bulkhead": -62.0, "end": -40.0}
FLOOR_TAB_Y = {"nose": 14.0, "U": 36.0, "split": 36.0, "stop": 36.0, "bulkhead": 36.0, "end": 10.0}
# saddles: no pins (the cradle arc and base are 2 mm thick); the layers are glued on the cling-wrapped bottle

# ---------------- removable printed assembly jigs (PLA, bench only, not in the mass table) ----------------
BOARD_Z = FP.BELLY_Z              # flat building board = underside of the bay floor
PRINT_BED = 256.0                 # Bambu P1S build volume (mm)
JIG_NOSE_WEDGE_X = (X_FRONT, NOSE_KINK)            # J1a: under the sloped nose floor
JIG_TAIL_WEDGE_X = (AFT_KINK, X_END)               # J1b: under the tail-cone floor
JIG_SQUARE_X = [(8.0, 28.0), (140.0, 160.0)]       # J2: 90 deg side squares (clear of the stubs and the servo pocket bulge)
JIG_SQUARE_OUT, JIG_SQUARE_TOP = 30.0, -77.0
JIG_NOSE_X, JIG_NOSE_OUT, JIG_NOSE_TOP = (-165.0, -35.0), 15.0, -45.0   # J3: nose taper blocks against the outer nose sides
JIG_TAIL_BLOCKS = [(X_END, X_END + 25.0), (600.0, 620.0)]              # J4: tube cradles; the first block's front face squares the end former
JIG_TAIL_HW, JIG_TAIL_TOP = 30.0, -30.0
JIG_SEAT_X = [(0.0, 140.0), (140.0, 280.0)]       # J5: wing-seat gauges (wing lower surface + 1 mm foam), 2 pieces
JIG_SEAT_H, JIG_SEAT_RAIL = 12.0, (48.0, 58.0)    # gauge height above the seat line; rail |Y| range over the side tops
RHO_PLA, JIG_INFILL = 1.24, 0.30                   # jig filament estimate
