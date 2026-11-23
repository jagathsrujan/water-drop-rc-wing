# Fuselage rev B — balsa pod, version 2 (designed for balsa construction)

Laser-cut balsa and ply pod with printed PETG permanent jigs and hard points. The twin Ø10/8 carbon tubes, the tail, the electronics (D-066), the wing rev A and every reservoir interface value (plan 03 §13) are the same as rev A. Rev A (`design/cad_fuselage/`) is not changed. Status: **adopted fuselage (D-068, 2026-11-23)**; rev A stays as the printed reference.

- Model: `Fuselage_revB_balsa.FCStd`. Rebuild in FreeCAD 1.1 (GUI): `BAL_SCRIPTS = "<repo>/design/cad_fuselage_balsa/scripts"` then `exec(open(BAL_SCRIPTS + "/run_all.py").read())` (about 2.5 min). Reads `Fuselage_revA.FCStd` for the reference bodies and never saves it.
- Numbers: `scripts/bal_params.py`. Checks: `check_report.txt` (all PASS). Mass: `mass_table.md`. Strength: `strength_estimate.m` → `strength_estimate.txt` (MATLAB). Pictures: `img/`.
- **STEP for Onshape / SolidWorks:** `export/WaterDrop_revB_assembly.step` (AP214, mm, 24.9 MB): top assembly `WaterDrop_Aircraft_revB` with the subassemblies `Fuselage_BalsaPod` (34 parts), `Reservoir` (27, closed state, no water volume), `Wing_revA` (89 real wing parts at +3°), `Tail` (10), `Electronics` (8 placeholders incl. the swept prop disc); every part named and coloured. Jigs separately in `export/Jigs_revB.step`. Onshape: Import → keep "Create assembly" ticked. SolidWorks: File → Open → STEP (opens as an assembly with parts). Read back in FreeCAD: 168 bodies, 266 solids, all valid.
- Clearance checks use hidden copies of the side layers without the hex holes (`PX_*`, conservative); mass uses the real panels.

## Construction
| Item | Build |
|---|---|
| Shape | Flat panels only. Sides and floor bend at the front stop (nose kink, X −29.2) and at the bulkhead (tail-cone kink, X 236): every kink sits on a former, no compound curves |
| Sides | 1.5 mm medium balsa (grain X) + 1.0 mm inner layer glued with crossed grain = 2.5 mm; inner layer in 1.0 mm birch ply in the launch-grip zone (X 30–130, lower half); 348 hex cells 8 mm across flats, 2.5 mm webs, film on both faces. Solid at the grip zone, round the holes and ±5 mm at every former |
| Right side at the release servo (X 44–96) | Single layer (§13: inner face ≥ Y 53.5) in 1.5 mm birch ply (balsa there fails the grip squeeze) + PETG D-059 arm pocket |
| Floor | 1.5 mm balsa, grain across (§13: outer −117, inner −115.5), 2 balsa keels 5 × 3 and 6 × 6 corner longerons through the formers |
| Cross members | 3 mm lite-ply U-formers at X 38, 105 (split round the belly opening), 170 (behind saddle 2), open at the top for the bottle lift-out; lower corners cut outside a 13 mm band round the bottle. Nose U-formers at X −130, −100 carry the battery tray. The wing closes the box when it is on |
| Front stop | 3 mm lite-ply bearing ring r 25–42 + rim + 4 spokes (10 g nose-in load of the water) |
| Bulkhead (X 236) and end former (X 302) | 3 mm birch ply ring + bar and 3 mm lite-ply end former, tubes glued through Ø10.3 holes with birch-ply rings; support span 69 mm. A removable printed fixture squares the end former to the tubes during the glue-up |
| Printed permanent jig (PETG) | Nose ring: collar + glue sleeve, seats the 3 mm birch-ply firewall (thrust wedge in F-D) |
| Saddles | Reservoir P12a/b outline (thin cradle arc + base with the strap tunnel) as laser-cut 3 mm lite-ply layers glued face to face on the bottle wrapped in cling film (the bottle is the jig); strap bridges in lite-ply |
| Other | PETG D-059 servo pocket + shelves; 1.5 mm birch-ply skids |
| Top | Wing-seat capstrip 6 × 3; nose hatch 1.5 mm light balsa in two flat pieces on 3 × 3 ledges, 4 magnet pairs; aft deck 1.5 mm |

