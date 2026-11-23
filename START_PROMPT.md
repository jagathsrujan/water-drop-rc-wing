# Starting prompt — continue the pod structure study on Windows (ANSYS)

1. Clone the repository and open a terminal in it:
   ```
   git clone https://github.com/jagathsrujan/water-drop-rc-wing.git
   cd water-drop-rc-wing
   ```
2. Start Claude Code in that folder. Make sure the ANSYS MCP is connected.
3. Paste the prompt below as the first message.

---

You continue the pod structure study (stage F-S) of the Boeing NAC 2026 water-drop RC aircraft in this repository, with ANSYS through the ANSYS MCP.

Read `design/cad_fuselage/structure/CONTINUE_ON_WINDOWS_ANSYS.md` completely and follow it. It contains the working rules (ASD-STE100 Simplified Technical English for every message to me, the co-design process with tier 1 / tier 2 decisions, the decision records, no commits or pushes unless I ask), the files to read first, the geometry (STEP files in `design/cad_fuselage/export/`), the materials, the load cases of D-064, the criteria of D-060, the present state with the known model problems, and the task.

Goal: the lightest printed rib / frame structure (with film-covered diamond windows where the stress is low) that makes the pod pass all load cases in ASA Aero 0.65, verified by FEM. Deliverable: the final `PAR` values in `design/cad_fuselage/scripts/fus_struct.py`, a study report, and the notebook and decision entries.

First step: confirm that the ANSYS MCP works, read the files listed in §1 of the continuation file, then send me a short plan and your first question, if any.

---

The full hand-off (state, loads, criteria, open items) is in `design/cad_fuselage/structure/CONTINUE_ON_WINDOWS_ANSYS.md`.
