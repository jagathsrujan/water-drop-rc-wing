"""Fuselage stage: first sizing (tail volume, neutral point, CG balance, mass by concept).

All values are estimates (interp.) until the parts are chosen and weighed.
Frame: wing frame (origin at the wing LE, X aft, mm). Run: python3 design/calc/fuselage_sizing.py
"""
import math

# --- wing rev A (design/02_wing_plan.md, design/aero/wing_lift_performance.txt)
S = 0.2772          # m2
c = 0.280           # m (MAC = chord, rectangular)
b = 0.990           # m
AR = b * b / S
a_w = 0.0668 * 180 / math.pi      # 3D lift slope, /rad
x_ac_w = 0.25 * c * 1000          # mm

X_CG_TARGET = 80.0                # water centroid (reservoir plan 13)

def tail(l_h_mm, Vh=0.45, Vv=0.035, AR_h=3.5, AR_v=1.6):
    l = l_h_mm / 1000
    Sh = Vh * S * c / l
    Sv = Vv * S * b / l
    bh = math.sqrt(Sh * AR_h); ch = Sh / bh
    hv = math.sqrt(Sv * AR_v); cv = Sv / hv
    return Sh, bh, ch, Sv, hv, cv

def neutral_point(l_h_mm, Vh, AR_h=3.5, eta=0.9, deps=0.55, fus_shift_mm=-12.0):
    """Stick-fixed NP (mm aft of the LE). deps: downwash gradient at the tail (interp.):
    a_w/(pi*AR) = 0.35 at the wing, 2*a_w/(pi*AR) = 0.69 far downstream; a tail about 2 chords
    aft is between these. Use the range 0.45 to 0.65; 0.55 is the central value.
    fus_shift: destabilising shift of the fuselage pod (interp., Gilruth method order)."""
    a_t = 2 * math.pi * AR_h / (2 + math.sqrt(AR_h ** 2 + 4))
    return x_ac_w + Vh * (a_t / a_w) * (1 - deps) * eta * c * 1000 + fus_shift_mm, a_t

# --- placeholder masses (g) and X (mm). Electronics: catalogue class values (interp., stage 3)
def masses(l_h_mm, tail_servos_aft=False, concept="pod_boom"):
    x_tail = X_CG_TARGET + l_h_mm            # tail AC station
    items = [
        ("wing rev A with 2 MG90S", 184.0, 110.0),          # vol-weighted CX 106 + film, servos at x 130
        ("reservoir rev A.2 dry parts", 47.5, 85.0),
        ("release servo MG90S", 13.4, 64.0),
        ("receiver", 8.0, 160.0),
        ("wiring, connectors", 15.0, 40.0),
        ("tail servos 2 x 9 g class", 18.0, (x_tail - 60) if tail_servos_aft else 200.0),
        ("pushrods / cables", 6.0 if not tail_servos_aft else 2.0, (x_tail + 200) / 2),
    ]
    if concept == "pod_boom":
        items += [("pod (balsa box round the bottle + nose, by area)", 56.0, 50.0),
                  ("boom carbon tube 10/8 mm", 0.0283 * (x_tail - 230) * 1.55, (x_tail + 230) / 2),
                  ("tail mount + boom clamp", 6.0, x_tail)]
    else:
        items += [("full balsa box fuselage", 56.0 + 0.105e6 * 2e-3 * 120 / 1000 * (l_h_mm / 600), 150.0)]
    Sh, bh, ch, Sv, hv, cv = tail(l_h_mm)
    m_tail = (Sh + Sv) * 1e6 * 2.0e-3 * 100 / 1000 * 1.0 + 4.0   # 2 mm light balsa + hinges, film-free
    items.append(("tail surfaces (2 mm light balsa sheet)", m_tail, x_tail))
    return items

NOSE = [("motor 2212 class", 55.0), ("prop 10 in folding + spinner", 15.0),
        ("ESC 30 A", 25.0), ("battery 3S 1000 mAh", 85.0)]

