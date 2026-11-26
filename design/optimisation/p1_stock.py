"""P1 single-stock study: mass, lamination schedule and sheets to buy for each candidate single balsa stock.

Every balsa part of the rev B Fusion model is re-made from ONE balsa stock (thickness s, generic medium grade);
the ply verdict of P1_single_stock.m replaces most lite-ply parts by cross-laminated balsa. Reads p1_parts.csv
(written by p1_parts.py) and the strip sections from tools/build_kit/kit_data.py. Plain Python:
    python design/optimisation/p1_stock.py
Writes p1_schedule_<s>.csv (per part) and p1_summary.csv, and prints the summary.

Assumptions (see P1_single_stock.md section 3; every one is an input below):
  RHO_BALSA   0.14 g/cm3 for every balsa part (generic local medium stock, user rule 2026-11-26)
  GLUE_LAM    dry glue per lamination interface, g/m2  (ESTIMATE - weigh a 100 x 100 test laminate)
  ETA_LASER   nesting efficiency of laser parts on 100 x 300 sheets (ESTIMATE; today's nesting is 39 %)
  ETA_STRIP   use of a 100 x 1000 sheet when strips are cut from it (ESTIMATE)
  SPARE       extra sheets for bad grain / heavy sheets (MATERIALS.md: 10-20 %)
"""
import csv
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools", "build_kit"))
import kit_data as K  # noqa: E402

RHO_BALSA = 0.14
RHO_TODAY = {"balsa_med": 0.14, "balsa_light": 0.10, "balsa_hard": 0.16, "ply": 0.65, "liteply": 0.45}
GLUE_LAM = 40.0
GLUE_RANGE = (20.0, 80.0)
ETA_LASER, ETA_STRIP, SPARE = 0.55, 0.85, 0.15
SHEET_M2 = 0.1                       # 100 x 1000 mm
STOCKS = [1.0, 1.5, 2.0, 3.0]
EMPTY_TODAY, WATER = 721.0, 996.0    # mass_table.md
POD_GLUE_FRAC = 0.10                 # mass_summary.py: pod glue 10 % of the wood

# ---- ply verdict (P1_single_stock.m): lite-ply parts that become cross-laminated balsa, and the minimum thickness
TO_BALSA = {  # name prefix: (min thickness mm, min layers, reason)
    "N1": (4.5, 3, "former: U-frame leg check margin 1.9 at 0/90/0 4.5 mm"),
    "N2": (4.5, 3, "former"), "B1": (4.5, 3, "former"), "B2-": (4.5, 3, "former"), "B4": (4.5, 3, "former"),
    "EF": (4.5, 3, "end former (with birch tube rings TR2)"),
    "BH": (6.0, 4, "bulkhead 4 x 1.5 X-lam with birch tube rings TR1: bearing margins >= 2.8"),
    "S1a": (3.0, 2, "saddle face: bottle bearing margin 62"), "S1d": (3.0, 2, "saddle face"),
    "S2a": (3.0, 2, "saddle face"), "S2d": (3.0, 2, "saddle face"),
    "S1B": (3.0, 2, "strap bridge"), "S2B": (3.0, 2, "strap bridge"),
    "TST": (3.0, 2, "tail-servo tray (judgement: CA-hardened screw holes)"),
    "TRAY": (3.0, 2, "battery tray (judgement)"),
}
KEEP_PLY = {"FS": "front stop: balsa fails the spoke check in both directions (P2 FEA decides lite-ply 3 vs birch 2 x 1.5)",
            "FW": "firewall: screw clamp crushes balsa across the grain", "SD-": "stub doubler: band stub bearing",
            "TR": "boom tube rings (bearing)", "RO-MP": "grip / servo zone (hand launch)", "RI-M": "grip zone inner",
            "LI-M": "grip zone inner", "FLAPSTOP": "flap stop (water load)", "SK": "skids (landing wear)",
            "HORN": "tail horns"}
NOT_PRIMARY_THIN = ("W-R055", "W-R165", "W-R220", "W-R275", "W-R330", "W-R385", "W-R440", "A1", "A2", "A3", "A4",
                    "CAPS-", "HN", "HF", "HA", "DECK", "ELEV", "RUDDER", "W-TIP")


def pre(name, table):
    best = None
    for p in table:
        if name.startswith(p) and (best is None or len(p) > len(best)):
            best = p
    return best


def layers(t, s, thin_ok):
    """number of layers of stock s for a part of thickness t."""
    n = max(1, math.floor(t / s + 0.5))
    if n * s < t - 0.01 and not thin_ok:
        n += 1
    if thin_ok and n > 1 and (n - 1) * s >= 0.66 * t:
        n -= 1
    return n


