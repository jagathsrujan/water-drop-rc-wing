# Engineering notebook: water reservoir and release mechanism

Stage started 2026-11-22. Process: cad-codesign, all steps (mechanism, more than one session).
Decision IDs for this stage start at D-033.

## 1. Inputs that exist

| Input | Value | Source |
|---|---|---|
| Payload | 1000 mL, about 996 g at 28 to 30 °C | rule + stage 1 |
| Reservoir | "sealed, securely mounted, and removable interior reservoir" | rule |
| Empty weight | Reservoir and release mechanism count in the empty weight | rule |
| Inspection | Judges inspect reservoir, mounting, release before take-off; exterior dry, zero visible leakage | rule |
| Qualifier | Fly ≥ 30 s with the full payload; no release needed; visible leakage before landing = score 0 | rule |
| Main round | Release on one channel, only by the pilot; release must begin over the zone; ≥ 30 s of flight before release | rule |
| Water released | Organizers weigh the removable reservoir immediately before and after the attempt | rule |
| Leakage | Leakage before the release does not count; if judges cannot tell leakage from release, the release score is 0 | rule |
| Abstract | Must explain reservoir, mounting, release mechanism, leakage prevention, CG management, safe operation | rule |
| Wing | SD7062, chord 280 mm, span 990 mm, high wing, rubber bands on 2 dowels, 156.6 g | D-001…D-023 |
| Mass without wing | 440 g *(interp., A1)*; empty about 597 g; loaded about 1593 g | brief |
| Fuselage | Not designed yet | — |
| Electronics | Must be sealed from the payload water | stage 1, section 6.5 |

## 2. Numbers (calculated 2026-11-22)

- Score sensitivity: at 597 g empty, each 10 g of empty mass costs about 2.75 score points (1.6 %).
- Residual water: in the main round, 1 g of water left in the reservoir costs about the same as 0.6 g of empty mass (100/E against 99600/E²). Complete drainage is a requirement, not a detail.
- Water mass fraction: 996 / 1593 = 62 % of the flight mass.
- Mount and seal loads (water only): 49 N at 5 g, 78 N at 8 g, 98 N at 10 g. The qualifier lands with the full water. A hand-launch aircraft lands on its belly.
- Drain time, vented rigid tank, Cd 0.6, at 1 g:

| Tank | Head | Outlet 20 mm | 25 mm | 35 mm | 45 mm |
|---|---|---|---|---|---|
| Ø80 mm (1 L bottle) | 199 mm | 5.4 s | 3.4 s | 1.8 s | 1.1 s |
| Ø90 mm | 157 mm | 6.0 s | 3.9 s | 2.0 s | 1.2 s |
| Ø105 mm (near a cube) | 115 mm | 7.0 s | 4.5 s | 2.3 s | 1.4 s |

  Without a vent, a rigid tank "glugs" and the drain time is about 2 to 3 times longer *(interp.)*.
- Ram pressure at 13 m/s, ρ 1.15: about 97 Pa, about 10 mm of water. Small against the 100 to 200 mm head.

## 3. Rule interpretations that change the design *(interp., to confirm)*

1. **The release must begin in the zone. It need not end in the zone.** Then the drain time is not the main driver. A smaller outlet gives a lighter valve, a shorter seal line and less leak risk. A long drain (more than about 10 s) still gives a long period of CG and trim change. Confirm with the organizers.
2. **The reservoir is weighed full, outside the aircraft.** Thus the valve must be part of the reservoir and must seal when the reservoir is out of the aircraft. The servo link must disconnect quickly, or the servo goes on the scale with the reservoir. The same set of parts must be on the scale before and after.
3. **The qualifier landing is with the full water.** The valve and its seal must survive a belly landing with 996 g on them. An outlet on the fuselage bottom is in the impact area.
4. **A vent is a leak path.** A rigid tank needs a vent that opens on the same channel (one servo can open the outlet and the vent). A collapsible reservoir needs no vent.
5. **Fill and a dry exterior.** The organizers pour the water. The fill port must take 1000 mL fast without a spill (the 120 s timer). The volume needs ullage margin (about 5 to 10 %, *interp.*).
6. **The outlet must be the lowest point at the flight attitude after the release**, not at the bench attitude. The water must not stay in corners.

## 4. My view before the interview (written before I asked the user)

