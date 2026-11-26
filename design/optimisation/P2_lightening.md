# P2 — Lightening and design-optimisation study (rev B, Fusion model)

Study only: no CAD or part-data change. Date 2026-11-26. Basis: the P1 decision (1.5 mm medium balsa at generic
grade, one 1.5 mm birch-ply stock, the laminates in `p1_schedule_1p5.csv` and P1 section 9), the part outlines in
the build-kit registry, and the cited design values of `references.md`. Scripts: [`p2_cutouts.py`](p2_cutouts.py) (masses of the
lightening holes from the outlines, pictures in `p2_fig/`), [`p2_cg.py`](p2_cg.py) (CG), [`P2_lightening.m`](P2_lightening.m) (hand calcs;
output in [`P2_lightening.txt`](P2_lightening.txt)).

**FEA status: not run.** Ansys MAPDL 2024 R1 is installed (`E:\ANSYS Inc\v241`), but the local licence server
rejects the licence: "Invalid (inconsistent) license key … usually happens when a license file has been altered"
(FlexNet −8,544, features ansys, mech_1/2, meba, preppost). Nothing was changed or installed. The critical parts are
checked by hand calcs below, including an orthotropic plate solution. The FEA moves to the tool chosen in P4 (see
section 6).

## 1. Ranked list of changes (for the user's approval)

Grams are against the P1 option A estimate of 728.1 g. "Margin" is allowable / ultimate stress (≥ 1 holds) with
the P1 design values (ρ 0.12, 5th percentile).

