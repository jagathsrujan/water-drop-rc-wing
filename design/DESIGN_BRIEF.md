# Design brief: water-drop aircraft, Boeing NAC 2026-27 (IIT Madras zone)

Status: draft 2026-11-21 (wing stage); reservoir items R13–R18 updated 2026-11-22 (D-045); fuselage items R20–R26 accepted by the user 2026-11-22 (gate 1, fuselage stage).

## Purpose
A hand-launched fixed-wing RC aircraft that carries 1000 mL of water in a sealed removable reservoir and releases it on one pilot command over a zone about 40 m away. Score = water mass × 100 / empty mass, so the empty aircraft must be as light as possible and still survive all flights (repairs only, no spare aircraft).

## Requirements
| ID | Requirement | Value | Why | Source | Checked by |
|---|---|---|---|---|---|
| R1 | Wingspan | ≤ 1.00 m (design 0.99 m for build tolerance) | Rule | rule | drawing, tape measure |
| R2 | Propeller | ≤ 13 in, not metal | Rule | rule | part list |
| R3 | T/W without payload | ≤ 1.5 at the venue; ≤ 1.37 measured in Bengaluru | Rule; denser air in Chennai | rule + derived (stage 1) | thrust stand |
| R4 | Payload | 1000 mL water (about 996 g at 28 to 30 °C) | Rule | rule + derived | — |
| R5 | Launch | Hand launch | Team choice | user | test flight |
| R6 | Loaded stall speed | ≤ 9.0 m/s at ρ = 1.05 kg/m³ (kept by the user with the modelled wing rev A, D-047; it permits about 648 g empty) | Safe hand launch | interp. + user | calculation, test |
| R7 | Wind | Controlled flight in 6 m/s mean, 10 m/s gust (10 m height) | Chennai afternoon, 90 % of hours | derived (stage 1) | calculation |
| R8 | Robustness | "Light but robust": survives a hard landing. No fixed mass allowance for robustness (D-047) | Same aircraft for all flights | user | design review |
| R9 | Wing controls | Ailerons only on the wing | Team choice | user | — |
| R10 | Flight window | Take-off to landing ≤ 3 min; ≥ 30 s before release | Rule | rule | — |
| R11 | Controls and release | No gyro, no programming, release on one channel | Rule | rule | — |
| R12 | Heat | Shade 32 °C; surfaces in sun 45 to 60 °C | Chennai January | derived (stage 1) + interp. | material choice |
| R13 | Reservoir | Sealed, securely mounted, removable, interior; holds 1000 mL (996 g) with ullage; 1 L Bisleri PET bottle, horizontal along the fuselage, neck aft (H3, D-035, D-037); filled in place through a top fill port ahead of the wing LE, without removal (D-049) | Rule; user choice | rule + user | inspection |
| R14 | Leakage | Zero visible leakage: at inspection, in flight, and at a belly landing with full water (design load 10 g, 98 N) | Rule (qualifier score 0); landing load | rule + interp. | drop test |
| R15 | Release | One channel, pilot only; V2 pin-latched trapdoor, rear hinge, on a bulkhead unit at the bottle bottom (D-034, D-040, D-042); passive one-way vent (D-043); second safety pin with a flag for the qualifier and transport (D-044) | Rule; user choice | rule + user | bench test |
| R16 | Drainage | Water left < 10 g at 0 to 3° pitch (pilot releases near level); drain ≤ 15 s | Score (1 g water ≈ 0.6 g empty mass); pilot trim time after a 62 % mass drop; H3 with a Ø14 bore gives 11.5 s (D-045) | derived + interp. | drain test |
| R17 | Reservoir mass | As light as possible; no fixed limit (D-047). Report the mass, without the release servo, at each stage | Score: 10 g ≈ 1.6 % | user | scale |
| R18 | Reservoir position | Water centroid at the empty-aircraft CG in X (x ≈ 80 mm aft of the wing LE, interp.); width ≤ 110 mm at the wing saddle | CG does not move at release; centre sheeting width | derived | CAD |
| R19 | Mass limits | No predetermined mass limit for the aircraft or for any part. Each stage reports its mass and the score effect; the team optimizes as the design goes on (D-047). Bought electronics (motor, ESC, battery, receiver, servos, wiring) use their catalogue mass as a fixed value: `design/FIXED_MASSES.md` | Score = water / empty mass; bought parts cannot be lightened | user | mass tables |
| R20 | Fuselage–reservoir interface | Meets `design/03_reservoir_plan.md` §13 (belly outer Z −117, floor −115.5, wing seat Z ≈ −13, width ≤ 110 at the wing saddle, servo wall ≥ Y 53.5 at X 50–90, belly opening X 47–115 / Y ±20, front stop X −27.2…−24.2, saddles X 8–20 / 160–172, fill hole X −11, safety-pin flag hole left side X 54 / Z −110.5) | Reservoir accepted first (D-033) | derived | CAD |
| R21 | Pitch stability | Vh ≥ 0.50, Vv ≥ 0.035; static margin ≥ 7 % at the worst downwash gradient (0.65) with the CG at X ≤ 80 | The bottle can move forward only (fill cap at X −2.000, zero margin); low-AR downwash not known well | derived | `design/calc/fuselage_sizing.py` |
| R22 | Tail | Conventional, elevator + rudder | Adverse yaw at loaded CL 0.8–1.1 with 0° dihedral; no mixing (rule) | user ("recommended") | — |
| R23 | Landing | Belly landing with full water (1.57 kg) without load into the valve (valve 3.5 mm recessed, D-051); folding prop; nose and belly take the load | Qualifier lands with 1000 mL; repairs only | interp. + rule | CAD, drop test |
| R24 | Reservoir access | Reservoir comes out up through the top with the wing off; fills in place with the magnet nose hatch off (no hole; changed from "Ø22 hole at X −11" by D-056) | D-046, D-049, D-056 | user | CAD |
| R25 | Heat by material | PLA parts only for the Bengaluru test flights; parts flown at the zonal meet R12 (PETG, ASA, balsa, carbon) | Chennai sun 45–60 °C | user + derived | material list |
| R26 | Electronics placement | Motor, ESC, battery, receiver and tail servos are placeholders (none in hand); positions parametric; battery position trims the CG | Selection in stage 3 | user | CAD |

