"""Run one variant of the pod structure study: geometry -> mesh -> zones -> static load cases -> buckling sweeps ->
results (JSON) and pictures. Run with the FreeCAD Python:
    /Applications/FreeCAD.app/Contents/Resources/bin/python run_study.py <variant> [--no-buckle] [--hmax 8]
Variants: base (F-A shell + F-B members), or a variant defined in scripts/fus_struct.py (fem_variant()).
Work files go to the scratchpad (WORK env or ./_work); results and pictures to design/cad_fuselage/structure/."""
import sys
import os
import json
import time
import argparse
import concurrent.futures as cf
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pod_model as PM  # noqa: E402
import shellfem as F  # noqa: E402
import pod_post as PP  # noqa: E402
import numpy as np  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("variant")
ap.add_argument("--no-buckle", action="store_true")
ap.add_argument("--hmax", type=float, default=None)
ap.add_argument("--workers", type=int, default=8)
ap.add_argument("--cases", default="")
a = ap.parse_args()

t0 = time.time()
if a.variant == "base":
    cfg = dict(PM.BASE)
else:
    import fus_struct as FS
    cfg = FS.fem_variant(a.variant, PM)
if a.hmax:
    cfg["hmax"] = a.hmax
WORK = os.path.join(os.environ.get("WORK", os.path.join(HERE, "_work")), cfg["name"])
OUT = os.path.join(PM.STRUCT, "results", cfg["name"])
IMG = os.path.join(PM.STRUCT, "img")
os.makedirs(WORK, exist_ok=True)
os.makedirs(OUT, exist_ok=True)
os.makedirs(IMG, exist_ok=True)
log = []


def say(s):
    print(s, flush=True)
    log.append(s)


g = PM.build_geometry(cfg, WORK)
say("geometry: %d faces, skin area %.0f mm2 (%.0f s)" % (g["n_faces"], g["skin_area"], time.time() - t0))
m = F.mesh(g["brep"], WORK, cfg["name"], cfg["hmax"])
say("mesh: %d elements (%s), %d nodes (%.0f s)" % (len(m["elems"]), dict(zip(*[v.tolist() for v in np.unique(m["nn"], return_counts=True)])),
                                                   len(m["nodes"]), time.time() - t0))
ctx = PM.classify(m, cfg)
grp = PM.groups(ctx)
zones = {}
for zn in sorted(set(ctx["zone"])):
    s = ctx["zone"] == zn
    zones[zn] = dict(area=float(ctx["area"][s].sum()), t=sorted(set(np.round(ctx["t"][s], 2).tolist())),
                     vol_cm3=float((ctx["area"][s] * ctx["t"][s]).sum() / 1000))
    say("  zone %-10s area %8.0f mm2  t %-14s vol %6.2f cm3" % (zn, zones[zn]["area"], zones[zn]["t"], zones[zn]["vol_cm3"]))
mass = {k: PM.mass_g(ctx, r) for k, r in (("PLA", 1.24), ("ASA Aero 0.65", 0.65))}
say("printed mass in the model (shell + modelled members, by area x t): PLA %.1f g, ASA Aero 0.65 %.1f g" % (mass["PLA"], mass["ASA Aero 0.65"]))

cases, ns, S = PM.load_cases(m, ctx)
if a.cases:
    keep = a.cases.split(",")
    cases = [c for c in cases if c["name"] in keep]
thumbs = PM.thumb_cases(m, ctx, cfg.get("thumb_points", {
    "lip140": (140.0, 1, "lip"), "side10": (10.0, 1, -60.0), "side150": (150.0, 1, -60.0), "side205": (205.0, 1, -60.0),
    "nose100": (-100.0, 1, -60.0), "grip80": (80.0, -1, -70.0), "floor80": (80.0, 35.0, "floor"), "aft250": (250.0, 1, -55.0)}))
for c in cases:
    Fr, Mo = F.resultant(m, c["loads"], about=(80, 0, -60))
    say("  %-5s %-60s applied F %s N, M %s N mm %s" % (c["name"], c["desc"], np.round(Fr, 2), np.round(Mo, 0), c.get("info", "")))

