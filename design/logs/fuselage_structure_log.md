# Fuselage pod structure (stage F-S) — engineering notebook

Started 2026-11-22. Side session "pod-structure-opt" (Opus). Task from the fuselage session: internal printed cross bars and ribs, lighter outer shell (windows, FEM-guided; topology optimization if practical). Output: `design/cad_fuselage/structure/` (study report, FEM files, pictures) and `design/cad_fuselage/scripts/fus_struct.py`. This session touches only these two places and this notebook.

Frame: wing frame (origin at the wing LE on the centreline, X aft, Y right, Z up, mm). Inputs read: plan 04 (§3, §5, §7, §8, §9), plan 03 §13–§14, `fuselage_log.md`, `fuselage_cad_log.md`, DECISIONS D-046, D-052…D-057, brief R14, R20–R26, `fus_params.py`, `fus_build.py`, `check_report_stageA.txt`.

## 1. Model state

| Item | State |
|---|---|
| F-A shell | `Fuselage_revA.FCStd` saved 21:41. `fus_build.py` and `fus_check.py` changed at 21:47–21:48. `run_all.log` does not exist at 21:55. **All numbers in this notebook that come from the shell are provisional until `run_all.log` shows DONE.** |
| Shell used for the bounds | `fus_build.build_pod()` in a separate headless process (the scripts are imported read-only; the GUI and its documents are not touched). `fus_params.py` sha1 74a22ce3aa, `fus_build.py` sha1 7e0c356b51. Parts saved as BREP in the session scratchpad. |
| F-A volumes (same as the check report) | F1 30.63, F2 36.01, F3 21.81, F4 12.29 cm³; total 100.74 cm³ (PLA 124.9 g, ASA Aero 0.65: 65.5 g) |
| Tools | FreeCAD 1.1.1 (headless `freecadcmd`), CalculiX 2.23, gmsh 4.15, numpy, scipy, matplotlib (FreeCAD Python). |

## 2. Material data

### 2.1 Sources
- Bambu PLA Basic Technical Data Sheet (Bambu Lab, Shopify CDN `Bambu_PLA_Basic_Technical_Data_Sheet.pdf`): specimens printed 100 % infill.
- Bambu ASA Aero Technical Data Sheet V1.0 (Shopify CDN `Bambu_ASA_Aero_Technical_Data_Sheet.pdf`). **The specimens were printed at 225 °C nozzle, 100 % infill, and annealed 80 °C 12 h. At 225 °C ASA Aero does not foam (it foams at 240–280 °C). The sheet density 0.99 g/cm³ agrees: these are values for unfoamed material.** The foamed values below are my estimates.

### 2.2 Data-sheet values

| Property | PLA Basic X-Y | PLA Basic Z | ASA Aero X-Y (unfoamed) | ASA Aero Z (unfoamed) |
|---|---|---|---|---|
| Density (ISO 1183) | 1.24 g/cm³ | | 0.99 g/cm³ (filament / unfoamed) | |
| Young's modulus (ISO 527) | 2680 ± 130 MPa | 2160 ± 90 | 2010 ± 260 | 1180 ± 210 |
| Tensile strength (ISO 527) | 39 ± 2 MPa | 35 ± 3 | 32 ± 4 | 21 ± 4 |
| Elongation at break | 12.2 % | 7.5 % | 5.1 % | 2.3 % |
| Bending modulus (ISO 178) | 2750 MPa | 2370 | 1510 | 1220 |
| Bending strength (ISO 178) | 76 MPa | 68 | 58 | 24 |
| Impact (ISO 179, unnotched) | 26.6 kJ/m² | 13.8 | 32.0 (notched 8.2) | 3.4 |
| HDT 0.45 MPa / Vicat | 57 °C / 57 °C | | 85 °C / 80 °C | |
| Max overhang / bridge (sheet) | — | | about 70° / about 40 mm | |

### 2.3 Values used in the FEM *(interp.)*
Foamed ASA Aero: Gibson–Ashby scaling from the unfoamed values with the relative density ρ/0.99: modulus ∝ (ρ/0.99)², strength ∝ (ρ/0.99)^1.5. Thin single-line walls: strength knock-down 0.7 (along the lines, X-Y) and 0.5 (across the layers, Z) *(interp.)*.

| Material | E X-Y | E Z | σ X-Y sheet → allowable | σ Z sheet → allowable |
|---|---|---|---|---|
| PLA Basic 1.24 | 2680 | 2160 | 39 → 27.3 MPa | 35 → 17.5 MPa |
| ASA Aero 0.53 | 576 | 338 | 12.5 → 8.8 | 8.2 → 4.1 |
| **ASA Aero 0.65 (design)** | **866** | **509** | **17.0 → 11.9** | **11.2 → 5.6** |
| ASA Aero 0.80 | 1313 | 771 | 23.2 → 16.3 | 15.3 → 7.6 |

