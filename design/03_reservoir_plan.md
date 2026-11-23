# 03 — Water reservoir and release mechanism: modelling plan (rev A)

Status: **approved, gate 3 passed 2026-11-22; built as rev A.2 and **accepted by the user 2026-11-22 for the test prints** — see §14 (as built) and §13 (fuselage interface); §12 replaces §11.3** (user: "Yes, start the model"). Decisions D-039…D-046 decided by the user, see §7 and DECISIONS.md. Bottle not measured: estimates in use.
Decisions in force: D-033 reservoir first, D-034 V2 pin-latched trapdoor, D-035 1 L Bisleri bottle, D-036/D-037 H3 horizontal bottle (outlet bulkhead at the bottom on the CG station, fill through the neck cap, vent at the forward top end), D-038 no hole in the wing.
Calculations: `design/calc/reservoir_cad_calc.py` (residual water, drain time, flange insertion, servo chain). Notebook: `design/logs/reservoir_log.md`; the CAD notebook will be `design/logs/reservoir_cad_log.md`.

## 1. Global frame

- Frame of the brief and the wing: origin at the wing LE on the centreline, X aft, Y to the right wing, Z up.
- The **fuselage datum is horizontal** in this model. The wing sits at +3° incidence on it (wing plan §1), so the wing underside in this frame is Z ≈ −13 mm from X 60 to 260 (calculated from `sd7062.dat`, sheeting included).
- The bottle axis is parallel to the datum: the bottle is level at the release attitude (fuselage about 0°, D-037).

## 2. One place for the bottle numbers *(interp. until measured)*

All bottle values live in one parameter file, `design/cad_reservoir/scripts/res_params.py`. The calc script uses the same values. When the user measures the bottle, only this file changes and the full model rebuilds.

| Parameter | Value used | Source |
|---|---|---|
| Body outer diameter | 80.0 mm (inner 79.4) | interp. (concept page) |
| Length, base to neck lip | 255 mm | interp. |
| Cylinder, from the base | yu 6 to 185 mm | interp. |
| Shoulder | yu 185 to 228 (cone to Ø25) | interp. |
| Neck bore | 21.0 mm | interp. (PCO 1881 is 21.7; Bisleri not known) |
| Neck thread OD / pitch | 25 mm / 3 mm *(placeholder, the fill cap is the original cap)* | interp. |
| Brim volume | about 1032 to 1040 mL | interp. |
| PET wall at the outlet band | 0.3 mm | interp. |
| Bottle mass | 22 g | interp. (weigh) |
| Ribs / grip panels | none modelled | **to measure**: the outlet must sit on a smooth band |

## 3. Positions in the frame (derived from §2)

| Item | Value | Note |
|---|---|---|
| Water centroid | X = 80.0, Y = 0 | interp.; the fuselage stage sets the final CG |
| Bottle base / neck lip | X = −23.7 / 231.3 | centroid is 103.7 mm from the base |
| Cylinder | X = −17.7 to 161.3 | |
| Bottle axis | Y = 0, **Z = −60** | top of the bottle Z −20: 7 mm under the wing underside (−13) for the strap and the fuselage top structure |
| Air bubble (996 mL) | 6 mm deep, ±22 mm wide at the top | |
| Outlet | X = 80 (on the centroid), bottom, Ø14 bore | moves if the smooth band is elsewhere |
| V2 seat face | Z ≈ −107 | stack: PET −100, outer gasket 1.0, base plate 6.0 |
| Belly skin (flap flush) | Z ≈ −111 | fuselage depth belly to wing ≈ 98 mm (concept 125 mm) |
| Vent | X ≈ −8, top of the cylinder | the LE is at X = 0; vent parts must stay ahead of X ≈ −2 above Z −13 |
| Release servo (if S1) | lower right corner, X ≈ 45 to 70, Y +40 to +52 | fuselage part, not reservoir |

## 4. Parts