**Layout.** The reservoir sets the fuselage section at the CG, not the reverse: it is 62 % of the flight mass and the largest single volume. The water centroid goes on the empty-aircraft CG in X (about 25 to 30 % of the 280 mm chord, x ≈ 70 to 85 mm aft of the wing LE, *interp.*). Then the release does not move the CG in X. The tank should be short in X and tall in Z: the free surface then moves the CG less in pitch during the drain and in climbs. A bottom outlet on the CG station keeps the centroid in X fixed as the water drains.

**Candidate concepts (my ranking, not shown to the user before their answer):**

| Rank | Concept | Mass estimate (tank + valve + servo + mount) | For | Against |
|---|---|---|---|---|
| 1 | Thin PET water bottle (1 L), neck down, vertical at the CG; printed valve cap on the neck; vent at the top opened by the same servo | about 50 to 60 g *(interp.: bottle 20 to 30 g, to weigh)* | Lightest, cheapest, food-grade seal, off the shelf, easy to photograph | Ø80 × 230+ mm sets a deep fuselage; vent needed; neck Ø21.7 mm limits the outlet (drain about 5 s vented, longer unvented) |
| 2 | Collapsible bag or soft bottle in a light cradle; bottom outlet valve; no vent | about 50 g | No vent, no slosh, no glug | Availability in India, puncture risk, residual water in folds, cradle needed for "securely mounted" |
| 3 | Custom tank (vacuum-formed PETG, glass/epoxy or printed PETG), near a cube 105 mm, funnel floor | 40 to 70 g + seal | Free shape, fits the fuselage best | Heavier, leak risk at every seam, more build time; LW-PLA is porous when foamed (*interp.*, test coupon needed); PLA fails R12 heat |

**My first choice:** concept 1, because it is the lightest and cheapest and has a factory seal. The open points are the vent and the fuselage depth.

**What would change my mind:** the user has a different fuselage concept that cannot take a deep section; a collapsible bottle is available at a low mass; the organizers want the release to finish in the zone.

## 5. Checks still to do
- Weigh the real candidate containers (1 L bottles of different brands, any soft bottle).
- LW-PLA and PETG water-tightness at thin walls: data or a test coupon.
- Check each candidate against each word of the rule: sealed, securely mounted, removable, interior.

## 6. Interview record
| Date | Question | User's answer | Effect |
|---|---|---|---|
| 2026-11-22 | Does the reservoir set the fuselage, or the reverse? | Reservoir first, then the fuselage | D-033. Agrees with my view. The reservoir stage must give the fuselage stage: outside envelope, water centroid station, mount points, outlet position. |
| 2026-11-22 | Describe the release | Servo with a disc at the end; the disc covers the opening; the servo turns the disc away and the water flows out | User's valve concept U1 (section 8). Form of the disc motion still unknown |
| 2026-11-22 | Launch | Hand launch (confirmed again) | Grip position still unknown |
| 2026-11-22 | Containers | 1 L PET bottle, or 1 to 1.2 L spout pouch | Containers C1 and C2 (section 8). Masses, sizes and spout bore unknown |
| 2026-11-22 | Release mechanism (gate 2) | "lets go with claude pick" after the 3D page | D-034 = V2 pin-latched trapdoor. V1 is the fallback; no V1 test print |
| 2026-11-22 | Container | Has neither container; proposes a Coke / Sprite 1 L bottle | D-035 = 1 L CSD PET bottle. Checked: meets the brief, about 5 to 10 g heavier than a thin water bottle, vent necessary |
| 2026-11-22 | Container (update) | Only 1.25 L Coke / Sprite and 1 L Bisleri are available; chose 1 L Bisleri | D-035 update: Bisleri 1 L. Neck and mass to measure; drain test with and without a vent |
| 2026-11-22 | Ports | Two valves: top for loading, bottom for unloading; holes in the bottle, printed valves, washer or plumbing glue | D-036 proposed: keep the top fill/vent port (good idea); release on the neck, no bottom hole; clamped bulkhead with washers, not glue |

## 7. Wing inputs and what they mean for the reservoir (2026-11-22)

Sources: `design/02_wing_plan.md`, `design/aero/wing_lift_performance.md`, `design/cad/mass_table.md`, D-005, D-008.