Consequences:
1. **The same geometry is 3.1 times less stiff in ASA Aero 0.65 than in PLA, and its allowable across the layers is 3.1 times lower.** The zonal ASA Aero pod sets the strength and buckling design. The PLA pod sets only the mass (R6 override of the test aircraft).
2. The structure is linear in one material: I solve with one reference modulus and scale. Stress does not change with E (one material, force loads); deflection scales with 1/E; the buckling factor scales with E. The report gives the lowest E that passes, so a weighed coupon test can settle the foamed value.
3. Print orientation is not decided (F-E). My assumption *(interp.)*: F2 prints belly down (open top up, layers ⟂ Z); F1 and F3 print on their split faces (layers ⟂ X; the nose and aft-cone tapers are ≤ 33° from the build axis, so no support). Fuselage bending stress σx then crosses the layers in F1 and F3. **To make the result independent of the orientation, I check the maximum principal stress against the Z allowable everywhere, and von Mises against the X-Y allowable.**
4. Proposed coupon test (cheap, settles items 1–2): print a 0.5 mm single-wall strip 20 × 120 mm in ASA Aero at the zonal foaming setting, weigh it (density), and load it as a cantilever with known weights (modulus from the deflection, strength from the break). Do it once in each direction (along and across the layers).

## 3. Load cases (limit loads; ultimate = 1.5 × limit)

Masses for the inertia loads (heavier PLA aircraft, loaded 1.72–1.73 kg, plan §5; electronics are placeholders, R26):

| Item | g | X | Load path into the pod |
|---|---|---|---|
| Water + reservoir rev A.2 | 1047.5 | 80 (water centroid) | saddles X 1.98–21.98 / 139.28–169.98 (as built), front stop X −29.22…−26.22 in X |
| Release servo MG90S | 13.4 | 64 | right wall, servo mount |
| Motor + prop + spinner | 70 | −190 | firewall X −173…−170 |
| ESC | 25 | −140 | nose floor / side |
| Battery 3S 1000 | 85 | −92 (slide −122…−62) | nose floor tray |
| Wing with servos | 184 | 110 | seat lips (bands) |
| Twin tubes 2 × Ø8/6 | 33 | 475 | socket block X 230–300 |
| Tail block + tail surfaces + pushrods | 33 | ≈ 650 | socket block (force + moment) |
| Tail servos + receiver | 26 | 215 | aft floor / bay |
| Wiring | 15 | distributed | — |
| Pod structure | from the model (density × volume) | | gravity body load in the FEM |

| LC | Case | Load (limit) | Reaction | Source |
|---|---|---|---|---|
| LC1 | Belly landing, full water | 10 g down on every mass; ground on the belly skids (front X −30…40, rear X 120…195 *(interp.)*); sub-cases a flat, b front skid only, c rear skid + aft-cone bottom | skid patches fixed in Z, 3-2-1 in X, Y | R14 (10 g, 98 N), R23 |
| LC2 | Nose-in / skid stop | 10 g aft-to-fore on every mass (water + reservoir 103 N on the front stop; nose group 17.7 N on the firewall and tray; wing 18 N on the band stubs) + 5 g down | front skid patch and nose bottom | R14, task (98 N on the stop) |
| LC3 | Hand launch | 5 g forward (10 m/s over 1.0 m *(interp.)*) + 1 g down on every mass; finger squeeze 40 N each side *(interp.)* on finger patches X 50–110, Z −100…−60 | palm patch on the floor X 40–120, Y ±(20…55) | D-054 |
| LC4 | Motor | thrust 12 N *(interp.; R3 gives ≤ about 10 N)*, torque 0.3 N·m *(interp.)* at the firewall; hatch off | band stubs + rear dowel | plan §3, key check 12 |
| LC5 | Band preload | 50 N total *(interp.)*: 2 × 12.5 N up at the stubs X −6, Z −24 (20 % inboard component), 25 N up at the rear dowel X 295, Z −22; wing reaction 50 N down on the seat lips near the bands | self-balanced, 3-2-1 | D-053, task |
| LC6 | Flight pull-up / gust | 3 g *(interp.; the wing stalls near 1.6 g at 12 m/s and 2.4 g at 15 m/s loaded)* on every mass; the pod hangs from the wing | band stubs (71 %) + rear dowel (29 %), by moment about the CG X 80 | derived |
| LC7 | Tail | a vertical 15 N at X 680 → at the sockets 15 N + 7.5 N·m (plan §6.2); b lateral 9 N at the fin (X ≈ 690, Z ≈ +40) → shear, yaw moment, torsion 0.72 N·m; c asymmetric stab 0.9 N·m torsion (twin tubes: ±28 N on the two sockets) | band stubs + rear dowel | plan §6.2 *(b, c interp.)* |
| LC8 | Handling, local | thumb press 10 N on a Ø15 mm patch at the lip, the grip zone, the nose sides with the hatch off and the window frames | local | key check 12 *(force interp.)* |

