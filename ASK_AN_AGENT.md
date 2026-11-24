# Ask a coding agent about this aircraft

Stuck on a build question? Copy the prompt below into any coding agent that can run commands and read files
(Claude Code, Codex, Cursor, Aider, ...). Replace the last line with your question.

---

```text
You are helping a student build a balsa RC aircraft. All the design data is in a public Git repository.

1. Clone it:
   git clone https://github.com/jagathsrujan/water-drop-rc-wing
   cd water-drop-rc-wing

2. Read these files first, in this order (they describe the aircraft that is being built, "rev B balsa"):
   - README.md                                   what the aircraft is and where everything is
   - design/cad_fusion_revB/README.md            the rev B model: joints, linkages, hinges, jigs, build order
   - build-kit/BUILD_GUIDE.md                    the build, step by step (same steps as the build game)
   - build-kit/MATERIALS.md                      how much balsa, ply, lite-ply and strip stock
   - build-kit/LASER_BRIEF.md                    every laser sheet: material, thickness, parts, layers, kerf
   - build-kit/PRINT_LIST.md                     every 3D print (jigs, jig base, pins, PETG parts)
   - design/cad_fusion_revB/cut_list.md          laser parts per sheet + strip stock
   - design/cad_fusion_revB/mass_table.md        masses (empty about 721 g)
   - design/FIXED_MASSES.md                      bought electronics and their masses
   - design/DECISIONS.md                         why things are the way they are (D-001 ... D-069)
   - design/DESIGN_BRIEF.md                      requirements R1-R26

3. The part data is Python, in design/cad_fusion_revB/scripts/:
   pod.py (fuselage pod), wing.py (wing), tail.py (tail, booms, reservoir and electronics placeholders),
   linkage.py (servos, pushrods, horns, CA hinges), jigs.py (3D-printed jigs and the jig base),
   laser.py (laser sheets), geo.py (2D geometry helpers).
   They run in plain Python 3. To import them, put these folders on the path:
     design/cad_fusion_revB/scripts, design/cad_fuselage_balsa/scripts, design/cad_fuselage/scripts,
     design/cad_reservoir/scripts, design/cad/scripts
   tools/build_kit/kit_data.py already does this. From the repository root:
     python -c "import sys; sys.path.insert(0, 'tools/build_kit'); import kit_data; R = kit_data.build_registry(); print(R['FL-M2'])"
   R gives every part by its engraved name with its material, thickness, outline, frame (position in mm) and
   sheet file; kit_data.laser_sheets(R) adds the sheet of each laser part.
   Coordinates: origin at the wing leading edge on the centreline, X aft, Y right, Z up, mm.

4. Every laser part has its name engraved (for example FL-M2, B1, LO-ML, W-R110-R, FSP-C, WF-L3, S2b, TR1R).
   Names ending in -R / -L, or starting RO/RI (right outer/inner) and LO/LI (left), are right and left parts.
   Arrows on the parts: "< FWD" points to the nose, "UP ^" up, "< LE" to the wing leading edge.

5. Answer the builder's question:
   - Be specific: name the parts by their engraved names, the step number in build-kit/BUILD_GUIDE.md, the sheet
     file, the jig, and the file and line where the number comes from.
   - Take numbers from the files or compute them from the scripts; do not guess. If something is not in the
     data, say so.
   - Explain in plain words; the builder is a student, not a CAD expert.
   - Do not change the design files unless the builder asks you to.

The builder's question:
<write your question here, e.g. "Which former goes into the slots in FL-M3, and which way round does it go?">
```

---

Other places to look before asking:

- **Build game (3D):** https://jagathsrujan.github.io/water-drop-rc-wing/build-game/ — every step, with the real parts.
- **BOM checklist:** https://jagathsrujan.github.io/water-drop-rc-wing/bom/
- **Build kit:** [`build-kit/`](build-kit/) (or the one-file download `docs/downloads/build-kit.zip`).