| # | Part | Material | Belongs to | Build method |
|---|---|---|---|---|
| P1 | Bottle (reference body, shell 0.3 mm) | PET | reservoir | revolve of the §2 profile |
| P2 | Outlet inner flange with stem | PETG | reservoir | oval saddle flange + stem, M17×1 thread (cosmetic) |
| P3 | Outlet outer gasket (saddle) | silicone or EVA sheet 1.5 mm | reservoir | cut from sheet |
| P4 | V2 base plate: saddle top, nut pocket, seat face, hinge knuckles, latch lugs | PETG | reservoir | one printed part |
| P5 | Outlet nut | PETG | reservoir | |
| P6 | Flap with hook and knuckle | PETG | reservoir | |
| P7 | Flap gasket | silicone or EVA 1.5 mm | reservoir | |
| P8 | Hinge pin Ø1.5, flap kick spring | steel | reservoir | bought |
| P9 | Release pin Ø2 with eye and stop | steel (spoke or piano wire) | reservoir (captive) | |
| P10 | Safety pin with red flag | steel + tape | reservoir | |
| P11 | Vent fitting (form per D-043) | PETG + bought valve | reservoir | |
| P12 | Saddles × 2 (cylinder and shoulder), front stop | PETG / balsa | fuselage | |
| P13 | Straps × 2 | 20 mm hook-and-loop | fuselage | |
| P14 | MG90S, arm, pull link, quick-release snap | bought | fuselage (snap on the pin eye) | placeholder MG90S as in the wing |

## 5. Main design results already calculated (before modelling)

1. **Outlet seal stack (tightest constraint).** The inner flange must go in through the neck (bore about 21 mm). A round flange Ø20.5 with a stem Ø16.4 × 9 mm needs a Ø21.5 mm hole: **it does not fit**. An **oval flange inserted end-on** (34 × 18.5 mm, long axis along the neck) with a **short stem Ø17 × 7.3 mm** needs Ø19.6 to 19.8 mm: it fits with 0.5 mm clearance. The stem length is set by the stack: PET 0.3 + gasket 1.0 + base plate 6.0.
2. **Seal land.** The inner land is only about 0.7 mm at the sides of the oval (9 mm at the ends). Thus the **main seal is the outer gasket**, under the large outer saddle of the base plate (gasket 30 × 34 mm). The water pressure pushes the PET wall out onto this gasket, so the seal gets tighter as the pressure increases. The inner flange only clamps. Neutral-cure silicone is a second seal (D-036).
3. **Lip height and residual water.** The concept had a flange plus an inner washer (about 2.7 mm high). Calculated residual (g) at the release:

| Lip height | 0° | 1° | 2° | 3° | 5° |
|---|---|---|---|---|---|
| 2.7 mm (concept stack) | 9.5 | 9.3 | 10.2 | 12.4 | 18.4 |
| 1.5 mm | 3.9 | 4.0 | 5.6 | 7.7 | 13.3 |
| **1.2 mm (plan)** | **2.8** | **3.1** | **4.7** | **6.8** | 12.2 |
| 0 (ideal) | 0 | 0.7 | 1.9 | 3.7 | 8.3 |

   The concept stack fails the D-037 condition (< 10 g at 0 to 3°). Plan: no inner washer, flange 1.2 mm with a 0.4 mm feathered rim. Above about 3° nose-up the pitch, not the lip, sets the residual.
