"""Reservoir rev A - ALL numbers in one place. Units: mm, g, deg. Frame: wing frame (X aft, Y right, Z up).
(interp.) = bottle estimate until the real bottle is measured: change here only, then run run_all.py.
Source: design/03_reservoir_plan.md section 2, 3, 11."""

# ---------------- frame ----------------
AXIS_Y = 0.0
AXIS_Z = -60.0            # bottle axis (along X)
X_CG = 80.0               # target water centroid X; outlet X
X_CG_TOL = 1.0
WING_UNDERSIDE_Z = -13.0  # wing underside in this frame
BOTTLE_TOP_MARGIN = 5.0   # bottle top must be >= 5 below the wing underside

# ---------------- bottle (interp.) ----------------
BOTTLE_PROFILE = [[0, 36], [6, 40], [185, 40], [228, 12.5], [235, 10.8], [255, 10.8]]  # [yu from base, outer radius]
WALL = 0.3                       # PET wall (interp.)
BASE_X_NOMINAL = -23.7           # start value; build shifts it so the water centroid = X_CG
PUNT_H, PUNT_R = 6.0, 30.0       # base dome: height, footprint radius (interp.)
NECK_BORE_D = 21.0               # interp.
NECK_OD = 25.0                   # interp. (placeholder thread, plain tube)
NECK_Y0, NECK_Y1 = 233.0, 255.0  # tube from/to (yu)
RING_D, RING_Y0, RING_Y1 = 32.0, 231.0, 233.0   # support ring
CAP_D, CAP_Y0, CAP_Y1 = 29.6, 241.0, 257.0      # original cap (interp.)
BOTTLE_MASS_G = 22.0             # interp. (weigh); includes the cap
WATER_ML = 1000.0
WATER_G = 996.0
RHO_PET = 1.38

R_CYL = 40.0                     # outer radius of the cylinder (profile)
R_IN = R_CYL - WALL              # inner wall radius = 39.7

# ---------------- holes in the bottle ----------------
OUT_HOLE_D = 17.3
OUT_X = X_CG
FILL_HOLE_D = 13.3            # fill hole in the bottle top (rev A.1, plan 12.1)
FILL_X_C = -11.0              # fill unit centre X (interp.: keep the flange on the straight cylinder)

# ---------------- P2 inner flange ----------------
FL_L, FL_W = 34.0, 18.5          # obround planform (X, Y)
FL_TOP_R = 38.5                  # top = cylinder R 38.5 (1.2 above the inner wall)
FL_RIM_H = 0.4                   # rim height above the wall
FL_RAMP_LEN = 1.5                # ramp length (horizontal)
BORE_D = 14.0
STEM_OD = 17.0
SEAT_Z = -107.0                  # seat face, stem end

# ---------------- P3 outer gasket ----------------
GK_OD, GK_ID = 30.0, 17.3
GK_R_IN, GK_R_OUT = 40.0, 41.0   # saddle: between PET outer and plate

# ---------------- P4 base plate ----------------
PL_SADDLE_R = 41.0
PL_BODY_D = 32.0
PL_HOLE_D = 17.4
POCKET_D, POCKET_DEPTH = 23.0, 3.5
LUG_X = (51.0, 61.0)
LUG_Y = ((-9.0, -4.0), (4.0, 9.0))
LUG_BOTTOM_Z = -113.5
REL_PIN_POS = (58.0, -110.5)     # (X, Z) release pin (moved -0.5 with the flap, R-C/D change 2)
SAF_PIN_POS = (54.0, -110.5)     # (X, Z) safety pin (moved -0.5 with the flap)
PIN_HOLE_D = 2.1
HINGE_X, HINGE_Z = 100.0, -111.0
KNUCKLE_D = 5.0
KNUCKLE_Y = ((-10.0, -4.0), (4.0, 10.0))
HINGE_HOLE_D = 1.6
WEB_T = 2.0                      # T2: thin web thickness of the tongues (lightening, ~3.5 g)
WEB_Y = 10.0                     # tongue half width
WEB_X = (50.0, 102.5)

# ---------------- P5 nut ----------------
NUT_OD, NUT_ID, NUT_T, NUT_GAP = 22.0, 17.0, 3.2, 0.3

