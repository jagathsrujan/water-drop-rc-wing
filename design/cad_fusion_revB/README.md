# Rev B in Fusion — the whole aircraft, remodelled for laser cutting

The balsa rev B aircraft (pod rev B, wing rev A, twin boom, cruciform tail) remodelled from scratch in Autodesk Fusion,
built live in the Fusion window through a local bridge (`tools/fusion_bridge/`). The FreeCAD models stay the reference:
every number comes from their parameter files (`bal_params.py`, `fus_params.py`, `res_params.py`, `wing_params.py`),
nothing is retyped. Status: **model complete, not yet built or weighed; the hex lightening of the pod sides is left out
in this pass.**

![Aircraft in Fusion](img/aircraft_iso.png)

## Result

| | Fusion rev B | FreeCAD reference |
|---|---|---|
| Parts | 279 bodies; 151 laser parts on 41 sheets | — |
| Pod | 165.1 g (no hex lightening, more tabs, tail-servo tray, laser saddles) | 133.1 g |
| Wing (without servos) | 156.7 g | 156.6 g |
| Tail | 78.4 g | 78.1 g |
| Empty aircraft / score | ≈ 721 g / ≈ 138 | 689 g / 144.5 |
| Interference (Fusion analysis, all bodies) | largest 0.01 mm³ (surface contacts only) | — |

The pod is 32 g heavier. The first things to try for that: the hex lightening (≈ 7 g), weighing the sheets and using
light stock for the inner layers (rev B estimate 6–8 g), and lighter saddles.

## Files

| Path | What |
|---|---|
| `export/WaterDrop_revB_fusion.f3d` | Fusion archive (open in Fusion: File → Open → Open from my computer) |
| `export/WaterDrop_revB_fusion.step` | STEP, one component per part, named as on the laser parts |
| `dxf/*.dxf` | Laser sheets: layer **CUT**, **ENGRAVE** (part names, single-stroke), **SHEET** (outline, do not cut) |
| `dxf/nesting.json`, `cut_list.md` | What is on each sheet; strip stock cut to length |
| `mass_table.md` | Mass from the Fusion bodies with the same densities, film and glue rules as the FreeCAD tables |
| `check/` | `bodies.json` (every body: material, volume, mass, box), `interference.json` (Fusion interference analysis) |
| `img/` | Pictures |
| `scripts/` | The model: `geo.py` (2D geometry), `pod.py`, `wing.py`, `tail.py` (part data), `fxlib.py` (Fusion helpers), `build_*.py` (bridge jobs), `laser*.py`, `check_model.py`, `mass_summary.py` |

## How it is built

Every part is its own Fusion component, drawn **flat in its own frame** (sketch on the component's XY plane, extruded
by the stock thickness) and placed by the component transform. So each laser part is a true flat pattern, its
bottom-face loops are the cut file, and its name is engraved 0.2 mm into the top face. Strip stock (keels,
longerons, capstrip, ledges, LE, spar caps, TE wedges, cap strips, D-box and centre sheeting) is modelled in place
and listed in the cut list. Electronics and the reservoir are simple placeholders.

Rebuild (Fusion open, ClaudeBridge running):

```powershell
python tools/fusion_bridge/fx.py design/cad_fusion_revB/scripts/build_all.py
```

Then `check_model.py` (with `DO_INTERFERENCE = True`), `laser_loops.py`, `export_views.py` in Fusion, and
`python laser.py`, `python mass_summary.py` in `scripts/`.

## Manufacturing rules

- **Sheet sizes:** balsa 100 × 300 mm with the grain along 300; every balsa part is ≤ 100 mm across the grain and is
  turned to its grain on the sheet. Ply / lite-ply 300 × 300.
- **Labels:** every laser part carries its name and a direction hint (`< FWD`, `UP ^`, `< LE`). The floor and the
  side panels also carry the name of the former that goes into each group of slots.
- **Slots** are drawn at the nominal stock thickness: set the laser's kerf offset so the tabs are a push fit. In the
  tapered nose and tail cone, the slots are opened by T·tan(angle), because the tabs cross those panels at an angle.

## Joints (stay in flight)

| Where | Joint |
|---|---|
| Formers → floor | 3 tabs per former (2 on B2 halves and the end former) through floor slots |
| Formers → sides | 2–3 tabs per side through both side layers (one in the upper strip, 1–2 in the lower) |
| Bulkhead, end former → aft deck | 2 tabs each up through the deck |
| Sides → floor | finger joint: tabs on the bottom edge of both side layers drop into notches in the floor edge |
| Floor pieces | dovetail keys (3 per joint; 2 at X 115 beside the belly opening) |
| Side laminate | outer 1.5 mm in a lower and an upper strip (joint at Z −40), inner 1.0 mm in pieces ≤ 100 mm wide with vertical grain: every joint is bridged by the other layer |
| Battery tray → nose formers | tabs into notches in the former legs |
| Tail-servo tray → sides | 2 tabs per side through the side laminate (new: replaces the rev B pads) |
| Saddles | 4 layers, each with 2 floor tabs, keel notches and 3 pin holes (2 mm toothpicks) |
| Strap bridges | legs through floor slots |
| Wing ribs → spar caps | notches (as rev A) |
| Wing ribs ↔ false spar | egg-crate: rib slotted from above, false spar from below |
| Shear webs → ribs | end tabs into rib slots: the inboard tab is high, the outboard tab low, so two webs never clash in one rib |
| False spar pieces | dovetail keys at Y ±145 and ±357.5 |
| Stabiliser halves → fin | 2 tabs per half through 4 slots in the fin (right and left tabs alternate) |
| Fin → tail block | 2 root tabs into slots in the PETG plate |
| Elevator joiner | wire laid in slots cut in the elevator halves |

## Changes from the FreeCAD models (proposed; not yet in `DECISIONS.md`)

1. **Pod sides:** split into strips and pieces to fit 100 mm balsa (see joints). No hex lightening in this pass.
2. **Pod:** a 3 mm lite-ply tail-servo tray between the sides replaces the rev B pads; the front-stop ring, the U
   formers and the bulkhead follow rev B. The saddles are laser-cut layers with lightening windows; the two inner
   layers of each stack are 3 mm balsa. The S2 strap bridges move 2 mm forward to clear former B4.
3. **Wing:** ribs are one piece from the LE stock to the TE stock. The false spar has its grain along the span, in
   3 pieces per side with an egg-crate joint at every rib; rev A (D-015) had vertical-grain pieces between the
   ribs. The webs get locking end tabs.
4. **Tail:** the stabiliser is two halves tabbed through the fin (rev A: one 490 mm piece through a split fin, which
   does not fit a 300 mm sheet).

## Not done yet

- Hex lightening of the side laminate (rev B saved about 7 g with it).
- Hatch magnets (4 pairs): their seats are not modelled.
- Hinge slots in the aileron and elevator LE strips are cut by hand (the false spar slots are laser-cut).
- Removable assembly jigs (rev B J1–J5) for this version.
- The wing servo bay, horns and guide clips are simplified. Electronics and the reservoir are envelopes only.