## 4. Criteria *(interp., to be agreed with the user: tier 1 "strength against mass")*
1. Strength at ultimate (1.5 × limit): maximum principal stress ≤ Z allowable and von Mises ≤ X-Y allowable (§2.3), ASA Aero 0.65 and PLA.
2. Buckling (linear, CalculiX `*BUCKLE`) at limit load: frames, lips, longerons and the global pod λ ≥ 2.0 (1.5 ultimate × 1.33 imperfection); skin panels between ribs λ ≥ 1.0 (wrinkles only above limit load, no collapse).
3. Stiffness: thumb press (LC8) ≤ 2.0 mm on the frames, the lips and the grip zone; tail socket under LC7 ≤ 2.0 mm and twist ≤ 0.5°.
4. Printability on the P1S without support in the assumed orientation (§2.3 item 3): no horizontal window top edge (window edges at ≥ 45° to the layers), no flat overhang > 3 mm on a rib or bar, bridges ≤ 20 mm (sheet allows about 40).

## 5. Bound of the mass saving before any FEM (F-A shell, headless tessellation of the OML)

Side-wall area that windows can use (both sides; keep-outs: 12 mm lip / hatch-seat band at the top, floor corner + 8 mm band at the bottom, grip zone X 35–125, band-stub bosses r 15, split joints ± 8 mm, front-stop band X −36…−20, socket block X ≥ 228, firewall frame X ≤ −160; the belly, the aft-cone bottom and the hatch are fully excluded):

| Band | Eligible area | Wall | Gross saving at 55 % windows |
|---|---|---|---|
| Nose sides X −160…−36 | 16 620 mm² | 0.8 | 7.3 cm³ = 4.8 g ASA Aero / 9.1 g PLA |
| Centre sides X −20…35 and 125…167 | 18 206 mm² (with the X 183–200 part) | 0.5 | 5.0 cm³ = 3.3 g / 6.2 g |
| Aft sides X 183…228 | 5 251 mm² | 0.5 | 1.4 cm³ = 0.9 g / 1.8 g |

Window frames (ribs) take back about 30–45 % of the gross saving; covering film adds about 0.5–0.8 g. **Windows alone: net about 3–5 g ASA Aero (0.5–0.8 % score) and 6–10 g PLA.**

Thickness lever (0.8 → 0.5 mm, ribs where the FEM needs them):

| Region | Area | Saving (gross) |
|---|---|---|
| Nose shell without the hatch | 39 930 mm² | 12.0 cm³ = 7.8 g ASA Aero / 14.9 g PLA |
| Hatch top | 15 747 mm² | 4.7 cm³ = 3.1 g / 5.9 g |
| Floor X −35…200 (without the belly opening) | 23 257 mm² | 7.0 cm³ = 4.5 g / 8.7 g |
| Aft-cone bottom | 10 449 mm² | 3.1 cm³ = 2.0 g / 3.9 g |

**The wall thickness is the larger lever (gross 17 g ASA Aero / 33 g PLA) than the windows.** The wall values are in `fus_params.py` (owned by the fuselage session, T2-4 / F-T2-6 / F-T2-7): I can only recommend them, backed by the FEM.

Score effect (99 600 / empty mass): ASA Aero 642 g → 155.1. −5 g: 156.4 (+0.8 %); −10 g: 157.6 (+1.6 %); −20 g: 160.1 (+3.2 %). PLA 728 g: −20 g lowers the loaded stall by about 0.06 m/s (R6 override).

