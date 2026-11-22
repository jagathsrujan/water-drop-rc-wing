# Balsa wing, rev A — design and build report

**Project:** water-drop RC aircraft for the Boeing National Aeromodelling Competition 2026-27 (IIT Madras zone).
**Part:** main wing, revision A.  **Status:** designed and checked in CAD; not built yet.
**Webpage and video:** https://jagathsrujan.github.io/water-drop-rc-wing/

---

## 1. Summary

The wing is a 990 mm span, 280 mm chord, rectangular, built-up balsa wing with the SD7062 airfoil, 0° dihedral and a high-wing rubber-band mount. A carbon-capped balsa spar carries bending, a 1.5 mm D-box carries torsion, and 325 mm ailerons are driven by MG90S servos mounted on 3D-printed PETG hatches.

The structure was modelled part by part in FreeCAD with re-runnable Python scripts. Every key check passes: span 990.00 mm, no overlapping parts, servo clearance ≥ 1.00 mm, no aileron contact at ±20°. The predicted mass is **156.6 g without servos** (184.0 g with two MG90S).

| Output | Where |
|---|---|
| FreeCAD model, STEP | `design/cad/Wing_revA.FCStd`, `design/cad/Wing_revA.step` |
| Laser DXF (21 sheets, 300 × 100 mm) | `design/cad/dxf/` |
| PETG STL (8 parts) | `design/cad/stl/` |
| Cut list, mass table | `design/cad/cut_list.md`, `design/cad/mass_table.md` |
| Indian BOM | `bom/BOM_India.md`, `bom/BOM_India.csv` |
| Build video (6:35) | `docs/media/wing_build.mp4` |
| Decision record (D-001 … D-023) | `design/DECISIONS.md` |
| Engineering notebooks | `design/logs/` |

## 2. Requirements

| ID | Requirement | Value | Source |
|---|---|---|---|
| R1 | Wingspan | ≤ 1.00 m; designed 0.990 m for build tolerance | Rule |
| R4 | Payload | 1000 mL water (≈ 996 g) | Rule |
| R5 | Launch | Hand launch | Team |
| R6 | Loaded stall speed | ≤ 9.0 m/s at ρ = 1.05 kg/m³ (Bengaluru test site) | Derived |
| R7 | Wind | Controlled flight in 6 m/s mean, 10 m/s gust | Weather study |
| R8 | Robustness | "Light but robust": survives a hard landing, repairable at the venue | Team |
| R9 | Controls | Ailerons only on the wing | Team |
| R12 | Heat | Surfaces in the sun 45–60 °C (Chennai, January) | Weather study |

Score = water mass × 100 / empty mass. The water mass is fixed, so the empty mass is the only variable: at an empty mass of about 580 g, each 10 g of wing costs about 1.7 % of the score.

Design air density: 1.05 kg/m³ (Bengaluru, December afternoon) and 1.15 kg/m³ (Chennai, January). Source: `design/01_weather_design_inputs.md` (11 seasons of METAR and reanalysis data).

## 3. Concept decisions

| Decision | Choice | Main reason | ID |
|---|---|---|---|
| Airfoil | SD7062 (14 %) | CLmax 1.58 with a gentle stall; Cd 0.012–0.013 from CL 0.2 to 0.7; small Cm (−0.08). High-lift sections (E423, S1223) have 4–7× the drag at cruise and after the drop. | D-001 |
| Chord | 280 mm, rectangular | Loaded stall speed 8.8 m/s (Bengaluru) with margin; each 20 mm of chord costs ≈ 8 g. Final value after a throw test. | D-002 |
| Build method | Balsa built-up | Lightest robust option (≈ 137–157 g vs 176 g LW-PLA, 208 g XPS), repairable. | D-003 |
| Wing position, mount | High wing, rubber bands | Simple, breaks free in a crash. | D-007, D-008 |
| Dihedral | 0° | One flat piece: continuous spar and sheeting, no joiner. The high wing and an experienced pilot make the neutral spiral mode acceptable. | D-012 |
| Hard points | PETG prints (not PLA) | Exact servo fit; PLA softens at 55–60 °C. | D-009 |
| Servo | MG90S | Hinge moment ≈ 0.05 N·m at 20 m/s; ×2 margin → 1.0 kg·cm; metal gears survive hard landings. | D-010 |