def nose_station(items):
    """X of the nose group (motor, prop, ESC, battery as one mass) that puts the CG on X_CG_TARGET."""
    m_n = sum(m for _, m in NOSE)
    mom = sum(m * (x - X_CG_TARGET) for _, m, x in items)
    return X_CG_TARGET - mom / m_n, m_n

if __name__ == "__main__":
    print(f"Wing S {S} m2, AR {AR:.2f}, a_w {a_w:.2f}/rad, wing AC x {x_ac_w:.0f} mm")
    print("\nTail size by arm (Vh 0.45, Vv 0.035):")
    print(" l_h  | Sh dm2 | b_h x c_h mm | Sv dm2 | h_v x c_v mm | NP mm | SM at CG 80 | nose group X | empty g | score")
    for l in (500, 550, 600, 650, 700):
        Sh, bh, ch, Sv, hv, cv = tail(l)
        np_, a_t = neutral_point(l, 0.45)
        items = masses(l)
        xn, mn = nose_station(items)
        empty = sum(m for _, m, _ in items) + mn
        print(f" {l:4d} | {Sh*100:5.2f}  | {bh*1000:4.0f} x {ch*1000:3.0f}   | {Sv*100:5.2f}  | {hv*1000:4.0f} x {cv*1000:3.0f}   |"
              f" {np_:5.0f} | {(np_-X_CG_TARGET)/c/10:5.1f} %    | {xn:7.0f}      | {empty:6.0f}  | {99600/empty:5.0f}")
    print("\nNP and static margin (CG 80) against the downwash gradient and Vh (l_h 600):")
    print(" Vh   | deps 0.45      | deps 0.55      | deps 0.65")
    for Vh in (0.40, 0.45, 0.50, 0.55, 0.60):
        row = []
        for d in (0.45, 0.55, 0.65):
            np_, _ = neutral_point(600, Vh, deps=d)
            row.append(f"NP {np_:4.0f} SM {(np_-X_CG_TARGET)/c/10:5.1f} %")
        print(f" {Vh:.2f} | " + " | ".join(row))
    print("\nPod mass by area (balsa 120 kg/m3, interp.):")
    pod = [("sides 2 x 390 x 100 x 2 mm, -30 % holes", 0.078*2e-3*120*1000*0.7),
           ("floor 390 x 110 x 1.5 mm", 0.043*1.5e-3*120*1000),
           ("top decks (nose hatch, aft deck) 1.5 mm", 0.02*1.5e-3*120*1000),
           ("firewall 3 mm ply 50 x 50", 4.5), ("front stop 3 mm balsa", 3.2),
           ("2 formers 3 mm balsa", 5.0), ("2 wing dowels 4 mm birch", 2.1),
           ("4 triangle longerons 6 x 6", 4*390*18*0.12/1000),
           ("glue", 5.0), ("film / tape 0.15 m2 x 50 g/m2", 7.5)]
    for n, m in pod:
        print(f"  {n:42s} {m:5.1f} g")
    print(f"  pod total {sum(m for _, m in pod):.1f} g (belly skid not included)")
    print("\nPlaceholder breakdown at l_h 600 (pod + boom):")
    items = masses(600)
    for n, m, x in items:
        print(f"  {n:42s} {m:6.1f} g  X {x:6.0f}")
    xn, mn = nose_station(items)
    for n, m in NOSE:
        print(f"  {n:42s} {m:6.1f} g  X {xn:6.0f} (group)")
    print(f"  empty total {sum(m for _, m, _ in items)+mn:.0f} g; loaded {sum(m for _, m, _ in items)+mn+996:.0f} g")
    print("\nR3 (rule): static thrust <= 1.5 x empty weight -> about", round(1.5*(sum(m for _,m,_ in items)+mn)), "g thrust max")


