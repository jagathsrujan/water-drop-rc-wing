# P3 brief — implement the approved changes in the rev B Fusion model

For the session that runs phase P3. Start it from branch `claude/optimisation-490645` (its own worktree), Opus, high
effort. The Fusion bridge must be running (`python tools/fusion_bridge/fx.py --ping` → pong). Only one Fusion job at
a time.

## Context

The water-drop RC aircraft rev B is modelled in Fusion from Python part data in `design/cad_fusion_revB/scripts/`.
Read these first:
- `design/OPTIMIZATION_PLAN.md`;
- `design/optimisation/P1_single_stock.md` (sections 4, 5, 9) and `P2_lightening.md` (sections 1, 2, 7);
- `design/cad_fusion_revB/README.md`;
- the notes `P1_single_stock.md` and `P2_lightening.md` in the shared notes folder
  `C:\Users\jagath srujan\AppData\Local\Claude-Data\claude_pzs8sxrjxfjjc\side-session-notes\local_29e6307b-30b3-404a-b082-7bb80e2753da`.

The bridge jobs follow the checkout they are run from (commit 812a4d8), so run them from your worktree:
`python tools/fusion_bridge/fx.py design/cad_fusion_revB/scripts/build_all.py`.
`build_all.py` closes every open Fusion document without saving: check `app.documents` first, and if any document is
saved or named (not "Untitled"), ask before running.

**User decisions:**
- One balsa stock, 1.5 mm medium (generic local grade).
- One birch-ply stock, 1.5 mm.
- No lite-ply.
- P2 changes 1–12 approved; the booms stay 10 × 8.

## What to change

Put the overrides in the Fusion part data (`pod.py`, `wing.py`, `tail.py`). **Do not change** the FreeCAD parameter
files `bal_params.py`, `fus_params.py`, `wing_params.py` or `res_params.py`: they are the reference of the FreeCAD
models.

1. **Materials and thicknesses (P1 option A):**

   | Part(s) | Today | New |
   |---|---|---|
   | Inner side layer | 1.0 | 1.5 balsa (`T_IN`); every width that uses `T_LAM` shifts 0.5 mm inward. Check the bottle and saddle clearances. |
   | Grip-zone inners RI-M2G, RI-M3G, LI-M2G | 1.0 birch | 1.5 birch |
   | Formers N1, N2, B1, B2-R/L, B4, EF | lite-ply 3 | **balsa 3 × 1.5 = 4.5 mm** (0/90/0, the legs along the outer-layer grain) |
   | FS | lite-ply 3 | **birch 2 × 1.5 with crossed face grain**, 4 spokes widened 10 → 14 mm (P2 item 9) |
   | BH | birch 3 | **balsa 4 × 1.5 = 6 mm** (0/90/90/0), birch tube rings TR1/TR2 kept |
   | Saddle faces S1a/S1d/S2a/S2d, bridges, TST | lite-ply 3 | balsa 2 × 1.5 |
   | TRAY | lite-ply 1.5 | balsa 2 × 1.5 = 3 mm (the tray drops 1.5: check the battery and ESC clearances) |
   | FW, SD, TR rings | birch 3 | 2 × 1.5 birch (same thickness) |

   Each former gets its own thickness (replace the single `FT`). It flows into `former_geom` (x1), the side slots
   (line ~251), the floor slots (~414), the deck tabs, the tray tabs (~684) and the jig fits. Choose the direction
   each former grows so nothing passes a kink or the pod end: EF ends at the pod end X 305, and BH sits on the aft kink
   X 236. Say what you chose.

2. **Balsa sheets are 100 mm wide.** B1 and B4 (110 × 104) and BH (105 × 101) do not fit one balsa piece in any
   layer. Make each layer from pieces ≤ 100 mm across the grain, with the joints staggered between layers so every
   joint is bridged (as the side laminate does). For example, a U-frame layer with vertical grain is two halves; a
   layer with horizontal grain is a bottom bar plus the leg tops. Every piece is a laser part with its name and layer
   engraved.

3. **Laser output for laminates:** a part made of n layers of 1.5 must appear in the DXF as n layer parts on 1.5 mm
   sheets (balsa or birch), named for example `B1-L1`, `B1-L2`, `B1-L3`, each turned to its own grain (alternating
   for cross-grain layers). Update `laser.py` (nesting, `cut_list.md`), `tools/build_kit/kit_data.py` (strip and sheet
   materials, `STRIP_RULES`) and the BOM, so the BOM lists **one balsa stock (1.5 mm medium, 100 × 1000) and one
   birch-ply stock (1.5 mm, 300 × 300)** plus the carbon, wire and hardware.

