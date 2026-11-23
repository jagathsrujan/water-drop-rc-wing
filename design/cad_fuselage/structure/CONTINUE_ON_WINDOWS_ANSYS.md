# Continuation prompt — pod structure study (stage F-S) on Windows with ANSYS

Copy everything between the two lines below into Claude Code on the Windows PC, started in the cloned repository folder.

---

You continue the **pod structure study (stage F-S)** of a hand-launched RC water-drop aircraft (Boeing NAC 2026). The study was started on a Mac with CalculiX; it moves to this Windows PC to use **ANSYS through the ANSYS MCP**. Work in this repository. Read the files listed below before you do anything.

## 0. Rules for this work (from the user's global instructions on the Mac; they are not on this PC)
- **Language:** write every message to the user in ASD-STE100 Simplified Technical English: approved simple words, one word for one meaning, active voice, simple tenses, no "-ing" verb forms as verbs or nouns, sentences ≤ 20 words in procedures and ≤ 25 in descriptions, vertical lists for 3+ items, numbers as figures with units. Code, file names and quotes stay exact. Accuracy wins over a style rule.
- **Co-design process (cad-codesign):** the user is a designer, not a reader. Form your own engineering view first, then ask. Tier 1 decisions (concept, material, interfaces, anything costly to reverse, any departure from the brief or a decision record) → stop and ask. Tier 2 (thicknesses, spacings, fillets, clearances) → decide by calculation, record, report in the next update. Weigh the user's input by evidence: needs and preferences are decisive; engineering claims are checked. Send a short update (done / decisions / checks / picture / next / one question) after each stage and at least every 30 minutes.
- **Records:** every tier 1 and tier 2 decision goes into `design/DECISIONS.md` (next free ID: **D-065**) or the stage notebook; keep `design/logs/fuselage_structure_log.md` as the engineering notebook as you work; add one row to `design/logs/DESIGN_LOG.md` per stage.
- **Git:** do not commit or push unless the user asks. When the user asks, work on a branch (for example `fs-ansys`), never force-push `main`. The repository is **public**.
- **Do not change** the reservoir model (`design/cad_reservoir/`) or the wing (`design/cad/`). The fuselage CAD is built only by `design/cad_fuselage/scripts/run_all.py` (FreeCAD GUI); do not hand-edit `Fuselage_revA.FCStd`.

## 1. Read first
1. `design/logs/fuselage_structure_log.md` — the whole notebook: materials (§2), load cases (§3), criteria (§4), mass bounds (§5), the engineer's view (§6), interview (§7), FEM method proof (§8), restart and load review (§9).
2. `design/DECISIONS.md` — **D-046** (no cross bar over the top opening X −27…231: the bottle lifts out upward), **D-054** (launch grip under the belly X 40–120), **D-058/D-059** (safety pin; servo-arm pocket), **D-060** (objective, film-covered windows, "balanced" strength level, FEM-guided layout), **D-061** (flap stop lip), **D-062** (F-B departures), **D-063** (tubes Ø10/8), **D-064** (load set and design material — the governing record for this study).
3. `design/04_fuselage_plan.md` (layout §3, parts §4, key checks §9) and `design/03_reservoir_plan.md` §13–§14 (binding interface).
4. `design/logs/fuselage_cad_log.md` — stages F-A, F-B, F-C as built (tier 2 decisions, checks, the OCC boolean fault on F3 in §5 of F-C).
5. `design/cad_fuselage/scripts/fus_struct.py` — the parametric structure design (diagrid ribs, frames, stringers, floor ribs, belly-opening rim, diamond windows, keep-outs) with `apply()` for the CAD and `fem_variant()` for the FEM. **Its `PAR` values are the deliverable of this study.**
6. `design/cad_fuselage/structure/fem/pod_model.py` (geometry for the FEM, zones and thicknesses, selectors, inertia, load cases), `shellfem.py`, `run_study.py` — the CalculiX implementation; use them as the specification of the loads and boundary conditions for ANSYS.
7. Results so far: `design/cad_fuselage/structure/results/base/` (baseline, run again 2026-11-23 15:05 with the D-064 loads), pictures in `structure/img/`. D1 (first structure design) has no result: see §6.

