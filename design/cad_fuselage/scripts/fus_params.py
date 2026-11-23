"""Fuselage rev A - ALL fuselage numbers in one place. Units: mm, g, deg. Frame: wing frame (origin wing LE on the
centreline, X aft, Y right, Z up; fuselage datum horizontal; wing at +3 deg about +Y through the origin).
Source: design/04_fuselage_plan.md sections 1, 3, 4, 7, 8, 9.
Parametric link (plan section 2): every value of the binding reservoir interface (design/03_reservoir_plan.md
section 13 / 14) is read from design/cad_reservoir/scripts/res_params.py (RP) and result_stageA.json.
Do not type those values again here. (interp.) = estimate / first value."""
import os as _os
import sys as _sys
import json as _json

HERE = _os.path.dirname(_os.path.abspath(__file__))
ROOT = _os.path.dirname(HERE)                                   # design/cad_fuselage
DESIGN = _os.path.dirname(ROOT)                                 # design
RES_SCRIPTS = _os.path.join(DESIGN, "cad_reservoir", "scripts")
if RES_SCRIPTS not in _sys.path:
    _sys.path.insert(0, RES_SCRIPTS)
import res_params as RP                                         # noqa: E402  (pure numbers, no FreeCAD)

RES_FCSTD = _os.path.join(DESIGN, "cad_reservoir", "Reservoir_revA.FCStd")
RES_DOC = "Reservoir_revA"
RES_A = _json.load(open(_os.path.join(DESIGN, "cad_reservoir", "result_stageA.json")))
DOC = "Fuselage_revA"
FCSTD = _os.path.join(ROOT, "Fuselage_revA.FCStd")
IMG = _os.path.join(ROOT, "img")

# ---------------- section 13 values, read from the reservoir model (do not retype) ----------------
BOTTLE_BASE_X = RES_A["base_x"]          # -25.72 (as built; plan section 13 / 14)
BELLY_Z = RP.BELLY_Z                     # belly outer skin, Z -117.0 (D-051)
BELLY_T = RP.BELLY_T                     # reservoir reference skin 1.5 (floor inner Z -115.5 with the F-B grid)
FLOOR_Z = RP.FLOOR_Z                     # inner floor plane, Z -115.5 (saddle feet; floor grid top in F-B)
FLOOR_HOLE_RECT = RP.FLOOR_HOLE_RECT     # belly opening (X0, X1, Y0, Y1) = (47, 115, -20, 20)
FILL_X_C = RP.FILL_X_C                   # fill unit centre X -11
CAP_TOP_Z = RP.F_CAP_Z1                  # fill cap top Z -7.0 (the vent-flap knob above it is measured on its RefRes shape)
Y_LIMIT = RP.Y_LIMIT                     # outer |Y| <= 55 (fuselage width <= 110 at the wing seat)
WING_CHORD = RP.WING_CHORD               # 280
WING_INCIDENCE = RP.WING_INCIDENCE       # +3 deg (D-005)
WING_DAT = RP.WING_DAT                   # design/aero/airfoil_coords/sd7062.dat
REL_PIN_POS = RP.REL_PIN_POS             # (X, Z) release pin
SAF_PIN_POS = RP.SAF_PIN_POS             # (X, Z) safety pin / flag hole centre (left wall), (54, -110.5)
SERVO_X_SHAFT = RP.SERVO_X_SHAFT
SERVO_Y_SHAFT = RP.SERVO_Y_SHAFT
SERVO_CASE_YMAX = RP.SERVO_Y_SHAFT + RP.MG90S["W"] / 2.0          # 51.0
ARM_R, ARM_T, ARM_W, ARM_Z_CENTER = RP.ARM_R, RP.ARM_T, RP.ARM_W, RP.ARM_Z_CENTER
ARM_SWEEP_DEG = (RP.ARM_CLOSED_DEG, -RP.ARM_CLOSED_DEG)           # -45 .. +45 (as in the reservoir check)
SADDLE1_X = (BOTTLE_BASE_X + RP.S1_YU[0], BOTTLE_BASE_X + RP.S1_YU[1])    # as built 5.98 .. 17.98 (sec. 13: 8 .. 20)
SADDLE2_X = (BOTTLE_BASE_X + RP.S2_YU[0], BOTTLE_BASE_X + RP.S2_YU[1])    # as built 157.98 .. 169.98 (sec. 13: 160 .. 172)
STOP_X = (BOTTLE_BASE_X - RP.STOP_GAP - RP.STOP_T, BOTTLE_BASE_X - RP.STOP_GAP)   # as built -29.22 .. -26.22 (sec. 13: -27.2 .. -24.2)
STOP_HOLE_D = RP.STOP_HOLE_D

