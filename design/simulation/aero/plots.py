"""P5: figures from the AVL results (results.json, written by run_avl.py).  python design/simulation/aero/plots.py
-> fig/lift_curve.png, fig/pitching_moment.png, fig/drag_polar.png, fig/ld_speed.png (static PNG for the reports)."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "fig")
R = json.load(open(os.path.join(HERE, "results.json")))
S1, S2 = "#2a78d6", "#eb6834"                 # categorical slots 1, 2 (dataviz reference palette)
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def axes(xlabel, ylabel, title):
    fig, ax = plt.subplots(figsize=(5.2, 3.6), dpi=160)
    fig.patch.set_facecolor(SURF)
    ax.set_facecolor(SURF)
    ax.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.set_xlabel(xlabel, color=INK2, fontsize=9)
    ax.set_ylabel(ylabel, color=INK2, fontsize=9)
    ax.set_title(title, color=INK, fontsize=10, loc="left")
    return fig, ax


def save(fig, name):
    os.makedirs(FIG, exist_ok=True)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, name), facecolor=SURF)
    plt.close(fig)


def main():
    sw = R["sweep"]
    a = [r["alpha"] for r in sw]
    st = R["stab_cruise"]
    fig, ax = axes("angle of attack α (deg)", "CL", "Lift curve (AVL, elevator 0)")
    ax.plot(a, [r["CL"] for r in sw], color=S1, lw=2, marker="o", ms=4)
    ax.annotate("CLα %.2f /rad" % st["CLa"], (a[-5], sw[-5]["CL"]), xytext=(-90, 10), textcoords="offset points",
                color=INK2, fontsize=8)
    save(fig, "lift_curve.png")

    fig, ax = axes("angle of attack α (deg)", "Cm about the CG", "Pitching moment, CG X %.0f mm" % R["xcg_mm"])
    ax.axhline(0.0, color=INK2, lw=0.8)
    ax.plot(a, [r["Cm"] for r in sw], color=S1, lw=2, marker="o", ms=4)
    ax.annotate("Cmα %.2f /rad, static margin %.1f %% MAC" % (st["Cma"], R["static_margin_pct"]), (a[2], sw[2]["Cm"]),
                xytext=(10, -4), textcoords="offset points", color=INK2, fontsize=8)
    save(fig, "pitching_moment.png")

    fig, ax = axes("CD (induced + SD7062 profile)", "CL", "Drag polar")
    ax.plot([r["CD"] for r in sw], [r["CL"] for r in sw], color=S1, lw=2, marker="o", ms=4)
    save(fig, "drag_polar.png")

    fig, ax = axes("airspeed V (m/s)", "L/D (trimmed)", "Trimmed L/D, Bengaluru (ρ 1.05)")
    site = "Bengaluru (design)"
    for m, col, lab in ((R["loaded_g"], S1, "loaded %.0f g" % R["loaded_g"]), (R["empty_g"], S2, "empty %.0f g" % R["empty_g"])):
        rows = [r for r in R["trim"] if r["site"] == site and abs(r["mass_g"] - m) < 0.5]
        v = [r["V"] for r in rows]
        ld = [r["LD"] for r in rows]
        ax.plot(v, ld, color=col, lw=2, marker="o", ms=5, label=lab)
        ax.annotate(lab, (v[-1], ld[-1]), xytext=(6, 0), textcoords="offset points", color=INK2, fontsize=8, va="center")
    ax.legend(frameon=False, fontsize=8, labelcolor=INK2, loc="lower center")
    ax.set_xlim(9, 18.5)
    save(fig, "ld_speed.png")
    print("figures in", FIG)


if __name__ == "__main__":
    main()
