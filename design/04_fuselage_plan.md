# 04 — Fuselage and tail: modelling plan (rev A)

Status: **approved, gate 3 passed 2026-11-22** (user: "Approve, start"); masses corrected after gate 2 (§5); D-052…D-057 decided (D-055 built-up tail; PLA test aircraft with full water: risk accepted by the user). Gate 1 (brief R20–R26) and gate 2 (concept U, D-052) passed.
Decisions in force: D-007 high wing, D-008 rubber bands on 2 dowels (front dowel: see D-053), D-033 reservoir first, D-039 FreeCAD, D-046 top removal, D-049 in-place fill, D-051 belly Z −117, **D-052 printed pod + twin Ø8/6 carbon tubes, tractor nose motor, conventional tail with elevator and rudder**.
Binding interface: `design/03_reservoir_plan.md` §13 (and §14 as built). Notebook: `design/logs/fuselage_log.md`. Calculation: `design/calc/fuselage_sizing.py`.
Execution: Opus subagent, effort xhigh (user, 2026-11-22), one stage at a time; checks and every user question by the main session.

## 1. Frame and datum
- Wing frame: origin at the wing LE on the centreline, X aft, Y right, Z up. Fuselage datum horizontal; wing at +3° (D-005).
- Wing lower surface at +3° (SD7062 × 280, sheeting included), the wing seat line:

| X | 2 | 5 | 10 | 20 | 40 | 60 | 80 | 100 | 130 | 160 | 200 | 240 | 260 | 280 (TE) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Z | −3.8 | −5.5 | −7.1 | −9.2 | −11.4 | −12.5 | −13.0 | −13.1 | −12.9 | −12.4 | −11.9 | −12.2 | −13.0 | −14.7 |

## 2. Parametric link to the reservoir
- The fuselage scripts import `design/cad_reservoir/scripts/res_params.py` and `result_stageA.json` and read every §13 value from there: `BELLY_Z`, `FLOOR_Z`, `FLOOR_HOLE_RECT`, `FILL_X_C`, saddle X, front stop X, servo position, pin X/Z, bottle base X. No §13 number is typed again in the fuselage files.
- One fuselage parameter file `design/cad_fuselage/scripts/fus_params.py` holds all fuselage numbers. If the bottle is measured and moves in X, `run_all.py` of the reservoir and then of the fuselage rebuilds both.
- The reservoir and the wing are shown in the fuselage model as reference bodies (imported from `Reservoir_revA.step` and `Wing_revA.step`, wing turned +3° about Y at the origin). They are not in the fuselage mass table.

## 3. Layout (stations in X, mm; *(interp.)* = estimate)

| Station | X | Item |
|---|---|---|
| Spinner tip / prop plane | ≈ −215 / −205 | folding prop 10 in, spinner Ø38 *(interp., stage 3)* |
| Motor | −200 … −173 | 2212-class placeholder Ø28 × 30, X-mount; thrust line Z −50, 2° down, 2° right (T2) |
| Firewall | −173 … −170 | 3 mm ply insert in a printed slot of the nose section; **X set by the CG check (F-D)**, first value from the calc |
| ESC | −165 … −120 (beside or under the battery) | behind the firewall, air in through the nose ring, out through a vent in the hatch |
| Battery bay | −165 … −35 (battery centre first value X −92) | 3S 1000 mAh placeholder 72 × 35 × 22, on a hook-and-loop tray, slide range ±30 for CG trim |
| Front band stubs (D-053 option a) | −6 | carbon rod Ø4 × 14 out of each side wall at Z −24 |
| Front stop former | −27.2 … −24.2 | 3 mm balsa insert (as the reservoir model P12c) in a printed slot (§13), Ø50 hole, takes 98 N nose-in |
| Nose hatch | −165 … −2 | printed, magnets; covers battery, bottle base and fill cap (D-056) |
| Fill cap | −11 (Y 0) | cap top Z −7; hatch top Z −4 there |
| Saddle 1 / saddle 2 | 8 … 20 / 160 … 172 | printed into the pod floor (T2: one part with the pod), feet on Z −115.5, strap slots |
| Release servo / servo wall | 50 … 90 (right) | inner face Y ≥ 53.5, outer Y 55 |
| Belly opening | 47 … 115, Y ±20 | §13 |
| Safety-pin flag hole | 54, Z −110.5 (left) | Ø10 *(interp.: ring Ø8 passes)* |
| Wing seat | 0 … 280 | side-wall tops follow §1 table, 8 mm inner lip, 1 mm foam tape |
| Aileron leads | ≈ 130 | slots in the seat lip, down the upper corners beside the bottle |
| Tail servos | 195 … 235, Y ±(20 … 45) | 2 × 9 g class beside the bottle neck, outside the bottle's lift-out envelope (T2) |
| Receiver | ≈ 215, floor | |
| Rear dowel | 295, Z −22 | Ø5 birch or carbon, through |
| Boom sockets | 230 … 300 | printed socket block, 2 × Ø8 bores, 70 mm engagement |
| Pod end | ≈ 300 | tail cone closes round the tubes |
| Twin tubes | 230 … ≈ 720 | 2 × Ø8/6 carbon, Y ±16, axis Z −40, straight and parallel |
| Tail block | ≈ 640 … 720 | printed, clamps both tubes, stab seat, fin socket |
| Stabilizer | LE ≈ 647, chord 132, span 490 | Sh 6.47 dm² (Vh 0.50 at l_h 600); **height per D-057** (recommended Z ≈ +45 on the fin, cruciform); elevator 30 % |
| Fin | root chord 110, tip 85, height 165 above the tubes | Sv 1.60 dm² (Vv 0.035); rudder 35 %; carries the stab if D-057 (a) or (b) |

