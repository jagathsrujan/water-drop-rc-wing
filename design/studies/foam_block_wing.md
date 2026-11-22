# Study: foam-block wing (user sketch, 2026-11-22) — notebook

Status: concept review, tier 1. No change to the CAD or the decisions. Claude's view is written here **before** the user's answers to the clarifying questions.

## 1. The sketch, as Claude reads it *(to confirm)*
- Short span-wise foam blocks with the SD7062 shape. Each block has a balsa airfoil plate of thickness x on its faces.
- Hollow bays between the blocks, closed only by the covering film.
- User's addition: 3D-print the LE and TE curves, for strength and for connections between the blocks, with jig features in the prints.
- Not shown: a spar, D-box sheeting, block width and count, foam type.

## 2. Numbers (SD7062 at 280 mm: section area 69.1 cm², perimeter 577 mm)

| Item | Mass |
|---|---|
| Foam, for each 10 mm of span: EPS 15 / EPS 20 / XPS 30 / XPS 35 kg/m³ | 1.0 / 1.4 / 2.1 / 2.4 g |
| Foam, full span solid: EPS 20 / XPS 30 | 137 / 205 g |
| 1.5 mm light balsa airfoil plate, no holes | 1.0 g each |
| Rev A rib, 2 mm medium, 33 % holes | 1.2 g each |
| Rev A: all ribs / D-box skins / cap strips | 22.7 / 20.2 / 4.2 g |

Example A: 17 XPS-30 blocks, 20 mm wide, at the rev A rib stations, 2 balsa plates each, D-box kept. Blocks + plates = 70 + 35 = 105 g, which replaces 22.7 g of ribs. **+82 g → score −12 %** (empty 597 g basis).
Example B: the same, but the blocks also replace the D-box and the cap strips: +58 g, **score −9 %**. The bays between the blocks are then open (film only) at the nose, so the torsion stiffness falls to that of the spar and the film. Aileron flutter and aileron reversal become risks.
Example C: 5 wide blocks (80 mm, 40 % of the span): about 93 g of blocks. The 120 mm bays then have no ribs: the film sags, and the LE and the TE have no support over the bay.
EPS 20 instead of XPS: the foam mass falls by about one third, but EPS dents easily and the surface is poor under film.

Printed LE and TE as wing parts (from `printed_vs_balsa_wing.md`): LE 18–41 g against 8.5 g in balsa; TE wedges 8–18 g against 2.7 g. **+15 to +48 g.** Printed parts used as removable jigs: 0 g.

## 3. What the concept does well
- Easy and accurate build: the balsa plates are the hot-wire templates, and each block comes out square and true to the airfoil. The team has a hot-wire cutter.
- Local strength: foam resists crushing (hand launch grip, rubber bands, landing) and absorbs impact better than a rib.
- Large glue faces for the spar, the LE and the TE.

## 4. Risks
- Mass: every useful layout found here is 50–80 g heavier than rev A (−8 to −12 % score). The spar is still needed, because the blocks carry no bending across the hollow bays.
- Torsion: low, unless the D-box stays (then the mass is highest).
- Process: CA attacks XPS and EPS (use PVA, epoxy or foam-safe CA). The iron for the covering film (110–120 °C) can melt the foam surface.
- Printed LE/TE in the airframe: heavy, and brittle across the layers in a nose-first impact (study §4).

## 5. Claude's view before the answers
As a method for the whole wing, it is **worse** for the score (+50 to +80 g) and it does not remove the spar, LE or TE. Two parts of the idea are good:
1. Foam used locally, where crushing and impact occur: the tips (about the same mass as the rev A tip rib + ring cap) and possibly the centre band seat.
2. Printed parts as **removable building jigs** (rib-alignment, LE/TE cradles with block locators): the build gets easier and more accurate at 0 g.
Recommendation (provisional): keep rev A. Add foam tip blocks and printed jigs, if the answers do not change the goal.

## 6. Questions for the user
1. The main goal of the change: easier build, more robust, or lighter?
2. Foam type, block width and number of blocks.
3. Spar and D-box: kept or removed?
4. Printed LE/TE: part of the wing in flight, or only a jig?
5. In the sketch, what is the "Balsa" above each block: an airfoil plate on each face, or a cap on top?

## 7. User's answers (2026-11-22)
- Goal: all four (easier and faster build, more robust, lighter, better airfoil accuracy).
- Blocks: a few wide blocks (about 3 to 7 blocks, 50 to 100 mm wide), long hollow bays between them.
- Spar and D-box: both stay.
- Printed LE and TE: part of the wing in flight, and they join the blocks.

## 8. Mass of the user's layout (ribs and cap strips removed, D-box and spar kept)

Change against rev A (156.6 g). The score change is on the 597 g empty basis.

| Foam | Blocks | Printed LE/TE in LW-PLA 0.55 | Printed LE/TE in PLA |
|---|---|---|---|
| EPS 20 | 3 × 80 mm | +28 g (−4.6 %) | +60 g (−9.2 %) |
| EPS 20 | 5 × 50 mm | +34 g (−5.4 %) | +66 g (−9.9 %) |
| XPS 30 | 5 × 50 mm | +51 g (−7.9 %) | +83 g (−12.2 %) |
| XPS 30 | 5 × 80 mm | +83 g (−12.1 %) | +114 g (−16.1 %) |

No layout is lighter than rev A. The lightest (EPS, 3 blocks, LW-PLA) is +28 g, and it has bays of about 190 mm. The rev A rib pitch is 55 mm.
Not included: ribs in the bays. Over a 100 to 190 mm bay, the film pulls the TE and the false spar inward, and the film aft of the spar sags. Most built-up wings need a rib at 75 mm or less for this reason *(interp.)*. With ribs added back, the "easier build" gain gets smaller.
D-box skin buckling: the skin panel is about 80 mm wide (LE to spar). Longer bays decrease the buckling load by only about 15 % *(interp., flat-plate k from 4.6 to 4.0)*, so the D-box stays sufficient.

## 9. Weighted comparison (weights from D-003: mass 5, robustness 4, build 3, accuracy 2)

| Criterion | Weight | A: rev A balsa | B: user's foam blocks (5 × 50 mm XPS, spar + D-box, LW-PLA LE/TE, +51 g) | C: rev A + foam tip blocks + printed removable jigs (≈ +1 g) |
|---|---|---|---|---|
| Mass (5 at 156.6 g, −1 for each 35 g) | 5 | 5 | 3.5 | 5 |
| Robustness | 4 | 3 | 3.5 (blocks resist crushing; printed LE is brittle in a nose impact) | 3.5 (foam tips take cartwheels) |
| Build ease and speed | 3 | 2 | 4 | 3 (jigs set the ribs, LE and TE) |
| Airfoil accuracy | 2 | 4 | 3 (blocks are exact; bays sag) | 4.5 |
| **Total** | | **51** | **49.5** | **57** |

Recommendation: **C**. It keeps the rev A mass and takes the 2 good parts of the user's idea: foam where impacts occur and printed parts that make the build accurate.
What B does better: the fastest build, and the largest glue faces.
What would make B win: (1) the team cannot build rev A by the deadline (A3: 10 Dec 2026); or (2) weighed samples show a much smaller mass penalty, for example hollowed EPS-15 blocks with balsa LE and TE.
Cheapest test: build one 165 mm span sample of A and of B, weigh both and press both by hand.
