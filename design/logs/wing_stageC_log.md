# Engineering notebook — Wing CAD rev A, Stage C (outputs)

Full rebuild: `design/cad/scripts/run_all.py` (Stage A → Stage B → checks → exports, saves the FCStd, log in `design/cad/run_all.log`).

## Outputs
| Output | File | Check |
|---|---|---|
| FreeCAD model | `design/cad/Wing_revA.FCStd` | 89 parts, 151 solids, all valid |
| STEP (all parts, MG90S placeholder included) | `design/cad/Wing_revA.step` (14.4 MB) | written by `Import.export` |
| Laser DXF (R12, mm, layers CUT / LABEL / SHEET) | `design/cad/dxf/laser_<thickness>_<grade>_sheetNN.dxf`, 21 sheets 300 × 100 | own read-back: 208 cut loops = model profiles within 0.02 mm; no part outside the 3 mm margin; no overlap. FreeCAD `importDXF` (independent reader): sheet 2 mm #3 imports in mm, rib outline 199.0 × 36.8 = model 199.00 × 36.81. Preview `design/cad/img/dxf_preview_*.png`. $INSUNITS is not an R12 variable: check mm on import with the 300 × 100 SHEET outline |
| STL (PETG, print orientation) | `design/cad/stl/` — ServoFrame_R/L, ServoHatch_R/L, Horn_R/L, RubPlate_LE/TE | all closed solids; mesh volume = shape volume |
| Cut list | `design/cad/cut_list.md` | strip stock with developed widths (D-box top 78.0, bottom 74.3 mm) |
| Mass table | `design/cad/mass_table.md`, `mass_table.csv` (written by `run_all.py`) | 156.6 g without servos (limit 160 g, D-023); 184.0 g with 2 × MG90S |
| Pictures | `design/cad/img/wing_iso.png`, `wing_iso_open.png`, `wing_top.png`, `wing_bottom.png`, `wing_front.png`, `wing_section_y140.png` | examined |

Sheets by group: 2 mm medium 8, 3 mm medium 3, 1.5 mm medium 4 (webs), 1.5 mm light 2 (tip rib layers), 1.5 mm selected light 3 (centre sheeting), 3 mm light 1 (tip caps). Total 21 sheets = 7 sheets of 100 × 1000 mm.

## Final key checks (`design/cad/check_report_stageC.txt`, `check_report_stageB_extra.txt`)
| # | Check | Result | Required |
|---|---|---|---|
| 1 | Span | 990.00 mm | 990.0, ≤ 1000 |
| 1 | Chord | 280.01 mm (spline nose 0.006 mm ahead of x = 0); 280.51 with the LE rub plate outside the film | 280.0 |
| 1 | Dihedral | 0° | 0° |
| 2 | Depth at x = 75.6 | 39.20 mm | 39.1 (plan value 0.1 mm low) |
| 3 | Spar caps under the sheeting | gap ≤ 0.21 mm | flush |
| 4 | Aileron | x 210–280, 325.00 mm, gaps 1.00 / 1.00 mm, no contact at ±20° (0.74 mm) | as plan |
| 5 | Servo clearance | body: 1.06 mm frame, 1.34 mm hatch plate, 5.04 mm cap strips; arm ±35° 1.00 mm; lugs 0.3 mm slip fit (mount) | ≥ 1 mm |
| 6 | Valid solids / overlaps > 1 mm³ | 151 valid / 0 (276 pairs) | all / 0 |
| 7 | Mass without servos | 156.6 g | ≤ 160 g (D-023) |

## Problems and fixes
- OCC gave wrong area and volume integrals for the full airfoil face made of one closed B-spline edge (6896 instead of 6924 mm²; extruded volume 14 % low). Only the tip caps used the unclipped face. `OUTER()` now has two edges (split at the LE); area = 6924.0 mm² = shoelace value. Full rebuild done; tip cap area check now within 5 mm² (0.1 %).
- Profile area check differences for the shear webs (≤ 0.9 mm²) and false spar pieces (≈ 21 mm²) are expected: these parts taper across their thickness. The DXF has the larger face; sand the edge to the contour after gluing.
- Picture tools: zoom by the Inventor camera string (pivy not available); printed parts shown without edges (dense facet edges showed as black).
- Hatch screw changed from M2 × 6 to M2 × 4 (boss height 4 mm).

## Not verified / limits
- MG90S is a placeholder with standard dimensions; the user's vendor file is not in `design/cad/vendor/` yet.
- Balsa densities, film and glue are estimates (±5 g on film and glue, ±20 % on balsa).
- No structural FEA; spar sizing from D-004 (margin about 4 at load factor 6).
- DXF tested by read-back and preview only, not on the H2D laser software; the laser kerf (≈ 0.1–0.2 mm) is not compensated.
- Rub plate width depends on the fuselage and the band layout *(interp.)*.

## Changes after the advisor review (same day)
- Hatch lug wall at the servo-screw pilot was 0.6 mm → lug-to-case gap 1.0 → 0.3 mm (slip fit) → wall 1.3 mm. Mass 156.4 → 156.6 g. D-022 updated.
- Mass markdown, pictures (`make_pictures.py`) and display settings moved into the scripts; `run_all.py` gives all outputs in one run. Rebuild repeated: 0 overlaps, 151 valid solids, 156.6 g.
- Plan §9 "As built" added; Stage A airfoil area corrected.
