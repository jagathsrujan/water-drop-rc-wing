# Study: 3D-printed instead of laser-cut balsa — wing rev A

Date: 2026-11-22. Status: study only. No change to the CAD, the decisions or the site. Any design change from this study is a tier 1 decision for the user.
Numbers: `design/studies/printed_vs_balsa_calc.py` (run it from the repo root; it reads `design/cad/mass_table.csv` and `design/aero/airfoil_coords/sd7062.dat`).

## 0. Answer

**Same geometry, printed instead of balsa:** printed is **stronger in almost every local check, but 3 to 6 times heavier**. The wing goes from 156.6 g to **469–691 g in LW-PLA** (foamed, 0.55–0.85 g/cm³), **854 g in ASA, 980 g in PLA, 988 g in PETG-CF and 1002 g in PETG**. That costs **35–59 % of the score** and puts the loaded stall speed at 9.6–10.9 m/s, above the 9.0 m/s requirement (R6). It is also **weaker** in three areas: sun heat (PLA and LW-PLA soften below 60 °C), impact (brittle across the layers, and 3–5× more wing kinetic energy to absorb), and creep.

**Redesigned for printing (a different design):** the lightest credible printed wing is a thin LW-PLA or ASA-Aero D-box shell with geodetic stiffeners and balsa aft (R1a), at **≈ 191 g (+35 g, −5.6 % score)**. A fully printed shell wing (R2) is **≈ 248 g (186–327 g), −14 % (−5 to −23 %)**. At these masses, the printed skins are **as weak as or weaker than** the balsa D-box in denting and shear buckling, and more brittle.

**Recommendation:** keep the balsa rev A structure. Keep printing only the hard points (as now). Use the printers for zero-mass building jigs. Details in §6.

---

## 1. Basis

- Geometry: rev A as built. Part volumes from `design/cad/mass_table.csv` (835.6 cm³ of balsa in 95.7 g). Kept in every variant: carbon caps 9.2 g, PETG parts 11.2 g, pushrods 1.3 g, film 29.2 g, glue 8.0 g, screws and hinges 2.0 g (60.9 g in total).
- Score: score = water / empty mass. Baseline empty mass **580 g** (task brief and `docs/REPORT.md` §2). D-003 used 440 g + wing ≈ 597 g; that basis moves the score changes below by less than 1 point. Score change is the exact ratio 580 / (580 + Δm) − 1. The "10 g ≈ 1.7 %" rule is linear and only valid for small changes; at +800 g it gives −140 %, which is not possible.
- Loads (D-004, REPORT §5.1): load factor 6, root moment 8.9 N·m, cap separation 33 mm, cap force 270 N, half-wing lift 42 N.
- Printers: Bambu Lab P1S, build volume 256 × 256 × 256 mm *(interp.: Bambu spec)*; H2D, 350 × 320 × 325 mm single nozzle *(interp.: Bambu spec; about 300 mm X with both nozzles)*. 0.4 mm nozzle.

## 2. Material data

### 2.1 Printed materials (data-sheet values, specimens printed 100 % infill)

| Material | ρ g/cm³ | E X-Y / Z (MPa) | Tensile X-Y / Z (MPa) | Bending Z (MPa) | Charpy unnotched X-Y / Z (kJ/m²) | HDT 0.45 MPa | Source |
|---|---|---|---|---|---|---|---|
| PLA (Bambu PLA Basic) | 1.24 | 2680 / 2160 | 39 / 35 | 68 | 26.6 / 13.8 (notched X-Y 7.9) | 57 °C (Tg 60) | Bambu PLA Basic TDS V2.0 |
| PETG (Bambu PETG HF) | 1.27 | 1810 / 1540 | 34 / 23 | — | not read | 69 °C | Bambu PETG HF TDS V1.0, read through a third-party copy *(interp.: official PDF not read)* |
| ASA (generic) | 1.05–1.07 | ≈ 2200 / 1500 | ≈ 37 / 24 | ≈ 40 | not read | ≈ 90–100 °C | *(interp.: typical ASA filament TDS; Bambu ASA sheet not read)* |
| PETG-CF (Bambu) | 1.25 | 2460 / 1340 | 59 / 38 | 62 | 41.2 / 10.7 (notched X-Y 15.7) | 74 °C | Bambu PETG-CF TDS V2.0 |
| PLA Aero (Bambu), low-foam specimen at 210 °C | 1.21 filament | 1350 / 1240 | 24 / 18 | **17** | 28.8 / **3.1** | **53 °C** (Tg 55) | Bambu PLA Aero TDS V4.0 |
| LW-PLA (colorFabb) unfoamed / **foamed 250 °C, 45 % flow** | 1.2 / ≈ 0.54 | 3350 / **860** (X-Y) | 43 / **10** (X-Y) | — | notched **3.7** (foamed) | HDT-B 60 °C (unfoamed) | colorFabb LW-PLA TDS v1.0 (2023-11-28); 0.54 = 0.45 × 1.2 *(interp.)* |
| LW-PLA-HT (colorFabb) foamed 230 °C, 60 % | ≈ 0.7 *(interp.: 0.6 × 1.2)* | 1050 | 9 | — | notched **< 1** | 72 °C printed unfoamed | colorFabb LW-PLA-HT TDS v1.0 |
| ASA Aero (Bambu), specimen at 225 °C | 0.99 | 2010 / 1180 | 32 / 21 | 24 | 32.0 / **3.4** | **85 °C** | Bambu ASA Aero TDS V1.0 |

