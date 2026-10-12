"""Black–Scholes Greeks for European options on a non-dividend-paying stock."""
from scipy.stats import norm
from .black_scholes import d1_d2
import math

def delta(S, K, T, r, sigma, option_type="call"):
    d1, d2 = d1_d2(S, K, T, r, sigma)
    delta_call = norm.cdf(d1)
    delta_put = (norm.cdf(d1)) - 1
    if option_type == "call":
        return delta_call
    elif option_type == "put":
        return delta_put
    else:
        raise ValueError("option_type must be 'call' or 'put'")


def gamma(S, K, T, r, sigma):
    d1, d2 = d1_d2(S, K, T, r, sigma)
    Gamma = norm.pdf(d1) / (S * sigma * math.sqrt(T))
    return Gamma

def vega(S, K, T, r, sigma):
    d1, d2 = d1_d2(S, K, T, r, sigma)
    Vega = S * norm.pdf(d1) * (math.sqrt(T))
    return Vega

def theta(S, K, T, r, sigma, option_type="call"):
    d1, d2 = d1_d2(S, K, T, r, sigma)
    first = - (S * norm.pdf(d1) * sigma) / (2 * math.sqrt(T))
    Theta_call = first - r * K * math.exp(-r * T) * norm.cdf(d2)
    Theta_put  = first + r * K * math.exp(-r * T) * norm.cdf(-d2)
    if option_type == "call":
        return Theta_call
    elif option_type == "put":
        return Theta_put
    else:
        raise ValueError("option_type must be 'call' or 'put'")

def rho(S, K, T, r, sigma, option_type="call"):
    d1, d2 = d1_d2(S, K, T, r, sigma)
    Rho_call = K * T * math.exp(-r * T) * norm.cdf(d2)
    Rho_put = - (K * T * math.exp(-r * T) * norm.cdf(-d2))
    if option_type == "call":
        return Rho_call
    elif option_type == "put":
        return Rho_put
    else:
        raise ValueError("option_type must be 'call' or 'put'")
