"""AMZN volatility smile from calls and puts on the same expiry.

Calls are priced with Black–Scholes (AMZN pays no dividend, so an American call is worth
the same as a European one). Puts are American, so their implied volatility comes from
the binomial tree; for comparison the script also runs the European formula on the puts.

Run from the repository root:  python -m examples.vol_smile_puts [EXPIRY]
"""
import sys
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
from pricing import implied_vol_american_put, implied_vol_newton


def clean(chain):
    chain = chain.copy()
    chain["mid"] = (chain["bid"] + chain["ask"]) / 2
    chain["spread"] = (chain["ask"] - chain["bid"]) / chain["mid"]
    return chain[(chain["bid"] > 0) & (chain["spread"] < 0.2)]


def solve(f, *args):
    try:
        return f(*args)
    except ValueError:          # price outside the no-arbitrage bounds
        return float("nan")


def smile(spot, r, T, calls, puts):
    calls = clean(calls)
    puts = clean(puts)
    calls["iv"] = [solve(implied_vol_newton, m, spot, k, T, r, "call")
                   for m, k in zip(calls["mid"], calls["strike"])]
    puts["iv_american"] = [solve(implied_vol_american_put, m, spot, k, T, r)
                           for m, k in zip(puts["mid"], puts["strike"])]
    puts["iv_european"] = [solve(implied_vol_newton, m, spot, k, T, r, "put")
                           for m, k in zip(puts["mid"], puts["strike"])]
    return calls, puts


def plot(spot, expiry, calls, puts, path):
    """Left: the smile from out-of-the-money options only (puts below spot, calls above).
    Right: American tree vs European formula on every put, in and out of the money."""
    lo, hi = 0.8 * spot, 1.3 * spot
    c = calls[(calls["strike"] >= spot) & (calls["strike"] < hi)]
    p_otm = puts[(puts["strike"] <= spot) & (puts["strike"] > lo)]
    p_all = puts[(puts["strike"] > lo) & (puts["strike"] < hi)]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5))
    ax1.plot(p_otm["strike"], p_otm["iv_american"], "s-", label="OTM puts (American tree)")
    ax1.plot(c["strike"], c["iv"], "o-", label="OTM calls (Black–Scholes)")
    ax1.set_title(f"AMZN smile from out-of-the-money options, expiring {expiry}")
    ax2.plot(p_all["strike"], p_all["iv_american"], "s-", label="American tree")
    ax2.plot(p_all["strike"], p_all["iv_european"], "x--", label="European formula")
    ax2.set_title("AMZN puts: in the money the European formula overstates σ")
    for ax in (ax1, ax2):
        ax.axvline(spot, color="gray", linestyle=":", label=f"Spot = {spot:.0f}")
        ax.set_xlabel("Strike K")
        ax.set_ylabel("Implied volatility")
        ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    print(f"Saved {path}")


if __name__ == "__main__":
    expiry = sys.argv[1] if len(sys.argv) > 1 else "2026-11-20"
    ticker = yf.Ticker("AMZN")
    spot = ticker.history(period="5d")["Close"].iloc[-1]
    r = yf.Ticker("^IRX").history(period="5d")["Close"].iloc[-1] / 100   # 13-week T-bill, quoted in %
    T = (pd.Timestamp(expiry) - pd.Timestamp.today().normalize()).days / 365
    chain = ticker.option_chain(expiry)
    calls, puts = smile(spot, r, T, chain.calls, chain.puts)
    print(f"Spot {spot:.2f}  r {r:.4f}  T {T:.4f}")
    print(puts[["strike", "mid", "iv_american", "iv_european", "impliedVolatility"]].to_string(index=False))
    plot(spot, expiry, calls, puts, "docs/vol_smile_puts.png")
