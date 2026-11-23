# Engineering notebook: reservoir detailed CAD (rev A)

Stage started 2026-11-22. Process: cad-codesign, all steps. Plan: `design/03_reservoir_plan.md`. Calculations: `design/calc/reservoir_cad_calc.py`.
Decision IDs for this stage start at D-039.

## 1. Inputs read
- `design/logs/reservoir_log.md` §1–12.2, D-033…D-038, brief R13–R18 and Q7–Q9, `design/studies/reservoir_layout.html` (bottle profile `RI`, `buildV2`, `buildBulkhead`, vent `VX = CEN − 16`), `design/studies/release_valves.html` (V2), wing plan and `sd7062.dat`.
- Tool state 2026-11-22: FreeCAD RPC running (addon 0.1.28, server 0.1.32: version warning, RPC healthy). Fusion bridge heartbeat from 2026-11-21, pid 19928 not alive → Fusion is not open.

## 2. Numbers calculated before the interview
- Wing underside in the fuselage-datum frame (incidence +3°): Z ≈ −13 mm from X 60 to 260.
- Bottle (interp. profile): centroid 103.7 mm from the base → base X −23.7, neck lip X 231.3, vent X ≈ −7.7. Bubble with 996 mL: 6 mm deep, ±22 mm.
- Residual water vs lip height and pitch: table in the plan §5.3. Concept stack (2.7 mm) fails < 10 g at 3° (12.4 g). 1.2 mm lip gives 6.8 g at 3°.
- Neck insertion: round Ø20.5 flange + Ø16.4 × 9 stem needs Ø21.5 (no); oval 18.5 minor + Ø17 × 7 stem needs Ø19.6 (yes, 21 mm bore).
- Servo: 10 mm arm → 14.1 mm travel, 8.8 N allowed; 15° twitch 2.6 mm.

## 3. My view before I asked (written before the questions)
| ID | My choice | Reason |
|---|---|---|
| D-039 | FreeCAD now, Fusion for the final printed parts after the tests | wing in FreeCAD; unmeasured bottle; many checks |
| D-040 | Rear hinge | front-hinged flap in the airflow trails back toward closed |
| D-041 | S1 lower right corner | short direct link |
| D-042 | F1 oval saddle flange, short stem, outer gasket is the main seal | only form that passes a 21 mm neck with Ø14 bore |
| D-043 | B passive one-way vent | no line, no pull force; test decides; A fallback |
| D-044 | SP1 second pin through the latch | latch holds even if the servo pulls; holds out of the aircraft |
| D-045 | R16 → drain ≤ 15 s, residual < 10 g at 0–3° | H3 with Ø14 gives 11.5 s |
| D-046 | Top removal, wing off; front stop + 2 saddles + 2 straps | nose-in 98 N needs a positive stop |

## 4. Interview record
| Date | Question | User's answer | Effect |
|---|---|---|---|
| 2026-11-22 | D-039 CAD tool | FreeCAD only | User override of the global rule (final printed parts in Fusion). Recorded with the cost: no feature timeline for the team. |
| 2026-11-22 | D-040 hinge | Rear hinge (recommended) | Changes D-034 |
| 2026-11-22 | D-041 servo | Beside the valve (recommended) | S1 |
| 2026-11-22 | D-042 flange | Oval saddle flange (recommended) | F1 |
| 2026-11-22 | D-043 vent | Passive one-way valve (recommended) | Changes D-037 (vent not on the pin line) |
| 2026-11-22 | D-044 safety pin | Second pin in the latch (recommended) | SP1 |
| 2026-11-22 | D-045 brief | Change R16 (recommended) | R13, R15, R16 updated |
| 2026-11-22 | D-046 removal | Up through the top (recommended) | Interface §11.4 |
| 2026-11-22 | Bottle measurements | Not yet, use estimates | res_params.py holds the estimates |
| 2026-11-22 | Gate 3 | Yes, start the model | Plan §11 added for the build |

## 5. Tier 2 decisions (Claude)
| ID | Decision | Reason |
|---|---|---|
| T2-1 | No stem flats; the base plate saddle aligns to the cylinder like the inner flange | Flats leave a 0.75 to 1.0 mm wall on a Ø14 bore; the saddle already prevents rotation |
| T2-2 | Flap gasket is a full disc Ø32 (no centre hole); the seat face is the plate face, the nut sits in a pocket | Fixed seat height relative to the hinge and latch → constant latch preload |
| T2-3 | Release pin tip 2 mm into the left lug (engagement 9.5 mm); retracted tip stays in the right lug (captive) | > 2 × twitch (2.6 mm), ≤ 14.1 mm travel with 4.6 mm slack |
| T2-4 | Hinge axis at the belly plane Z −111; knuckles 2.5 mm below the belly | Lets the flap trail to about 170°; small knuckle exposure |
| T2-5 | Bottle profile = outer radius; inner = outer − 0.3 | The measured value will be the outer diameter |

## 6. Stage R-A / R-B build record (2026-11-22)

Built in FreeCAD document `Reservoir_revA`, saved at `design/cad_reservoir/Reservoir_revA.FCStd`. Rebuild: `exec(open(".../design/cad_reservoir/scripts/run_all.py").read())` inside FreeCAD (log: `design/cad_reservoir/run_all.log`). All bottle numbers are in `scripts/res_params.py` (interp.).

