# Electronics — Robu.in shopping list (D-066)

Prices and stock as listed on Robu.in on 23 Nov 2026 (INR, incl. GST). Check before you order. Masses go into `design/FIXED_MASSES.md`; weigh each part when it arrives.

| Item | Product | Qty | Unit ₹ | Line ₹ | Mass each | Stock (23 Nov) | Link |
|---|---|---|---|---|---|---|---|
| Motor | DYS D2830 1000 KV 2–4S | 1 | 1379 | 1379 | 52 g *(interp.)* | in stock | https://robu.in/product/dys-d2830-1000-kv-2-4s-brushless-motor/ |
| Prop adapter | A2212 motor prop adapter (collet type), 3.17 mm | 2 | 69 | 138 | 5 g *(interp.)* | in stock | https://robu.in/?s=A2212+Motor+Prop+Adapater |
| Propeller | HQProp thin electric 10 × 5 (2 pcs, standard rotation "CCW") | 2 | 329 | 658 | 14 g | **out of stock** | https://robu.in/product/hqprop-thin-electric-prop-10x5-2ccw-propeller/ |
| ESC | Hobbywing Skywalker 40A V2 (5 V / 5 A SBEC) | 1 | 1819 | 1819 | 36 g | in stock | https://robu.in/product/hobbywing-skywalker-40a-v2-esc-fixed-wing/ |
| Battery | Pro-Range 11.1 V 1000 mAh 30C 3S, XT60 | 1 | 1049 | 1049 | 85 g | **out of stock** | https://robu.in/product/pro-range-11-1v-1000mah-30c-3s-lithium-polymer-battery-pack/ |
| Tail servos | MG90S metal gear, 180° | 2 | 296 | 592 | 13.4 g | in stock | https://robu.in/product/mg90s-9g-servo-metal-gear/ |

**Total: ₹5,635.** Two prop packs = 4 props (a fixed prop can break at a belly landing, D-066). Two collets: one spare.

Also needed (not priced): XT60 male plug for the ESC input; 3.5 mm bullets if the motor and ESC do not match; heat-shrink for the ESC and the receiver (water, see the weather study).

Setup notes:
- Set the ESC **brake on** (Skywalker stick programming) so the prop stops before touchdown.
- Measure static thrust in Bengaluru with a fresh pack: ≤ 1.37 × the weighed empty mass (≈ 890 g at 650 g). If it is over, use a smaller prop (9 × 5) rather than a transmitter throttle limit (rule: no programming).