## 2. Geometry
- Frame: wing frame, mm. Origin at the wing LE on the centreline; X aft, Y right, Z up. Wing at +3° about Y.
- `design/cad_fuselage/export/Fuselage_revA_pod_FB.step` — pod parts after stage F-B: F1 nose, F2 centre, F3 aft, F4 hatch, F5a/b skids, F6 balsa front stop, F7 ply firewall, F8 rear dowel, F9 band stubs. **No ribs yet.**
- `design/cad_fuselage/export/Fuselage_revA_assembly.step` — everything (pod, tail, wing rev A at +3°, reservoir references, placeholders), for context and load points.
- Skins (printed single wall, `fus_params.py`): sides and aft-cone sides 0.5 mm; floor, bottom corners, nose (X < −35), hatch top, aft-cone bottom, end wall 0.8 mm. Belly outer Z −117.0; width 110 (|Y| ≤ 55) at X 0–280; top open X −2…280 (closed by the wing on 1 mm foam tape — the wing is **not** a structural lid). Belly opening X 47–115, Y ±20.
- Members that exist in any case: 8 × 0.8 mm seat lips X 2…280; joint sleeve/frame at X 175; 3 mm balsa front stop X −29.22…−26.22 (Ø50 hole); 3 mm ply firewall X −173…−170; socket block X 233.5–305.1 with 2 bores Ø10.3 at Y ±16, Z −40 (D-063); D-059 servo pocket wall 1.2 mm.
- Print orientation (interp.): F2 belly down; F1 and F3 on their split faces. Check principal stress against the Z (across-layer) allowable everywhere.

## 3. Material (D-064: design for ASA Aero 0.65)
| | E X-Y | E Z | allowable X-Y | allowable Z | density |
|---|---|---|---|---|---|
| ASA Aero 0.65 (foamed, interp.) | 866 MPa | 509 MPa | 11.9 MPa | 5.6 MPa | 0.65 g/cm³ |
| PLA Basic (test pod) | 2680 | 2160 | 27.3 | 17.5 | 1.24 |
| Balsa 3 mm (stop) | ≈ 1000 (isotropic avg.) | | | | 0.12–0.16 |
| Birch ply 3 mm (firewall) | ≈ 5000 | | | | 0.60–0.65 |
The CalculiX model used one isotropic E = √(866·509) = 664 MPa, ν 0.35. Self-weight with PLA density (heavier aircraft). If ANSYS uses an orthotropic shell, state the layer direction per part.

## 4. Load cases (limit; ultimate = 1.5 × limit) — D-064
Masses: water + reservoir 1047.5 g at X 80 (saddles X 1.98–21.98 / 139.28–169.98, front stop in X); release servo 13.4 g at X 64 (right wall); motor + prop 70 g at X −190 (firewall); ESC 25 g at X −140; battery 85 g at X −92 (tray); wing 184 g at X 110 (seat lips/bands); tubes now **Ø10/8: 42.9 g at X 480**; tail 35 g at ≈ X 690 (socket block); tail servos + receiver 26 g at X 215; wiring 15 g distributed.
| LC | Case | Load and reaction |
|---|---|---|
| LC1a | Flat belly landing | 10 g down on every mass; skids fixed (front X −30…40, rear X 120…195, \|Y\| < 35) |
| LC1b / LC1c | Front skid first / rear skid first | 10 g at the contact, rigid-body pitch of the loaded aircraft (inertia relief; see `pod_model.relief`) |
| LC2 | Nose-in | 10 g fore-aft (98 N on the front stop) + 5 g down, front skid |
| LC3 | Hand launch | 5 g forward + 1 g down, palm fixed (floor X 40–120, \|Y\| 20–50), **finger squeeze 20 N each side** (X 50–110, Z −100…−60) |
| LC4 | Motor | 12 N thrust + 0.3 N·m torque at the firewall, hatch off; reaction at the band stubs + rear dowel |
| LC5 | Band preload | 50 N total: 2 × 12.5 N up at the stubs (X −6, Z −24), 25 N up at the dowel (X 295, Z −22); 50 N down on the seat lips near the bands; self-balanced |
| LC6 | Flight 3 g | pod hangs from the stubs (71 %) and the dowel (29 %) |
| LC7a/b/c | Tail | 19.7 N vertical at X 680 (7.5 N·m at the socket); 9 N lateral at the fin (X 690, Z +40) + 0.72 N·m; 0.9 N·m asymmetric stab torsion (± on the two sockets) |
| LC8 | Thumb press | 10 N on a Ø15 patch: lip X 140, sides X 10 / 150 / 205, nose X −100, grip X 80, floor X 80, aft X 250 |