4. **"No step at the outlet lip"** means: (a) the flange rim is ≤ 0.5 mm high and ramps (≤ 30°) to the 1.2 mm top; (b) the flow area never gets smaller downstream: bore Ø14 in the stem, nut pocket Ø ≥ 17, flap seat Ø ≥ 14; (c) the stem end is flush with or above the seat face, so there is no pocket under the lip.
5. **Installation and alignment.** Pass a string in through the outlet hole and out through the neck. Tie it to the flange, then pull the flange down the neck and into the hole. The oval saddle sits in the curved wall and cannot turn. Two flats on the stem key the base plate, so the hinge line is square to the bottle axis without a measurement. The round nut turns freely.
6. **Drain time** (vented, Cd 0.6, Ø14): 11.5 s level, 11.4 s at 3°. Ø16 gives 8.8 s but its stem does not pass the neck. This **conflicts with R16** (4 to 8 s): see D-045.
7. **Servo chain.** MG90S (0.177 N·m at 4.8 V), 10 mm arm, 90° throw: pin travel 14.1 mm, allowed pull 8.8 N (50 % margin, D-034). Power-up twitch 15° *(interp.)* = 2.6 mm. Pin engagement ≥ 6 mm (more than 2 × twitch). Pull estimate: gasket preload 8 N *(interp.)* + water 0.2 N (1 g), lever 0.5, μ 0.3 on hook and 2 lugs → about 2.5 N. Margin to 8.8 N: 3.5 ×.
8. **Water force on the flap:** 0.18 N at 1 g, 1.8 N at 10 g. The landing load goes into the pin (shear) and the hinge, not the servo.

## 6. Mass estimate (without the servo; no fixed limit since D-047, was R17 ≤ 50 g)

| Item | g |
|---|---|
| Bottle (weigh) | 22.0 |
| Inner flange 1.0, outer gasket 0.5, base plate 4.0, nut 0.8 | 6.3 |
| Flap 2.0, flap gasket 0.4, hinge pin 0.3, spring 0.2 | 2.9 |
| Release pin 0.4, safety pin with flag 0.8 | 1.2 |
| Vent fitting (D-043 option B) | 2.5 |
| Saddles 2 × 3.5, straps 2 × 1.5 | 10.0 |
| Sealant | 0.5 |
| **Total** | **45.4** (margin 4.6 g) |

The bottle is half of the budget. If it weighs more than about 26 g, the margin is gone.

## 7. Decision points (tier 1 = I stop and ask; tier 2 = I decide and report)

| ID | Decision | Tier | Options | My recommendation and reason |
|---|---|---|---|---|
| D-039 | CAD tool — **user: FreeCAD only** | 1 | (a) FreeCAD now, Fusion 360 later for the final printed parts; (b) Fusion 360 now; (c) FreeCAD only | (a). The wing is in FreeCAD, the bottle is not measured, and the parts are test prints that need many checks. Fusion is not open now (the bridge heartbeat is old). After the bench tests pass, rebuild the printed parts in Fusion for the team. |
| D-040 | Flap hinge side | 1 (changes D-034) | (a) front hinge (D-034); (b) rear hinge, latch at the front | (b). A front-hinged flap that hangs in the airflow is pushed back toward **closed** (it trails like a flag). A rear-hinged flap trails flat behind the outlet: the airflow holds it open and it is out of the stream. The landing load path does not change. |
| D-041 | Release servo position | 1 | S1 lower right corner beside the valve; S2 nose bay ahead of the bottle with a 100 mm pull wire in a tube | S1. Short direct link, less slack. Cost: fuselage 110 mm wide at the valve (about +2 g of fuselage). S2 keeps the fuselage about 92 mm wide but takes nose space from the battery. |
| D-042 | Outlet inner flange form | 1 | F1 oval saddle flange, short stem, outer gasket seal (§5.1–5.5); F2 round flange (does not pass the neck); F3 rubber grommet, no rigid flange | F1. It is the only form that passes a 21 mm neck with a Ø14 bore. Final sizes after the neck is measured. |
| D-043 | Vent | 1 | A: plug lifted by a line from the release pin (concept); B: passive one-way vent (aquarium air check valve, about ₹30, about 1 g) in a small top bulkhead; C: no vent, if the drain test passes without one | B. No line around the bottle, no extra pull force or travel. It lets air in when the water runs out and shuts when the inside pressure is higher (heat, squeeze, landing, slosh). Risks: crack pressure too high (slow drain), weep at low pressure. The bench test decides; A is the fallback. |
| D-044 | Safety pin | 1 | SP1: second pin through the latch lugs and hook from the left side, red flag; SP2: clip that stops the release pin from sliding | SP1. The flap stays latched even if the servo pulls. It also holds the valve shut out of the aircraft (weigh-in, transport). Keep it in for the qualifier; remove it before the main-round launch. |
| D-045 | Brief R13, R15, R16 | 1 (brief change) | R16 now: drain 4 to 8 s, outlet lowest at −2 to +5° | Change R16 to: drain ≤ 15 s (Q7 open), residual < 10 g at 0 to 3° pitch, the pilot releases near level. R13 "neck down" → "horizontal (H3)". R15 "cap unit" → "bulkhead unit". |
| D-046 | Fuselage interface and removal | 1 | Removal up through the top with the wing off, or a side or belly hatch | Top, wing off (rubber bands). Front stop at X −25 takes the 98 N nose-in load; saddle 1 at X ≈ 15, saddle 2 (cone) at the shoulder X ≈ 165 to 185 takes the launch load aft; 2 straps; floor hole with 3 mm clearance round the V2 so that no load goes into the valve. Servo link: fishing snap on the pin eye. |
| — | Weigh-in set | (rule, Q8) | | On the scale: bottle, outlet unit, flap, release pin (captive), safety pin, vent. In the aircraft: saddles, straps, servo, arm, link with snap. Same set before and after. |
| T2 | Wall thicknesses, clearances (0.3 mm sliding, 0.2 mm press), thread form (printed or heat-set), print orientation, spring form, gasket material | 2 | | decide by rule, report in the next update |

