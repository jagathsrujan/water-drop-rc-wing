# Fuselage stage — engineering notebook

Started 2026-11-22. Stage after the reservoir (D-033). Binding interface: `design/03_reservoir_plan.md` §13 and §14. Calculation: `design/calc/fuselage_sizing.py`. Frame: wing frame (origin wing LE on the centreline, X aft, Y right, Z up; fuselage datum horizontal; wing at +3°).

## 1. Inputs read
- Reservoir rev A.2 (§13): belly outer Z −117, floor inner −115.5; wing seat Z ≈ −13; width ≤ 110 at the wing saddle; servo side-wall inner face ≥ Y 53.5 at X 50–90; belly opening X 47–115, Y ±20; front stop X −27.2…−24.2; saddles X 8–20, 160–172; fill hole X −11 (Ø22, or 2 mm forward), cap top Z −7; safety-pin flag hole left side X 54, Z −110.5; removal up through the top with the wing off.
- Bottle base X −25.72, neck lip X ≈ 229 (bbox of the reservoir parts X −31.4 to 229.3, Z −100 to −20).
- **Fill cap X max −2.000 against the rule "parts above Z −13 at X ≤ −2": zero margin.** The bottle (and the water centroid) can move **forward only** unless the fill port moves. The tail must be sized so that the CG can stay at X ≤ 80.
- Wing rev A: 184.0 g with servos; volume-weighted CX of the structure 106 mm → wing CG ≈ X 110 *(interp.: film and servos added by estimate)*. Two dowels + rubber bands (D-008), centre sheeting y ±56, aileron leads exit at the bottom centre at x ≈ 130.
- Rule (rulebook p. 3–4): T/W ≤ 1.5 without payload (excess thrust is cancelled with ballast at the CG); prop ≤ 13 in, not metal; electric only; no gyro, no programming in receivers or for any mission step; hand launch allowed; same aircraft in all rounds and it must match the abstract; 2.5 % difference in span, chord and **fuselage length** between teams of one college (Q5).
- Bought electronics not selected (FIXED_MASSES.md): motor, ESC, battery, prop, receiver, tail servos.

## 2. My view before the interview (written before the first question)

### 2.1 Tail size and the CG
`fuselage_sizing.py`, Vh = horizontal tail volume, SM = static margin at CG X 80:

| Vh | downwash 0.45 | 0.55 (central) | 0.65 |
|---|---|---|---|
| 0.45 | SM 13.4 % | 9.5 % | 5.6 % |
| 0.50 | 15.7 % | 11.4 % | 7.1 % |
| 0.55 | 18.1 % | 13.4 % | 8.6 % |

- The downwash gradient at the tail of a low-AR wing (3.54) is not known well: 0.35 at the wing, 0.69 far aft. Design value 0.55, range 0.45 to 0.65.
- **My choice: Vh 0.50 to 0.55, Vv 0.035, tail arm 600 to 650 mm.** At Vh 0.50 the SM stays ≥ 7 % for the worst downwash. A small extra tail area is cheap (about 1.5 g per dm²) against a CG that cannot move aft.
- At l_h 600, Vh 0.50: Sh ≈ 6.5 dm² (about 475 × 137 mm); Sv ≈ 1.6 dm² (about 160 × 100 mm).

### 2.2 Concepts for the structure (my ranking)
Pod mass from the skin area (390 mm long box round the bottle and the nose): **≈ 55 g** (not 42 g). Aft part: carbon tube Ø10/8 × 450 mm 19.7 g + clamp 6 g ≈ 26 g, against a tapered 1.5 mm balsa box ≈ 28 g.

| Concept | Mass to the tail (g, interp.) | Cost | Build | Comment |
|---|---|---|---|---|
| A. Full balsa box, laser-cut sides, triangle-stock corners | ≈ 84 | lowest (balsa in stock) | 2–3 days, all on the laser | One material, venue repair with CA, team knows it |
| B. Balsa pod + carbon tube boom | ≈ 81 | tube + clamp ≈ ₹600–900 *(interp.)* | 2 days | Stiffest boom, simple tail mount; pushrods outside the tube |
| C. Balsa pod + balsa stick truss aft (film) | ≈ 70 | lowest | 3–4 days | Lightest; weak to hand handling and to a launch grip aft |
| D. LW-PLA printed pod + boom | ≈ 95+ | filament | print time | Softens near 55 °C (R12), heavier per area |

