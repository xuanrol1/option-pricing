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
    lo, hi = 0.8 * spot, 1.3 * spot
    c = calls[(calls["strike"] > lo) & (calls["strike"] < hi)]
    p = puts[(puts["strike"] > lo) & (puts["strike"] < hi)]
    plt.figure(figsize=(8, 4.5))
    plt.plot(c["strike"], c["iv"], "o-", label="Calls (Black–Scholes)")
    plt.plot(p["strike"], p["iv_american"], "s-", label="Puts (American tree)")
    plt.plot(p["strike"], p["iv_european"], "x--", alpha=0.6, label="Puts (European formula)")
    plt.axvline(spot, color="gray", linestyle=":", label=f"Spot = {spot:.0f}")
    plt.xlabel("Strike K")
    plt.ylabel("Implied volatility")
    plt.title(f"AMZN implied volatility, calls and puts expiring {expiry}")
    plt.legend()
    plt.savefig(path, dpi=160)


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
