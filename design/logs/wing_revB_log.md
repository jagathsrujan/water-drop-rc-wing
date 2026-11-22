# Wing rev B (foam-block construction) — engineering notebook

Started 2026-11-22. Decision in force: D-024 (user): keep rev A unchanged, model option B as rev B, compare, then choose.
Rev A is not changed. Rev B lives in `design/cad_revB/`.

## 1. Section numbers (SD7062 × 280, from `wing_geom.py`, freecadcmd)

| Region | Area cm² |
|---|---|
| Outer outline | 69.24 |
| Inner outline (1.5 mm inset, x 3–258) | 60.84 |
| Inner, x 6–71.1 (under the D-box, forward of the front web) | 19.34 |
| Outer, x 80.1–205 (aft of the rear web, film directly on foam) | ≈ 37.9 (inner 34.18 + 1.5 mm skin band) |
| Outer, x 208–255 (fixed bays only) | 4.74 |
| Foam block section: aileron bay / fixed bay | 57.3 / 62.0 |

Depths: x 6 16.3 mm, x 75.6 39.2 mm, x 205 16.8 mm, x 255 4.5 mm.

## 2. Claude's view before the questions (written before the user answers)

### 2.1 Layout (block stations keep the rev A interfaces)
Candidate L7, 7 blocks, plates at the rev A rib faces:
- Centre C: foam y ±54.5, plates ±(54.5–56), x 6–255. Replaces rib 0, ribs ±55 and the aft centre sheeting (band seat on foam + film; rub plates kept).
- Servo S: plates y 110–111.5 and 164–165.5, foam 111.5–164 with the servo pocket. The servo frame tabs glue to faces 111.5 / 164, the same as rev A → servo clearance unchanged.
- Mid M: plates 274–275.5 and 329.5–331, foam 275.5–329.5.
- Tip T: plates 438.5–440 (face 438.5 keeps the 1 mm aileron gap) and 490.5–492, foam 440–490.5, x 6–255; rev A ring cap kept at 492–495.
- Hollow bays: 56–110 (54 mm), 165.5–274 (108.5 mm), 331–438.5 (107.5 mm).
- Foam length 423 mm of 984 mm (43 %). Foam volume ≈ 2410 cm³ (servo pockets removed).

### 2.2 Bay checks (film tension T = 150 N/m *(interp.)*, q at 25 m/s, ρ 1.05 = 328 Pa, Cp −1)
| Check | Bay 54 mm (rev A pitch) | Bay 108 mm, no rib | Limit |
|---|---|---|---|
| Film pillow aft of spar, δ = p a² / 8T | 0.8 mm | 3.2 mm | ≈ 1 mm *(interp.)* |
| False spar bow, q = 2T = 0.3 N/mm, span grain E 2500, I = 37.7 mm⁴: pinned / clamped | 0.35 / 0.07 mm | 5.6 / 1.1 mm | hinge gap 2 mm |
| D-box top skin buckling at n = 6, orthotropic balsa (D11 478, D22 7.3, D3 37 N·mm), b = 53 mm, pinned (**superseded**: b is 75 mm, see §8) | 1.56 MPa capacity | 0.76 MPa capacity; applied at y = 165: 0.45 MPa (0.444 × 1.02) → margin 1.7 | ≥ 1.0 (n = 6 has the 1.5 factor) |

Result: the D-box does not need ribs in the 108 mm bays (margin 1.7 outboard of y = 165; rev A root margin 1.5). The film and the false spar do: 3.2 mm pillow and up to 5.6 mm hinge-line bow against a 2 mm gap. With a vertical-grain false spar (E_T ≈ 38 MPa) the bow is about 66× larger, so the rev B false spar must have span-wise grain (one piece from 1000 mm stock).
**View:** one half rib (x 80–205, 1.5 mm light, with cap strips) at y = 220 and y = 385 each side: ≈ 0.6 g each, 2.5 g total. The D-box part of the bay stays open.

### 2.3 Mass (change against rev A 156.6 g; empty basis 597 g; score 996 × 100 / empty)
Removed from rev A: ribs 2 mm 14.7, aft pieces 0.7, ribs 110 3.7, tip ribs 3.6, cap strips 4.2, LE 8.5, TE wedges 2.7, centre sheeting 5.2 = **43.3 g**.
Added: foam (2410 cm³), 14 face plates (≈ 0.86 g each in 1.5 mm light without holes, ≈ 0.58 g with 33 % holes), half ribs 2.5 g, printed LE (32.7 cm³ printed) and fixed-bay TE (14.1 cm³), foam glue ≈ 3 g *(interp.)*.

| Foam | Foam g | Δ with ASA Aero LE/TE (33 g) | Score change |
|---|---|---|---|
| EPS 15 solid | 36 | +39 g | −6.1 % |
| EPS 20 solid | 48 | +51 g | −7.9 % |
| EPS 20 hollowed (≈ 45 % removed) | 27 | +30 g | −4.8 % |
| XPS 30 solid | 72 | +75 g | −11.2 % |
| XPS 35 solid | 84 | +87 g | −12.7 % |