## 4. Geometry and frame

Origin at the leading edge on the centreline; X aft, Y right, Z up; the chord line is at Z = 0 along the whole span.

| Item | Value |
|---|---|
| Span | 990.0 mm (tip faces at y = ±495) |
| Chord / area / aspect ratio | 280 mm / 0.277 m² / 3.5 |
| Airfoil | SD7062 × 280, B-spline through the published coordinates |
| Depth at the spar (x = 75.6) | 39.20 mm |
| Depth at the hinge line (x = 210) | 15.46 mm |
| Incidence | +3° to the fuselage datum, set by the fuselage saddle (not in the wing) |

## 5. Structure

All ribs and skins follow the airfoil: rib outline = airfoil offset 1.5 mm inward along the normal (room for the sheeting and cap strips).

| Part | Size / material | Position |
|---|---|---|
| Ribs | 2 mm medium balsa (130 kg/m³), laser cut, 6 lightening holes (≈ 33 % of the area) | y = 0, ±55, ±165, ±220, ±275, ±330, ±385, ±439.5 |
| Ribs at the aileron inboard end | 3 mm medium; no holes in the servo-frame area; Ø8 wire hole | y = ±110 |
| Tip ribs | 2 × 1.5 mm light balsa, grain crossed, no holes | y = ±489 … ±492 |
| Tip caps | 3 mm light balsa ring, 10 mm wide | y = ±492 … ±495 |
| Leading edge | 6 mm medium balsa, carved to the nose | x = 0–6 |
| D-box sheeting | 1.5 mm selected light balsa (≈ 90 kg/m³), top and bottom | x = 6–80, full span |
| Centre sheeting | 1.5 mm selected light, 8 pieces, grain chord-wise | y = ±56, x = 80–255 (split at the false spar) |
| Spar caps | 3 × 6 hard balsa + 0.5 × 6 carbon on the outer face, top and bottom | x = 72.6–78.6, one piece 984 mm |
| Shear webs | 1.5 mm medium, vertical grain, between the ribs | front face full span; rear face |y| ≤ 164 |
| False spar | 3 mm medium, vertical grain, full airfoil depth | x = 205–208 |
| Cap strips | 1.5 × 6 light balsa on each open-bay rib | x = 80–205 (and 208–255 in the fixed bays) |
| TE wedges | Hard balsa, 25 mm | x = 255–280, y ≤ ±111.5 and ±438.5 … ±492 |

### 5.1 Spar check (D-004)
Design load factor 6 (limit load 4 × safety factor 1.5) at the loaded mass. Lift per half wing ≈ 42 N acting at 0.212 m from the root → root bending moment ≈ 8.9 N·m. Cap separation ≈ 33 mm → cap force ≈ 270 N → stress in one 0.5 × 6 mm carbon strip ≈ 90 MPa, against ≈ 400 MPa allowable for a thin pultruded strip supported by balsa and webs *(estimate)*. Margin ≈ 4. The rear web near the centre adds shear area where the rubber bands and the fuselage load the wing.

### 5.2 Torsion and ailerons
The closed D-box (LE + 1.5 mm skins + front web) carries the aileron and pitching moments. The ailerons (70 mm chord, 25 %) hinge on the full-depth false spar.

## 6. Ailerons, hinges and servo installation

