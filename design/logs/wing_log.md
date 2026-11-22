# Engineering notebook — Stage 2: wing (airfoil, planform, build method)

## 2026-11-21 Claude's own view, written before the user interview

### Inputs from files
- Rulebook: span 1 m max, prop 13 in max, T/W ≤ 1.5 without payload, electric, no gyro, hand launch or take-off with landing gear, 3 min window, release zone about 40 m away.
- Score = water mass / empty mass. Water about 996 g is fixed. Only the empty mass changes the score.
- Weather (stage 1): design density 1.05 kg/m³ (Bengaluru test), 1.15 kg/m³ (Chennai venue). Wind 6 m/s mean, gust 10 m/s. Shade temperature 32 °C max; sun on surfaces can reach 45 to 60 °C *(interp.)*.

### Key coupling found
- T/W ≤ 1.5 is on the EMPTY mass. A lighter aircraft is allowed less thrust. Empty 500 g → 750 gf max thrust → loaded T/W about 0.5. This makes launch and climb with 1 kg water the hard case, and it pushes toward a low stall speed (large chord, high-lift airfoil).
- Span is capped at 1 m. Induced drag depends on span loading W/b, not on aspect ratio. So chord is the main free variable: more chord = lower stall speed and lower cruise CL, but more wing mass and more profile drag.

### Rough sizing (rho 1.05, loaded 1.55 kg, S = 0.95 × b × c)
| Chord | S m² | Wing loading kg/m² | Vs, CLmax 1.1 | Vs, CLmax 1.5 | CL at 12 m/s |
|---|---|---|---|---|---|
| 0.20 m | 0.19 | 8.2 | 11.8 m/s | 10.1 m/s | 1.06 |
| 0.24 m | 0.23 | 6.8 | 10.7 m/s | 9.2 m/s | 0.88 |
| 0.28 m | 0.27 | 5.8 | 9.9 m/s | 8.5 m/s | 0.76 |
| 0.32 m | 0.30 | 5.1 | 9.3 m/s | 8.0 m/s | 0.66 |

Re at flight speed: about 150k to 230k. Kinematic viscosity 1.75e-5 m²/s (Bengaluru).

### My view (before the user's)
- Chord: 0.26 to 0.30 m, rectangular or slight taper only at the tips (simple to build, good low-speed handling). AR about 3.5 to 4.
- Airfoil: a high-lift, moderately cambered section for Re 150k to 250k, for example E423 or a slightly thinner high-lift section. S1223 gives the highest CLmax but has a thin cusped trailing edge, a large nose-down moment, and is hard to build. Clark Y is easy to build but CLmax is lower. Airfoil study by subagent to confirm.
- Build method ranking (lightest strong wing for about 0.27 m², with a carbon spar):
  1. Balsa built-up with film covering: about 70 to 110 g *(interp.)*. Lightest. Needs balsa supply, laser-cut or hand-cut ribs, build skill and time.
  2. LW-PLA 3D print (Bambu): about 160 to 220 g *(interp.)*. Repeatable and fast. Fragile on impact. PLA softens near 55 to 60 °C: risk in the Chennai sun.
  3. XPS or EPS hot-wire core with spar and tape or film skin: about 180 to 260 g *(interp.)*. Robust and cheap, but heavy for this score.
  4. Standard PLA print: about 300 to 400 g *(interp.)*. Too heavy.
- Each 100 g of wing mass costs about 15 to 20 % of the score at an empty mass of 500 to 600 g.

### Questions that change the geometry
- Tools and skills: laser cutter, hot-wire cutter, printer, balsa supply, build experience.
- Launch method and pilot experience (sets the stall speed target).
- Empty mass target and the deadline (the abstract with 5 to 10 build photos is due 20 days before the zonal).

