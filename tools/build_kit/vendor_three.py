"""Turn the three.js npm package (ES modules only) into two classic scripts for the build game, so the game works
from file:// (browsers block ES-module imports there) as well as on GitHub Pages.

    npm pack three            (gives three-<version>.tgz; unpack it)
    python tools/build_kit/vendor_three.py <path to the unpacked 'package' folder>

Writes docs/build-game/vendor/three.js (window.THREE), vendor/OrbitControls.js (THREE.OrbitControls) and the
three.js licence. The code itself is not changed: each module is wrapped in its own function scope and its
import / export statements are replaced by plain object lookups."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "docs", "build-game", "vendor")
STMT = re.compile(r"^(import|export)\s*\{([^}]*)\}\s*(?:from\s*'([^']+)')?\s*;\s*$", re.M)


def pairs(lst):
    out = []
    for item in lst.split(","):
        item = item.strip()
        if not item:
            continue
        m = re.match(r"(\w+)(?:\s+as\s+(\w+))?$", item)
        if not m:
            raise ValueError("cannot parse " + item)
        out.append((m.group(1), m.group(2) or m.group(1)))
    return out


def wrap(src, imports_from):
    """Body of one module: (code without import/export, [(local, exported)], [(name, alias) re-exported from core])."""
    exports, reexports, imports = [], [], []

    def sub(m):
        kind, lst, frm = m.group(1), m.group(2), m.group(3)
        if kind == "import":
            imports.extend(pairs(lst))
            return ""
        if frm:
            reexports.extend(pairs(lst))
        else:
            exports.extend(pairs(lst))
        return ""
    code = STMT.sub(sub, src)
    if re.search(r"^\s*(import|export)\b", code, re.M):
        raise ValueError("unhandled import/export left")
    return code, exports, reexports, imports


def main(pkg):
    os.makedirs(OUT, exist_ok=True)
    core = open(os.path.join(pkg, "build", "three.core.js"), encoding="utf-8").read()
    mod = open(os.path.join(pkg, "build", "three.module.js"), encoding="utf-8").read()
    ccode, cexp, _, cimp = wrap(core, None)
    assert not cimp
    mcode, mexp, mre, mimp = wrap(mod, "core")
    head = core.split("*/", 1)[0] + "*/\n"
    js = [head, "// Bundled for classic <script> use by tools/build_kit/vendor_three.py (code unchanged).\n",
          "(function () {\n'use strict';\nconst __core = (function () {\n", ccode,
          "\nreturn {" + ", ".join("%s: %s" % (b, a) for a, b in cexp) + "};\n})();\n",
          "(function () {\nconst {" + ", ".join("%s: %s" % (a, b) for a, b in mimp) + "} = __core;\n", mcode,
          "\nconst THREE = {" + ", ".join("%s: __core.%s" % (b, a) for a, b in mre) + "};\n",
          "".join("THREE.%s = %s;\n" % (b, a) for a, b in mexp),
          "window.THREE = THREE;\n})();\n})();\n"]
    open(os.path.join(OUT, "three.js"), "w", encoding="utf-8").write("".join(js))
    oc = open(os.path.join(pkg, "examples", "jsm", "controls", "OrbitControls.js"), encoding="utf-8").read()
    ocode, oexp, ore, oimp = wrap(oc, "three")
    js = ["// three.js OrbitControls (MIT), bundled for classic <script> use by tools/build_kit/vendor_three.py\n",
          "(function () {\n'use strict';\nconst {" + ", ".join("%s: %s" % (a, b) for a, b in oimp) + "} = window.THREE;\n",
          ocode, "".join("window.THREE.%s = %s;\n" % (b, a) for a, b in oexp), "})();\n"]
    open(os.path.join(OUT, "OrbitControls.js"), "w", encoding="utf-8").write("".join(js))
    ver = re.search(r"REVISION = '(\d+)'", core)
    lic = open(os.path.join(pkg, "LICENSE"), encoding="utf-8").read()
    open(os.path.join(OUT, "LICENSE-three.txt"), "w", encoding="utf-8").write(
        "three.js r%s (npm package 'three'), MIT licence:\n\n%s" % (ver.group(1) if ver else "?", lic))
    print("vendor written to", OUT, "three r%s" % (ver.group(1) if ver else "?"))


if __name__ == "__main__":
    main(sys.argv[1])