Pod cross-section: outer Y ±55 and belly Z −117 from X −35 to 200; the top is the wing seat (X 0–280) or the hatch at Z −4 (X −200 to −2). Nose taper from 110 × 113 at X −35 to about 56 × 56 at the firewall X −170 (centre Z −50). The firewall X is a parameter (first value −170 after D-055: nose group centroid X ≈ −137 for CG X 80). Aft taper from X 200: the bottom rises from Z −117 to about −60 at X 300; the section ends at about 60 × 44 round the socket block.

## 4. Parts

| # | Part | Material | Build |
|---|---|---|---|
| F1 | Pod nose section (X −173 … −24): firewall, battery tray rails, ESC mount, hatch seat | PLA (tests) / ASA Aero (zonal) | print |
| F2 | Pod centre section (X −24 … 175): front stop slot, saddles, floor with belly opening and strap slots, servo wall, flag hole, wing seat lip, band stub bosses | same | print |
| F3 | Pod aft section (X 175 … 300): tail cone, tail servo bay, receiver tray, rear dowel bosses, boom socket block | same | print |
| F4 | Nose hatch with magnets (4 × Ø6 × 2) | same | print |
| F5 | Belly skids, replaceable, 1.5 mm, ahead of and behind the belly opening | PETG | print |
| F6 | Front band stubs Ø4 (D-053 a), rear dowel Ø5, 3 mm ply firewall, 3 mm balsa front stop | carbon / birch / ply / balsa | bought, laser cut |
| F7 | Twin tubes 2 × Ø8/6 × ≈ 490 | carbon pultruded | bought |
| F8 | Tail block (tube clamps, stab seat, fin socket, pushrod exits) | PETG (tests and zonal) | print |
| F9 | Stabilizer + elevator, fin + rudder (cruciform, stab at Z ≈ +45), CA hinges, horns | built-up balsa + film (D-055) | laser cut / build |
| F10 | Pushrods 2 × (Ø2 carbon + steel ends), guides clipped on the tubes | carbon, steel, PETG | bought / print |
| F11 | Placeholders: motor, folding prop + spinner, ESC, battery, receiver, 2 tail servos | — | reference |

Joints between F1/F2/F3: printed sleeves 10 mm long at the formers, glued (T2). Split chosen so that each section prints on the P1S (256 mm) and on the H2D.

## 5. Mass and CG (`fuselage_sizing.py`, concept U, corrected 2026-11-22)
- Pod mass by area (skin 0.167 m², 505 mm; + inner ribs, floor grid, hatch rim, socket block; + ply firewall and balsa front stop):

| Pod wall | PLA 1.24 | LW-PLA 0.55 *(interp.)* | ASA Aero 0.53 / **0.65** / 0.80 (Bambu: 50–75 % of ASA) |
|---|---|---|---|
| 0.45 single wall | 146 g | 69 g | 67 / **80** / 97 g |
| 0.5 sides, 0.8 floor + nose | 187 g | 87 g | 85 / **102** / 124 g |
| 0.8 everywhere | 219 g | 101 g | 98 / **118** / 144 g |