Foamed-density scaling *(interp.)*: a power law through the two colorFabb LW-PLA points gives E ∝ ρ^1.70 and strength ∝ ρ^1.83. Values used:

| Foamed grade | E (MPa) | Tensile X-Y (MPa) | Bending Z (MPa) *(interp.: 0.4 × X-Y bending, ratio from PLA Aero and ASA Aero TDS)* |
|---|---|---|---|
| LW-PLA 0.44 g/cm³ | ≈ 610 | ≈ 7 | ≈ 5 |
| LW-PLA 0.55 g/cm³ | 890 | 10.3 | 7.9 |
| LW-PLA 0.70 g/cm³ | 1340 | 16.1 | 12.2 |
| LW-PLA 0.85 g/cm³ | 1860 | 22.9 | 17.4 |
| ASA Aero 0.70 g/cm³ (same law from its TDS point) | 1110 | 17.0 | 12.9 |

Printed density of foamed grades: 0.55–1.05 g/cm³ (Bambu PLA Aero store page; 0.54 at 240 °C). This study uses 0.55 / 0.70 / 0.85 for solid parts, and 0.44–0.71 for single-wall shells (0.20–0.32 kg/m² at 0.45 mm) *(interp.)*.

### 2.2 Balsa (along the grain L, across the grain T)

| Grade | ρ kg/m³ | E_L (MPa) | E_T (MPa) | Compression ∥ (MPa) | Across-grain bending (MPa) | Source |
|---|---|---|---|---|---|---|
| Selected light (D-box) | 90 | 1700 | 26 | 5.5 | ≈ 1.0 | scaled linearly with ρ *(interp.)* |
| Medium | 130 | 2500 | 38 | 8.0 | 1.5 | *(interp.)* between the two sources below |
| Hard | 160 | 3400 | 51 | 9.8 | — | Wood Handbook (secondhand quote: E 3.4 GPa, compression ∥ 14.9 MPa) |

Sources: medium class 120–180 kg/m³: E 2037 MPa, MOR 16.6 MPa, compression ∥ 9.2 MPa, shear ∥ 1.9 MPa (peer-reviewed PNG balsa study, doi 10.1007/s00107-015-0983-0). Ratios E_T/E_L = 0.015, G_LT/E_L = 0.037, G_LR/E_L = 0.054 (Wood Handbook ch. 5; G = 0.045 E_L used). Across-grain bending and compression ⊥ (7 % of ∥) are *(interp.)*. Moduli and strengths rise about linearly with density (Borrega & Gibson 2015).

### 2.3 Specific properties

| Material | E/ρ (MJ/kg) | Strength/ρ (kJ/kg) | Skin bending efficiency E^⅓/ρ |
|---|---|---|---|
| Balsa 90–160, along grain | **19–21** | **61** (compression) | **94–133** |
| Balsa, across grain | 0.3 | ≈ 5–11 | 23–33 |
| PLA | 2.2 (Z 1.7) | 31 (Z 28) | 11 |
| PETG HF | 1.4 (Z 1.2) | 27 (Z 18) | 10 |
| ASA | 2.1 (Z 1.4) | 35 (Z 22) | 12 |
| PETG-CF | 2.0 (Z 1.1) | 47 (Z 30) | 11 |
| LW-PLA 0.55–0.85 | 1.6–2.2 | 19–27 | 14–17 |
| ASA Aero 0.70 | 1.6 | 24 | 15 |

