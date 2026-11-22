# 02 — Wing structure and modelling plan (rev A)

Status: approved (gate 3, per the task brief 2026-11-21). Built as wing CAD rev A — see §9 "As built" for the values that changed during the build.
Decisions in force: D-001 SD7062 (user), D-002 chord 0.28 m (user, first value), D-003 balsa built-up, "as robust as possible while lightweight" (user), high wing (user), rubber-band attachment (user), FreeCAD (user), 9 g metal-gear servo MG90S (Claude by rule, user picked the model).

## 1. Global frame and main dimensions

- Origin: wing leading edge at the centreline, chord line horizontal at the root. X aft, Y to the right wing, Z up. Incidence (+3°) is added when the wing goes on the fuselage, not in the wing model.
- Dihedral 0° (changed by the user 2026-11-21): flat one-piece wing, chord line at Z = 0 along the whole span.
- Span: **990.0 mm** (tip faces at y = ±495 mm; rule ≤ 1000 mm).
- Chord 280.0 mm, constant (rectangular). SD7062 coordinates from `design/aero/airfoil_coords/sd7062.dat`, scaled × 280.
- Airfoil depth at the main spar (x = 75.6 mm): 39.1 mm. At the hinge line (x = 210 mm): 15.5 mm.

## 2. Structure — what thickness of balsa where

| Item | Material and size | Position | Reason |
|---|---|---|---|
| Ribs (normal) | **2 mm** medium balsa (about 130 kg/m³), laser cut, lightening holes aft of the spar | Every 55 mm: y = 55, 165, 220, 275, 330, 385 | 55 mm pitch holds the film shape and takes hand loads |
| Ribs at the aileron ends | **3 mm** medium balsa | y = 110, 440 | Carry the aileron end loads and the servo frame |
| Centre rib | **2 mm** medium balsa | y = 0 | Supports the centre sheeting under the rubber bands |
| Tip rib | **3 mm** balsa (two 1.5 mm sheets glued cross-grain) + soft balsa tip cap | y = 493.5 | Takes cartwheel impacts, lighter than a printed tip |
| Leading edge | **6 mm** hard balsa (about 160 kg/m³), carved to the nose shape | x = 0 to 6 | Takes launch knocks and ground strikes |
| D-box sheeting | **1.5 mm** light balsa (about 100 kg/m³), top and bottom | x = 6 to 80, full span | Torsion stiffness for the ailerons; holds the airfoil nose |
| Centre sheeting | **1.5 mm** light balsa, top and bottom, full chord | y = −55 to +55 | Takes the rubber-band load and the hand pressure |
| Main spar caps | **3 × 6 mm** hard balsa + **0.5 × 6 mm** carbon strip on the outer face, top and bottom | x = 72.6 to 78.6 | Bending; one piece tip to tip (980 mm from 1000 mm strips) |
| Shear webs | **1.5 mm** balsa, vertical grain | Front face of the spar full span; rear face also from y = 0 to 165 | Shear; closes the D-box |
| False spar (hinge spar) | **3 mm** balsa, vertical grain | x = 205 to 208, full span | Holds the aileron hinges; closes the rib ends |
| Cap strips | **1.5 × 6 mm** balsa, top and bottom of each rib | Spar to trailing edge | Film support; stops rib cracks |
| Trailing edge (non-aileron bays) | Hard balsa wedge, 25 mm wide | x = 255 to 280, y = 0 to 110 and 440 to 495 | Robust TE where the wing has no aileron |
| Aileron | Built up: **3 mm** LE (V-bevel), **2 mm** ribs at the wing rib stations, balsa TE wedge | x = 210 to 280, y = 112.5 to 437.5 (325 mm) | Light and stiff; solid balsa at 15.5 mm depth is too heavy |
| Hinges | CA hinge strips, 4 for each aileron | Centre line of the false spar | Robust, standard |
| Film | Light film (Oralight class, about 50 g/m²), white or yellow | All | Light colour keeps the wing cooler in the sun |

Rib outline = airfoil outline minus 1.5 mm top and bottom (room for sheeting or cap strips).

## 3. Aileron and servo mechanism

- Servo: MG90S (metal gear). Model with the standard size (body 22.8 × 12.2 × 28.5 mm, tabs 32.5 mm) until the user's CAD file comes; then replace it.
- Position: in the bay between the ribs at y = 110 and 165, x about 115 to 150. The servo lies on its side: output shaft along the span, body 12.2 mm deep. The airfoil depth inside the skins there is about 31 mm.
- Servo frame: printed PETG frame glued between the two ribs at the bottom skin. Printed PETG hatch (1.2 mm) with a slot for the arm, held by 4 × M2 screws. The servo screws to the hatch, so it comes out as one unit for service at the venue.
- Linkage: 1.2 mm steel wire pushrod with a Z-bend at the servo arm and a clevis (or Z-bend) at the horn. Printed PETG control horn on the aileron bottom at y ≈ 140, x ≈ 218. Pushrod under the bottom skin, about 75 mm long.
- Throw: ±15° (provisional, D-006). V-bevel on the aileron LE allows ±20° without contact.
- Wires: 8 mm holes in the ribs at x ≈ 130, from the servo bay to the centre; exit at the bottom centre sheeting into the fuselage.

