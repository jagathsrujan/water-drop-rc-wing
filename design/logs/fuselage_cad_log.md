# Fuselage CAD rev A — engineering notebook

Plan: `design/04_fuselage_plan.md` (approved, gate 3 passed 2026-11-22). Binding interface: `design/03_reservoir_plan.md` §13 and §14. Design notebook: `design/logs/fuselage_log.md`.
Model: `design/cad_fuselage/Fuselage_revA.FCStd`. Scripts: `design/cad_fuselage/scripts/`. Frame: wing frame (origin at the wing LE on the centreline, X aft, Y right, Z up, mm). The fuselage datum is horizontal. The wing is at +3° about +Y through the origin.

## Stage F-A (2026-11-22)

### 1. Tool state and inputs
- FreeCAD 1.1.1 GUI with the FreeCAD MCP (addon 0.1.28, server 0.1.32). The version warning stays. The RPC works, but the old addon ignores the call timeout (90 s). Long runs continue in FreeCAD after the call times out. I read the result from `run_all.log`.
- The document `Reservoir_revA` stayed open. The scripts only read its shapes (`Shape.copy()`). They do not call any `res_build` function, and they do not change, recompute or save that document.
- I proved the full build and the checks in a headless `freecadcmd` process first (build 5 s, checks 24 s). Then I ran `run_all.py` in the GUI three times (build 34 s, checks about 180 s, pictures about 60 s). The third run is the final one: `run_all.log` ends with DONE.
- After the runs, the GUI shows `Reservoir_revA` with `Modified = True`. This flag is not evidence of a change: `Fuselage_revA` also showed `Modified = True` directly after its own `saveAs`. Evidence that the reservoir is unchanged: 45 objects in my first listing and 45 at the end; my scripts only read shapes and colours and never save it; the file `Reservoir_revA.FCStd` on disk is unchanged (last write 20:29, before this stage). Do not save that document without a reason.
- Inputs that I read: plan 04 §1–§9, plan 03 §13–§14, `design/cad_reservoir/README.md`, `res_params.py`, `res_build.py`, `run_all.py`, `result_stageA.json`, the reservoir check report, and `design/cad/scripts/wing_geom.py` (wing profile method).

### 2. Files
| File | Content |
|---|---|
| `scripts/fus_params.py` | All fuselage numbers. It imports `res_params` (RP) and reads `result_stageA.json`. No §13 value that exists in the reservoir model is typed again. Typed: the servo-wall limit Y 53.5 (not in `res_params`) and the old §13 saddle and stop X values, which are used only for the difference report. The servo Z levels in the checks come from the `RefRes_P14_Servo_MG90S` shape and from `ARM_Z_CENTER ± ARM_T/2` |
| `scripts/fus_build.py` | Helpers (document, groups, PCHIP, section wires, lofts), wing reference, seat line, pod build, reservoir copy, pictures |
| `scripts/build_stageA.py` | Stage F-A build (reference bodies, pod, hatch, split), save |
| `scripts/fus_check.py` | Stage F-A checks a–g → `check_report_stageA.txt` |
| `scripts/make_pictures.py` | Six pictures → `img/stageA_*.png` |
| `scripts/run_all.py` | Full rebuild, checks, pictures, removal of TMP objects, save, `run_all.log` (DONE or ERROR) |

Rebuild: in FreeCAD, `exec(open("<project>/design/cad_fuselage/scripts/run_all.py").read())`.

### 3. Items built
- Group `Ref` (reference bodies, not parts: no mass, no export):
  - 33 `RefRes_<name>` objects. These are copies of the reservoir parts: 28 closed-state parts (with `Water`) and 5 open-state parts (`*_open`, hidden). The reservoir `Ref_*` objects and `P15_Funnel` are not copied. Each object has the properties `ResState` (closed/open) and `MovingSet`.
  - Moving set for the lift-out (19): P1_Bottle, P1c_Cap, Water, P2–P9, P10_SafetyPin, P10_Flag, P11a–P11f (closed state). The saddles P12a/b, the straps P13a/b, the front stop P12c and the servo parts P14 stay in the fuselage.
  - `Ref_Wing`: SD7062 × 280. It is one B-spline through the `.dat` points, as in the wing CAD (`wing_geom.outer_curve`). It is extruded Y −495…+495 and turned +3° about +Y. TE at X 279.62, Z −14.654.
- Group `Pod` (parts):
  - `F1_PodNose` X −170…−24, `F2_PodCentre` X −24…175, `F3_PodAft` X 175…300 (print split T2-7).
  - `F4_NoseHatch` X −165…−2: the shell inside 3 mm below the top line.
  - Colours: pod light grey, hatch orange, bottle 70 % transparent, other RefRes 40 %, wing 80 %.

### 4. Build method
1. Outer mould line (OML) from 4 pieces. Each section is a rounded rectangle (half-width W, bottom Zb, top Zt, corner radii Rb and Rt):
   - Nose X −170…−35: smooth loft through 10 sections, 15 mm apart. The section values come from a monotone cubic (PCHIP) through the knots.
   - Hatch region X −35…−2: prism, W 55, Zb −117, Zt −4, Rb 6, Rt 4.
   - Open region X −2…280: ruled loft (sections at X −2, 200, then every 5 mm to 280). The top is high (Z +2) at first. Then I cut it with an XZ profile prism. The top edge of the profile is the wing lower surface (same B-spline, turned +3°) moved down by the 1.0 mm foam tape. Ahead of X 2, the profile goes from Z −4 at X −2 in a straight line to the seat at X 2. Aft of the TE, it follows the deck slope.
   - Aft deck X 280…300: ruled loft. The top goes from Z −15.65 to −16, and Rt goes from 0.3 to 6.
