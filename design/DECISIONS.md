# Decision record

Newest at the bottom. Tier 1 = the user decides after the comparison. Tier 2 = Claude decides by rule or calculation and reports it.

## D-001: Wing airfoil (tier 1) — PROPOSED, waiting for the user

Date: 2026-11-21. Stage: 2 (wing).

**Question:** Which airfoil for the wing?

**Flight conditions:** Re 160k to 240k. Hand launch needs high CLmax. Loaded cruise at 13 m/s needs CL 0.6 to 0.7. After the release, CL is 0.2 to 0.3.

| Airfoil | CLmax (2D) | Stall | Cd at CL 0.3 / 0.7 | Cm at CL 0.8 | Lower surface | Build |
|---|---|---|---|---|---|---|
| **SD7062** | 1.58 | very gentle | 0.0124 / 0.0125 | -0.080 | convex | easy, 14 % thick |
| Clark Y | 1.38 | gentle | 0.0112 / 0.0115 | -0.082 | flat | easiest |
| MH 114 | 1.77 | very gentle | 0.025 / 0.015 | -0.189 | 2 % concave | medium |
| NACA 6412 | 1.58 | sharp | 0.0175 / 0.0127 | -0.145 | 1 % concave | medium |
| E423 / S1223 / CH10 | 2.0 to 2.25 | medium to sharp | 0.045 to 0.085 | -0.23 to -0.25 | 5 to 6 % concave | hard (thin trailing edge) |

Source: `design/aero/airfoil_study.md` (NeuralFoil xlarge, Re 180k, Ncrit 9). The high-lift section drag values have low confidence (0.25 to 0.78). I did not check them against wind-tunnel data in this session. The CLmax values are also not checked against wind-tunnel data.

**Total drag, not only section drag:** at AR 3.6 and CL 0.62, the induced drag coefficient is CL²/(π·AR·e) = 0.040. This is about 3 times the section Cd. Thus MH 114 gives only about 8 % more wing drag than SD7062 (0.057 against 0.053), not 35 %. The high-lift sections still give 60 to 100 % more wing drag.

**Trim effect** *(interp., tail arm 0.6 m, 13 m/s, ρ 1.05)*: the tail download to balance Cm is about 1.0 N for SD7062 and 2.2 N for MH 114. The extra 1.2 N is about 8 % of the weight. The wing must carry it, so the stall speed of MH 114 increases by about 4 %. This removes most of the 5.5 % stall-speed gain from its higher CLmax.

**My view before I asked:** E423 (high CLmax for the hand launch). **Changed by evidence:** the high-lift sections have 4 to 7 times the drag at cruise and after release, and 3 times the pitching moment.
**My proposal now:** SD7062. Reasons: small nose-down moment (smaller tail, small trim loss), very gentle stall, nearly flat lower surface (easy for film, foam or print), 14 % thickness (deep spar), low drag over the full CL range.
**Runner-up:** MH 114. Its 2D CLmax is 0.19 higher. After the trim loss, the net stall-speed gain is only about 1 to 2 % *(interp.)*. It needs a larger tail and has a 2 % concave lower surface.
**User's view:** none given before the comparison.
**Decision (2026-11-21):** SD7062. **Decided by:** user, after the comparison. **How to reverse:** new rib outlines only; the planform does not change.

## D-002: Wing chord and planform (tier 1) — PROPOSED, waiting for the user

**Question:** Which chord, with span fixed at 1.00 m (rule maximum)?

Chord sweep, SD7062, wing CLmax 1.35 *(interp.: 0.85 × airfoil CLmax)*, balsa wing, rest of aircraft 440 g *(interp.)*:

| Chord | Area m² | AR | Wing g | Empty g | Score | Vs Bengaluru | Vs Chennai |
|---|---|---|---|---|---|---|---|
| 0.24 m | 0.240 | 4.2 | 107 | 547 | 182 | 9.4 m/s | 9.0 m/s |
| 0.26 m | 0.260 | 3.8 | 114 | 554 | 180 | 9.1 m/s | 8.7 m/s |
| **0.28 m** | **0.280** | **3.6** | **122** | **562** | **177** | **8.8 m/s** | **8.4 m/s** |
| 0.30 m | 0.300 | 3.3 | 131 | 571 | 174 | 8.5 m/s | 8.1 m/s |