| Wing fact | Value | Effect on the reservoir |
|---|---|---|
| Planform | Rectangular, chord 280 mm = MAC, LE at x = 0 | CG station from the chord directly |
| CG station | 25 to 33 % MAC → x ≈ 70 to 92 mm; provisional x = 80 mm *(interp.: final value from the tail volume in the fuselage stage)* | Water centroid at x = 80 mm; the outlet on the same station |
| Main spar | x = 72.6 to 78.6 mm | The water centroid is near the spar: the lift and the water weight are on almost the same line, so the fuselage carries little bending between them |
| Centre sheeting (saddle) | y = −55 to +55 mm, full chord | Fuselage width at the saddle ≤ 110 mm. A wider reservoir must be below the saddle and the fuselage must taper up |
| Aileron servo wires | Exit the bottom centre sheeting at x ≈ 130 mm | The reservoir top must leave a wire path at x ≈ 130 |
| Attachment | Rubber bands over 2 dowels, one-piece wing | With the wing off, the top of the fuselage is open: a top-loaded reservoir is possible, but each fill then needs a wing removal (120 s timer). To decide |
| Incidence | +3° to the fuselage datum; fuselage about 2° nose-up loaded at 13 m/s, near level after release at 9 m/s | The outlet must be the lowest point from about −2° to +5° pitch *(interp.)*: floor slope ≥ 10° to the outlet |
| Loaded stall | 8.9 m/s Bengaluru, 8.5 m/s Chennai (9.2 / 8.8 with tail down-load) | Each +10 g of reservoir adds only about 0.03 m/s. The reservoir mass is a score problem, not a lift problem |
| Max load factor in flight, loaded (wing stalls first) | 2.1 at 13 m/s, 2.8 at 15 m/s (Bengaluru); 2.3 / 3.1 (Chennai) | Water load on the mount in flight 21 to 30 N. The landing (49 to 98 N at 5 to 10 g) is the design case |
| Release | Mass 1593 → 597 g (−62 %). At 13 m/s the lift is then 2.7 × the weight; the same CL needs only 8 m/s | A fast dump (1 to 2 s) gives a sharp pitch-up and climb. A drain of about 4 to 8 s gives the pilot time to push and trim. This supports a moderate outlet (about 20 to 25 mm, vented), not a fast dump *(interp.: confirm in the test flights)* |
| Mass in the lift calculation | 440 g (aircraft without wing, A1) + 156.6 g (wing without servos) | The 27.4 g of aileron servos must be inside the 440 g, or the empty mass is 624 g. The 440 g also holds the reservoir. Reservoir budget proposal: ≤ 50 g including valve and mount, without the release servo *(interp.)* |

## 8. Check of the user's concepts (2026-11-22)

### U1: servo-driven disc over the outlet (user's valve)
The idea works. The result depends on how the disc moves:

| Form | Load path at landing | Check | Result |
|---|---|---|---|
| U1-a: disc turns **in its own plane** and slides over the hole (gate / shutter); servo shaft normal to the outlet face | Water pressure pushes along the shaft into the bearing and the frame, not into the gears | Seal preload from a spring or clamp, not from the servo. Friction torque at r 20 mm: preload 5 to 10 N, μ 0.3 → 0.03 to 0.06 N·m = 17 to 34 % of the MG90S stall torque (0.177 N·m) | Good. Needs a low-friction face (PTFE tape, smooth PETG on silicone) and a test of the friction when wet |
| U1-b: disc on the servo arm **swings away like a door**, outside the outlet | Water pressure pushes the disc open; only the servo torque holds it shut | 22 mm outlet, 200 mm head: 0.74 N at 1 g, 7.4 N at 10 g. MG90S at r 20 mm holds 8.8 N maximum. A hard landing can push it open → leak before release → qualifier score 0. The servo also stays loaded all flight | Marginal. Not acceptable without a latch or an over-centre lock |
| U1-c: door **inside** the reservoir (water pressure holds it shut, as a toilet flapper) | Water pressure pushes the disc shut | Servo pulls 0.74 N + seal stiction to open | Self-sealing, but the link goes through the wall: a second seal |

My view: U1-a is the right form of the user's idea. Ask which form the user means.

### C1 / C2: containers

