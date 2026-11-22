# Wing designs — rev A (balsa built-up) and rev B (foam blocks)

Boeing NAC 2026-27, IIT Madras zone. Status 2026-11-22.
This file is the summary of the two wing designs in this workspace: where each one is, what it is, and how they compare.
Details: rev A plan `design/02_wing_plan.md`; rev B plan `design/cad_revB/REVB_PLAN.md`; comparison `design/studies/revA_vs_revB.md`; decisions `design/DECISIONS.md` (rev A D-001 … D-023, rev B D-024 … D-032).

**Status:** rev A is the reference design (Claude's recommendation: rev A; 156.6 g, R6 passes). Rev B was modelled only for the comparison (D-024); the user did not choose it (247.7 g, R6 and the heat check fail). The user has not made a final A/B choice; the build before selection is limited by time and money (D-024, brief A5).

## 1. Common to both designs

| Item | Value |
|---|---|
| Airfoil | SD7062 (D-001) |
| Span / chord | 990.0 mm (tip faces y = ±495) / 280.0 mm, rectangular (D-002) |
| Wing area / aspect ratio | 0.2772 m² / 3.54 |
| Dihedral, twist | 0°, 0° (D-012, D-005) |
| Frame | Origin at the LE on the centreline; X aft, Y right wing, Z up; chord line at Z = 0 |
| Spar | Carbon 0.5 × 6 mm + hard balsa 3 × 6 mm caps, top and bottom, x 72.6–78.6, 984 mm one piece; 1.5 mm shear webs (D-004) |
| D-box | 1.5 mm light balsa (≈ 90 kg/m³), x 6–80, top and bottom, full span |
| False spar (hinge spar) | 3 mm medium balsa, x 205–208, full span (span-wise grain — see note in §5) |
| Ailerons | Built-up, x 210–280, y 112.5–437.5 (325 mm), hinge x 209, 4 CA hinges each, V-bevel LE, ±20° clear (D-006, D-016, D-020, D-021) |
| Servos | MG90S on its side in the bay y 110–165, PETG frame and 0.8 mm hatch, servo comes out with the hatch (D-010, D-022) |
| Attachment | One-piece wing, rubber bands, PETG band rub plates at the LE and TE (D-008) |
| Covering | Film, 50 g/m² (0.585 m²) |

## 2. Rev A — balsa built-up (reference)

**Files:** `design/cad/` — `Wing_revA.FCStd`, `Wing_revA.step`, `dxf/` (21 laser DXF files on 300 × 100 mm sheets + `nesting.json`), `stl/` (8 PETG parts), `cut_list.md`, `mass_table.md`, `img/`. Rebuild: `design/cad/scripts/run_all.py`. Material cost: `bom/BOM_HavocHobby.md`.

**Construction**
- 17 rib stations at 55 mm pitch: 2 mm medium ribs with ≈ 33 % lightening holes; 3 mm ribs at y ±110 (aileron and servo bay ends); 2 mm rib at ±439.5.
- 6 mm medium balsa LE; hard balsa TE wedges (x 255–280) in the fixed bays.
- Full sheeting at the centre (y ±56, top and bottom) for the rubber bands.
- 1.5 × 6 mm cap strips on the ribs aft of the D-box.
- Tip: rib of 2 × 1.5 mm light balsa at y 489–492 + 3 mm light ring cap y 492–495.

**Characteristics**

| Item | Value |
|---|---|
| Wing mass without / with servos | **156.6 g / 184.0 g** (limit 160 g, D-023) |
| Empty aircraft (440 g + wing) / score | 597 g / **166.9** |
| Loaded stall speed, ρ 1.05 (R6 ≤ 9.0 m/s) | **8.86 m/s** (margin +0.14); Chennai ρ 1.15: 8.46 m/s |
| Pieces | 147 modelled (135 balsa, 2 carbon, 8 PETG, 2 steel) |
| Build time, hands-on *(interp.)* | ≈ 24–33 h |
| Material cost (structure) | ≈ ₹9,130 + Araldite Standard; with servos ≈ ₹10,130 |
| Heat (45–60 °C surface) | Passes (balsa does not soften; film can sag) |
| Robustness | Spar margin ≈ 5 at n = 6; D-box skin buckling margin 1.5; rib crush is a local dent; tip ring cap takes cartwheels |
| Repair at the venue | Easy: balsa, CA, film patch |
| Strong points | Lightest; known methods for the team; all parts laser-cut and accurate (±0.1 mm) |
| Weak points | Many small pieces (64 cap-strip pieces, 17 ribs to set square); film sags between ribs in the sun |

## 3. Rev B — foam blocks (comparison model, not chosen)

**Files:** `design/cad_revB/` — `Wing_revB.FCStd`, `Wing_revB.step`, `stl/` (18 parts: PLA LE/TE, keys, joiners, PETG servo parts), `mass_table.md` (with variants), `lift_revB.txt`, `img/`, `REVB_PLAN.md`, `README.md`. Rebuild: `build_stage1.py`, `build_stageB.py`, `build_stage3.py` in `design/cad_revB/scripts/`. Notebook: `design/logs/wing_revB_log.md`. No laser DXF files.

**Construction**
- 7 XPS 30 kg/m³ foam blocks, hollow (7 mm walls, 44–49 % removed): centre y ±54.5; servo bays y 111.5–164 (with a servo pocket); mid y 275.5–329.5; tips y 440–490.5 (D-025, D-026).
- 14 face plates, 1.5 mm light balsa, which are also the hot-wire templates (stepped outline; holes = cavity templates) (D-030).
- Hollow bays of 54 / 108.5 / 107.5 mm, with 1.5 mm half ribs (x 78.6–205) at y ±220 and ±385 (D-027).
- Printed PLA LE in 5 segments (≤ 275.5 mm, fit the H2D), with 14 locator keys for the plates and 4 joiners; printed PLA TE in the fixed bays (x 250–280) (D-028).
- Bottom centre sheeting kept, top removed (D-031). D-box, spar, false spar, ailerons and servo parts as rev A.

**Characteristics**

| Item | Value |
|---|---|
| Wing mass without / with servos | **247.7 g / 275.1 g** (+91.1 g against rev A) |
| Empty aircraft / score | 688 g / **144.8 (−13.3 %)** |
| Loaded stall speed, ρ 1.05 | **9.11 m/s — fails R6** (−0.11 m/s); Chennai 8.70 m/s |
| Variants (same geometry) | ASA Aero LE/TE 217.3 g, 9.02 m/s (fails); ASA Aero LE + balsa TE 206.5 g, 9.00 m/s, −7.7 % |
| Pieces | 164 modelled; 138 build pieces (97 balsa, 17 foam, 12 printed PLA parts + 26 key halves on the LE, 2 carbon, 8 PETG, 2 steel) |
| Build time, hands-on *(interp.)* | ≈ 22–30 h + 10–14 h unattended printing |
| Material cost change *(interp.)* | ≈ +₹100 to +₹900 against rev A (fewer 2 mm balsa sheets; XPS board, PLA and spray adhesive added) |
| Heat | **PLA LE/TE fail** (HDT 57 °C at a 60 °C surface); XPS passes; ASA Aero would pass |
| Robustness | Better crush and impact resistance in the blocks (43 % of the span, best at the tips); D-box skin buckling margin 1.4 in the long bays; 1.5× the wing energy in a crash |
| Repair at the venue | Harder: foam-safe glue, filler, spare printed LE segments |
| Strong points | Blocks locate on the LE keys (easy alignment); 38 fewer balsa pieces; film fully supported over the blocks |
| Weak points | +91 g; R6 and heat fail; new methods (hot-wire cavities, film on foam with spray adhesive, large prints); 4 hinges glue into foam (epoxy or foam-safe CA) |

## 4. Side by side

| | Rev A | Rev B |
|---|---|---|
| Mass without servos | **156.6 g** | 247.7 g |
| Score | **166.9** | 144.8 |
| Loaded stall, ρ 1.05 | **8.86 m/s ✓** | 9.11 m/s ✗ |
| Heat (60 °C) | **✓** | ✗ (PLA) |
| Crush / tip impact | local dents | **better in the blocks** |
| Alignment in the build | 17 ribs on the plan | **7 blocks on LE keys** |
| Methods known to the team | **all** | several new |
| Build time *(interp.)* | ≈ 24–33 h | ≈ 22–30 h + printing |
| Repair at the venue | **easy** | harder |
| Simpler for this team | **yes** | no |

Pictures side by side: `design/studies/revA_vs_revB_img/` (iso, iso without the top skin, sections y = 140 / 200 / 300, bay and servo bay).

## 5. Open items
- Final A/B choice and the build before selection (D-024): open.
- Rev A note to correct: D-015 / `design/cad/scripts/wing_params.py` call the false spar "vertical grain"; it must have span-wise grain (a vertical-grain 3 mm spar bows ≈ 20 mm under film tension).
- Weigh the balsa sheets, the film and (for rev B) the XPS, then correct the densities; both mass tables have ±5 g (film, glue) and ±20 % (balsa) uncertainty.
- The fuselage, reservoir and release mechanism are not designed yet; the abstract must explain them.