_REG = []


def registry():
    if not _REG:
        _REG.append(K.build_registry())
    return _REG[0]


def run(s, glue=GLUE_LAM):
    R = registry()
    rows = list(csv.DictReader(open(os.path.join(HERE, "p1_parts.csv"), encoding="utf-8")))
    out = []
    for r in rows:
        n_, mat, kind, t = r["name"], r["mat"], r["kind"], float(r["t_mm"])
        m0 = float(r["mass_g"])
        area = float(r["area_cm2"]) / 1e4                      # m2, one face (laser parts / sheet strips)
        rec = dict(name=n_, assembly=r["assembly"], mat_today=mat, t_today=t, mass_today=m0, kind=kind)
        if mat in ("ply", "liteply"):
            k = pre(n_, TO_BALSA)
            if k:
                tmin, nmin, why = TO_BALSA[k]
                n = max(nmin, math.ceil(tmin / s - 1e-6))
                if s >= 3.0:
                    n = max(2, n)                              # keep it cross-laminated
                rec.update(new="balsa %d x %.1f X-lam" % (n, s), t_new=n * s, n=n,
                           mass_wood=area * n * s * RHO_BALSA * 1e3, glue_m2=area * (n - 1), sheet_m2=area * n / ETA_LASER,
                           note=why)
            else:
                k2 = pre(n_, KEEP_PLY)
                rec.update(new="keep " + mat, t_new=t, n=1, mass_wood=m0, glue_m2=0.0, sheet_m2=0.0,
                           note=KEEP_PLY.get(k2, "keep"))
            out.append(rec)
            continue
        # ---------------- balsa parts ----------------
        thin_ok = n_.startswith(NOT_PRIMARY_THIN) or r["load"] in ("S", "L")
        if kind == "laser":
            n = layers(t, s, thin_ok)
            tn = n * s
            rec.update(new="%d x %.1f" % (n, s), t_new=tn, n=n, mass_wood=area * tn * RHO_BALSA * 1e3,
                       glue_m2=area * (n - 1), sheet_m2=area * n / ETA_LASER,
                       note="thinner (check)" if tn < t - 0.01 else ("thicker" if tn > t + 0.01 else ""))
        else:
            e = R[n_]
            desc, th, w, L = K.strip_dims(n_, e)
            L /= 1e3
            vol_ratio = RHO_BALSA / RHO_TODAY[mat]              # flown volume kept, density changes
            if n_.startswith("Longeron"):
                nl = layers(1.5, s, False)
                tl = nl * s
                a_new = tl * 6 + tl * (6 - tl)                   # L of two legs 6 mm, mm2
                a_old = 0.5 * 6 * 6
                rec.update(new="L-section 2 legs %d x %.1f" % (nl, s), t_new=tl, n=nl,
                           mass_wood=m0 * vol_ratio * a_new / a_old, glue_m2=(nl - 1) * 2 * 6 * L / 1e3 + tl * L / 1e3,
                           sheet_m2=nl * (6 + 6 - tl + 2) * L / 1e3 / ETA_STRIP, note="L instead of triangle")
            elif n_.startswith(("DBOX", "CS-", "CAPS-")):
                n = layers(t, s, thin_ok)
                tn = n * s
                rec.update(new="%d x %.1f sheet" % (n, s), t_new=tn, n=n, mass_wood=area * tn * RHO_BALSA * 1e3,
                           glue_m2=area * (n - 1), sheet_m2=area * n / ETA_STRIP,
                           note=("NOT FEASIBLE: 3 mm will not wrap the LE" if (n_.startswith("DBOX") and tn >= 3.0) else
                                 ("thinner (check)" if tn < t - 0.01 else ("thicker: +mass" if tn > t + 0.01 else ""))))
            else:
                th_l = max(th, w) if n_.startswith(("TE-", "AIL-TE")) else th
                th_lam = min(th, w) if n_.startswith(("TE-", "AIL-TE")) else th
                wid = max(th, w) if n_.startswith(("TE-", "AIL-TE")) else w
                n = math.ceil(th_lam / s - 1e-6)
                if n_ == "LE":
                    wid = 16.3
                if n_.startswith(("TE-", "AIL-TE")):          # staggered strips sanded to the wedge
                    widths = [wid * (1 - k / n) for k in range(n)]
                    gl = sum(widths[1:]) * L / 1e3
                    sh = sum(w_ + 1 for w_ in widths) * L / 1e3
                else:
                    gl = (n - 1) * wid * L / 1e3
                    sh = n * (wid + 1) * L / 1e3
                sand = abs(n * s - th_lam) > 0.01
                rec.update(new="%d x %.1f laminated%s" % (n, s, ", sanded" if sand else ""), t_new=th_lam, n=n,
                           mass_wood=m0 * vol_ratio, glue_m2=gl, sheet_m2=sh / ETA_STRIP,
                           note="sand to %.1f" % th_lam if sand else "")
        out.append(rec)
    for rec in out:
        rec["mass_glue"] = rec["glue_m2"] * glue
        rec["mass_new"] = rec["mass_wood"] + rec["mass_glue"]
    return out


