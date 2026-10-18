import pytest
from pricing import bs_price
from pricing.implied_vol import implied_vol_bisection, implied_vol_newton

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