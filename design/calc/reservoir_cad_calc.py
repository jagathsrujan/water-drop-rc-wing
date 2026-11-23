"""Reservoir CAD planning calculations (H3 horizontal 1 L Bisleri bottle).

All bottle numbers are estimates (interp.) until the real bottle is measured.
Change BOTTLE below only; everything else is derived.

Frame: wing frame of the brief (origin wing LE at the centreline, X aft, Y right, Z up),
fuselage datum horizontal (wing incidence +3 deg is applied to the wing, not here).
Run: python3 design/calc/reservoir_cad_calc.py
"""
import math
import numpy as np

# ---------------- inputs (interp. until measured) ----------------
BOTTLE = dict(
    profile=[[0, 36], [6, 40], [185, 40], [228, 12.5], [235, 10.8], [255, 10.8]],  # [yu from base, inner radius]
    neck_bore=21.0,      # mm
    wall=0.3,            # mm PET wall at the outlet band
)
X_CG = 80.0              # water centroid station (interp., fuselage stage sets final CG)
BORE = 14.0              # outlet bore (key check >= 14)
EXIT_BELOW_WALL = 12.0   # outlet exit plane below the inner wall (stem + gasket + V2 seat)
WATER_ML = 1000.0
G = 9810.0


def ri(yu, prof=BOTTLE["profile"]):
    if yu <= prof[0][0]:
        return prof[0][1]
    for a, b in zip(prof, prof[1:]):
        if yu <= b[0]:
            return a[1] + (b[1] - a[1]) * (yu - a[0]) / (b[0] - a[0])
    return prof[-1][1]


YU = np.arange(0.25, 235, 0.5)          # slices up to the neck (neck water ignored, as in the concept page)
RS = np.array([ri(y) for y in YU])
DY = 0.5
CEN = float((RS**2 * YU).sum() / (RS**2).sum())   # volume centroid from the base
X_BASE = X_CG - CEN                      # base station in the wing frame
X_SLICE = X_BASE + YU                    # slice stations
R_OUT = BOTTLE["profile"][2][1]          # cylinder radius at the outlet


def seg_area(d, r):
    d = np.clip(d, -r, r)
    return r * r * np.arccos(-d / r) + d * np.sqrt(r * r - d * d)


def vol_below(level, pitch_deg, x_out=X_CG):
    """Water volume (mm3) below a horizontal plane at height `level` (measured in the tilted frame
    from the bottle axis at x_out); pitch nose-up positive, so the aft (neck) end is low."""
    p = math.radians(pitch_deg)
    d = (level + (X_SLICE - x_out) * math.sin(p)) / math.cos(p)
    return float((seg_area(d, RS) * DY).sum())


def residual_g(lip_h, pitch_deg, x_out=X_CG):
    p = math.radians(pitch_deg)
    lip_level = (-R_OUT + lip_h) * math.cos(p)
    return vol_below(lip_level, pitch_deg, x_out) / 1000 * 0.996


def drain_time(bore, lip_h, pitch_deg, cd=0.6, x_out=X_CG):
    p = math.radians(pitch_deg)
    a = math.pi * bore**2 / 4
    lip_level = (-R_OUT + lip_h) * math.cos(p)
    exit_level = (-R_OUT - EXIT_BELOW_WALL) * math.cos(p)
    levels = np.linspace(lip_level, R_OUT, 600)
    vols = np.array([vol_below(L, pitch_deg, x_out) for L in levels])
    vol, t, dt = WATER_ML * 1000, 0.0, 0.01
    while t < 120:
        L = float(np.interp(vol, vols, levels))
        if L <= lip_level + 0.02:
            break
        vol -= cd * a * math.sqrt(2 * G * max(L - exit_level, 0)) * dt
        t += dt
    return t


def enclosing_d(flange_w, flange_t, stem_od, stem_len):
    """Smallest circle around the end-on insertion profile of a flange with an integral stem:
    a bar flange_w x flange_t with a stem stem_od wide and stem_len long below it."""
    best = 1e9
    for c in np.linspace(0, flange_t + stem_len, 2001):
        r = max(math.hypot(flange_w / 2, c), math.hypot(flange_w / 2, flange_t - c),
                math.hypot(stem_od / 2, flange_t + stem_len - c))
        best = min(best, r)
    return 2 * best


if __name__ == "__main__":
    print(f"Centroid from base {CEN:.1f} mm; base X {X_BASE:.1f}; shoulder X {X_BASE + 185:.1f}; "
          f"neck lip X {X_BASE + 255:.1f}; vent (base + 16) X {X_BASE + 16:.1f}")
    full = vol_below(R_OUT, 0) / 1000
    print(f"Interior volume to the neck (no punt): {full:.0f} mL")
    # ullage bubble depth, level
    for h in np.linspace(0, 20, 2001):
        if full * 1000 - vol_below(R_OUT - h, 0) >= (full - WATER_ML) * 1000:
            print(f"Air bubble with {WATER_ML:.0f} mL, level: depth {h:.1f} mm, half-width "
                  f"{math.sqrt(2 * R_OUT * h):.1f} mm at the top")
            break
    print("\nResidual water (g) vs lip height at the outlet and pitch (nose up)")
    pitches = [0, 1, 2, 3, 5]
    print("lip mm " + "".join(f"{p:>7}deg" for p in pitches))
    for lip in [0.0, 0.5, 0.8, 1.0, 1.2, 1.5, 2.0, 2.7]:
        print(f"{lip:6.1f} " + "".join(f"{residual_g(lip, p):10.1f}" for p in pitches))
    print("\nDrain time (s), Cd 0.6, vented, exit 12 mm below the wall")
    for bore in [12, 14, 16]:
        print(f"bore {bore}: " + ", ".join(f"{p} deg {drain_time(bore, 1.2, p):.1f}" for p in [0, 3]))
    print("\nInsertion through the neck (end-on, major axis along the neck): enclosing diameter")
    nb = BOTTLE["neck_bore"]
    for fw, ft, so, sl in [(20.5, 1.2, 16.4, 9.0), (18.5, 1.2, 17.0, 9.0), (18.5, 1.2, 17.0, 7.0),
                           (17.0, 1.2, 17.0, 9.0), (20.5, 1.2, 17.0, 9.0)]:
        d = enclosing_d(fw, ft, so, sl)
        print(f"flange minor {fw} x t {ft}, stem OD {so} x {sl}: {d:.1f} mm "
              f"({'fits' if d <= nb - 0.5 else 'NO'} in a {nb} mm bore with 0.5 mm clearance)")
    print("\nServo chain (MG90S stall 0.177 N m at 4.8 V, 90 deg throw, 50 % force margin)")
    for r in [8, 10, 12, 15]:
        travel = 2 * r * math.sin(math.radians(45))
        twitch = r * math.radians(15)
        print(f"arm {r} mm: pin travel {travel:.1f} mm, allowed pull {0.5 * 0.177 / (r / 1000):.1f} N, "
              f"15 deg twitch {twitch:.1f} mm")
    # outlet water force on the flap seal (inner gasket diameter 16 mm), head = bottle dia + exit depth
    head = 2 * R_OUT + EXIT_BELOW_WALL
    a = math.pi * 0.016**2 / 4
    for n in [1, 2, 10]:
        print(f"water force on the flap at {n} g: {1000 * 9.81 * n * head / 1000 * a:.2f} N")
