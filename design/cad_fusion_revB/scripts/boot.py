# Run first in every bridge call: puts the scripts on sys.path and reloads the modules (edits take effect).
import importlib
import os
import sys

SCRIPTS = r"C:\Projects\water-drop-rc-wing\design\cad_fusion_revB\scripts"
REPO = r"C:\Projects\water-drop-rc-wing"
for p in (SCRIPTS, os.path.join(REPO, "design", "cad_fuselage", "scripts"),
          os.path.join(REPO, "design", "cad_fuselage_balsa", "scripts"), os.path.join(REPO, "design", "cad", "scripts"),
          os.path.join(REPO, "design", "cad_reservoir", "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)


def rl(name):
    if name in sys.modules:
        return importlib.reload(sys.modules[name])
    return importlib.import_module(name)