Along the grain, balsa has about 10× the specific stiffness and 1.3–3× the specific strength of any print, and 6–12× the skin-bending efficiency. Across the grain, balsa is the weaker one (about 0.15× the specific stiffness of PLA). Rev A puts the grain along every main load path, and carbon carries the bending. That is why balsa wins on mass.

## 3. Mass

### 3.1 Same geometry (direct substitution)

Print rules: 0.4 mm nozzle, 0.45–0.5 mm lines. 1.5 mm skins = 3 perimeters; 2 mm ribs = 4 perimeters (both print solid, fill 1.0). 3 mm parts (rib 110, false spar, tip rib, tip cap, aileron LE) = 2 + 2 walls + 15 % infill → fill 0.66. LE 6 × 17 strip = 2 walls + 15 % → 0.50. TE wedges → 0.85. Printed volume 741 cm³ (balsa 836 cm³).

| Group | Balsa g | Printed cm³ | PLA | PETG | ASA | PETG-CF | LW-PLA 0.55 | LW-PLA 0.70 | LW-PLA 0.85 |
|---|---|---|---|---|---|---|---|---|---|
| Ribs (incl. tip ribs) | 22.7 | 161.6 | 200 | 205 | 173 | 202 | 89 | 113 | 137 |
| D-box skins | 20.2 | 225.0 | 279 | 286 | 241 | 281 | 124 | 158 | 191 |
| Shear webs | 8.9 | 68.2 | 85 | 87 | 73 | 85 | 38 | 48 | 58 |
| Ailerons | 8.7 | 54.9 | 68 | 70 | 59 | 69 | 30 | 38 | 47 |
| LE | 8.5 | 32.7 | 41 | 41 | 35 | 41 | 18 | 23 | 28 |
| False spar | 6.2 | 31.6 | 39 | 40 | 34 | 40 | 17 | 22 | 27 |
| Spar caps, balsa part | 5.7 | 35.4 | 44 | 45 | 38 | 44 | 19 | 25 | 30 |
| Centre sheeting | 5.2 | 58.0 | 72 | 74 | 62 | 72 | 32 | 41 | 49 |
| Cap strips | 4.2 | 41.3 | 51 | 52 | 44 | 52 | 23 | 29 | 35 |
| Tip caps | 2.8 | 18.4 | 23 | 23 | 20 | 23 | 10 | 13 | 16 |
| TE wedges | 2.7 | 14.1 | 18 | 18 | 15 | 18 | 8 | 10 | 12 |
| Kept parts (carbon, PETG, film, glue, hardware) | 60.9 | | 60.9 | 60.9 | 60.9 | 60.9 | 60.9 | 60.9 | 60.9 |
| **Wing without servos** | **156.6** | | **980** | **1002** | **854** | **988** | **469** | **580** | **691** |
| Factor on rev A | 1.0 | | 6.3 | 6.4 | 5.5 | 6.3 | 3.0 | 3.7 | 4.4 |
| Score change | — | | −58.7 % | −59.3 % | −54.6 % | −58.9 % | −35.0 % | −42.2 % | −48.0 % |
| Loaded stall speed (R6 ≤ 9.0 m/s; rev A 8.8) | 8.8 | | 10.9 | 10.9 | 10.6 | 10.9 | 9.6 | 9.9 | 10.2 |

ASA Aero at 0.70 g/cm³ gives the same mass as LW-PLA 0.70 (580 g). The printed skins do not need film: that saves 10.5 g (0.210 m² of sheeted area) in every column, which does not change the result.

**Can the carbon caps go?** In PLA, PETG and PETG-CF, a 3 × 6 printed cap alone carries 270 N at 15 MPa (margin 2.3–3.9). But the tip deflection at n = 6 grows from 2.6 mm to 24–36 mm, and the sustained heat case (§4.6) is worse. In LW-PLA the margin is 1.1, and the hard balsa cap alone has 0.7. The carbon stays in every variant (9.2 g).

### 3.2 Redesigned for printing (different design, not rev A)

