"""Pictures for the pod structure study: element maps on the right wall, left wall and belly, and an iso view."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402


def _polys(m, idx):
    nd = m["nodes"]
    out = []
    for i in idx:
        k = 4 if m["nn"][i] == 8 else 3
        out.append([nd[v] for v in m["elems"][i][:k]])
    return out


def maps(m, ctx, val, path, title, vmin=None, vmax=None, cmap="viridis", label="", mask=None, marks=()):
    """Three panels: right wall (seen from +Y), left wall (seen from -Y, X still to the right), belly (from below).
    val: per-element value. mask: elements to draw (default all skin-like elements)."""
    X, Y, Z = ctx["cen"].T
    n = ctx["nrm"]
    if mask is None:
        mask = np.ones(len(X), bool)
    sel = {"right wall (Y > 0)": mask & (n[:, 1] > 0.5) & (Y > 0),
           "left wall (Y < 0)": mask & (n[:, 1] < -0.5) & (Y < 0),
           "belly (from below, Y up)": mask & (n[:, 2] < -0.5)}
    vmin = np.nanmin(val[mask]) if vmin is None else vmin
    vmax = np.nanmax(val[mask]) if vmax is None else vmax
    fig, axs = plt.subplots(3, 1, figsize=(13, 10.5))
    for ax, (nm, s) in zip(axs, sel.items()):
        idx = np.where(s)[0]
        P3 = _polys(m, idx)
        if "belly" in nm:
            P2 = [[(p[0], p[1]) for p in poly] for poly in P3]
        else:
            P2 = [[(p[0], p[2]) for p in poly] for poly in P3]
        pc = PolyCollection(P2, array=val[idx], cmap=cmap, edgecolors="none")
        pc.set_clim(vmin, vmax)
        ax.add_collection(pc)
        ax.autoscale()
        ax.set_aspect("equal")
        ax.set_title(nm, fontsize=10)
        ax.set_xlabel("X mm")
        ax.set_ylabel("Y mm" if "belly" in nm else "Z mm")
        for mk in marks:
            if mk[0] == nm[:4]:
                ax.plot(*mk[1], "r+", ms=12, mew=2)
        ax.grid(alpha=0.25)
    fig.suptitle(title, fontsize=12)
    fig.colorbar(pc, ax=axs, shrink=0.8, label=label)
    fig.savefig(path, dpi=110)
    plt.close(fig)


def iso(m, ctx, val, path, title, vmin=None, vmax=None, cmap="viridis", label="", disp=None, scale=0.0, elev=22, azim=-60):
    """Iso view of all elements coloured by val; optional displaced shape (disp {node: vec}, scale)."""
    nd = dict(m["nodes"])
    if disp is not None and scale:
        nd = {k: tuple(np.add(v, scale * disp.get(k, np.zeros(3)))) for k, v in nd.items()}
    polys = []
    for i in range(len(m["elems"])):
        k = 4 if m["nn"][i] == 8 else 3
        polys.append([nd[v] for v in m["elems"][i][:k]])
    vmin = np.nanmin(val) if vmin is None else vmin
    vmax = np.nanmax(val) if vmax is None else vmax
    cm = plt.get_cmap(cmap)
    cols = cm(np.clip((val - vmin) / max(vmax - vmin, 1e-12), 0, 1))
    fig = plt.figure(figsize=(12, 7.5))
    ax = fig.add_subplot(111, projection="3d")
    pc = Poly3DCollection(polys, facecolors=cols, edgecolors="none", linewidths=0)
    ax.add_collection3d(pc)
    xyz = np.array(list(nd.values()))
    c = xyz.mean(axis=0)
    r = (xyz.max(axis=0) - xyz.min(axis=0)).max() / 2
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r * 0.6, c[2] + r * 0.6)
    ax.set_box_aspect((1, 1, 0.6))
    ax.view_init(elev=elev, azim=azim)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    sm = plt.cm.ScalarMappable(cmap=cm)
    sm.set_clim(vmin, vmax)
    fig.colorbar(sm, ax=ax, shrink=0.6, label=label)
    ax.set_title(title, fontsize=11)
    fig.savefig(path, dpi=110)
    plt.close(fig)