### Items built
- R-A: `P1_Bottle` (shell 0.3 mm, punt, neck tube Ø25, support ring Ø32, holes Ø17.3 outlet and Ø8.3 vent), `P1c_Cap`, `Water` (1000 mL, horizontal surface Z −23.53).
- R-B closed: `P2_InnerFlange`, `P3_OuterGasket`, `P4_BasePlate`, `P5_Nut`, `P6_Flap`, `P7_FlapGasket`, `P8_HingePin`, `P9_ReleasePin`, `P10_SafetyPin`, `P10_Flag`.
- R-B open (group `B_Open`, hidden): `P6/P7_*_open` at 160°, `P9_ReleasePin_open` (+12 mm), `P10_SafetyPin_open`, `P10_Flag_open` (pulled out 30 mm). Reference `Ref_BellySkin` (hidden, not a part, not in mass or overlap checks).

### Tier 2 decisions (Claude)
| # | Decision | Alternatives | Reason and numbers |
|---|---|---|---|
| T2-1 | Bottle shifted in X by −2.02 mm: base X −25.72 (plan −23.7); neck lip X 229.28 | keep −23.7 and move the outlet | §11.1 rule. Centroid with the punt and neck water was 82.02; now 80.000. Outlet stays at X 80. |
| T2-2 | Punt read as a spherical cap, footprint R30, height 6 (sphere R78), shifted +0.3 for the inner wall | other dome shape | §11.1 gives only "6 mm high, R30". Interior 1012.4 mL. |
| T2-3 | Neck finish: tube Ø25 OD / Ø21 bore, yu 233–255; ring Ø32 × 2 at yu 231; cap = hollow Ø29.6 × 16, yu 241–257, bore Ø25 | solid cap | Cap is a contact-only part, mass counted in the 22 g bottle. |
| T2-4 | Rim chamfer made with `makeChamfer` (0.8 along the side face, 1.5 along the top), stem fused before the chamfer | loft ramp | Chamfer on the fused body; the stem Ø17 would otherwise stand above the ramp. Rim 0.423 mm, ramp 27.4°. |
| T2-5 | Base plate tongues (front X 50–80, rear X 80–102.5, Y ±10) are 2.0 mm webs on the seat plane, not blocks up to the saddle; knuckle webs 4 mm square; lug and knuckle blocks Z-down | solid tongues up to R41 | Plate mass 2.96 g by the rule (solid tongues about 5.7 g). Target about 3.5 g met without more pockets. Webs stay ≥ 4 mm from the bottle. |
| T2-6 | Fixed knuckle = cylinder Ø5 + block up to the web; flap knuckle bridge box X 95–100 (flap material) | other join | Gap between the Ø34 disc (X ≤ 97) and the knuckle (X ≥ 97.5) closed by a bridge. Fixed knuckles Y 4–10, flap knuckle Y ±3.6: 0.4 mm side clearance. |
| T2-7 | Pin eyes as tori: P9 eye Ø6 (wire Ø1), P10 ring Ø8 (wire Ø1); flag 40 × 20 × 0.2 in the plane Z −110, Y −22…−62 | other eye form | §11.2 gives only the outer sizes. |
| T2-8 | Open state: safety pin pulled out 30 mm (tip Y −21), not 12 mm | retract 12 | A 12 mm retract leaves the tip at Y −3, still inside the hook tab (±3.3), so the flap would stay latched. |
| T2-9 | Belly reference slab Z −111…−109.5, X 30–150, Y ±35, opening = rectangle X 48–106 × Y ±12 plus Ø40 circle at the flap | no opening | Closed flap and hook sit inside the skin layer; the opening is flap + 3 mm (§11.4). |
| T2-10 | Water modelled as interior below the surface minus the P2 flange (999.56 mL after the cut) | keep ideal 1000 mL | No overlap with P2. Nominal 1000 mL / 996 g used for mass. |
| T2-11 | Mass: P2, P5, P6 as thin (full solid, 1.27); P4 as thick (×0.45); gaskets silicone 1.15 solid; steel 7.85; tape 1.2; spring 0.2 g | EVA gaskets | See problems 2 and 3 below. |

### Checks (full text: `design/cad_reservoir/check_report_stageAB.txt`)
| Check | Result | Limit |
|---|---|---|
| Bottle top Z | −20.00 | ≤ −18 PASS |
| Water 1000 mL, centroid X | 80.000 (after the shift) | 80 ± 1 PASS |
| 1 Insertion circle of P2 (projection on YZ) | Ø19.895 (centre z −101.83) | ≤ 20.5 PASS |
| 2 Bore from the flange top to the seat | Ø14.000 at 7 Z levels, flush stem end at Z −107.0 | ≥ 14.0, not smaller PASS |
| 3 Lip | top 1.200, rim 0.423, ramp 27.4° | 1.2 / 0.5 / 30° PASS |
| 3 Residual water 0/1/2/3/5° (calc, modelled geometry) | 2.8 / 3.0 / 4.4 / 6.4 / 11.5 g (calc defaults 2.8 / 3.1 / 4.7 / 6.8 / 12.2) | < 10 g at 0–3° PASS |
| 4 Open 160°: flap and gasket in the Ø14 tube, seat to −60 | 0.000 mm³ both; tube free from 80° to 180° | PASS |
| 4 Belly skin slab sweep | 0 mm³ from 0° to 176°; first contact 177° (hook tab flips above the hinge axis) | max clear open angle 176° |
| 5 Release pin | travel to free the hook 9.30 mm (9.5 with 0.2 margin) ≤ 14.1; engagement in the tab 6.60 ≥ 6; retracted 12: tip Y +6.0, 3.0 mm in the right lug | PASS |
| Overlaps (25 pairs) | none above 0.5 mm³; plate to bottle shell min distance 1.000 mm | PASS |
| `isValid()` all parts | all valid | PASS |