| Variant | Description | Wing g | Δ g | Score |
|---|---|---|---|---|
| R1a low / **mid** / high | Printed D-box shell (LE + skins + front web, x 0–78.6), 0.45 mm single wall LW-PLA or ASA Aero at 0.44 / 0.58 / 0.71 g/cm³ (0.20 / 0.26 / 0.32 kg/m²), geodetic stiffeners at ≈ 25 mm (×1.35–1.6), 3 span segments. Balsa ribs aft, rest of rev A unchanged, no film on the D-box. | 166 / **191** / 221 | +10 / **+35** / +64 | −1.7 / **−5.6** / −10.0 % |
| R1b low / mid / high | Same shell, 0.8 mm (2 walls), diaphragms at 55 mm | 193 / 221 / 246 | +37 / +64 / +90 | −5.9 / −10.0 / −13.4 % |
| R2 low / **mid** / high | Fully printed shell wing (all skins 0.585 m², internal geodetic ×1.35–1.6), carbon caps, PETG hard points, no film | 186 / **248** / 327 | +29 / **+92** / +171 | −4.8 / **−13.6** / −22.7 % |
| H1 | Printed ribs only, balsa sheeting: same rib outline / redesigned 1.6 mm truss rib 55 % open (LW-PLA 0.70) | 261 / 202 | +105 / +46 | −15 / −7.4 % |
| H1 PETG | Same, in PETG | 365 / 258 | +209 / +102 | −27 / −15 % |

R1a low fails the shear-buckling check (§4.2); the lowest credible R1a is "mid". R2 low (186 g) is near the D-003 estimate (176 g), but it needs the same 0.44 g/cm³ single-wall skin as R1a low, so this study does not take it as credible. The truss rib needs 1.6 mm struts, not 1.2 mm (§4.4).

Removed from rev A for R1: LE 8.5 g, D-box skins 20.2 g, front web 6.6 g, rib noses (36 % of the rib area, 8.2 g), film on the D-box 8.4 g = 52.0 g.

### 3.3 Printability

| Item | Check |
|---|---|
| Span-wise parts, 984 mm | Do not fit. H2D: 3 segments (y −492…−165, −165…165, 165…492 = 327 / 330 / 327 mm) on the 350 mm axis. P1S: 5 segments (217 / 220 / 110 / 220 / 217 mm) to keep joints at rib stations. Joints need a carbon spar that runs through all segments. |
| Ribs | Longest rib piece (x 6–205) is 199 × 36.8 mm (DXF read-back): fits both printers. A one-piece rib x 6–255 (249 mm) fits the H2D, and fits the P1S only on the diagonal. |
| 1.5 mm skins | 3 perimeters at 0.5 mm (Arachne): good with a 0.4 mm nozzle. A flat-printed skin cannot be bent round the nose (bending strain t/2R = 1.5/(2 × 5) = 15 % at the LE, nose radius ≈ 5 mm *(interp.)*; PLA breaks at 12 %, PLA Aero at 2.6 %). Print the LE and both skins as one curved C-shell per segment, LE up, chord vertical (≈ 80 mm tall), no supports. Then span-wise bending is in the layer plane, but chord-wise skin bending (denting) crosses the layers: the weak direction. |
| 2 mm ribs, webs, cap strips | Print flat, 4 / 3 perimeters, in-plane loads in X-Y. Cap strips become T-flanges on the ribs in a print design. |
| Thick parts | LE strip and TE wedges with 2 walls + 15 % infill (fill 0.50 / 0.85). |
| LW-PLA / PLA Aero | 100 % flow first layer at 200 °C, then foam at ≈ 230–250 °C with 45–65 % flow (colorFabb TDS). Foamed lines vary in width: plan ±0.2–0.3 mm on slots *(interp.)*. Dry the filament (55 °C, 8 h). |
| ASA / ASA Aero | Chamber 45–60 °C, bed 80–90 °C (Bambu ASA Aero TDS): use the H2D (heated chamber *(interp.)*); the P1S is enclosed but not heated. Fumes: ventilate. |
| PETG-CF | Abrasive: hardened nozzle *(interp.: H2D has hardened nozzles; the P1S stock nozzle must be changed)*. |
| Print time | Direct substitution ≈ 0.5–1.0 kg of thin-walled parts: ≈ 40–70 h *(interp.)*. Laser cutting of the rev A balsa: ≈ 2–3 h *(interp.)*. |

## 4. Strength

### 4.1 Spar bending, n = 6 (root moment 8.9 N·m)

