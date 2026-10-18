"""Plot Black–Scholes prices and Greeks against the stock price, and Monte Carlo convergence."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pricing import bs_price, delta, gamma, mc_price, mc_standard_error, theta, vega

K, T, r, sigma = 40, 0.5, 0.10, 0.20
CALL, PUT = "#2a78d6", "#eb6834"
INK, MUTED, SURFACE = "#0b0b0b", "#52514e", "#fcfcfb"

plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": "#e4e3df", "grid.linewidth": 0.6, "font.size": 10})


def greeks_figure(path):
    S = np.linspace(20, 60, 401)
    panels = [("Price", lambda s, t: bs_price(s, K, T, r, sigma, t), True),
              ("Delta", lambda s, t: delta(s, K, T, r, sigma, t), True),
              ("Gamma (call = put)", lambda s, t: gamma(s, K, T, r, sigma), False),
              ("Vega (call = put)", lambda s, t: vega(s, K, T, r, sigma), False),
              ("Theta (per year)", lambda s, t: theta(s, K, T, r, sigma, t), True)]
    fig, axes = plt.subplots(1, 5, figsize=(17, 3.6))
    for ax, (title, f, both) in zip(axes, panels):
        ax.plot(S, [f(s, "call") for s in S], color=CALL, lw=2, label="Call")
        if both:
            ax.plot(S, [f(s, "put") for s in S], color=PUT, lw=2, label="Put")
        ax.axvline(K, color=MUTED, lw=0.8, ls="--")
        ax.set_title(title, color=INK, loc="left", fontsize=11)
        ax.set_xlabel("Stock price S")
    axes[0].legend(frameon=False)
    s_peak = K * np.exp(-(r + 1.5 * sigma**2) * T)   # where d1 = -sigma*sqrt(T)
    axes[2].annotate(f"peak at S ≈ {s_peak:.1f} (d₁ = −σ√T)", xy=(s_peak, gamma(s_peak, K, T, r, sigma)), xytext=(44, 0.06),
                     color=MUTED, fontsize=9, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    fig.suptitle(f"Black–Scholes price and Greeks  (K = {K}, T = {T}, r = {r:.0%}, σ = {sigma:.0%})",
                 color=INK, x=0.01, ha="left", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def convergence_figure(path):
    S0 = 42
    ns = np.unique(np.logspace(2, 6, 25).astype(int))
    # An independent seed per point, so each estimate is a separate experiment.
    est = np.array([mc_price(S0, K, T, r, sigma, "call", n=n, seed=i) for i, n in enumerate(ns)])
    se = np.array([mc_standard_error(S0, K, T, r, sigma, "call", n=n, seed=i) for i, n in enumerate(ns)])
    exact = bs_price(S0, K, T, r, sigma, "call")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.fill_between(ns, est - 2 * se, est + 2 * se, color=CALL, alpha=0.15, lw=0, label="±2 standard errors")
    ax.plot(ns, est, color=CALL, lw=2, marker="o", ms=4, label="Monte Carlo estimate")
    ax.axhline(exact, color=INK, lw=1, ls="--", label=f"Black–Scholes {exact:.4f}")
    ax.set_xscale("log")
    ax.set(xlabel="Number of simulated paths", ylabel="Call price")
    ax.set_title("Monte Carlo converges to the Black–Scholes price  (S = 42)", color=INK, loc="left")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    greeks_figure("docs/greeks.png")
    convergence_figure("docs/mc_convergence.png")
