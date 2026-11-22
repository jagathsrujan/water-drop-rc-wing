# Wing rev B (foam blocks) — CAD for the A/B comparison

- Plan: `REVB_PLAN.md`. Notebook: `../logs/wing_revB_log.md`. Decisions D-024 … D-032 in `../DECISIONS.md`. Comparison: `../studies/revA_vs_revB.md`.
- Model: `Wing_revB.FCStd` (FreeCAD 1.1), STEP `Wing_revB.step`, printed parts `stl/` (PLA LE/TE, PETG servo parts).
- Rebuild in FreeCAD's Python console, in this order (each with `WING_SCRIPTS` = this `scripts/` folder): `build_stage1.py`, `build_stageB.py`, `build_stage3.py`.
- Values: `scripts/wing_params.py` (rev B section at the end). The scripts are copies of rev A (`../cad/scripts/`) with paths, document name and checks changed; rev A is not changed.
- Mass: `mass_table.md` (with ASA Aero, LW-PLA and B-lite variants). Checks: `check_report_stage3.txt`, `check_report_stageB_extra.txt`. Lift: `lift_revB.txt`.
- Not made: laser DXF files for the plates and half ribs (comparison model only).