**Sensitivity:** the wing CLmax of 1.35 is not checked. If the real wing CLmax is 1.20, every stall speed is 6 % higher: 9.3 m/s at 0.28 m, 9.0 m/s at 0.30 m, 8.8 m/s at 0.32 m (Bengaluru).

**Criterion:** loaded stall speed ≤ 9.0 m/s at the Bengaluru density, for a safe hand launch *(interp.)*. This target is also a guess. With an empty mass of about 560 g, the loaded T/W is only about 0.54, so the throw speed matters.
**My proposal:** 0.28 to 0.30 m, rectangular. Set the final value with launch evidence: the heaviest aircraft that the team threw before, or a throw test with a 1.5 kg dummy and a phone video to measure the throw speed. Each 0.02 m of chord costs about 8 g (about 1.4 % of the score).
**Span:** 0.99 m nominal, not 1.00 m, so that build tolerance does not break the rule.
**Decision:** pending.

## D-003: Wing build method (tier 1) — PROPOSED, waiting for the user

Wing masses at chord 0.28 m, t/c 14 % (`design/calc/wing_mass_model.py`, first estimates *(interp.)*, to be corrected with weighed samples).

| | Balsa built-up (robust) | LW-PLA print | XPS hot-wire + tape | PLA print |
|---|---|---|---|---|
| Wing mass | 137 g | 176 g | 208 g | 410 g |
| Empty mass | 577 g | 616 g | 648 g | 850 g |
| Score | 173 | 162 | 154 | 117 |

Weighted table (1 = poor, 5 = good). Weights from the user's answers: "light but robust", repairs only at the venue, deadline not known.

| Criterion | Weight | Balsa (robust) | LW-PLA | XPS | PLA |
|---|---|---|---|---|---|
| Wing mass (score) | 5 | 4.6 | 3.5 | 2.5 | 1 |
| Survives hard landing / cartwheel | 4 | 4 | 2 | 5 | 3 |
| Repair at the venue | 3 | 4 | 2 | 4 | 2 |
| Airfoil accuracy | 2 | 3 | 5 | 4 | 5 |
| Build time, schedule risk | 3 | 3 | 4 | 5 | 4 |
| Tolerance to sun heat (45 to 60 °C surface) | 2 | 3 | 2 | 4 | 2 |
| **Weighted total** | | **72** | **57.5** | **75.5** | **49** |

Mass score: 5 at 122 g, minus 1 for each 35 g more.

**My view before I asked:** balsa built-up.
**Comparison:** XPS wins the weighted table by 3.5 points, on robustness and build time. But the estimate makes XPS 71 g heavier than robust balsa. That is about 11 % of the score. The user chose "light but robust"; the text of that option said about 20 to 40 g extra. The user must confirm if this is a limit.
**Uncertainty:** nobody weighed these masses. The XPS value (density, 35 % hollow) is the least certain, and it decides the result.
**Cheapest test:** make a 100 mm span sample of the wing in balsa, LW-PLA and XPS, and weigh each. Multiply by 10 for the full wing.
**My preference:** balsa built-up, robust version (laser-cut ribs, carbon spar caps, D-box, plywood root and tip ribs, film). This is a preference until the samples are weighed.
**What XPS does better:** it survives impacts, it builds in 1 to 2 days, and it does not sag in the sun. XPS wins if the team values robustness and build time more than 11 % of the score, or if the schedule is very short.
**Decision (2026-11-21):** balsa built-up, "as robust as possible while lightweight". **Decided by:** user, after the comparison (samples not weighed). **Risk accepted:** less impact tolerance than XPS; film can sag in the sun.

## D-004: Spar (tier 2, provisional: applies to the balsa wing)
Carbon pultruded strip 0.5 × 6 mm top and bottom, full span, at 27 % chord, with 1.5 mm balsa shear web (vertical grain). Design load factor 6 (limit 4 × 1.5): root moment 8.9 N·m, cap force 270 N, stress 90 MPa against about 400 MPa allowable *(interp.)*, margin about 4. Decided by: Claude by calculation. Reverse: change strip size.