## 6. My view before the interview (written before the questions)
1. **Main structure.** The 0.5 mm foamed ASA Aero skin is a weak structural material (E ≈ 0.87 GPa, Z allowable ≈ 5.6 MPa). A 40 × 40 mm panel of it deflects many millimetres under a 10 N thumb load (plate formula: w = 0.0056 P a²/D, D = 10.4 N·mm → 8.6 mm linear). Loads must go through a printed frame: ring frames at the formers and splits, the seat lips as top longerons, a floor grid, and diagonal ribs on the side walls. The skin is then mainly an aerodynamic cover; windows cost little stiffness where the frame carries the load.
2. **Where the mass is.** Make all skins 0.5 mm (nose, hatch, floor, aft-cone bottom) and stiffen with ribs where the FEM needs them; add windows only in the side-wall bands of §5. Expected net about 10–15 g ASA Aero and 20–30 g PLA. Windows alone give about 3–5 g ASA Aero.
3. **Cross bars.** Allowed only in the nose (one closed frame at the firewall and one at X ≈ −40, so that X −160…−45 stays open for the battery: 72 mm long, it goes in from the top) and aft of the bottle cap (X ≥ 236; the cap reaches X 229.3). These close the open U-section at its ends, which is good for torsion and for the side walls with the hatch or the wing off. No bar across X −27…231 (D-046).
4. **Window shape.** Diamonds with edges at ±45° and corner radius ≥ 3 mm: support-free in either print orientation, a natural diagrid (each land between two windows carries a ±45° rib), and no horizontal edge to bridge.
5. **Window covering (tier 1).** My view: self-adhesive clear film or clear tape, about 50 g/m² (≈ 0.5–0.8 g for all windows), no heat. Iron-on film needs 90–120 °C, above the PLA glass transition (60 °C). Open windows let air into the closed pod cavity (drag) and leave the release servo and wiring open to dust and water.
6. **Strength against mass (tier 1).** My view: the "balanced" level — the criteria of §4 (FoS 1.5, frame buckling ≥ 2.0, skin wrinkle ≥ 1.0 at limit, thumb press ≤ 2 mm on the frame). A stricter level keeps the 0.8 mm floor and nose. A lighter level accepts dents and repairs after hard landings.
7. **Topology tool (tier 1).** My view: no topology-optimization loop. The skin is already at the minimum printable wall (one line, 0.5 mm), so a density or BESO loop on the skin can only remove or keep skin; a strain-energy map over all load cases gives the same window map. FEM-guided layout: strain-energy and stress envelopes over LC1–LC8 → windows in the low-energy zones inside the keep-outs → ribs on the load paths → FEM check. A BESO macro is a download (permission needed) and adds no information here.
8. **FEM method.** Shell elements (6-node triangles S6 in CalculiX) on the outer surface of F1–F3, thickness by zone; ribs and frames as shell strips joined to the skin (conformal mesh by gmsh `Coherence`); windows as holes. Solids at 0.5 mm need several elements through the thickness: not practical on a 470 mm pod. First a smoke test on a flat plate (buckling against k = 4, bending stress against 6M/t²) to prove the result reader.
9. **Baseline for the comparison.** F-A shell + the members that F-B adds in any case: seat lip 8 mm, ring ribs 0.8 × 6 at the formers (T2-4), front stop (3 mm balsa in a slot), firewall (3 mm ply) with its frame, socket block, split sleeves. The mass saving is the difference on the same input shapes. My ribs replace the T2-4 former ribs where they coincide.

## 7. Interview record

### Round 1 (2026-11-22)
- Asked (neutral options, my view already written in §6): purpose, window cover, strength against mass, method.
- User: "what do you recommend" for the first three, "recommended" for the method.
- I gave my recommendations with one reason each (§6 items 5–7: mass objective with stiffness limits; self-adhesive clear film or tape; balanced; FEM-guided layout). User: **"Accept all 4"** → **D-060**.
- Classified: all four are needs and preferences (decisive). The skin thickness change is an engineering claim that the FEM must prove; it goes to the fuselage session as a recommendation (it owns `fus_params.py`).

### Model status update
- 21:58: `run_all.log` ends with DONE. `fus_params.py` sha1 74a22ce3aa, `fus_build.py` sha1 7e0c356b51: the same files that I used for the bounds in §5. The F-A volumes are unchanged (100.74 cm³). The §5 numbers are therefore final for F-A.
- New since my first reading: D-058 (pull the safety pin before the lift-out), D-059 (local outward pocket in the right wall at X 52–77, Z −113…−107, wall 1.2 mm, in F-B). The pocket is inside the grip zone keep-out.

## 8. FEM method proof (smoke test, `structure/fem/smoke_plate.py`, result `structure/fem/smoke_result.txt`)
Inter-session note (fuselage session, 2026-11-22): print split moves from X −24 to X −26.22 (aft face of the balsa front stop = joint former F1/F2); hatch top +1 mm over X −25…−2; D-059 pocket X 52–77, Z −113…−107 right, 1.2 mm wall (no window, no thin skin there); skin on slopes corrected to t/cos(slope) in F-B.