# ---------------- P6 flap, P7 flap gasket ----------------
FLAP_D, FLAP_T = 34.0, 2.5
FLAP_ZTOP = -109.0               # flap top (moved -0.5: gasket now 2.0 mm), bottom = -111.5
FLAP_ZBOT = FLAP_ZTOP - FLAP_T
FLAP_SKIN = 1.2                  # solid skin under the gasket (lightening, change 1)
FLAP_RIB_W, FLAP_RIB_PITCH = 1.2, 8.0   # grid of pockets on the lower face, rib width / pitch
FLAP_RIM_W = 1.2                 # solid rim ring at the edge of the disc
FLAP_KEEP = ((51.0, 69.0, -5.5, 5.5), (91.0, 104.0, -5.5, 5.5))   # solid zones (X0, X1, Y0, Y1): hook tab, knuckle
TAB_X = (51.5, 66.0)
TAB_HALF_Y = 3.3
TAB_BOTTOM_Z = -113.0
FLAP_KNUCKLE_HALF_Y = 3.6
FGK_D, FGK_T = 32.0, 2.0         # EVA closed-cell foam 2.0 mm, 0.10 g/cm3 (interp.), top face stays at Z -107.0

# ---------------- P8 hinge pin, P9 release pin, P10 safety pin ----------------
HP_D, HP_Y = 1.5, (-10.0, 10.0)
RP_D = 2.0
RP_TIP_Y, RP_ENG_END_Y = -6.0, 15.0    # tip, end of straight part (closed)
RP_EYE_D, RP_EYE_Y0, RP_EYE_Y1 = 6.0, 15.0, 21.0
RP_RETRACT = 12.0
SP_D = 2.0
SP_TIP_Y, SP_STRAIGHT_END_Y = 9.0, -14.0
SP_RING_D, SP_RING_Y0, SP_RING_Y1 = 8.0, -14.0, -22.0
SP_REMOVE = 30.0                      # open state: safety pin pulled out
FLAG = (40.0, 20.0, 0.2)              # Y length, X width, thickness
WIRE_D = 1.0                          # wire of the eye rings
OPEN_ANGLE = 150.0   # rev A.2: 160 deg now hits the lower belly skin (first contact 157 deg); 150 = plan minimum

# ---------------- reference (pictures only) ----------------
BELLY_Z = -117.0   # D-051 lower belly: outer skin Z -117.0, 1.5 thick (floor inner Z -115.5)
BELLY_T = 1.5

# ---------------- mass ----------------
RHO = {"PETG": 1.27, "silicone": 1.15, "steel": 7.85, "tape": 1.2, "EVA": 0.10, "balsa": 0.16}
THICK_RULE = 4.0     # printed part thicker than this: x0.45 (2 walls, 15 % infill, interp.)
INFILL_FACTOR = 0.45
SPRING_G = 0.2       # kick spring, bought, not modelled
BOTTLE_PICTURE_BODY = True   # the modelled PET shell is only a picture body; the mass table uses BOTTLE_MASS_G
BUDGET_G = None                  # no fixed reservoir mass limit (D-047); was 50.0 g (R17)

# ---------------- R-C fill unit P11 (plan 12.1, replaces the vent of 11.3) ----------------
F_FL_D = 16.5                    # fill flange round, 1.2 thick (R38.5 .. R39.7 at the top wall)
F_BORE = 10.0
F_STEM_OD = 13.0
F_STEM_TOP_Z = -9.5
F_GK_OD, F_GK_ID = 18.0, FILL_HOLE_D   # rev A.2: OD 20 -> 18 (overhung the base heel)
F_NUT_D, F_NUT_TOP_Z, F_NUT_ID = 18.0, -16.5, 13.0
F_CAP_D, F_CAP_Z0, F_CAP_Z1, F_CAP_WALL, F_CAP_ID = 18.0, -16.0, -7.0, 1.5, 13.0
F_VHOLE_D, F_VHOLE_PCD, F_VHOLES = 1.5, 6.0, 6       # vent holes in the cap top wall (+ one centre hole)
F_FLUTES, F_FLUTE_R, F_FLUTE_AT = 12, 1.0, 9.3        # knurl flutes: radius, centre radius (T2)
F_SEAL_ID, F_SEAL_OD, F_SEAL_T = 10.0, 13.0, 1.0       # cap seal ring under the cap top wall
F_FLAP_D, F_FLAP_T = 8.5, 0.8                          # vent flap (umbrella)
F_FLAP_STEM_D = 1.4                                    # T2: 0.05 mm radial clearance in the Ø1.5 centre hole
F_KNOB_D, F_KNOB_T = 3.0, 1.0
FUSE_HOLE_D = 25.0               # fuselage fill hole (reference)
FUSE_TOP_Z = (-4.0, -2.5)        # fuselage top deck (interp., reference only)
FUSE_TOP_X = (-50.0, -1.0)
# P15 funnel (ground support, STL only)
FUN_TOP_D, FUN_H, FUN_WALL = 70.0, 50.0, 1.2
FUN_SPOUT_OD, FUN_SPOUT_L, FUN_RIB = 7.0, 25.0, 1.0
FUN_NECK_Z = 5.5                 # picture position: neck Z (spout tip 10 mm into the stem)
V_RULE_X_MAX = -2.0              # key check 6: above Z -13 only at X <= -2
V_RULE_Z = -13.0
V_WING_CLEAR = 3.0
WING_CHORD = 280.0
WING_INCIDENCE = 3.0
WING_HALF_SPAN = 60.0
import os as _os
WING_DAT = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))), "aero", "airfoil_coords", "sd7062.dat")