- Empty mass (all other items: wing 184, reservoir 47.5, release servo 13.4, tubes 33, tail surfaces 25.5, printed tail block 8, tail servos 18, pushrods 7, receiver 8, wiring 15, nose group 180 g):
  - U, ASA Aero: **628 g** (0.45 wall, score 158.6) / **650 g** (0.5/0.8, score 153.3) / **666 g** (0.8, score 149.5). B for reference: 623 g, 159.8.
  - U prototype in normal PLA (0.5/0.8): 735 g → loaded stall 9.24 m/s: **R6 fails** for the Bengaluru test flights. LW-PLA prototype (in the workshop): 635 g, 8.97 m/s.
- **R6 margin:** R6 (loaded stall ≤ 9.0 m/s at ρ 1.05) allows about 648 g empty with wing rev A. The 0.5/0.8 ASA Aero pod is on this limit; the wall (T2-4) and the weighed test section decide.
- CG at X 80 needs the nose group (motor, prop, ESC, battery, 180 g) at X ≈ −166 with the tail servos in the pod; at X ≈ −214 with the servos at the tail. **Tail servos in the pod shorten the nose by about 48 mm** (T2-1).
- PLA test prototype (user, D-052 update): 735 g → loaded stall 9.24 m/s with 1000 mL. With ≤ 900 mL the loaded mass is ≤ 1644 g and the stall ≤ 9.0 m/s (mitigation proposed).
- R3: static thrust ≤ 1.5 × empty ≈ 940 to 1000 g (motor choice, stage 3).

## 6. Main design results already calculated
1. Tail volume (R21): Vh 0.50 gives SM 11.4 % (downwash 0.55) and 7.1 % (0.65) at CG X 80. The CG must not go aft of X 80 (the fill cap has 0 mm margin at the LE rule, so the bottle can move forward only).
2. Twin tubes Ø8/6: design moment 7.5 N·m (5 N tail load × 0.5 m × 3) shared by 2 tubes → 109 MPa against ≈ 600 MPa *(interp.)*: margin 5.5. Ø6/4 gives margin 2.7 but less stiffness; Ø8/6 kept (stiffness for elevator authority and flutter).
3. Front hold-down conflict: the bottle base (X −25.7) lifts out upward; a through front dowel or a fixed deck between X −27 and 0 blocks it. Side stubs at X −6 hold the bands outside |Y| 55, so nothing crosses the opening and the bands never cross the hatch (D-053).
4. Fill access (decided D-056 b: hatch off, no hole): the cap is Ø18 with flutes; through a Ø22 hole with the hatch top 3 mm above the cap, fingers cannot turn it. Either a printed cap key (ground tool, like the funnel) through the Ø22 hole, or the fill with the hatch off (D-056).
5. Wing wake at the tail (X 680), centre-line Z for downwash 0.45 / 0.55 / 0.65: loaded 10 m/s +0 / −11 / −23; loaded 12 m/s −19 / −28 / −36; loaded 15 m/s −35 / −40 / −46; empty 12–18 m/s −46 to −59; wing stall +29 / +12 / −5. A stab on the tubes (Z ≈ −32) is in the wake in loaded cruise. A stab below the wake (Z ≤ −65) strikes the ground at a 6° nose-up touchdown (ground at the tail Z −67). A stab at Z ≈ +45 on the fin clears the wake by ≥ 16 mm at the stall and ≥ 45 mm in loaded cruise (D-057).
6. Ground contact: skids 1.5 mm under the belly → valve 5 mm above the ground (§13 check 11 needs ≥ 3 mm). Folding prop. The tubes (Z −40) and the tail are well above the belly line in a belly landing.

## 7. Decision points (tier 1 = I stop and ask; tier 2 = I decide and report)

**Decided by the user 2026-11-22:** D-052 confirmed (U; prototype in normal PLA, see §5 and DECISIONS), D-053 (a) side stubs, D-054 (a) grip under the belly, D-056 (b) fill with the hatch off (no hole), D-057 (a) cruciform, stab Z ≈ +45. D-055 built-up balsa + film; PLA test aircraft with the full 1000 mL (risk accepted by the user, R6 override for the tests); gate 3 passed.


