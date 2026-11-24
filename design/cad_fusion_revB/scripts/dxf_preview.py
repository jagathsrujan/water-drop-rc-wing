"""PNG previews of the laser sheets (matplotlib): CUT red, ENGRAVE blue, SHEET grey."""
import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "cad", "scripts"))
import dxf_io

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dxf")
IMG = os.path.join(os.path.dirname(D), "img")


def draw(files, out, cols=1):
    rows = (len(files) + cols - 1) // cols
    fig, axs = plt.subplots(rows, cols, figsize=(9 * cols, 3.3 * rows), squeeze=False)
    for ax, fn in zip(axs.flat, files):
        for kind, lay, g in dxf_io.read(os.path.join(D, fn)):
            col = {"CUT": "#d22", "ENGRAVE": "#15c", "SHEET": "#999"}.get(lay, "k")
            lw = 0.5 if lay != "SHEET" else 0.8
            if kind == "poly":
                xs = [p[0] for p in g]; ys = [p[1] for p in g]
                if lay != "ENGRAVE":
                    xs.append(g[0][0]); ys.append(g[0][1])
                ax.plot(xs, ys, color=col, lw=lw)
            elif kind == "circle":
                ax.add_patch(plt.Circle((g[0], g[1]), g[2], fill=False, color=col, lw=lw))
        ax.set_aspect("equal"); ax.set_title(fn, fontsize=9); ax.axis("off")
    for ax in list(axs.flat)[len(files):]:
        ax.axis("off")
    fig.tight_layout(); fig.savefig(out, dpi=170); plt.close(fig)


if __name__ == "__main__":
    files = sorted(f for f in os.listdir(D) if f.endswith(".dxf"))
    sel = sys.argv[1:] or files
    draw([f for f in files if any(s in f for s in sel)], os.path.join(IMG, "dxf_preview.png"))
    print(len(files), "sheets")