# section 13 value that is not in res_params (typed here, source: 03_reservoir_plan.md section 13, plan 04 section 3)
SERVO_WALL_INNER_MIN = 53.5              # right side-wall inner face >= Y 53.5 at X 50 .. 90
SERVO_WALL_X = (50.0, 90.0)
SECTION13_REF = dict(saddle1=(8.0, 20.0), saddle2=(160.0, 172.0), stop=(-27.2, -24.2))   # for the difference report only

# ---------------- stations (plan section 3) ----------------
FIREWALL_X = -170.0                      # pod front = aft face of the 3 mm ply firewall (X set by the CG check, F-D)
NOSE_END_X = -35.0                       # end of the nose taper; full section X -35 .. 200
HATCH_X = (-165.0, -2.0)                 # nose hatch F4 (D-056)
HATCH_TOP_Z = -4.0                       # hatch top X -35 .. -2 (plan section 3: fill cap -11, cap top -7, hatch top -4)
HATCH_DEPTH = 3.0                        # F4 = shell within 3 mm below the top line (F-A simple split; ledge in F-B)
OPEN_X = (-2.0, 280.0)                   # top open between the side walls (wing on the side-wall tops)
AFT_X0 = 200.0                           # start of the aft taper
POD_END_X = 300.0
SPLIT_X = (STOP_X[1], 175.0)             # print split F1 | F2 | F3; F-B: F1/F2 at the aft face of the balsa front stop (joint former), was -24
FOAM_T = 1.0                             # foam tape on the wing seat (T2-8)
DECK_END_Z = -16.0                       # aft deck at X 300 (deck X 280 -> 300 from the TE seat Z to -16)

# ---------------- cross-sections: rounded rectangles (W half-width, Zb bottom, Zt top, Rb, Rt) ----------------
# Nose X -170 .. -35 (interp.); monotone cubic (PCHIP) between the knots. Knot X -2 = the X -35 values, so the
# taper meets the constant section with zero slope.
# T2 (F-A): Rb 15 of the first values -> 6 in the full section (servo wall, section 13); nose Rb 10/12/9/6.
NOSE_KNOTS = [   # X,     W,    Zb,     Zt,   Rb,   Rt
    (-170.0, 28.0, -78.0, -22.0, 10.0, 10.0),
    (-120.0, 44.0, -100.0, -10.0, 12.0, 8.0),
    (-60.0, 53.0, -114.0, -5.0, 9.0, 5.0),
    (-35.0, 55.0, BELLY_Z, HATCH_TOP_Z, 6.0, 4.0),
    (-2.0, 55.0, BELLY_Z, HATCH_TOP_Z, 6.0, 4.0),
]
NOSE_LOFT_DX = 15.0                      # smooth loft sections every 15 mm (X -170, -155, ..., -35)
CENTRE_W = Y_LIMIT                       # 55: outer |Y| <= 55 at X 0 .. 280 (section 13)
CENTRE_RB = 6.0                          # T2 (was 15): inner face >= Y 53.5 down to the servo bottom Z -111.9
# Aft X 200 .. 300 (interp.): W, Zb, Rb; knot X 190 = full section (zero slope at X 200). Rb at X 250 14 -> 10 (T2).
AFT_KNOTS = [   # X,    W,    Zb,   Rb
    (190.0, 55.0, BELLY_Z, 6.0),
    (200.0, 55.0, BELLY_Z, 6.0),
    (250.0, 45.0, -95.0, 10.0),
    (300.0, 30.0, -52.0, 10.0),
]
AFT_LOFT_DX = 5.0                        # ruled loft sections every 5 mm in the aft taper
DECK_RT = (0.3, 6.0)                     # aft deck top corner radius X 280 -> 300 (linear)
OPEN_RT = 0.3                            # outer top corner of the open-region side walls (wall top edge)
HIGH_ZT, HIGH_RT = 2.0, 2.0              # open region: outer loft top before the seat cut
INNER_HIGH_ZT, INNER_HIGH_RT = 12.0, 2.0  # open region: inner loft top (above everything -> open top)