| ID | Decision | Tier | Options | My recommendation and reason |
|---|---|---|---|---|
| D-053 | Front wing hold-down (changes D-008 front dowel) | 1 | (a) carbon stubs Ø4 out of each side wall at X ≈ −6, Z −24; (b) through dowel at X ≈ −40 over the hatch: the bands must come off for each battery change and to open the hatch; (c) through dowel at X −6 (blocks bottle removal: not valid) | (a). Nothing crosses the top opening; the hatch opens with the wing on; the bands stay away from the fill cap. Cost: the band crosses the LE at y ≈ ±50 → wing rub plates move from y ±15 to y ±40…±60 (small wing change, rev A.1). |
| D-054 | Launch grip | 1 | (a) palm under the belly at the CG (X 40–120), fingers on the sides; (b) on the pod behind the wing TE (X 290–330, ≈ 60 wide), 230 mm aft of the CG; (c) finger recesses in the left side under the wing | (a). Hand on the CG: no pitch torque at the throw (b gives 3.5 N·m at the wrist with 1.57 kg). The belly there is the stiffest part (floor + saddles); the flap is recessed 3.5 mm and latched, palm pressure pushes it closed. (c) conflicts with the release servo on the right. |
| D-055 | Tail surface build | 1 | (a) 3 mm light balsa sheet + film ≈ 25.5 g; (b) 2 mm sheet, 30 % holes, film ≈ 18 g; (c) built-up balsa frame + ribs + film ≈ 14 g; (d) printed LW-PLA/ASA Aero ≈ 30 g+ | (c) if the team accepts the build time (laser-cut frame, one evening); else (b). Each gram at the tail also lengthens the nose: (c) against (a) saves ≈ 11.5 g at the tail and ≈ 30 mm of nose. |
| D-056 | Nose hatch and fill | 1 (detail of D-049) | (a) one magnet hatch X −200…−2 with a Ø22 fill hole + printed cap key (ground tool); (b) the same hatch, no hole: lift the hatch (magnets), fill, close | (b). The hatch comes off in 1 s with the wing on (D-053 a), so the cap is turned by hand; no hole, no key to lose, less drag. Fill time unchanged. |
| D-057 | Stabilizer height (wing wake, §6.5) | 1 | (a) cruciform: stab through the fin at Z ≈ +45; (b) T-tail: stab on the fin top, Z ≈ +130; (c) stab on the tubes, Z ≈ −32 (as in the reference photos) | (a). Out of the wake in every case we fly; elevator pushrod up the fin by about 80 mm; fin root in the tail block takes the stab load; ≈ +4 g. (b) is also clear but the fin must carry the stab at its tip (stiffness, flutter). (c) is in the wake in loaded cruise: pitch trim changes as the speed changes. |
| T2-1 | Tail servos in the pod beside the neck, pushrods between the tubes | 2 | | Nose ≈ 48 mm shorter for the same CG (§5); servos protected at a tail strike |
| T2-2 | Tail arm l_h 600 (tail AC X 680) | 2 | 550 / 600 / 650 | Empty mass changes < 2 g over the range; 600 keeps the stab span ≤ 490 |
| T2-3 | Tube spacing Y ±16, axis Z −40 | 2 | | Pushrods fit between; tubes clear the ground by ≥ 10 mm at an 8° nose-up touchdown (ground at the tail Z −50) |
| T2-4 | Shell wall 0.5 mm single wall on the sides and the aft cone; 0.8 mm floor and nose; inner ribs 0.8 × 6 at the formers and a floor grid | 2 | | Floor and nose take the landing and motor loads; ≈ 22 g less than 0.8 mm everywhere; final after the weighed test section |
| T2-5 | Saddles printed as one part with the pod floor; front stop and firewall as 3 mm balsa / 3 mm ply inserts in printed slots | 2 | | Saddles: no glue joint in the landing load path (their mass moves from the reservoir table to the pod). Inserts: a solid printed 3 mm former costs ≈ 15 g in ASA Aero against 3.2 g balsa |
| T2-6 | Thrust line Z −50, 2° down, 2° right | 2 | | Usual values; trim in the test flights |
| T2-7 | Print split at X −24 and X 175, glued sleeves | 2 | | Fits the P1S; joints at formers |
| T2-8 | Clearances: 0.3 mm on the tubes in the sockets, foam tape 1 mm on the wing seat, ≥ 3 mm between moving parts and the structure | 2 | | Rules from the reservoir stage |

**After stage F-A (2026-11-22):** D-058 safety pin pulled before the lift-out (lift-out check without the safety pin); D-059 local servo-arm pocket X 52–77, Z −113…−107, inner face ≥ Y 56.3, wall 1.2 mm; tier 2 by the main session: hatch top +1 mm over X −25…−2, print split at X −26.22 (balsa front stop = joint former), sloped-skin offset t / cos(slope), aft-cone bottom 0.8 mm, bottom corner R6. Model positions win over §13: saddles and front stop 2.02 mm forward (bottle base X −25.72).

## 8. Build stages (after gate 3)