2. Inner solid from matching pieces:
   - Nose: offset 0.8 on all sides, concentric corners, 1 mm extension at the front (open front).
   - Hatch region: sides 0.5, floor 0.8, top 0.8.
   - Open region: top at Z +12, so the top is open between the side walls.
   - Deck: top 0.5, end wall 0.8 at X 299.2…300.
   - In the hatch, open and deck pieces, the bottom corner is concentric with the outer corner (radius Rb − 0.8). The corner is therefore 0.8 thick everywhere. A short line (0.3 mm over 1.5 mm height) goes from the corner to the 0.5 mm side wall.
3. Shell = OML − inner. Then I cut the belly opening FLOOR_HOLE_RECT (prism through all Z). Then F4 = shell ∩ hatch region (X −165…−2, Z above top line − 3). The rest is split at X −24 and X 175.
4. After each step: `isValid()`, exactly one solid, volume and extents from the mesh. `BoundBox` is loose on B-spline faces, so I report mesh extents. No face or edge is selected by index.
5. Nose loft check (between the sections, at X −167.5…−37.5): the loft follows the PCHIP values within 0.32 mm (largest at X −162.5). From X −147.5 aft, the difference is within 0.08 mm. The wall thickness from the section extents is 0.800 at all 11 stations. The minimum distance between the outer and inner section wires is 0.800 at the 4 stations X −162.5, −117.5, −72.5 and −40.

### 5. Sections used (tier 2, values in `fus_params.py`)
| X | W | Zb | Zt | Rb | Rt | First value (task) |
|---|---|---|---|---|---|---|
| −170 | 28 | −78 | −22 | 10 | 10 | same |
| −120 | 44 | −100 | −10 | 12 | 8 | Rb 14 |
| −60 | 53 | −114 | −5 | 9 | 5 | Rb 15 |
| −35 … 200 | 55 | −117 | −4 (to X −2), then the seat line | **6** | 4 (hatch), 0.3 (side-wall top edge) | Rb 15 |
| 250 | 45 | −95 | seat line | 10 | 0.3 | Rb 14 |
| 280 | 36.65 | −72.05 | −15.66 (deck) | 10 | 0.3 | — |
| 300 | 30 | −52 | −16 | 10 | 6 | same |

Between the knots: PCHIP. A knot at X −2 (equal to X −35) gives zero slope at X −35. A knot at X 190 (equal to X 200) gives zero slope at X 200.

### 6. Tier 2 decisions
| # | Decision | Alternatives | Reason and numbers |
|---|---|---|---|
| F-T2-1 | Bottom corner radius Rb 6 in the full section X −35…200 (first value 15) | Rb 15 / 10 / 9 / 8 | §13 is binding: the right side-wall inner face must be at Y ≥ 53.5 for X 50–90, over the servo height. The inner face at the servo bottom Z −111.9 (concentric 0.8 corner): Rb 15 → Y 50.18; 10 → 52.79; 9 → 53.21; 8 → 53.59; 6 → 54.12. The arm sweep (Y max 53.26) at the arm bottom face Z −111.4: Rb 15 puts the inner face at Y 50.64, so the arm would hit the corner; Rb 6 puts it at 54.18 (arm sweep to wall 0.92 mm; the maximum with any radius is 1.24, set by §13). The servo body itself clears Rb 15 (boss about 1.2 mm), so the decision rests on the §13 rule and the arm. Rb 6 also gives 2.25 mm to the pulled-out safety pin on the left side (Rb 15: overlap). |
| F-T2-2 | Nose Rb 10 / 12 / 9 / 6 and aft Rb 6 / 10 / 10 (first values 10 / 14 / 15 / 15 and 15 / 14 / 10) | keep the first values | The taper must meet the full-section Rb 6 without a step. A smaller aft radius keeps space for the tail servos (X 195–235, Y ±20…45, F-B). |
| F-T2-3 | Wing reference and seat line from one B-spline through the `.dat` points (as in the wing CAD), not a polygon | polygon (reservoir `Ref_Wing`, plan §1 table) | The real wing is built from the B-spline. Differences to the plan §1 table: X 2 −4.05 (table −3.8), X 10 −7.17 (−7.1), X 100 −13.15 (−13.1), TE −14.65 (−14.7). |
| F-T2-4 | Side-wall top = wing lower surface − 1.0 mm vertically (the profile cut uses the same curve) | normal offset | Vertical gap 1.000 everywhere. The normal gap is 0.82 at X 2 (steep LE region) and ≥ 0.97 from X 12. Both are inside 1.0 ± 0.3. |
| F-T2-5 | Top line X −2 → 2: straight line from Z −4 (hatch top) to the seat at X 2 (−5.05) | — | The task does not define this interval. The wing LE is 2.96 mm from the hatch. |
| F-T2-6 | Bottom face (floor and its corners) 0.8 over the whole length, also on the rising aft-cone bottom; aft-cone sides and deck 0.5 | aft-cone bottom 0.5 | The aft belly touches the ground first at a nose-up landing. Cost about 2.4 cm³ (3 g PLA). This departs from the literal plan T2-4 ("0.5 on the aft cone"). The parameter `T_AFT_BOTTOM` (0.8) reverses it: set 0.5 and run `run_all.py`. |
| F-T2-7 | Top skin X −35…−2 (hatch) 0.8 | 0.5 | The hatch is one part that is handled at each flight, with magnets in F-B. The inner face is then at Z −4.8: 2.2 mm above the cap top. |
| F-T2-8 | Side-wall thickness steps from 0.8 (nose) to 0.5 at X −35 (0.3 mm ledge on the inner face) | ramp over 5 mm | One section shape for all pieces aft of X −35. The ledge is inside the pod, so it has no effect on the print. |
| F-T2-9 | Bottom corner concentric (0.8 everywhere in the corner), with a 0.3 × 1.5 mm transition to the 0.5 side wall | non-concentric corner (0.8 → 0.5 taper, minimum 0.5) | The task asks for 0.8 including the bottom corner radii. |
| F-T2-10 | Outer top corner of the open-region walls R0.3 | square | No coincident edge with the inner side face (Y W − 0.5). The wall top at the inner face is at the seat Z exactly. |
| F-T2-11 | Pod front at X −170 (FIREWALL_X) is open; the firewall (3 mm ply), its slot and the closed frame come in F-B | closed 0.8 front wall | The firewall is a ply insert (plan T2-5). The nose top X −170…−165 stays with F1 as a 5 mm ring. |
| F-T2-12 | Hatch F4 = shell inside 3 mm below the top line, side edges cut horizontally on the top corners | — | The task method. The hatch lifts straight up: its width increases downward to the cut, and the front and aft cuts are vertical. |
| F-T2-13 | Nose: smooth loft. Open region and aft: ruled lofts (5 mm). Hatch region: prism | one ruled loft for everything | Smooth nose for printing and pictures. The ruled open region holds the flat belly (Z −117.000 exactly) and the vertical walls. |