## 8. Build stages (after gate 3; execution by a Sonnet subagent, checks by me)

| Stage | Content | Update |
|---|---|---|
| R-A | Parameter file, bottle body, water volume, frame check against the wing | picture + volume, centroid |
| R-B | Outlet unit: inner flange, gasket, base plate, nut, flap, gasket, hinge, release pin, safety pin | picture + section + insertion check |
| R-C | Vent fitting (per D-043) | picture + clearance to the LE |
| R-D | Saddles, front stop, straps, servo, arm, link (per D-041, D-046) | picture + width check |
| R-E | Checks, mass table, exports (FCStd, STEP, STL of each printed part), iso and half-section pictures, bench-test sheet | review with the user |

The model uses Part-workbench Python in one named document `Reservoir_revA`, saved at `design/cad_reservoir/Reservoir_revA.FCStd`, with scripts in `design/cad_reservoir/scripts/` (same pattern as the wing: `run_all.py` rebuilds everything). Threads are cosmetic (plain cylinders) in the model; the printed thread is drawn only on the STL parts if the test needs it *(T2)*.

## 9. Key checks (builder and verifier test these numbers)

1. Inner flange end-on insertion profile: enclosing diameter ≤ neck bore − 0.5 mm (now 20.5 mm).
2. Outlet bore ≥ 14.0 mm everywhere from the flange top to the seat; no smaller section downstream.
3. Lip: rim ≤ 0.5 mm, top ≤ 1.2 mm above the inner wall; residual ≤ 10 g at 0 to 3° (from the calc with the modelled lip).
4. Flap clear of the stream when open: no flap part inside the Ø14 bore projected down to 60 mm below the seat, at an open angle ≥ 150°.
5. Pin engagement ≥ 6 mm (> 2 × 2.6 mm twitch); pin travel needed ≤ 14 mm (10 mm arm).
6. Vent parts ahead of X = −2 for every point above Z = −13, and ≥ 3 mm from the wing in any position.
7. Bottle, valve, vent, saddles and straps inside Y = ±55 (110 mm) at the wing saddle; servo S1 inside Y ±52 (inner wall).
8. Reservoir mass (printed parts by volume × PETG 1.27 g/cm³ at the planned infill, bought parts by catalogue, bottle 22 g) without the servo: report the total; no fixed limit (D-047).
9. All solids `isValid()`; no overlap except at contact faces; the bottle top is ≥ 5 mm under the wing underside.
10. Water centroid at X = 80 ± 1 mm with 996 g.