My ranking: A first (cost, team skill, venue repair, equal mass), B second (stiffer, faster tail mount). A and B differ by only about 3 g; funds and build time decide.

### 2.3 Other first choices
- Tail: conventional, flat 2 mm light balsa sheet (or built-up if mass matters), elevator and rudder. Rudder kept: loaded CL 0.8–1.1 near 10–12 m/s gives strong adverse yaw with 0° dihedral; the rudder costs about 12 g (servo + horn + pushrod). V-tail rejected: it needs mixing (rule risk on "programming").
- Motor: tractor in the nose, folding prop (survives a belly landing with 1.55 kg), 2–3° down and right thrust (T2).
- Battery: nose bay ahead of the front stop on a slide tray, for CG trim. Nose group centroid needed ≈ X −90 (motor ≈ −140, battery ≈ −75).
- Tail servos: in the pod behind the bottle neck (X ≈ 240–270), long pushrods. This keeps the nose shorter than servos at the tail.
- Landing: replaceable belly skid strips ahead of and behind the belly opening, folding prop; the valve stays 3.5 mm recessed (D-051).
- Empty mass estimate with placeholders: **≈ 572 g** (score ≈ 174), loaded ≈ 1568 g. R3: static thrust ≤ ≈ 860 g.

## 3. Geometric conflicts to solve (become key checks)
1. **Top between X −27 and 0:** the bottle base (X −25.7) comes out upward with the wing off. A fixed deck or a through dowel there blocks removal. The fill hole is at X −11. → Proposal: a removable nose hatch from the firewall to the LE (covers the battery bay and carries the Ø22 fill hole); the front dowel must not cross the opening.
2. **Front dowel and bands:** bands must not cross over the fill cap (top Z −7) or stop the funnel.
3. **Launch grip:** at the CG station the fuselage is 110 mm wide and the belly opening, the flap and the safety-pin flag are there. Grip position and width to ask.
4. **Aileron leads:** exit at x ≈ 130 into a 7 mm gap above the bottle (strap 1 mm). Route down the upper corners between the bottle and the side walls (≈ 13 mm each side at the top).
5. **Qualifier landing with full water (1.55 kg):** belly and nose take the load; prop folds; the valve takes no load.
6. Wing saddle follows the SD7062 lower surface at +3° (Z ≈ −13 at X 60–260).

## 4. Interview record
(to be filled)

### Round 1 (2026-11-22)
- Parts in hand: **none** → all electronics are placeholders, positions parametric.
- Build before 10 Dec: **CAD only** for the fuselage (photos show the wing and the reservoir).
- Structure (user): "3D print using normal PLA, replace it with ASA Aero if we get selected; also we can try a balsa fuselage if it is very much better in strength or any reason; I want to try a dual carbon boom."
  - Classified: material = preference + method (check); twin boom = preference, reason not yet given (ask).
- Tail: "recommended" → user asks for my recommendation.

