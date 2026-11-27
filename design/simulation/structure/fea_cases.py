"""P6: FEA case files for SOLIDWORKS Simulation (run_fea.ps1 / SwFea.cs), written from the rev B part data and the
cited material data (design/optimisation/references.md). Plain Python:
    python design/simulation/structure/fea_cases.py [--mass-empty g]     -> cases/<name>.json
Units mm, N, MPa in this file (converted to SI in the JSON). Model axes for every case: sketch on the Front plane,
u -> X, v -> Y, extrusion -> +Z.

Materials (design values, R1 = USDA Wood Handbook FPL-GTR-190):
- balsa, rho_d 0.12 g/cm3: E_L = 3400 x 0.12/0.16 = 2550 MPa (R1 Table 5-5a, linear in density); E_T/E_L 0.015,
  E_R/E_L 0.046, G_LR/E_L 0.054, G_LT/E_L 0.037, G_RT/E_L 0.005 (R1 Table 5-1); nu_LR 0.229, nu_LT 0.488, nu_RT 0.665,
  nu_TR 0.231, nu_RL 0.018, nu_TL 0.009 (R1 Table 5-2);
- birch ply veneer (paper birch proxy): E_L 11 000 MPa (R1 Table 5-3a), yellow-birch ratios E_T/E_L 0.050,
  E_R/E_L 0.078, G_LR/E_L 0.074, G_LT/E_L 0.068, G_RT/E_L 0.017 (R1 Table 5-1);
- carbon pultruded strip: E 28 GPa (Easy Composites TDS lower bound, R3), isotropic.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.dirname(os.path.dirname(HERE))
for p in ("cad_fuselage_balsa/scripts", "cad_fuselage/scripts", "cad_reservoir/scripts", "cad/scripts", "cad_fusion_revB/scripts"):
    sys.path.insert(0, os.path.join(DESIGN, p))
CASES = os.path.join(HERE, "cases")
G = 9.81
EL_B = 3400.0 * 0.12 / 0.16                   # MPa
EL_H = 11000.0


def ortho(name, axes, EL, r, rho):
    """orthotropic material with the L, R, T directions on the model axes given as a string like 'TRL' (x, y, z)."""
    E = {"L": EL, "R": r["ER"] * EL, "T": r["ET"] * EL}
    Gm = {"LR": r["GLR"] * EL, "LT": r["GLT"] * EL, "RT": r["GRT"] * EL}
    nu = r["nu"]                                       # nu[ij] = -e_j / e_i for stress in i
    g = lambda a, b: Gm.get(a + b, Gm.get(b + a))
    x, y, z = axes
    return dict(name=name, model="ortho", EX=E[x] * 1e6, EY=E[y] * 1e6, EZ=E[z] * 1e6,
                NUXY=nu[x + y], NUYZ=nu[y + z], NUXZ=nu[x + z],
                GXY=g(x, y) * 1e6, GYZ=g(y, z) * 1e6, GXZ=g(x, z) * 1e6, rho=rho)


BALSA = dict(ER=0.046, ET=0.015, GLR=0.054, GLT=0.037, GRT=0.005,
             nu={"LR": 0.229, "LT": 0.488, "RT": 0.665, "TR": 0.231, "RL": 0.018, "TL": 0.009})
BIRCH = dict(ER=0.078, ET=0.050, GLR=0.074, GLT=0.068, GRT=0.017,
             nu={"LR": 0.426, "LT": 0.451, "RT": 0.697, "TR": 0.426, "RL": 0.043, "TL": 0.024})   # R1 Table 5-2, yellow birch
CARBON = dict(name="carbon strip (TDS lower bound)", model="iso", E=28.0e9, nu=0.3, rho=1400.0)


def rect(u0, u1, v0, v1):
    return [[u0, v0], [u1, v0], [u1, v1], [u0, v1]]


def write(case):
    os.makedirs(CASES, exist_ok=True)
    case["part"] = os.path.join(CASES, case["name"] + ".SLDPRT")
    for b in case["bodies"]:
        b["loops"] = [[[u, v] for u, v in loop] for loop in b["loops"]]
    json.dump(case, open(os.path.join(CASES, case["name"] + ".json"), "w"), indent=1)
    print("case", case["name"], len(case["bodies"]), "bodies")


def spar(mass_kg, n=6.0, size=2.0):
    """Half-wing spar (caps, webs, root-bay doubler) as a cantilever from the root rib, the n = 6 ultimate lift as a
    uniform normal force pushing up on the underside of the bottom cap (root moment 0.5 W L: conservative against the near-elliptic lift, 0.42 W L).
    D-box skins, LE and ribs are left out (they also carry bending): conservative for the cap stresses."""
    import wing as W
    P = W.P
    X0, X1 = P.X_SPAR
    ZT, ZB = W.ZT, W.ZB
    tc, tb = P.CAP_CARBON_T, P.CAP_BALSA_T
    L = P.Y_END
    wf, wr = W.WF_X, W.WR_X
    zlf, zuf = W.rng(W.zl_in, *wf, mode=max), W.rng(W.zu_in, *wf, mode=min)
    zlr, zur = W.rng(W.zl_in, *wr, mode=max), W.rng(W.zu_in, *wr, mode=min)
    xd = (wf[0] - P.WEB_T, wf[0])
    zld, zud = W.rng(W.zl_in, *xd, mode=max), W.rng(W.zu_in, *xd, mode=min)
    cap = ortho("balsa cap (grain span)", "TRL", EL_B, BALSA, 120.0)
    web = ortho("balsa web (grain vertical)", "RLT", EL_B, BALSA, 120.0)
    bodies = [
        dict(name="CAP-C-TOP", loops=[rect(X0, X1, ZT - tc, ZT)], depth=L, material=CARBON),
        dict(name="CAP-B-TOP", loops=[rect(X0, X1, ZT - tb - tc, ZT - tc)], depth=L, material=cap),
        dict(name="CAP-C-BOT", loops=[rect(X0, X1, ZB, ZB + tc)], depth=L, material=CARBON),
        dict(name="CAP-B-BOT", loops=[rect(X0, X1, ZB + tc, ZB + tc + tb)], depth=L, material=cap),
        dict(name="WEB-F", loops=[rect(wf[0], wf[1], zlf, zuf)], depth=L, material=web),
        dict(name="WEB-R", loops=[rect(wr[0], wr[1], zlr, zur)], depth=P.REAR_WEB_Y, material=web),
        dict(name="WEB-F1D", loops=[rect(xd[0], xd[1], zld, zud)], depth=55.0 - 0.75, z0=1.5, material=web),
    ]
    W_N = n * mass_kg * G / 2.0
    case = dict(name="spar_n6", bodies=bodies,
                fixtures=[dict(faces=[{"body": "*", "at": [2, 0.0]}])],
                loads=[dict(total_N=W_N, faces=[{"body": "CAP-C-BOT", "extreme": [1, "min"]}])],   # lift: pushes up on the underside
                mesh=dict(size=size / 1000.0 * 1000.0),
                probes=[dict(label="carbon top cap SZ (MPa)", kind="stress", component=2, faces=[{"body": "CAP-C-TOP", "all": 1}]),
                        dict(label="carbon bottom cap SZ (MPa)", kind="stress", component=2, faces=[{"body": "CAP-C-BOT", "all": 1}]),
                        dict(label="balsa top cap SZ (MPa)", kind="stress", component=2, faces=[{"body": "CAP-B-TOP", "all": 1}]),
                        dict(label="balsa bottom cap SZ (MPa)", kind="stress", component=2, faces=[{"body": "CAP-B-BOT", "all": 1}]),
                        dict(label="front web TYZ (MPa)", kind="stress", component=5, faces=[{"body": "WEB-F", "all": 1}]),
                        dict(label="tip UY (mm)", kind="disp", component=1, faces=[{"body": "CAP-C-TOP", "at": [2, L]}])],
                hand=dict(load_N=W_N, L_mm=L, root_moment_Nmm=W_N * L / 2.0, note="uniform load, cantilever"))
    write(case)
    return case


def wingbox(mass_kg, n=6.0, size=2.0, zsplit=50.0):
    """The half-wing box: spar caps (split at zsplit so the probes read the beam region, clear of the clamped root),
    webs, root-bay doubler, D-box skins and LE (closed section: carries the torsion, as built). Ribs left out.
    Lift n x loaded weight / 2 as a uniform upward force on the underside of the bottom carbon cap."""
    import wing as W
    P = W.P
    X0, X1 = P.X_SPAR
    ZT, ZB = W.ZT, W.ZB
    tc, tb = P.CAP_CARBON_T, P.CAP_BALSA_T
    L = P.Y_END
    wf, wr = W.WF_X, W.WR_X
    xd = (wf[0] - P.WEB_T, wf[0])
    rz = lambda f, a, b, m: W.rng(f, a, b, mode=m)
    cap = ortho("balsa (grain span)", "TRL", EL_B, BALSA, 120.0)
    web = ortho("balsa web (grain vertical)", "RLT", EL_B, BALSA, 120.0)
    caps = [("CAP-C-TOP", rect(X0, X1, ZT - tc, ZT), CARBON), ("CAP-B-TOP", rect(X0, X1, ZT - tb - tc, ZT - tc), cap),
            ("CAP-C-BOT", rect(X0, X1, ZB, ZB + tc), CARBON), ("CAP-B-BOT", rect(X0, X1, ZB + tc, ZB + tc + tb), cap)]
    bodies = []
    for nm, loop, mat in caps:
        bodies.append(dict(name=nm + "-ROOT", loops=[loop], depth=zsplit, material=mat))
        bodies.append(dict(name=nm, loops=[loop], depth=L - zsplit, z0=zsplit, material=mat))
    bodies += [
        dict(name="WEB-F", loops=[rect(wf[0], wf[1], rz(W.zl_in, *wf, max), rz(W.zu_in, *wf, min))], depth=L, material=web),
        dict(name="WEB-R", loops=[rect(wr[0], wr[1], rz(W.zl_in, *wr, max), rz(W.zu_in, *wr, min))], depth=P.REAR_WEB_Y, material=web),
        dict(name="WEB-F1D", loops=[rect(xd[0], xd[1], rz(W.zl_in, *xd, max), rz(W.zu_in, *xd, min))], depth=55.0 - 0.75, z0=1.5, material=web),
        dict(name="DBOX-TOP-ROOT", loops=[W.skin_band(P.X_LE, P.X_DBOX, True)], depth=zsplit, material=cap),
        dict(name="DBOX-TOP", loops=[W.skin_band(P.X_LE, P.X_DBOX, True)], depth=L - zsplit, z0=zsplit, material=cap),
        dict(name="DBOX-BOT-ROOT", loops=[W.skin_band(P.X_LE, P.X_DBOX, False)], depth=zsplit, material=cap),
        dict(name="DBOX-BOT", loops=[W.skin_band(P.X_LE, P.X_DBOX, False)], depth=L - zsplit, z0=zsplit, material=cap),
        dict(name="LE", loops=[W.outer_clip(0.0, P.X_LE)], depth=L, material=cap)]
    W_N = n * mass_kg * G / 2.0
    pr = lambda label, kind, comp, body, rule: dict(label=label, kind=kind, component=comp, faces=[dict(body=body, **rule)])
    case = dict(name="wingbox_n6", bodies=bodies,
                fixtures=[dict(faces=[{"body": "*", "at": [2, 0.0]}])],
                loads=[dict(total_N=W_N, faces=[{"body": "CAP-C-BOT", "extreme": [1, "min"]}, {"body": "CAP-C-BOT-ROOT", "extreme": [1, "min"]}])],
                mesh=dict(size=size),
                probes=[pr("carbon top cap SZ, z > %g (MPa)" % zsplit, "stress", 2, "CAP-C-TOP", {"all": 1}),
                        pr("carbon bottom cap SZ, z > %g (MPa)" % zsplit, "stress", 2, "CAP-C-BOT", {"all": 1}),
                        pr("balsa top cap SZ, z > %g (MPa)" % zsplit, "stress", 2, "CAP-B-TOP", {"all": 1}),
                        pr("D-box top skin SZ, z > %g (MPa)" % zsplit, "stress", 2, "DBOX-TOP", {"all": 1}),
                        pr("D-box top skin SZ, root segment (MPa)", "stress", 2, "DBOX-TOP-ROOT", {"all": 1}),
                        pr("balsa top cap SZ, root segment (MPa)", "stress", 2, "CAP-B-TOP-ROOT", {"all": 1}),
                        pr("carbon top cap SZ, root segment (MPa)", "stress", 2, "CAP-C-TOP-ROOT", {"all": 1}),
                        pr("front web TYZ (MPa)", "stress", 5, "WEB-F", {"all": 1}),
                        pr("tip UY, carbon top (mm)", "disp", 1, "CAP-C-TOP", {"at": [2, L]}),
                        pr("tip UY, LE (mm)", "disp", 1, "LE", {"at": [2, L]})],
                hand=dict(load_N=W_N, L_mm=L, root_moment_Nmm=W_N * L / 2.0,
                          moment_at_split_Nmm=W_N / L * (L - zsplit) ** 2 / 2.0, note="uniform load, cantilever"))
    write(case)
    return case


def circle(cx, cy, r, n=96):
    return [[cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)] for k in range(n)]


def fillet(poly, r, min_turn=20.0, n=6):
    """round every corner of a closed polygon that turns by more than min_turn degrees with radius r (tangent arc of
    n segments); corners whose edges are too short for the radius get the largest radius that fits."""
    P = [(float(a), float(b)) for a, b in poly]
    m = len(P)
    out = []
    for i in range(m):
        p0, p1, p2 = P[i - 1], P[i], P[(i + 1) % m]
        ax, ay = p0[0] - p1[0], p0[1] - p1[1]
        bx, by = p2[0] - p1[0], p2[1] - p1[1]
        la, lb = math.hypot(ax, ay), math.hypot(bx, by)
        if la < 1e-9 or lb < 1e-9:
            continue
        ax, ay, bx, by = ax / la, ay / la, bx / lb, by / lb
        cosang = max(-1.0, min(1.0, ax * bx + ay * by))
        ang = math.acos(cosang)                      # interior angle between the edges
        if math.degrees(math.pi - ang) < min_turn:
            out.append(list(p1))
            continue
        t = math.tan(ang / 2.0)
        d = min(r / t, 0.45 * la, 0.45 * lb)
        rr = d * t
        s1 = (p1[0] + ax * d, p1[1] + ay * d)
        s2 = (p1[0] + bx * d, p1[1] + by * d)
        hx, hy = ax + bx, ay + by
        hl = math.hypot(hx, hy)
        c = (p1[0] + hx / hl * rr / math.sin(ang / 2.0), p1[1] + hy / hl * rr / math.sin(ang / 2.0))
        a1, a2 = math.atan2(s1[1] - c[1], s1[0] - c[0]), math.atan2(s2[1] - c[1], s2[0] - c[0])
        da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        for k in range(n + 1):
            a = a1 + da * k / n
            out.append([c[0] + rr * math.cos(a), c[1] + rr * math.sin(a)])
    return out


R_CORNER = 2.0


def front_stop(size=0.75, sheets=2):
    """Front stop FS, the nose-in landing (D-064 LC2: 10 g on the reservoir + water 1.035 kg, x 1.5 ultimate = 152 N).
    The plate as built: 2 sheets of 1.5 birch ply with crossed face grain (veneers 0/90/0 + 90/0/90), outline,
    D50 hole and the 4 windows from the pod part data (14 mm spokes). Fixed on its edge faces (glued and tabbed into the
    sides, floor and hatch frame). The bottle base bears on the ring r 25 ... 42: a 0.5 mm soft pad on that ring takes
    the load (spreads it like the bottle base; its stiffness is negligible)."""
    import pod as POD
    p = [q for q in POD.all_parts()[0] if q["name"] == "FS"][0]
    zc = POD.RP.AXIS_Z
    holes = []
    for c in p["cutters"]:
        if isinstance(c, tuple) and c[0] == "circle":
            holes.append(circle(c[1], c[2], c[3]))
        else:
            holes.append([[u, v] for u, v in c])
    outline = [[u, v] for u, v in p["outline"]]
    import geo as GEO
    inside = lambda h: all(GEO.point_in_poly((u, v), outline) for u, v in h)
    dropped = [h for h in holes if not inside(h)]
    holes = [h for h in holes if inside(h)]       # the 2 keel notches at the bottom corners cross the edge: left solid
    if dropped:
        print("front stop: %d edge notches left solid (at the fixed edge, far from the spokes)" % len(dropped))
    u0, u1 = min(q[0] for q in outline), max(q[0] for q in outline)
    v0, v1 = min(q[1] for q in outline), max(q[1] for q in outline)
    # each 1.5 mm sheet (veneers 0/90/0, 0.5 mm each) as one orthotropic layer with its bending stiffness:
    # E_face = (26 E_L + E_T) / 27, E_cross = (26 E_T + E_L) / 27 (outer veneers 26/27 of the section's I);
    # in-plane Poisson 0.05 and the through-thickness shear moduli (mean of G_LR and G_RT) are estimates
    ET, Ef = BIRCH["ET"] * EL_H, None
    Ef, Ec = (26 * EL_H + ET) / 27.0, (26 * ET + EL_H) / 27.0
    Gp, Gt, Ez = BIRCH["GLT"] * EL_H, 0.5 * (BIRCH["GLR"] + BIRCH["GRT"]) * EL_H, BIRCH["ER"] * EL_H
    sheet = lambda name, ex, ey: dict(name=name, model="ortho", EX=ex * 1e6, EY=ey * 1e6, EZ=Ez * 1e6, NUXY=0.05,
                                      NUYZ=0.43, NUXZ=0.43, GXY=Gp * 1e6, GYZ=Gt * 1e6, GXZ=Gt * 1e6, rho=650.0)
    holes = [h[::2] if len(h) > 60 else h for h in holes]                 # 48-sided D50 hole: fewer faces
    holes = [h if len(h) == 48 else fillet(h, R_CORNER) for h in holes]   # window corners r 2 (proposed); D50 hole as is
    mats = [sheet("birch sheet, face grain X", Ef, Ec), sheet("birch sheet, face grain Y", Ec, Ef)]
    bodies = [dict(name="FS-S%d" % (k + 1), loops=[outline] + holes, depth=1.5, z0=1.5 * k,
                   material=mats[k % 2 if sheets == 2 else (k + 1) % 2])          # 3 sheets: Y / X / Y (outer grain along the loaded spokes)
              for k in range(sheets)]
    T = 1.5 * sheets
    pad = dict(name="iso", model="iso", E=100.0e6, nu=0.3, rho=100.0)
    pad["name"] = "soft pad (load spreader)"
    bodies.append(dict(name="PAD", loops=[circle(0.0, zc, 42.0), circle(0.0, zc, 25.0)], depth=0.5, z0=T, material=pad))
    m_res = 0.996 + 0.0387
    Wu = 1.5 * 10.0 * G * m_res
    # glued edge: every outline face (tab ends and the edge between the tabs), not only the outermost ones
    fix = [{"body": "FS-S%d" % (k + 1), "at": [ax, v]} for k in range(sheets)
           for ax, v in sorted(set([(0, q[0]) for q in outline] + [(1, q[1]) for q in outline]))]
    # outer faces: z 0 (sheet 1, face veneer grain X) and z 3 (sheet 2, face veneer grain Y); stresses in the sheet
    # layer, turned into veneer stresses by margins.py (same strain: sigma_veneer = sigma_sheet E_veneer / E_sheet)
    probes = [dict(label="S1 face z 0, SX (MPa)", kind="stress", component=0, faces=[{"body": "FS-S1", "at": [2, 0.0]}]),
              dict(label="S1 face z 0, SY (MPa)", kind="stress", component=1, faces=[{"body": "FS-S1", "at": [2, 0.0]}]),
              dict(label="S%d face z %g, SX (MPa)" % (sheets, T), kind="stress", component=0, faces=[{"body": "FS-S%d" % sheets, "at": [2, T]}]),
              dict(label="S%d face z %g, SY (MPa)" % (sheets, T), kind="stress", component=1, faces=[{"body": "FS-S%d" % sheets, "at": [2, T]}])]
    probes.append(dict(label="ring UZ (mm)", kind="disp", component=2, faces=[{"body": "PAD", "at": [2, T + 0.5]}]))
    case = dict(name="front_stop_nose_in" + ("" if sheets == 2 else "_%dsheet" % sheets), bodies=bodies, fixtures=[dict(faces=fix)],
                loads=[dict(total_N=Wu, faces=[{"body": "PAD", "at": [2, T + 0.5]}])], mesh=dict(size=size),
                probes=probes,
                hand=dict(load_N=Wu, spoke_stress_MPa=(Wu / 4 * 7.5) / (14 * T ** 2 / 6), sheets=sheets,
                          margin_P2=1.57, f_along_MPa=85 * (1 - 1.645 * 0.16), f_across_MPa=0.04 * 85 * (1 - 1.645 * 0.16),
                          E_L=EL_H, E_T=ET, E_face=Ef, E_cross=Ec,
                          note="P2: spoke = cantilever W/4 at 7.5 mm, layered-section first-ply allowable"))
    write(case)
    return case


def grip_panel(kind="grip", size=0.75, support="clamped"):
    """Pod side panel between formers B1 and B2 (67 x 95 mm) under a finger squeeze (P2 LC3: 15 x 15 mm patch, 30 N
    ultimate). kind 'grip': outer balsa 1.5 (grain X) + birch 1.5 (veneers 90/0/90, face grain vertical); kind 'side':
    outer balsa 1.5 (grain X) + inner balsa 1.5 (grain vertical). Edges clamped (the formers, keel and longeron hold
    them; P2 used simply supported edges, so P2 is the conservative bound and this case the stiff one). The finger
    presses on the outer face through a 0.5 mm soft pad.
    support 'frame': instead of clamped edge faces, the panel is bonded onto 1.5 mm wide, 4.5 mm deep balsa strips
    round its edge (the former, keel and longeron glue lands), fixed at their far face. The narrow strips let the edge
    rotate, as a side panel does over a thin former when only one bay is pressed: close to simply supported."""
    A, B = 67.0, 95.0
    bx = ortho("balsa, grain X", "LTR", EL_B, BALSA, 120.0)
    by = ortho("balsa, grain Y", "TLR", EL_B, BALSA, 120.0)
    hx = ortho("birch veneer, grain X", "LTR", EL_H, BIRCH, 650.0)
    hy = ortho("birch veneer, grain Y", "TLR", EL_H, BIRCH, 650.0)
    if kind == "grip":
        lay = [("IN-V1", 0.5, hy, 90, "birch"), ("IN-V2", 0.5, hx, 0, "birch"), ("IN-V3", 0.5, hy, 90, "birch")]
    else:
        lay = [("IN", 1.5, by, 90, "balsa")]
    lay.append(("OUT", 1.5, bx, 0, "balsa"))
    bodies, z = [], 0.0
    for nm, t, mat, a, w in lay:
        bodies.append(dict(name=nm, loops=[rect(0.0, A, 0.0, B)], depth=t, z0=z, material=mat))
        z += t
    pad = dict(name="soft pad (finger)", model="iso", E=100.0e6, nu=0.3, rho=100.0)
    bodies.append(dict(name="PAD", loops=[rect(A / 2 - 7.5, A / 2 + 7.5, B / 2 - 7.5, B / 2 + 7.5)], depth=0.5, z0=z, material=pad))
    fix = [{"body": "*", "at": [0, 0.0]}, {"body": "*", "at": [0, A]}, {"body": "*", "at": [1, 0.0]}, {"body": "*", "at": [1, B]}]
    if support == "frame":
        sv = ortho("balsa strip, grain Y", "TLR", EL_B, BALSA, 120.0)
        su = ortho("balsa strip, grain X", "LTR", EL_B, BALSA, 120.0)
        w, d = 1.5, 4.5
        for nm, loop, mat in (("SUP-U0", rect(0.0, w, 0.0, B), sv), ("SUP-U1", rect(A - w, A, 0.0, B), sv),
                              ("SUP-V0", rect(w, A - w, 0.0, w), su), ("SUP-V1", rect(w, A - w, B - w, B), su)):
            bodies.append(dict(name=nm, loops=[loop], depth=d, z0=-d, material=mat))
        fix = [{"body": "*", "at": [2, -d]}]
    probes = []
    for nm, t, mat, a, w in lay:
        along, across = (0, 1) if a == 0 else (1, 0)
        probes.append(dict(label="%s (%s, %d deg) stress along grain (MPa)" % (nm, w, a), kind="stress", component=along,
                           faces=[{"body": nm, "all": 1}]))
        probes.append(dict(label="%s (%s, %d deg) stress across grain (MPa)" % (nm, w, a), kind="stress", component=across,
                           faces=[{"body": nm, "all": 1}]))
    probes.append(dict(label="centre UZ (mm)", kind="disp", component=2, faces=[{"body": "PAD", "at": [2, z + 0.5]}]))
    p5 = lambda cov: 1 - 1.645 * cov
    case = dict(name="side_panel_%s%s" % (kind, "_frame" if support == "frame" else ""), bodies=bodies, fixtures=[dict(faces=fix)],
                loads=[dict(total_N=30.0, faces=[{"body": "PAD", "at": [2, z + 0.5]}])], mesh=dict(size=size),
                probes=probes,
                hand=dict(load_N=30.0, margin_P2=2.09 if kind == "grip" else 1.28,
                          deflection_P2_mm=0.4 if kind == "grip" else 1.0,
                          balsa_f_along_MPa=21.6 * 0.75 * p5(0.16), balsa_f_across_MPa=0.04 * 21.6 * 0.75 * p5(0.16),
                          birch_f_along_MPa=85 * p5(0.16), birch_f_across_MPa=0.04 * 85 * p5(0.16),
                          note="P2: Navier, simply supported, first-ply failure"))
    write(case)
    return case


def main():
    a = sys.argv
    empty = float(a[a.index("--mass-empty") + 1]) if "--mass-empty" in a else 708.0
    m = (empty + 996.0) / 1000.0
    spar(m)
    c = wingbox(m, size=2.5)                           # 2.5 mm mesh: convergence check
    c["name"] = "wingbox_n6_h25"
    c["images"] = False
    write(c)
    wingbox(m)                                         # 2.0 mm mesh (reported); written last
    front_stop()
    # side panels: secondary parts, covered by the P2 hand calcs (grip_panel() kept for a later check)


if __name__ == "__main__":
    main()
