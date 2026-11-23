# Stage F-B brief — pod inner features (fuselage CAD rev A)

Written by the main fuselage session, 2026-11-23. Approved plan: `design/04_fuselage_plan.md` (gate 3). Stage F-A is done and verified.

## Read first
- `design/04_fuselage_plan.md`: §3 stations, §4 parts, §7 decisions, the paragraph "After stage F-A" above §8, §8 stage F-B, §9 key checks.
- `design/logs/fuselage_cad_log.md` (stage F-A notebook: tier 2 decisions and methods) and `design/cad_fuselage/check_report_stageA.txt`.
- The F-A scripts in `design/cad_fuselage/scripts/`: `fus_params.py`, `fus_build.py`, `build_stageA.py`, `fus_check.py`, `make_pictures.py`, `run_all.py`.
- `design/DECISIONS.md` D-052 to D-060; `design/03_reservoir_plan.md` §13/§14; `~/.claude/CLAUDE.md` section "Building in FreeCAD (execution)".
- Frame: wing frame, origin at the wing LE on the centreline, X aft, Y right, Z up, mm. Values of the reservoir model win over §13 numbers (saddle sleeves X 5.98–17.98 and 157.98–169.98, front stop X −29.22…−26.22).

## Scope — functional features only
Do NOT add structural ribs, cross bars, stringers, floor stiffening grids, lightening windows or wall-thickness changes for mass: the side session "pod-structure-opt" designs these with FEM and delivers `scripts/fus_struct.py` later. Do not create or edit `design/cad_fuselage/structure/`, `scripts/fus_struct.py` or `design/logs/fuselage_structure_log.md`.

## Changes to F-A (main-session tier 2 decisions)
1. Print split F1/F2 moves to the balsa front stop: F1 ends at X −29.22, F2 starts at X −26.22; the 3 mm balsa front stop F6_FrontStop sits between them as the joint former. F2 gets a 10 mm forward joint sleeve (0.8 mm) that passes inside F1 through a matching inset of the plate outline; the same kind of sleeve at the F2/F3 split X 175. Each printed part must still fit 256 × 256 × 256.
2. Hatch top raised 1 mm (Z −3) over X −25…−2, blended forward: every fill part (fill cap top Z −7, vent-flap knob top Z −6.0) ≥ 2 mm from the hatch inner face; wing LE ≥ 1 mm.
3. Skin thickness normal to the surface: inner offset t / cos(slope) on sloped skin (nose 0.8, aft-cone bottom 0.8, sides 0.5, all normal to the surface).

## Features to add
4. F6_FrontStop: 3 mm balsa at X −29.22…−26.22, outline = pod inner section (minus the sleeve inset), Ø50 hole on the bottle axis (Y 0, Z −60) as reservoir P12c; takes 98 N nose-in. RefRes_P12c stays a hidden reference, not in the overlap checks.
5. F7_Firewall: 3 mm ply at X −173…−170 (FIREWALL_X), in a printed frame ring (6 mm wide) at the nose front; plane tilted for 2° down and 2° right thrust; 4 × M3 holes on the 16/19 mm X-mount pattern, Ø10 centre hole, 2 cooling holes Ø12. (Motor, ESC, battery placeholders come in F-D.)
6. Battery tray rails on the nose floor X −165…−35 for a 72 × 35 × 22 battery sliding ±30 mm about centre X −92; hook-and-loop strap slots; ESC space beside or under it (45 × 25 × 10).
7. Nose hatch F4: 4 mm inner ledge on both side walls along X −165…−2; 4 magnets Ø6 × 2 (2 near X −150, 2 near X −20) in printed bosses on the ledge and matching pockets in the hatch; a front tongue or locating tab. The hatch lifts straight up with the wing ON (D-056) and must not touch the band paths (item 8).
8. Front band stubs (D-053): carbon rod Ø4, 14 mm out of each side wall at X −6, Z −24, in a printed boss inside each wall (Ø10, 8 mm deep) with gussets into the wall; no cross bar between them (it would cut the bottle; bottle top Z −20). Band paths as Ø2 lines from each stub over the wing LE to the rear dowel (one straight band each side and one crossed pair): ≥ 3 mm to the hatch, the fill cap and the hatch lift path.
9. F8 rear dowel Ø5 through the pod at X 295, Z −22, in printed bosses; check the wing TE and the aft deck.
10. Wing seat lip: 8 mm inward lip (0.8 mm) along both side-wall tops X 2…280 following the seat line; outside the bottle lift-out envelope.
11. Saddles integrated into the floor (plan T2-5): fuse the reservoir saddle shapes (RefRes_P12a_Saddle1, RefRes_P12b_Saddle2, model positions) with the floor through printed pads from the floor skin to the saddle feet (FLOOR_Z −115.5); strap slots 22 × 2.5 mm beside each saddle. Record that their mass moves from the reservoir table to the pod.
12. Release-servo wall pocket (D-059): right wall outward pocket X 52–77, Z −113…−107, inner face ≥ Y 56.3, wall 1.2 mm (outer ≈ Y 57.5), blended into the 0.5 mm wall; arm sweep ≥ 3 mm from all structure. Servo mount for the upright MG90S (shaft down; exact pose from RefRes_P14_Servo_MG90S): printed frame from the wall/floor holding the tabs with 2 × M2, ≥ 2 mm from the bottle and the arm.
13. Safety-pin flag hole Ø10 in the left wall at X 54, Z −110.5 (D-058).
14. F5 belly skids (PETG, replaceable): 1.5 mm × 15 mm on the centreline, X −120…40 and X 120…≈ 220 following the belly line; not inside the belly opening. Ground check: lowest valve part ≥ 3 mm above the skid plane.
15. Tail servo bay in F3 (T2-1): 2 servos of the 9 g class (placeholder 23 × 12.2 × 29, tabs 32) beside the bottle neck, about X 195–235, |Y| 20…45, on printed mounts; outside the bottle lift-out envelope (vertical prism over the moving set + 2 mm), inside the walls. Receiver tray about X 215 on the floor (placeholder 45 × 25 × 12).
16. Boom socket block in F3: 2 bores Ø8.3 for the Ø8/6 tubes at Y ±16, axis Z −40 nominal (tier 2: may move within Z −30…−45), ≥ 70 mm engagement (may extend up to 10 mm aft of the pod end as a collar), 1.6 mm walls, web to the shell; it must start aft of the bottle-cap lift-out envelope (cap end X 231.3, cap radius 14.8 about Z −60): the cap must lift straight up without contact. 2 pushrod exit holes Ø3 between the tubes. (Tubes come in F-C.)