| Item | C1: 1 L PET bottle, neck down | C2: 1 to 1.2 L spout pouch |
|---|---|---|
| Mass *(interp., to weigh)* | 20 to 30 g | 10 to 15 g |
| Outlet bore | 21.7 mm (PCO 1881 neck) → about 4.5 s vented | Depends on the spout: 8.6 mm → 30 s, 10 mm → 22 s, 16 mm → 8.5 s, 22 mm → 4.5 s |
| Vent | Necessary. Headspace is only about 4 % (996 mL in about 1040 mL brim-full), so the water touches a top vent hole in slosh → a top vent must also have a valve. Without a vent the bottle glugs (about 2 to 3 × slower, about 10 to 13 s) or collapses in part | Not necessary: the pouch collapses |
| Shape and mount | Rigid, known shape, Ø about 80 mm; mount by a neck collar and one strap | Soft, shape changes with the water: needs a cradle (the fuselage bay walls can be the cradle) |
| Residual water | Low, if the neck is the lowest point | Folds can close before the pouch is empty: test needed |
| Valve fit | Printed valve cap on the 28 mm neck thread | Valve cap on the spout thread (spout size not known) |
| Fill | Fill upright, screw on the closed valve cap, turn over | Fill through the spout, screw on the valve cap |

Both fit the 110 mm saddle width. The decision between C1 and C2 waits for the real masses and the spout bore.

## 9. Release mechanism concepts (2026-11-22, user asked for better options)

### Candidates
| ID | Mechanism | How the landing load (full water, belly) is carried |
|---|---|---|
| V1 | User's rotary disc gate (U1-a): disc turns in its own plane, spring-loaded face seal | Along the servo shaft into the frame |
| V2 | Pin-latched trapdoor: flap with a soft flat gasket, hinge on the front edge, latch hook on the rear edge; a steel pin through the latch holds it shut; the servo pulls the pin; a light spring and the airflow swing the flap aft | Into the pin (shear) and the hinge, never into the servo |
| V3 | Radial plug (O-ring plug in the bore) pulled out by the servo | Plug friction (and a retaining pin) |
| V4 | Film seal over the outlet, cut by a servo blade | Film; new film each flight |
| V5 | Pinch valve on a silicone tube | Servo holds the tube shut all the time |
| V6 | Printed butterfly valve | Shaft; edge seal |
| V7 | Inside flapper (U1-c): the water pressure holds it shut; the servo lifts it | Water pressure closes it (self-sealing) |
| — | Commercial ball valve | Out: plastic 3/4 in valve 40 to 60 g, dry torque 0.3 to 1 N·m > MG90S 0.177 N·m |
| — | Drop the whole reservoir | Out: the reservoir is weighed after the flight; a falling 1 kg mass is a safety risk |

### Weighted scores (my estimates, 1 to 5; the user can change the weights)
| Criterion | Weight | V1 | V2 | V3 | V4 | V5 | V6 | V7 |
|---|---|---|---|---|---|---|---|---|
| Leak-tight until command (handling, weighing, 10 g landing) | 30 | 4 | 5 | 4 | 5 | 2 | 2 | 5 |
| Mass | 20 | 4 | 4 | 4 | 5 | 4 | 4 | 3 |
| Opens fully every time on command (wet, after vibration) | 20 | 3 | 4 | 3 | 2 | 4 | 4 | 4 |
| Full bore, no water left | 10 | 5 | 5 | 4 | 3 | 1 | 4 | 4 |
| Simple, cheap, quick to build | 10 | 3 | 4 | 3 | 3 | 4 | 3 | 2 |
| Re-arm in less than 120 s | 5 | 5 | 4 | 4 | 2 | 5 | 5 | 3 |
| Open state survives the landing after release (attempt 2) | 5 | 5 | 3 | 4 | 5 | 5 | 5 | 5 |
| **Total /100** | | **78** | **87** | **74** | **77** | **64** | **68** | **78** |

The scores are my judgement, not measurements. V1, V7 and V4 are within 1 point. Only a test can make the V1/V2 difference certain.

### Force checks
- Water force on a 22 mm outlet, 200 mm head: 0.74 N at 1 g, 7.4 N at 10 g.
- V2 pin pull in flight (1 to 2 g), μ 0.3: 4.7 N with a 15 N gasket preload, 15 N with 50 N preload. MG90S at a 10 mm arm: 17.7 N. **Condition:** use a soft flat gasket (silicone sheet or EVA foam) with a low preload, or a latch shape that keeps the gasket force off the pin. Measure the pull force with a spring scale before the build. An O-ring face seal can need 50 N or more and then V2 fails.
- V1 seal friction: 17 to 34 % of the servo torque at 5 to 10 N preload, μ 0.3 (section 8). Wet friction is not known.