Mass table: `design/cad_reservoir/mass_table_stageAB.csv`. Stage subtotal 34.30 g (bottle 22 given, P2 1.27, P3 0.56, P4 2.96, P5 0.62, P6 3.50, P7 1.39, pins 0.28 + 0.62 + 0.71, flag 0.19, spring 0.2).

### Problems and fixes
1. `makeChamfer` failed when the probe used `common()` with a line on the chamfered solid; the rim is now checked from vertex radii. Chamfer applied after fusing the stem (stem above the ramp otherwise).
2. Flap 3.50 g and flap gasket 1.39 g are above the plan values (2.0 g and 0.4 g). The plan used 1.5 mm EVA sheet; a solid disc at silicone density is conservative. Outlet unit plus flap group plus pins: plan 32.4 g, modelled 34.3 g. Remaining budget with vent 2.5, saddles and straps 10, sealant 0.5: 47.3 g of 50 g. A lighter flap (ribs, 15 % infill: about 1.6 g) is an open T2 choice for R-E.
3. Modelled PET shell mass: 21 274 mm³ × 1.38 = 29.4 g against 22 g given (interp.). The shell at a uniform 0.3 mm is thicker than a real bottle (thin in the body). Weigh the real bottle; the mass table uses 22 g.
4. First belly slab had a rectangular opening only; the Ø34 flap (Y ±17) overlapped it at 0°. Opening enlarged (T2-9).
5. Picture camera: the Inventor `setCameraOrientation` from basis vectors, with animation off, replaced `viewFront` (blank picture). Iso views for the outlet are from below (camera looks up).
6. Interior volume 1012 mL (plan estimate 1032–1040), so the air bubble at 1000 mL is 3.2 mm deep, not 6 mm.

### Pictures (`design/cad_reservoir/img/`)
`stageA_iso.png`, `stageB_outlet_iso_closed.png`, `stageB_outlet_iso_open.png`, `stageB_section_Y0.png`, `stageB_section_X80.png`. Sections are temporary clipped copies, deleted after the picture; the saved file holds none.

## 7. Stage R-C / R-D / R-E build record (2026-11-22)

Same document `Reservoir_revA`; full rebuild with `design/cad_reservoir/scripts/run_all.py` (log `run_all.log`, ends DONE). Reports: `check_report.txt`, `mass_table.md/.csv`. README: `design/cad_reservoir/README.md`.

### Changes from the main session (applied first)
| # | Change | Result |
|---|---|---|
| 1 | Flap P6 lightened: solid skin 1.2 mm under the gasket, grid of pockets 6.8 mm square on the lower face (pitch 8, ribs 1.2 wide, 1.3 deep), rim ring 1.2, hook tab zone and knuckle zone solid | **2.60 g, target ≤ 1.8 g NOT MET** (was 3.50). Tried variants: no grid ribs 2.29 g; skin 1.0 mm 2.47 g; skin 1.0 and no ribs 2.12 g; Ø32 flap 2.40 g; skin 0.8 and no ribs 1.94 g. The skin alone (Ø34 × 1.2) is 1.38 g, tab and knuckle about 0.7 g. 1.8 g needs a thinner skin or a smaller flap: a main-session decision. Total still passes (below). |
| 2 | Flap gasket P7: EVA 2.0 mm, 0.10 g/cm³ (interp.), top face at Z −107.0 | 0.16 g (was 1.85 g with silicone at 2.0 mm). Flap top −108.5 → −109.0, flap Z −111.5…−109.0. **Moved with the flap by −0.5:** flap, release pin and safety pin axes (Z −110 → −110.5), lug holes and tab holes, flag, pin rings. **Not moved:** hinge axis (Z −111.0), fixed knuckles, lugs, plate. Flap knuckle cylinder top trimmed flat to −109.0 (T2). |
| 3 | Mass table: bottle 22 g (interp.); the modelled shell (29.4 g) is only a picture body | Done, noted in the table. |

Consequences of change 2: the flap bottom is now 0.5 mm **below** the belly plane (Z −111.5 against −111.0), not flush. The first contact of the open flap with the belly slab moved from 177° to 176° (largest clear open angle 175°). Checks 4 and 5 rerun: PASS.