## Result (densities interp.: medium balsa 0.14, light 0.10, birch ply 0.65, lite-ply 0.45, PETG 1.27 g/cm³; glue 10 % of wood)
| | Rev A printed ASA Aero 0.65 | Rev B v1 (thin box) | Rev B v2 before the trims | **Rev B v2, adopted (D-068, D-069)** |
|---|---|---|---|---|
| Pod (same scope) | 120.9 g, no internal structure | 91.0 g | 141.6 g | **133.1 g** |
| Empty aircraft | 677 g | 647 g | 698 g | **689 g** |
| Score | 147 | 154 | 143 | **144.5** |
| Loaded stall, Bengaluru | 9.14 m/s | 9.06 m/s | 9.20 m/s | **9.17 m/s** |
| Strength (D-064 loads, ultimate 1.5 × limit) | removed FEM study: 6–65 × allowable without ribs | front stop, right side fail | margins ≥ 1.16 | **design loads ≥ 1.31** |

Margins (allowable / ultimate stress, `strength_estimate.txt`): front stop ring 3.8, spokes 1.3; side in the grip zone 1.61; right side ply insert 1.93; frames ≥ 4.0; tail cone 19; floor over the skids 1.4–1.8; saddle bearing 9.5.
Handling rule: a 20 N finger squeeze outside the grip zone (1.5 + 1.0 mm balsa) has margin 0.80 at ultimate (1.2 at the limit load); carry the aircraft by the grip zone or the wing.
Biggest free saving: weigh every sheet and use light stock (0.10–0.12) for the inner layers, hatch and deck; set `RHO` in `bal_params.py`.

## Assembly: self-locating parts and removable jigs (D-069)
**Stays in flight:** every former (nose frames, front stop, bay frames, bulkhead, end former) has 2 floor tabs and 2 side tabs (8 mm wide, former thickness long) that pass through laser-cut slots in the floor and the side laminate; sand them flush. Keels and longerons pass through notches in the formers. The PETG nose ring is the only printed part in the pod.

**Removable jigs** (PLA, about 218 g of filament at 30 % infill; STL in `jigs/`, model orientation; all fit the 256 mm bed; checked: no overlap with the pod, tubes, reservoir or electronics, contact 0.00 mm where they locate):

| Jig | Use | Print |
|---|---|---|
| J1a nose wedge, J1b tail wedge | Screw to a flat building board; the bay floor lies flat on the board, the wedges hold the nose floor (16°) and tail-cone floor (39°) at their angles; grooves clear the skids | flat bottom down |
| J2 side squares ×4 (X 8–28, 140–160, both sides) | L-blocks against the outer side faces: sides vertical while the floor/former joints cure | base down |
| J3 nose taper blocks L/R | Hold the nose sides at their plan angle between the front stop and the nose ring | base down |
| J4 tube cradles ×2 (X 305–330, 600–620) | Hold both tubes parallel at Y ±16, Z −40 above the board; the first cradle's front face squares the end former. Glue the tubes into the bulkhead and end former with the cradles in place: this sets the tail incidence | base down |
| J5 wing-seat gauges ×2 (X 0–140, 140–280) | Wing lower surface at +3° + 1 mm foam: sand the side tops and the capstrip until the gauge sits without rocking | flat top down |

**Build order:** (1) laminate the side layers flat under weights; (2) screw J1 to the board, lay the floor, drop the formers into their slots, add keels and longerons; (3) add the sides onto the tabs with J2 and J3; (4) nose ring + firewall; (5) tubes through the bulkhead and end former on the J4 cradles; (6) aft deck, capstrip, sand with J5; (7) saddles on the cling-wrapped bottle, then glue them in; (8) film, skids.

