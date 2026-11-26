# P3 — the approved P1/P2 changes in the rev B Fusion model

Date 2026-11-26. Brief: [`P3_brief.md`](P3_brief.md). Model: [`design/cad_fusion_revB/`](../cad_fusion_revB/README.md).

## Result

| | P2 estimate | **P3 model** |
|---|---|---|
| Empty mass | 708.2 g | **702.6 g** (direct sum of every body, catalogue electronics, film, glue, lamination glue) |
| Score (996 × 100 / empty) | 140.6 | **141.8** |
| CG empty / with 996 g water | X ≈ 82 / ≈ 81 | **X 82.4 / X 81.0 mm** |
| Stock | 1 balsa + 1 birch | balsa 1.5 mm medium + birch ply 1.5 mm, nothing else |
| Laser parts | — | **226** (198 balsa, 28 birch); 41 laminated parts made of 113 layer pieces |
| Laser sheets | — | **44 balsa 300 × 100 + 1 birch 300 × 300** |
| Buy | 18 sheets 100 × 1000 (P1 estimate) | **25 balsa 100 × 1000** (21 + 15 % spare: 15 for the laser, 6 for strips and sheeting) + **1 birch 300 × 300** |

Group masses (`mass_table.md`): pod 135.8 g, wing 159.5 g (without servos), tail 75.7 g.

The model is 5.6 g (0.8 %) under the P2 estimate. P2 added up P1's part-by-part estimate; P3 measures every body in
Fusion (exact hex cells, exact laminate outlines, lamination glue from the real face areas). The difference is within
the accuracy of the estimate. The real uncertainty is the sheet density: ±0.02 g/cm³ is ±29 g (P1). Weigh the sheets.

The laser part of the sheet count agrees with P1's 55 % nesting assumption: 0.83 m² of part outline on 44 laser sheets
is 63 % of the sheet area, and 15 of the 21 sheets go to the laser. The rest are the strips and sheeting.

## What was implemented

All of the P3 brief, sections 1–8, except the hatch magnet seats (see Open items). Highlights:

- **Overrides in one file:** [`revb_params.py`](../cad_fusion_revB/scripts/revb_params.py) copies the FreeCAD
  parameter modules and overrides them. The FreeCAD files are unchanged.
- **Per-former thickness** (`FORMER`):

  | Formers | Build |
  |---|---|
  | N1, N2, B1, B2, B4, EF | balsa 3 × 1.5 (0/90/0) |
  | BH | balsa 4 × 1.5 |
  | FS | birch 2 × 1.5, crossed grain, 14 mm spokes |

  The direction each former grows:

  | Former | Final X range (mm) | Grows |
  |---|---|---|
  | N1 | −130 … −125.5 | aft |
  | N2 | −100 … −95.5 | aft |
  | B1 | 38 … 42.5 | aft |
  | B2 | 105 … 109.5 | aft |
  | B4 | 170.03 … 174.53 | aft |
  | BH | 236 … 242 | aft from the aft kink |
  | EF | 300.5 … 305 | forward from the pod end, so the pod length stays 305 |

  The side and floor slots, deck tabs, tray tabs and jig fits all follow the former thickness.
- **Laminates** ([`lam.py`](../cad_fusion_revB/scripts/lam.py)): every multi-layer part is one component with one
  body per layer piece (`B1-2a` = layer 2, piece a). Each piece is ≤ 100 mm across the grain and ≤ 294 mm along it.
  The joints are staggered between layers. [`lam_check.py`](../cad_fusion_revB/scripts/lam_check.py) checks that
  each piece is connected, its size, and that the layers cover the part: 113 pieces OK.
- **Laser:** each layer piece is its own laser part, turned to its own grain. The new MaxRects nester
  (`laser.py`) gives 44 balsa sheets where the old shelf packer needed 46. The kerf coupon is 1.5 mm only.
