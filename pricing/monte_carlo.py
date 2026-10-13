"""Monte Carlo pricing of European options under risk-neutral geometric Brownian motion."""
import numpy as np


def mc_price(S, K, T, r, sigma, option_type="call", n=100000, seed=0):
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal(n)
    S_T = S * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
    call = np.maximum(S_T - K, 0)
    put = np.maximum(K - S_T, 0)
    if option_type == "call":
        payoff = call
    elif option_type == "put":
        payoff = put
    else:
        raise ValueError("option_type must be 'call' or 'put'")
    Mean = np.exp(-r * T) * payoff.mean()
    return Mean


def mc_standard_error(S, K, T, r, sigma, option_type="call", n=100000, seed=0):
    """Standard error of mc_price: the discounted payoff's sample std divided by sqrt(n)."""
    rng = np.random.default_rng(seed)
    S_T = S * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * rng.standard_normal(n))
    payoff = np.maximum(S_T - K, 0) if option_type == "call" else np.maximum(K - S_T, 0)
    return np.exp(-r * T) * payoff.std(ddof=1) / np.sqrt(n)
