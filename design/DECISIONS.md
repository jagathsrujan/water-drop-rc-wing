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

## D-023: Mass limit after Stage B (tier 1) — SUPERSEDED by D-047 (no fixed mass limit)
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

## D-033: Design order — reservoir before fuselage (tier 1)
**Options:** (a) design the reservoir first, then the fuselage around it; (b) design the fuselage first, then fit a reservoir inside it.
**User's view:** (a) "design the reservoir first and then the fuselage" (2026-11-22).
**Claude's view (notebook, written before the answer):** (a). The water is 62 % of the flight mass and the largest single volume, so it sets the fuselage section at the CG.
**Decision:** (a). The reservoir envelope, its CG station and its mount interface become inputs to the fuselage stage. **Decided by:** user. **Reverse:** possible until the fuselage stage starts; after that, a reservoir change also changes the fuselage.

## D-034: Release mechanism (tier 1) — DECIDED 2026-11-22: V2 pin-latched trapdoor (hinge moved to the rear edge by D-040)
**Options:** V1 user's rotary disc gate; V2 pin-latched trapdoor; V3 radial plug; V4 cut film; V5 pinch valve; V6 butterfly; V7 inside flapper. Weighted table in `design/logs/reservoir_log.md` section 9.
**User's view:** V1 (servo turns a disc away from the opening).
**Claude's view:** V2 (87/100) ahead of V1 and V7 (78) and V4 (77). In V2 the landing load goes into the pin and the hinge, not the servo, and the seal is static. The scores are judgement; the gap is not measured.
**Proposal:** print V1 and V2 as caps for a 28 mm bottle neck (PETG, a few grams each), then do a wet drop test and measure the pull force or torque. Choose from the results. **Condition for V2:** soft flat gasket, pin pull ≤ 50 % of the servo force.
**Decided by:** user, 2026-11-22 ("lets go with claude pick"), after a review of the 3D comparison page (`design/studies/release_valves.html`). The V1 test print is not done; V1 stays the fallback if V2 fails its tests.
**Tests before the build is final:** (1) pin pull force with full water and a wet soft gasket ≤ 50 % of the servo force (≤ 8.8 N at a 10 mm arm); (2) drop test with full water, no weep; (3) the flap opens fully every time in 10 trials.
**Reverse:** change to V1 (rotary disc gate) if a test fails; the valve is a cap unit on the 28 mm thread, so the reservoir does not change.

## D-035: Reservoir container (tier 1) — DECIDED 2026-11-22: 1 L Bisleri still-water PET bottle (first answer: 1 L soft-drink bottle, not available; see the update)
**Options:** C1a thin still-water 1 L PET bottle; C1b 1 L carbonated soft-drink (CSD) PET bottle; C2 1 L spout pouch.
**User's view:** C1b, "cant we just use coke or sprite 1l bottle".
**Claude's view (before the answer):** C1 bottle over the pouch (availability before 10 Dec, rigid mount, about 22 mm bore). Between C1a and C1b no preference was formed.
**Check of the user's choice:** C1b meets every requirement. For: standard 28 mm PCO 1881 neck (the valve cap thread can be drawn now; most Coca-Cola bottles use PCO 1881 *(interp., confirm on the real bottle)*), thick wall made for internal pressure (strong at the landing), rigid and round for the mount. Cost: about 30 to 35 g *(interp., no sourced 1 L figure)*, about 5 to 10 g more than a thin still-water bottle (about 1 to 1.6 % score); the wall does not collapse, so the vent is necessary.
**Decision:** C1b. **Decided by:** user. Mass to be weighed on the real bottle. If only a 1.25 L size is sold locally, it is acceptable (more headspace, about +5 g *(interp.)*).
**Reverse:** the valve cap stays on the 28 mm thread; a still-water bottle with the same neck needs no other change.