## 5. Criteria (D-060 "balanced", D-064)
1. Strength at ultimate: max principal ≤ Z allowable and von Mises ≤ X-Y allowable (ASA Aero 0.65; report PLA too).
2. Buckling at limit: frames, lips, stringers, global λ ≥ 2.0; skin panels between ribs λ ≥ 1.0.
3. Stiffness: LC8 ≤ 2.0 mm on frames, lips and the grip zone only (skin panels may flex); tail socket under LC7 ≤ 2.0 mm, twist ≤ 0.5°.
4. Printability: no horizontal window top edge (window edges ≥ 45° to the layers), no flat overhang > 3 mm on a rib, bridges ≤ 20 mm.
5. Keep-outs (fus_struct.py header): no member across X −27…231 at the top (D-046); battery path in the nose floor |Y| < 22 at X −165…−35 free; no window in the belly, aft-cone bottom, grip zone X 35–125, servo pocket, stub bosses, flag hole, socket block, split joints, lip band.

## 6. State and known problems
- **Baseline (no ribs), CalculiX, ASA Aero 0.65, D-064 loads:** stress utilization LC3 32, LC1b 24, LC1c 22, LC5 16, LC8 grip 16, LC2 14, LC8 sides 12, LC7a 9, LC6 6.4, LC1a 6.1, LC4 2.2. Printed mass in that model 88.0 g ASA Aero / 167.9 g PLA.
- **Suspected model artefact (check first):** linear deflections of 60–150 mm in LC1b/c, LC2, LC3, LC5, while a beam estimate of the pod gives about 1 mm. Local panels and point-like load patches control the result. Before designing to these peaks, make sure every mass goes into the structure through its real mount (saddle feet, tray posts, servo shelves, firewall, sockets), not as a pressure on bare 0.5 mm skin, and that the reaction patches are realistic. Report peak and "far-field" values separately.
- **D1 did not solve in CalculiX:** `ccx failed (static): gen3dnor: in node 40278 opposite normals are defined`. The rib/frame shells meet the skin shells at T-junctions, and the expanded shell normals there are opposite. In ANSYS, use shell elements with shared nodes at the T-junctions (no 3D expansion), or model the ribs as beams/stiffeners on the skin.
- **CalculiX limit (Mac):** this build finds only buckling factors near 1.0; the study used a load-scale sweep. ANSYS eigen-buckling does not need this.
- **OCC boolean fault:** FreeCAD `common` fails silently on F3 between X 175 and 200; the check scripts use `fus_build.ovl()` (gap test + point test). Keep that in mind if you mesh F3 from FreeCAD.
- Expected result: the final pod mass will be higher than the 120 g shell-only value (ASA Aero 0.65, all F-B parts) because ribs and frames are needed; the goal is the lightest structure that passes, then film-covered diamond windows (D-060) where the stress is low.

## 7. Task
1. Set up: confirm the ANSYS MCP works (version, licence, a small test). Import `Fuselage_revA_pod_FB.step`. Build a shell model of F1–F3 (outer surface or mid-surface; thickness by zone as §2) with the members of §2.
2. **Validation:** reproduce the baseline with the same loads and compare with §6 (order of magnitude, hot-spot locations). Explain differences. Then fix the load introduction if the artefact of §6 is real.
3. Design: start from `fus_struct.PAR` (diagrid 0.8 × 5 mm at 30 mm spacing, frames X 40/80/120, V-struts X 236 and −40, floor stringers |Y| 31, rim round the belly opening, lower wall stringer Z −104). Change spacing, depth, thickness and skin thickness (0.8 → 0.5 where possible) to pass §5 with the least mass. Then add windows in the low-stress bays.
4. Verify the final design: all LCs, buckling, stiffness; mass in ASA Aero 0.65 and PLA.
5. Deliver: the final `PAR` values in `fus_struct.py` (keep the keep-outs), a study report `design/cad_fuselage/structure/structure_study.md` (inputs, method, validation, iterations with mass and utilization, final result, pictures in `structure/img/`), notebook and decision entries, and the ANSYS project files in `design/cad_fuselage/structure/ansys/` (no large result files in git: add a `.gitignore` for them).
6. CAD integration is done afterwards on the Mac (FreeCAD GUI, `run_all.py` with `fus_struct.apply`). If FreeCAD is on this PC and the user wants it here, set the environment variable `FUS_SCRIPTS` to the scripts folder (the default path in the scripts is the Mac home folder) and run `run_all.py` inside the FreeCAD GUI.

## 8. Other open items (not this task; keep them in mind)
- Tail strike: the tail block touches the ground from about 7.6° nose-up on the aft belly corner. Options given to the user: a 1.5 mm PETG skid pad under the tail block (recommended) or tubes raised 7 mm. Not decided.
- Stage F-D (electronics placeholders, CG at X 80, firewall and battery position) and F-E (exports) are not started.

Start by reading the files of §1, then send the user a short plan (in STE) with the first question, if any.

---
