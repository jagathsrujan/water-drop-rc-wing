# Plan: move to a clean workspace and produce the abstract

Written 2026-11-27. Source of the competition demands: *NAC 2026-27 Zonal Round Problem Statement* (the PDF the user
attached; not committed, `.gitignore` keeps `*.pdf` out).

## 1. Where things stand today

| Item | State | Where |
|---|---|---|
| Newest aircraft (rev B, single 1.5 mm balsa stock, P1/P2 changes applied) | committed, **not on `main`** | branch `claude/optimisation-490645` (10 commits ahead of `main`) |
| Simulations P4–P6 (AVL aero, SolidWorks CFD geometry, SolidWorks FEA, margins) | **uncommitted**, 1.1 GB | `design/simulation/` in the optimisation worktree |
| Mass / score | 702.6 g empty, score 141.8 | `design/cad_fusion_revB/mass_table.md` (optimisation branch) |
| Abstract package (P7) | not started | `design/abstract/` does not exist |
| User's FreeCAD edit | uncommitted, must not be touched | `design/cad_fuselage_balsa/Fuselage_revB_balsa.FCStd` on `main` |
| Repo size | ~380 MB on disk, ~120 commits of history incl. rev A wing, printed pod, foam wing | `C:\Projects\water-drop-rc-wing` |

Junk found: `fluent-*.trn`, `fluent-999999-error.log` (repo root, failed Fluent launch), `__pycache__/`, a 1 GB
SolidWorks results file (`*.CWR`) plus `.BDF/.BD2/.gsz/PerformanceLog.txt/~$*.SLDPRT` solver scratch, two stale
worktrees and three old local branches.

## 2. What the rulebook asks the abstract to contain

From *Abstract Submission to Qualify for Zonals* and the design constraints:

| # | Demand | Hard limit |
|---|---|---|
| A1 | A4, 1.5 line spacing, standard format (template from the IIT Madras site) | **≤ 15 pages** |
| A2 | Zip of photographs **of the aircraft during construction** | **5 to 10 photos** |
| A3 | Basic design: dimensions, wing area, estimated flight speed | — |
| A4 | Reservoir, mounting, release mechanism | — |
| A5 | Leakage prevention | — |
| A6 | Centre-of-gravity management | — |
| A7 | Safe operation | — |
| A8 | Due ≥ 20 days before the zonal, by e-mail | date from the user (Q1 in the brief) |

Compliance the abstract should show (design constraints): span ≤ 1 m (990), prop ≤ 13 in, not metal (10 × 5), T/W ≤
1.5 without payload, electric only, no gyro / programming / FPV, 2.4 GHz, one-channel pilot-commanded release,
sealed removable reservoir counted in empty mass, 30 s minimum flight, 3 min window.

**A2 is the critical path:** the photos must show the real aircraft being built, so cutting and building must start
before the abstract can be finished.

## 3. Sort: keep, condense, drop

