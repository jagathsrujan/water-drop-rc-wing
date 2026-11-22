# Wing rev A — CAD

- Model: `Wing_revA.FCStd` (FreeCAD 1.1). STEP: `Wing_revA.step`.
- Rebuild everything: in FreeCAD's Python console, `exec(open("<repo>/design/cad/scripts/run_all.py").read())`. Values live in `scripts/wing_params.py`.
- Laser: `dxf/laser_<thickness>_<grade>_sheetNN.dxf` (300 × 100 mm sheets, grain along X; layer CUT = cut, LABEL = part names, SHEET = sheet outline — do not cut LABEL or SHEET). Previews in `img/dxf_preview_*.png`.
- Print (PETG): `stl/` — frame, hatch and horn come as right/left pairs.
- Lists: `cut_list.md` (laser groups + strip stock + hardware), `mass_table.md`.
- Checks: `check_report_stageC.txt`, `check_report_stageB_extra.txt`.
- `vendor/`: put the MG90S CAD file here; the model uses a placeholder with standard dimensions.
