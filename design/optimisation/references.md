# References — optimisation and simulation of the rev B water-drop aircraft

Shared by every phase (P1–P7). Each entry says what was taken from it and where. **Estimates** (values not taken
from a source or computed from one) are listed separately at the end and are marked *(estimate)* in the reports.

## Sources

**[R1]** Kretschmann, D.E. *Mechanical Properties of Wood*. Chapter 5 in: Forest Products Laboratory, *Wood
Handbook — Wood as an Engineering Material*, General Technical Report FPL-GTR-190, USDA Forest Service, Madison WI,
2010 (with 2018 errata). Read from https://research.fs.usda.gov/treesearch/37427 (2026-11-26). (The 2021 edition,
FPL-GTR-282, could not be fetched; FPL blocks automated downloads.)

| Used for | Where | Value |
|---|---|---|
| Balsa (*Ochroma pyramidale*), 12 % MC | Table 5-5a (metric), p. 5-18 | SG 0.16; MOR 21,600 kPa; MOE 3,400 MPa; work to max. load 14 kJ/m³; compression ∥ 14,900 kPa; shear ∥ 2,100 kPa |
| Same, inch-pound check | Table 5-5b, p. 5-22 | MOR 3,140 lbf/in²; MOE 0.49 × 10⁶ lbf/in²; compression ∥ 2,160; shear ∥ 300 |
| Elastic ratios, balsa | Table 5-1, p. 5-2 | E_T/E_L 0.015; E_R/E_L 0.046; G_LR/E_L 0.054; G_LT/E_L 0.037; G_RT/E_L 0.005 |
| Elastic ratios, lite-ply and birch-ply proxies | Table 5-1, p. 5-2 | eastern cottonwood E_T/E_L 0.047; yellow birch E_T/E_L 0.050 |
| Poisson's ratios, balsa | Table 5-2, p. 5-3 | ν_LR 0.229; ν_LT 0.488; ν_RT 0.665; ν_TR 0.231; ν_RL 0.018; ν_TL 0.009 |
| Lite-ply proxy: eastern cottonwood (*Populus deltoides*), 12 % MC | Table 5-3a, p. 5-4 | SG 0.40; MOR 59,000 kPa; MOE 9,400 MPa; compression ∥ 33,900; compression ⊥ 2,600; shear ∥ 6,400 kPa |
| Birch-ply proxy: paper birch (*Betula papyrifera*), 12 % MC | Table 5-3a, p. 5-4 | SG 0.55; MOR 85,000 kPa; MOE 11,000 MPa; compression ∥ 39,200; compression ⊥ 4,100; shear ∥ 8,300 kPa |
| Coefficients of variation | Table 5-6, p. 5-26 | MOR 16 %; MOE 22 %; compression ∥ 18 %; compression ⊥ 28 %; shear ∥ 14 %; SG 10 % |
| Properties vs specific gravity | Table 5-11a, p. 5-29 | hardwoods, 12 % MC: compression ⊥ = 21,600 G^2.09 kPa (and the other functions) |
| Linear scaling with SG within a species | text, p. 5-26 | "within a species … linearly … related to specific gravity; … linear analysis is suggested" |
| Strength at an angle to the grain (Hankinson) | Eq. 5-2 and list, p. 5-29 | bending Q/P = 0.04–0.10 (lowest value used for across-grain bending) |

**[R2]** Borrega, M., Gibson, L.J. *Mechanics of balsa (Ochroma pyramidale) wood*. Mechanics of Materials 84 (2015)
75–90, doi:10.1016/j.mechmat.2015.01.014. Abstract only (full text rate-limited): balsa density 60–380 kg/m³; axial
modulus and strength, and bending and torsion properties, increase **linearly** with density; radial compression is
non-linear. Used as support for the linear density scaling of [R1]; no numbers taken.

**[R3]** Easy Composites Ltd. *Technical Datasheet CFP — Carbon Fibre Pultrusions*, version 1.0, revised
20/09/2024. https://media.easycomposites.eu/datasheets/EC-TDS-Carbon-Fibre-Pultrusions.pdf. Lengthways: tensile
strength 400–500 MPa, tensile modulus 28–40 GPa, compressive strength 200–320 MPa, flexural strength 250–400 MPa;
density 1.30–1.50 g/cm³; 0.5 × 3 mm strip listed. "Typical properties", not for specification. The lower bounds are
used. (The modulus is low for a UD carbon pultrusion; it is the published value and is conservative for strength.)

**[R4]** This repository: loads D-064 (pod) and D-004 (wing, n = 6 ultimate, root moment 8.9 N·m) in
`design/DECISIONS.md`; masses and densities in `design/cad_fusion_revB/mass_table.md` and `scripts/mass_summary.py`;
part geometry in `design/cad_fusion_revB/scripts/` and `check/bodies.json`; earlier checks in
`design/cad_fuselage_balsa/strength_estimate.m`.

**[R5]** JustKraft (India), product BWS003, *Balsa wood sheet 5 × 100 × 1000 mm* —
https://justkraft.com/product/balsa-wood-sheet---5x100x1000mm---model-making-bws003 (seen 2026-11-26). Shows that
100 × 1000 mm balsa sheets are sold in India. Thickness range, grade and price not verified.

**[R6]** Roark-type plate and beam formulas, as already used in `strength_estimate.m` (annular plate, centre-loaded
plate, beams). Young, W.C., Budynas, R.G., *Roark's Formulas for Stress and Strain*, 7th ed., McGraw-Hill, 2002.
*(The formulas are standard; the exact case numbers were not re-checked in this phase.)*

## Estimates (not from a source; to be replaced by a measurement or a cited value)

| Value | Used | Where it should come from |
|---|---|---|
| Design balsa density for strength 0.12 g/cm³, for mass 0.14 g/cm³ | P1 | user rule (generic local stock); weigh the sheets bought |
| Lamination glue 40 g/m² dry per interface (range 20–80) | P1 mass | weigh a 100 × 100 test laminate of 2 × 1.5 mm |
| Lite-ply 3 mm = 3 equal poplar veneers; birch 1.0 / 1.5 = 3 veneers, 3 mm = 5 | P1 laminates | the supplier's lay-up (count the veneers) |
| Birch and lite-ply veneer properties from solid-wood proxies (paper birch, eastern cottonwood) | P1 | a ply datasheet (EN 636 / EN 12369-2 values are paywalled) |
| Compression ⊥ of balsa from the hardwood SG function (extrapolated below its data range) | P1 | balsa-specific data ([R2] full text) or a coupon test |
| Nesting efficiency 55 % (laser), 85 % (strips) | P1 sheet count | the P3 re-nesting |
| Spar cap lever arm 29.5 mm (SD7062 thickness at 27 % chord minus skins and caps) | P1 | the wing part data in P6 |
| M3 X-mount screw radius 9.5 mm | P1 | the motor's mount drawing |