### Failure modes for every candidate
1. Servo twitch at power-up: the pin engagement (V2) or the disc overlap (V1) must be larger than the twitch travel.
2. Qualifier: a release counts as leakage → score 0. Add a removable mechanical safety lock (pin with a flag) for the qualifier and for transport.
3. Bottle only: the vent valve is part of the release mechanism (section 8). V2 can release the vent with the same pin; V1 needs a second disc or a link.
4. Belly landing: recess the valve above the fuselage floor; the outlet goes through a hole in the floor.

### My recommendation
V2, with a test against V1 before the choice is final. Build the valve as a cap unit with a thread (28 mm PCO 1881 bottle neck, or an adapter for the pouch spout) so that the container choice stays open.
What V1 does better: no part hangs below the outlet after release; it can close again (bench tests).
What would make V1 win: wet friction torque below about 30 % of the servo stall torque, and no weep in a 10 g drop test with full water.

### Assumptions while the user's answers are open *(interp.)*
- Container masses: bottle 25 g, pouch 12 g. Pouch spout bore: unknown (10 mm and 22 mm both possible).
- Launcher grip: under the wing at the CG, fuselage ≤ 90 mm wide at the grip.
- 10 Dec: CAD pictures plus a built valve on a bottle with a bench drain test (cheap, gives abstract photos).

## 10. Container choice without samples (2026-11-22)

The user has neither container on hand. Data from a web search (standard mode):

| Item | 1 L PET bottle (C1) | 1 L spout pouch (C2) |
|---|---|---|
| Mass | 28 g lightest finished 1 L bottle on PCO 1881 (ALPLA catalogue); 33 to 36 g typical (ALPLA, Petainer). Indian still-water bottles are often lighter *(interp., to weigh)* | No 1 L data found; about 10 to 15 g *(interp.)* |
| Neck / spout | 28 mm PCO 1881 or PCO 1810 on soft drinks; Indian still-water bottles can use a different short neck *(interp.: measure the real bottle before the cap thread is drawn)* | Indian sellers list stock spouts of 10 mm and 16 mm; one 21 mm spout found only on a small beverage pouch |
| Drain (vented / pouch) | About 4.5 s through about 22 mm | 16 mm → 8.5 s; 10 mm → 22 s |
| Availability | Any shop, about ₹20 to 30, today | Stock pouches from 100 pieces, custom from 1000; 1 L price not listed; delivery time unknown against 10 Dec |
| Vent | Needed, or the thin wall collapses: test both | Not needed |
| Mount | Rigid, neck collar + strap | Needs a cradle (mass) |

**My view:** C1, the PET bottle. It is available today at almost no cost, it is rigid for a secure mount, and the bore gives the 4 to 8 s drain of R16. The pouch saves about 15 to 20 g (about 3 % score) but needs a cradle that takes back part of the saving, has a slow stock spout, and has a supply risk before 10 Dec.
**Test to add:** drain of the inverted bottle without a vent (thin wall collapses?) and with a vent. If it drains fully in less than about 10 s without a vent, the vent is not necessary.
**Action for the user:** buy one 1 L still-water bottle; weigh it; measure diameter, height, neck thread outer diameter and bore.

Sources: https://product-catalogue.alpla.com/product/1000-ml-beverage-bottle-pco-1881 ; https://www.petainer.com/pet-plastic-bottles/water-bottles/1l-water-bottle-28mm-pco-1810 ; https://m.indiamart.com/impcat/spout-pouch.html ; https://www.tradeindia.com/products/spout-pouches-9929067.html

## 11. Full drainage through the neck (user question, 2026-11-22)

- Neck down and vertical, the neck is the lowest point of the bottle. The shoulder slopes to the neck at about 25 to 40° *(interp., measure on the Bisleri bottle)*. All free water flows to the neck if the bottle tilt plus the aircraft pitch stays below the shoulder angle. Loaded pitch is about +2°, after release about 0° (D-005): large margin.
- In a coordinated turn the apparent gravity stays along the aircraft vertical axis, so the water still goes to the neck.
- Water that stays: only a wet film and drops on the wall. Wetted area about 710 cm². Film 0.02 to 0.1 mm → 1.4 to 7.1 g → 0.14 to 0.71 % of the released water *(interp.)*.
- A hole at another place is worse: the base of a water bottle has a domed or petaloid shape with pockets, and a side hole leaves the water below it.
- Design rules that follow:
  1. The bore of the valve cap must be equal to or larger than the neck bore, with no step or pocket under the neck lip.
  2. Keep the bottle axis within about 20° of the fuselage vertical (shoulder angle minus pitch margin).
  3. Keep the flap and the gasket out of the stream after release, so that no puddle stays on them.