### 7. Checks (full text: `design/cad_fuselage/check_report_stageA.txt`)
| Check | Result | Limit |
|---|---|---|
| a Belly outer Z, X −35…200 (353 samples) | −117.0000 everywhere; floor skin inner face −116.200 (grid to FLOOR_Z −115.5 in F-B: 0.70 mm) | = BELLY_Z PASS |
| b Outer \|Y\| max, X 0–280 | 55.000; whole pod 55.000 | ≤ 55.0 PASS |
| b Right side-wall inner face, X 50–90, Z −111.9…−80.4 (servo extents from the model, 21 levels) | min Y 54.122 (at Z −111.9) | ≥ 53.5 PASS |
| b Arm tip sweep −45…+45° (Y max 53.26) to F2 | 0.92 mm | INFO (plan §9.2 asks ≥ 2 mm; §13 allows at most 1.24) |
| c Shell inside the belly-opening prism | 0.000 mm³ | 0 PASS |
| d Overlap pod parts / hatch ↔ RefRes (closed and open) and Ref_Wing | 0 for all, except P10_Flag 2.80 mm³ and P10_Flag_open 2.80 mm³ (F2, left wall) | **FAIL** (flag through the wall by §13; the hole comes in F-B) |
| d Minimum distances | saddles 0.70 (feet on FLOOR_Z, the floor grid fills this in F-B); vent-flap knob 1.20; open flap 1.80; fill cap 2.20; pulled safety pin 2.25; straps 2.30; servo 3.50; front stop 4.20; bottle 14.5; wing 0.845 (seat, normal gap at X 2) | INFO |
| e Wing seat gap, X 2…279.5 every 10 mm, at the wall top | vertical 1.000; normal 0.820…1.000 | 1.0 ± 0.3 PASS |
| e Wing LE ↔ hatch | 2.964 mm | ≥ 1.0 PASS |
| e Hatch inner face above the cap top | 2.200 mm (inner face Z −4.800) | ≥ 2.0 PASS |
| e Hatch ↔ vent-flap knob P11f (top Z −6.0) | 1.200 mm | INFO |
| f Lift-out, full moving set | contact at dz 0: P10_Flag ↔ F2 (2.80 mm³) | **FAIL** |
| f Lift-out without P10_Flag | no contact to +120 | PASS |
| g isValid() all solids | all valid | PASS |
| g Build volume (sorted sizes) | F1 110 × 110 × 146; F2 110 × 113 × 199; F3 104.2 × 110 × 125; F4 19.5 × 109.7 × 163 | ≤ 256 PASS |
| g Skin thickness normal to sloped skin (section-plane value 0.8) | aft-cone bottom X 290 0.565, X 260 0.662; nose bottom X −165 0.708; hatch top X −160 0.776 | INFO (see section 8) |

