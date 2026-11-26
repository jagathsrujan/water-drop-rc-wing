# Workspace rules — water-drop RC aircraft

## Pictures for the abstract and reports
- Whenever a CAD model, FEA run or CFD run is made or updated, **save pictures of it** for the abstract and the
  reports. Don't wait to be asked.
  - CAD: iso, side, top, front and detail views (Fusion: `design/cad_fusion_revB/scripts/export_views.py` → `img/`).
  - FEA: stress and displacement plots of every reported case, next to its result JSON
    (`design/simulation/structure/cases/`).
  - CFD: pressure and velocity cut plots and a streamline or surface-pressure view (`design/simulation/aero/`).
- Collect the ones the abstract uses in `design/abstract/fig/` with a caption list.

## Engineering
- Every material value is cited (USDA Wood Handbook FPL-GTR-190, datasheets) or marked as an estimate; sources go in
  `design/optimisation/references.md`.
- Balsa is the generic local grade: design strength at density 0.12 g/cm³, mass at 0.14 g/cm³. No premium or sorted
  light sheets.
- One balsa stock (1.5 mm medium) and one birch-ply stock (1.5 mm); thicker parts are laminated from 1.5 mm layers.

## Repository
- Ask the user before pushing anything to `main`.
- Never touch the user's uncommitted `design/cad_fuselage_balsa/Fuselage_revB_balsa.FCStd`.