# ---------------- static run (all cases as steps of one deck)
steps = [dict(kind="static", bc=c["bc"], loads=c["loads"], grav=c["grav"], rf_sets=c["rf"]) for c in cases + thumbs]
F.write_deck(os.path.join(WORK, "static.inp"), m, grp, PM.MATS, steps, nsets=ns)
F.run_ccx(WORK, "static", threads=4)
say("static solved (%.0f s)" % (time.time() - t0))
frd = F.read_frd(os.path.join(WORK, "static.frd"))
rf = F.read_rf(os.path.join(WORK, "static.dat"))
say("frd read (%.0f s)" % (time.time() - t0))
pr = ctx["mat"] == "PR"
res = dict(variant=cfg["name"], cfg={k: v for k, v in cfg.items() if k != "struct"}, zones=zones, mass_model_g=mass,
           n_elem=len(m["elems"]), cases={})
X, Y, Z = ctx["cen"].T
ener_env = np.zeros(len(X))
ids, xyz = F.node_array(m)
pos = {k: i for i, k in enumerate(ids)}
rf_i = 0
for k, c in enumerate(cases + thumbs, start=1):
    blk = {b["name"][:4]: b for b in frd["blocks"] if b["set"] == k}
    vm, p1, p3 = F.elem_stress(m, frd, blk["STRE"])
    d = F.disp_2d(m, frd, blk["DISP"])
    dmag = np.array([np.linalg.norm(d[n]) for n in ids])
    # elements near supports and load patches (local peaks) are reported separately
    sup = set()
    for nsn, _, _ in c["bc"]:
        sup |= set(ns[nsn])
    supxyz = xyz[[pos[n] for n in sup]] if sup else np.zeros((0, 3))
    near = np.zeros(len(X), bool)
    if len(supxyz):
        from scipy.spatial import cKDTree
        dd, _ = cKDTree(supxyz).query(ctx["cen"])
        near = dd < 8.0
    far = pr & ~near
    r = dict(desc=c["desc"], info=c.get("info", {}))
    for nm, arr, sgn in (("vm", vm, 1), ("p1", p1, 1), ("p3", p3, -1)):
        aa = sgn * arr
        i_all = int(np.argmax(np.where(pr, aa, -1e9)))
        i_far = int(np.argmax(np.where(far, aa, -1e9)))
        r[nm] = dict(max=float(aa[i_all]), at=ctx["cen"][i_all].round(1).tolist(), zone=str(ctx["zone"][i_all]),
                     max_far=float(aa[i_far]), at_far=ctx["cen"][i_far].round(1).tolist(), zone_far=str(ctx["zone"][i_far]))
    r["dmax"] = float(dmag.max())
    r["dmax_at"] = xyz[int(np.argmax(dmag))].round(1).tolist()
    if c.get("patch") is not None:
        pn = _ = None
        pn_ids = sorted(set(int(v) for v in m["elems"][c["patch"]].ravel() if v > 0))
        r["d_patch"] = float(max(np.linalg.norm(d[n]) for n in pn_ids))
    nrf = len(c.get("rf", []))
    r["reactions"] = rf[rf_i:rf_i + nrf]
    rf_i += nrf
    if "ENER" in blk:
        _, pe = F.map_to_2d(m, frd, blk["ENER"])
        en = np.array([pe[i].mean() if i in pe and len(pe[i]) else 0.0 for i in range(len(X))])
        r["energy_mJ"] = float(np.sum(en * ctx["area"] * ctx["t"]))
        if not c["name"].startswith("LC8"):
            ener_env = np.maximum(ener_env, np.where(pr, en / max(en[far].max(), 1e-30), 0))
    res["cases"][c["name"]] = r
    for mat, sg in PM.SIG.items():
        r.setdefault("util", {})[mat] = dict(z=PM.FOS * r["p1"]["max_far"] / sg["z"], xy=PM.FOS * r["vm"]["max_far"] / sg["xy"],
                                             z_peak=PM.FOS * r["p1"]["max"] / sg["z"])
    say("  %-12s vm %6.2f (far %6.2f @%s %s) p1 %6.2f (far %6.2f) p3 %6.2f  dmax %6.2f mm%s  U_ASA z %.2f xy %.2f"
        % (c["name"], r["vm"]["max"], r["vm"]["max_far"], r["vm"]["at_far"], r["vm"]["zone_far"], r["p1"]["max"], r["p1"]["max_far"],
           r["p3"]["max"], r["dmax"], (" patch %.2f" % r["d_patch"]) if "d_patch" in r else "", r["util"]["ASA Aero 0.65"]["z"],
           r["util"]["ASA Aero 0.65"]["xy"]))
    if c["name"] in ("LC1a", "LC1b", "LC2", "LC3", "LC6", "LC7a", "LC7b", "LC7c"):
        val = PM.FOS * p1 / PM.SIG["ASA Aero 0.65"]["z"]
        PP.maps(m, ctx, np.where(pr, val, np.nan), os.path.join(IMG, "%s_%s_util.png" % (cfg["name"], c["name"])),
                "%s %s: %s\nmax principal stress x 1.5 / Z allowable (ASA Aero 0.65, 5.6 MPa)" % (cfg["name"], c["name"], c["desc"]),
                vmin=0, vmax=1.0, cmap="turbo", label="utilisation (1.0 = allowable)", mask=pr)