## 10. Open items for the user

- **Bottle measurements** (one Bisleri 1 L): mass; brim volume (fill to the brim, weigh the water; the estimated profile gives only 1012 mL, so 12 mL of air above 1000 mL); body outer diameter; length base to neck lip; length of the straight cylinder; neck thread outer diameter; neck bore (inner diameter at the top); thread pitch; positions and depth of any ribs or grip panels, and the width of the smooth band near mid-length; one side photo with a ruler.
- Answers to D-039 to D-046.

## 11. Detailed geometry for the build (after gate 3, 2026-11-22)

User decisions: D-039 FreeCAD only, D-040 rear hinge, D-041 servo S1, D-042 oval saddle flange, D-043 passive vent, D-044 second safety pin, D-045 brief change, D-046 top removal. All values in the §1 frame (mm). *(interp.)* = estimate; (T2) = builder may adjust within the stated limit and must report it.

### 11.1 Bottle (P1) and water
- Outer radius profile `[[0,36],[6,40],[185,40],[228,12.5],[235,10.8],[255,10.8]]` (yu from the base), revolved about the X axis, base at X = −23.7, neck aft. Inner = outer − 0.3 mm. Punt: base dome 6 mm high, R30 (as the concept page). Neck finish: plain tube Ø25 OD from yu 233 to 255 with a support ring Ø32 × 2 at yu 231 *(interp.)*; original cap Ø29.6 × 16 on the neck.
- Bottle axis Y = 0, Z = −60.
- Water: 996 g (1000 mL) solid inside the bottle, free surface horizontal at the level that gives 1000 mL; report the centroid X (target 80 ± 1; if not, move the bottle in X so it is 80 and report the base X).
- Holes in the bottle: outlet Ø17.3 at X = 80 bottom; vent Ø8.3 at X = −7.7 top.

### 11.2 Outlet unit (P2 to P10), centred at X = 80, Y = 0
| Part | Geometry |
|---|---|
| P2 inner flange | Obround (stadium) planform 34 (X) × 18.5 (Y). Underside = cylinder R 39.7 about the bottle axis (sits on the inner wall). Top = cylinder R 38.5 (1.2 mm thick). Rim: top edge chamfer from 1.2 down to 0.4 mm over 1.5 mm (≤ 30°). Bore Ø14.0 through. Stem Ø17.0 OD, from the underside down to Z = −107.0 (seat face), bore Ø14.0. Thread M17×1 cosmetic (plain cylinder). No flats: the saddle shape aligns it (T2 change from §5.5). |
| P3 outer gasket | Saddle ring OD 30, ID 17.3, 1.0 mm (compressed 1.5 mm sheet), between the PET outer surface (R 40) and the plate (R 41). |
| P4 base plate | Saddle top = cylinder R 41.0 about the bottle axis; round body Ø32 from the saddle down to the flat seat face at Z = −107.0. Centre hole Ø17.4. Nut pocket from below Ø23.0 × 3.5 deep. Front latch lugs: 2 lugs Y = −9…−4 and +4…+9, X = 51…61, hanging from the seat face down to Z = −113.5, holes Ø2.1 at (X 58, Z −110.0) for the release pin and (X 54, Z −110.0) for the safety pin. Rear hinge knuckles: 2 fixed knuckles Y = −10…−4 and +4…+10, Ø5 about the hinge axis X = 100, Z = −111.0, joined to the plate; hinge pin hole Ø1.6. Plate stays inside Y ±17. Wall/rib lightening (T2) to meet ≈ 3.5 g. |
| P5 nut | Ø22 OD, M17×1 (cosmetic: ID 17.0), 3.2 thick, in the pocket, bottom face 0.3 above the seat face. |
| P6 flap | Disc Ø34 × 2.5 centred X 80, under the gasket: Z −108.5…−111.0. Front hook tab X 51.5…66, Y −3.3…+3.3, down to Z −113.0, holes Ø2.1 at the two pin positions. Rear knuckle Y −3.6…+3.6, Ø5 on the hinge axis, joined to the disc. Closed state shown. |
| P7 flap gasket | Full disc Ø32 × 1.5 on the flap top, Z −107.0…−108.5 (shown uncompressed, touching the seat face). |
| P8 hinge pin | Ø1.5 steel, Y −10…+10 on the hinge axis. Kick spring: not modelled (bought torsion spring or a small elastic, T2), list it in the mass table at 0.2 g. |
| P9 release pin | Ø2.0 steel along Y at (X 58, Z −110): tip at Y −6.0 (2 mm into the left lug), straight to Y +15, eye Ø6 ring at Y +15…+21 in the XY plane. Engagement to free the hook = tip −6.0 → +3.5 = 9.5 mm. |
| P10 safety pin | Ø2.0 steel along Y at (X 54, Z −110) from the left: tip at Y +9 (through both lugs), straight to Y −14, ring Ø8 at Y −14…−22, red flag 40 × 20 × 0.2 tape at the ring. |
- Open state (separate copy for the pictures and check 4): flap, gasket and P6 rotated 160° about the hinge axis (front edge down and aft); pins retracted 12 mm (+Y for P9).
- Belly skin reference (not a part): plane Z = −111.0, 1.5 mm thick, for the pictures only.