# ---------------------------------------------------------------- concept U (D-052)
def concept_U(l_h=600.0, Vh=0.50, servos_aft=False, pod_g=75.0):
    """Printed pod + 2 x 8/6 carbon tubes. Returns the item list without the nose group."""
    x_t = X_CG_TARGET + l_h
    Sh = Vh * S * c / (l_h / 1000); Sv = 0.035 * S * b / (l_h / 1000)
    tube_len = x_t + 40 - 230                    # sockets from X 230 to the tail block
    items = [
        ("wing rev A with 2 MG90S", 184.0, 110.0),
        ("reservoir rev A.2 dry parts", 47.5, 85.0),
        ("release servo MG90S", 13.4, 64.0),
        ("receiver", 8.0, 215.0),
        ("wiring, connectors (nose + pod)", 15.0, 0.0),
        ("printed pod (ASA Aero, interp.)", pod_g, 60.0),
        ("boom sockets (printed)", 8.0, 265.0),
        ("2 carbon tubes 8/6", 2 * 22.0 * tube_len * 1.55 / 1000, (230 + x_t + 40) / 2),
        ("tail block (printed)", 8.0, x_t + 10),
        ("tail surfaces 3 mm light balsa + film + hinges", (Sh + Sv) * 1e6 * 3e-3 * 85 / 1000 * 0.75 + (Sh + Sv) * 2 * 50 + 2.0, x_t + 15),
    ]
    if servos_aft:
        items += [("tail servos 2 x 9 g at the tail", 18.0, x_t - 40),
                  ("2 servo extensions 60 cm", 8.0, (230 + x_t) / 2),
                  ("short pushrods", 1.0, x_t)]
    else:
        items += [("tail servos 2 x 9 g in the pod (beside the neck)", 18.0, 215.0),
                  ("2 pushrods carbon 2 mm + steel ends + guides", 7.0, (230 + x_t) / 2)]
    return items, Sh, Sv

if __name__ == "__main__":
    print("\n=== Concept U (D-052): printed pod + twin 8/6 tubes, Vh 0.50 ===")
    print(" l_h | servos | Sh dm2 | Sv dm2 | nose group X | empty g | score")
    for l in (550, 600, 650):
        for aft in (False, True):
            items, Sh, Sv = concept_U(l, servos_aft=aft)
            xn, mn = nose_station(items)
            e = sum(m for _, m, _ in items) + mn
            print(f" {l} | {'tail' if aft else 'pod '}   | {Sh*100:5.2f}  | {Sv*100:5.2f}  | {xn:6.0f}       | {e:6.0f}  | {99600/e:5.1f}")
    items, Sh, Sv = concept_U(600)
    print("\nU breakdown (l_h 600, servos in the pod):")
    for n, m, x in items:
        print(f"  {n:48s} {m:6.1f} g  X {x:6.0f}")
    xn, mn = nose_station(items)
    print(f"  nose group (motor, prop, ESC, battery) {mn:.0f} g at X {xn:.0f}")
    print(f"  empty {sum(m for _,m,_ in items)+mn:.0f} g")


# ---------------------------------------------------------------- pod mass by area (plan 04 geometry)
# Skin areas (mm2) from the plan stations: nose X -205..-35 (56x56 -> 110x113, hatch included),
# centre X -35..200 (2 sides, floor, seat lip; top open under the wing), aft X 200..300 (taper to 60x44).
A_NOSE = 335 * 170          # mean perimeter x length
A_SIDES = 2 * 235 * 104 + 2 * 8 * 235
A_FLOOR = 235 * 110
A_AFT = 314 * 100
EXTRAS_CM3 = 15.4 + 8.3 + 3.0 + 10.0   # inner ribs at formers, floor grid, hatch rim, socket block (saddles stay in the reservoir total)
INSERTS_G = 4.5 + 3.2                   # 3 mm ply firewall, 3 mm balsa front stop (inserts in printed slots)
RHO_PRINT = {"PLA": 1.24, "LW-PLA": 0.55, "ASA Aero low": 0.53, "ASA Aero": 0.65, "ASA Aero high": 0.80}
# ASA Aero: printed density 50-75 % of ASA (Bambu product page) -> 0.53-0.80; LW-PLA 0.55 (interp.)