### 8. Volumes and masses (shell only, no ribs, grid, sockets, firewall or magnets)
| Part | cm³ | PLA 1.24 | ASA Aero 0.53 | 0.65 | 0.80 |
|---|---|---|---|---|---|
| F1_PodNose | 30.63 | 38.0 g | 16.2 g | 19.9 g | 24.5 g |
| F2_PodCentre | 36.01 | 44.7 g | 19.1 g | 23.4 g | 28.8 g |
| F3_PodAft | 21.81 | 27.0 g | 11.6 g | 14.2 g | 17.4 g |
| F4_NoseHatch | 12.29 | 15.2 g | 6.5 g | 8.0 g | 9.8 g |
| Total | 100.74 | 124.9 g | 53.4 g | 65.5 g | 80.6 g |

Plan §5 (0.5/0.8 walls, 505 mm, with ribs, floor grid, hatch rim and socket block): PLA 187 g, ASA Aero 0.65 102 g. Scaled to the modelled 470 mm: 174 g and 95 g. The F-A shell is 72 % (PLA) and 69 % (ASA Aero) of these values. The difference is the inner structure of F-B. The plan estimate is not contradicted yet. The F-B mass shows the final number.

Skin thickness on sloped skin. The method of the task (inner section = W − t, Zb + t, R − t) sets the thickness in the section plane (vertical or horizontal). Where the skin slopes in X, the thickness normal to the surface is smaller (measured at Y 0, check report section g):
| Station | Section-plane value | Normal thickness |
|---|---|---|
| X 290, aft-cone bottom | 0.806 | 0.565 |
| X 260, aft-cone bottom | 0.800 | 0.662 |
| X 230, aft-cone bottom | 0.800 | 0.704 |
| X −165, nose bottom | 0.800 | 0.708 |
| X −130, nose bottom | 0.800 | 0.751 |
| X −160, hatch top | 0.800 | 0.776 |

F-T2-6 gives ground contact as its reason, so the aft-cone bottom is the important case (0.57 mm at X 290). A fix for F-B: offset each inner section value by t / cos(slope) (about +3 g PLA). I did not apply it, because the task gives the section method.

### 9. Differences between the reservoir model and §13 (the model wins)
| Item | §13 | As built (reservoir model) |
|---|---|---|
| Saddle 1 | X 8…20 | sleeve X 5.98…17.98; feet and strap pads X 1.98…21.98 |
| Saddle 2 | X 160…172 | sleeve X 157.98…169.98; pads from X 139.28 |
| Front stop | X −27.2…−24.2 | X −29.22…−26.22 |

All three follow the bottle base (−25.72 against the plan value −23.7: −2.02 mm, reservoir T2-1/T2-15). Servo case Y 38.8…51.0, Z −111.9…−80.4: the same as §13. The front stop lies in F1, 2.22 mm ahead of the split at X −24. The plan §4 table puts the slot in F2. F-B must decide (move the split aft, or put the slot in F1). I did not move the split.

### 10. Problems and fixes
1. The MCP addon (protocol 1) ignores the call timeout. The GUI run continued after the call timed out. I read the result from `run_all.log`.
2. `BoundBox` on lofted and B-spline shapes was loose (for example, F3 Z max +10.0 against the real −12.82). `optimalBoundingBox` was also wrong once (F4 Z min −27.5 against −23.46). The helper `mesh_bb()` now gives the extents from a tessellation.
3. My first property name `State` hid the built-in `DocumentObject.State`. I changed it to `ResState`.
4. In the first top view, the limit lines showed black, because the black edge lines covered the thin boxes. The temporary bodies now get `LineColor` = shape colour, and the Y ±55 lines are 1.6 mm wide.
5. Each save over an existing file makes a FreeCAD backup (`Fuselage_revA.<date-time>.FCBak`). These stay untracked.
6. The advisor review found typed servo Z levels (−111.9, −80.4, −111.4, −110.5) in `fus_check.py`. They now come from the model and `res_params`. The results did not change.

### 11. Open items for the main session (tier 1, not decided)
Process: the `cad-codesign` skill applies to this execution stage as follows: no tier 1 decision made, every tier 2 decision recorded above with alternatives and numbers, the questions below go to the main session (the subagent does not ask the user). I did not change `DECISIONS.md`, `DESIGN_BRIEF.md` or `DESIGN_LOG.md` (outside the permitted files).
1. **Safety-pin flag and lift-out (checks d, f).** `P10_Flag` (40 × 20 × 0.2, Y −62…−22 at X 44–64, Z −110.5) crosses the left wall by design. The flag hole (F-B) removes the overlap (check d), but not the lift-out block (check f): the flag is outside the pod when the bottle goes up. Options:
   - (a) Procedure: pull the safety pin with the flag before the lift-out. The sweep without the flag passes to +120.
   - (b) A vertical slot in the left wall from the flag hole (Z −110.5) up to the wall top, so the flag goes up with the bottle. This cuts the left wall over its full height at X 44–64 (plus the strap and wing seat load path there).
   My view: (a), because the pin is "remove before flight" and the lift-out is a ground task.
2. **Release-servo arm clearance.** The arm sweep is 0.92 mm from the wall (plan §9.2: ≥ 2 mm; T2-8: ≥ 3 mm for moving parts). With the §13 wall (inner face Y ≥ 53.5, 0.5 wall at Y 54.5) the maximum is 1.24 mm with any corner radius. Options:
   - (a) Accept 0.9 mm (the arm moves in a fixed plane).
   - (b) A local recess in the wall at X 55–75, Z −112…−109 (outer bulge about 1 mm beyond Y 55).
   - (c) A shorter arm or the servo 1 mm inboard (reservoir change).