| # | Change | Δ mass | Margin after (before) | Risk | Effort | Recommend |
|---|---|---|---|---|---|---|
| 1 | **Fix the mass bookkeeping:** `build_pod.py` leaves the extra bodies that joins create in NOSE-RING and SERVO-MOUNT on Fusion's default material ("Steel", 7.85). They are PETG (`pod.py`). `fxlib.build_list` already re-applies the material; `build_pod.py` does not | **−11.4 g** (on paper; the aircraft is that light already) | — | none | 1 line + rebuild | **yes** |
| 2 | **Wing tip ribs and tip caps** W-TIP-R/L, W-TIPCAP-R/L in **one** 1.5 layer instead of 2 × 1.5 | −5.3 g | judgement: tip knocks only; the tip rib still carries the cap strips | low–medium | part data | **yes** |
| 3 | **Hex lightening of the pod sides** through both layers (157 cells, 8 mm across flats, 2.5 mm webs; FreeCAD rev B rule set; grip zone, servo zone, band stubs and ±5 mm at the formers solid) | −3.8 g (film on the inner face over the holes counted) | aft-cone bending 12.4 (14.8 solid); finger squeeze outside the grip zone 1.28 between holes (handling rule as rev B) | low (rev B design) | laser only | **yes** |
| 4 | **Hatch** HN-R/L, HF: hex cells | −0.9 g | judgement (hatch under film) | low | laser only | yes |
| 5 | **Trays** TST, TRAY: windows | −0.6 g | judgement (servo screws and battery strap zones solid) | low | laser only | yes |
| 6 | **Floor** windows between formers, outside the saddle feet, skid line and formers | −0.4 g | landing load path left solid | low | laser only | yes |
| 7 | **Aft deck** windows | −0.3 g | — | low | laser only | yes |
| 8 | Extra cells in the 1.5 ribs beside the existing holes (ribs 165 only fit) | −0.2 g | judgement | low | laser only | optional |
| 9 | **Front stop FS (needed):** lay the two 1.5 birch sheets **crossed** (alternating veneers) and widen the 4 spokes 10 → 14 mm | +0.6 g *(estimate)* | **1.57** (0.78 for 2 × 1.5 parallel; 0.16 for today's lite-ply) | low | part data | **yes** |
| 10 | **Floor pads (needed):** one 40 × 15 birch 1.5 pad on the floor under each saddle foot, over the skid | +1.2 g | floor crushing **1.09** (0.41); pad bending 2.29 | low | 2 small parts | **yes** |
| 11 | **Wing root web** WF-R1/L1 (y 0–110) as 2 × 1.5 | +0.4 g | **2.09** (1.04) | none | part data | yes |
| 12 | **CG:** the empty CG is about **X 89**, 9 mm aft of X 80 *(estimate, section 4)*. Move the **receiver** to the nose bay (X −40) and the **battery** to the front of its range (X −120): no mass | 0 g | CG −7.2 mm → X ≈ 82 | low | placeholders + tray | **yes** |
| 13 | **Booms 10 × 8 → 8 × 6 mm** carbon tube | −9.4 g, CG −5.2 mm | strength 1.22 (2.06); stiffness 47 % of today | **medium–high** (tail stiffness, flutter) | buy | **not now**: P5/P6 decide with a measured or better-sourced E |
| — | Rejected: inner side layer as vertical posts in place of a full sheet | (≈ −10 g) | finger squeeze 0.75 between posts (orthotropic plate) | — | — | no |
| — | Rejected: a smaller LE with the D-box wrapped round it | ≈ 0 g | the extra D-box sheet weighs what the LE loses | — | — | no |
| — | Formers, bulkhead, saddles, stab, fin, elevators, rudder | 0 g | already windowed: no further 8–20 mm cells fit inside the solid bands | — | — | — |

**Totals:**
- Physical changes 2–11: **−8.5 g** (−11.2 lightening, +2.2 strength fixes).
- With the bookkeeping fix 1: **−19.9 g**.

**New estimate:** 728.1 − 11.4 − 8.5 = **708.2 g empty, score 140.6**. With the booms (13), if P6 clears them:
about 698.8 g, score 142.5.

The biggest lever is still **sheet density** (P1: ±0.02 g/cm³ = ±29 g). Weigh every sheet and put the lightest on
the D-box (31.5 g), the sheeting (8.1 g) and the tail.

## 2. The P1 open items

**(a) Front stop (nose-in 10 g, 102 N limit, 152 N ultimate; spoke = cantilever W/n at 7.5 mm):**

| Lay-up (2 × 1.5 birch) | 4 spokes × 10 | 4 × 14 | 6 × 10 | 6 × 14 | full plate |
|---|---|---|---|---|---|
| faces parallel (0/90/0/0/90/0) | 0.78 | 1.09 | 1.17 | 1.64 | 1.24 |
| **crossed (0/90/0/90/0/90)** | 1.12 | **1.57** | 1.68 | 2.35 | 1.77 |

Crossing the two sheets costs nothing, and it makes both spoke directions equal. With 14 mm spokes the margin is
1.57. P3 makes the front stop as two 1.5 birch layers with crossed face grain and 14 mm spokes.

**(b) Floor crushing at the 10 g belly landing:**
- Today: 76 N per saddle (ultimate) crushes the 1.5 balsa floor between the 15 mm saddle foot and the 15 mm skid at
  0.34 MPa, against 0.14 MPa (compression ⊥, proportional limit, 5th percentile, *estimate*).
- A bearing length of 36.6 mm is needed. A **40 × 15 × 1.5 birch pad** on the floor top under each saddle foot gives
  1.09, and the pad itself 2.29 in bending.
- Note: the allowable is a proportional limit. Balsa beyond it dents progressively rather than breaking, so this is
  a serviceability margin as much as a strength one.

**(c) Side grip zone, orthotropic plate:** a Navier double series for a simply supported plate, with layer stiffness
from R1 Tables 5-1 and 5-2, a 15 × 15 mm finger patch and 30 N ultimate. Margin is first-layer failure:

| Panel 67 × 95 (between B1 and B2) | Laminate | Margin | Centre deflection |
|---|---|---|---|
| Grip zone (X 30–130, lower half) | balsa 1.5 (grain X) + birch 1.5 | **2.09** | 0.4 mm |
| Elsewhere | balsa 1.5 + balsa 1.5 crossed | **1.28** | 1.0 mm |
| Inner layer as posts (outer only, 20 mm between posts) | balsa 1.5 | 0.75 → rejected | 0.3 mm |

So the isotropic formula of P1 was too crude: both laminates pass. The simply supported edge is conservative,
because the formers and keels clamp the panel.

**(d) Ribs 2 → 1.5 mm:**
- The rib web shear at the spar is small: 5.6 N per rib at n 6, τ ≈ 0.12 MPa against 1.21.
- The cap-notch bearing check across the rib grain does not discriminate. It is below 1 for the 2 mm ribs of rev A
  too (0.14 MPa allowable is a 5th-percentile proportional limit), and the D-box takes most of the front pressure.
- Keep the root and horn ribs at 2 × 1.5 (P1). Put a glue fillet at each cap notch. Confirm in P6.

**(e) Bulkhead / boom joint:**
- P1 hand calcs: ring bearing 5.8, ring-to-plate glue shear on the balsa face 4.3, plate bearing 6.2, plate without
  a ring 2.8.
- FEA is pending (section 6).
- Aft-cone bending with the side holes: 12.4.

**(f) Root web shear:** 1.04 with one 1.5 web. Two layers in the root bay give 2.09 for 0.4 g (change 11).

## 3. Sheets

- With the changes above, the balsa area falls by about 0.02 m².
- The P1 estimate of **18 sheets of 100 × 1000** (55 % nesting, 15 % spare) stands; P3 re-nests on one stock and
  gives the real count.
- Birch: 1 sheet of 300 × 300 × 1.5 (front stop 2 layers, firewall, doublers, rings, grip inners, RO-MP, skids, flap
  stop, horns, and now 2 floor pads).

## 4. CG (estimate)

[`p2_cg.py`](p2_cg.py) works from:
- every body of `bodies.json` at the centre of its bounding box, with masses corrected per finding 1;
- the electronics placeholders, at the catalogue masses of `FIXED_MASSES.md` (the receiver at its 13.5 g
  placeholder);
- film and glue at their assembly centroid;
- water at X 80, where the reservoir build puts the water centroid (`res_params.X_CG`).

| | Mass | CG X |
|---|---|---|
| Empty (as modelled, corrected) | 704.9 g | **89.4** |
| Loaded (996 g water at X 80) | 1700.9 g | 83.9 |

Levers (empty CG shift):

| Lever | Shift |
|---|---|
| Battery to X −120 (front of `BATT_XC_RANGE`) | −2.9 mm |
| Receiver from X 186 to X −40 | −4.3 mm |
| Booms 8 × 6 | −5.2 mm |
| Each gram off the tail | −0.85 mm |
| Each gram of nose ballast | −0.38 mm (ballast is the worst option) |

With the battery and receiver moved, the empty CG is about X 82 and the loaded CG about X 81. **P5 sets the CG
range** (neutral point and static margin), so X 80 may not be a hard limit. The placeholder positions, wiring
(not modelled) and the bounding-box centroids make this ±3 mm at best.

## 5. Other findings

- The **cut-outs are worth little on this design** (about 6.6 g of holes fit in all). The formers, saddles,
  bulkhead and tail are already windowed, and the 8 mm solid bands of the rev B rule set leave little room on the
  100 mm wide side pieces. The remaining mass is in the D-box and sheeting (39.6 g), the LE (11.1 g), the ribs
  (16.0 g), the carbon booms (42.8 g) and the PETG prints (41.3 g).
- **PETG prints** are counted solid (1.27 g/cm³) in the mass table. The tail block (6.2 g), collars (5.0 g), nose
  ring and servo parts can be printed with 2–3 walls and 15–20 % infill. P3 should read the real masses from the
  slicer (Bambu Studio shows the filament mass) instead of the solid-volume estimate.
- **Hatch magnet seats** (4 pairs of D6 × 2) are not modelled. P3 should add 6.2 mm holes in HF and in the hatch
  (mass neutral).
- **Covering film:** the wing uses 50 g/m² and the pod and tail 30 g/m², both *estimates*. Weigh a 100 × 100 mm
  piece of the film you buy: on the wing's 0.585 m², 10 g/m² is 5.9 g.

## 6. FEA

- **Pending.** The plan's FEA cases are the front stop, the floor under a saddle, the grip-zone panel and the
  bulkhead / boom joint.
- Ansys MAPDL cannot run here until the licence problem is fixed. That is the user's call: a valid licence, or the
  free Ansys Student edition, which is limited to small models but enough for these parts.
- Otherwise these cases move to the tool P4 picks: SolidWorks Simulation is installed with SolidWorks 2026.
- The hand calcs above size every change in the list, so none of them waits for the FEA.

## 7. Decision (gate P2)

**2026-11-26, the user: "Approve 1–12".** P3 implements changes 1–12 of section 1. The booms stay 10 × 8 mm until
P5/P6.