# ---------------- walls (T2-4) ----------------
T_SIDE = 0.5                             # side walls and aft cone sides / deck
T_FLOOR = 0.8                            # bottom face incl. the bottom corner radii (concentric corner), X <= 200
T_AFT_BOTTOM = 0.8                       # bottom face of the aft cone X > 200 (F-T2-6; set 0.5 for the literal plan T2-4 '0.5 on the aft cone')
T_NOSE = 0.8                             # everywhere in the nose X < -35
T_HATCH_TOP = 0.8                        # top skin X -35 .. -2 (hatch); T2
T_END = 0.8                              # aft end wall at X 300
TRANS_H = 1.5                            # inner transition 0.8 (corner) -> 0.5 (side) over 1.5 mm height (T2)

# ---------------- reference wing ----------------
WING_HALF_SPAN_REF = 495.0               # Ref_Wing extruded Y -495 .. +495 (simplified, no sheeting steps)

# ---------------- checks ----------------
GAP_TOL = 0.3                            # wing seat gap 1.0 +- 0.3
SEAT_DX = 10.0                           # seat samples every 10 mm, X 2 .. 280
SEAT_X = (2.0, 280.0)
LE_CLEAR_MIN = 1.0                       # wing LE <-> hatch
HATCH_CAP_MIN = 2.0                      # hatch inner face above the fill cap top
OVERLAP_TOL = 1e-3                       # mm3
LIFT_STEP, LIFT_TRAVEL = 2.0, 120.0
BUILD_VOL = 256.0
RHO = {"PLA": 1.24, "ASA Aero 0.53": 0.53, "ASA Aero 0.65": 0.65, "ASA Aero 0.80": 0.80}
PLAN_MASS = {"PLA": 187.0, "ASA Aero 0.65": 102.0}   # plan section 5, 0.5 / 0.8 walls, 505 mm, with ribs, grid, sockets
PLAN_LEN = 505.0

# moving set for the lift-out sweep (closed state); the rest of the reservoir objects stay in the fuselage
MOVING_SET = ["P1_Bottle", "P1c_Cap", "Water", "P2_InnerFlange", "P3_OuterGasket", "P4_BasePlate", "P5_Nut",
              "P6_Flap", "P7_FlapGasket", "P8_HingePin", "P9_ReleasePin", "P10_SafetyPin", "P10_Flag",
              "P11a_FillFlange", "P11b_FillGasket", "P11c_FillNut", "P11d_FillCap", "P11e_CapSeal", "P11f_VentFlap"]
RES_SKIP_PREFIX = ("Ref_", "P15_")       # not copied (reservoir references and the ground funnel)

# ---------------- colours (pictures) ----------------
COL_POD = (0.82, 0.82, 0.84)
COL_HATCH = (0.95, 0.55, 0.10)
COL_WING = (0.70, 0.78, 0.90)
TR_WING = 80
TR_BOTTLE = 70
TR_RES = 40