3. **Hatch over the vent-flap knob.** The cap-top check passes (2.2 mm). The silicone knob P11f is only 1.2 mm under the hatch. This is information unless the main session wants 2 mm to every fill part. Options: a local 0.5 mm skin over the cap (1.5 mm), or a hatch top at Z −3.2.

### 12. Pictures (`design/cad_fuselage/img/`, 1600 × 1200, white background)
| Picture | Content |
|---|---|
| `stageA_iso.png` | Pod, hatch (orange), reservoir references and the wing (clipped to Y ±160 for the picture, transparent) |
| `stageA_iso_nowing.png` | The same without the wing: open top X −2…280, aft deck, flag (red) out of the left wall |
| `stageA_side.png` | Side view from the left with the wing section: hatch line, seat under the wing, aft taper |
| `stageA_section_Y0.png` | Half model Y ≥ 0, seen from the left: bottle, saddles, front stop, fill unit under the hatch, outlet at the belly |
| `stageA_section_X80.png` | Slab X 80…90, seen from the front (looking aft, so the right side +Y is on the left of the picture): servo beside the right wall, R6 bottom corners, floor with the belly opening, wing above |
| `stageA_top_limits.png` | Top view: red lines Y ±55, blue lines at the wing LE (X 0) and TE (X 279.6), orange mark at the servo-wall limit Y 53.5 (X 50–90) |

The pictures use temporary `TMP_` copies (clipped wing, section cuts, lines). The script deletes them, and the saved file has none (checked: 0 TMP objects; groups Pod 4, Ref 34; the 5 open-state RefRes objects are hidden).

## Stage F-B (2026-11-23)

Brief: `design/cad_fuselage/stageB_brief.md`. Built by the main session (the F-B subagent was stopped for speed). The first build ran at 10:01. The main session and the structure side session were stopped. On 2026-11-23 this session continued the work, fixed 4 model faults and 3 check faults. Checks corrected and run again at 10:33. Flap-stop lip added after D-061; final build and checks run 10:39.

### 1. Files
| File | Content |
|---|---|
| `scripts/build_stageB.py` | F-B features, fused into F1…F4; new parts F5a/F5b, F6, F7, F8, F9; placeholders (battery, ESC, tail servos, receiver) |
| `scripts/fus_check_b.py` | F-B checks → `check_report_stageB.txt` |
| `scripts/make_pictures_b.py` | 9 F-B pictures |
| `scripts/run_all.py` | now F-A build + checks + pictures, then F-B build + checks + pictures, save |
| `scripts/fus_params.py` | F-B values (section "stage F-B"); split F1/F2 at X −26.22 |

### 2. Items built (brief items 1–16)
Split at the balsa front stop F6 (X −29.22…−26.22) with 10 mm joint sleeves (F1 ahead, F2 aft, F2 into F3 at X 175); hatch blister +1 mm over the fill unit; F7 ply firewall in a 6 × 4 mm printed frame ring; battery tray at Z −80 (X −160…−36) on 6 posts, 2 strap slots; ESC under the tray; hatch ledge 1.2 × 4 mm with 4 magnet pairs; F9 Ø4 carbon band stubs in Ø10 bosses with ribs; F8 Ø5 rear dowel at X 295 in bosses; 8 mm seat lip; saddles fused into the floor with pads, strap bridges with 22 mm slots; D-059 servo pocket (1.2 mm wall) and the MG90S mount; Ø10 flag hole; F5a/F5b PETG skids 1.5 mm; tail-servo shelves at X 216.5, |Y| 28; receiver placeholder; boom socket block from X 233.5 (2 × Ø8.3 bores, 1.6 wall, bulkhead frame and bar), 2 × Ø3 pushrod exits.

### 3. Tier 2 decisions
| # | Decision | Alternatives | Reason and numbers |
|---|---|---|---|
| F-B-T2-1 | Hatch magnets: pad and boss follow the sloped hatch joint line; magnet axis normal to the joint line | flat joint face at the magnet (first build) | At X −150 the nose top line slopes 0.268 (15°). With a flat face, the F1 pad went into the hatch and the hatch boss went into F1: overlap 9.75 mm³, hatch lift-off FAIL at +0 mm. Now: no contact up to +60 mm. |
| F-B-T2-2 | Magnet position from the local outer width at the joint line, ≥ 0.6 mm wall outside the pocket, and the hatch pocket ≥ 0.5 mm under the outer surface (search inboard in 0.5 mm steps) | position from the maximum section width W (first build) | First build: at X −20 the pocket edge was at Y 55.3, outside the skin (outer Y 55.0). At X −150 the rounded top corner (Rt 9.25) cut the top of the hatch pocket (9.1 mm³ outside). Now: magnets at |Y| 24.91 (X −150) and 49.67 (X −20), 0 mm³ outside. |
| F-B-T2-3 | 6 mm wide bracket from each F1 magnet pad to the side wall | — | After F-B-T2-2 the X −150 pads were 1.3 mm from the ledge: F1 had 3 solids. Now 1 solid. |
| F-B-T2-4 | Release-servo shelves under the tabs (Z −104.4…−101.4), servo goes in from the top, M2 from above; gussets above the shelves beside the tabs | shelves at the case top (first build) | First build: the tab detection used a 4.9 mm end band, but the MG90S tabs are 4.5 mm long. The band also took the case, so the shelves were at the case top (Z −80.4), not at the tabs (Z −101.4…−98.9). Shelf bottom −104.4 is above the pocket wall top −105.3; arm 5 mm below. |
| F-B-T2-7 | Battery slide range X −125…−67 about −96 | ±30 about −92 (brief) | At −92 + 30 the aft end hits the front stop F6. The aft end stays ≥ 1 mm ahead of the stop plate. |
| F-B-T2-9 | Flap-stop lip (D-061): floor 0.8 → 1.2 mm over X 115…121, Y ±24, inside the pod | thicker (1.6) / wider | The flap tip hits the outer edge at Z −117; 1.2 mm doubles the edge bending stiffness (t³: 3.4×) for 0.14 g PLA. |
| F-B-T2-8 | Safety-pin flag: Ø10 hole plus a box slot round the flag in the left wall | Ø10 hole only (brief item 13) | The 40 × 20 flag crosses the wall (Y −62…−22); the hole alone leaves an overlap. The slot is in the flag bounding box + 1 mm. |

