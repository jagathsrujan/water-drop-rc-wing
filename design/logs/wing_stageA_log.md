# Engineering notebook — Wing CAD rev A, Stage A (primary structure)

Session: Opus, 2026-11-21. Plan: `design/02_wing_plan.md` (the task calls it approved; the file still says "waiting for gate 3" — gate 3 taken as passed by the task brief).
Scripts: `design/cad/scripts/` — `wing_params.py` (all values), `wing_geom.py` (2D sections), `wing_build.py` (document helpers), `build_stageA.py`, `wing_check.py`, `crop_images.py`.
Method: every part is a 2D section in the XZ plane (OUTER = SD7062 × 280; INNER = OUTER offset 1.5 mm along the normal, closed at x = 258; SKIN = OUTER − INNER), clipped to its x range, minus notches and holes, then extruded along Y. Neighbour parts share exact faces.

## Checks before the build
| Item | Measured | Plan | Note |
|---|---|---|---|
| Depth at x = 75.6 | 39.20 mm | 39.1 mm | B-spline through the .dat points; not adjusted |
| Depth at x = 210 (hinge) | 15.46 mm | 15.5 mm | |
| Airfoil area | 6896 mm² — **corrected in Stage C: 6924 mm²** (OCC integral error on a one-edge closed spline; see `wing_stageC_log.md`) | — | perimeter 576.8 mm |
| INNER valid | yes, area 6084 mm² | — | inner depth at x = 255: 1.48 mm, at x = 258: 0.83 mm |

## Mass projection before the build (tier 1 stop)
Plan structure, from the section areas: 172 g without servos (limit 145 g). Main items: film 29, ribs 31, D-box 23, printed + pushrods 16, LE 10.5, carbon 9, aileron 9, glue 8 g. Stopped and asked: user chose the reduction set (D-013), new limit 155 g. Tip layout, false spar crossing, horn support: user accepted the recommendations (D-014, D-015, D-016).

## What was built (right side, mirrored; continuous parts tip to tip y = ±492)
| Part | Section / size | Position | Grade (kg/m³) |
|---|---|---|---|
| LE | OUTER ∩ x 0–6 | y ±492 | medium 130 (D-013) |
| D-box sheeting top / bottom | SKIN ∩ x 6–80 | y ±492 | selected light 90 (D-013) |
| Centre sheeting | SKIN ∩ x 80–205 and 208–255, top and bottom | y 0–56 each side (8 pieces) | selected light 90 |
| Spar caps | carbon 0.5 × 6 (outer), hard balsa 3 × 6 | x 72.6–78.6; carbon faces z = 28.579 / −7.391 | carbon 1550, hard 160 |
| Shear web front | INNER ∩ x 71.1–72.6, pieces between ribs | full span | medium 130 |
| Shear web rear | INNER ∩ x 78.6–80.1 | |y| ≤ 164 | medium 130 |
| False spar | OUTER ∩ x 205–208 (full depth, D-015) | y ±492 | medium 130 |
| Centre rib | INNER ∩ x 6–205 + aft piece 208–255, 2 mm | y = 0 | medium |
| Ribs 2 mm | same | y ±55, ±165, ±220, ±275, ±330, ±385, ±439.5 | medium |
| Ribs 3 mm | same | y ±110 | medium |
| Aft rib pieces (x 208–255) | fixed bays | y 0, ±55, ±110, ±439.5, tip | medium (tip: light) |
| Tip rib | 3 mm (2 × 1.5 cross-grain), no holes | y ±489 to ±492 | light 100 |
| Tip cap | OUTER − 10 mm inset (ring), 3 mm | y ±492 to ±495 | light 100 |
| Cap strips | SKIN ∩ x 80–205 (and 208–255 at fixed bays), 6 mm wide | ribs 110…439.5, tip | light 100 |
| TE wedges | OUTER ∩ x 255–280 | y −111.5…111.5; ±438.5…±492 | hard 160 |

Rib holes (D-018): centres x = 21, 48, 98, 130, 160, 186; d = inner depth − 8 mm, max 26 mm → 17.2, 26.0, 26.0, 22.9, 16.8, 10.6 mm. Ribs ±110 and ±165: only x = 21, 48, 186 (servo frame zone). Rib ±110: wire hole Ø8 at x = 130. Wire exit Ø10 in the bottom centre sheeting at x = 130, y = ±28. Hole area ≈ 33 % of the rib area.

## Stage A checks (from `design/cad/check_report_stageA.txt`)
| Check | Result | Required |
|---|---|---|
| Span (Y extent) | 990.00 mm | 990.0, ≤ 1000 |
| Chord (X extent) | 280.00 mm | 280.0 |
| Dihedral | 0° (chord line z = 0, mirror-symmetric) | 0° |
| Depth at x = 75.6 | 39.20 mm | 39.1 (plan value is 0.1 mm low) |
| Spar caps under the sheeting | max gap carbon-to-sheeting 0.21 mm top, 0.20 mm bottom; cap depth outer-to-outer 35.97 mm | flush |
| Valid solids | 117 of 117 | all |
| Overlaps > 1 mm³ | 0 (242 neighbour pairs tested) | 0 |
| Stage A mass (with film 29.2 g and glue 8 g) | 133.3 g | — |
| Projected wing (+ aileron ≈ 8, printed ≈ 9, pushrods/screws ≈ 3.6) | ≈ 154 g | ≤ 155 g (D-013) |

## Problems and fixes
- `makeOffset2D` not used for INNER (sharp TE); numeric normal offset instead (advisor note). For the 10 mm tip ring, the numeric inset was invalid near the TE; `makeOffset2D(-10)` gave a valid face (area 2275 mm²) and is used.
- First gap between the holes at x = 22 and 47 was 3.3 mm; moved to x = 21 and 48 → 5.5 mm.
- Old addon (0.1.28) returns a timeout after 90 s but the job continues; the check script writes its report to a file, which is read afterwards.
- Picture tools: view animation off, orthographic camera; close-ups made from temporary cut copies, deleted after the picture.

## Pictures
`design/cad/img/stageA_iso.png`, `stageA_iso_open.png` (top skins hidden), `stageA_top.png`, `stageA_front.png`, `stageA_root_closeup.png`, `stageA_tip_closeup.png`, `stageA_tip_outboard.png`.