### Items built
- R-C: `P11a_VentFlange` (round Ø18 × 1.2 between R38.5 and R39.7 at the top wall, stem Ø8 / bore Ø4 to Z −14.5), `P11b_VentGasket` (Ø18 × 1.0 saddle), `P11c_VentNut` (Ø14, top Z −16.0), `P11d_VentElbow` (printed, Ø10), `P11e_VentValve` (placeholder body Ø11 × 26, barbs Ø4.5 × 8, axis Z −10, X −12 to −54); `Ref_Wing` (SD7062 × 280, +3°, Y ±60, hidden).
- R-D: `P12a_Saddle1`, `P12b_Saddle2`, `P13a/b_Strap`, `P12c_FrontStop` (balsa), floor reference (`Ref_BellySkin`, extended to X −35…235, Y ±55 with the opening and a pin slot), `P14_Servo_MG90S` placeholder, `P14_ServoArm`, `P14_LinkWire`, `P14_QuickSnap`.
- R-E: all checks, mass table, `Reservoir_revA.step` (26 parts, closed, no water, no reference), 10 STL files in `stl/`, README, 11 pictures.

### Tier 2 decisions (Claude)
| # | Decision | Alternatives | Reason and numbers |
|---|---|---|---|
| T2-12 | Vent nut bottom is a saddle (R41 cut), nut top Z −16.0, elbow Ø10 sits on the nut | flat nut | The nut touches the gasket along the centre line; top below −13. Elbow X max −2.70 (limit −2). |
| T2-13 | Valve placed X −12 (aft barb start) to −54 (forward barb end); body ends at −46 | valve X −12 to −46 in total | §11.3 gives "−12 forward to −46" and barbs 8 mm each end plus body 26 = 42 mm; I read −46 as the body end. Forward barb is the air intake. |
| T2-14 | Vent flange has no rim ramp (round, 1.2 thick) | ramp as on P2 | Vent is at the top, above the water; no lip effect. |
| T2-15 | Saddles and the front stop follow the bottle base: saddle 1 at 31.7…43.7 mm from the base (X 6.0…18.0), saddle 2 at 183.7…195.7 mm (X 158.0…170.0); stop X −29.22…−26.22 (0.5 mm in front of the base at −25.72) | keep the plan X values | The bottle moved −2.02 mm (T2-1); relative positions keep the plan meaning and follow later measured bottles. |
| T2-16 | Saddle = 2 mm sleeve (inner = bottle + 0.5), lower 120°, 12 mm wide; saddle 2 follows the shoulder cone (aft stop); foot = beam 6 mm wide Y ±40, 1.6 thick, two pads Y 34…40; centre web 2 mm | full plate foot (4.8 g) | Mass 4.13 g and 4.29 g (plan 3.5 g each). Pads are wide enough to take the strap tail. |
| T2-17 | Straps are on the cylinder (strap 1 at 27.7…47.7 mm from the base, strap 2 at 165…185, just forward of the shoulder), 20 × 1 mm, arc to 65° from the bottom, then a tail down to the pad (Y 37…38) | strap on the cone | The tail geometry stays simple and the strap does not slide on the cone. Tails clear the saddle ends by 0.2 mm. |
| T2-18 | Servo orientation: shaft along −X, case L axis along Z (shaft near the top end), W axis along Y; shaft Y 44.9, Z −87.3; case bottom face X 88.1 (case X 65.4…88.1, boss and spline to X 56.6); arm plane X 57.1…58.9 (on the pin line X 58); closed arm at −45° from straight down, 90° turn | other orientations | L along Y does not fit (tabs 32.5 mm span Y 19…52 and meet the eye and snap). L along Z with the shaft at the bottom end gives a link length of only 7 mm (limit 10). With the shaft at the top end: wire 16.8 mm. Case Y 38.8…51.0, Z −109.05…−76.55. Body to the +X side keeps the mass near the CG station (X 65…88). Plan §3 X 45…70 not kept. |
| T2-19 | Link: snap Ø2 × 12 along Y from the eye (Y 21.0 to 33.0, Z −110.5); wire Ø0.8 from the arm tip rim to the snap end | wire into a tip hole | No overlap with the arm. |
| T2-20 | Floor reference: slot X 43…65 across the floor for the pin line | no slot | The pin line (Z −110.5) lies inside the 1.5 mm floor layer (Z −111…−109.5). Finding for the fuselage design. |
| T2-21 | Print orientation (STL): P2 stem up; P4 as modelled with supports under the seat face; P6 skin face down; vent flange stem down; vent nut flat top down; saddles foot down | other | `stl/print_orientation.txt`. P4 cannot have the seat face on the bed because lugs and knuckles hang below the seat plane (tier 1 if the plate shape is to change). |
| T2-22 | Front stop counted as fuselage structure, shown in the mass table but not in the 50 g total (2.90 g); arm, wire and snap are counted | count the stop | Plan §6 has no stop. Total with the stop is 52.65 g. |

