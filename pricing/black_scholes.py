"""Black–Scholes prices for European calls and puts on a non-dividend-paying stock."""
import math
from scipy.stats import norm


def d1_d2(S, K, T, r, sigma):
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return d1, d2


def bs_price(S, K, T, r, sigma, option_type="call"):
    d1, d2 = d1_d2(S, K, T, r, sigma)
    C = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    P = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    if option_type == "call":
        return C
    elif option_type == "put":
        return P
    else:
        raise ValueError("option_type must be 'call' or 'put'")