### 4. Checks (full text: `design/cad_fuselage/check_report_stageB.txt`, run 10:39)
| Check | Result |
|---|---|
| Validity, solids, build volume | all valid; F1–F4 1 solid each; largest 211.2 mm (F2) ≤ 256 — PASS |
| Belly Z | −117.000 — PASS |
| Width at the wing seat (above Z −105) | 55.000 ≤ 55 — PASS |
| D-059 bulge | Y max 57.5 at X 51.4…77.6, Z −115.7…−105.3 (allowed) |
| Belly opening free | 0.000 mm³ — PASS |
| Overlap with reservoir parts and wing | 0.0000 mm³ — PASS |
| Arm sweep | 3.02 mm (≥ 3) — PASS |
| Placeholders (tail servos, receiver, battery, ESC) | 0 mm³ overlap; nearest reservoir part 8.97 mm (tail servos to the bottle) — PASS |
| Lift-out +120 in 2 mm steps (pin pulled, D-058; pod parts and placeholders stay) | no contact — PASS |
| Hatch lift-off +60 with the wing on | no contact — PASS (FAIL in the first build) |
| Band paths to hatch / hatch lift path / fill cap | 9.89 / 9.89 / 32.24 mm (≥ 3) — PASS |
| Band paths to the aft deck (brief item 9) | 1.32 mm at X 280.8, Y −38.3 (crossed band; no limit given) — see §6 |
| Pushrod path tail servos → Ø3 exits | not checked (pushrods come in F-C) |
| Skid plane to the lowest valve part | 5.00 mm (≥ 3) — PASS |
| Contact faces (by design) | servo tabs on shelves 0.00; straps on bridges 0.00; bottle on saddles 0.42 (foam tape); bottle on F6 0.51 |
| Open flap travel | 1.80 mm at 150°; first contact 157° on the aft edge with the 1.2 mm lip = flap stop (D-061) — PASS |

The F-A report (`check_report_stageA.txt`) still shows d and f FAIL for the safety-pin flag. It checks the F-A shell before the F-B flag hole, and D-058 pulls the pin before the lift-out. F-B checks 3 and 5 pass.

### 5. Masses (g)
| Part | cm³ | PLA | ASA Aero 0.65 |
|---|---|---|---|
| F1_PodNose | 45.74 | 56.7 | 29.7 |
| F2_PodCentre (with saddles and the flap-stop lip) | 57.92 | 71.8 | 37.7 |
| F3_PodAft | 35.57 | 44.1 | 23.1 |
| F4_NoseHatch | 12.62 | 15.6 | 8.2 |
| F5a/F5b skids (PETG) | 5.85 | 7.4 | 7.4 |
| F6 balsa, F7 ply, F8 birch, F9 carbon, 8 magnets | — | 13.8 | 13.8 |
| **Total** | | **209.5** | **119.9** (0.53: 101.7; 0.80: 142.6) |

The saddles (8.78 g PETG in the reservoir table) are now in F2. No ribs, grid or windows yet: these come from the structure session F-S.

### 6. Open items (tier 1)
Departures from the brief or from D-059 (built; **accepted by the user, D-062**):
- **D-059 pocket Z.** Cavity Z −114.5…−106.5 against D-059 Z −113…−107 (1.5 mm wider at the bottom and 0.5 mm at the top) for 3 mm vertical arm clearance (T2-8). With the D-059 values the clearance is about 1.7 mm. Bulge Y max 57.5 at X 51.4…77.6, Z −115.7…−105.3.
- **Flat firewall.** Brief item 5 asks for a tilted plane (2° down, 2° right). Built flat (simple laser cut); a printed wedge spacer in F-D gives the thrust angles.
- **Bands on the aft deck.** The crossed bands come 1.32 mm from F3 at X 280.8 (the band-path lines in the check are estimates). Options: accept (bands lie on the deck, local rub plate), or raise the rear dowel (X 295, Z −22).
Other items:
1. ~~Open flap 1.80 mm to the belly-opening edge~~: closed by D-061 (flap stop with lip).
2. **Pushrod path not checked.** The route from the tail servos (X 216.5, |Y| 28) to the Ø3 exits passes the cap lift-out prism and the socket block; check in F-C.
3. **Structure session F-S stopped.** Baseline static FEM done; buckling sweep not finished (orphan run stopped at 10:13); D1 not run. Its ribs and windows are not in the model.

