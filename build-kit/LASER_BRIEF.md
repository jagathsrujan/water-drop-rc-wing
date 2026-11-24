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
| Balsa, LIGHT grade (about 100 kg/m3) | 1.5 mm | 100 x 300 mm | 1 | 3 | 0.015 m2 | 49 % | 1 sheet(s) 100 x 1000 mm (each gives 3 laser sheets of 100 x 300) |
| Balsa, LIGHT grade (about 100 kg/m3) | 3 mm | 100 x 300 mm | 4 | 7 | 0.030 m2 | 25 % | 2 sheet(s) 100 x 1000 mm (each gives 3 laser sheets of 100 x 300) |
| Balsa, MEDIUM grade (about 140 kg/m3) | 1 mm | 100 x 300 mm | 6 | 16 | 0.076 m2 | 42 % | 2 sheet(s) 100 x 1000 mm (each gives 3 laser sheets of 100 x 300) |
| Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 mm | 11 | 46 | 0.178 m2 | 54 % | 4 sheet(s) 100 x 1000 mm (each gives 3 laser sheets of 100 x 300) |
| Balsa, MEDIUM grade (about 140 kg/m3) | 2 mm | 100 x 300 mm | 8 | 31 | 0.064 m2 | 27 % | 3 sheet(s) 100 x 1000 mm (each gives 3 laser sheets of 100 x 300) |
| Balsa, MEDIUM grade (about 140 kg/m3) | 3 mm | 100 x 300 mm | 5 | 14 | 0.047 m2 | 31 % | 2 sheet(s) 100 x 1000 mm (each gives 3 laser sheets of 100 x 300) |
| Lite-ply (poplar ply) | 1.5 mm | 300 x 300 mm | 1 | 1 | 0.005 m2 | 5 % | 1 sheet(s) 300 x 300 mm |
| Lite-ply (poplar ply) | 3 mm | 300 x 300 mm | 2 | 17 | 0.033 m2 | 18 % | 2 sheet(s) 300 x 300 mm |
| Birch plywood (aircraft ply) | 1 mm | 300 x 300 mm | 1 | 3 | 0.007 m2 | 7 % | 1 sheet(s) 300 x 300 mm |
| Birch plywood (aircraft ply) | 1.5 mm | 300 x 300 mm | 1 | 7 | 0.009 m2 | 11 % | 1 sheet(s) 300 x 300 mm |
| Birch plywood (aircraft ply) | 3 mm | 300 x 300 mm | 1 | 8 | 0.009 m2 | 9 % | 1 sheet(s) 300 x 300 mm |

**41 sheets, 153 parts.**

## Every sheet