### Checks (full text in `check_report.txt`)
| Check | Result | Limit |
|---|---|---|
| 1 P2 insertion circle / vent flange | Ø19.895 / Ø18.042 | ≤ 20.5 PASS |
| 2 Bore | Ø14.000 at 7 levels, stem end flush Z −107 | ≥ 14.0 PASS |
| 3 Lip, residual 0/1/2/3/5° | top 1.200, rim 0.423; 2.8 / 3.0 / 4.4 / 6.4 / 11.5 g | PASS |
| 4 Open 160°, bore tube | 0.000 mm³; tube free from 80°; first belly contact 176° | PASS |
| 5 Release pin | travel 9.30 (+0.2); engagement 6.60; retracted tip Y +6.0, 3.0 mm in the right lug | PASS |
| 6 Vent | parts above Z −13: elbow X max −2.70, valve −12.0; distance to the wing 6.07 / 11.9 / 12.0 / 13.8 / 14.0 mm | ≤ −2 and ≥ 3 PASS |
| 7 Widths | bottle, vent, saddles, straps, stop ≤ ±50 (strap ±41); servo case Y 38.8…51.0, Z ≥ −109.05 | ±55 / ≤ 52 / ≥ −109.5 PASS |
| 7 Arm swing | arm tip rim reaches Y 53.97 at +45° (1.97 mm past 52); tip centre 51.97 | see problems |
| Servo link | wire 16.84 mm; eye travel 14.14 (hook free at 78.5° of 90°); wire tension 8.7 N at 2.5 N pull, torque 41 N mm = 23 % of stall | wire ≥ 10, travel ≥ 12, ≤ 50 % PASS |
| Servo clearance | min 2.18 mm (case tab corner to the bottle); swept arm to the bottle 9.11 mm; servo to P4 22.8, flap 22.3, strap 34.9, saddle 39.4 | ≥ 2 PASS |
| 8 Mass | 47.75 g (without the MG90S 13.4 g and the stop 2.90 g) | ≤ 50 PASS, margin 2.25 g |
| 9 | all valid, 0 overlaps > 0.5 mm³ in the full model; bottle to the wing 6.86 mm, top Z −20 vs wing −13.1 | PASS |
| 10 | water centroid X 80.000, 1000 mL | PASS |

### Problems
1. Flap 2.60 g against the 1.8 g target (see change 1). Options: (a) accept, the total passes; (b) skin 1.0 mm and no grid ribs, 2.12 g; (c) thinner skin 0.8 mm, 1.94 g, still above; (d) flap Ø30 with a Ø28 gasket (changes §11.2, tier 1).
2. Arm swing envelope exceeds Y 52 by 1.97 mm at the end of the swing. The case is inside 52. Options: arm radius 8.5 mm (travel 12.0, tip rim 52.9); servo 2 mm inboard is blocked by the bottle (tab corner 0.35 mm from the bottle); move the inner wall to Y 54.
3. Servo tab corner is only 2.18 mm from the bottle (limit 2): no spare. It follows from the 32.5 mm tab span between Z −109.05 and −76.55.
4. The release-pin line lies in the floor layer, and the pin eye, safety-pin ring and the link cross the floor: the floor needs a slot X 43…65 (modelled in the reference).
5. Wire at the closed position is steep (4.8 mm along Y, 16 mm along Z): tension 3.5 × the pull. Torque is still 23 % of the stall value. A lower servo position is blocked by the 2 mm bottle clearance.
6. P4 print orientation: the sealing seat face is a support surface, to be sanded.
7. Flap bottom 0.5 mm below the belly (consequence of change 2).

### Pictures (`design/cad_reservoir/img/`)
`full_iso_closed.png`, `full_iso_closed_low.png`, `full_iso_open.png`, `section_Y0_full.png`, `stageB_outlet_iso_closed.png`, `stageB_outlet_iso_open.png`, `stageB_section_Y0.png`, `stageB_section_X80.png`, `vent_closeup.png`, `top_view_limits.png`, `stageA_iso.png`. Each part has its own colour, also on the cut faces. All viewed, none empty.

## 8. Verification by the main session (2026-11-22)
Pictures opened and read: `full_iso_closed.png`, `full_iso_open.png`, `section_Y0_full.png`, `top_view_limits.png`, `stageB_outlet_iso_closed.png`, `stageB_section_Y0.png`, `stageB_outlet_iso_open.png`. Mass table and check report read.

| Key check | Limit | Model | Result |
|---|---|---|---|
| 1 Insertion circle (outlet / vent flange) | ≤ 20.5 | 19.90 / 18.04 | pass |
| 2 Bore | ≥ 14.0, no smaller downstream | 14.000 | pass |
| 3 Lip / residual | rim ≤ 0.5, top ≤ 1.2; < 10 g at 0–3° | 0.42 / 1.20; 2.8, 3.0, 4.4, 6.4 g (11.5 g at 5°) | pass |
| 4 Flap clear of the stream | open ≥ 150° | clear from 80°; 160° shown; max 176° | pass |
| 5 Pin engagement / travel | ≥ 6 (2 × twitch) / ≤ 14.1 | 9.3 to free (6.6 in the tab) / 14.14 eye travel | pass |
| 6 Vent ahead of X −2 above Z −13; ≥ 3 mm from the wing | | X −2.70; 6.1 mm | pass |
| 7 Width | ±55; servo ≤ 52 | all inside ±55; servo case Y 38.8–51.0, **arm rim 53.97 at +45°** | case pass, arm 1.97 mm past the assumed inner wall |
| 8 Mass without the servo | ≤ 50 g | 47.75 g; **50.65 g with the balsa front stop** | pass only if the front stop is fuselage structure |
| 9 Valid, no overlap; bottle to wing | ≥ 5 mm | no pair > 0.5 mm³; 6.86 mm | pass |
| 10 Water centroid | X 80 ± 1 | 80.000 (bottle moved −2.02 mm, base X −25.72) | pass |

