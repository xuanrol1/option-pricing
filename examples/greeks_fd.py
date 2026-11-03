"""Compare analytical Greeks with central finite differences of the Black–Scholes price.

Prints a Markdown table for the Hull example and saves docs/greeks_fd_error.png,
which shows how the finite-difference error depends on the bump size h.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pricing import bs_price, delta, gamma, vega

P = dict(S=42, K=40, T=0.5, r=0.10, sigma=0.20)   # Hull, Example 15.6
INK, MUTED, SURFACE = "#0b0b0b", "#52514e", "#fcfcfb"
COLORS = {"Delta": "#2a78d6", "Gamma": "#eb6834", "Vega": "#1f9e74"}


def price(**kw):
    return bs_price(**{**P, **kw}, option_type="call")


def fd_delta(h):
    return (price(S=P["S"] + h) - price(S=P["S"] - h)) / (2 * h)


def fd_gamma(h):
    return (price(S=P["S"] + h) - 2 * price() + price(S=P["S"] - h)) / h**2


def fd_vega(h):
    return (price(sigma=P["sigma"] + h) - price(sigma=P["sigma"] - h)) / (2 * h)


GREEKS = {"Delta": (delta(**P, option_type="call"), fd_delta),
          "Gamma": (gamma(**P), fd_gamma),
          "Vega": (vega(**P), fd_vega)}


def table(h=1e-4):
    lines = ["| Greek | Analytical | Central difference (h = 1e-4) | Absolute error |",
             "| --- | --- | --- | --- |"]
    for name, (exact, fd) in GREEKS.items():
        approx = fd(h)
        lines.append(f"| {name} | {exact:.8f} | {approx:.8f} | {abs(approx - exact):.1e} |")
    return "\n".join(lines)


def error_figure(path):
    hs = np.logspace(-9, -1, 81)   # h stays below σ = 0.2 so σ − h > 0
    plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
        "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
        "grid.color": "#e4e3df", "grid.linewidth": 0.6, "font.size": 10})
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for name, (exact, fd) in GREEKS.items():
        err = np.array([abs(fd(h) - exact) for h in hs])
        err = np.where(err == 0, np.nan, err)   # exact zeros cannot be drawn on a log scale
        ax.plot(hs, err, color=COLORS[name], lw=1.8, label=name)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set(xlabel="Bump size h", ylabel="|finite difference − analytical|")
    ax.set_title("Finite-difference error: rounding error (small h) vs truncation error (large h)",
                 color=INK, loc="left", fontsize=11)
    ax.annotate("rounding ∝ ε/h\n(Gamma: ε/h²)", xy=(1e-8, 1e-5), color=MUTED, fontsize=9)
    ax.annotate("truncation ∝ h²", xy=(3e-2, 1e-9), color=MUTED, fontsize=9)
    ax.legend(frameon=False, loc="lower left")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    print(table())
    error_figure("docs/greeks_fd_error.png")