| | Carbon stress (margin to ≈ 400 MPa *(interp.)*) | Cap stress (margin to strength) | Tip deflection at n = 6 |
|---|---|---|---|
| Rev A (hard balsa + carbon) | 78 MPa (margin 5.1) | 2.0 MPa (4.9) | 2.6 mm |
| PLA cap + carbon | 80 MPa (5.0) | 1.6 MPa (24) | 2.7 mm |
| PETG cap + carbon | 83 MPa (4.8) | 1.2 MPa (28) | 2.8 mm |
| LW-PLA 0.70 cap + carbon | 85 MPa (4.7) | 0.9 MPa (18) | 2.8 mm |

**Same.** Carbon carries 85 % of the cap stiffness, so the printed cap changes the margin by less than 10 %. Shear webs (42 N over 1.5 × 39.1 mm = 0.72 MPa): balsa margin 2.7 (shear ∥ 1.9 MPa); PLA 33; LW-PLA 0.70 13 (in-plane shear ≈ 0.6 × tensile *(interp.)*). **Printed is stronger** in the webs.

The flight root moment does not grow with a heavy wing: the wing mass relieves it (PLA direct 7.6 N·m against 8.5 N·m for rev A, same model). **But a hard landing loads the spar with the wing's own mass.** At 10 g on touchdown *(interp.)*: rev A 2.2 N·m (25 % of the design moment), LW-PLA direct 7.4 N·m (83 %), PLA direct 12.2 N·m (137 %; carbon stress then ≈ 108 MPa, margin ≈ 3.7, so the spar does not fail, but the printed parts and joints see 1.4× the design load), R2 mid 3.3 N·m (38 %).

### 4.2 D-box torsion

Design torque 4.0 N·m *(interp.: Cm −0.08 plus a 15° aileron at 25 m/s = 1.6 N·m, plus the n = 6 lift 40 mm forward of the shear centre = 1.7 N·m, rounded up)*. D-box enclosed area 2254 mm², skin arc 159 mm, web 39.1 mm (from the SD7062 coordinates). Shear buckling uses a flat panel plus a curvature term 0.1 E t/R with R = 167 mm *(interp.)*.

| | GJ (N·m²) | vs rev A | Shear stress | Margin (strength) | Margin (shear buckling) |
|---|---|---|---|---|---|
| Rev A balsa 1.5 mm | 12.6 | 1.0 | 0.59 MPa | 3.2 | 2.2 |
| PLA 1.5 | 153 | 12× | 0.59 | 35 | 28 |
| PETG 1.5 | 103 | 8.2× | 0.59 | 23 | 19 |
| ASA 1.5 | 125 | 10× | 0.59 | 24 | 23 |
| LW-PLA 0.70, 1.5 | 76 | 6.1× | 0.59 | 12 | 14 |
| R1a low, 0.45 @ 0.44, panels 25 mm | 10.4 | 0.8× | 1.97 | 1.6 | **0.6 (fails)** |
| R1a mid, 0.45 @ 0.58, panels 25 mm | 16.6 | 1.3× | 1.97 | 2.6 | **1.0** |
| R1b mid, 0.8 @ 0.58, diaphragms 55 mm | 29.5 | 2.3× | 1.11 | 4.6 | 1.7 |

**Same geometry: printed is much stronger and 6–12× stiffer.** Redesign: about the same stiffness as rev A, and a lower shear-buckling margin.

### 4.3 Skin buckling at n = 6 and denting from hand loads

Top D-box skin in compression at the spar strain (≈ 600 µε), panel 53 × 75 mm between ribs, curvature R = 167 mm:

| | Applied | Buckling stress | Margin |
|---|---|---|---|
| Rev A balsa 1.5 (orthotropic, E_L 1700, E_T 26) | 1.02 MPa | 1.56 MPa | 1.5 |
| PLA / PETG / LW-PLA 1.5 | 0.8–1.6 MPa | 4.4–8.7 MPa | 5.4 |
| R1a 0.45 mm, 25 mm panels | 0.36–0.58 MPa | 1.0–1.6 MPa | 2.8 |
| R1b 0.8 mm, 55 mm diaphragms | 0.36–0.58 MPa | 0.8–1.3 MPa | 2.2 |

Denting (a thumb or a ground strike on the skin) *(interp. method)*: a plate cracks under a point load at a load ∝ σ × t² in its weakest direction, and dents in proportion to 1 / (E t³). The weakest direction is across the grain for balsa, and across the layers (Z) for a curved shell printed LE up.

