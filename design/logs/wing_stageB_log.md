# Engineering notebook — Wing CAD rev A, Stage B (aileron and servo)

Script: `design/cad/scripts/build_stageB.py` (run after `build_stageA.py`); checks: `wing_check.stage_b_checks()` and `wing_check.run("B")` → `design/cad/check_report_stageB*.txt`, `mass_table_stageB.csv`.

## Calculations before the build
- Hinge line: x = 209.0 (centre of the 2 mm gap between the false spar, x 208, and the aileron apex, x 210), z = 6.98 (mid-depth at x = 209).
- V-bevel: for 20° about (209, 6.98), an LE corner at the skin (|dz| ≈ 7.7 mm) needs x ≥ 211.3 for 0.5 mm clearance → bevel from the apex at x = 210 to x = 211.5 at the skins; the strip is 1.5 mm at the skins.
- CA hinges (20 mm wide): glue area in 3 mm balsa = 2 × 3 × 20 = 120 mm² on each side → ≥ 100 N per hinge at about 1 MPa balsa shear. Air load on one aileron ≈ 0.0228 m² × 230 Pa (20 m/s) ≈ 5 N. Margin > 20 with 4 hinges. 3 mm of wood is sufficient; no hinge blocks.
- Linkage: servo arm r = 12.65 mm, horn arm (hole below the hinge) = 16.47 mm, pushrod horizontal at z = −9.49 (4 mm below the skin), 70.5 mm between holes. ±15° aileron → ±4.3 mm → ±20° servo; ±20° aileron → ±5.6 mm → ±26° servo.

## What was built (right side, mirrored)
| Part | Size / section | Position | Material |
|---|---|---|---|
| Aileron LE | OUTER ∩ x 210–213 with V-bevel, 4 hinge slots | y 112.5–437.5 | medium balsa |
| Aileron ribs | OUTER ∩ x 213–255, 2 mm, full depth | ends y 112.5–114.5, 435.5–437.5; stations 165, 220, 275, 330, 385 | medium |
| Horn rib | same, 2 mm | y 148.85–150.85 | medium |
| Aileron TE | OUTER ∩ x 255–280 | y 112.5–437.5 | medium (D-020) |
| CA hinge slots | 20 × 0.8 mm, x 200–218 (through the false spar and the aileron LE) | y = 130, 247.5, 302.5, 420 | — |
| MG90S placeholder | case 22.8 × 12.2 × 22.7, top to 28.5, tabs 32.5 × 2.5, spline Ø4.8 × 3 | case y 118–146.5 (shaft outboard), x 121.6–144.4, z −2.94…9.26; shaft x 138.5 | not in the wing mass |
| Servo arm | single arm, r = 12.65, hole Ø1.4 | plane y 147.2–149.0 | not in the wing mass |
| Servo frame | ring 1.0 mm on the lower contour, 4–5 mm wide, opening x 114–152 / y 117–158; 4 glue tabs 6 × 2.5 × 6 on the rib faces; 4 bosses Ø5 with Ø1.6 pilot holes | x 110–156, y 113–162 | PETG |
| Servo hatch | 0.8 mm on the lower contour + 2 servo lugs (4 mm, Ø1.5 pilot holes for the servo screws), arm slot 22 × 3.8 mm, 4 × Ø2.2 | x 110–156, y 113–162 | PETG |
| Horn | 1.5 mm slot-in plate, glued to the horn rib face and the LE strip, hole Ø1.5 at (209, −9.49) | y 147.35–148.85 | PETG |
| Pushrod | Ø1.2 steel, beside the arm and horn plates, Z-bend pins through both holes | y 149.6, x 138.5–209 | steel |
| Band rub plates | 0.5 mm shell on the LE (upper x 0–20, around the nose to lower x 3) and on the TE (upper x 250–279) | y ±15 *(interp. band width)* | PETG |

## Stage B checks
| Check | Result | Required |
|---|---|---|
| Aileron x, length | 210–280 (horn to 206.5), 325.00 mm | 210–280, 325 mm |
| Aileron end gaps | 1.00 / 1.00 mm | 1 mm |
| Aileron ±15° / ±20° | 0 mm³ interference; min gap 1.00 / 0.74 mm (false spar) | no contact at ±20° |
| Servo clearance (body) | 1.00 mm hatch, 1.06 mm frame, 5.04 mm cap strips, 6.5 mm rib 110 | ≥ 1 mm |
| Servo tabs | bear on the hatch lugs (mount); ≥ 23 mm from the structure | — |
| Arm at −35°, 0°, +35° | 1.00 mm to the hatch slot in each position | ≥ 1 mm |
| Overlaps > 1 mm³ | 0 (276 pairs tested, 151 valid solids) | 0 |
| Span / chord | 990.00 / 280.00 mm (280.51 with the LE rub plate outside the film) | 990 / 280 |
| Wing mass without servos | **156.3 g** | ≤ 155 g (D-013) → stop and ask |

Stage B masses (g, both sides): aileron LE 2.8, ribs 1.4, horn ribs 0.2, TE 4.3; frames 3.2, hatches 5.8, horns 0.8, pushrods 1.3, rub plates 1.2; hatch screws 1.2, CA hinges 0.8 (estimates).

## Problems and fixes
- First run: hatch lugs touched the servo case (0.0 mm) → lugs moved 1 mm off the case ends and 1 mm outboard; frame opening widened to x 114–152.
- Arm at +35° touched the hatch slot end (0.0 mm) → slot ±9 → ±11 mm.
- 12 overlaps from modelling (arm hub on the spline, straight pushrod through arm and horn, flat boss/tab seats on curved faces) → hub bore Ø4.8, pushrod with Z-bend pins beside the plates, seats at the high point + 0.05/0.2 mm. Result 0 overlaps.
- First mass 160.1 g (hatches 3.4 g, frames 2.6 g each) → D-013 item 5 applied: hatch 1.0 → 0.8 mm, ring 1.5 → 1.0 mm, tabs 10 × 8 → 6 × 6 mm, rub plates 40 × 0.6 → 30 × 0.5 mm → 156.3 g.

## Pictures
`design/cad/img/stageB_iso.png`, `stageB_servo_bay_iso.png`, `stageB_servo_bay_bottom.png`, `stageB_section_y140.png`, `stageB_section_y148.png`.