def pod_U(rho, wall_side, wall_floor_nose):
    v = (A_SIDES + A_AFT) * wall_side + (A_FLOOR + A_NOSE) * wall_floor_nose   # mm3
    return (v / 1000 + EXTRAS_CM3) * rho + INSERTS_G

def pod_B():
    """Balsa pod over the same 505 mm length + PETG socket block."""
    area = (A_NOSE + A_SIDES + A_FLOOR + A_AFT) / 1e6
    skin = area * 1.7e-3 * 120 * 1000 * 0.85          # 2 mm sides / 1.5 mm floor and hatch, 15 % holes
    return skin + 4.5 + 3.2 + 7.5 + 4.4 + 6.0 + area * 50 + 10.0 * 1.27

# ---------------------------------------------------------------- wing wake at the tail
def wake_z(alpha_w_deg, deps, x_tail=680.0):
    """Wake centre-line Z at x_tail (body frame). Wing at +3 deg on the datum; zero-lift alpha -4.1 deg."""
    a_f = alpha_w_deg - 3.0
    eps = deps * (alpha_w_deg + 4.1)
    return -14.65 + (x_tail - 280.0) * math.tan(math.radians(a_f - eps))

if __name__ == "__main__":
    print("\n=== Pod mass by area (plan 04 geometry, 505 mm) ===")
    print(f" skin area {(A_NOSE+A_SIDES+A_FLOOR+A_AFT)/1e6:.3f} m2")
    for label, ws, wf in (("0.45 single wall everywhere", 0.45, 0.45), ("0.5 sides, 0.8 floor + nose", 0.5, 0.8), ("0.8 everywhere", 0.8, 0.8)):
        print(" " + label + ": " + ", ".join(f"{k} {pod_U(r, ws, wf):.0f} g" for k, r in RHO_PRINT.items()))
    print(f" B balsa pod + PETG sockets: {pod_B():.0f} g")
    base = sum(m for n, m, _ in concept_U(600)[0] if not n.startswith("printed pod")) + 180.0
    print(" Empty mass (all other items as concept_U, l_h 600, nose group 180 g):")
    for label, pod in (("B", pod_B()), ("U ASA Aero 0.45", pod_U(0.65, .45, .45)), ("U ASA Aero mid", pod_U(0.65, .5, .8)),
                       ("U ASA Aero 0.8", pod_U(0.65, .8, .8)), ("U LW-PLA mid", pod_U(0.55, .5, .8)), ("U PLA mid", pod_U(1.24, .5, .8))):
        e = base + pod
        vs = 8.86 * math.sqrt((e + 996) / 1593)
        print(f"  {label:18s} pod {pod:5.0f} g  empty {e:5.0f} g  score {99600/e:5.1f}  loaded stall {vs:.2f} m/s (R6 <= 9.0)")

    print("\n=== Wing wake centre-line Z at the tail (X 680) ===")
    cases = [("loaded 10 m/s", 12.7), ("loaded 11", 9.7), ("loaded 12", 7.6), ("loaded 13", 5.9), ("loaded 15", 3.6),
             ("empty 10", 2.6), ("empty 12", 0.7), ("empty 13", 0.0), ("empty 15", -0.9), ("empty 18", -1.8), ("wing stall", 20.0)]
    print(" case            | a_wing | Z (deps 0.45) | 0.55 | 0.65")
    for n, a in cases:
        print(f" {n:15s} | {a:5.1f}  | {wake_z(a,.45):6.1f}        | {wake_z(a,.55):6.1f} | {wake_z(a,.65):6.1f}")
    # ground line at the tail for a nose-up touchdown about the aft belly corner (X 200, Z -117)
    for th in (4, 6, 8, 10):
        print(f" ground at X 680 for {th} deg nose-up on the belly corner (X 200, Z -117): Z {-117 + 480*math.tan(math.radians(th)):.0f}")
