# Wing rev B (foam-block construction) — modelling plan

Status: plan, 2026-11-22. Decisions: D-024 (user: model option B and compare), D-025 … D-032 (this plan).
Rev A (`design/cad/`) is the reference and is **not changed**. Rev B scripts: `design/cad_revB/scripts/` (copied from rev A and changed). Outputs: `design/cad_revB/` (`Wing_revB.FCStd`, `Wing_revB.step`, `mass_table.md`, `img/`).
Notebook with all the numbers: `design/logs/wing_revB_log.md`.

## 1. Frame and fixed geometry (same as rev A)
- Origin: wing LE at the centreline. X aft, Y right wing, Z up. Chord line at Z = 0, dihedral 0°.
- Span 990.0 mm (tip faces y = ±495). Chord 280.0 mm. SD7062 × 280 (`design/aero/airfoil_coords/sd7062.dat`).
- Outer outline OUT; inner outline IN = OUT inset 1.5 mm (rev A `wing_geom.py`).
- Reused from rev A without change: D-box sheeting (x 6–80, 1.5 mm, y ±492), spar caps (carbon 0.5 × 6 + hard balsa 3 × 6 at x 72.6–78.6), false spar (x 205–208, full span; **span-wise grain**), shear webs (front x 71.1–72.6 full span, rear x 78.6–80.1 at |y| ≤ 164; pieces between the stations that cross the spar), tip ring caps (y 492–495), ailerons (x 210–280, y 112.5–437.5, built-up, hinge x 209, 4 CA hinges), servo installation (MG90S placeholder, PETG frame, 0.8 mm hatch, lugs, arm, horn rib, horn, pushrod), band rub plates.

## 2. What changes

### 2.1 Foam blocks — XPS 30 kg/m³, hollow, 7 mm walls (D-025, D-026)
Each block has a front piece and an aft piece (the spar passes between them); fixed-bay blocks also have a TE piece.

| Block | Foam y (right side; mirrored) | Plates (1.5 mm) | Pieces (x) | Notes |
|---|---|---|---|---|
| C centre | −54.5 … +54.5 (one block) | ±54.5–56 | front 6–71.1 (inner outline); aft 80.1–205; TE 208–250 | Top: outer outline (film on foam). Bottom aft of the D-box: inner outline under the kept bottom centre sheeting. Wire hole Ø10 at x 130, y ±28 through the bottom wall. |
| S servo | 111.5–164 | 110–111.5, 164–165.5 | front 6–71.1; aft 80.1–205 | Servo pocket in the aft piece: x 108–158, full width between plates, from the lower surface up to the servo top + 1.5 mm. No aft cavity (the pocket replaces it). Ø8 wire hole in plate 110 at x 130. |
| M mid | 275.5–329.5 | 274–275.5, 329.5–331 | front 6–71.1; aft 80.1–205 | — |
| T tip | 440–490.5 | 438.5–440, 490.5–492 | front 6–71.1; aft 80.1–205; TE 208–250 | Outer plate 490.5–492 solid (impact face, as rev A D-018). Ring cap 492–495 kept. |

- Hollow bays: 56–110 (54 mm), 165.5–274 (108.5 mm), 331–438.5 (107.5 mm).
- Cavities (D-025): offset 7 mm from the outer surface (8.5 mm where the foam is under 1.5 mm sheeting), ends 7 mm from each piece face (x), cavity cut off where its height < 4 mm. Front cavity ≈ 45 %, aft ≈ 48 % of the piece section. TE pieces are solid (too thin).
- Build note: each cavity is hot-wire cut through a kerf from the spar face of the piece; the shear webs and caps cover the kerf.

### 2.2 Face plates — 1.5 mm light balsa (100 kg/m³) (D-030)
- Outline = hot-wire template: **stepped** — inner outline for x < 80 (under the D-box), outer outline for x ≥ 80 (film on foam); C plates also inner on the bottom aft of the D-box (under the bottom centre sheeting).
- x 6–205 one piece with notches for the spar caps (as rev A ribs). Fixed-bay plates (±54.5–56, 110–111.5, 438.5–440, 490.5–492) also have an aft piece x 208–253: the 3 mm tail (x 250–253) locates in a slot in the printed TE.
- Holes = the cavity outlines of the block (so the plate is also the cavity template). S plates: front cavity hole only + Ø8 wire hole in plate 110. Outer tip plate: no holes.

### 2.3 Half ribs (D-027)
- 1.5 mm light balsa, x 78.6–205, inner outline, at y = ±220 and ±385. Lightening holes at x 98, 130, 160, 186 (rev A rule D-018).
- Cap strips 1.5 × 6 mm light, x 80–205 top and bottom, centred on the half rib.