4. **Strips from the 1.5 sheet:**
   - keels 3 × 5, capstrips 3 × 6 and ledges 3 × 3 become 2 × 1.5 laminated strips;
   - the longerons become an L of 1.5 × 6 + 1.5 × 4.5 instead of the 6 × 6 triangle (model change);
   - the spar-cap balsa CAP-B becomes 2 × 1.5 medium (was 3 mm hard);
   - the LE becomes 4 × 1.5 × 16.3 laminated, then shaped;
   - the TE wedges and aileron TE become 4 staggered 1.5 strips sanded to the wedge;
   - the aileron LE becomes 2 × 1.5 × 15;
   - the D-box, centre sheeting and cap strips become 1.5 medium.

   These are cut-list and BOM changes; the geometry is unchanged apart from the longerons.

5. **Wing:**
   - ribs W-R055 … W-R440 and the aileron ribs 2.0 → **1.5**;
   - W-C and AH-R/L 2.0 → 2 × 1.5;
   - W-R110 and FSP 3.0 → 2 × 1.5 (same thickness);
   - the rib thickness feeds the egg-crate slots in the false spar and the web end-tab slots: check them with
     `check_joints.py` and the interference check;
   - P2 item 2: tip ribs W-TIP-R/L and tip caps W-TIPCAP-R/L as **one 1.5 layer**. Keep the half span 495: move
     `Y_END` and lengthen the span-wise parts rather than shortening the wing, or say why not;
   - P2 item 11: the root-bay webs WF-R1 / WF-L1 as 2 × 1.5;
   - P2 item 8: the extra cells in rib 165 (`p2_cells.json`).

6. **Tail:** stab, fin, elevators and rudder 3.0 → 2 × 1.5 cross-grain (same thickness). Horns 1.5 birch.

7. **P2 changes:**
   - **1:** `build_pod.py` re-applies `p["mat"]` to every body after `add_join` (as `fxlib.build_list` does).
   - **3:** hex cells through both side layers. Recompute them with `design/optimisation/p2_cutouts.py` after the
     thickness changes; the rule set is in its docstring, and `p2_cells.json` has the old centres. Add film on the
     inner face over the holes to the mass rules.
   - **4–7:** cells in the hatch, TST/TRAY, floor and deck (`p2_cutouts.py` rules).
   - **10:** two 40 × 15 × 1.5 birch floor pads on the floor top under the saddle feet, centred on the skid line. The
     saddle layers get a matching 1.5 mm notch so they bear on the pads.
   - **12:** the receiver placeholder to X −40 and the battery to X −120. Check them against the nose formers and
     the ESC.
   - **Hatch magnet seats:** 4 pairs of D6 × 2 → 6.2 mm holes in HF and the hatch.

8. **Jigs:** update every jig that fits a changed part: J2 squares, J3, J4a (squares the end former), the former
   slots in the jig base, the wing cradles if the ribs move, and TJ2. Keep every jig on the 256 mm bed.

## Checks (all must pass before the report)

- `check_model.py` with `DO_INTERFERENCE = True`: only surface contacts.
- `check_joints.py`.
- `laser_loops.py` then `python laser.py`.
- `python mass_summary.py`: the new mass table. Compare it with the P2 estimate of 708.2 g and explain the
  difference.
- `python design/optimisation/p2_cg.py`: the CG.
- `export_views.py`.
- `python tools/build_kit/make_build_kit.py`: its check report must show 0 problems. Update the build steps in
  `tools/build_kit/steps.py` for the laminating steps (laminate the sheets flat under weights before laser cutting,
  stagger the joints).
- Update `design/cad_fusion_revB/README.md`, `mass_table.md` and `build-kit/MATERIALS.md`.
- Export the `.f3d` and the STEP.

Commit on your branch (end each commit message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`). Do
not push and do not merge: the user approves P3 before anything goes to `main`. Never touch
`design/cad_fuselage_balsa/Fuselage_revB_balsa.FCStd`. Leave a hand-over note `P3_fusion.md` in the shared notes
folder. In your final message, put first the branch and commit, the new empty mass and score, the part count, the
sheet count and the check results.