### Keep as is (moved into the new layout)
| From (optimisation branch) | To | Note |
|---|---|---|
| `design/cad_fusion_revB/scripts/`, `README.md`, `mass_table.md`, `cut_list.md`, `dxf/`, `jigs/`, `print/`, `check/` | `aircraft/model/` | the single source of truth |
| `design/cad_fusion_revB/img/` | `aircraft/model/img/` | prune to the views the abstract and README use |
| `WaterDrop_revB_fusion.f3d` (59 MB) | `aircraft/model/export/` via **Git LFS** | STEP (110 MB) is regenerated, only the 13 MB zip kept (LFS) |
| FreeCAD script modules that `kit_data.py` / the Fusion scripts import from `cad/`, `cad_fuselage/`, `cad_fuselage_balsa/`, `cad_reservoir/` | `aircraft/lib/` | only the imported `.py` files; find them with an import trace, not by guess |
| `tools/build_kit/`, `tools/fusion_bridge/`, `tools/build_site.py` | `tools/` | fix paths after the move |
| `build-kit/` | `build-kit/` | regenerated, not copied |
| `design/optimisation/` (P1, P2: `.m`, `.md`, `.csv`, `p2_fig/`, `references.md`) | `analysis/optimisation/` | `references.md` becomes the master reference list |
| `design/simulation/aero/` (AVL input/output, CFD geometry, figures, `results.json`) | `analysis/aero/` | |
| `design/simulation/structure/` scripts, case `.json`, `*_result.json`, `*.png`, `margins.md` | `analysis/structure/` | **not** the solver files |
| `design/simulation/P4_tool_choice.md` | `analysis/TOOLS.md` | |
| `design/aero/airfoil_study.*`, `wing_lift_performance.*`, `airfoil_coords/` | `analysis/aero/airfoil/` | airfoil selection evidence for the abstract |
| `design/calc/fuselage_sizing.py`, `wing_sizing.py`, `wing_lift.py`, `reservoir_cad_calc.py` | `analysis/sizing/` | |
| `design/FIXED_MASSES.md`, `bom/BOM_Electronics_Robu.md` | `aircraft/` | |
| `docs/build-game/`, `docs/bom/`, `docs/downloads/` | `docs/` | only if the website stays (decision D3) |

### Condense (rewrite short, originals stay in the archived old repo)
| From | To | How |
|---|---|---|
| `DECISIONS.md` (68 KB, D-001…D-069 + P-gates) | `history/DECISIONS.md` | only decisions that still hold for the flying aircraft, one line each with the reason; superseded ones become one line under "Dropped" |
| `DESIGN_BRIEF.md` | `aircraft/REQUIREMENTS.md` | R1–R26 updated to rev B and the 2026-27 rules; every requirement gets "met / open / value" |
| `01_weather_design_inputs.md`, `02_wing_plan.md`, `03_reservoir_plan.md`, `04_fuselage_plan.md`, `WING_DESIGNS.md`, `logs/*` (10 logs), `studies/*` | `history/DESIGN_HISTORY.md` | one page: rev A wing → foam-block wing (not adopted) → printed pod rev A → balsa rev B → single-stock optimisation; densities, wind, heat inputs kept as a table. This feeds the abstract's "design process" section |
| `OPTIMIZATION_PLAN.md` (P1–P7) | `history/DESIGN_HISTORY.md` | phases done P1–P6, P7 moves to `abstract/` |
| `README.md`, `ASK_AN_AGENT.md` | new `README.md`, `ASK_AN_AGENT.md` | new paths, new numbers |
| `CLAUDE.md` (workspace rules) | new `CLAUDE.md` | same rules + abstract rules (section 5) |

### Drop (left in the archived repo, not carried over)
| What | Size | Why |
|---|---|---|
| `design/cad/` FreeCAD wing rev A model, DXF, STL | 20 MB | superseded by the rev B wing (scripts imported by rev B kept, above) |
| `design/cad_revB/` foam-block wing | 19 MB | studied, not adopted |
| `design/cad_fuselage/` printed pod rev A models and exports | 42 MB | superseded |
| `design/cad_fuselage_balsa/` FreeCAD models, exports, jigs | 43 MB | Fusion model replaced it (keep imported scripts only) |
| `design/cad_reservoir/` FreeCAD models, STL | 3.5 MB | reservoir parts are in the Fusion model |
| `design/video/`, `docs/media/wing_build.mp4` (45 MB), `docs/REPORT.md`, `docs/img/` | 47 MB | rev A wing video and report |
| `design/weather_scripts/` | 12 KB | inputs kept as numbers in the history |
| `design/simulation/p4/` benchmark | 41 MB | result kept as one table in `analysis/TOOLS.md`; `SwFeaBench.cs` kept |
| Solver scratch: `*.CWR`, `*.BDF`, `*.BD2`, `*.gsz`, `*-BenchMark-Solver.txt`, `PerformanceLog.txt`, `~$*`, `*.SLDPRT` in cases | ~1.1 GB | rebuilt by `run_fea.ps1` from the case JSON |
| `fluent-*.trn`, `fluent-*.log`, `__pycache__/` | — | junk |
| `bom/BOM_India.md` (rev A wing BOM) | — | replaced by the generated build-kit BOM |

