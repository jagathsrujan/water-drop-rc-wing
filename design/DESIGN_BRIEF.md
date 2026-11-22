# Design brief: water-drop aircraft, Boeing NAC 2026-27 (IIT Madras zone)

Status: draft 2026-11-21 (wing stage). Not yet agreed.

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
| R6 | Loaded stall speed | ≤ 9.0 m/s at ρ = 1.05 kg/m³ | Safe hand launch | interp. | calculation, test |
| R7 | Wind | Controlled flight in 6 m/s mean, 10 m/s gust (10 m height) | Chennai afternoon, 90 % of hours | derived (stage 1) | calculation |
| R8 | Robustness | "Light but robust": survives a hard landing; extra mass limit about 20 to 40 g (option text, to confirm) | Same aircraft for all flights | user | design review |
| R9 | Wing controls | Ailerons only on the wing | Team choice | user | — |
| R10 | Flight window | Take-off to landing ≤ 3 min; ≥ 30 s before release | Rule | rule | — |
| R11 | Controls and release | No gyro, no programming, release on one channel | Rule | rule | — |
| R12 | Heat | Shade 32 °C; surfaces in sun 45 to 60 °C | Chennai January | derived (stage 1) + interp. | material choice |

## Constraints
- Manufacture: Bambu printer with LW-PLA, laser cutter, hot-wire cutter, balsa and hand tools are available. The team built and flew RC aircraft before.
- Abstract with 5 to 10 build photos is due 20 days before the zonal.
- Air density: 1.05 kg/m³ (Bengaluru test), 1.15 kg/m³ (Chennai venue).

## Global frame
Origin: wing leading edge at the centreline. X: aft. Y: right wing. Z: up.

## Assumptions *(interp.)*
| ID | Assumption | Value used | What changes it |
|---|---|---|---|
| A1 | Mass of the aircraft without the wing | 440 g | Component selection (stage 3) |
| A2 | Wing CLmax / airfoil CLmax | 0.85 | Test flights |
| A3 | Wing complete by | 10 Dec 2026 | Zonal date from the user |
| A4 | Wing mass estimates per method | see D-003 | Weighed material samples |

## Open questions
| ID | Question | Needed before | Owner |
|---|---|---|---|
| Q1 | Zonal date | Build schedule | user |
| Q2 | Airfoil, chord, build method (D-001 to D-003) | Rib design | user |
| Q3 | Wing position: high, mid or low wing | Fuselage stage | user |
| Q4 | Does T/W ballast count in the empty weight? | Motor choice | organizers |
| Q5 | Do other teams from the same college enter? (2.5 % rule on span, chord, fuselage length) | Final dimensions | user |
| Q6 | Heaviest aircraft the team hand-launched before, or a 1.5 kg dummy throw test | Final chord | user |

## Change log
| Date | Change | Reason | Decision ID |
|---|---|---|---|
| 2026-11-21 | Brief started | Wing stage | — |
| 2026-11-21 | Wing mass limit 145 g → 155 g (reduction set) → 160 g without servos | CAD volumes: 172 g projected, 156.4 g after the reduction set | D-013, D-023 |
| 2026-11-21 | Tip rib inboard (y 489–492), 3 mm ring tip cap y 492–495; false spar full depth; aileron end ribs and horn rib | Span and fit problems found in CAD planning | D-014, D-015, D-016 |
| 2026-11-21 | Wing CAD rev A built (`design/cad/Wing_revA.FCStd`) | Stages A–C | — |