Open points for the user review: (a) front stop counted or not in R17 (it carries the 98 N nose-in load); (b) servo arm swing past Y 52: 9 mm arm (travel 12.7 mm, needs 9.3 + slack) or a 1.5 mm side wall (inner Y 53.5) at the servo; (c) flap 2.60 g against 1.8 g target; (d) saddles 8.4 g against 7 g budget; (e) interior volume of the estimated profile 1012 mL → 12 mL air: measure the brim volume; (f) servo tab 2.18 mm from the bottle; (g) base plate prints with supports, sand the seat face.

**Note 2026-11-22 (D-047):** the 50 g reservoir limit (R17) no longer applies. Key check 8 is now a reported mass (47.75 g; 50.65 g with the balsa front stop). Open point (a) stays only for the mass table: count the front stop as fuselage or reservoir structure.

## 8.1 Review with the user (2026-11-22)
| Question / need | User | Effect |
|---|---|---|
| "How will the organizers fill the bottle?" | Asked during the review | Fault found: the forward-pointing vent valve stuck out about 28 mm past the bottle base, so the bottle could not stand on its base for a fill outside the aircraft |
| Fill method | "not clear how they want it … fill in place, need not be removed" | D-049: one top fill port ahead of the LE (only about 20 mm of straight bottle there), vent inside the cap; removal stays for the weigh-in |
| Vent valve in the cap | "recommend" | D-050: printed seat + silicone flap (Claude); fallback aquarium valve |
Rev A.1 spec in the plan §12; bench tests T5 (cap vent) and T6 (fill in place) updated.

## 9. Rev A.1 fill unit build record (2026-11-22)

Plan §12 (D-049, D-050) replaces §11.3. Rebuilt with `design/cad_reservoir/scripts/run_all.py` (log DONE); reports `check_report.txt`, `mass_table.md/.csv`; README updated.

### What changed
- Removed: old vent parts P11a–e, hole Ø8.3 at X −7.7, their STL files (`P11a_vent_flange`, `P11c_vent_nut`, `P11d_vent_elbow`), their mass rows, `vent_closeup.png`, group `C_Vent`.
- Added (group `C_Fill`): `P11a_FillFlange`, `P11b_FillGasket`, `P11c_FillNut`, `P11d_FillCap`, `P11e_CapSeal`, `P11f_VentFlap`; hole Ø13.3 at X −11.0 in the bottle top. `Ref_FuselageTop` (reference: deck Z −4.0…−2.5, X −50…−1, Ø25 hole, interp. height, hidden). `P15_Funnel` in group `E_Ground` (hidden; STL only; not in the STEP, mass or overlap check).
- All new numbers are in `res_params.py` (block "R-C fill unit"). The coordinator had set `BUDGET_G = None` (D-047): the mass report now shows the total without a limit.

### Tier 2 decisions
| # | Decision | Reason |
|---|---|---|
| T2-23 | X_c kept at −11.0 (no move) | Window for X_c: flange on the cylinder needs X_c ≥ −11.47; cap X max ≤ −2 needs X_c ≤ −11.0 for the Ø18 cap. Only 0.47 mm of play. |
| T2-24 | Vent flap stem Ø1.4 in the Ø1.5 centre hole | A Ø1.5 stem in a Ø1.5 hole is a coincident surface; 0.05 mm radial clearance. |
| T2-25 | 12 knurl flutes: cylinders R1.0 at radius 9.3 (0.7 mm deep), Z −15.5…−7.5 | §12.1 says T2. |
| T2-26 | Same rim chamfer as P2 on the flange water-side face (rim 0.423 mm, ramp 1.5 mm) | §12.1 asks for 1.2 → 0.4 over 1.5 mm. |
| T2-27 | Funnel: cone Ø70 → Ø7, wall 1.2 (radial offset), spout Ø7 OD, bore Ø4.6, 2 ribs 1.0 × 1.5 mm, 25 mm long; picture position: neck at Z +5.5, spout tip 10 mm into the stem | §12.1 gives only outer sizes. |
| T2-28 | Capacity method: lip level = lowest point of the fill flange; second figure at the top of the bore entrance; bore column up to the cap seal added; 5° case by rotating the interior about the pivot (X 80, Z −60) | Plan text is short; both levels are shown. |
| T2-29 | Print orientation: flange stem down, nut flat top down, cap top wall down (open end up), funnel rim down | `stl/print_orientation.txt` |

### Checks (full text in `check_report.txt`; checks 1–10 rerun)
| Check | Result | Limit |
|---|---|---|
| Fill flange insertion circle | Ø19.273 | ≤ 20.5 PASS |
| Fill flange on the straight cylinder | cylinder starts X −19.72; flange front edge −19.25 (0.47 mm margin) | ≥ start PASS |
| Fill parts above Z −13 | X max −2.000 (cap) | ≤ −2 PASS (zero margin) |
| Distance to the wing reference | cap 4.87; flange 8.39; seal 7.67; flap 9.42; nut 12.87; gasket 14.79 | ≥ 3 PASS |
| Standing on the base plane (X = −25.72) | bottle and neck cap min X −25.72; fill unit −21.00; outlet unit 44.0 | PASS |
| Capacity, level, lip lowest point Z −22.10 | water below 1007.3 mL; trapped air 5.2 mL; + bore column 0.9 → max fill 1008.2 mL | ≥ 1000 PASS |
| Capacity, level, bore entrance top Z −21.50 | 1009.6 mL; air 2.8 mL; max 1010.6 mL | |
| Capacity, 5° nose up, lip point (plane Z −14.90) | 1011.3 mL; air 1.1 mL; max 1012.3 mL | ≥ 1000 PASS |
| Checks 1–5, 7, 9, 10 | unchanged and PASS: Ø19.895, Ø14.000, lip 1.200 / 0.423 and residual 2.8–6.4 g, open 160°, pin 9.30 / 6.60, widths, 0 overlaps, centroid 80.000 | |
| Check 8 mass | 47.26 g (rev A 47.75 g: −0.49 g; fill unit 3.21 g) without the MG90S and the balsa stop; with the stop 50.15 g | no fixed limit (D-047) |