## Constraints
- Manufacture: Bambu printer with LW-PLA, laser cutter, hot-wire cutter, balsa and hand tools are available. The team built and flew RC aircraft before.
- Abstract with 5 to 10 build photos is due 20 days before the zonal.
- Air density: 1.05 kg/m³ (Bengaluru test), 1.15 kg/m³ (Chennai venue).

## Global frame
Origin: wing leading edge at the centreline. X: aft. Y: right wing. Z: up.

## Assumptions *(interp.)*
| ID | Assumption | Value used | What changes it |
|---|---|---|---|
| A1 | Mass of the aircraft without the wing | 440 g (estimate, not a limit) | Component selection (stage 3): replace the electronics part with the catalogue masses in `design/FIXED_MASSES.md` |
| A2 | Wing CLmax / airfoil CLmax | 0.85 | Test flights |
| A3 | Wing complete by | 10 Dec 2026 | Zonal date from the user |
| A5 | Build before selection | Only the stages that the abstract photos need, at minimum cost (user, 2026-11-22: exams, limited funds) | Selection result |
| A4 | Wing mass estimates per method | see D-003 | Weighed material samples |

## Open questions
| ID | Question | Needed before | Owner |
|---|---|---|---|
| Q1 | Zonal date | Build schedule | user |
| Q2 | Airfoil, chord, build method (D-001 to D-003) | Rib design | user |
| Q3 | ~~Wing position~~ — closed: high wing (D-007) | — | — |
| Q4 | Does T/W ballast count in the empty weight? | Motor choice | organizers |
| Q5 | Do other teams from the same college enter? (2.5 % rule on span, chord, fuselage length) — the fuselage length is fixed when the abstract goes out | Abstract (10 Dec 2026) | user |
| Q6 | Heaviest aircraft the team hand-launched before, or a 1.5 kg dummy throw test | Final chord | user |
| Q7 | Must the release only begin over the zone, or also end there? (sets the outlet size) | Reservoir concept | organizers |
| Q8 | Is the reservoir weighed with or without parts that stay in the aircraft (servo, link)? | Reservoir concept | organizers |
| Q9 | How do the organizers supply the water (jug, bottle) and how much time is there to fill? May the team give its own funnel? Is the reservoir weighed empty or full before the attempt? | Fill procedure (design fills in place, D-049) | organizers |

## Change log
| Date | Change | Reason | Decision ID |
|---|---|---|---|
| 2026-11-21 | Brief started | Wing stage | — |
| 2026-11-21 | Wing mass limit 145 g → 155 g (reduction set) → 160 g without servos | CAD volumes: 172 g projected, 156.4 g after the reduction set | D-013, D-023 |
| 2026-11-21 | Tip rib inboard (y 489–492), 3 mm ring tip cap y 492–495; false spar full depth; aileron end ribs and horn rib | Span and fit problems found in CAD planning | D-014, D-015, D-016 |
| 2026-11-21 | Wing CAD rev A built (`design/cad/Wing_revA.FCStd`) | Stages A–C | — |
| 2026-11-22 | Container: 1 L Bisleri bottle (R13) | Availability, mass | D-035 |
| 2026-11-22 | R13–R18 added (reservoir); release mechanism V2 chosen | Reservoir interview and gate 2 | D-033, D-034 |
| 2026-11-22 | Reservoir stage started; Q7–Q9 added (rule points that set the reservoir concept) | Rulebook read for the reservoir | — |
| 2026-11-22 | R13, R15, R16 changed for H3 (horizontal bottle, bulkhead unit, drain ≤ 15 s, residual < 10 g at 0–3°) | Reservoir CAD plan, gate 3 | D-045 |
| 2026-11-22 | Reservoir CAD decisions: FreeCAD only, rear hinge, servo beside the valve, passive vent, oval saddle flange, second safety pin, top removal | Reservoir CAD plan | D-039…D-046 |
| 2026-11-22 | In-place fill through a top fill port with the vent in the cap | User: fill method not clear; no removal for each fill | D-049, D-050 |
| 2026-11-22 | Wing rev B (foam blocks) modelled for comparison in `design/cad_revB/`; rev A unchanged. Rev B 247.7 g, fails R6 (9.11 m/s) and R12 heat (PLA). A/B choice in D-024 | User's concept (D-024) | D-024…D-032 |
| 2026-11-22 | All mass limits removed (wing 160 g, reservoir R17 50 g, R8 robustness allowance); R19 added; electronics at catalogue mass (`design/FIXED_MASSES.md`) | User: optimize as the design goes on, no predetermined weight | D-047 |
| 2026-11-22 | R6 kept (stall ≤ 9.0 m/s); wing rev A stays as modelled | User: the wing is already modelled | D-047 |
| 2026-11-22 | Fuselage stage started: R20–R26 added, Q3 closed; no electronics in hand; fuselage CAD only before the abstract | Fuselage interview, gate 1 | — |
| 2026-11-22 | Fuselage concept U (printed pod + twin carbon tubes), PLA test prototype (R6 override for the tests), side band stubs, launch grip under the belly, fill with the hatch off (R24), cruciform tail | Fuselage gate 2 and plan decisions | D-052…D-054, D-056, D-057 |