| Item | Value |
|---|---|
| Aileron | x = 210–280, y = 112.5–437.5 (325 mm); 3 mm V-bevelled LE, 2 mm ribs (ends, stations, horn rib), medium-balsa TE |
| Hinge line | x = 209 (centre of the 2 mm gap), z = 6.98 |
| V-bevel | apex at x = 210, 1.5 mm each side at the skins → ±20° with no contact (smallest gap 0.74 mm) |
| Hinges | 4 CA hinges, 20 mm wide, at y = 130, 247.5, 302.5, 420. Glue area 120 mm² each side → > 100 N per hinge vs ≈ 5 N air load per aileron |
| Servo | MG90S on its side between ribs 110 and 165, shaft outboard, case y = 118–146.5, shaft at x = 138.5 |
| Mount | PETG frame (ring 1.0 mm + glue tabs + 4 bosses) glued to the rib faces; 0.8 mm PETG hatch with two servo lugs; 4 × M2 × 4 screws; servo comes out with the hatch |
| Linkage | arm 12.65 mm, horn 16.47 mm below the hinge line, 1.2 mm steel pushrod 70.5 mm between holes with Z-bends, 4 mm below the skin |
| Throw | ±15° aileron ≈ ±20° servo; ±20° aileron ≈ ±26° servo |

Clearances measured in CAD: servo body ≥ 1.06 mm to the frame, 1.34 mm to the hatch plate, 5.04 mm to the cap strips; servo arm 1.00 mm to the hatch slot at −35°, 0° and +35°. The hatch lugs are a 0.3 mm slip fit to the servo case ends (mount).

## 7. Mass

Volume × density from the CAD solids, plus film (50 g/m² × 0.585 m²) and glue (8 g estimate).

| Group | Mass (g) |
|---|---|
| Ribs (incl. tip ribs, aft pieces) | 22.7 |
| Sheeting (D-box + centre) | 25.5 |
| Spar caps (balsa + carbon) | 14.8 |
| Leading edge | 8.5 |
| Shear webs | 8.9 |
| False spar | 6.2 |
| Cap strips | 4.2 |
| TE wedges, tip caps | 5.4 |
| Ailerons | 8.7 |
| Printed PETG parts | 11.2 |
| Pushrods, screws, hinges | 3.3 |
| Film covering | 29.2 |
| Glue (estimate) | 8.0 |
| **Total without servos** (rows are rounded) | **156.6** |

History: the plan structure projected 172 g (limit 145 g). The user chose the reduction set D-013 (larger lightening holes, lighter grades where loads are low, ring tip caps, lighter printed parts) → 156.4 g, and then set the limit to 160 g (D-023). Uncertainty: film and glue ±5 g, balsa density ±20 % between sheets.

## 8. Verification

| # | Check | Result | Required |
|---|---|---|---|
| 1 | Span | 990.00 mm | ≤ 1000 mm |
| 1 | Chord | 280.01 mm | 280 mm |
| 2 | Depth at x = 75.6 | 39.20 mm | 39.1 mm (plan value 0.1 mm low) |
| 3 | Spar caps under the sheeting | gap ≤ 0.21 mm | flush |
| 4 | Aileron | 325.00 mm, end gaps 1.00 / 1.00 mm, no contact at ±20° | as plan |
| 5 | Servo clearance | ≥ 1.00 mm (body and arm ±35°) | ≥ 1 mm |
| 6 | Solids / overlaps | 151 valid; 0 overlaps > 1 mm³ in 276 neighbour pairs | 0 |
| 7 | Mass | 156.6 g | ≤ 160 g |
| — | DXF | 208 cut loops read back = model profiles within 0.02 mm; FreeCAD importer reads mm, rib 199.0 × 36.8 mm = model | — |
| — | STL | all 8 meshes closed; mesh volume = solid volume | — |

## 9. Manufacturing

**Laser cutting.** 21 DXF sheets (300 × 100 mm, three per 100 × 1000 mm balsa sheet), grouped by thickness and grade. Grain runs along X in every file; vertical-grain parts (webs, false spar pieces, tip-rib layer b) are turned 90° in the nest. Layers: `CUT` (cut), `LABEL` (names, do not cut), `SHEET` (outline). Planned machine: Bambu H2D laser module (work area ≈ 310 × 270 mm). Kerf is not compensated.