| Stage | Content | Update |
|---|---|---|
| F-A | Parameter file with the reservoir link; reference bodies (reservoir, wing at +3°); pod outer shape (sections and lofts) and shell; print split | picture + §13 envelope checks |
| F-S | Pod structure (user request 2026-11-22): printed internal cross bars / ribs and skin windows, FEM-guided, in the side session "pod-structure-opt" (Opus, xhigh); delivers `design/cad_fuselage/structure/` and `scripts/fus_struct.py`; integrated into the build after review (after F-B, before F-E) | study report + FEM pictures + mass saving |
| F-B | Pod inner features: front stop, saddles, floor, belly opening, skids, servo wall, flag hole, seat lip, lead slots, band stubs, rear dowel, hatch with magnets, tail servo bay, receiver tray, socket block | pictures (iso, section Y 0, section X 80) + interface checks |
| F-C | Tubes, tail block, stabilizer + elevator, fin + rudder, horns, pushrods and guides | picture + tail volume, SM |
| F-D | Electronics placeholders, mass table, CG; firewall and battery positions set so that CG = X 80 with the battery in the middle of its range | CG, mass, score, R6 margin |
| F-E | All checks, exports: `Fuselage_revA.FCStd`, assembly STEP (fuselage + reservoir + wing), STL of each printed part in the print orientation, DXF of the balsa tail parts, mass table, check report; pictures: iso, iso from below, half-section Y 0, top view with limits, side view with the ground line | review with the user |

Model in one document `Fuselage_revA`, saved at `design/cad_fuselage/Fuselage_revA.FCStd`; scripts in `design/cad_fuselage/scripts/` (`fus_params.py`, `fus_build.py`, `build_stageA.py` …, `fus_check.py`, `make_pictures.py`, `export.py`, `run_all.py`), same pattern as the wing and the reservoir. Part-workbench Python, one `Part::Feature` per part, no face or edge indices.

## 9. Key checks (builder and verifier test these numbers)
1. §13 envelope: belly outer Z −117.0, floor inner −115.5; outer width ≤ 110.0 at X 0–280; servo wall inner face ≥ Y 53.5 at X 50–90; belly opening X 47–115, Y ±20 (open, no structure inside it); front stop X −27.2…−24.2 with the Ø50 hole; saddles X 8–20 and 160–172 on Z −115.5; flag hole centre X 54, Z −110.5 on the left wall.
2. No overlap between any fuselage part and the reservoir (closed and open states) or the wing; ≥ 0.5 mm at the saddles (foam tape) and ≥ 2 mm elsewhere; the flap opens to 150° without contact.
3. Bottle lift-out: the reservoir assembly moves straight up (+Z) by 120 mm with the wing and the hatch off without contact (sweep test in steps of 2 mm).
4. Hatch: comes off upward with the wing on; no band path within 3 mm of it (D-053, D-056).
5. Wing seat: the side-wall tops are within 1.0 ± 0.3 mm (foam tape) of the wing lower surface at X 2–280 in the band |Y| 45–55; the wing LE clears the hatch by ≥ 1 mm.
6. Ground: with the skids, the lowest valve part is ≥ 3 mm above the ground plane (§13 check 11); prop folded inside the ground line.
7. Tail: Vh ≥ 0.50 and Vv ≥ 0.035 from the modelled areas and arms; SM ≥ 7 % at downwash 0.65 with the CG from F-D.
8. CG of the empty aircraft at X 80 ± 2 with the battery in the middle of its slide range; report the range of CG that the slide gives.
9. Twin tubes: straight, parallel, ≥ 70 mm in the sockets, ≥ 40 mm in the tail block; pushrods free between them with ≥ 2 mm.
10. Each printed section fits a 256 × 256 × 256 mm build volume in its print orientation.
11. Mass table: printed parts by volume × density (PLA 1.24, ASA Aero 0.65 *(interp.)*, PETG 1.27), bought parts at catalogue values (FIXED_MASSES.md), report empty mass, score and R6 margin for both PLA and ASA Aero. No mass limit (D-047).
12. Nose without the hatch: the open-top nose channel (side walls + floor + firewall) carries the motor thrust and the 98 N nose-in load; side-wall top lips ≥ 6 mm and a closed frame at the firewall (visual check in the sections; hatch not counted as structure).
13. Stabilizer ≥ 15 mm from the wake centre-line of §6.5 at every listed case for the D-057 choice.
14. All solids `isValid()`; no zero-thickness faces; the saddles and the front stop carry the 98 N landing load into the floor and walls by a continuous printed path (visual check in the sections).
