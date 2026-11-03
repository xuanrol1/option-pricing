import pytest
from pricing import bs_price
from pricing import binomial_price
from pricing.implied_vol import implied_vol_american_put, implied_vol_bisection, implied_vol_newton

METHODS = [implied_vol_bisection, implied_vol_newton]


@pytest.mark.parametrize("method", METHODS)
@pytest.mark.parametrize("option_type", ["call", "put"])
@pytest.mark.parametrize("S", [35, 40, 45])
@pytest.mark.parametrize("T", [0.25, 1.0, 2.0])
@pytest.mark.parametrize("sigma", [0.1, 0.2, 0.45, 0.8])
def test_round_trip(method, option_type, S, T, sigma):
    K, r = 40, 0.05
    price = bs_price(S, K, T, r, sigma, option_type)                                        
    assert method(price, S, K, T, r, option_type) == pytest.approx(sigma, abs=1e-6)   


@pytest.mark.parametrize("method", METHODS)
def test_rejects_price_above_upper_bound(method):
    with pytest.raises(ValueError):
        method(50, 42, 40, 0.5, 0.10, "call")
        

@pytest.mark.parametrize("method", METHODS)
def test_deep_out_of_the_money_put(method):
    S, K, T, r, sigma = 55, 40, 0.5, 0.05, 0.05
    price = bs_price(S, K, T, r, sigma, "put")
    assert method(price, S, K, T, r, "put") == pytest.approx(sigma, abs=1e-6)

@pytest.mark.parametrize("S", [32, 40, 48])
@pytest.mark.parametrize("T", [0.25, 1.0])
@pytest.mark.parametrize("sigma", [0.15, 0.3, 0.6])
def test_american_put_round_trip(S, T, sigma):
    K, r = 40, 0.05
    price = binomial_price(S, K, T, r, sigma, "put", n=300, american=True)
    if price <= K - S:
        # Deep in the money at low σ the put is exercised at once and is worth exactly
        # K − S for every low enough σ, so σ cannot be recovered (S = 32, σ = 15%).
        with pytest.raises(ValueError):
            implied_vol_american_put(price, S, K, T, r, n=300)
    else:
        assert implied_vol_american_put(price, S, K, T, r, n=300) == pytest.approx(sigma, abs=1e-5)


def test_european_formula_overstates_american_put_vol():
    # Feeding an American put price into Black–Scholes treats the early-exercise premium
    # as extra volatility.
    S, K, T, r, sigma = 36, 40, 1.0, 0.05, 0.25
    price = binomial_price(S, K, T, r, sigma, "put", n=500, american=True)
    assert implied_vol_american_put(price, S, K, T, r) == pytest.approx(sigma, abs=1e-5)
    assert implied_vol_newton(price, S, K, T, r, "put") > sigma + 0.02


@pytest.mark.parametrize("price", [8.0, 4.0, 40.0])
def test_american_put_rejects_prices_outside_bounds(price):
    # S = 32, K = 40: intrinsic value 8, upper bound K = 40; 4 is below intrinsic.
    with pytest.raises(ValueError):
        implied_vol_american_put(price, 32, 40, 0.5, 0.05)