np.save(os.path.join(OUT, "ener_env.npy"), ener_env)
PP.maps(m, ctx, np.where(pr, np.log10(np.maximum(ener_env, 1e-6)), np.nan), os.path.join(IMG, "%s_energy_envelope.png" % cfg["name"]),
        "%s: strain-energy density envelope over LC1-LC7 (each case normalised to its own maximum)" % cfg["name"],
        vmin=-4, vmax=0, cmap="magma", label="log10 (energy density / case max)", mask=pr)
PP.iso(m, ctx, ctx["t"], os.path.join(IMG, "%s_thickness_iso.png" % cfg["name"]), "%s: FEM model, shell thickness" % cfg["name"],
       vmin=0.4, vmax=2.0, cmap="viridis", label="thickness mm")
say("static post done (%.0f s)" % (time.time() - t0))
json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1)

# ---------------- buckling sweeps
if not a.no_buckle:
    jobs = []
    for c in cases:
        if not c.get("buckle"):
            continue
        for s in F.BUCKLE_SCALES:
            name = "bk_%s_%03d" % (c["name"], int(round(s * 100)))
            st = dict(kind="buckle", nmodes=8, bc=c["bc"], loads=F.scale_loads(c["loads"], s),
                      grav=(c["grav"][0] * s, c["grav"][1]) if c["grav"] else None)
            F.write_deck(os.path.join(WORK, name + ".inp"), m, grp, PM.MATS, [st], nsets=ns)
            jobs.append((c["name"], s, name))

    def one(j):
        cn, s, name = j
        try:
            F.run_ccx(WORK, name, threads=1, timeout=3600)
            f = F.read_buckle(os.path.join(WORK, name + ".dat"))
            return cn, s, name, (f[0] if f else [])
        except Exception as e:  # noqa: BLE001
            return cn, s, name, "ERR " + str(e)[:300]
    found = {}
    with cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
        for cn, s, name, f in ex.map(one, jobs):
            if isinstance(f, str):
                say("  buckle %s s %.2f: %s" % (cn, s, f))
                continue
            for mi, v in enumerate(f):
                if v > 0:
                    found.setdefault(cn, []).append((v * s, s, name, mi))
    say("buckling sweeps done (%.0f s)" % (time.time() - t0))
    for cn, lst in found.items():
        lst.sort()
        lam, s, name, mi = lst[0]
        res["cases"][cn]["buckle"] = dict(lam=lam, next=[round(v[0], 3) for v in lst[1:6]], job=name, mode=mi)
        fr = F.read_frd(os.path.join(WORK, name + ".frd"))
        dbl = [b for b in fr["blocks"] if b["name"].startswith("DISP")]
        dm = F.disp_2d(m, fr, dbl[mi])
        amp = np.array([np.linalg.norm(dm.get(n, np.zeros(3))) for n in ids])
        res["cases"][cn]["buckle"]["at"] = xyz[int(np.argmax(amp))].round(1).tolist()
        eamp = np.array([max(np.linalg.norm(dm.get(int(v), np.zeros(3))) for v in m["elems"][i] if v > 0) for i in range(len(X))])
        say("  %-5s buckling factor (limit load, E %.0f MPa) %.3f at %s ; next %s"
            % (cn, PM.E_ASA, lam, res["cases"][cn]["buckle"]["at"], res["cases"][cn]["buckle"]["next"]))
        PP.maps(m, ctx, eamp / max(eamp.max(), 1e-30), os.path.join(IMG, "%s_%s_buckle.png" % (cfg["name"], cn)),
                "%s %s: first buckling mode, factor %.2f at limit load (ASA Aero 0.65, E %.0f MPa)" % (cfg["name"], cn, lam, PM.E_ASA),
                vmin=0, vmax=1, cmap="inferno", label="mode amplitude (normalised)")
    json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1)
open(os.path.join(OUT, "run.log"), "w").write("\n".join(log) + "\n")
say("DONE %.0f s" % (time.time() - t0))
