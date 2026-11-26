# Laser brief: sheet by sheet

Hand this file and the `laser/` folder to the laser shop. Generated from the nesting of the part data (`design/cad_fusion_revB/dxf/nesting.json`) by `tools/build_kit/make_build_kit.py`.

## Rules for every sheet

- **DXF R12, units mm, 1:1.** Do not scale.
- **Layer CUT** (red): cut through. **Layer ENGRAVE** (blue): single-stroke part names and arrows - *score* them at low power as a line, do not fill. **Layer SHEET** (grey): the sheet outline - do NOT cut, it only shows the sheet.
- **Order:** engrave first, then the inner cuts (holes, slots), then the outer outlines, so parts do not move before their holes are cut.
- **Grain:** balsa sheets are 100 x 300 mm with the grain along the 300 mm side. Every balsa part is already turned to its grain on the sheet - do not rotate the parts. Ply and lite-ply: 300 x 300 mm, any direction.
- **Kerf:** slots are drawn at the nominal stock thickness. Measure your sheets with calipers, then cut the kerf test (`laser/kerf-test/kerf_test_<t>mm.dxf`) from the same sheet and pick the slot where the TAB strip is a firm push fit. Set that as the kerf offset (or tell the shop). Balsa varies sheet to sheet: test each thickness.
- **Engraved face up:** the engraving is on the face that stays visible while you build. Lay every sheet the same side up as cut.
- **Power:** balsa burns easily: low power, high speed, air assist on, several light passes rather than one heavy one. Test on scrap first. Ply needs more power; lite-ply in between.

## Material summary

| Material | Thickness | Sheet size | Sheets | Parts | Part area | Use of the sheet | Buy |
|---|---|---|---|---|---|---|---|
| Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 mm | 44 | 198 | 0.536 m2 | 41 % | 15 sheet(s) 100 x 1000 mm (each gives 3 laser sheets of 100 x 300) |
| Birch plywood (aircraft ply) | 1.5 mm | 300 x 300 mm | 1 | 28 | 0.039 m2 | 44 % | 1 sheet(s) 300 x 300 mm |

**45 sheets, 226 parts.**

## Every sheet

