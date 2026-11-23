# Reservoir rev A.1 (water reservoir, release valve, fill unit with vent, mount, servo link)

FreeCAD model of the horizontal 1 L bottle reservoir of the Boeing NAC 2026 aircraft. Frame: wing frame (origin at the wing LE on the centreline, X aft, Y right, Z up, fuselage datum horizontal). Plan: `design/03_reservoir_plan.md`. Notebook: `design/logs/reservoir_cad_log.md`. Bottle numbers are estimates until the real bottle is measured.

## Rebuild
1. Open FreeCAD with the FreeCAD MCP add-on running (do not close other documents).
2. In FreeCAD (or through the MCP `execute_code` tool, timeout 600 s or more) run:
   `exec(open("<project>/design/cad_reservoir/scripts/run_all.py").read())`
3. It rebuilds stages R-A to R-D in the document `Reservoir_revA`, runs all checks, makes the pictures, writes STEP and STL, and saves the FCStd. The log is `run_all.log` (last line `DONE`, or `ERROR` with the traceback).

## Where the numbers are
- **Bottle numbers** (profile, wall, punt, neck, cap, bottle mass): `scripts/res_params.py`, section "bottle (interp.)". When the real bottle is measured, change only this block and run `run_all.py`. The bottle base X is found by the build so that the water centroid is at X = 80 (`result_stageA.json`).
- All other part dimensions (outlet unit, vent, saddles, servo) are in the same file.

## Files
| File | Content |
|---|---|
| `Reservoir_revA.FCStd` | the model (one `Part::Feature` per part; groups A_Bottle, B_Outlet, B_Open (hidden), C_Fill, D_Mount, D_Servo, Ref (hidden)) |
| `Reservoir_revA.step` | assembly, closed state (no water, no reference bodies) |
| `stl/*.stl` | printed parts in the print orientation (P15 funnel is a ground-support part: STL only, not in the STEP, mass table or overlap check); `stl/print_orientation.txt` gives the orientation of each |
| `check_report.txt` | all key checks 1 to 10 with the numbers |
| `mass_table.md`, `mass_table.csv` | mass of each part and the total (without the MG90S; no fixed limit, D-047) |
| `check_report_stageAB.txt`, `mass_table_stageAB.csv` | the accepted stage R-A / R-B reports (older, flap before the lightening) |
| `img/` | pictures (see below) |
| `run_all.log` | log of the last full rebuild |
| `result_stageA.json` | bottle numbers found by the build (base X, volumes, centroid) |
| `bench_tests.md` | bench-test sheet (written earlier) |

## Scripts (`scripts/`)
`res_params.py` (all numbers), `res_build.py` (helpers and one function per part), `build_stageA.py` (bottle, water, holes), `build_stageB.py` (outlet unit, open-state copy, belly reference), `build_stageC.py` (fill unit P11a-f, funnel P15, fuselage fill-hole and wing references), `build_stageD.py` (saddles, straps, stop, servo, arm, link), `res_check.py` (checks and mass table), `make_pictures.py`, `export_stageE.py` (STEP, STL), `run_all.py`.

## Pictures (`img/`)
`stageA_iso`, `full_iso_closed`, `full_iso_closed_low`, `full_iso_open`, `section_Y0_full` (whole reservoir at Y = 0), `stageB_outlet_iso_closed`, `stageB_outlet_iso_open`, `stageB_section_Y0`, `stageB_section_X80` (outlet close-ups), `fill_closeup` (iso section at Y = 0 with the wing and the fuselage fill hole), `fill_with_funnel` (funnel P15 above the fill port), `top_view_limits` (Y +-55 red, servo limit +-52 orange, wing LE blue).

## Reference bodies (not parts)
`Ref_BellySkin` (floor and belly skin Z -111 to -109.5 with the opening round the valve and a slot for the pin line), `Ref_FuselageTop` (deck with the D25 fill hole, interp. height), `Ref_Wing` (SD7062 x 280 mm, +3 deg, Y +-60). They are hidden, are not in the STEP, the mass table or the overlap check, and are used for checks 4 and 6 and for pictures.

## Rev A.1 (D-049, D-050)
The rev A vent (P11a-e, hole D8.3 at X -7.7) is replaced by the fill unit of plan section 12: hole D13.3 at X -11.0 (`FILL_X_C` in `res_params.py`), parts P11a fill flange, P11b gasket, P11c nut, P11d cap with vent holes, P11e cap seal, P11f vent flap. Group `C_Fill`; the funnel P15 is in group `E_Ground` (hidden).

## Rev A.2 (D-051, T2-30)
Belly lowered: skin outer face Z -117.0, floor Z -115.5 (`BELLY_Z`, `FLOOR_Z`); belly opening `FLOOR_HOLE_RECT`. MG90S upright with the shaft down, arm in the plane Z -110.5 (`SERVO_X_SHAFT`, `SERVO_Y_SHAFT`). Fill gasket OD 18. Open-state pose 150 deg (`OPEN_ANGLE`). New picture `servo_link.png`. Check 11 (nothing below Z -114) is in `check_report.txt`.
T2-31: arm R 9, shaft Y 44.90, shaft X 64.364 (arm envelope Y max 53.26).