| Test | First result | Problem found | Fix | Final result |
|---|---|---|---|---|
| Node mapping of the expanded shell results (.frd → 2D nodes) | 1.35 mm from the 2D node (t/2 = 0.5) | the .frd node order of C3D20R/C3D15 puts the mid-surface nodes before the top mid-side nodes | `EXP` table changed | 0.500 mm (exact) |
| Cantilever strip bending, 1 N tip | σx at mid-length 15.37 MPa; tip 193.7 mm; reaction 1.000 N | — | — | theory 15.00 MPa (+2.5 %, plate-strip effect); tip between beam 200 and plate 175.5 |
| SS plate 200 × 100 × 1 buckling, k = 4 | factor 0.787–0.93 (2.1–2.8 × theory), also S8R, S8, solid C3D20R | **this CalculiX build (2.23, SPOOLES/ARPACK) returns only the buckling factors near 1.0 (shift 1); a factor below about 0.5 is not found** (cantilever column at 2.0 N gives modes 2–6 only; at 0.45 N mode 1 appears at 0.933) | `buckle_sweep`: reference load × s, s = 0.03 … 8 (each ×2), lowest λ·s over all runs | S8R 0.3726 against 0.3749 (−0.6 %); S6 0.3733 |
| Euler column 100 × 20 × 1, clamped | 3.81 (mode 1 missing) | same | same | 0.421 (beam 0.411, plate strip 0.469) |

Element: S8R (all-quad mesh by gmsh subdivision, final size about hmax/2); S6 is also correct once the sweep is used.

## 9. Restart in the fuselage session (2026-11-23)
The side session and its orphan buckling sweep were stopped at 10:13. The user asked the fuselage session to make the pod lighter with honeycomb or another pattern "without compromising strength". The fuselage session continues this study (one session, no parallel edits of the model).

### 9.1 Baseline result read before the restart
`results/base/run.log` (F-A shell + F-B members, ASA Aero 0.65): stress utilization LC3 65, LC1b/c 22–24, LC5 16, LC8 grip 16, LC2 14, LC1a 6.1, LC4 2.2; linear deflections up to 291 mm. The 0.5 mm open U-section without ribs is far too weak. The work is therefore "the lightest rib structure that meets the criteria", then windows where the stress is low.

### 9.2 Pattern view (given to the user)
A honeycomb sandwich core is not possible in a one-line 0.5 mm skin. Levers: thinner skins with an isogrid / diagrid rib net (largest), film-covered windows in low-stress bays (3–5 g ASA Aero), and slicer honeycomb or gyroid infill in the thick printed parts (socket block, tail block, saddles, shelves; no CAD change). Window shape: diamonds at ±45° (support-free in foamed ASA Aero; hexagons have 30° edges).

### 9.3 Load review, round 2 (→ D-064)
User: grip under the belly and a firm side grip; belly landing "let's not compromise"; landing surface not known; band load: Claude's default; material ASA Aero 0.65. Changes: LC3 squeeze 40 → 20 N each side (`SQUEEZE_N` in `pod_model.py`); all other loads unchanged; LC8 2 mm limit only on frames, lips and the grip zone.

### 9.4 Model state for the new runs
Fuselage model after F-B, F-C and D-063: split X −26.22, tubes Ø10/8 (sockets Ø10.3), F-B features. `pod_model` builds the shell from `fus_build.build_pod()` with the current `fus_params.py`; the F-B features that are not modelled as members (tray, shelves, ledge pads) are not in the FEM (conservative for stiffness).

### 9.5 Runs on 2026-11-23 and hand-off
- Baseline again with the D-064 loads (`results/base/run.log`): LC3 32 (was 65 with 40 N squeeze); all other cases unchanged (LC1b 24, LC1c 22, LC5 16, LC8 grip 16, LC2 14, LC7a 9.1, LC6 6.4, LC1a 6.1, LC4 2.2).
- `pod_model.selectors`: the rear socket bearing selector now uses the end-wall position, not the zone (in D1 the rib tagging took end-wall elements: "empty selector brgRL").
- D1 (fus_struct PAR, 103.9 g ASA Aero in the model, +15.9 g against the baseline) stops in CalculiX: "gen3dnor: opposite normals" at the rib–skin T-junctions (3D expansion of the shells).
- Concern written down: linear deflections of 60–150 mm against about 1 mm from a beam estimate: the local load introduction (masses on bare skin, small patches) must be checked before the design follows the peaks.
- The user moved the study to the Windows PC with the ANSYS MCP. Hand-off prompt: `design/cad_fuselage/structure/CONTINUE_ON_WINDOWS_ANSYS.md`; STEP files in `design/cad_fuselage/export/`.
