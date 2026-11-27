# P4 — Simulation tool evaluation (what can run on this PC, and what the abstract uses)

Date 2026-11-26. Every result below was run here, not assumed.

## Recommendation

| Analysis | Tool | Why |
|---|---|---|
| **Aerodynamics** (lift curve, polars, Cm-α, neutral point, trim, control) | **AVL 3.52** (Drela & Youngren, MIT, GPL) with SD7062 profile drag from NeuralFoil | Flow5 / XFLR5 are not installed. AVL is the standard vortex-lattice code for small aircraft, it is scriptable (repeatable runs from the part data), and it gives the stability derivatives the abstract needs. |
| **CFD** (pressure and velocity pictures, a check of lift and drag) | **SOLIDWORKS Flow Simulation 2026** | Installed and licensed, with an API. Ansys Fluent will not start (licence). |
| **FEA** (spar, front stop, floor, grip panel, bulkhead) | **SOLIDWORKS Simulation 2026** (static, solid and shell) | Installed and licensed, driven from the API. The benchmark agrees with the hand solution within 1 %. Ansys MAPDL will not start (licence). |
| Hand calculations, post-processing | MATLAB R2024b (MCP) | As P1/P2. |

## What was tried

### Ansys 2024 R1 (installed at `E:\ANSYS Inc\v241`)
- **MAPDL** (MCP `ansys-mapdl`): the installation is found, but the process exits at start-up. The licence server
  (`1055@localhost`) rejects every feature (ansys, mech_1/2, meba, preppost, ane3fl): "Invalid (inconsistent) license
  key … usually happens when a license file has been altered" (FlexNet −8,544).
- **Fluent** (MCP `ansys-fluent`, PyFluent): the MCP's PyFluent wants 2024 R2 or newer (AWP_ROOT242+). Launched by
  path, Fluent 24.1 ends with "Unexpected license problem; exiting" (Shared Web License).
- **Verdict:** not usable on this PC until there is a valid licence: the company or university licence, or the
  free Ansys Student edition, whose limits (128k nodes / cells) are enough for these parts. Nothing was changed in
  the licence setup.

### SOLIDWORKS 2026 SP0 (Simulation, Flow Simulation)
- **MCP `solidworks`:** connected (revision 34.0.0). It has CAD tools only (sketch, extrude, mates, drawings,
  mass properties), no simulation tools.
- **Simulation API:** the add-in loads (`LoadAddIn` → 0) and `CosmosWorks` is reachable. PowerShell late binding
  fails (TYPE_E_ELEMENTNOTFOUND), so the studies are written in C# and compiled at run time by PowerShell `Add-Type`
  against the interop assemblies in `SOLIDWORKS\api\redist` ([`p4/SwFeaBench.cs`](p4/SwFeaBench.cs),
  [`p4/run_sw_bench.ps1`](p4/run_sw_bench.ps1)).
- **FEA benchmark:** balsa cantilever 100 × 10 × 3 mm, E 2.55 GPa (P1 design value), clamped at one end, 0.5 N
  spread over the top face:

  | | Hand (beam theory) | SolidWorks Simulation |
  |---|---|---|
  | Tip deflection | W L³ / (8 E I) = 1.089 mm | **1.080 mm (−0.9 %)** |
  | Bending stress at the root | W L / 2 · c / I = 1.67 MPa | 2.23 MPa peak (the stress spike at a clamped edge with Poisson coupling); beam value away from the clamp |
  | Mesh / time | | 30,831 quadratic tetrahedra, 1 mm, solved in 3.9 s |

- **Flow Simulation API:** type library `binCFW\EFDApi.tlb` (IApplication, IProject, goals, cut plots, image
  export). It converts to .NET with `TypeLibConverter` (there is no tlbimp on this PC), so CFD runs can be scripted
  too.

### Aerodynamic panel / VLM codes
- Flow5, XFLR5, OpenVSP: not installed.
- **AVL 3.52:** downloaded from the official MIT page (`https://web.mit.edu/drela/Public/web/avl/avl352.exe`,
  1,793,164 bytes, GPL, under the user's standing permission) and run here. The model
  `design/simulation/aero/avl/revB.avl` is written by `make_avl.py` from the CAD parameter files. First run: CL 0.50
  at α 2°, CLα 3.81 /rad, neutral point X 116.5 mm → static margin 13 % MAC with the CG at X 80.

## Credibility for the abstract
- Every model is generated from the same part data as the CAD, so the geometry is the built aircraft.
- Each tool has a check:
  - FEA: the benchmark above; P6 adds a mesh convergence study and compares with the P2 hand calcs.
  - VLM: CLα against the finite-wing estimate a = a₀ / (1 + a₀ / (π e AR)).
  - CFD: against AVL plus the profile drag.
- Material data come from the Wood Handbook ([`references.md`](../optimisation/references.md)).