### 11.3 Vent unit (P11), at X = −7.7, top (Z = −20)
- Inner flange: round Ø18 × 1.2, underside = cylinder R 39.7 (inside the top wall), stem Ø8 OD / Ø4 bore up to Z = −14.5. Outer gasket Ø18 × 1.0 saddle. Nut Ø14 × 3 (cosmetic M8×1).
- Check valve placeholder (aquarium air check valve *(interp.: body Ø11 × 26 mm, barbs Ø4.5 × 8 at each end)*): a printed elbow on the stem turns forward; the valve axis along X at Z = −10, from X −12 forward to X −46. Air goes in from the forward end.
- Rule: every vent part above Z = −13 must be at X ≤ −2 (check 6).

### 11.4 Mount (P12, P13) — fuselage parts
- Saddle 1 at X = 8…20, saddle 2 at X = 160…172 (cone side: follow the shoulder profile so it bears on the shoulder, aft stop). Each saddle: PETG, 12 mm wide in X, inner face = bottle outer + 0.5 mm (foam tape), wraps the lower 120° of the bottle, wall 2 mm, flat foot on the floor plane Z = −109.5, outer width ≤ Y ±50.
- Front stop: 3 mm balsa plate in the YZ plane at X = −27.2…−24.2 with a Ø50 hole (bears on the base rim), outline Y ±50, Z −105…−25.
- Straps: 20 mm wide × 1 mm hook-and-loop band round the bottle top at each saddle, ends at the saddle feet.
- Floor reference plane Z = −109.5 (inner) with a hole round the V2: 3 mm clearance round P4 and P6 closed (pictures only).

### 11.5 Release servo (P14) — fuselage part, S1
- MG90S placeholder from the wing scripts (`design/cad/scripts/`), lying flat with the shaft along X, under the lower right curve of the bottle, case inside Y ≤ 52 and Z ≥ −109.5, ≥ 2 mm from the bottle, straps, saddles and the outlet unit (T2: choose the exact position and orientation; stop and report if no position meets these limits).
- Arm 10 mm radius, swings ±45° about the shaft; at the closed position the arm points so that a +45° turn pulls the pin eye +Y by ≥ 12 mm (9.5 engagement + 2.5 slack). Link: Ø0.8 steel wire from the arm tip to a fishing snap on the pin eye, length ≥ 10 mm.

