"""Rev B (Fusion) parameter overrides of the optimisation study (design/optimisation/P1_single_stock.md, P2_lightening.md).

The FreeCAD parameter files (bal_params, wing_params, fus_params, res_params) stay the reference of the FreeCAD models
and are NOT edited. The Fusion part data imports BP, WP, FP, RP from here: copies of those modules with the values the
user approved (P1 gate 2026-11-26: one balsa stock 1.5 mm medium, one birch-ply stock 1.5 mm, no lite-ply; P2 gate:
changes 1-12)."""
import types

import bal_params as _BP
import fus_params as _FP
import res_params as _RP
import wing_params as _WP

STOCK_T = 1.5          # the one balsa stock and the one birch-ply stock (mm)


def _copy(mod, **over):
    ns = types.SimpleNamespace(**{k: getattr(mod, k) for k in dir(mod) if not k.startswith("__")})
    for k, v in over.items():
        if not hasattr(ns, k):
            raise KeyError("override of an unknown parameter: %s.%s" % (mod.__name__, k))
        setattr(ns, k, v)
    ns.__name__ = mod.__name__ + " (rev B overrides)"
    return ns


FP = _copy(_FP, BATT_XC=-120.0)                       # P2 item 12: battery at the front of its range (CG)
RP = _copy(_RP)
BP = _copy(_BP,
           T_SIDE_IN=STOCK_T,                          # inner side layer 1.0 -> 1.5 (single stock)
           TRAY_T=2 * STOCK_T,                         # battery tray: 1.5 lite-ply -> 2 x 1.5 balsa
           TRAY_X=(-146.0, _BP.TRAY_X[1]),             # P3: the 3 mm tray starts 4 mm further aft, clear of the sloped nose floor
           STOP_SPOKE=14.0,                            # P2 item 9: front-stop spokes 10 -> 14 mm
           T_HATCH=STOCK_T,
           RX_X0=-76.0)                                # P2 item 12: receiver on the battery tray (X -76 .. -31)
WP = _copy(_WP,
           RIB_C=(_WP.RIB_C[0], 2 * STOCK_T),          # centre rib 2.0 -> 2 x 1.5
           RIBS=[(y, STOCK_T if abs(t - 2.0) < 1e-6 else t) for y, t in _WP.RIBS],   # ribs 2.0 -> 1.5 (rib 110 stays 3 = 2 x 1.5)
           AIL_RIB_T=STOCK_T,                          # aileron ribs and horn ribs 2.0 -> 1.5
           # P2 item 2: tip rib and tip cap one 1.5 layer (were 3 mm); the span stays 990: the tip rib moves out to
           # Y 492 .. 493.5, the cap is Y 493.5 .. 495, and the span-wise parts run to Y 493.5
           TIP_RIB=(_WP.HALF_SPAN - 2 * STOCK_T + STOCK_T / 2, STOCK_T),
           TIP_CAP=(_WP.HALF_SPAN - STOCK_T, _WP.HALF_SPAN),
           Y_END=_WP.HALF_SPAN - STOCK_T,
           # P3: the rear web runs to the inner face of rib 165, which moved from Y 164.0 to 164.25 when the rib
           # went 2.0 -> 1.5: without this the servo-bay rear webs WR-R3 / WR-L3 dropped out of the model
           REAR_WEB_Y=165.0 - STOCK_T / 2)

# former thickness and material (P1): balsa 3 x 1.5 (0/90/0), bulkhead 4 x 1.5, front stop 2 x 1.5 birch crossed
FORMER = {"N1": (3, "balsa_med"), "N2": (3, "balsa_med"), "FS": (2, "ply"), "B1": (3, "balsa_med"),
          "B2": (3, "balsa_med"), "B4": (3, "balsa_med"), "BH": (4, "balsa_med"), "EF": (3, "balsa_med")}

# floor bearing pads under the saddle feet (P2 item 10): birch 1.5, 15 wide on the skid line, X ranges clear of the formers
PAD_W = 15.0
PAD_X = {"S1": (-8.0, 32.0), "S2": (132.0, 169.9)}

# laminated balsa / birch parts: name -> list of layers, each (grain axis 'u' | 'v', split) where split is None,
# ('u', [cuts]) or ('v', [cuts]): the layer is cut into pieces at those local coordinates (pieces <= 100 mm across the
# grain on the 100 mm balsa sheet); joints are staggered between layers. Filled in by pod.py / wing.py / tail.py.