| # | File | Material | Thickness | Sheet | Parts | Cut length | Engrave length |
|---|---|---|---|---|---|---|---|
| 1 | `balsa-medium_1.5mm_sheet01.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | STAB-R-1, EF-1 | 3.03 m | 0.07 m |
| 2 | `balsa-medium_1.5mm_sheet02.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | STAB-R-2, EF-3 | 2.95 m | 0.08 m |
| 3 | `balsa-medium_1.5mm_sheet03.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | STAB-L-1, WR-L2, A437-L, AH-R | 3.15 m | 0.18 m |
| 4 | `balsa-medium_1.5mm_sheet04.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | STAB-L-2, WR-R3, AH-L | 2.97 m | 0.14 m |
| 5 | `balsa-medium_1.5mm_sheet05.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | LO-ML | 2.04 m | 0.13 m |
| 6 | `balsa-medium_1.5mm_sheet06.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | FIN-1, FL-M2 | 2.17 m | 0.14 m |
| 7 | `balsa-medium_1.5mm_sheet07.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | FIN-2, FL-M3 | 2.04 m | 0.14 m |
| 8 | `balsa-medium_1.5mm_sheet08.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | W-TIPCAP-R, W-TIPCAP-L | 1.86 m | 0.07 m |
| 9 | `balsa-medium_1.5mm_sheet09.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | RO-M3L, RO-NL, A330-L, A385-R, A385-L | 2.52 m | 0.40 m |
| 10 | `balsa-medium_1.5mm_sheet10.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | LO-NL, FL-N2, B2-R-2a, A275-R, A275-L, A330-R | 2.40 m | 0.40 m |
| 11 | `balsa-medium_1.5mm_sheet11.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | FL-T1, HN-R, TST-1, S1a-2 | 2.78 m | 0.22 m |
| 12 | `balsa-medium_1.5mm_sheet12.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | ELEV-R-1, ELEV-L-1, TRAY-2a | 2.98 m | 0.13 m |
| 13 | `balsa-medium_1.5mm_sheet13.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | ELEV-R-2, ELEV-L-2, WR-L3, B2-L-2b | 2.36 m | 0.15 m |
| 14 | `balsa-medium_1.5mm_sheet14.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | LO-MU, W-C-1, FSP-C-1, A165-R, A165-L | 2.75 m | 0.24 m |
| 15 | `balsa-medium_1.5mm_sheet15.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | W-C-2, W-R055-R, S1b-2 | 2.42 m | 0.13 m |
| 16 | `balsa-medium_1.5mm_sheet16.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | W-R055-L, W-R110-R-1, S1c-2 | 2.24 m | 0.16 m |
| 17 | `balsa-medium_1.5mm_sheet17.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | W-R110-R-2, W-R110-L-1, S1d-2 | 2.06 m | 0.15 m |
| 18 | `balsa-medium_1.5mm_sheet18.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | W-R110-L-2, W-R440-R, S2a-2 | 2.22 m | 0.16 m |
| 19 | `balsa-medium_1.5mm_sheet19.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | W-R440-L, W-TIP-R, S2b-2 | 2.01 m | 0.17 m |
| 20 | `balsa-medium_1.5mm_sheet20.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | W-TIP-L, W-R165-R, S1a-1, A220-R, A220-L | 2.14 m | 0.27 m |
| 21 | `balsa-medium_1.5mm_sheet21.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | BH-2a, HN-L, RO-NU, S2c-2 | 2.93 m | 0.22 m |
| 22 | `balsa-medium_1.5mm_sheet22.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | W-R165-L, W-R220-R, N2-2 | 2.23 m | 0.16 m |
| 23 | `balsa-medium_1.5mm_sheet23.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | W-R220-L, W-R275-R, N2-3 | 2.21 m | 0.12 m |
| 24 | `balsa-medium_1.5mm_sheet24.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | W-R275-L, W-R330-R, RI-N1 | 2.32 m | 0.21 m |
| 25 | `balsa-medium_1.5mm_sheet25.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | W-R330-L, W-R385-R, LI-N1 | 2.27 m | 0.20 m |
| 26 | `balsa-medium_1.5mm_sheet26.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | W-R385-L, RUDDER-1, N1-2, BH-2b | 2.50 m | 0.15 m |
| 27 | `balsa-medium_1.5mm_sheet27.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | RI-T1, LI-T1, N2-1, FSP-L2-1, S1BL-2, S2BR-1, S2BR-2, S2BL-1, S2BL-2 | 2.47 m | 0.33 m |
| 28 | `balsa-medium_1.5mm_sheet28.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | DECK, RI-N2, RO-M1L, HF, RI-M2U | 3.27 m | 0.38 m |
| 29 | `balsa-medium_1.5mm_sheet29.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | LI-N2, FL-M1, FSP-L1-2, WF-R2 | 2.28 m | 0.25 m |
| 30 | `balsa-medium_1.5mm_sheet30.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | B1-1a, B1-3b, RO-TL, FSP-C-2 | 2.06 m | 0.18 m |
| 31 | `balsa-medium_1.5mm_sheet31.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | RI-M4, LI-M4, LO-TL, FSP-R1-1, A437-R | 2.67 m | 0.36 m |
| 32 | `balsa-medium_1.5mm_sheet32.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | B4-1a, B4-3b, N1-1, FSP-R1-2 | 1.86 m | 0.14 m |
| 33 | `balsa-medium_1.5mm_sheet33.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | RI-M1, LI-M1, LI-M3U | 2.15 m | 0.24 m |
| 34 | `balsa-medium_1.5mm_sheet34.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | BH-3a, RUDDER-2, TRAY-1, LI-M2U, RO-TU | 2.75 m | 0.30 m |
| 35 | `balsa-medium_1.5mm_sheet35.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | BH-4b, BH-1a, N1-3, FSP-L1-1, B4-2b | 2.35 m | 0.17 m |
| 36 | `balsa-medium_1.5mm_sheet36.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | LO-NU, FL-N1, B1-1b, RO-M3U, S2d-2, B1-2b, S1BR-1, S1BR-2, S1BL-1 | 2.52 m | 0.44 m |
| 37 | `balsa-medium_1.5mm_sheet37.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | B1-3a, B4-1b, B4-3a, B1-2a, RO-M1U, EF-2 | 2.03 m | 0.25 m |
| 38 | `balsa-medium_1.5mm_sheet38.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | B4-2a, BH-1b, BH-4a, LI-M5, S1b-1, LO-TU | 2.69 m | 0.28 m |
| 39 | `balsa-medium_1.5mm_sheet39.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | RI-M5, FL-M4, BH-3b, B2-R-1, FSP-L2-2, WR-R2, TST-2a, A112-R, A112-L | 2.88 m | 0.43 m |
| 40 | `balsa-medium_1.5mm_sheet40.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | B2-R-3, B2-L-1, B2-L-3, S1c-1, S1d-1, FSP-R2-1, FSP-R2-2, RI-M3U, B2-R-2b | 3.10 m | 0.38 m |
| 41 | `balsa-medium_1.5mm_sheet41.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | S2a-1, S2b-1, S2c-1, S2d-1, WF-L2, WF-R3, WF-L3 | 2.54 m | 0.19 m |
| 42 | `balsa-medium_1.5mm_sheet42.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | WF-R4, WF-L4, WF-R5, WF-L5, WF-R6, WF-L6, WF-R7, B4-2c | 1.45 m | 0.22 m |
| 43 | `balsa-medium_1.5mm_sheet43.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | WF-L7, TRAY-2b, WF-R8, WF-L8, WR-R1, WR-L1, WF-R1, B1-2c | 1.60 m | 0.23 m |
| 44 | `balsa-medium_1.5mm_sheet44.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | WF-L1, WF-R9, WF-L9, WF-R1D, WF-L1D, B2-L-2a, TST-2b | 1.41 m | 0.22 m |
| 45 | `birch-ply_1.5mm_sheet01.dxf` | Birch plywood (aircraft ply) | 1.5 mm | 300 x 300 | FS-1, FS-2, RO-MP, LI-M2G, FW-1, FW-2, SK3, RI-M3G, SK1, SK2, RI-M2G, PAD-S1, PAD-S2, TR1R-1, TR1R-2, TR1L-1, TR1L-2, TR2R-1, TR2R-2, TR2L-1, TR2L-2, FLAPSTOP, SD-R-1, SD-R-2, SD-L-1, SD-L-2, HORN-E, HORN-R | 6.41 m | 1.07 m |

Cut and engrave lengths are summed from the DXF files (useful for a quote).