### Problems and notes
1. The fill-unit gasket (OD 20) reaches 1.28 mm ahead of the cylinder start (X −21.0 against −19.72), the nut 0.28 mm, the cap 0.27 mm: they sit on the base chamfer zone where the PET is below R40 (gap under the gasket up to about 1 mm). Fix options: X_c −10.5 gives all edges behind the start except the gasket (0.8 mm) but the cap X max −1.5 (> −2): fails the cap rule; a cap Ø17 at X_c −10.5 gives cap X max −2.0 and flange margin 0.97, gasket OD 19 reaches −20.0. The design is not changed; this is for the main session.
2. The Ø25 fuselage fill hole spans X −23.5…+1.5: it reaches 1.5 mm aft of the wing LE (X 0).
3. Funnel Ø70: no overlap with the wing reference (0 mm³; the cone is above the wing at X > 0), but it is above the wing nose; it needs the cap off and the fuselage hole open.
4. Cap top-wall vent holes and the flap are modelled closed; air path through the Ø1.5 holes is not simulated.

### Pictures (`design/cad_reservoir/img/`)
`full_iso_closed.png`, `full_iso_closed_low.png`, `full_iso_open.png`, `section_Y0_full.png`, `top_view_limits.png` (remade), new `fill_closeup.png`, `fill_with_funnel.png`; `vent_closeup.png` deleted.

## 10. Rev A.2 build record (2026-11-22)

D-051 lower belly (user) and T2-30 servo link (coordinator). Full rebuild with `run_all.py` (DONE). Reports: `check_report.txt`, `mass_table.md/.csv`.

### Changes
- Belly outer skin Z −117.0, 1.5 thick (floor inner Z −115.5). `Ref_BellySkin` moved down 6 mm; opening X 47…115, Y ±20 (flap/plate outline + 3 mm, T2 reading), pin slot removed. Bottle and outlet unit not moved. Saddle feet down to Z −115.5; front stop outline down to Z −111.
- Servo: MG90S upright, inverted, shaft vertical pointing down; case L along X, W along Y (Y 39.80…52.00), case Z −111.90…−80.40; shaft X 65.07, Y 45.90; arm R 10 in the horizontal plane Z −110.5; arm tip X = 58.00 at ±45°; wire Ø0.8 straight along Y from the snap end (Y 33) to the arm tip (tip Y 38.83 closed, 52.97 after the 90° turn); the arm is cut by the wire (hole), no overlap.
- Fill-unit outer gasket OD 20 → 18: overhang ahead of the cylinder start 1.28 → **0.28 mm** (nut 0.28, cap 0.27 unchanged).
- T2 (mine): open-state pose and check 4 angle set to 150° (was 160°): at 160° the flap now touches the new belly skin (first contact 157°).

### Checks (full text in `check_report.txt`)
| Check | Result | Limit |
|---|---|---|
| 4 Open flap, new belly opening | first contact with the skin 157°; largest clear open angle **156°**; bore tube Ø14 × 60 free from 80° to 180°; 0 mm³ at 150° | ≥ 150° PASS |
| 11 Lowest points, closed | lowest non-saddle part Z −113.90 (strap tails), then P4 lug −113.50, P6 −113.49; margin to the ground plane 3.10 mm; saddle feet −115.50 stand on the floor (exempt) | ≥ −114.0 PASS |
| Gap under the valve | lug/knuckle bottom −113.50 to the skin outer face −117.0 = 3.50 mm | |
| Wire angle to the pin axis | closed 0.0°, end of travel 0.0°, mid travel 30.2° (information) | ≤ 20° at the ends PASS |
| Wire length | 5.83 mm | ≥ 5 PASS |
| Eye travel | 14.14 mm (mid travel 7.86); hook free after 55.0° of the 90° turn | ≥ 12 PASS |
| Servo torque for 2.5 N | 17.7 N mm at closed (10 %); worst over the turn 27.4 N mm (15.5 %) | ≤ 50 % PASS |
| Servo clearance | min 3.60 mm (case to the floor reference); case to the bottle 4.72; arm to the floor 4.10, to the bottle 21.78; wire to the floor 4.60 | ≥ 2 PASS |
| Arm swing envelope | Y max 54.97 (rim of the tip disc; tip centre 52.97): 2.97 mm beyond 52, 0.97 mm beyond 54 | report; case Y max 52.00 |
| Fill unit | unchanged: flange margin 0.47 mm, cap X max −2.000, distances to the wing ≥ 4.87, insertion Ø19.273, capacity 1008.2 mL (level), 1012.3 mL (5°) | PASS |
| Checks 1, 2, 3, 5, 7, 9, 10 | unchanged: Ø19.895, Ø14.000, 1.200 / 0.423 mm, residual 2.8–6.4 g, pin 9.30 / 6.60, 0 overlaps, centroid 80.000 | PASS |
| Mass | 47.51 g (A.1 47.26 g: +0.25 g; rev A 47.75 g: −0.24 g); saddle feet are longer, gasket lighter | no limit (D-047) |