# ---------------- R-D mount and servo (plan 11.4, 11.5) ----------------
FLOOR_Z = -115.5                 # inner floor plane (D-051); floor / belly skin reference Z -117.0 .. -115.5
FLOOR_X = (-35.0, 235.0)
FLOOR_HALF_Y = 55.0
FLOOR_HOLE_RECT = (47.0, 115.0, -20.0, 20.0)    # belly opening: X 3 mm ahead of the lugs to 15 mm aft of the hinge axis, Y = flap/plate outline + 3 mm (T2 reading)
SADDLE_W = 12.0                  # in X
SADDLE_WALL = 2.0
SADDLE_GAP = 0.5                 # foam tape between bottle and saddle
SADDLE_WRAP_DEG = 120.0
S1_YU = (31.7, 43.7)             # saddle 1, from the bottle base (plan X 8..20 at base -23.7)
S2_YU = (183.7, 195.7)           # saddle 2 on the shoulder (plan X 160..172)
FOOT_T = 1.6
FOOT_HALF_Y = 40.0
FOOT_BEAM_W = 6.0
FOOT_PAD_Y = (34.0, 40.0)
STRAP_W, STRAP_T = 20.0, 1.0
STRAP1_YU = (27.7, 47.7)
STRAP2_YU = (165.0, 185.0)       # on the cylinder, just forward of the shoulder
STRAP_END_DEG = 65.0             # arc ends at this angle from the bottom
STRAP_TAIL_Y = (37.0, 38.0)
STRAP_MASS_G = 1.5               # hook-and-loop, bought (plan 6)
STOP_T, STOP_GAP = 3.0, 0.5      # balsa plate in front of the base
STOP_HOLE_D = 50.0
STOP_Y = 50.0
STOP_Z = (-111.0, -25.0)        # D-051: outline down to Z -111
SERVO_MASS_G = 13.4              # MG90S (excluded from the reservoir total)
MG90S = dict(L=22.8, W=12.2, H=22.7, H_TOP=28.5, TAB_L=32.5, TAB_T=2.5, TAB_Z=18.5, SHAFT_FROM_END=5.9,
             SPLINE_D=4.8, SPLINE_H=3.0, TAB_HOLE_PITCH=27.5)   # as in the wing scripts (placeholder)
SERVO_Y_SHAFT = 44.9             # T2-30: MG90S upright and inverted (shaft vertical, pointing down); shaft Y = W mid-line, case Y 39.8..52.0
SERVO_X_SHAFT = 64.364           # shaft X: arm tip X at +-45 deg = 58 (the pin X)
ARM_Z_CENTER = REL_PIN_POS[1]    # arm slab centred on the pin plane Z -110.5
ARM_R, ARM_T, ARM_W = 9.0, 1.8, 4.0   # T2-31: arm R 9 (was 10)
ARM_CLOSED_DEG = -45.0           # arm angle: tip = (Xs - R cos a, Ys + R sin a); a = 0 points along -X; + = toward +Y
LINK_WIRE_D = 0.8
SNAP_D, SNAP_L, SNAP_Y0 = 2.0, 12.0, 21.0
SERVO_CLEAR = 2.0
Y_LIMIT = 55.0
SERVO_Y_LIMIT = 52.0