| Skin | Crack load vs rev A | Dent stiffness vs rev A |
|---|---|---|
| Rev A balsa 1.5, across grain (≈ 1.0 MPa, E_T 26 MPa) | 1.0 | 1.0 |
| PLA 1.5, curved, Z (68 MPa, 2160 MPa) | 66× | 85× |
| PETG 1.5, Z (48, 1540) | 46× | 60× |
| PETG-CF 1.5, Z (62, 1340) | 60× | 53× |
| LW-PLA 0.70 1.5, Z (12, 1210) | 12× | 47× |
| R1a low / mid, 0.45 mm, Z | **0.5× / 0.8×** | **0.6× / 0.9×** |
| R1b low / mid, 0.8 mm, Z | 1.4× / 2.4× | 3.2× / 5.2× |

The balsa sheet is about 65× stiffer along the grain than across it. A printed shell is nearly the same in both directions (Z/X-Y = 0.4–0.9 in strength). So at the same thickness, printed skins resist denting far better. At the same mass (0.45 mm), they are weaker than balsa.

### 4.4 Ribs

Squeeze of the wing at a rib: 50 N over 20 mm of rib edge *(interp.)*. The balsa rib is loaded across the grain.

| Rib | Stress | Strength | Margin |
|---|---|---|---|
| Rev A balsa 2 mm (compression ⊥ ≈ 0.6 MPa) | 1.25 MPa | 0.6 MPa | **0.4 (local crush)** |
| PLA 2 mm, flat print | 1.25 | 39 | 31 |
| PETG 2 mm | 1.25 | 34 | 27 |
| LW-PLA 0.70, 2 mm | 1.25 | 16 | 13 |
| LW-PLA 0.58 truss rib 1.6 mm | 1.56 | 11 | 7.3; strut buckling 1.9 (1.2 mm struts: 0.8, fails) |

**Printed ribs are 13–30× stronger at the same geometry.** This is the one place where printed clearly helps robustness, but a printed rib that keeps the margin costs +46 g (LW-PLA truss) to +102 g (PETG truss). The cap strips and the sheeting spread a real hand load over more than 20 mm, so the balsa crush is local (a dent), not a broken rib.

### 4.5 Impact and cartwheel

| | Value | Source |
|---|---|---|
| Balsa crush energy along the grain | ≈ 4.5 MJ/m³ ≈ **30 J/g** | *(interp.: plateau ≈ 0.7 × 9.2 MPa to 0.7 strain)* |
| Balsa crush energy across the grain | ≈ 0.3 MJ/m³ ≈ 2.4 J/g | *(interp.)* |
| Bending fracture energy, MOR²/2E | balsa 0.07 MJ/m³ (0.45 J/g); PLA 1.05 (0.85 J/g); PLA Aero Z 0.10 (0.10 J/g) | TDS values, *(interp. method)* |
| Charpy unnotched X-Y / Z | PLA 26.6 / 13.8; PETG-CF 41.2 / 10.7; PLA Aero 28.8 / **3.1**; ASA Aero 32.0 / **3.4** kJ/m² | Bambu TDS |
| Charpy notched, foamed | LW-PLA 3.7; LW-PLA-HT **< 1** kJ/m² | colorFabb TDS |
| Wing kinetic energy at 9 m/s (with servos) | rev A 7.5 J; R1a mid 8.9 J; R2 mid 11.2 J; LW-PLA direct 24.6 J; PLA direct 40.8 J | calc |

**Worse for printed.** A solid PLA or PETG part takes more energy to break than the same balsa part (≈ 15× per volume, ≈ 2× per gram in bending). But the direct-substitution wing brings 3–5.5× the kinetic energy, and the foamed grades are brittle across the layers (Z impact 3.1–3.4 kJ/m², about 1/10 of X-Y). Balsa crushes locally along the grain and absorbs about 30 J/g; prints crack along a layer line. Repair at the venue: balsa takes CA and a patch; cracked foamed prints are hard to repair well *(interp.)*.

### 4.6 Heat and creep (surface 45–60 °C, R12)