## 2026-11-21 User interview (round 1 and 2)
- Tools: Bambu printer + LW-PLA, laser cutter, hot-wire cutter, balsa supply and hand tools — all four methods possible. (user)
- Launch: hand launch. (user)
- Experience: the team built and flew RC aircraft before. (user)
- Build method view: no preference; asked for all parameters and the reason. (user)
- Priority: "light but robust" — accept about 20 to 40 g more for a wing that survives a hard landing. (user)
- Control surfaces: ailerons only. (user)
- Deadline: user will check the zonal date. Assume 10 Dec 2026 for the wing. (interp.)

## 2026-11-21 Airfoil study result (subagent, NeuralFoil xlarge, design/aero/airfoil_study.md)
- My first view (E423-class high-lift section) is WRONG for this mission. Changed by evidence:
  - Loaded cruise at 13 m/s needs CL 0.6 to 0.7; after the water release CL is only 0.2 to 0.3.
  - E423, S1223, CH10: Cd 0.045 to 0.085 at CL 0.2 to 0.7 (4 to 7 times Clark Y / SD7062), lower-surface separation; Cm -0.23 to -0.25. They help only at launch.
  - Low surrogate confidence on those values (0.25 to 0.78), but the trend agrees with known XFOIL behaviour of these sections.
- SD7062: CLmax 1.58 (gentle stall, drop 0.013), Cd 0.0119 to 0.0129 from CL 0.2 to 0.7, Cm -0.086, t/c 14 % (deep spar), convex lower surface (easy for film). Best all-round section.
- Clark Y: CLmax 1.38, lowest drag, flat bottom, easiest build. Stall speed 0.5 to 0.6 m/s higher than SD7062 at the same chord.
- MH 114: CLmax 1.77, but Cd 0.0165 at loaded cruise CL 0.62 (+35 % vs SD7062), Cm -0.19, 2 % concave lower surface. Upgrade option only if launch tests show the stall speed is too high.

## 2026-11-21 Chord sweep (design/calc/wing_sizing.py), SD7062, wing CLmax = 0.85 x 1.58 = 1.35 (interp.)
| Chord | Wing g (balsa) | Empty g | Score | Vs Bengaluru | Vs Chennai | CL loaded @13 m/s |
|---|---|---|---|---|---|---|
| 0.24 | 107 | 547 | 182 | 9.4 | 9.0 | 0.71 |
| 0.26 | 114 | 554 | 180 | 9.1 | 8.7 | 0.66 |
| 0.28 | 122 | 562 | 177 | 8.8 | 8.4 | 0.62 |
| 0.30 | 131 | 571 | 174 | 8.5 | 8.1 | 0.58 |
- Each 0.02 m of chord costs about 8 g (about 1.4 % of score) and lowers Vs by about 0.3 m/s.
- Hand-launch target Vs ≤ 9.0 m/s at the Bengaluru density (interp.). 0.26 m is marginal if the aircraft is 50 g heavier than planned. 0.28 m gives margin. My proposal: 0.28 m.

## 2026-11-21 Build method comparison (design/calc/wing_mass_model.py, chord 0.28, t/c 0.14)
- Balsa 122 g (robust version +15 g = 137 g), LW-PLA 176 g, XPS 208 g, PLA 410 g.
- Weighted table (see DECISIONS.md D-003): XPS 75.5, balsa 72, LW-PLA 57.5, PLA 49. XPS wins the table on robustness and build time.
- But XPS is 71 g heavier than robust balsa (about 11 % score). The user accepted only 20 to 40 g for robustness. So my proposal is robust balsa; XPS is the runner-up.

## Spar check (tier 2)
- Design load factor 6 (limit 4 x 1.5). Lift per half 42 N at 0.212 m → root moment 8.9 N·m. Spar depth about 33 mm → cap force 270 N.
- Carbon pultruded strip 0.5 x 6 mm, top and bottom, full span, 1.5 mm balsa shear web: stress 90 MPa vs about 400 MPa allowable (interp., local buckling with web support) → margin about 4.