Result: roughly **60–80 MB** in the new repo (most of it the `.f3d` and STEP zip in LFS) instead of ~1.5 GB.

## 4. New workspace layout

```
C:\Projects\nac26-waterdrop\              (new repo, see D1/D2)
├── CLAUDE.md                     rules: tool routing, pictures, citations, balsa grade, abstract rules
├── README.md                     what it is, key numbers, where things are
├── RULES.md                      the 2026-27 rules as a checklist (no PDF in git)
├── KEY_NUMBERS.md                generated: dimensions, wing area, masses, speeds, T/W, score, CG
├── aircraft/
│   ├── REQUIREMENTS.md           condensed brief, met / open per item
│   ├── FIXED_MASSES.md           bought parts, catalogue → weighed
│   ├── model/                    Fusion part data, DXF, jigs, print, check, img, export (LFS)
│   ├── lib/                      FreeCAD-derived geometry modules the model imports
│   └── BOM_Electronics.md
├── analysis/
│   ├── TOOLS.md                  which tool for what, and why (P4)
│   ├── sizing/                   hand sizing scripts
│   ├── aero/                     airfoil study, AVL, CFD
│   ├── structure/                FEA cases, margins
│   ├── optimisation/             P1 single stock, P2 lightening, references.md
│   └── propulsion/               NEW: thrust, T/W, current, endurance
├── abstract/
│   ├── REQUIREMENTS_MATRIX.md    rulebook demand → section → evidence file
│   ├── OUTLINE.md                sections, page budget
│   ├── sections/01_…md           one file per section
│   ├── fig/  + CAPTIONS.md       every figure used, with its source file
│   ├── tables/                   generated from the data (never typed by hand)
│   ├── photos/  + PHOTO_PLAN.md  5–10 construction photos and the zip
│   ├── references.md             (link to analysis/optimisation/references.md)
│   ├── template/                 the IIT Madras format (user downloads it)
│   ├── make_abstract.py          sections + tables + figs → .docx in the template → PDF
│   └── out/                      Abstract.pdf, Photos.zip (checked: A4, 1.5, ≤ 15 pages)
├── build-kit/                    generated
├── history/                      DESIGN_HISTORY.md, DECISIONS.md
├── tools/                        build_kit, fusion_bridge, make_key_numbers.py, check_abstract.py
└── docs/                         website (optional)
```

New files to write: `CLAUDE.md`, `README.md`, `RULES.md`, `KEY_NUMBERS.md` + `tools/make_key_numbers.py`,
`aircraft/REQUIREMENTS.md`, `history/DESIGN_HISTORY.md`, `history/DECISIONS.md`, everything in `abstract/`,
`analysis/propulsion/`, `tools/check_abstract.py`.

## 5. Migration steps

**M0 — Settle the old repo first** (no data loss)
1. Check no session is still running simulations in the optimisation worktree.
2. Commit the keepable part of `design/simulation/` on `claude/optimisation-490645` (solver files ignored).
3. Ask the user: merge `claude/optimisation-490645` into `main` (P3 gate) — needed so the archive's `main` is the
   newest design.
4. Leave the user's `Fuselage_revB_balsa.FCStd` as it is; ask whether it carries over (it is a FreeCAD file, dropped
   by default).
5. Tag `archive/pre-migration-2026-11-27`, push the tag. Old repo becomes read-only reference.

**M1 — Create the new repo**
1. `git init` at the new path, Git LFS for `*.f3d`, `*.step.zip`, `*.SLDPRT`.
2. Copy the "keep" files into the new layout (script with a manifest, so it can be checked: every copied file listed,
   every dropped file listed with its reason).
3. Fix imports and paths: `kit_data.py` path list → `aircraft/lib`, `aircraft/model/scripts`; Fusion bridge job
   paths; `run_fea.ps1`, AVL and CFD scripts; build-site paths.