## 4. Printed parts (PETG)

| Part | Why printed |
|---|---|
| Servo frame + hatch (× 2) | Exact fit to the MG90S, quick removal |
| Control horns (× 2) | Simple, light |
| Band rub plates at LE and TE centre | Stop the rubber bands cutting the film |

PETG, not PLA: PLA softens near 55 to 60 °C; a wing in the Chennai sun can reach 45 to 60 °C.
Not printed: the tip ribs (balsa is lighter and absorbs impact).

## 5. Laser cutting

- Bambu H2D laser module. The work area (about 310 × 270 mm, check the exact value) takes a 280 mm rib and a 100 mm wide balsa sheet cut to 300 mm lengths.
- An outside laser cutter is an option for speed; the DXF files are the same.

## 6. Build in FreeCAD (execution)

Document `Wing_revA`, saved at `design/cad/Wing_revA.FCStd`. Each part is one `Part::Feature` with a clear name and a colour per material. Continuous parts (LE, sheeting, spar caps, false spar) are one piece tip to tip. Ribs: build the right side, then mirror.

Stages (an update with pictures after each):
- **Stage A — primary structure (right half, then mirrored):** ribs, centre rib, tip rib, LE, D-box and centre sheeting, spar caps (balsa + carbon), shear webs, false spar, cap strips, TE wedges.
- **Stage B — aileron and servo:** aileron (built up), hinge line, servo bay frame, hatch, MG90S placeholder, control horn, pushrod, wire holes.
- **Stage C — outputs:** STEP of the wing, DXF of all laser parts nested on 300 × 100 mm sheets by thickness, STL of the printed parts, mass table (volume × density + film + glue), iso, top and section pictures (section through the servo bay, y = 140).

## 7. Decision points ahead

| Point | Tier |
|---|---|
| Final chord after the throw test (0.28 or 0.30 m) | 1 |
| Replacement of the servo placeholder with the user's MG90S CAD | 2 |
| Rib lightening hole sizes, cap strip widths, small fits | 2 |
| Aileron throw and horn length | 2 |
| Wing mass above 145 g (without servos) | 1 — stop and report |

## 8. Key checks

1. Span 990.0 mm (≤ 1000 mm); chord 280.0 mm; dihedral 0°.
2. Airfoil depth at x = 75.6 mm: 39.1 mm (outer surface).
3. Spar caps fit inside the outline: carbon outer face flush with the rib outline under the 1.5 mm sheeting.
4. Aileron: x = 210 to 280, length 325 mm, gap 1 mm at each end.
5. MG90S fits inside the skins in the y = 110 to 165 bay with ≥ 1 mm clearance.
6. All solids `isValid()`. No parts overlap except at glue faces.
7. Wing mass without servos ≤ 145 g (estimate in D-003: 137 g).

## 9. As built — rev A (2026-11-21)

The model is `design/cad/Wing_revA.FCStd` (rebuild: `design/cad/scripts/run_all.py`). These values differ from §1–§8:

| Item | Plan | As built | Decision |
|---|---|---|---|
| Mass limit (key check 7) | 145 g | 160 g without servos (model 156.6 g) | D-013, D-023 |
| Rib at y = ±440 | 3 mm | 2 mm at y = ±439.5 (face at 438.5 keeps the 1 mm aileron gap) | D-013 |
| Lightening holes | aft of the spar | also forward of the spar, ≈ 33 % of the rib area | D-013, D-018 |
| LE | hard balsa | medium balsa | D-013 |
| D-box / centre sheeting | light 100 | selected light sheets ≈ 90 kg/m³ | D-013 |
| Tip | tip rib 3 mm at y = 493.5 + cap | tip rib y 489–492 (2 × 1.5 mm light, no holes) + 3 mm light ring cap y 492–495 (10 mm wide) | D-013, D-014 |
| Continuous parts | 980 mm | 984 mm (y ±492) | D-019 |
| False spar crossing | — | full depth; ribs, cap strips and centre sheeting divide at x 205 / 208 | D-015 |
| Centre sheeting | y ±55, one area | y ±56, 8 pieces, grain chord-wise | D-017 |
| Aileron | ribs at wing stations | + 2 mm end ribs + 2 mm horn rib; TE medium balsa | D-016, D-020 |
| Hinge line | — | x = 209 (gap 2 mm), 4 CA hinges at y = 130, 247.5, 302.5, 420 | D-021 |
| Horn | y ≈ 140, x ≈ 218 | slot-in horn at y = 148.1, hole 16.47 mm below the hinge at x = 209 | D-016, D-022 |
| Hatch | 1.2 mm | 0.8 mm + 2 servo lugs; frame ring 1.0 mm | D-013, D-020 |
| Rub plates | — | 0.5 mm, y ±15 *(interp.)* | D-020 |
| Depth at x = 75.6 (key check 2) | 39.1 mm | 39.20 mm (spline through the .dat points) | — |