| Material | HDT 0.45 MPa | Margin to 60 °C | Thermal stress vs carbon, ΔT 30 K *(interp. CTE)* |
|---|---|---|---|
| Balsa | no softening (stiffness ≈ −10 % at 60 °C *(interp.)*) | — | 0.2 MPa |
| PLA | 57 °C | **−3 °C** | 5.5 MPa (14 % of tensile) |
| LW-PLA / PLA Aero | 53 °C | **−7 °C** | 2.8 MPa (17 %) |
| PETG HF | 69 °C | +9 °C | 3.3 MPa (10 %) |
| PETG-CF | 74 °C | +14 °C | 3.0 MPa (5 %) |
| ASA Aero | 85 °C | +25 °C | 2.3 MPa (14 %) |
| ASA | ≈ 95 °C *(interp.)* | ≈ +35 °C | 5.9 MPa (16 %) |

**Worse for printed.** PLA and LW-PLA fail: near their HDT, the modulus falls quickly and the skin creeps under the band load and the film shrink. PETG passes with a small margin. ASA and ASA Aero pass. The printed skin also expands about 15–20× more than the carbon spar it is bonded to, which adds a steady 2–6 MPa in the sun. For balsa, the heat risk is film sag, not the structure (D-003).

### 4.7 Layer adhesion (weak direction)

Z / X-Y tensile strength: PLA Basic 0.90, PETG HF 0.68, PETG-CF 0.64, PLA Aero 0.75, ASA Aero 0.66. Z / X-Y bending strength for the foamed grades: 0.38–0.41. Z / X-Y impact for the foamed grades: 0.11. For comparison, balsa across / along the grain is about 0.02–0.1. **The print is much more isotropic than balsa.** But in a printed wing, the weak direction always falls on a real load: chord-wise skin bending (denting, LE-up print) or span-wise bending (span-up print). The foamed grades are weakest exactly where impact and denting load them.

## 5. Verdict

### 5.1 Same geometry (direct substitution)

| Item | Rev A balsa | PLA | PETG | ASA | LW-PLA 0.55–0.85 | ASA Aero 0.70 |
|---|---|---|---|---|---|---|
| Wing mass, g | 156.6 | 980 | 1002 | 854 | 469–691 | 580 |
| Score change | — | −59 % | −59 % | −55 % | −35 to −48 % | −42 % |
| Loaded stall, m/s (≤ 9.0) | 8.8 | 10.9 ✗ | 10.9 ✗ | 10.6 ✗ | 9.6–10.2 ✗ | 9.9 ✗ |
| Spar bending, n = 6 | margin 5.1 | same (5.0) | same (4.8) | same | same (4.7) | same |
| Shear webs | margin 2.7 | better (33) | better (27) | better | better (13) | better |
| D-box torsion stiffness | 1.0 | better 12× | better 8× | better 10× | better 6× | better ≈ 5× |
| Skin buckling, n = 6 | margin 1.5 | better (5.4) | better (5.4) | better | better (5.4) | better |
| Skin denting (crack load) | 1.0 | better 66× | better 46× | better ≈ 40× | better ≈ 12× | better ≈ 12× |
| Rib squeeze | margin 0.4 | better (31) | better (27) | better | better (13) | better |
| Impact / cartwheel | crushes, ≈ 30 J/g | worse: 5.4× wing energy | worse: 5.5× energy, ductile | worse: 4.7× energy | worse: 3–4× energy, brittle in Z | worse: 3.3× energy, brittle in Z |
| Hard-landing spar load (wing inertia) | 25 % of design | worse 137 % | worse 140 % | worse ≈ 120 % | worse 70–100 % | worse 83 % |
| Heat (HDT − 60 °C) | no softening | worse (−3 °C) ✗ | worse (+9 °C) | same (+35 °C) | worse (−7 °C) ✗ | same (+25 °C) |
| Creep under band load *(interp.: judged from HDT margin)* | low | worse | worse (small) | same | worse | same |
| Repair at the venue *(interp.: judgement)* | easy | medium | medium | medium | hard | hard |

### 5.2 Redesigned for printing (different designs)

| Item | Rev A | R1a mid (printed D-box, 0.45 mm) | R1b mid (printed D-box, 0.8 mm) | R2 mid (fully printed) |
|---|---|---|---|---|
| Wing mass, g | 156.6 | 191 | 221 | 248 (186–327) |
| Score change | — | −5.6 % | −10.0 % | −13.6 % (−5 to −23 %) |
| D-box torsion stiffness | 1.0 | same (1.3×) | better (2.3×) | ≈ same *(interp.)* |
| Torsion shear buckling | margin 2.2 | worse (1.0) | worse (1.7) | ≈ R1a |
| Skin buckling, n = 6 | margin 1.5 | better (2.8) | better (2.2) | ≈ R1a |
| Skin denting (crack load) | 1.0 | about the same (0.8×, inside the uncertainty) | better (2.4×) | about the same (≈ 0.8×) |
| Impact | crushes | worse (brittle in Z) | worse | worse |
| Heat | ok | LW-PLA ✗ / ASA Aero ok | same | same |