**M2 — Prove nothing broke**
1. `python tools/build_kit/make_build_kit.py` → same parts, quantities, sheets as the old repo (diff the BOM CSV).
2. `mass_summary.py` → 702.6 g, CG X 82.4 (same as now).
3. AVL run → same `results.json`.
4. One FEA case rebuilt from its JSON in SolidWorks → same margin.
5. Open the `.f3d` in Fusion and rebuild one part through the bridge.

**M3 — Write the condensed and new documents** (section 3 "Condense", section 4 "New files").

**M4 — Close the gaps the abstract needs** (each is its own task)
| Gap | Why it matters | Task |
|---|---|---|
| T/W without payload not shown | rule: ≤ 1.5 (≤ 1.37 at Bengaluru per R3). D2830 + 10 × 5 on 3S may exceed 1.05 kg static thrust on a 703 g aircraft | thrust from the motor datasheet / a thrust stand; throttle-limit or prop choice if over |
| Loaded stall speed 9.22 m/s at ρ 1.05 (AVL) vs R6 ≤ 9.0 | hand-launch requirement | decide: accept (8.81 at the Chennai venue), or lighten / change CL |
| "Estimated flight speed" | rule A3 | pick the cruise speed from the AVL trim table (L/D ≈ 11 at 14 m/s loaded) with power and endurance |
| Leakage prevention evidence | rule A5 | drain / drop / tilt test plan; seal details from the reservoir design |
| Receiver, wiring not selected | mass and safe operation (failsafe) | select a 2.4 GHz receiver, set failsafe throttle off |
| CFD pictures | P5 plan, CLAUDE.md picture rule | run the SolidWorks Flow Simulation case on the CFD geometry that already exists |
| Real masses | estimates until weighed | weigh parts as they are built, update `FIXED_MASSES.md` and `KEY_NUMBERS.md` |
| Construction photos | rule A2 | follow `PHOTO_PLAN.md` while building |

**M5 — Write the abstract** (≤ 15 pages, page budget in brackets)
1. Title, team, zone (template) [1]
2. Mission and scoring strategy: score = water / empty mass, why minimum mass [1]
3. Rules compliance table [0.5]
4. Configuration and dimensions: 3-view, span, chord, wing area, AR, tail volumes, fuselage length [1.5]
5. Aerodynamics: airfoil choice, AVL lift curve / polar / Cm-α, static margin 12.6 %, stall and estimated flight
   speeds, CFD pictures [2]
6. Propulsion and T/W [0.5]
7. Structure and materials: single balsa stock, lightening, FEA margins [1.5]
8. Water reservoir and mounting [1]
9. Release mechanism (one channel, trap door, drain time) [1]
10. Leakage prevention [0.5]
11. CG management (water on the CG, CG unchanged at release, battery trim) [0.5]
12. Mass budget and predicted score [0.5]
13. Manufacturing: laser kit, jigs, build photos [1.5]
14. Safe operation: pre-flight checklist, safety pin, launch, failsafe, emergency [0.5]
15. References [0.5]

Each number in the text comes from `KEY_NUMBERS.md` or a generated table, so the text and the data cannot disagree.
`check_abstract.py` checks page count, A4, line spacing, that each A1–A7 demand has a section, and 5–10 photos in
the zip.

**M6 — Submit**: user reviews the PDF and photos, sends the e-mail (≥ 20 days before the zonal).

## 6. Decisions needed from the user

| # | Question | Recommendation |
|---|---|---|
| D1 | New repo path and name | `C:\Projects\nac26-waterdrop`, new private GitHub repo |
| D2 | Fresh git history, or keep the old history? | **Fresh** history; old repo archived with a tag and linked from the README |
| D3 | Keep the website (build game, BOM checklist)? | Keep, it is small and the team uses it to build |
| D4 | Merge the optimisation branch into `main` before archiving? | Yes |
| D5 | Zonal date (sets the abstract deadline, date − 20 days) | needed |
| D6 | Team names, college, zone confirmation (IIT Madras), and the template from the IIT Madras site | needed for the title page |