### 11.6 Pictures and exports (stage R-E)
- Colours: PET clear-light blue (transparency 70), water blue (transparency 50), PETG light grey, moving parts red, gaskets black, steel blue-grey, servo dark grey, saddles green, balsa tan.
- Pictures (1600 × 1200, white background, `fitAll`): iso closed; iso open; half-section at Y = 0 (whole reservoir); outlet close-up section at Y = 0; outlet close-up section at X = 80; vent close-up; top view with the 110 mm limit lines and the wing LE line.
- Exports: `Reservoir_revA.FCStd`, `Reservoir_revA.step` (assembly, closed), STL of each printed part (P2, P4, P5, P6, vent flange, vent nut, vent elbow, saddle 1, saddle 2) in the print orientation, `mass_table.md/.csv`, `check_report.txt`.
- Mass rule: printed parts thicker than 4 mm: volume × 1.27 g/cm³ × 0.45 (2 walls, 15 % infill, interp.); thinner parts: volume × 1.27. Bought parts: catalogue or estimate, marked.

## 12. Rev A.1 — in-place fill (D-049, D-050), 2026-11-22. Replaces §11.3.

Reason: the user wants the reservoir filled in the aircraft; the rev A vent valve stuck out 28 mm past the bottle base (bottle could not stand). The separate vent (old P11a–e, hole Ø8.3 at X −7.7) is removed. One top fitting = fill port + vent.

### 12.1 Fill unit P11, top centre, X_c = −11.0 (interp.: depends on where the straight cylinder starts; keep the flange on the cylinder), Y = 0
| Part | Geometry |
|---|---|
| Hole in the PET | Ø13.3 at X −11, top |
| P11a fill flange (inside, PETG) | Round Ø16.5 × 1.2; its top face follows the inner wall (cylinder R 39.7 about the bottle axis) and sits on it from below; bore Ø10.0; stem Ø13.0 OD / Ø10.0 bore from the flange up to Z −9.5 (cosmetic thread M13×1 on the stem above the nut). Rim: chamfer 1.2 → 0.4 over 1.5 mm on the water side. |
| P11b outer gasket (silicone) | Saddle ring OD 20, ID 13.3, 1.0 thick, Z −20.0…−19.0 at the centre |
| P11c nut (PETG) | Ø18 × 2.5, saddle underside R 41.0 about the bottle axis, ID 13.0; top flat at Z −16.5 |
| P11d cap (PETG) | Ø18 OD, internal ID 13.0 (cosmetic thread), from Z −16.0 to −7.0, top wall 1.5 mm (Z −8.5…−7.0) with 6 vent holes Ø1.5 on a Ø6 circle and a Ø1.5 centre hole; 12 knurl flutes on the outside (T2) |
| P11e cap seal (silicone ring) | ID 10, OD 13, 1.0 thick, under the cap top wall (Z −9.5…−8.5), pressed by the stem top end |
| P11f vent flap (silicone umbrella) | Disc Ø8.5 × 0.8 under the cap top wall inside the seal ring (Z −9.3…−8.5) covering the 6 holes, with a stem Ø1.5 up through the centre hole and a retaining knob Ø3 × 1 above the cap top |
| Fuselage fill hole (reference, not a part) | Ø25 in the fuselage top at X −11 |
| P15 funnel (ground support, not on the aircraft, not in the mass) | Cone Ø70 top, 50 high, wall 1.2, spout Ø7 OD × 25 long with 2 external ribs 1 mm so air can leave through the Ø10 bore; STL only |

### 12.2 Checks for rev A.1 (add to §9)
- Fill flange end-on insertion circle ≤ 20.5 (estimate Ø19.2).
- Every fill-unit part above Z −13 at X ≤ −2; ≥ 3 mm from the wing reference.
- The fill flange sits fully on the straight cylinder (front edge X ≥ start of the cylinder).
- The bottle stands upright on its base on a flat plane with no part below the base plane (the outlet unit is on the side).
- Capacity: water that can be poured with the aircraft level = interior volume above the fill-flange lip level excluded; report the air trapped above the lip and the max fill (must be ≥ 1000 mL).
- Mass table and total updated; old vent parts removed from the model, the STL folder and the pictures.

