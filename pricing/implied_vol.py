import math
from .black_scholes import bs_price
from .greeks import vega


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