# ---------------- stage F-B (functional features; plan 04 section 3/4, stageB_brief.md) ----------------
SLEEVE_L, SLEEVE_T = 10.0, 0.8           # joint sleeves (F1 ring ahead of the stop plate, F2 ring behind it, F2 ring into F3)
FW_T = 3.0                               # ply firewall X -173 .. -170
FW_RING_W, FW_RING_L = 6.0, 4.0          # printed frame ring inside the pod front
MOTOR_C = (0.0, -50.0)                   # thrust line Y, Z (2 deg down / 2 deg right by a printed wedge spacer in F-D, T2)
XMOUNT = (16.0, 19.0)                    # X-mount hole circles, M3 holes D3.2
FW_COOL = [(15.0, -62.0), (-15.0, -62.0)]   # cooling holes D12 (Y, Z)
TRAY_Z, TRAY_T, TRAY_X, TRAY_HW = -80.0, 1.2, (-160.0, -36.0), 20.0   # battery tray plate (top Z -80)
BATT = (75.0, 34.0, 17.0)                # Pro-Range 3S 1000 mAh 30C, 85 g, XT60 (Robu SKU 23749, D-066) L x W x H
BATT_XC, BATT_XC_RANGE = -96.0, (-125.0, -68.5)   # centre and slide range (aft end >= 1 mm ahead of the stop plate; front end ahead of the tray)
ESC = (60.0, 25.0, 8.0)                  # Hobbywing Skywalker 40A V2, 36 g, 5 V / 5 A SBEC (D-066), under the tray
ESC_X0 = -92.0                           # ESC front end; aft end X -32 stays >= 2 mm ahead of the front stop F6 (X -29.2)
MOTOR_D, MOTOR_L = 35.0, 30.0            # DYS D2830 1000 KV can + X-mount from the firewall face (interp.: Robu gives no drawing)
COLLET = (12.0, 14.0)                    # collet prop adapter D x L ahead of the motor (interp.)
PROP_D, PROP_T, PROP_X = 254.0, 8.0, -209.0   # HQProp 10x5 thin electric, fixed (D-066): swept disc centre plane X, hub thickness
LEDGE_T, LEDGE_W = 1.2, 4.0              # hatch ledge under the hatch flanges
MAGNET_D, MAGNET_H = 6.0, 2.0
MAGNET_X = (-150.0, -20.0)
BLISTER = (-22.0, -2.0, 13.0, 1.0)       # hatch top raised 1 mm over the fill unit: X0, X1, half-width, height
STUB_X, STUB_Z, STUB_D, STUB_OUT, STUB_IN = -6.0, -24.0, 4.0, 14.0, 8.0
STUB_BOSS_D = 10.0
DOWEL_X, DOWEL_Z, DOWEL_D = 295.0, -22.0, 5.0
LIP_W, LIP_T = 8.0, 0.8                  # wing seat lip
POCKET_X, POCKET_Z = (52.6, 76.4), (-114.5, -106.5)   # D-059 cavity (Z widened 1.5 mm each way: arm 3 mm vertical clearance, T2)
POCKET_YIN, POCKET_WALL = 56.3, 1.2
FLAG_HOLE_D = 10.0
FLAP_STOP_LIP = (6.0, 24.0, 0.4)        # flap-stop lip aft of the belly opening: length aft of X 115, half-width, extra thickness on the floor (T2)
SKID_T, SKID_HW = 1.5, 7.5
SKID_X = [(-120.0, 40.0), (120.0, 220.0)]
TSERVO = (23.0, 12.2, 29.0, 32.0)        # 9 g class placeholder L (X), W (Y), H (Z), tab length
TSERVO_XC, TSERVO_YC, TSERVO_ZB = 216.5, 28.0, -101.0
RX = (25.0, 45.0, 12.0)                  # receiver placeholder (X, Y, Z), on the floor behind saddle 2
RX_X0, RX_ZB = 177.0, -115.0
TUBE_OD, TUBE_ID = 10.0, 8.0              # 2 x carbon pultruded tube (D-063, user 2026-11-23; was 8/6 in D-052)
SOCK_Y, SOCK_Z, SOCK_BORE, SOCK_WALL = 16.0, -40.0, TUBE_OD + 0.3, 1.6   # bore = tube OD + 0.3 (glue, T2-8)
SOCK_X0, SOCK_DEPTH = 233.5, 70.0        # block starts aft of the bottle-cap lift-out prism (cap end X 231.3)
PUSHROD_EXIT = []                        # F-C: exit holes are cut along the pushrod lines (side walls, outboard of the tubes); F-B (Y +-5, Z -46) dropped
COL_BALSA = (0.85, 0.72, 0.50)
COL_PLY = (0.75, 0.60, 0.40)
COL_CARBON = (0.15, 0.15, 0.15)
COL_PETG = (0.30, 0.55, 0.85)
COL_PH = (0.35, 0.35, 0.38)


