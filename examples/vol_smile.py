import pandas as pd
import yfinance as yf
from pricing import implied_vol_newton
import matplotlib.pyplot as plt

ticker = yf.Ticker("AMZN")
spot = ticker.history(period="5d")["Close"].iloc[-1]
r = yf.Ticker("^IRX").history(period="5d")["Close"].iloc[-1] / 100   # 13 周国债收益率，报价单位是 %

expiry = "2026-11-20"
T = (pd.Timestamp(expiry) - pd.Timestamp.today()).days / 365

calls = ticker.option_chain(expiry).calls
calls["mid"] = (calls["ask"] + calls["bid"]) / 2                               # ① bid 和 ask 的中间价
calls["spread"] = (calls["ask"] - calls["bid"]) / calls["mid"]
calls = calls[(calls["bid"] > 0) & (calls["spread"] < 0.2)]

print("Spot:", spot, " r:", r, " T:", T)
print(calls[["strike", "bid", "ask", "mid", "spread", "impliedVolatility"]])


my_ivs = []
for _, row in calls.iterrows():
    try:
        iv = implied_vol_newton(row["mid"], spot, row["strike"], T, r, "call")       
    except ValueError:
        iv = float("nan")
    my_ivs.append(iv)

calls["my_iv"] = my_ivs
print(calls[["strike", "mid", "impliedVolatility", "my_iv"]])


plot_data = calls[(calls["strike"] > 0.8 * spot) & (calls["strike"] < 1.3 * spot)]

plt.figure(figsize=(8, 4.5))
plt.plot(plot_data["strike"], plot_data["my_iv"], "o-", label="My Newton solver")
plt.plot(plot_data["strike"], plot_data["impliedVolatility"], "x--", label="Yahoo Finance")
plt.axvline(spot, color="gray", linestyle=":", label=f"Spot = {spot:.0f}")
plt.xlabel("Strike K")
plt.ylabel("Implied volatility")
plt.title(f"AMZN implied volatility, calls expiring {expiry}")
plt.legend()
plt.savefig("docs/vol_smile.png", dpi=160)
plt.show()