## 13. Interface for the fuselage stage (output of D-033), as built rev A.2
| Item | Value (frame §1) |
|---|---|
| Wing seat / fuselage top under the wing | Z ≈ −13 (wing underside at +3° incidence); bottle top Z −20, strap 1 mm |
| Belly outer skin (D-051) | Z −117.0, 1.5 mm; floor inner Z −115.5; fuselage depth belly to wing ≈ 104 mm |
| Belly opening | X 47 to 115, Y ±20 (flap opens to 156°; an aft edge at X 120 gives about 163°) |
| Ground clearance of the valve | lowest valve parts Z −113.5: 3.5 mm above the skin outer face (check 11) |
| Release servo S1 (T2-30, T2-31) | MG90S upright, shaft down, in the lower right corner; case Y 38.8 to 51.0, Z −111.9 to −80.4; arm R 9 in the pin plane Z −110.5; side wall inner face ≥ Y 53.5 at X 50 to 90 |
| Fuselage width | ≤ 110 mm at the wing saddle; reservoir parts inside Y ±55 |
| Front stop (former) | X −27.2 to −24.2, Z −111 to −25, bears on the bottle base rim; takes the 98 N nose-in load |
| Saddles | X 8…20 and 160…172, feet on the floor Z −115.5; 2 straps |
| Fill port access | hole in the fuselage top at X −11 (Ø25 in the model reaches X +1.5: make it Ø22, or offset it 2 mm forward); fuselage top ahead of the LE must clear the cap top Z −7  **— Fuselage stage (D-056, 2026-11-22): no hole; the magnet nose hatch (X −200…−2) lifts off and the cap is turned by hand.** |
| Safety-pin flag | through a hole in the left side wall at X 54, Z −110.5 |
| Removal | up through the top with the wing off (weigh-in) |
| Water centroid | X 80.0 (interp.; the fuselage stage sets the final CG and can move the bottle in X; the outlet and fill port move with it) |

## 14. As built — rev A.2 (2026-11-22)
Model `design/cad_reservoir/Reservoir_revA.FCStd` (rebuild `scripts/run_all.py`; all values in `scripts/res_params.py`). These values differ from §3, §4, §9 and §11; where they differ, this table is in force.

| Item | Plan | As built | Decision |
|---|---|---|---|
| Bottle base | X −23.7 | X −25.72 (water centroid exactly X 80.000) | T2 (notebook §6) |
| Bottle interior | 1032 to 1040 mL (estimate) | 1012 mL from the outer-radius profile − 0.3 mm wall and the punt; max fill 1008 mL level. The real brim volume replaces it (measure) | T2-5 |
| Vent | separate top vent at X −7.7 (§3, §4 P11, §9 check 6, §11.3) | removed; fill port Ø10 at X −11 with the vent flap in the cap (§12) | D-049, D-050 |
| Fill gasket | OD 20 | OD 18 (overhang on the base heel 0.28 mm) | T2 (notebook §10) |
| Flap P6 | 2.5 mm solid, 2.0 g | 1.2 mm skin + pocket grid, 2.60 g; Z −109.0 to −111.5 | T2 (notebook §7) |
| Flap gasket P7 | silicone Ø32 × 1.5 | EVA foam 2.0 mm, 0.16 g | T2 (notebook §7) |
| Pins | Z −110 | Z −110.5 | T2 (notebook §7) |
| Belly | Z −111 | Z −117 (valve recessed 3.5 mm) | D-051 |
| Open state | 160° | 150° shown; max 156° | T2 (notebook §10) |
| Release servo | flat, shaft along X, R 10 arm, wire 73° off the pin axis at closed | upright, shaft down, R 9 arm in the pin plane, wire along the pin axis | T2-30, T2-31 |
| Mass (no limit since D-047) | 45.4 g estimate | 47.5 g without the servo and the balsa stop (see `mass_table.md`) | — |