## Checks (extend `fus_check.py`; write `design/cad_fuselage/check_report_stageB.txt`)
All F-A checks again, plus:
- §13 envelope (belly −117; width ≤ 110 at the wing seat X 0–280 except the D-059 pocket at Z −113…−107; servo wall; belly opening clear; flag hole position).
- Zero overlap with every reservoir part (closed and open states) and the wing; minimum distances listed; ≥ 2 mm for all features except contact faces (saddle–bottle 0.5 mm foam tape; front stop on the base rim by design: report).
- Lift-out sweep +Z to +120 in 2 mm steps with the wing, the hatch, the straps and the safety pin removed: no contact with any fuselage part.
- Hatch lift-off +Z 60 mm with the wing on: no contact; band paths ≥ 3 mm.
- Servo arm sweep ≥ 3 mm to the pocket; flap open 150° without contact; valve ≥ 3 mm above the skid plane.
- isValid for every solid; build volume per printed part; masses per part for PLA 1.24, ASA Aero 0.53/0.65/0.80, PETG 1.27, balsa 120, ply 600 kg/m³; totals.

## Pictures (`make_pictures.py`, 1600 × 1200, white, fitAll; open and look at each)
stageB_iso, stageB_iso_below, stageB_section_Y0, stageB_section_X80 (servo + pocket), stageB_section_Xm6 (band stubs + hatch), stageB_section_X260 (socket block + tail servos), stageB_top, stageB_hatch_closeup, stageB_servo_pocket_closeup.

## Rules
- Part-workbench Python; one Part::Feature per part; no face/edge indices; isValid/BoundBox/Volume after each part; removeSplitter after big fusions.
- `run_all.py` rebuilds F-A + F-B from scratch, runs checks and pictures, removes TMP_ objects, saves `Fuselage_revA.FCStd`, log ends DONE.
- Work in small steps and make progress visible on disk: write the stage F-B section of the notebook as you go, write `build_stageB.py` feature by feature, run a partial build and save early.
- Make NO tier 1 decisions (layout, interfaces, materials, anything against the plan, §13 or D-052…D-060): stop and return the options with numbers.
- Record every tier 2 decision with alternatives and numbers in `design/logs/fuselage_cad_log.md`, section "Stage F-B", ASD-STE100 Simplified Technical English style.
- Change only files in `design/cad_fuselage/` (except the structure-session files) and `design/logs/fuselage_cad_log.md`. Do not commit. No TMP objects in the saved file. Do not save `Reservoir_revA`.

## Report (final message)
Files changed; each check PASS/FAIL with numbers; masses per part (PLA and ASA Aero) and totals; every tier 2 decision with its reason; any open tier 1 question with options and numbers; picture paths.