## 6. Recommendation

1. **Keep the balsa rev A structure (no change).** At the same geometry, a printed wing is stronger in every local check except heat and impact, but it is 3–6.4× heavier. It costs 35–59 % of the score and fails the stall-speed requirement R6. At the same mass, printed is weaker. The balsa wing wins because rev A puts the grain along every main load and uses carbon for bending.
2. **Do not use a printed D-box or a fully printed wing.** The best printed redesign (R1a mid) costs 35 g (−5.6 %), and its skin is not more robust than balsa (0.8× crack load, shear-buckling margin 1.0, brittle across the layers). If the team still wants to try one, use **ASA Aero** (HDT 85 °C), not LW-PLA or PLA Aero (HDT 53 °C).
3. **Hybrids:**
   - Printed ribs with balsa sheeting: +46 g (LW-PLA truss) to +102 g (PETG truss). Not worth it: the balsa rib crush is local and the cap strips spread the load.
   - Only the hard points printed: this is what rev A already does (11.2 g PETG). Keep it. Optional upgrade, tier 1 for the user: print the band rub plates (top surface, steady band load, in the sun) in ASA instead of PETG. Mass 1.2 → 1.0 g; HDT margin +9 → ≈ +35 °C.
4. **Use the printers for tooling (zero wing mass):** a rib-alignment jig (17 ribs at 55 mm pitch, square to the board), LE and TE cradles, a spar-cap laminating clamp, airfoil sanding blocks, an aileron V-bevel guide and a hinge-slot jig. These make the balsa wing more accurate and stronger at no mass cost. This is not a design change.
5. **Lowest margins of rev A in this estimate** (for information; not a reason for a change): top-skin buckling at n = 6 is margin 1.5, which is sufficient because n = 6 already includes the 1.5 safety factor. The rib crush margin of 0.4 comes from an assumed 50 N load on 20 mm of rib, and gives a local dent, not a broken rib. The D-box skin has its lowest crack load across the grain. Handle the wing at the spar and the ribs. The static sand-bag test in REPORT §12 also checks the skin buckling margin.
6. **Cheapest test if the team wants proof:** print a 100 mm span D-box sample in ASA Aero or LW-PLA at 0.45 mm, and cut the same span of rev A in balsa. Weigh both and press both with a thumb gauge. This replaces the *(interp.)* foam density and stiffness values (D-003 suggested the same test).

## 7. Main uncertainties

- Foamed-grade properties come from a two-point power law through the colorFabb LW-PLA data sheet; Bambu Aero data-sheet specimens are low-foam. Real thin-wall values can differ by ±30 %.
- Balsa values vary ±20 % between sheets (mass table note) and between sources (E 2.0–3.4 GPa at medium density).
- Torque, hand-load and landing-g values are estimates *(interp.)*. They set the absolute margins. The large ratios (mass ×3–6.4, same-geometry strength ×6–66, HDT) come from data sheets and are robust. The near-1 ratios (R1 denting 0.5–0.8×, rev A margins 0.4–1.5) depend on estimated values: balsa across-grain strength (1.0–1.5 MPa), compression across the grain, the foam law and the foamed Z strengths. Treat those rows as "about the same", not as exact.
- The PETG HF and generic ASA values were not read from the official PDFs.

Sources (data sheets read): Bambu PLA Basic TDS V2.0, PLA Aero TDS V4.0, ASA Aero TDS V1.0, PETG-CF TDS V2.0 (cdn.shopify.com, Bambu Lab); colorFabb LW-PLA and LW-PLA-HT TDS v1.0 (2023-11-28). Search summaries: Bambu PETG HF TDS V1.0 (botland.com.pl copy), Bambu PLA Aero store page (printed density 0.55–1.05 g/cm³), balsa: doi 10.1007/s00107-015-0983-0, Wood Handbook GTR-190 ch. 5, Borrega & Gibson (Mech. Mater. 2015).