### Check of the printed pod (engineering claim / method)
Skin area of the pod ≈ 0.15 m² (390 mm long, 110 × 104 at the bottle, nose taper).
| Pod | Wall | Mass (interp.) | Heat (R12, 45–60 °C surface) | Note |
|---|---|---|---|---|
| Balsa box + ply/PETG hard points | 2 mm sides, 1.5 mm floor | ≈ 55 g | OK | lightest; CA repair at the venue |
| PLA print (1.24 g/cm³) | 0.45 mm single wall + inner ribs | ≈ 100 g | **fails** (Tg ≈ 55–60 °C): Bengaluru tests only | brittle on impact, cracks along layers |
| ASA Aero (foamed, ≈ 0.6–0.7 g/cm³ *(interp.)*) | ≈ 0.6 mm foamed wall + ribs | ≈ 70 g | OK (ASA ≈ 95 °C) | interfaces printed exactly |
- Printed pod costs ≈ +15 g (ASA Aero) against balsa: score −2.6 %. PLA prototype ≈ +45 g: only for test flights, and the CG changes when the material changes (re-trim).
- Twin carbon booms Ø8/6 × 500 mm: ≈ 34 g against one Ø10/8 boom ≈ 20 g (+14 g, and a second fin if H-tail).
- **Pusher between twin booms (if that is the intent):** a 10 in prop on the pod centreline (Z ≈ −60) reaches Z ≈ −187, 70 mm below the belly: ground strike at a belly landing and the released water goes through the disc. A pusher needs the thrust line high (Z ≥ +20, a pylon) — conflicts with the rubber-band one-piece wing that comes off for the reservoir.

### Round 2 (2026-11-22)
User sent 4 photos of a reference aircraft and "i like this twin boom style" in place of the answers. Read from the photos:
- printed pod (white, smooth), tractor motor in the nose, high wing with crossed rubber bands on top of the pod;
- **two carbon tubes side by side** (about 25–35 mm apart *(interp.)*) as one boom from the pod rear to a printed tail block;
- conventional tail: stabilizer with elevator, one fin with rudder; 2 small servos on the tail block (short linkages).
- So "twin boom" = a twin-tube single boom with a tractor nose, not a pusher. The pusher concern is closed.
- Launch grip and the pod material question not answered → launch grip goes into the plan as a tier 1 decision point; material: the round 1 answer stands (PLA prototype, ASA Aero for the zonal, balsa if much better).

### Twin tube boom sizing (first check)
Tail load design 5 N at 0.5 m × 3 (gust + landing) → M = 7.5 N·m, shared by 2 tubes:
- Ø8/6 (I = 137 mm⁴): 109 MPa per tube against ≈ 600 MPa pultruded *(interp.)*: margin 5.5; 2 × 470 mm ≈ 32 g.
- Ø6/4 (I = 51 mm⁴): 220 MPa: margin 2.7; ≈ 23 g. Stiffness (flutter, elevator authority) to check in the plan.
- Two tubes in two sockets cannot turn in the clamp (a single round tube can).

### Concept comparison (gate 2)
Mass to the tail = pod + boom + clamps / tail block, without the tail surfaces (interp.):
| | U: user — printed pod (PLA → ASA Aero) + twin tubes | A: full balsa box (my first view) | B: balsa pod + twin tubes | H: hybrid pod (balsa sides + printed formers, nose, saddles) + twin tubes |
|---|---|---|---|---|
| Mass to the tail | ≈ 110 g (PLA prototype ≈ 140 g) | ≈ 84 g | ≈ 95 g | ≈ 102 g |
| Empty mass / score | ≈ 598 g / 166.6 | ≈ 572 g / 174.1 | ≈ 583 g / 170.8 | ≈ 590 g / 168.8 |

Weighted (1 poor … 5 good); weights from the brief: mass 5, belly landing with water 4, venue repair 3, heat 2, build effort 3, interface accuracy 3.
| Criterion | W | U | A | B | H |
|---|---|---|---|---|---|
| Mass | 5 | 3 | 5 | 4 | 3.5 |
| Belly landing 1.57 kg | 4 | 3 | 4 | 4 | 4 |
| Venue repair | 3 | 3 | 5 | 4 | 4 |
| Heat (zonal) | 2 | 4 | 4 | 4 | 4 |
| Build effort | 3 | 5 | 3 | 3 | 3 |
| Interface accuracy (§13) | 3 | 5 | 3 | 3 | 4 |
| **Total** | | **77** | **82** | **74** | **74.5** |
- A wins by 5 points, on mass (−4.3 % score for U) and repair. U wins on build effort and exact interfaces.
- What makes U win: ASA Aero ≤ 0.5 g/cm³ as printed (test print of a 100 mm pod section, weigh) halves the mass gap.
- All candidates meet the brief (no mass limit, D-047): the choice is the user's preference; cost stated.
- Tail recommendation (user asked): conventional, elevator + rudder, single fin on the twin-tube tail block, Vh 0.50, Vv 0.035.