Printed LE + TE: LW-PLA 0.55 26 g, ASA Aero 0.70 33 g, PETG 59 g (balsa LE + TE: 11.2 g).
**No rev B layout is lighter than rev A.** The lightest credible (EPS 15 hollow, 1.0 mm plates, LW-PLA) is about +14 g, but LW-PLA fails the heat check.

### 2.4 Views on each open item
- Foam: **EPS 20, solid** (+51 g with ASA Aero). Hollowing saves ≈ 21 g but adds hand work and removes most of the crush gain. XPS 30 has a better surface and 2–3× the crush strength, +24 g.
- Layout: **L7**. Every rev A rib station becomes a plate or a half rib; foam is where loads enter (band seat, servo, tips).
- Bay ribs: **half ribs at 220 and 385** (numbers above).
- Printed LE/TE material: **ASA Aero** on the H2D (HDT 85 °C, +25 °C margin to a 60 °C surface). LW-PLA fails (HDT 53 °C). PETG passes by +9 °C, but +26 g against ASA Aero.
- Plates: **1.5 mm light balsa with lightening holes** ≥ 8 mm from the edge; edge sealed with thin CA so that the hot wire glides *(interp.)*. 1.0 mm saves ≈ 3 g but is weak as a template and as a film edge.
- Printed TE extent: fixed bays only (centre and tips). The aileron bays keep the rev A balsa false spar (span grain) and the rev A ailerons.
- LE print split: 5 segments with joints at block centres (y 0 is inside C; ±137.5 in S; ±302.5 in M): lengths 189.5 / 165 / 275 / 165 / 189.5 mm. The 275 mm centre piece fits the H2D (350 mm); all fit the H2D.

### 2.5 Added after the advisor review (before the questions)
- **R6 headroom.** Rev A loaded stall 8.86 m/s with tail download (8.73 wing alone), loaded 1593 g, ρ 1.05 (`wing_lift_performance.txt`). V ∝ sqrt(mass) → R6 (9.0 m/s) allows **Δ ≤ +50.7 g**. Column for §2.3: EPS 15 +39 g → 8.97; EPS 20 +51 g → 9.00 (on the limit); EPS 20 hollow +30 g → 8.94; XPS 30 +75 g → 9.07 (fails); XPS 35 +87 g → 9.10 (fails). Filament (EPS 20, L7): LW-PLA +44 g → 8.98; PETG +77 g → 9.07 (fails).
- **Centre sheeting (D-008 asks for it).** Band contact on top, n = 6: 85 N over ≈ 4 × 6 × 200 mm = 4800 mm² → 18 kPa (EPS 20 strength ≈ 100 kPa, margin ≈ 5). Saddle on the bottom: 60 N preload *(interp.)* on 2000 mm² → 30 kPa = about the long-term creep limit of EPS 20 (≈ 30 % of strength *(interp.)*); hard landing 10 g × 1.44 kg on the saddle → 70 kPa, near EPS 15/20 strength. View: keep the **bottom** centre sheeting (2.6 g), remove the top aft sheeting. Tier 1 (departs from D-008) → ask.
- **Printed TE in the aileron bays.** The user's concept has a printed TE that joins the blocks. In the aileron bays that part is the false spar. Ask: printed hinge spar or rev A balsa false spar.
- **Facts to ask first:** ASA Aero is not in the workshop list (LW-PLA, PETG). Foam on hand is not known.
- **Film flattening.** Besides the pressure pillow, film shrink over a 108 × 125 mm unsupported panel pulls the surface flat between plates (camber loss aft of the spar). This adds to the half-rib case.
- **False spar grain (rev A follow-up, not fixed here).** The 54 mm column uses span-grain E 2500. Rev A specifies vertical grain; with E_T ≈ 38 MPa the rev A false spar bows ≈ 20 mm under q = 0.3 N/mm even at 53 mm. Probably a wording error (a 984 mm one-piece spar from 1000 mm stock has span grain). Listed as a rev A follow-up.
- **Plate outline = hot-wire template:** stepped — inner outline (1.5 mm inset) forward of x 80 (under the D-box), outer outline aft. Key check.
- **Film on bare foam:** the iron (110–120 °C) melts EPS/XPS (soften ≈ 75–90 °C *(interp.)*). Film bonds only to balsa and printed parts (plates, D-box, LE, TE, half ribs); over foam it is not ironed; shrink with low heat.
- **Servo frame tabs** seat on the rev A cap strips at ribs 110/165 (z = lower surface + 1.5 + 0.2). Rev B has no cap strips there: the tabs seat on foam/plate. Recheck in stage 2.