- **P2 changes 1–12:**
  - Hex cells in the sides, floor, deck, hatch, TST/tray and rib 165. The side holes go through both layers and are
    filmed on the inner face.
  - Floor pads under the saddles.
  - Root-bay web doublers.
  - Tip rib and tip cap as one 1.5 mm layer, with the half span kept at 495.
  - Receiver on the tray at X −76 … −31, battery at X −120.
  - The join bodies keep their material (P2 finding 1).
- **Strips:** single 1.5 sheet stock, longerons as an L (1.5 × 6 + 1.5 × 4.5). The build kit's strip rules,
  materials, BOM, "What to buy" section and a new "laminate the parts" step are all updated.

## Checks

| Check | Result |
|---|---|
| Fusion interference, all 453 bodies | **contacts only**. Largest: battery corner on the sloped nose floor 0.54 mm³ (the real pack has rounded corners), pushrod ends at the horns 0.02–0.20 mm³ (as before), FS / ledge 0.14 mm³. The J5 seat gauges and WC1 wing cradles stand where the wing goes in the model: intended, as before. |
| `check_joints.py` | 14 dovetail joints, 0 gaps or overlaps |
| `lam_check.py` | 113 layer pieces OK |
| `laser_loops.py` / `laser.py` | exact loops for all 226 parts; 45 DXF sheets |
| `mass_summary.py`, `p2_cg.py` | 702.6 g, CG X 82.4 (one source for the film and glue lines now) |
| `make_build_kit.py` | **0 problems** |
| Jigs | 42 jigs + 5-part jig base + 20 pins rebuilt; base / jig clashes 0 |
| Exports | `export/WaterDrop_revB_fusion.f3d` (59 MB), `export/WaterDrop_revB_fusion.step.zip` (13.5 MB zipped; the 110 MB STEP is over the GitHub file limit and is not committed) |

### Problems the checks found, and the fixes

1. **Battery tray in the nose floor (74 mm³).** The tray went from 1.5 to 3 mm and its underside cut into the
   15.5° nose floor at its front end. The tray now starts at X −146 instead of −150.
2. **Servo-bay rear webs missing (WR-R3 / WR-L3).** Rib 165 went from 2.0 to 1.5 mm, which moved its inner face from
   Y 164.0 to 164.25. That is past the rear-web limit `REAR_WEB_Y = 164`, so the webs silently dropped out. The
   limit now follows the rib (164.25). The build kit's part check caught it.
3. **Wing mass counted the wing jigs** (the WC cradles sit under the Wing component): 280 g instead of 159 g.
   `mass_summary.py` now leaves out the jigs, and `p2_cg.py` takes its film and glue lines from it.
4. **Stale parameters in Fusion.** The Fusion Python process kept an old `revb_params` in memory, because it is
   imported with `from … import`. `boot.py` now reloads `geo`, `revb_params` and `lam` first. The full builds were
   not affected: they ran before the last parameter edit, which a spot check of the receiver, pads, centre-rib
   layers and web doubler confirmed.
5. **The jig fit check crashed** on root-level bodies (no assembly context). Fixed as in `check_model.py`.

## Open items

- **Hatch magnet seats** (4 pairs D6 × 2; their 3.4 g is in the mass) are not modelled. A 2 mm magnet doesn't sit
  flush in the 1.5 mm hatch, and the ledges are 3 mm wide, so each pair needs a small seat (for example a birch pad
  on the ledge) near X −150 and X −20. This is a small design task for the next model pass.
- **CG:** the loaded CG is X 81.0, 1 mm aft of the X 80 target. The battery is already at the front of its range.
  P5 checks the static margin at this CG (AVL at P2: SM 13 % at X 80; about 12.6 % at X 81).
- **Nesting:** many parts nearly fill a 300 × 100 sheet, so the bounding-box nester is near its limit (bounding-box
  fill 74 %). True-shape nesting could save a few more sheets.
- **Build speed:** a full Fusion rebuild takes about 1.5 h, because the parametric timeline is single-threaded.
  Proposed: one Fusion file per sub-assembly plus direct modelling, or a parallel FreeCAD builder that reuses the
  same part data. The user decides after P3.
