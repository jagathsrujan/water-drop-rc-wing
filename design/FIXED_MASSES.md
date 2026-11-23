# Fixed masses: bought electronics and parts

Started 2026-11-22 (D-047, brief R19).

Bought parts cannot be made lighter. Use the catalogue (datasheet) mass of each part as a fixed value in every mass table and score calculation. Do not set a budget for these parts. When the team receives a part, weigh it and write the measured value in the "Weighed" column; the weighed value then replaces the catalogue value.

The design optimizes only the parts that the team makes (wing, fuselage, tail, reservoir parts). There is no fixed mass limit for these parts or for the aircraft (D-047).

## Register

| Part | Qty | Model | Catalogue mass each (g) | Source | Weighed each (g) | Total in use (g) | Status |
|---|---|---|---|---|---|---|---|
| Aileron servo | 2 | MG90S (metal gear, 180°) | 13.4 | datasheet *(interp.: common value, confirm on the bought part)* | — | 26.8 | selected (D-010) |
| Release servo | 1 | MG90S | 13.4 | datasheet *(interp.)* | — | 13.4 | selected (D-041) |
| Tail servos (elevator, rudder) | 2 | MG90S | 13.4 | datasheet *(interp.)* | — | 26.8 | selected (D-066) |
| Motor | 1 | DYS D2830 1000 KV, 3.175 mm shaft, 210 W | 52 | *(interp.: Robu gives no net mass, shipping 80 g)* | — | 52 | selected (D-066) |
| Prop adapter | 1 | A2212 collet type, 3.17 mm | 5 | *(interp.)* | — | 5 | selected (D-066) |
| ESC | 1 | Hobbywing Skywalker 40A V2, 5 V / 5 A switching BEC, 60 × 25 × 8 mm | 36 | Robu specification | — | 36 | selected (D-066) |
| Battery (LiPo) | 1 | Pro-Range 3S 1000 mAh 30C, XT60, 75 × 34 × 17 mm | 85 | Robu specification | — | 85 | selected (D-066); out of stock on Robu 2026-11-23 |
| Propeller (≤ 13 in, not metal) | 1 | HQProp 10 × 5 thin electric, fixed (not folding, D-066) | 14 | Robu: 28 g per pair | — | 14 | selected (D-066); out of stock on Robu 2026-11-23 |
| Receiver | 1 | not selected | — | — | — | — | stage 3 |
| Servo extension leads | 2 | 30 cm, 22 AWG | — | — | — | — | selected (wing BOM) |
| Wiring, connectors | — | not selected | — | — | — | — | stage 3 |

Servo arms are counted with the servos in the wing mass table (2 × MG90S + arms = 27.4 g).

**Nose group (D-066):** motor 52 + adapter 5 + prop 14 + ESC 36 + battery 85 = **192 g** (plan placeholder 180 g; XT60 plug on the ESC ≈ 3 g in the wiring line). Tail servos 26.8 g (plan 18 g). Stage F-D sets the firewall and battery positions for CG X 80 with these values. Shop list: `bom/BOM_Electronics_Robu.md`.

## How to use

1. At part selection, write the model and the catalogue mass from the seller's datasheet.
2. Use the catalogue mass in the A1 estimate (brief) in place of the electronics part of the 440 g.
3. Weigh each part when it arrives. Write the weighed value. Use it from then on.