### Round 3 (2026-11-22): gate 1 accepted; user asks for a recommendation
User: "which one do you recommend for easy to build, high strength but still will get good score". Gate 1 brief additions: accepted (R20–R26 written).

Re-weighted with the user's criteria (build effort 5, strength 5, mass 4, repair 3, heat 2, interface 3 = 22). Two scores corrected with reasons (new facts, not to fit an answer):
- Build effort A 3 (unchanged), B 3 → 4: the aft part of B is 2 bought tubes glued into 2 printed sockets; the aft part of A is a 440 mm tapered box with formers that must be jigged straight.
- Strength B 4 → 4.5: a 1.5 mm balsa aft box crushes under a hand grip or a cartwheel; carbon tubes do not. U stays 3 (foamed ASA has a lower strength; layer lines split on impact).
| Criterion | W | U | A | B | H |
|---|---|---|---|---|---|
| Mass | 4 | 3 | 5 | 4 | 3.5 |
| Strength (landing, handling) | 5 | 3 | 4 | 4.5 | 4.5 |
| Venue repair | 3 | 3 | 5 | 4 | 4 |
| Heat (zonal) | 2 | 4 | 4 | 4 | 4 |
| Build effort | 5 | 5 | 3 | 4 | 3.5 |
| Interface accuracy | 3 | 5 | 3 | 3.5 | 4 |
| **Total** | | **84** | **87** | **89** | **85** |
**Recommendation: B — laser-cut balsa pod + twin Ø8/6 carbon tubes + printed PETG hard points** (motor mount, nose hatch with the fill hole, boom socket block, tail block; saddles already PETG). Empty ≈ 583 g, score ≈ 170.8: −1.9 % against A, +2.5 % against U. Runner-up A (lightest, but more build work and no carbon boom). U stays possible: the same layout with the pod printed.

### Gate 2 result and correction (2026-11-22)
- User chose **U** (D-052) against my recommendation B. Recorded as a preference with its cost.
- Advisor review found the pod mass too low for the plan geometry (505 mm, 0.8 mm wall). By area (`fuselage_sizing.py`, skin 0.167 m²):
  | Pod | PLA | LW-PLA 0.55 | ASA Aero 0.53 / 0.65 / 0.80 |
  |---|---|---|---|
  | 0.45 single wall | 146 g | 69 g | 67 / 80 / 97 g |
  | 0.5 sides, 0.8 floor + nose | 187 g | 87 g | 85 / 102 / 124 g |
  | 0.8 everywhere | 219 g | 101 g | 98 / 118 / 144 g |
  Balsa pod B (same length) + PETG sockets: 76 g.
- Empty: B 623 g (159.8); U ASA Aero 628 / 650 / 666 g; PLA prototype 735 g (loaded stall 9.24 m/s, R6 fails); LW-PLA prototype 635 g (8.97 m/s). ASA Aero density source: Bambu product page "50–75 % of the density of regular ASA" (regular ASA ≈ 1.05–1.07).
- Front stop and firewall changed to inserts (3 mm balsa, 3 mm ply) in printed slots: a solid printed 3 mm former costs ≈ 15 g in ASA Aero, the balsa plate 3.2 g (T2).

### Wing wake at the tail (advisor item 2)
Wake centre-line Z at X 680 (downwash 0.45 / 0.55 / 0.65): loaded 10 m/s +0 / −11 / −23; loaded 12 m/s −19 / −28 / −36; loaded 15 m/s −35 / −40 / −46; empty 12–18 m/s −46 … −59; wing stall +29 / +12 / −5.
- Stab at Z −32 (plan draft, T2-3) is **in the wake in loaded cruise** (12–13 m/s) → rejected.
- Low stab below the wake (Z ≤ −65): the ground at the tail is Z −67 at a 6° nose-up touchdown → stab strikes. Rejected.
- **High stab, Z ≈ +45 on the fin (cruciform):** clear by ≥ 16 mm at the stall (worst), ≥ 45 mm in loaded cruise, ≥ 90 mm empty. T-tail (stab at the fin top, Z ≈ +130): clear always, heavier fin. → tier 1 decision D-057.