## 3. User's answers (2026-11-22)
Round 1:
- Foam: **XPS 30 solid** (Claude's view was EPS 20 solid).
- LE/TE filament: **"normal PLA for now but can buy later"** (Claude's view ASA Aero). PLA HDT 57 °C: fails the 60 °C sun check by 3 °C. Recorded as user choice with that risk; the mass table also shows ASA Aero and LW-PLA.
- Blocks: "recommended" → 7 blocks (L7).
- Bay ribs: "recommended" → half ribs at y 220 and 385.
Round 2 (after Claude reported: XPS 30 solid + PLA = +100 g, stall 9.13 m/s, fails R6; ASA Aero 9.07 m/s also fails):
- **Hollow all XPS blocks** (option text: "about 45 % removed, 10 mm walls").
- Hinge spar: "recommended" → rev A balsa false spar (span-wise grain) in the aileron bays; printed TE only in the fixed bays.
- Plates: "recommended" → 1.5 mm light balsa with holes; with hollow blocks the holes are the cavity templates.
- Centre skin: "recommended" → keep the bottom centre sheeting, remove the top.

## 4. Correction after the answers (tier 2, Claude)
- **Foam wall thickness.** The option text "45 % removed, 10 mm walls" was wrong: 10 mm walls remove only 25–29 % (fwd piece 25 %, aft piece 29 %). 45 % needs ≈ 7 mm walls (6 mm: 51 / 55 %; 8 mm: 38 / 42 %). Used: **7 mm walls** (keeps the mass the user chose on). Vertical offset from the surface, cavity ends 7 mm from each piece face, cavity ends where its height < 4 mm.

## 5. Stage 1 — structure (build_stage1.py)
- Built: 7 blocks (17 foam pieces), 14 plates, 4 half ribs + caps, D-box, bottom centre sheeting, spar, webs (7 bays), false spar, LE ×5 + 14 keys + 4 joiners, TE centre + 2 tips, ring caps.
- Checks: span 990.00, chord 280.01 (XMin −0.006), depth at 75.6 39.20, 134 solids valid, 0 overlaps > 1 mm³. Cavity fraction front 0.442, aft 0.486, aft centre 0.461. LE key centre z 2.87.
- Mass stage 1: 227.2 g (PLA 69.9, XPS 46.7). Problem: 20 g above the pre-model estimate (TE 26.1 g at x 250–280 against 18 g; glue +6; keys 3.2; bottom sheeting kept). No geometry change; reported.
- Pictures: `design/cad_revB/img/stage1_*.png`.

## 6. Stage 2 — aileron and servo (build_stageB.py + pocket)
- Rev A stage B unchanged; pocket x 108–158, y 111.5–164, top z 10.76.
- Checks: servo nearest: hatch lugs 0.30 (mount, as rev A), frame 1.06, hatch plate 1.34, foam 1.50, plate 110 6.5 mm. Arm ±35°: 1.00 mm. Aileron ±20°: 0 mm³, min gap 0.74 (±20°) / 1.00 (±15°); length 325.00, end gaps 1.00 / 1.00. 168 solids valid, 0 overlaps.
- Tier 2: frame tabs glue only to the plate faces (no cap strip seat) — D-032.
- Mass 247.7 g without servos.

## 7. Stage 3 — outputs (build_stage3.py)
- `Wing_revB.FCStd`, `Wing_revB.step` (86 parts), `stl/` (18 printed parts), `mass_table.md` (+ variants), `lift_revB.txt` (lift script copy with EMPTY = 0.440 + 0.2478: loaded stall 8.98 / 9.11 m/s wing alone / with tail download).
- Problem: the FreeCAD MCP add-in (0.1.28) ignores the timeout; the stage 3 call reported a timeout but completed in FreeCAD (files checked).
- Rev A pictures for the bay and y = 200/300 sections were made from a scratch copy of `Wing_revA.FCStd` (closed without saving).
- Rev A integrity: SHA-1 of all 80 files in `design/cad/` equal before and after.

## 8. Corrections after the advisor review (2026-11-22)
- **Skin buckling width.** The rev A study panel is 53 × 75 mm: 53 mm is the rib bay, 75 mm is the chord-wise width (x 6–80). Recalculated with b = 75 mm: rev A (L 53) 1.21 + 0.25 curvature = 1.46 MPa (study 1.56); rev B bay L 108.5: D11 (75/108.5)² = 228, + 2 D3 74.8, + D22 term 15.3 → N 0.558 N/mm → 0.37 + 0.25 = **0.62 MPa** against 0.45 MPa applied at y = 165 → **margin 1.4** *(interp.)*. Bay 56–110: margin ≈ 1.8. Still > 1.0: D-027 (half ribs aft only) holds.
- **Wire hole.** Plate 110 Ø8 hole at mid-depth (z 10.88) was above the pocket roof (z 10.76): the plug could not pass. Lowered to z 5.0 (`WIRE_HOLE_Z_B`), inside the pocket. Tier 2.
- **Hinge slots.** Hinges at y 130 and 302.5 reach x 200–205 inside blocks S and M (80 mm³ each). Slots now cut in the foam (`build_stageB.py`). Glue these 4 hinges with epoxy or foam-safe CA. Tier 2.
- **Wall thickness.** The 7 mm wall is a vertical offset. Measured normal walls: 6.87 mm aft, 5.52 mm at the nose of the front piece, 4.0 mm between the LE joiner groove and the front cavity. Key check 6 changed to these values.
- **Round-2 answers** "recommended" on options with no label: recorded as **delegated to Claude** (D-029, D-030, D-031), not as the user's own choice.