## D-005: Wing incidence, twist, dihedral (tier 2, provisional: assumes a high wing, Q3 open)
- Incidence +3° to the fuselage datum *(interp.)*. Loaded cruise needs about 5° wing angle of attack (1.3° 2D at CL 0.6 + 3.7° from AR 3.6); the fuselage then flies about 2° nose-up loaded at 13 m/s, and near level after release at 9 m/s (CL about 0.46). Final value set with the fuselage.
- Washout 0°. A rectangular wing stalls at the root first, so the ailerons stay effective. Simpler to build.
- Dihedral: see D-012 (0°).
Decided by: Claude by rule. Reverse: change the jig.

## D-006: Ailerons (tier 2, provisional)
Chord 25 % (70 mm), throw ±15° *(interp.)*, one 9 g servo each side. Decided by: Claude by rule (typical sport sizing). Reverse: change the hinge line.
**Superseded in part (2026-11-21, plan rev A):** span-wise position y = 112.5 to 437.5 mm (325 mm long), between the ribs at y = 110 and 440, gap 1 mm at each end. The old value (120 to 470 mm, 350 mm long) is not valid.

## D-002 update (2026-11-21)
Chord 0.28 m for the first model. **Decided by:** user. Final value after a throw test (Q6).

## D-007: Wing position (tier 1)
High wing. **Decided by:** user. Effect: the reservoir sits below the wing near the CG. (The old note "dihedral 2° each side" is superseded by D-012: dihedral 0°.)

## D-008: Wing attachment (tier 1)
Rubber bands over two fuselage dowels; one-piece wing. **Decided by:** user. Effect: full balsa sheeting at the centre (y = ±55 mm) and printed band rub plates at the LE and TE.

## D-009: Hard points — printed instead of plywood (tier 1)
**User's view:** 3D print the root ribs, tip ribs, servo hatches and dihedral braces, to make the build easy.
**Check:** printed PETG suits the root ribs (the 2° wedge is exact), the servo frames and hatches (exact MG90S fit), horns and rub plates. It does not suit the dihedral joint: printed layers are weak in tension across the layers and creep under a steady load. The root bending moment is 8.9 N·m at a load factor of 6. The tip ribs are lighter and absorb impact better in laminated balsa.
**Decision:** print root ribs, servo frames, hatches, horns and rub plates in PETG. Dihedral joint: continuous carbon caps (bent to 4°) + 3 mm balsa braces. Tip ribs: 3 mm laminated balsa. **Decided by:** changed from user input, with the reason above. PETG, not PLA, for the sun temperature (stage 1).
**How to reverse:** replace a printed part with a ply part of the same outline.

## D-010: Aileron servo (tier 2)
9 g metal-gear servo, MG90S (model chosen by the user). Need: hinge moment about 0.05 N·m (0.5 kg·cm) at 20 m/s and 15°, safety factor 2 → about 1.0 kg·cm. A 5 g servo gives about 0.8 kg·cm. Metal gears survive a hard landing. Cost: about 8 g for two servos against 5 g servos. **Decided by:** Claude by calculation.

## D-011: Laser cutting (tier 2)
Bambu H2D laser module (work area about 310 × 270 mm, to be checked); ribs are 280 mm long. Balsa 100 × 1000 mm sheets cut to 300 mm lengths. An outside laser cutter can use the same DXF files. **Decided by:** Claude by rule.

## D-012: Dihedral 0° (tier 1)
**User's view:** dihedral is complicated; make it 0°.
**Check:** a high wing gives an effective dihedral of its own (side-wash at the wing-fuselage junction), and the aircraft has ailerons and an experienced pilot. A flat wing then has about neutral spiral stability: the pilot must hold the bank in turns. This is acceptable without a gyro for an experienced pilot.
**Gains:** one flat building board, spar caps and sheeting one piece tip to tip, no dihedral braces, no glass tape, no wedge root rib. About 5 g lighter *(interp.)*. Span grows from 989.4 to 990.0 mm (still ≤ 1000 mm).
**Decision:** 0°. **Decided by:** user. Changes D-005 (dihedral line) and D-009 (printed root ribs removed; a 2 mm balsa centre rib instead).
**How to reverse:** a 1° to 2° dihedral needs a centre joint again (braces, wedge rib).

