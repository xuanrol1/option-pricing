import pytest
from pricing import bs_price, delta, gamma, rho, theta, vega

# Hull, Options, Futures, and Other Derivatives, Example 15.6 parameters
HULL = dict(S=42, K=40, T=0.5, r=0.10, sigma=0.20)
GRID = [dict(S=S, K=40, T=T, r=0.05, sigma=sigma)
        for S in (25, 40, 55) for T in (0.1, 1.0) for sigma in (0.1, 0.4)]


def test_hull_values():
    assert delta(**HULL, option_type="call") == pytest.approx(0.7791, abs=1e-4)
    assert delta(**HULL, option_type="put") == pytest.approx(-0.2209, abs=1e-4)
    assert gamma(**HULL) == pytest.approx(0.0500, abs=1e-4)
    assert vega(**HULL) == pytest.approx(8.813, abs=1e-3)
    assert theta(**HULL, option_type="call") == pytest.approx(-4.559, abs=1e-3)
    assert theta(**HULL, option_type="put") == pytest.approx(-0.754, abs=1e-3)
    assert rho(**HULL, option_type="call") == pytest.approx(13.982, abs=1e-3)
    assert rho(**HULL, option_type="put") == pytest.approx(-5.043, abs=1e-3)


def _bump(p, name, h):
    up, down = dict(p), dict(p)
    up[name] += h; down[name] -= h
    return up, down


@pytest.mark.parametrize("p", GRID)
@pytest.mark.parametrize("option_type", ["call", "put"])
def test_greeks_match_finite_differences(p, option_type):
    """Analytical Greeks must agree with central differences of the price."""
    price = lambda q: bs_price(**q, option_type=option_type)
    h = 1e-4
    up, down = _bump(p, "S", h)
    assert delta(**p, option_type=option_type) == pytest.approx((price(up) - price(down)) / (2*h), abs=1e-6)
    assert gamma(**p) == pytest.approx((price(up) - 2*price(p) + price(down)) / h**2, abs=1e-4)
    up, down = _bump(p, "sigma", h)
    assert vega(**p) == pytest.approx((price(up) - price(down)) / (2*h), abs=1e-5)
    up, down = _bump(p, "r", h)
    assert rho(**p, option_type=option_type) == pytest.approx((price(up) - price(down)) / (2*h), abs=1e-5)
    # Theta is the change in value as calendar time passes, i.e. as T falls.
    up, down = _bump(p, "T", h)
    assert theta(**p, option_type=option_type) == pytest.approx(-(price(up) - price(down)) / (2*h), abs=1e-5)


@pytest.mark.parametrize("p", GRID)
def test_call_put_relations(p):
    """Differentiating put-call parity: delta differs by 1; gamma and vega are shared."""
    assert delta(**p, option_type="call") - delta(**p, option_type="put") == pytest.approx(1.0)
    assert gamma(**p) > 0 and vega(**p) > 0
    assert rho(**p, option_type="call") > 0 > rho(**p, option_type="put")


@pytest.mark.parametrize("greek", [delta, theta, rho])
def test_rejects_unknown_option_type(greek):
    with pytest.raises(ValueError):
        greek(**HULL, option_type="straddle")