### User request (2026-11-22, during stage F-A): internal printed cross bars + lighter shell (hollowing / topology optimization), in new Opus sessions
**My view before the work (written first):**
- The pod shell is already hollow (0.5 mm sides, 0.8 mm floor and nose). "Hollowing" can only mean windows (cut-outs) in the skin between load paths, with internal ribs, stringers or cross bars carrying the loads (geodesic / truss side walls).
- Gain is real but modest. Sides + aft cone ≈ 0.084 m² × 0.5 mm = 42 cm³ (27 g ASA Aero, 52 g PLA). 40 % windows save ≈ 11 g ASA Aero / 21 g PLA; film over the windows adds ≈ 1.5 g; cross bars ≈ 1 g each (ASA Aero). Net ≈ −8 to −15 g ASA Aero (≈ 1.5–2.5 % score), ≈ −15 to −30 g PLA (helps the R6 override of the test aircraft).
- A thin printed shell is governed by buckling, impact and handling, not by stress. FEM with real load cases must decide; a pure stress-based topology result on a 0.5 mm shell gives lattices that may not print in foamed ASA.
- Hard constraints: no cross bar across the top opening X −27…231 (the bottle lifts out upward, D-046); none across the battery path in the nose; no windows in the floor landing zone, the grip zone X 40–120 (D-054), the servo wall, the saddle feet, the band-stub bosses, the socket block; drag: windows covered with film or tape.
- Useful cross bars: across the nose top under the hatch (the open-top nose channel, key check 12), behind the bottle cap (X 240–280), and X-bracing ribs on the side walls.
- FreeCAD has no built-in topology optimization; CalculiX FEM is available (`mcp__freecad__run_fem_analysis`). A BESO macro would be a download (needs the user's permission).
**Execution:** the user asked for new Opus sessions → one side session "pod structure optimization", after stage F-A gives the shell; headless FreeCAD only while the GUI is in use; its own files; integration into the build after its result is reviewed.

### Stage F-A verification by the main session (2026-11-22)
- Pictures seen: stageA_iso, section_Y0, section_X80 — shape as planned; side walls 0.5 mm × ≈ 100 mm high are connected only by the floor in the seat region (the structure session F-S adds ribs / cross bars there and in the nose channel).
- Independent probe in FreeCAD: F1 30.63, F2 36.01, F3 21.81, F4 12.29 cm³ (total 100.74 = 65.5 g ASA Aero 0.65 / 124.9 g PLA), all valid; right wall at X 70: inner face Y 54.122 at Z −111.9, 54.30 at Z −110.5 (arm plane), 54.5 above; servo case Y max 51.0, arm envelope Y max 53.26 → arm clearance ≈ 0.9–1.0 mm. Agrees with the subagent report.
- My tier 2 decisions after F-A: (1) hatch top raised 1 mm over X −25…−2 (Z −3) so every fill part has ≥ 2 mm (vent knob 1.2 → 2.2 mm; LE–hatch clearance ≈ 2 mm, ≥ 1 required); (2) print split moved from X −24 to X −26.22 (aft face of the balsa front stop): the stop becomes the joint former between F1 and F2 (F2 length 201 mm, fits); (3) sloped skin offset t / cos(slope) in F-B (+≈ 3 g PLA); (4) aft-cone bottom 0.8 mm accepted (tail-strike / landing contact zone); (5) Rb 6 accepted (forced by the §13 wall position).
- Grip zone conflict noticed: D-054 grip (X 40–120, fingers on the sides) covers the right wall at the release-servo arm (X 58–71). A 0.5 mm wall pressed by fingers can move > 1 mm and jam the arm. → question 2 to the user.
