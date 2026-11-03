"""Binomial tree convergence to Black–Scholes, and the early-exercise boundary of an American put."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pricing import american_put_boundary, binomial_price, bs_price

P = dict(S=40, K=40, T=1.0, r=0.05, sigma=0.30)
CALL, PUT = "#2a78d6", "#eb6834"
INK, MUTED, SURFACE = "#0b0b0b", "#52514e", "#fcfcfb"

plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": "#e4e3df", "grid.linewidth": 0.6, "font.size": 10})


def convergence_figure(path):
    ns = np.arange(5, 201)
    euro = np.array([binomial_price(**P, option_type="put", n=n) for n in ns])
    amer = np.array([binomial_price(**P, option_type="put", n=n, american=True) for n in ns])
    exact = bs_price(**P, option_type="put")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(ns, euro, color=CALL, lw=1.2, label="European put (tree)")
    ax.plot(ns, amer, color=PUT, lw=1.2, label="American put (tree)")
    ax.axhline(exact, color=INK, lw=1, ls="--", label=f"Black–Scholes European put {exact:.4f}")
    premium = binomial_price(**P, option_type="put", n=2000, american=True) - exact
    ax.annotate(f"early-exercise premium ≈ {premium:.3f}", xy=(120, exact + premium / 2),
                color=MUTED, fontsize=9)
    ax.set(xlabel="Number of tree steps n", ylabel="Put price")
    ax.set_title("CRR tree prices converge like 1/n, alternating between even and odd n",
                 color=INK, loc="left", fontsize=11)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def boundary_figure(path):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for sigma, color in ((0.20, CALL), (0.30, PUT), (0.45, "#1f9e74")):
        t, S_star = american_put_boundary(**{**P, "sigma": sigma}, n=1000)
        # Even steps share node prices, so plotting them alone removes the tree's zigzag.
        ax.plot(t[::2], S_star[::2], color=color, lw=1.8, label=f"σ = {sigma:.0%}")
    ax.axhline(P["K"], color=MUTED, lw=0.8, ls="--")
    ax.annotate("strike K = 40", xy=(0.3, P["K"] - 1.0), color=MUTED, fontsize=9)
    ax.annotate("exercise below the curve", xy=(0.05, 24), color=MUTED, fontsize=9)
    ax.set(xlabel="Time t (years; expiry at T = 1)", ylabel="Critical stock price S*(t)")
    ax.set_title("American put: early-exercise boundary  (K = 40, r = 5%)",
                 color=INK, loc="left", fontsize=11)
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    convergence_figure("docs/binomial_convergence.png")
    boundary_figure("docs/put_boundary.png")