- Test: weigh the empty valve-and-bottle unit dry, fill, drain neck down for the planned release time, weigh again. The difference is the residual water.

## 12. Fuselage depth with a vertical bottle (user concern, 2026-11-22)

User: "if the water bottle is placed vertical the fuselage height will be too much". Valid: belly to wing underside about 300 mm.
Cost of depth: about 0.1 g of side panel per mm of depth (1.5 mm balsa, 120 kg/m³, 300 mm bay, 2 sides), so 180 mm extra ≈ 19 g ≈ 3 % score; frontal area 300 × 90 mm ≈ 0.027 m² → about 0.8 N drag at 13 m/s (blunt, Cd 0.3, *interp.*) against about 1.4 N wing drag; large side area in crosswind.

| Option | Depth (belly to wing) | Water left | Drain | New holes / seals | CG during the drain | Notes |
|---|---|---|---|---|---|---|
| H1 vertical, neck down (current) | about 300 mm | film, 1 to 7 g | 2.8 s vented | 1 at the top (air side) | no shift in X | simplest |
| H2 tilted 35 to 45°, neck down | about 230 to 260 mm | film, if tilt − pitch > shoulder angle (about 31°, *interp.*) | similar | 1 at the top | water slides toward the neck: X shift | saves only 40 to 70 mm |
| H3 horizontal, outlet hole at mid-length bottom | about 105 mm | 0 g level, 5 g at 2° pitch, 19 g at 5°, 38 g at 8° | about 12 s (Ø14 bore, inner flange through the neck) | 1 at the bottom (full pressure, landing zone, curved wall) + vent at the top | small if level; water runs to the low end at pitch | lowest, lightest fuselage; needs a curved-wall bulkhead test |
| H4 two 500 mL bottles, vertical, tandem about the CG | about 235 mm | film | similar | 2 valves on one pin line | none if both drain equally | +about 10 g (second bottle and valve), *interp.* |

**My view:** the user's need (a low fuselage) is decisive. H3 gives by far the largest gain (−195 mm, about −19 g of fuselage, less drag). Its costs are a seal in the bottom of a thin curved wall and residual water that depends on the pitch at release. H3 is the best choice if a bench test of the curved-wall bulkhead passes (no weep at a 10 g equivalent drop) and the residual at 0 to 3° pitch stays under about 10 g. H1 stays the fallback. H2 and H4 give too little gain for their cost.
Mount H3 with the bottle level at the release attitude (fuselage about 0°), outlet at the CG station.

### 12.1 H3 concept model (2026-11-22, user: "model h3")
3D concept page `design/studies/reservoir_layout.html` (published as an artifact). Bottle shape re-estimated to 1040 mL brim (Ø80, cylinder to yu 185, neck lip 255, *interp.*); water centroid 105 mm from the base, placed on the CG (x = 0 in the page frame), neck aft.
H3 as modelled: outlet bulkhead at mid-length bottom (Ø14 bore, 1.5 mm inner lip), V2 below, vent bulkhead at the top with a plug lifted by the same pin line, 2 printed saddles at ±70 mm with straps, wing chord at y = 70.
Calculated in the page (vented, Cd 0.6): fuselage depth belly to wing about 125 mm (vertical layouts 286 to 298 mm); drain 11.6 s level; water left 4 g at 0°, 5 g at 2°, 13 g at 5° pitch (replaces the rough 19 g at 5° in the table above).
Not yet modelled: the curved shape of the bulkhead flanges (drawn flat), the fuselage structure, the real bottle dimensions.

### 12.2 Vent position (2026-11-22)
User: H3 is good, but a hole through the wing is needed for the release mechanism. Check: no; see D-038. The vent moved to the forward top end (x = CEN − 16 ≈ 89 mm, page frame), ahead of the LE at 80 mm; the pin line runs on the +z side of the bottle. Page republished.
