import math
from .black_scholes import bs_price
from .greeks import vega
from .binomial import binomial_price


def _check_bounds(price, S, K, T, r, option_type):
    disc_K = K * math.exp(-r * T)
    if option_type == "call":
        lower = max(S - disc_K, 0)
        upper = S
    else:
        lower = max(disc_K - S, 0)
        upper = disc_K
    
    if price <= lower or price >= upper:
        raise ValueError(f"Price {price} is outside the no-arbitrage bounds ({lower}, {upper})")
    
    

def implied_vol_bisection(price, S, K, T, r, option_type="call", tol=1e-8, max_iter=200):
    _check_bounds(price, S, K, T, r, option_type)
    low = 1e-4
    high = 5.0

    for i in range(max_iter):
        mid = (high + low) / 2
        model_price = bs_price(S, K, T, r, mid, option_type)

        if model_price > price:
            high = mid
        else:
            low = mid

        if high - low < tol:
            break

    return mid


def implied_vol_newton(price, S, K, T, r, option_type="call", tol=1e-8, max_iter=50):
    _check_bounds(price, S, K, T, r, option_type)
    sigma = 0.2                                  

    for i in range(max_iter):
        model_price = bs_price(S, K, T, r, sigma, option_type)
        diff = model_price - price 
        v = vega(S, K, T, r, sigma) 
        
        if v < 1e-8:
            return implied_vol_bisection(price, S, K, T, r, option_type)
        
        step = diff / v
        sigma = sigma - step
        
        if abs(step) < tol:
            return sigma


    return implied_vol_bisection(price, S, K, T, r, option_type)   


def implied_vol_american_put(price, S, K, T, r, n=500, tol=1e-6, max_iter=100):
    """Implied volatility of an American put, by bisection on the CRR tree price.

    An American put is worth at least its intrinsic value K − S (it can be exercised
    now) and at most K. At or below intrinsic value no unique σ exists: every low enough
    σ gives exactly K − S, because the put would be exercised at once.
    """
    lower, upper = max(K - S, 0), K
    if price <= lower or price >= upper:
        raise ValueError(f"Price {price} is outside the American put bounds ({lower}, {upper})")
    model = lambda sigma: binomial_price(S, K, T, r, sigma, "put", n=n, american=True)
    # CRR needs d < e^(r dt) < u, i.e. σ > r √dt; below that p falls outside (0, 1).
    low, high = max(1e-4, 1.01 * abs(r) * math.sqrt(T / n)), 5.0
    if not model(low) < price < model(high):
        raise ValueError(f"Price {price} is not reached for σ in [{low}, {high}]")
    for _ in range(max_iter):
        mid = (low + high) / 2
        if model(mid) > price:
            high = mid
        else:
            low = mid
        if high - low < tol:
            break
    return (low + high) / 2