## D-013: Wing mass reduction set (tier 1)
Date: 2026-11-21. Stage: wing CAD rev A, before Stage A.
**Trigger:** the projection from the section areas of the plan structure gave 172 g without servos (limit 145 g, task rule: stop and ask). The D-003 estimate (137 g) did not include the 3 mm ribs, tip caps, false spar, printed parts and pushrods.
**Options:** (A) reduction set, about 154 g, new limit 155 g; (B) keep the plan, about 172 g; (C) reduction set + 1.0 mm D-box sheeting, about 145 g, D-box torsion stiffness about -33 %.
**Claude's view:** A. It keeps the D-box and the spar as planned (robustness) and removes mass where the load is low.
**Decision:** A. **Decided by:** user. Contents:
1. Larger lightening holes in all ribs, also forward of the spar (about 33 % of the rib area instead of 12 %).
2. Rib at y = ±440 in 2 mm (not 3 mm), placed at y = ±439.5 so the aileron gap stays 1 mm. Tip rib in light balsa (100 kg/m³).
3. Tip cap as a 10 mm wide outline ring (3 mm light balsa); film covers the open centre.
4. LE in medium balsa (130 kg/m³), not hard.
5. Lighter printed hatch and frame (Stage B).
6. Weigh the sheets and use light sheets (about 90 kg/m³) for the D-box and centre sheeting.
**New mass limit:** 155 g without servos. **How to reverse:** each item separately.

