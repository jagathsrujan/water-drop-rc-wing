# Run first in every bridge call: puts the scripts on sys.path and reloads the modules (edits take effect).
import importlib
import os
import sys

SCRIPTS = os.path.dirname(os.path.abspath(__file__))   # follows the checkout / worktree the job is run from
MODEL = os.path.dirname(SCRIPTS)
REPO = os.path.dirname(os.path.dirname(MODEL))
for p in (SCRIPTS, os.path.join(REPO, "design", "cad_fuselage", "scripts"),
          os.path.join(REPO, "design", "cad_fuselage_balsa", "scripts"), os.path.join(REPO, "design", "cad", "scripts"),
          os.path.join(REPO, "design", "cad_reservoir", "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)


_OWN = os.path.normcase(os.path.abspath(REPO))
_SUBS = (os.path.join("design", "cad_fusion_revB", "scripts"), os.path.join("design", "cad_fuselage", "scripts"),
         os.path.join("design", "cad_fuselage_balsa", "scripts"), os.path.join("design", "cad", "scripts"),
         os.path.join("design", "cad_reservoir", "scripts"))
# the Fusion Python process outlives the jobs: drop the script folders of any other checkout (main / other worktree)
for _p in list(sys.path):
    _n = os.path.normcase(os.path.abspath(_p))
    if _n.endswith(tuple(os.path.normcase(s) for s in _SUBS)) and not _n.startswith(_OWN):
        sys.path.remove(_p)
for _k, _m in list(sys.modules.items()):
    _f = os.path.normcase(os.path.abspath(getattr(_m, "__file__", "") or "/"))
    if os.path.dirname(_f).endswith(tuple(os.path.normcase(s) for s in _SUBS)) and not _f.startswith(_OWN):
        del sys.modules[_k]


def rl(name):
    m = sys.modules.get(name)
    if m is not None:
        f = os.path.normcase(os.path.abspath(getattr(m, "__file__", "") or ""))
        if not f.startswith(_OWN):
            del sys.modules[name]            # loaded from another checkout: import afresh from this one
        else:
            return importlib.reload(m)
    return importlib.import_module(name)