**Strip stock.** Spar caps 3 × 6 × 984 (hard); LE 6 × 17 × 984; TE stock 25 × 4.6 (wing 330, ailerons 2 × 325); aileron LE 3 × 15.5 × 325; D-box sheets 78.0 and 74.3 mm developed width × 984; cap strips 1.5 × 6 (32 × 126, 12 × 48 mm). Full list: `design/cad/cut_list.md`.

**Printing.** PETG, thin parts printed solid (frame, 0.8 mm hatch with lugs, horns, rub plates). Frames, hatches and horns come as right/left pairs.

## 10. Build procedure

1. **Weigh and sort the balsa.** Density = mass / volume. Light (< 100 kg/m³): sheeting, cap strips, tip caps. Medium (100–150): ribs, webs, false spar, LE, ailerons. Hard (> 150): spar caps, wing TE.
2. **Spar caps.** Epoxy two 3 × 0.5 mm carbon strips side by side on each 3 × 6 mm balsa strip; cure flat under weights on plastic film.
3. **Ribs.** Pin the bottom spar cap carbon-face-down on the board. Pack the rib noses on a 3.5 mm strip (at x = 6) and the rib tails on a 7.8 mm strip (at x = 205). Glue the ribs square with thin CA.
4. **LE, false spar, TE.** Glue the LE stock, the false spar (vertical-grain pieces, joints on the ribs), the aft rib pieces and the TE wedges. Keep the TE straight.
5. **Top spar cap and webs.** Glue the top cap carbon-face-up; fit the vertical-grain webs between the ribs (front full span, rear |y| ≤ 164).
6. **Top sheeting.** Sand flush; glue the top D-box sheet (wet the outer face for the nose bend), the top centre sheets and the cap strips.
7. **Turn over.** Bottom D-box sheet, bottom centre sheets (Ø10 wire exits at y = ±28), bottom cap strips; epoxy the servo frames; pull the servo leads through the rib holes.
8. **Tips.** Laminate and fit the tip ribs, then the ring tip caps; sand the whole wing.
9. **Ailerons.** Build, V-bevel, cut the hinge slots in the false spar and the aileron LE.
10. **Covering.** Iron the edges first (≈ 110–120 °C or as the film maker says), shrink the bays with a heat gun; ailerons separately; open the slots and hatches.
11. **Controls.** CA hinges (wick thin CA after alignment), epoxy horns, servos on the hatches, Z-bend pushrods, hatches with 4 × M2 × 4.
12. **Final.** Rub plates, centre the servos, set ±15° throw, weigh.

Glues: thin CA for tight joints and hinges; PVA (Fevicol SH) for sheeting and laminates; epoxy for carbon, printed parts and rub plates.

## 11. Bill of materials (India)

See `bom/BOM_India.md` (links, prices as listed in November 2026, what to ask for, where to buy offline). Estimated total of the priced items ≈ ₹15,300, plus glue, screws, board and small tools.

## 12. Known limits and open items

- MG90S is modelled as a placeholder with standard dimensions; measure the real servos (and repeat the clearance check) before printing.
- Hinge gap 2 mm; smallest gap at ±20° is 0.74 mm. A smaller gap would need a thicker aileron LE (tier-1 change).
- Rub-plate width (±15 mm) and wire exits (y = ±28) depend on the fuselage, which is not designed yet.
- No FEA: spar sized by hand calculation (margin ≈ 4 at n = 6); a static sand-bag test of the built wing is recommended.
- DXF files are verified by read-back and import, not yet by a test cut.
- Balsa densities, film and glue masses are estimates: weigh parts and update `design/cad/scripts/wing_params.py`, then run `run_all.py`.

## 13. How to rebuild the model

In FreeCAD 1.1 (Python console):

```python
WING_SCRIPTS = "<path to repo>/design/cad/scripts"
exec(open(WING_SCRIPTS + "/run_all.py").read())
```

This rebuilds all parts, runs the checks, and writes the STEP, DXF, STL, cut list, mass table and pictures. The video is made with `design/video/narration.py` (macOS `say`), `design/video/render_freecad.py` (inside FreeCAD) and `design/video/make_video.py` (PIL + ffmpeg). The webpage and BOM are made with `tools/build_site.py`.
