# Build kit: rev B balsa water-drop aircraft

Everything a builder needs, and nothing else. Generated from the part data by `tools/build_kit/make_build_kit.py`; do not edit these files by hand (run the script again after a design change).

| File / folder | What it is |
|---|---|
| [`BOM.pdf`](BOM.pdf) | Bill of materials to print and tick: every laser part, strip, print, electronics, hardware. Online with saved ticks: https://jagathsrujan.github.io/water-drop-rc-wing/bom/ |
| [`BUILD_GUIDE.md`](BUILD_GUIDE.md) | The build step by step (same steps as the build game: https://jagathsrujan.github.io/water-drop-rc-wing/build-game/) |
| [`LASER_BRIEF.md`](LASER_BRIEF.md) | For the laser shop: material, thickness, sheet size, layers, kerf, sheet by sheet |
| [`MATERIALS.md`](MATERIALS.md), [`materials.csv`](materials.csv) | How much balsa, ply, lite-ply and strip stock to buy |
| [`PRINT_LIST.md`](PRINT_LIST.md) | Every 3D print with material and quantity |
| `laser/` | 41 DXF sheets (153 parts) + `kerf-test/` coupons |
| `print/jigs/` | 37 PLA jigs, 5 jig-base segments, the locating pin |
| `print/aircraft/`, `print/reservoir/`, `print/wing/` | PETG parts of the aircraft |

## Order of work

1. Buy the materials (`MATERIALS.md`, `BOM.pdf`). Weigh the balsa: light sheets for the light parts.
2. Cut the kerf test, then the sheets (`LASER_BRIEF.md`). Keep each sheet's parts together.
3. Print the jigs and the jig base first, then the PETG parts (`PRINT_LIST.md`).
4. Play the build game once (https://jagathsrujan.github.io/water-drop-rc-wing/build-game/): it shows every part in 3D and catches the usual mistakes.
5. Build with `BUILD_GUIDE.md` on the bench.

Questions about the design: see [`../ASK_AN_AGENT.md`](../ASK_AN_AGENT.md).