### Problems and options
1. Arm swing: rim reaches Y 54.97. Options: inner wall at Y 55 or more; arm 9 mm radius (travel 12.73, rim 54.26, tip X at ±45° = 58.71, so the wire is 7° off the pin axis; estimates, not modelled); or shaft 1 mm inboard (rim 53.97, case Y 38.8, bottle clearance about 3.7 mm, estimate).
2. Mid-travel wire angle 30° (arm swings in X by 3 mm): the snap and eye must allow that swivel.
3. Flap hits the skin above 156°: opening aft edge X 115 (hinge +15). A larger opening (aft edge X 120) would allow about 163° (estimate, not modelled).
4. Gasket overhang 0.28 mm remains (nut 0.28, cap 0.27).

### Pictures (`img/`)
Remade: `full_iso_closed`, `full_iso_closed_low`, `full_iso_open`, `section_Y0_full` (with the belly skin), `stageB_outlet_iso_closed`, `stageB_outlet_iso_open`, `stageB_section_Y0`, `stageB_section_X80`, `top_view_limits`. New: `servo_link.png`.

### 10.1 T2-31 arm 9 mm, servo 1.0 mm inboard (2026-11-22)
ARM_R 10 → 9.0; shaft Y 45.90 → 44.90 (case Y 38.80…51.00); shaft X 64.364 so the arm tip X at ±45° = 58.00. Full rebuild DONE.
| Check | Result | Limit |
|---|---|---|
| Arm envelope Y max (rim of the tip disc) | 53.26 (tip centre 51.26); was 54.97 | ≤ 53.5 PASS |
| Wire angle to the pin axis | closed 0.0°, end 0.0°, mid travel 28.4° (information) | ≤ 20° at the ends PASS |
| Wire length | 5.54 mm | ≥ 5 PASS |
| Eye travel | 12.73 mm (mid 7.03) | ≥ 12 PASS (margin 0.73) |
| Turn to free the hook (9.5 mm pull) | 62.3° of 90° | |
| Servo torque for 2.5 N | 15.9 N mm closed (9.0 %); worst over the turn 24.4 N mm (13.8 %) | ≤ 50 % PASS |
| Clearances | min 3.60 mm (case to floor); case to bottle 3.84 (was 4.72); arm to bottle 21.60, to floor 4.10 | ≥ 2 PASS |
| Checks 1–11, fill unit | unchanged, no FAIL, 0 overlaps; open angle 156°, lowest part −113.90 | PASS |
| Mass | 47.50 g (was 47.51) | no limit |
Pictures remade and viewed: `servo_link`, `top_view_limits`, `full_iso_closed`, `section_Y0_full`, plus `stageB_section_Y0`, `full_iso_open`. STEP, STL (arm) and README refreshed by the rebuild.

## 11. Final tier 2 decisions and closing notes (main session, 2026-11-22)
| ID | Decision | Reason |
|---|---|---|
| T2-30 | MG90S upright, shaft down, arm in the pin plane Z −110.5; wire along the pin axis | The flat servo gave a wire 73° off the pin axis at closed: axial share 0.29 of the tension, lug friction about the same → near self-locking. Now 0° at closed and at the end, 28° at mid travel; torque 9 to 14 % of stall |
| T2-31 | Arm R 9, servo 1 mm inboard | Arm rim reached Y 54.97 (the 110 mm outer skin); now 53.26; eye travel 12.73 mm (needs 9.5); case to bottle 3.84 mm |
| T2-32 | Bottle profile kept as outer radius − 0.3 mm wall with the punt: interior 1012 mL, max fill 1008 mL level | The 1040 mL brim in the reservoir notebook is also an estimate; the measured brim volume replaces both. The tight capacity margin (8 mL) comes from the estimate, not from the bottle |
Final verification (main session): `section_Y0_full.png` shows the valve 3.5 mm above the belly line; `top_view_limits.png` shows all parts inside Y ±55 (flag outside on purpose); `servo_link.png` shows the straight pull. Bench test T3 limit stays 8.8 N (conservative: the effective lever at the start is 6.4 mm with the 9 mm arm, so the servo force there is higher than at a 10 mm arm).

**2026-11-22: the user accepted rev A.2 for the test prints (cad-codesign step 6 closed).** Next: measure the bottle (res_params.py), print the outlet and fill units in PETG, run bench_tests.md T1 to T6.

**2026-11-22: bottle measurements and bench tests T1 to T6 deferred by the user (exams, limited funds).** Rev A.2 stays on estimated bottle values; the fuselage stage starts (session "Fuselage stage: plan and CAD around reservoir A.2") with the reservoir interface kept parametric. Risk: the fill-port fit (0.47 mm) and the capacity (1008 mL) can change when the real bottle is measured.
