import pytest
from pricing import binomial_price, bs_price

CASES = [dict(S=42, K=40, T=0.5, r=0.10, sigma=0.20),
         dict(S=40, K=40, T=1.0, r=0.05, sigma=0.30),
         dict(S=30, K=40, T=2.0, r=0.02, sigma=0.50)]


@pytest.mark.parametrize("p", CASES)
@pytest.mark.parametrize("option_type", ["call", "put"])
def test_european_tree_converges_to_black_scholes(p, option_type):
    tree = binomial_price(**p, option_type=option_type, n=2000)
    assert tree == pytest.approx(bs_price(**p, option_type=option_type), abs=5e-3)


def test_error_shrinks_roughly_like_one_over_n():
    # CRR error oscillates between even and odd n, so compare two even step counts.
    p = CASES[1]
    exact = bs_price(**p)
    err_100 = abs(binomial_price(**p, n=100) - exact)
    err_1000 = abs(binomial_price(**p, n=1000) - exact)
    assert err_1000 < err_100 / 5


@pytest.mark.parametrize("p", CASES)
def test_american_call_equals_european_without_dividends(p):
    # Early exercise of a call on a non-dividend stock gives up time value and interest on K.
    euro = binomial_price(**p, option_type="call", n=500)
    amer = binomial_price(**p, option_type="call", n=500, american=True)
    assert amer == pytest.approx(euro, abs=1e-10)


@pytest.mark.parametrize("p", CASES)
def test_american_put_is_worth_at_least_european_and_intrinsic(p):
    euro = binomial_price(**p, option_type="put", n=500)
    amer = binomial_price(**p, option_type="put", n=500, american=True)
    assert amer >= euro - 1e-12
    assert amer >= max(p["K"] - p["S"], 0)


def test_deep_itm_american_put_has_early_exercise_premium():
    # S=30, K=40: a European put is worth about K e^(−rT) − S here, below intrinsic value 10.
    p = dict(S=30, K=40, T=2.0, r=0.05, sigma=0.20)
    euro = binomial_price(**p, option_type="put", n=500)
    amer = binomial_price(**p, option_type="put", n=500, american=True)
    assert euro < 10 < amer + 1e-12
    assert amer - euro > 0.5


def test_hull_american_put():
    # Hull, Example 21.1: S=50, K=50, T=5/12, r=10%, σ=40%; a 5-step tree gives 4.49.
    amer = binomial_price(50, 50, 5 / 12, 0.10, 0.40, "put", n=5, american=True)
    assert amer == pytest.approx(4.49, abs=0.005)


def test_rejects_unknown_option_type():
    with pytest.raises(ValueError):
        binomial_price(**CASES[0], option_type="straddle")