### 7. Problems and fixes
1. The first rebuild in the GUI timed out at the MCP call (addon protocol 1 ignores the timeout). The run continued; results read from `run_all.log`.
2. The pocket width check measured an empty compound common and printed 1.8e308. It now measures F2 directly with `mesh_bb`.
3. Faults fixed: F-B-T2-1 … T2-4.

### 8. Pictures (`design/cad_fuselage/img/`, 1600 × 1200)
`stageB_iso`, `stageB_iso_below`, `stageB_section_Y0`, `stageB_section_X80` (servo + pocket), `stageB_section_Xm6` (band stubs + hatch), `stageB_section_X260` (slab X 200–262: tail servos, receiver, socket block), `stageB_top`, `stageB_hatch_closeup`, `stageB_servo_pocket_closeup` (bottle hidden).

## Stage F-C (2026-11-23) — tail, and the wing rev A in the assembly

Plan 04 §3, §4 (F7–F10), §6, §9 checks 7, 9, 13. Built by the main session. The user asked during the stage to add the real wing rev A to the assembly.

### 1. Files
| File | Content |
|---|---|
| `scripts/build_stageC.py` | F10 tubes, F11 tail block, F12 stab, F13 elevator, F14 fin, F15 rudder, F16 joiner, F17 horns, F18 pushrods, F19 guide clips, servo-arm placeholders, pushrod exit slots in F3 |
| `scripts/build_wing_asm.py` | copies the 89 parts of `design/cad/Wing_revA.FCStd` as `W_*` (group Wing), +3° about Y through the origin; the wing file is opened read-only and closed unsaved |
| `scripts/fus_check_c.py` | F-C checks → `check_report_stageC.txt` (§10: real wing against every part) |
| `scripts/make_pictures_c.py` | `assembly_iso`, `assembly_iso_aft`, `stageC_*` |
| `scripts/fus_params.py` | section "stage F-C"; `PUSHROD_EXIT` emptied (F-B holes at Y ±5, Z −46 replaced) |
| `scripts/fus_build.py` | `ovl()` and `common_robust()` (see §5) |

### 2. Geometry (wing frame, mm)
- Tubes 2 × Ø8/6 carbon, Y ±16, axis Z −40, X 235.1…725.0 (489.9 long): 70.0 in the pod sockets, 45.0 in the tail-block collars.
- Tail block F11 (PETG): collars X 680–726 (wall 1.2, bore Ø8.3), top plate X 667–738 at Z −31.6…−30 with 6 lightening holes, 2 ribs and 3 cross ribs, fin socket walls 1.2 × 8 mm.
- Stab F12 (fixed): LE X 647, hinge X 739.4, Y ±245, Z 43.5…46.5 (3 mm balsa); frame 6 mm, centre rib 10 mm (fin joint), ribs at |Y| 45/90/135/180, one diagonal per bay (Warren truss). Elevator F13: X 739.9…779.0 (30 %), 2 halves, frame 4 mm, root cutback |Y| 5.5 at the hinge → 24 at the TE.
- Fin F14 (fixed): root chord 110 at Z −30, tip 85 at Z +135 (165 high), hinge X 739.4, lower part to the stab bottom and upper part from the stab top (stab continuous, D-057); rudder F15 35 %, X 739.9…778, Z −28…135.
- Elevator and rudder hinge on one line X 739.65 (gap 0.5, CA hinges). Steel U-joiner Ø1.5 at X 743.5, Z 45, |Y| ≤ 50, legs 15 mm aft; it crosses the rudder in a Ø7 LE notch.
- Horns 1.5 mm G10: elevator (left, below) attach point X 741.4, Y −25, Z 30.5; rudder (right) X 741.4, Y 12.5, Z 20.
- Pushrods Ø2 carbon, straight from the servo arms (X 222.5, |Y| 36, Z −68) to the horns, outboard of the tubes; exit slots Ø4 (±15 mm along the rod) in the F3 side walls at X 286.2 (elevator) and 289.3 (rudder); 2 guide clips per rod at X 400 and 570.