## D-014: Tip layout (tier 1)
**Problem:** a 3 mm tip rib at y = 493.5 ends at y = 495.0, so the tip cap has no space inside the 990.0 mm span.
**Options:** (A) tip rib inboard at y = 489 to 492, cap y = 492 to 495; (B) tip rib at y = 492 to 495, no cap.
**Claude's view:** A (the cap closes the ends of the LE, sheeting, spar and TE, and takes the cartwheel knocks).
**Decision:** A, with the cap as an outline ring (D-013). **Decided by:** user (accepted Claude's recommendation). Continuous span-wise parts end at y = ±492.

## D-015: False spar crossing (tier 1)
**Problem:** the false spar (x = 205 to 208, full span) crosses the fixed-bay ribs, the cap strips and the centre sheeting.
**Options:** (A) false spar to the outer airfoil surface; the parts that cross it divide into a front piece (to x = 205) and an aft piece (from x = 208); (B) false spar 1.5 mm below the surface, sheeting and cap strips run over it, plus a hinge-line cap strip in the aileron bays.
**Claude's view:** A (full-depth hinge face for the film and the aileron LE, no extra part).
**Decision:** A. **Decided by:** user (accepted Claude's recommendation).

## D-016: Aileron end ribs and horn rib (tier 1)
**Problem:** with ribs only at the wing stations, the horn has only film to mount on and the aileron ends are open.
**Options:** (A) 2 mm end ribs + one 2 mm horn rib at the horn station, slot-in printed horn glued to the rib side and into the aileron LE; (B) end ribs + 1.5 mm hard-balsa horn pad.
**Claude's view:** A (larger glue area, about +0.6 g for each aileron).
**Decision:** A. **Decided by:** user (accepted Claude's recommendation).

## D-017: Centre sheeting pieces and grain (tier 2)
The centre sheeting is 112 mm wide (y ±56) and the sheet is 100 mm. Grain chord-wise, joint at y = 0 on the centre rib, and divided at the false spar (D-015): 8 pieces, each 56 mm wide (x 80–205 and 208–255, top and bottom, each side). **Decided by:** Claude by rule (sheet width). **Reverse:** grain span-wise with a chord-wise joint at x ≈ 180.

## D-018: Rib holes, wire path, tip rib (tier 2)
Lightening holes at x = 21, 48, 98, 130, 160, 186; d = inner depth − 2 × 4 mm, max 26 mm (17.2 to 26.0 mm); ligaments ≥ 5.5 mm; ≈ 33 % of the rib area (D-013 item 1). Ribs ±110 and ±165 keep x 98–160 solid for the servo frame glue faces. Wire path: Ø8 hole in rib ±110 at x = 130, then through the x = 130 lightening hole (Ø22.9) of rib ±55, exit Ø10 in the bottom centre sheeting at x = 130, y = ±28. The tip rib has no holes (impact face). **Decided by:** Claude by rule (4 mm edge margin on 2 mm balsa; frame glue area). **Reverse:** change `HOLE_*` in `wing_params.py`.

## D-019: Small fits in Stage A (tier 2)
- Continuous span-wise parts (LE, sheeting, spar caps, false spar) end at y = ±492 (inner face of the tip cap): 984 mm, from 1000 mm stock.
- Spar caps: carbon outer faces at the minimum / maximum of the inner outline over x 72.6–78.6 (z = 28.579 / −7.391); gap to the sheeting ≤ 0.21 mm. Rib notches cut through to the outline.
- Cap strips: 6 mm wide, centred on the rib; at ribs ±110 / ±439.5 the aft strips are flush with the face toward the aileron (1 mm aileron gap stays clear). No cap strips on ribs 0 and ±55 (under the centre sheeting).
- Grades the plan did not give: cap strips light 100, false spar and webs medium 130, tip cap light 100, aft rib pieces as the rib.
**Decided by:** Claude by rule. **Reverse:** values in `wing_params.py`.

## D-020: Aileron and printed-part details (tier 2)
- Aileron TE wedge in medium balsa (130), not hard: lighter by 1 g, the aileron TE takes less handling than the wing TE.
- Aileron ribs full depth (no cap strips): small bays, lighter.
- Hatch 0.8 mm (plan 1.2 mm), frame ring 1.0 mm, glue tabs 6 × 2.5 × 6 mm (D-013 item 5). Thin PETG parts printed solid: infill factor 1.0 used in the mass table (conservative).
- Band rub plates 0.5 mm, 30 mm wide (y ±15), outside the film. Width depends on the fuselage and the bands *(interp.)*.
**Decided by:** Claude by rule. **Reverse:** values in `wing_params.py`.

## D-021: Hinges (tier 2)
4 CA hinges, 20 mm wide, at y = 130, 247.5, 302.5, 420 (clear of the ribs and the horn rib), slots 0.8 mm, x 200–218. Check: 120 mm² of glue in 3 mm balsa on each side → ≥ 100 N per hinge; air load ≈ 5 N per aileron. No hinge blocks needed. **Decided by:** Claude by calculation.

## D-022: Servo installation fits (tier 2)
MG90S on its side, shaft outboard, case y 118–146.5, shaft at x 138.5; 1 mm clearance to the hatch and frame; tabs screwed to two hatch lugs, so the servo comes out with the hatch. Arm r = 12.65 mm, horn 16.47 mm below the hinge, pushrod 70.5 mm at 4 mm below the skin. ±15° aileron needs ±20° servo. Horn at y = 148.1 (plan "≈ 140"; moved so the servo fits inside the frame opening with 1 mm). **Decided by:** Claude by rule. **Reverse:** `SERVO_*`, `ARM_*` in `wing_params.py`. The placeholder is replaced when the user's MG90S file arrives (tier 2).
**Update (Stage C):** hatch lugs 0.3 mm from the servo case ends (slip fit), so the wall at the servo-screw pilot hole is 1.3 mm (was 0.6 mm at a 1 mm gap). The structure clearances stay ≥ 1 mm.

## D-023: Mass limit after Stage B (tier 1)
**Trigger:** 156.3 g without servos after Stage B, limit 155 g (D-013).
**Options:** (A) accept, limit 160 g; weigh the sheets and the film and correct the mass table; (B) aileron TE light balsa and 2 mm tip cap ring, about 154 g, less robust.
**Claude's view:** A (1.3 g ≈ 0.2 % of the score, inside the ±5 g uncertainty of film and glue).
**Decision:** A. **Decided by:** user. New limit 160 g without servos.

## D-024: Foam-block wing construction (tier 1) — PROPOSED, waiting for the user
**User's idea (sketch, 2026-11-22):** a few wide foam blocks with balsa airfoil plates on their faces, hollow film-covered bays between them, spar and D-box kept, printed LE and TE in the wing. Goals: easier build, more robust, lighter, more accurate.
**Check:** no layout is lighter than rev A: +28 g to +114 g (score −4.6 to −16 %). The bays still need ribs to hold the film and the TE. Details: `design/studies/foam_block_wing.md`.
**Options:** A rev A unchanged (51 points); B user's foam blocks (49.5); C rev A + foam tip blocks + printed removable jigs (57).
**Claude's view:** C. **Decision (2026-11-22):** keep rev A unchanged as the reference, copy it, and model option B as wing rev B for a direct comparison (mass, score, gains, losses). The final choice between A and B follows the comparison. **Decided by:** user (against Claude's recommendation C; the model will give the measured numbers).
**Comparison result (2026-11-22, `design/studies/revA_vs_revB.md`):** rev B as modelled (XPS 30 hollow, PLA LE/TE) 247.7 g without servos, +91.1 g against rev A; score 166.9 → 144.8 (−13.3 %); loaded stall 9.11 m/s (R6 fails by 0.11 m/s; rev A 8.86 m/s); PLA LE/TE fail the 60 °C heat check. Best variant (ASA Aero LE + balsa TE) 206.5 g, −7.7 %, 9.00 m/s. Claude's recommendation: rev A.
**User's answer (2026-11-22):** no A/B choice. The user can build rev A, but its build is too complex for the time and money available before 10 Dec 2026 (exams; the abstract needs 5–10 construction photos). The user wants to spend the minimum before selection and build the full aircraft only after selection.
**Status:** rev B not chosen (it fails R6 and the heat check). Rev A stays the reference design. Open: a staged, low-cost build plan for the abstract photos (photos must show the real aircraft during its construction, and the aircraft must match the abstract: rules, "Abstract Submission" item 1 and General Guideline 1).

## D-025: Rev B foam (tier 1)
Date: 2026-11-22. Stage: wing rev B (D-024).
**Options (7 blocks, half ribs, ASA Aero LE/TE):** EPS 15 solid +39 g; EPS 20 solid +51 g; EPS 20 hollow +30 g; XPS 30 solid +75 g (stall 9.07 m/s, fails R6).
**Claude's view:** EPS 20 solid. **User:** XPS 30 solid. **Check:** with the user's PLA LE/TE, XPS 30 solid = +100 g → 9.13 m/s (fails R6 by 0.13). Reported to the user.
**Decision:** XPS 30, **all blocks hollow** (after the check). Wall 7 mm (tier 2, Claude): the option text "45 % removed, 10 mm walls" was wrong; 10 mm walls remove only 25–29 %, 7 mm remove 44–49 %. **Decided by:** user (foam, hollow), Claude (wall). **Reverse:** `WALL`, `RHO["xps"]` in `design/cad_revB/scripts/wing_params.py`.

## D-026: Rev B block layout (tier 1)
7 blocks with the plates at rev A rib faces: centre y ±54.5 (plates ±54.5–56), servo bays 111.5–164, mid 275.5–329.5, tips 440–490.5 (ring cap kept). Hollow bays 54 / 108.5 / 107.5 mm. Alternatives: 5 blocks (≈ −12 g, 273 mm bay), 3 blocks (≈ −18 g). **Decided by:** user ("recommended" = Claude's view). **Reverse:** `BLOCKS`, `C_FOAM`.

## D-027: Rev B ribs in the hollow bays (tier 1)
**Check:** 108 mm bays with no rib: film pillow 3.2 mm at 25 m/s (0.8 at 54 mm); hinge spar bow 1.1–5.6 mm under film tension 150 N/m *(interp.)* against a 2 mm hinge gap; D-box skin buckling margin 1.4 *(interp.)* outboard of y = 165 (no rib needed there).
**Decision:** 1.5 mm light half ribs x 78.6–205 with cap strips at y ±220 and ±385 (2.2 g). **Decided by:** user ("recommended"). **Reverse:** `HALF_RIBS`.

## D-028: Rev B printed LE/TE material (tier 1)
**Options:** LW-PLA (lightest, HDT 53 °C fails heat), ASA Aero (HDT 85 °C, buy, H2D), PETG (heaviest).
**Claude's view:** ASA Aero. **User:** "normal PLA for now but can buy later". **Check:** PLA HDT 57 °C, 3 °C below a 60 °C surface (fails R12); PLA LE + TE = 69.9 g against 11.2 g balsa.
**Decision:** model in PLA; the mass table also gives ASA Aero and LW-PLA. **Decided by:** user, risk stated (heat). **Reverse:** density only, same STL files.
Geometry (tier 2, Claude): LE in 5 segments 189.5 / 164.75 / 275.5 / 164.75 / 189.5 mm (joints at block centres y ±137.75, ±302.5; all fit the H2D, the centre piece is too long for the P1S); 14 locator keys 3 × 4 × 12 mm at the plates with 1.6 mm slots; 4 joiners 20 mm; TE x 250–280 in the fixed bays with 3 mm plate slots. Print fill: LE 0.50, TE 0.85, keys 1.0.

## D-029: Rev B hinge spar (tier 1)
Rev A balsa false spar (x 205–208, full span) in the aileron bays, with **span-wise grain**; printed TE only in the fixed bays. Printed hinge spar would be +33 g in PLA (+16 g ASA Aero). **Decided by:** delegated to Claude (the user answered "recommended" to options with no label).
Note (rev A follow-up, not changed): rev A D-015 / `wing_params.py` say "vertical grain"; a 3 mm vertical-grain spar bows ≈ 20 mm under film tension at 53 mm. A 984 mm one-piece spar from 1000 mm stock has span-wise grain; correct the rev A note.

## D-030: Rev B face plates (tier 1)
1.5 mm light balsa; stepped outline (inner outline x < 80 under the D-box, outer outline x ≥ 80); holes = the foam cavity outlines (the plate is also the cavity template); servo-block plates have only the front cavity hole (frame glue faces solid, Ø8 wire hole in plate 110); outer tip plate solid. 14 plates = 9.9 g. **Decided by:** delegated to Claude ("recommended" to options with no label).

## D-031: Rev B centre sheeting (tier 1, departs from D-008)
**Check:** saddle load on XPS 30: 30 kPa preload, 70 kPa at a 10 g landing, against ≈ 250 kPa crush *(interp.)*.
**Decision:** keep the bottom centre sheeting (saddle, wire exit Ø10 at x 130, y ±28), remove the top (−2.7 g). **Decided by:** delegated to Claude ("recommended" to options with no label; Claude's notebook view).

## D-032: Rev B detail fits (tier 2)
- Foam pieces split at the spar: front x 6–71.1 (inner outline), aft x 80.1–205 (outer outline; centre: bottom inset), TE piece x 208–250 (fixed bays, solid). Cavities cut by hot wire through a kerf in the spar face (covered by the webs).
- Servo pocket in block S: x 108–158, full width between the plates, from the lower surface to z 10.76 (servo top + 1.5 mm). Frame tabs glue to the plate faces only (the rev A cap strips under them are gone): 4 × 36 mm² of epoxy.
- Shear webs in pieces between the plates; rear web |y| ≤ 164 as rev A.
- Plate 110 wire hole lowered to z 5.0 (inside the servo pocket; rev A mid-depth z 10.88 was above the pocket roof z 10.76).
- Hinge slots at y 130 / 302.5 also cut in the foam of blocks S / M; glue these hinges with epoxy or foam-safe CA.
- Glue 14 g *(interp.)*: rev A 8 g + 4 g foam bonds + 2 g spray adhesive for film on foam (the iron melts XPS).
**Decided by:** Claude by rule. **Reverse:** `wing_params.py` rev B section.