def summary(out):
    d = {}
    for a in ("Pod", "Wing", "Tail"):
        sub = [r for r in out if r["assembly"] == a]
        d[a] = (sum(r["mass_today"] for r in sub), sum(r["mass_new"] for r in sub))
    old = sum(v[0] for v in d.values())
    new = sum(v[1] for v in d.values())
    pod_glue = POD_GLUE_FRAC * (d["Pod"][1] - d["Pod"][0])   # the 10 % assembly-glue rule follows the pod wood
    empty = EMPTY_TODAY + (new - old) + pod_glue
    sheets = sum(r["sheet_m2"] for r in out)
    nb = math.ceil(sheets * (1 + SPARE) / SHEET_M2)
    feasible = not any("NOT FEASIBLE" in r.get("note", "") for r in out)
    nlam = sum(1 for r in out if r["n"] > 1 and not r["new"].startswith("keep"))
    glue = sum(r["mass_glue"] for r in out)
    return dict(d=d, old=old, new=new, empty=empty, score=WATER * 100 / empty, sheets_m2=sheets, buy=nb,
                feasible=feasible, laminated_parts=nlam, glue=glue)


def baseline_generic():
    """today's thicknesses and materials, every balsa part at the generic 0.14 g/cm3."""
    rows = list(csv.DictReader(open(os.path.join(HERE, "p1_parts.csv"), encoding="utf-8")))
    dm = sum(float(r["mass_g"]) * (RHO_BALSA / RHO_TODAY[r["mat"]] - 1) for r in rows if r["mat"].startswith("balsa"))
    dpod = sum(float(r["mass_g"]) * (RHO_BALSA / RHO_TODAY[r["mat"]] - 1) for r in rows
               if r["mat"].startswith("balsa") and r["assembly"] == "Pod")
    return EMPTY_TODAY + dm + POD_GLUE_FRAC * dpod


def main():
    b = baseline_generic()
    print("Today as modelled: empty %.1f g, score %.1f" % (EMPTY_TODAY, WATER * 100 / EMPTY_TODAY))
    print("Today at generic medium 0.14 (no light/hard grades): empty %.1f g, score %.1f" % (b, WATER * 100 / b))
    summ = []
    for s in STOCKS:
        out = run(s)
        S = summary(out)
        lo, hi = (summary(run(s, g))["empty"] for g in GLUE_RANGE)
        fn = os.path.join(HERE, "p1_schedule_%s.csv" % ("%.1f" % s).replace(".", "p"))
        keys = ["name", "assembly", "kind", "mat_today", "t_today", "mass_today", "new", "n", "t_new", "mass_wood",
                "mass_glue", "mass_new", "note"]
        with open(fn, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            for r in out:
                w.writerow({k: (round(r[k], 2) if isinstance(r[k], float) else r[k]) for k in keys})
        row = dict(stock="%.1f mm medium" % s, pod=S["d"]["Pod"][1], wing=S["d"]["Wing"][1], tail=S["d"]["Tail"][1],
                   wood_today=S["old"], wood_new=S["new"], lam_glue=S["glue"], empty=S["empty"], score=S["score"],
                   empty_glue_lo=lo, empty_glue_hi=hi, sheets_m2=S["sheets_m2"], buy_100x1000=S["buy"],
                   laminated_parts=S["laminated_parts"], feasible=S["feasible"])
        summ.append(row)
        print("%-15s pod %5.1f wing %5.1f tail %4.1f | wood %5.1f -> %5.1f (lam glue %4.1f) | empty %5.1f g "
              "(glue 20-80: %5.1f-%5.1f) score %5.1f | %.2f m2 -> buy %d sheets | %d laminated parts %s" % (
                  row["stock"], row["pod"], row["wing"], row["tail"], row["wood_today"], row["wood_new"], row["lam_glue"],
                  row["empty"], lo, hi, row["score"], row["sheets_m2"], row["buy_100x1000"], row["laminated_parts"],
                  "" if row["feasible"] else "NOT FEASIBLE (D-box)"))
    with open(os.path.join(HERE, "p1_summary.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summ[0]))
        w.writeheader()
        for r in summ:
            w.writerow({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})


if __name__ == "__main__":
    main()