# ---------------- stage F-C (tail: tubes, tail block, surfaces, horns, pushrods; plan 04 sections 3, 4, 6, 9) ----------------
TUBE_X = (SOCK_X0 + SOCK_WALL, 725.0)    # from the socket bore bottom to the tail block (length about 490)
TB_X = (667.0, 738.0)                    # tail block (PETG): top plate X range
TB_COLLAR_X = (680.0, 725.0)             # tube collars (45 mm >= 40, key check 9)
TB_COLLAR_WALL, TB_PLATE_T = 1.2, 1.6
TB_TOP_Z = -30.0                          # plate top = fin root
TB_SOCKET_H, TB_SOCKET_WALL = 8.0, 1.2    # fin socket walls on the plate
T_SURF = 3.0                             # balsa thickness of all tail frames (D-055 built-up)
HINGE_X = 739.65                         # elevator and rudder hinge line (CA hinges, gap 0.5: fixed parts end 739.4, moving parts start 739.9)
STAB_LE_X, STAB_C, STAB_HS, STAB_Z = 647.0, 132.0, 245.0, 45.0   # Sh 6.47 dm2, elevator 30 % (hinge at 70 %), stab centre plane Z +45 (D-057)
FIN_ROOT_Z, FIN_TIP_Z = TB_TOP_Z, TB_TOP_Z + 165.0
FIN_CR, FIN_CT = 110.0, 85.0             # rudder 35 %; hinge line vertical at HINGE_X
RUD_Z0 = TB_TOP_Z + 2.0                  # rudder bottom 2 mm above the tail block plate
ELEV_ROOT_Y = (5.5, 24.0)                # elevator inner edge |Y| at the hinge and at the TE (rudder +-25 deg clearance)
JOINER_D, JOINER_X, JOINER_HY, JOINER_LEG = 1.5, 743.5, 50.0, 15.0   # steel U joiner on the elevator LE strip
RUD_NOTCH_D = 7.0                        # rudder LE notch round the joiner
HORN_T, HORN_HOLE = 1.5, 1.2
ELEV_HORN_PT = (741.4, -25.0, 30.5)      # pushrod attach point (left elevator, below)
RUD_HORN_PT = (741.4, 12.5, 20.0)        # pushrod attach point (rudder, right)
TSERVO_SHAFT_X = TSERVO_XC + 6.0         # 9 g servo: output shaft near the aft end
ARM_HOLE_Y, ARM_Z = 36.0, -68.0          # servo arm 8 mm outboard; pushrod start (Z-bend on the arm)
PUSHROD_D = 2.0                          # carbon rod; steel Z-bend ends (mass only)
GUIDE_X = (400.0, 570.0)                 # printed guide clips on the tubes (free length <= 180 mm)
RHO_BALSA, RHO_PETG, RHO_CARBON, RHO_STEEL = 0.12, 1.27, 1.55, 7.85    # g/cm3
FILM_G_M2 = 30.0                         # covering film (interp.), both sides of each framed surface