| # | File | Material | Thickness | Sheet | Parts | Cut length | Engrave length |
|---|---|---|---|---|---|---|---|
| 1 | `balsa-light_1.5mm_sheet01.dxf` | Balsa, LIGHT grade (about 100 kg/m3) | 1.5 mm | 100 x 300 | HN-R, HN-L, HF | 1.08 m | 0.20 m |
| 2 | `balsa-light_3mm_sheet01.dxf` | Balsa, LIGHT grade (about 100 kg/m3) | 3 mm | 100 x 300 | W-TIPCAP-R, W-TIPCAP-L | 1.86 m | 0.07 m |
| 3 | `balsa-light_3mm_sheet02.dxf` | Balsa, LIGHT grade (about 100 kg/m3) | 3 mm | 100 x 300 | ELEV-R, ELEV-L | 2.48 m | 0.07 m |
| 4 | `balsa-light_3mm_sheet03.dxf` | Balsa, LIGHT grade (about 100 kg/m3) | 3 mm | 100 x 300 | RUDDER, W-TIP-R | 1.33 m | 0.12 m |
| 5 | `balsa-light_3mm_sheet04.dxf` | Balsa, LIGHT grade (about 100 kg/m3) | 3 mm | 100 x 300 | W-TIP-L | 0.57 m | 0.06 m |
| 6 | `balsa-medium_1mm_sheet01.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1 mm | 100 x 300 | RI-N1, LI-N1, RI-T1 | 1.24 m | 0.29 m |
| 7 | `balsa-medium_1mm_sheet02.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1 mm | 100 x 300 | LI-T1, RI-M4, LI-M2U, RI-M2U | 1.24 m | 0.31 m |
| 8 | `balsa-medium_1mm_sheet03.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1 mm | 100 x 300 | LI-M4, RI-N2, LI-M3U | 0.99 m | 0.27 m |
| 9 | `balsa-medium_1mm_sheet04.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1 mm | 100 x 300 | LI-N2, RI-M1, RI-M3U | 0.91 m | 0.25 m |
| 10 | `balsa-medium_1mm_sheet05.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1 mm | 100 x 300 | LI-M1, LI-M5 | 0.70 m | 0.15 m |
| 11 | `balsa-medium_1mm_sheet06.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1 mm | 100 x 300 | RI-M5 | 0.33 m | 0.08 m |
| 12 | `balsa-medium_1.5mm_sheet01.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | FL-M2, FL-M3, WR-R2 | 1.60 m | 0.26 m |
| 13 | `balsa-medium_1.5mm_sheet02.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | FL-N2, FL-T1, WR-L2 | 1.11 m | 0.21 m |
| 14 | `balsa-medium_1.5mm_sheet03.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | LO-ML | 0.91 m | 0.13 m |
| 15 | `balsa-medium_1.5mm_sheet04.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | RO-M3L, RO-M1L, RO-TL | 1.24 m | 0.32 m |
| 16 | `balsa-medium_1.5mm_sheet05.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | RO-NL, LO-NL | 0.96 m | 0.23 m |
| 17 | `balsa-medium_1.5mm_sheet06.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | LO-TL, DECK, FL-N1 | 1.02 m | 0.23 m |
| 18 | `balsa-medium_1.5mm_sheet07.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | FL-M1, WR-R3, WR-L3, WF-R2, WF-L2, RO-M3U, RO-TU, LO-TU | 2.12 m | 0.47 m |
| 19 | `balsa-medium_1.5mm_sheet08.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | WF-R3, WF-L3, WF-R4, WF-L4, WF-R5, WF-L5, WF-R6 | 1.31 m | 0.19 m |
| 20 | `balsa-medium_1.5mm_sheet09.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | WF-L6, WF-R7, WF-L7, WF-R8, WF-L8, WR-R1, WR-L1 | 1.30 m | 0.19 m |
| 21 | `balsa-medium_1.5mm_sheet10.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | WF-R1, WF-L1, WF-R9, WF-L9, FL-M4, LO-MU | 1.75 m | 0.27 m |
| 22 | `balsa-medium_1.5mm_sheet11.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 1.5 mm | 100 x 300 | RO-M1U, RO-NU, LO-NU | 1.02 m | 0.26 m |
| 23 | `balsa-medium_2mm_sheet01.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 2 mm | 100 x 300 | W-R165-R, W-R165-L, A112-R, A112-L, A165-R, A165-L | 1.74 m | 0.34 m |
| 24 | `balsa-medium_2mm_sheet02.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 2 mm | 100 x 300 | W-R220-R, W-R220-L, A220-R, A220-L, A275-R, A275-L | 2.11 m | 0.30 m |
| 25 | `balsa-medium_2mm_sheet03.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 2 mm | 100 x 300 | W-R275-R, W-R275-L, A330-R, A330-L, A385-R, A385-L | 2.11 m | 0.30 m |
| 26 | `balsa-medium_2mm_sheet04.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 2 mm | 100 x 300 | W-R330-R, W-R330-L, A437-R, A437-L, AH-R, AH-L | 2.11 m | 0.33 m |
| 27 | `balsa-medium_2mm_sheet05.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 2 mm | 100 x 300 | W-R385-R, W-R385-L | 1.69 m | 0.10 m |
| 28 | `balsa-medium_2mm_sheet06.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 2 mm | 100 x 300 | W-C, W-R055-R | 1.93 m | 0.12 m |
| 29 | `balsa-medium_2mm_sheet07.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 2 mm | 100 x 300 | W-R055-L, W-R440-R | 1.91 m | 0.15 m |
| 30 | `balsa-medium_2mm_sheet08.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 2 mm | 100 x 300 | W-R440-L | 0.94 m | 0.07 m |
| 31 | `balsa-medium_3mm_sheet01.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 3 mm | 100 x 300 | STAB-R | 2.76 m | 0.04 m |
| 32 | `balsa-medium_3mm_sheet02.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 3 mm | 100 x 300 | STAB-L | 2.76 m | 0.03 m |
| 33 | `balsa-medium_3mm_sheet03.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 3 mm | 100 x 300 | FIN, S1b, FSP-C | 2.63 m | 0.09 m |
| 34 | `balsa-medium_3mm_sheet04.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 3 mm | 100 x 300 | S1c, S2b, S2c, W-R110-R | 2.26 m | 0.13 m |
| 35 | `balsa-medium_3mm_sheet05.dxf` | Balsa, MEDIUM grade (about 140 kg/m3) | 3 mm | 100 x 300 | W-R110-L, FSP-R1, FSP-L1, FSP-R2, FSP-L2 | 2.82 m | 0.23 m |
| 36 | `lite-ply_1.5mm_sheet01.dxf` | Lite-ply (poplar ply) | 1.5 mm | 300 x 300 | TRAY | 0.36 m | 0.08 m |
| 37 | `lite-ply_3mm_sheet01.dxf` | Lite-ply (poplar ply) | 3 mm | 300 x 300 | FS, B1, B4, N2, N1, EF, S1a, S1d, S2a, B2-R, B2-L, S1BR, S1BL, S2BR, S2BL | 6.27 m | 0.48 m |
| 38 | `lite-ply_3mm_sheet02.dxf` | Lite-ply (poplar ply) | 3 mm | 300 x 300 | S2d, TST | 0.94 m | 0.07 m |
| 39 | `birch-ply_1mm_sheet01.dxf` | Birch plywood (aircraft ply) | 1 mm | 300 x 300 | LI-M2G, RI-M3G, RI-M2G | 0.70 m | 0.31 m |
| 40 | `birch-ply_1.5mm_sheet01.dxf` | Birch plywood (aircraft ply) | 1.5 mm | 300 x 300 | RO-MP, SK3, SK1, SK2, HORN-E, HORN-R, FLAPSTOP | 1.14 m | 0.31 m |
| 41 | `birch-ply_3mm_sheet01.dxf` | Birch plywood (aircraft ply) | 3 mm | 300 x 300 | BH, FW, TR1R, TR1L, TR2R, TR2L, SD-R, SD-L | 1.95 m | 0.14 m |

Cut and engrave lengths are summed from the DXF files (useful for a quote).