### 3. Tier 2 decisions
| # | Decision | Alternatives | Reason and numbers |
|---|---|---|---|
| F-C-T2-1 | Pushrods straight and outboard of the tubes; exits in the side walls | between the tubes through the end wall (F-B holes Y ±5, Z −46) | A rod from a servo at \|Y\| 28 to an exit between the tubes needs a bend, and a straight rod with inboard arms crosses over a tube with 0.5 mm. Outboard: 7.1 mm to the tubes, 3.44 mm to the servos (minimum). |
| F-C-T2-2 | Elevator and rudder on one hinge line; joiner through a rudder LE notch | rudder hinge aft of the elevator TE; separate elevator horns on both halves | Cruciform with one stab: the joiner crosses the rudder axis, so a Ø7 notch is sufficient (2.75 mm clear). |
| F-C-T2-3 | V-bevel 25° each side on the elevator and rudder LEs | square LEs (first build) | Square LEs turn into the fixed TEs (overlap up to 5.6 mm³). With the bevel: no contact at ±20° / ±25° and all combinations. |
| F-C-T2-4 | Built-up frames 3 mm balsa: frame 6 mm (fixed) / 4 mm (moving), ribs 3 mm, Warren diagonals in the stab and fin | sheet with holes | D-055 (c). 15.3 g for the surfaces, joiner, horns and film against the D-055 estimate 14 g. |
| F-C-T2-5 | Tail block: collars + perforated plate + ribs | solid block (11.8 cm³ = 15 g) | 8.4 cm³ = 10.7 g PETG (plan 8 g interp.). |
| F-C-T2-6 | 2 guide clips per rod at X 400 and 570 | 1 clip | Free length ≤ 180 mm: Euler load ≈ 29 N against ≈ 18 N servo stall push; 1 clip gives ≈ 13 N. |
| F-C-T2-7 | Elevator root cutback \|Y\| 5.5 → 24 | 4 → 20 (first build) | Elevator–rudder gap at rudder ±25° was 0.45 mm; now ≥ 1.12 mm. The cutback removes 0.012 dm² (0.2 % of Sh): Vh from the planform 0.500, net 0.499. |

### 4. Checks (`check_report_stageC.txt`)
| Check | Result |
|---|---|
| Validity | all valid — PASS |
| Overlaps: tail parts, pod parts, reservoir, wing, placeholders | 0.0000 mm³ — PASS |
| Pushrod clearance (key check 9, ≥ 2) | 3.44 mm (servo placeholders); tubes 7.10 — PASS |
| Surface travel (elevator ±20°, rudder ±25°, combinations) | no contact; hinge gaps 0.48; elevator–rudder ≥ 1.12 — PASS |
| Vh / Vv (key check 7) | 0.500 / 0.0364 — PASS |
| SM at CG X 80 | 16.4 / 12.0 / 7.6 % at downwash 0.45 / 0.55 / 0.65 — PASS (final CG in F-D) |
| Stab to the wake centre-line (key check 13, ≥ 15) | 15.0 mm (wing stall, downwash 0.45) — PASS (zero margin) |
| Tubes in sockets / block | 70.0 / 45.0 mm — PASS |
| Ground at a nose-up touchdown on the aft belly corner | 6°: 16.3 mm; **8°: −2.3 mm (tail block touches)** — see §6 |
| Real wing in the assembly | 0 mm³ with every part; wing seat 0.84 (F2, X 2.4) and 0.99 (F3, TE); hatch 2.02; fill cap 4.33 |
| Mass | tail 67.6 g (tubes 33.4, block 10.7, balsa 8.6, film 4.9, joiner 1.8, horns 0.6, pushrods 5.1 + ends 1.6, clips 1.6); plan 73.5 g |

### 5. Overlap method (problem found and fixed)
`F3_PodAft` (loft) has BOP faults (TooSmallEdge, C0 edges). OCC `common` returns an empty result without an error for any tool that cuts F3 between X 175 and 200; `cut` works there. A first fix (V − V(cut)) gave false overlaps on touching faces (0.29 mm³ hatch on its ledge). Final `fus_build.ovl()`: 0 for a real gap (distToShape > 0); for contact, `common`; if `common` gives 0, a point test (≤ 300 surface points of each shape strictly inside the other) flags a missed overlap as 1.0 mm³. Tested: touching hatch 0, F3 box at X 190 flag, F3 box at X 200 30 605 mm³ (exact), gaps 0. All F-A, F-B and F-C checks were run again with it: same results (the F-A d/f FAIL is the known flag case before the F-B flag hole). A second fault was in the travel check: `rh` was chosen with `is` (FreeCAD gives new objects) and compared the elevator horn with itself.

### 6. Open item (tier 1)
**Tail strike.** Pivot on the aft belly corner (X 200, Z −117): the tail block touches the ground at about 7.7° nose-up (6°: 16.3 mm clear; 8°: −2.3 mm). A flared landing at the wing stall is about 7–10° nose-up (wing incidence +3°), so the tail block can touch first. Plan T2-3 said "≥ 10 mm at 8°"; with the tube bottom at Z −44 that was 6 mm at X 680 and is −0.8 mm at the tube ends X 725.

### 7. Change after the stage: tubes Ø10/8 (D-063, user)
`TUBE_OD, TUBE_ID = 10.0, 8.0`; socket bores Ø10.3 (`SOCK_BORE = TUBE_OD + 0.3`), tail-block bores Ø10.3, collars r 6.35, guide clips follow. Full rebuild 14:55, all F-B and F-C checks PASS.
| Item | Ø8/6 | Ø10/8 |
|---|---|---|
| Tubes (2) | 33.4 g | 42.9 g |
| Tail block | 10.7 g | 11.4 g |
| Pod F3 (socket block) | 35.6 cm³ | 37.0 cm³ (+1.8 g PLA, +0.9 g ASA Aero 0.65) |
| Tail total | 67.6 g | 78.1 g |
| Pushrods to tubes | 7.10 mm | 6.10 mm |
| Cap to F3 (lift-out still free) | 5.53 mm | 4.63 mm |
| Tail block to the ground | contact from ≈ 7.7° | contact from ≈ 7.6° (8°: −3.2 mm) |

