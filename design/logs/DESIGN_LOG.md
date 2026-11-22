# Design log

Stage-by-stage summary. Details in the stage notebooks (`design/logs/*_log.md`) and `design/DECISIONS.md`.

| Date | Stage | What was done | Checks | Pictures |
|---|---|---|---|---|
| 2026-11-21 | 1 Weather | Design inputs (density, wind, temperature) | — | — |
| 2026-11-21 | 2 Wing concept | SD7062, chord 280 mm, balsa built-up, high wing, rubber bands, 0° dihedral (D-001…D-012) | — | — |
| 2026-11-21 | Wing CAD rev A, Stage A | Primary structure in FreeCAD (`design/cad/Wing_revA.FCStd`): ribs, LE, D-box and centre sheeting, carbon/balsa spar caps, shear webs, full-depth false spar, cap strips, TE wedges, tip ribs and ring caps, lightening and wire holes. Mass stop at 172 g projected → reduction set D-013 (limit 155 g); D-014…D-016 settled with the user. | Span 990.00, chord 280.00, depth 39.20 mm, 117 valid solids, 0 overlaps, Stage A 133.3 g, projected ≈ 154 g | `design/cad/img/stageA_*.png` |
| 2026-11-21 | Wing CAD rev A, Stage B | Aileron (V-bevel LE, end ribs, station ribs, horn rib, TE), 4 CA hinge slots each side, MG90S placeholder on its side, PETG frame and 0.8 mm hatch with servo lugs, slot-in horn, Z-bend pushrod, band rub plates. Fixed 2 clearance faults and 12 modelling overlaps; lightened the printed parts (D-013 item 5). | Aileron 325.00 mm, gaps 1.00 mm, no contact at ±20° (0.74 mm), servo ≥ 1.00 mm, arm ±35° 1.00 mm, 0 overlaps, 156.3 g (limit 155 g → asked) | `design/cad/img/stageB_*.png` |
| 2026-11-21 | Wing CAD rev A, Stage C | Outputs: FCStd, STEP, 21 laser DXF sheets (read back), 8 STL, cut list, mass table, pictures. Fixed an OCC area/volume error on the full airfoil face (split at the LE) and rebuilt all stages with `run_all.py`. | Span 990.00, chord 280.01, depth 39.20, aileron 325.00, servo ≥ 1.00 mm, 0 overlaps, 156.6 g after the lug fix (limit 160 g) | `design/cad/img/wing_*.png`, `dxf_preview_*.png` |