### 2.4 Printed LE and TE — PLA now, ASA Aero later (D-028)
- LE: rev A LE outline x 0–6, y ±492, in 5 segments with butt joints at y = ±137.75 (S block centre) and ±302.5 (M block centre): lengths 189.5 / 164.75 / 275.5 / 164.75 / 189.5 mm (all fit the H2D 350 mm; the centre piece is too long for the P1S 256 mm).
- LE locator keys (jig features in flight): at each of the 14 plate stations a key x 6–9, z camber ± 2, 12 mm long, centred on the plate, with a 1.6 mm slot for the plate nose. The key sits in a 5 mm groove in the foam front piece. Joiners: key-size bars (x 6–9, z ± 2, 20 mm long) across each LE joint, inside the block groove.
- TE (fixed bays only): x 250–280, outer outline, centre y −111.5…+111.5 (223 mm, fits the P1S) and tips y 438.5–492 (53.5 mm). Slots 1.6 mm wide, 3 mm deep (x 250–253) at the plate tails.
- Print fill for the mass table: LE 0.50 (2 walls + 15 %), keys and joiners 1.0, TE 0.85 (rev A study rule).

### 2.5 Removed from rev A
All ribs (centre, 55, 110, 165 … 439.5, tip ribs), the aft rib pieces, all cap strips except on the half ribs, the balsa LE, the balsa TE wedges, the top centre sheeting. The bottom centre sheeting stays (x 80–205 and 208–250, y ±56), with the Ø10 wire exit (D-031).

## 3. Densities for the mass table
Rev A values (`RHO`): sheet 90, light 100, medium 130, hard 160, carbon 1550, PETG 1270, steel 7850. Added: **XPS 30**, **PLA 1240** (also reported: ASA Aero 700 *(interp.)*, LW-PLA 550 *(interp.)*). Film 50 g/m² on the same area as rev A. Glue: rev A 8 g + 4 g for the foam bonds (D-box to foam, plates, LE, TE) + 2 g spray adhesive for film on foam *(interp.)* = **14 g**.

## 4. Stages (update with a picture after each)
1. **Stage 1 — structure:** blocks, plates, half ribs and caps, D-box, bottom centre sheeting, spar, webs, false spar, printed LE (segments, keys, joiners), printed TE, tip ring caps. Checks 1–4, 6.
2. **Stage 2 — aileron and servo:** rev A stage B (aileron, hinges, servo, frame, hatch, horn, pushrod, rub plates) + the servo pocket. Checks 5, 7.
3. **Stage 3 — outputs:** FCStd, STEP, mass table, pictures (iso, iso without top skins, section y = 140, section y = 300 through block M, bay view), then the comparison.

## 5. Decision points
| Point | Tier |
|---|---|
| Stall speed above 9.0 m/s after the measured mass | 1 — report, user decides |
| Servo pocket or frame tab seat does not give the rev A clearance | 1 |
| Cavity wall, key and slot sizes, joint positions, pocket margins | 2 |
| Names, colours | 3 |

## 6. Key checks
1. Span 990.0 mm; chord 280.0 mm (rub plates excluded); dihedral 0°.
2. All solids `isValid()`; no overlap > 1 mm³ between parts (glue faces touch).
3. Plate outline = stepped template: inner outline at x < 80, outer at x ≥ 80 (C plates: inner on the bottom aft of the D-box); each plate face is flush with the foam face of its block.
4. Hollow-bay lengths 54 / 108.5 / 107.5 mm; half ribs at ±220, ±385; every LE segment ≤ 350 mm; LE joints inside blocks.
5. Aileron at ±20°: no interference, minimum gap ≥ rev A (0.74 mm); aileron length 325.0 mm, end gaps 1.0 mm.
6. Foam cavities: 7 mm vertical offset (8.5 mm under sheeting); measured normal walls ≥ 6.8 mm aft, ≥ 5.5 mm at the nose, 4.0 mm behind the LE joiner grooves; cavity fraction front ≈ 44 %, aft ≈ 49 %.
7. Servo: ≥ 1.00 mm to every part except the mount (as rev A), arm ±35° ≥ 1.00 mm; foam pocket wall ≥ 1.0 mm from the servo, arm and frame.
8. Mass and stall: wing mass without servos; loaded stall at ρ 1.05 with tail download ≤ 9.0 m/s (R6) — expected to fail with PLA (≈ +68 g → 9.05 m/s) and pass with ASA Aero (≈ +43 g → 8.98 m/s).