### D-035 update (2026-11-22): 1 L soft-drink bottles are not available locally
**New fact (user):** available are 1.25 L Coke / Sprite and 1 L Bisleri (still water).
**Check:**
| Item | 1 L Bisleri | 1.25 L Coke / Sprite |
|---|---|---|
| Mass *(interp., to weigh)* | about 20 to 25 g | about 38 to 42 g |
| Score at 597 g empty (bottle 25 g in A1) | about 167.7 | about 162.7 (−3 %) |
| Headspace with 996 mL | about 44 mL (4 %) | about 300 mL (23 %): more slosh, more fuselage depth |
| Wall | Thin: can collapse as it drains → the vent can maybe go (test) | Thick: vent necessary |
| Neck | Not known (Indian water bottles often use a short neck, not PCO 1881): measure | 28 mm PCO 1881 *(interp.)* |
| Landing | Full bottle is hydraulically stiff; wall protected inside the fuselage | Strong |
**Claude's recommendation:** 1 L Bisleri, because it is lighter, smaller and may need no vent. The unknown neck is a measurement, not a risk. Buy both (about ₹80) and weigh them before the choice is final. Fallback: 1.25 L soft-drink bottle.
**Decision:** 1 L Bisleri still-water bottle. **Decided by:** user, 2026-11-22 (Claude's recommendation). Weigh it to confirm (estimate 20 to 25 g); if it is not at least 10 g lighter than the 1.25 L soft-drink bottle, the choice opens again.
**Open measurements:** mass, diameter, height, neck thread outer diameter, bore, thread pitch; bench drain test with and without a vent hole.

## D-036: Bottle ports (tier 1) — SUPERSEDED by D-037 (H3: outlet bulkhead at the bottom, fill through the neck, vent at the top)
**User's view (2026-11-22):** two valves, one at the top for loading and one at the bottom for unloading; cut holes in the bottle, fit 3D-printed valves, seal with a washer or plumbing glue / cement.
**Check:**
- The idea of a separate top fill port is good: the release valve stays closed and untouched after the inspection, the fill happens in the flight attitude (neck down), so any weep of the release valve shows at the inspection, and the same port can be the vent.
- A drilled hole for the **bottom** valve is the worst place for a new seal: it carries the full head (2.1 kPa at 1 g, 21.5 kPa at a 10 g landing) and the impact. The neck is already a thick, accurate, factory-sealed port of about 22 mm. Use the neck thread for the release valve (V2 cap): no hole.
- **Glue on PET:** PVC plumbing solvent cement does not dissolve PET, so it does not weld it; epoxy and CA bond to PET only weakly, and the thin wall flexes and peels a glued joint *(interp.: general adhesive data, test needed)*. Thus glue must not be the main seal. Use a clamped bulkhead fitting: printed inner flange + outer nut, a rubber or silicone washer on each side of the wall; a neutral-cure silicone sealant only as a second seal.
- **Top port position:** centre of the bottle base (the thickest, flattest PET area at the injection gate). The inner flange goes in through the neck, so the flange outer diameter must be ≤ the neck bore (about 21 mm *(interp.)*) and the hole about 16 mm.
- **Top port form depends on the drain test:** no vent needed → a simple screw cap on the fill port; vent needed → a vent plug on the same V2 pin line.
**Claude's proposal:** release valve on the neck (no hole); one new hole at the top for a clamped bulkhead fill/vent port.
**Decided by:** open.

## D-037: Bottle orientation (tier 1) — DECIDED 2026-11-22: H3 horizontal bottle (vent changed by D-043, D-049, D-050; fill in place by D-049)
**User's need (2026-11-22):** a vertical bottle makes the fuselage too deep.
**Options:** H1 vertical (≈300 mm), H2 tilted 35 to 45° (≈230 to 260 mm), H3 horizontal with a mid-length bottom outlet (≈105 mm), H4 two 500 mL bottles in tandem (≈235 mm). Table in `design/logs/reservoir_log.md` section 12.
**Claude's view:** H3, if the curved-wall bulkhead passes a drop test and the residual at 0 to 3° pitch is under about 10 g; H1 as the fallback. Note: H3 changes D-036 (the outlet is then a hole in the wall, not the neck; the neck becomes the fill port).
**User (2026-11-22):** "model h3" — concept model made (`design/studies/reservoir_layout.html`): depth about 125 mm, drain 11.6 s, water left 4 / 5 / 13 g at 0 / 2 / 5° pitch.
**Decided by:** user, 2026-11-22 ("h3 is good"). Conditions: drop test of the curved bottom bulkhead (no weep) and drain test (< 10 g left at 0 to 3° pitch). Fallback: H1 vertical. D-036 changes with it: outlet = bulkhead at the mid-length bottom; fill = original neck cap; vent = top bulkhead opened by the V2 pin line.

## D-038: No hole through the wing; vent at the forward top end of the bottle (tier 1) — Claude's decision, user may overrule
**User's view (2026-11-22):** "we will have to model a hole through the wing for release mechanism".
**Check:** the H3 vent bulkhead was drawn at the top on the CG station (x = 80 mm aft of the LE), directly under the main spar (x = 72.6 to 78.6) and the centre sheeting that takes the rubber-band load (y ±55, D-008). A hole there cuts the spar caps or the D-box at the point of highest bending. The vent and the release need no wing hole: the vent only needs air inside the fuselage, which is open to the outside through the outlet hole in the floor; the pin line runs inside the fuselage on the side of the bottle.
**Decision:** no hole in the wing. Move the vent to the forward top end of the cylinder (x ≈ 89 mm in the page frame, about 9 mm ahead of the wing LE). Two gains: it is clear of the wing, and it is the highest point of the bottle when the aircraft is nose-up, so the air bubble is at the vent and no water comes out of it when it opens.
**Decided by:** Claude (structure rule); confirmed by the user 2026-11-22 ("yes no wing hole"). **Reverse:** if a new reason for a wing hole appears, re-open.

## D-039 … D-046: Reservoir detailed CAD decisions (tier 1) — DECIDED 2026-11-22 by the user
Plan: `design/03_reservoir_plan.md` §5 and §7 (numbers), notebook `design/logs/reservoir_cad_log.md` §3 (Claude's view written before the questions). Each line: options → decision (who) → reason → how to reverse.

| ID | Question | Options | Claude's view | Decision (user) | Reason / reverse |
|---|---|---|---|---|---|
| D-039 | CAD tool | FreeCAD now + Fusion later; Fusion now; FreeCAD only | FreeCAD now, Fusion for the final printed parts after the tests | **FreeCAD only** (user override of the global rule "final printed parts in Fusion"; cost: no editable feature timeline for the team) | Same tool as the wing. Reverse: rebuild the printed parts in Fusion 360 from the same parameters. |
| D-040 | V2 flap hinge side (changes D-034) | front hinge (D-034); rear hinge, latch at the front | rear hinge | **Rear hinge**, latch and pins at the front edge | A front-hinged flap in the airflow trails back toward closed; a rear-hinged flap trails flat behind the outlet, open and out of the stream. Load path unchanged. Reverse: mirror the flap. |
| D-041 | Release servo position | S1 lower right corner beside the valve; S2 nose bay with a pull wire | S1 | **S1 beside the valve** | Short direct link. Cost: fuselage 110 mm wide at the valve (about +2 g). Reverse: S2 with a 100 mm wire in a tube. |
| D-042 | Outlet inner flange form | F1 oval saddle flange + short stem, outer gasket = main seal; F2 round flange; F3 grommet | F1 | **F1 oval saddle flange** (34 × 18.5 × 1.2 mm, stem Ø17 × 7.3 mm, no inner washer) | Only form that passes a 21 mm neck with a Ø14 bore (enclosing Ø19.7 vs 20.5 allowed). The 1.2 mm lip gives 2.8 / 6.8 g residual at 0 / 3°; the concept stack (2.7 mm) gave 12.4 g at 3°. Reverse: re-size after the neck is measured. |
| D-043 | Vent (changes D-037 "vent opened by the pin line"; **superseded in part by D-049 / D-050: the vent is now in the fill cap**) | A plug lifted by a line; B passive one-way vent (aquarium air check valve); C no vent if the test passes | B | **B passive one-way vent** | No line, no extra pull force or travel; it shuts when the inside pressure is higher. Bench test: crack pressure and weep. Reverse: A (plug on a line). |
| D-044 | Safety pin | SP1 second pin through the latch from the left; SP2 clip on the release pin | SP1 | **SP1 second pin, red flag** | Flap stays latched even if the servo pulls, and out of the aircraft. In for the qualifier, out before the main-round launch. |
| D-045 | Brief R13, R15, R16 | keep R16 (4–8 s) → H3 fails; change R16 | change | **Change R16**: drain ≤ 15 s, residual < 10 g at 0 to 3° pitch, release near level; R13 → horizontal (H3); R15 → bulkhead unit | H3 with Ø14 gives 11.5 s; Ø16 does not pass the neck. Q7 (release must only begin in the zone) is still open with the organizers. |
| D-046 | Fuselage interface and removal | top with the wing off; side hatch; belly hatch | top | **Up through the top, wing off** | Front stop takes the 98 N nose-in load; saddle 1 (cylinder) and saddle 2 (shoulder cone); 2 straps; 3 mm clearance round the valve so no load goes into it; fishing snap on the pin eye for the servo link. |

**Bottle measurements:** not available yet (user, 2026-11-22). The model uses the estimates in `design/cad_reservoir/scripts/res_params.py` *(interp.)*.

## D-049: Fill in place through a top fill port; vent inside the fill cap (tier 1) — DECIDED 2026-11-22 by the user
**User's need (2026-11-22):** the organizers' fill method is not clear; the reservoir must be fillable in the aircraft, without removal and re-installation each time. Also fix the fault found in the review: the forward-pointing vent valve stuck out about 28 mm past the bottle base, so the bottle could not stand on its base.
**Constraint found:** the bottle top is under the wing except about 20 mm of straight cylinder ahead of the LE (X −19.7 to 0 with the estimated profile), so only one top fitting fits there.
**Options:** (a) one top fill port ahead of the LE with a screw cap that carries the one-way vent; (b) flip the bottle (neck forward) and fill through the original neck with the aircraft held nose-up ≥ 45°.
**Claude's view (before the answer):** (a): no layout change, aircraft level during the fill, about 1 g lighter than the rev A vent, and the fault goes away because the separate vent goes.
**Decision:** (a). **Decided by:** user. (Numbered D-047 when first written; renumbered D-049 because another session used D-047 for the mass-limit decision at the same time.) Fill port Ø10 bore at X ≈ −11, top centre; screw cap with the vent inside; fill through a Ø25 hole in the fuselage top with the team's printed funnel (Ø7 spout, air ribs), aircraft level or ≤ 5° nose-up; estimated 30 to 45 s *(interp., bench test T6)*. Top removal (D-046) stays possible, because the rule has the organizers weigh the removable reservoir before and after the attempt.
**Changes:** D-043 (the vent is now in the fill cap, not a separate fitting); D-046 (in-place fill is the normal method). **Reverse:** (b) or the rev A separate vent with the elbow turned to the side.

## D-050: Vent valve inside the fill cap (tier 1) — DECIDED 2026-11-22 by Claude at the user's request ("recommend")
**Options:** (a) printed seat with small holes + silicone flap disc on the inside (umbrella type), round, about 8 mm high; (b) bought aquarium check valve on a short silicone tube from the cap.
**Decision:** (a). (First numbered D-048; renumbered D-050 with D-049.) Reason: round, so it turns with the cap; low; nothing loose on the fuselage top. Risk: a home-made flap can weep at low pressure → bench test T5. **Fallback:** (b), with a barb on the cap.

## D-047: No predetermined mass limits; bought electronics at catalogue mass (tier 1) — DECIDED 2026-11-22 by the user
**User (2026-11-22):** remove any weight limit; "we will optimize our design as we go on and need not be restricted by a predetermined weight". Also: "for stuff like motor esc battery and other electronics save their default weight since that cant be changed".
**What was in force:** no limit on the total aircraft mass. Limits on parts: wing 160 g without servos (D-023, user), reservoir ≤ 50 g without the servo (R17, Claude *(interp.)*), robustness allowance 20 to 40 g (R8, option text). A1 (440 g without the wing) is an estimate, not a limit, and stays.
**Decision:** remove the three limits. Each stage reports its mass and the score effect (score = water × 100 / empty mass); mass checks have no pass/fail. Bought electronics use the catalogue mass as a fixed value: `design/FIXED_MASSES.md` (brief R19). D-013 and D-023 stay as history.
**Not changed:** R3 (T/W ≤ 1.5, rule). R6 (loaded stall ≤ 9.0 m/s at ρ 1.05, Claude *(interp.)*) stays: the user kept it (2026-11-22, "since we have already modelled the wing let it be there"). Reason: with rev A (8.86 m/s at 1593 g, stall ∝ √mass) it allows about 1644 g loaded, about 648 g empty, about 50 g above the present 597 g estimate. R6 is a hand-launch safety criterion, but in effect it is the real cap on the total mass for this wing.
**Effect on open checks:** reservoir key check 8 (47.75 g, 50.65 g with the front stop) is now a reported value, not a pass/fail.
**Decided by:** user. **Reverse:** put limits back in R8, R17 and the wing key check 7.

## D-051: Belly 6 mm lower so the valve is recessed (tier 1) — DECIDED 2026-11-22 by the user
**Problem found at the final check (Claude):** the V2 lugs, hook tab and hinge knuckles reach Z ≈ −113.5 and the flap −111.5, below the assumed belly line Z −111. At a full-water qualifier landing the valve touches the ground first and the load goes into the valve and the 0.3 mm PET seal (against R14 and the "no load into the valve" rule of D-046).
**Options:** (a) belly 6 mm lower (outer skin Z −117, floor inner −115.5; depth belly to wing 98 → 104 mm, about +1 g of side panel); valve recessed 3.5 mm; belly opening to 15 mm aft of the hinge so the flap still opens to about 158°; (b) two belly skids 6 mm deep beside the opening (about +2 g, more drag).
**Claude's view:** (a): no parts outside the fuselage line, less drag, and it also gives room to stand the release servo upright (see T2-30 in the CAD log).
**Decision:** (a). **Decided by:** user. New key check 11: in the closed state no reservoir or servo part is within 3 mm of the ground plane Z −117. **Reverse:** (b) skids.

## D-052: Fuselage concept (tier 1) — DECIDED 2026-11-22 by the user: U, printed pod + twin carbon tube boom
**Options** (notebook `design/logs/fuselage_log.md` §4, masses to the tail without the tail surfaces, interp.): U printed pod (PLA for the Bengaluru tests, ASA Aero for the zonal) + 2 × Ø8/6 carbon tubes ≈ 110 g; A full balsa box ≈ 84 g; B balsa pod + twin tubes + printed PETG hard points ≈ 95 g; H hybrid pod (balsa sides, printed nose/formers) + twin tubes ≈ 102 g.
**Criteria:** first weights (brief): mass 5, landing strength 4, repair 3, heat 2, build effort 3, interface accuracy 3 → A 82, U 77, H 74.5, B 74. User's criteria ("easy to build, high strength, good score"): build 5, strength 5, mass 4, repair 3, heat 2, interfaces 3 → B 89, A 87, H 85, U 84 (B build 3 → 4 and strength 4 → 4.5 corrected with reasons, see the notebook).
**User's view (first):** "3D print using normal PLA, replace it with ASA Aero if we get selected; balsa if it is very much better in strength; I want to try a dual carbon boom". Reference photos: printed pod, tractor nose motor, high wing on crossed bands, two carbon tubes side by side, conventional tail with servos at the tail.
**Claude's view:** first A (notebook §2.2); with the user's criteria B (balsa pod + twin tubes).
**Decision:** **U** — printed pod, twin Ø8/6 carbon tubes side by side, tractor nose motor, conventional tail with elevator and rudder (R22). **Decided by:** user (preference between options that all meet the brief; no mass limit, D-047).
**Cost (as told to the user at the decision):** empty ≈ 598 g (interp.), score ≈ 166.6: −2.5 % against B, −4.3 % against A.
**Cost corrected 2026-11-22 (after the decision, plan 04 geometry, pod 505 mm, skin by area, tail surfaces with film and printed sockets/tail block added to all concepts):** B ≈ 623 g (score 159.8); U in ASA Aero (0.53–0.80 g/cm³, Bambu: 50–75 % of ASA) ≈ 628 g with a 0.45 mm single wall (−0.7 %), ≈ 650 g with 0.5 mm sides and 0.8 mm floor and nose (−4.1 %, loaded stall 9.01 m/s = R6 limit), ≈ 666 g with 0.8 mm everywhere (−6.4 %). Normal-PLA prototype ≈ 735 g: loaded stall 9.24 m/s, **R6 fails** for the test flights; LW-PLA (in the workshop) ≈ 635 g, 8.97 m/s. The user is asked to confirm D-052 with these numbers. PLA prototype ≈ +30 g more (Bengaluru tests only, R25; CG re-trim when the material changes). ASA Aero printed density not known: a weighed 100 mm test section corrects the estimate.
**How to reverse:** B — same layout, the pod as a laser-cut balsa box; the tube sockets, tail block and tail stay the same.

## D-052 update (2026-11-22): user confirms U with the corrected masses; prototype in normal PLA (user override of R6 for the test aircraft)
**Asked with:** U ASA Aero 628–650 g (score −0.7 % to −4.1 % against B 623 g); normal-PLA prototype 735 g (loaded stall 9.24 m/s, R6 ≤ 9.0 fails); LW-PLA prototype 635 g (8.97 m/s). Claude recommended U with an LW-PLA prototype.
**Decision:** U, prototype in normal PLA for the Bengaluru tests, ASA Aero for the zonal (same geometry). **Decided by:** user. **Risk:** the test aircraft breaks R6 by 0.24 m/s with full water (harder hand launch, stall near the launcher). Mitigation and acknowledgement: see the next entry when answered. The CAD does not change; the mass table reports both materials.

## D-053: Front wing hold-down — carbon side stubs (tier 1, changes the front dowel of D-008) — DECIDED 2026-11-22 by the user
**Problem:** the bottle base (X −25.7) lifts out upward with the wing off (D-046); a through front dowel or a fixed deck between X −27 and 0 blocks it.
**Options:** (a) carbon stubs Ø4 out of each side wall at X ≈ −6, Z −24; (b) through dowel at X ≈ −40 over the hatch (bands off for each battery change and to open the hatch); (c) through dowel at X −6 (blocks removal, not valid).
**Claude's view:** (a). **Decision:** (a). **Decided by:** user. **Effect:** the bands cross the wing LE at y ≈ ±50 → the wing LE/TE rub plates move from y ±15 to about y ±40…±60 (wing rev A.1 follow-up, not in this stage). Rear dowel stays a through dowel at X 295. **Reverse:** (b).

## D-054: Launch grip — palm under the belly at the CG (tier 1) — DECIDED 2026-11-22 by the user
**Options:** (a) under the belly at X 40–120, fingers on the sides; (b) on the pod at X 290–330, 230 mm aft of the CG (≈ 3.5 N·m at the wrist with 1.57 kg); (c) finger recesses on the left side (the right side has the release servo).
**Claude's view:** (a). **Decision:** (a). **Decided by:** user. **Effect:** the floor between the saddles and the side walls at X 40–120 are the grip zone (stiff floor grid, no sharp edges at the belly opening, safety-pin flag clear of the fingers). **Reverse:** (c) on the left side.

## D-056: Nose hatch and fill — magnet hatch, fill with the hatch off (tier 1, detail of D-049) — DECIDED 2026-11-22 by the user
**Options:** (a) magnet hatch X −200…−2 with a Ø22 fill hole + printed cap key; (b) the same hatch with no hole: lift it, turn the cap by hand, fill, close.
**Claude's view:** (b) (with D-053 a, the hatch comes off with the wing on). **Decision:** (b). **Decided by:** user. **Changes:** R24 (no Ø22 hole) and the fill-hole line of reservoir plan §13 (note added). The in-place fill of D-049 stays (the reservoir is not removed). **Reverse:** (a).

## D-057: Stabilizer height — cruciform tail, stab at Z ≈ +45 (tier 1) — DECIDED 2026-11-22 by the user
**Problem:** wing wake centre-line at the tail (X 680) from Z +28 (stall) to −59 (empty, 18 m/s); loaded cruise −19 to −46. A stab on the tubes (Z −32) sits in it in loaded cruise; a stab below it (Z ≤ −65) strikes the ground at a 6° nose-up touchdown.
**Options:** (a) cruciform, stab through the fin at Z ≈ +45; (b) T-tail, Z ≈ +130; (c) on the tubes, Z −32 (reference photos).
**Claude's view:** (a): clear by ≥ 16 mm at the stall and ≥ 45 mm in loaded cruise; ≈ +4 g; elevator pushrod up the fin ≈ 80 mm. **Decision:** (a). **Decided by:** user. **Reverse:** (b) (fin stiffer) — not (c).

## D-052 risk acknowledgement (2026-11-22): PLA test aircraft flies with the full 1000 mL — user override, risk accepted
**Asked:** accept the risk with the mitigation "≤ 900 mL on the Bengaluru test flights (stall ≤ 9.0 m/s), 1000 mL only in the ASA Aero aircraft", or accept the full 1000 mL, or use LW-PLA.
**Answer:** "Accept, full 1000 mL". **Recorded risk:** loaded stall ≈ 9.2 m/s (735 g PLA estimate; ≈ 9.2 m/s at 728 g with the built-up tail) against R6 9.0 m/s on the test flights: higher throw speed needed, stall near the launcher at a weak throw. The user acknowledged it explicitly. Not reopened unless new evidence (weighed prototype, throw-speed video) appears.

## D-055: Tail surface build — built-up balsa + film (tier 1) — DECIDED 2026-11-22 by the user
**Options:** built-up balsa frame + ribs + film ≈ 14 g; 2 mm sheet with 30 % holes + film ≈ 18 g; 3 mm sheet + film ≈ 25.5 g; printed ≈ 30 g+.
**Claude's view:** built-up. **Decision:** built-up (laser-cut frame and ribs, film). **Decided by:** user. **Effect:** with the cruciform (+4 g) the tail is ≈ 18 g; the nose group moves from X ≈ −166 to ≈ −137 (ASA Aero) for CG X 80; first firewall position X −170 (F-D sets the final value). Empty ≈ 642 g ASA Aero mid wall (score 155.1), ≈ 728 g PLA prototype. **Reverse:** 2 mm sheet.

## Gate 3 (fuselage plan) — PASSED 2026-11-22
User: "Approve, start". Plan `design/04_fuselage_plan.md`. Execution by an Opus subagent at xhigh effort, one stage at a time (user instruction 2026-11-22).

## D-058: Safety-pin flag at the reservoir lift-out — pull the pin first (tier 1) — DECIDED 2026-11-22 by the user
**Problem (stage F-A check f):** the flag of the safety pin goes out through the left side-wall hole (X 54, Z −110.5, §13); with the pin in, the reservoir cannot lift out (contact at dz 0). Without the flag the lift-out sweep is clear to +120 mm.
**Options:** (a) pull the safety pin and flag out through the side hole before the lift-out (ground task), re-insert it from below out of the aircraft; (b) vertical slot X 44–64 from the hole to the wall top (weakens the wall in the grip zone); (c) flag down through the belly opening (changes §13).
**Claude's view:** (a). **Decision:** (a). **Decided by:** user. **Procedure:** wing off → hatch off → unclip the servo snap → pull the safety pin by the flag → lift the reservoir → re-insert the safety pin for the weigh-in and transport. The release pin (captive) keeps the flap latched during the lift-out. No model change; the lift-out check runs without the safety pin. **Reverse:** (b).

## D-059: Release-servo arm clearance — local wall pocket with a stiff wall (tier 1) — DECIDED 2026-11-22 by the user
**Problem (stage F-A):** the arm swing (Y max 53.26, plane Z −110.5) is 0.9–1.0 mm from the right side wall (inner face 54.1–54.3); the rule for moving parts is ≥ 3 mm (T2-8). The launch grip (D-054) puts fingers on this wall; a 0.5 mm wall can move > 1 mm and jam the arm.
**Options:** (a) local outward pocket at X 52–77, Z −113…−107, inner face ≥ Y 56.3, wall 1.2 mm (outer ≈ Y 57.5); (b) accept 0.9 mm; (c) move the servo ≈ 2 mm inboard (reservoir change).
**Claude's view:** (a). **Decision:** (a). **Decided by:** user. **Effect:** belly locally ≈ 115 mm wide at Z −113…−107 (the wing seat stays 110: R18 / §13 "≤ 110 at the wing saddle" is met); ≈ +0.5 g. Built in stage F-B. **Reverse:** (c).

## D-060: Pod structure (stage F-S) — objective, window cover, strength against mass, method (tier 1) — DECIDED 2026-11-22 by the user
**Problem:** the user asked for printed internal cross bars and a lighter pod shell (windows or topology optimization). Notebook `design/logs/fuselage_structure_log.md` §5–§7. Bound before FEM (F-A shell): side windows net ≈ 3–5 g ASA Aero / 6–10 g PLA; skins 0.8 → 0.5 mm (nose, hatch, floor, aft-cone bottom) gross ≈ 17 g ASA Aero / 33 g PLA. ASA Aero (foamed 0.65, interp.) is ≈ 3.1 × less stiff than PLA in the same geometry, so it sets the strength.
**Options:** objective (mass / stiffness / both); window cover (self-adhesive clear film or tape / iron-on film / open); trade-off (strength first: keep 0.8 mm floor and nose, windows only / balanced: all skins 0.5 mm + ribs where the FEM needs them + side windows, FoS 1.5, frame buckling ≥ 2.0 / mass first: FEM minimum, smaller margins); method (FEM-guided layout / own BESO-type script / BESO macro download).
**User's view:** asked for Claude's recommendation on each.
**Claude's view (written in the notebook before the questions):** mass is the objective with stiffness limits (buckling, thumb press, tail stiffness); self-adhesive clear film or tape (no heat: PLA softens at 60 °C; repair at the venue; closed cavity); balanced; FEM-guided layout (the skin is already one printed line thick, so a removal loop gives the same map as the stress and strain-energy envelopes; no download).
**Decision:** all four recommendations. **Decided by:** user ("Accept all 4"). **Effect:** the skin thickness change (0.8 → 0.5 mm) is a recommendation to the fuselage session, which owns `fus_params.py` (T2-4, F-T2-6, F-T2-7). **Reverse:** strength first (keep 0.8 mm floor and nose).

## D-061: Release-valve flap stop at the belly-opening edge (tier 1) — DECIDED 2026-11-23 by the user
**Problem:** stage F-B check: the open flap (150° pose) is 1.80 mm from the aft edge of the belly opening; the brief asks ≥ 2 mm for features. The opening `FLOOR_HOLE_RECT` X 47…115 is a reservoir value (`res_params.py`). Travel in the model (hinge X 100, Z −111): 150° 1.80 mm, 153° 0.96, 156° 0.12, 158° contact. The reservoir has no flap stop, so the flap always swings until it hits the skin. The water stream is free from 80° to 180° (reservoir check 4).
**Options:** (a) keep X 115, accept 1.8 mm; (b) move the aft edge to X 116 (contact at about 159°, reservoir model run again); (c) keep X 115 and make the aft edge the flap stop with a local reinforcement.
**User's view:** asked "what is better".
**Claude's view:** (c). Option (b) only moves the impact by about 2° and changes a reservoir interface for no gain in flow.
**Decision:** (c): opening stays X 47…115; flap stop = aft edge of the opening at 157°; lip 1.2 mm total (floor 0.8 + 0.4) over X 115…121, Y ±24 (`FLAP_STOP_LIP`, +0.11 cm³ = 0.14 g PLA). **Decided by:** user ("Yes, add the lip"). **Reverse:** set `FLAP_STOP_LIP` thickness 0 and run `run_all.py`.

## D-062: Stage F-B departures from the brief accepted as built (tier 1) — DECIDED 2026-11-23 by the user
**Problem:** three items in stage F-B differ from the brief or from D-059 (notebook `fuselage_cad_log.md`, Stage F-B §6).
**Items:** (1) D-059 pocket cavity Z −114.5…−106.5 instead of −113…−107: arm vertical clearance 3 mm (D-059 values: about 1.7 mm); bulge Y max 57.5 at X 51.4…77.6, Z −115.7…−105.3. (2) Firewall flat (laser cut) instead of tilted; 2° down / 2° right thrust by a printed wedge spacer in F-D. (3) Crossed rubber bands 1.32 mm from the aft deck at X 280.8 (band lines estimated): accepted, with a rub strip (tape) on the deck at assembly, not modelled.
**Claude's view:** accept all three (reasons above).
**Decision:** accept all three as built. **Decided by:** user ("Accept all 3"). **Reverse:** (1) set `POCKET_Z` to (−113, −107); (2) tilt the firewall in `build_stageB.py`; (3) raise `DOWEL_Z`. Then run `run_all.py`.

## D-063: Boom tubes Ø10/8 instead of Ø8/6 (tier 1) — DECIDED 2026-11-23 by the user
**Problem:** stage F-C built the twin boom tubes as Ø8/6 (D-052, plan §6.2). The user asked for hollow carbon tubes of 10 mm OD and 8 mm ID.
**Numbers (2 tubes, 489.9 mm each, carbon 1.55 g/cm³):** Ø8/6: 33.4 g, I = 137 mm⁴, stress 109 MPa at the 7.5 N·m design moment (margin 5.5). Ø10/8: 42.9 g (+9.5 g), I = 290 mm⁴ (2.1× bending and torsion stiffness), 65 MPa (margin 9.3). Score at about 642 g empty ASA Aero: 155.1 → about 152.9 (−1.4 %).
**Claude's view:** Ø8/6 meets the strength requirement; Ø10/8 is a stiffness choice (flutter, elevator authority, handling) that costs 9.5 g. Classified as a preference between options that meet the brief: followed.
**Decision:** Ø10/8. **Decided by:** user ("use a hollow one of 10mm od and 8 mm id"). **Effect:** `TUBE_OD/TUBE_ID` 10/8; socket bores and tail-block bores Ø10.3; tail-block collars and guide clips follow. **Reverse:** `TUBE_OD, TUBE_ID = 8.0, 6.0` in `fus_params.py`, run `run_all.py`.

## D-064: Pod structure load set and design material (tier 1) — DECIDED 2026-11-23 by the user
**Problem:** the F-S baseline FEM (pod shell + F-B members, no ribs) gives stress utilizations of 6 to 65 in ASA Aero 0.65 (LC3 65, LC1b/c 22–24, LC5 16, LC8 grip 16). Several loads are estimates; they decide the rib mass. Notebook `fuselage_structure_log.md` §3.
**Questions and answers:** launch grip → palm under the belly **and** a firm side grip; landing surface → not known ("let's not compromise" on the belly landing); band preload → Claude's default; design material → ASA Aero 0.65.
**Decision (limit loads; ultimate 1.5 × limit):** LC1a/b/c belly landing 10 g at the contact, unchanged (hard surface assumed); LC2 nose-in 10 g + 5 g down unchanged; **LC3 hand launch 5 g + 1 g with a finger squeeze 20 N each side (was 40 N)** on the palm grip; LC4 motor 12 N + 0.3 N·m; LC5 band preload 50 N total; LC6 3 g; LC7a/b/c tail loads; LC8 thumb 10 N, 2 mm limit only on frames, lips and the grip zone (skin panels between ribs may flex). Strength, buckling and stiffness criteria of `fuselage_structure_log.md` §4 for **ASA Aero 0.65 (foamed, interp.)**; the PLA test pod then has about 3× margin. **Decided by:** user (answers to the load review). **Reverse:** change the load values in `structure/fem/pod_model.py` and run the study again. **Open:** a weighed coupon test of foamed ASA Aero (§2 item 4) refines the material values.

## D-065: Pod structure study (stage F-S) removed (tier 1) — DECIDED 2026-11-23 by the user
**Problem:** the F-S study (printed ribs, frames and film-covered windows, FEM-guided; D-060, D-064) moved to the Windows PC. ANSYS MAPDL had no valid licence there; the CalculiX model ran after fixes (shell normals, load balance, mesh slivers, rib tagging), but the first rib design D1 (+18 g ASA Aero) still had stress utilisations up to 13 and the next iteration D2 added about 11 g more.
**Decision:** roll back the study and remove it: `design/cad_fuselage/scripts/fus_struct.py`, the folder `design/cad_fuselage/structure/` (FEM scripts, results, pictures, hand-off), `design/logs/fuselage_structure_log.md` and `START_PROMPT.md` are deleted. The fuselage CAD stays as built in F-A … F-C (`Fuselage_revA.FCStd`, `run_all.py`; it never used `fus_struct`). D-060 and D-064 stay as history only; their notebook links point to the deleted notebook (git history, commit fcb6963). **Decided by:** user ("roll back all the design changes from making holes and doing fea … reset it to just CAD"; scope: "also remove the whole study"). **Reverse:** restore the files from commit fcb6963; the Windows work of 2026-11-23 is in a backup patch outside the repository (`C:\Projects\fs_work\backup_fs-calculix_2026-11-23`).
