import pytest
from pricing import bs_price, mc_price, mc_standard_error

CASES = [dict(S=42, K=40, T=0.5, r=0.10, sigma=0.20),
         dict(S=40, K=40, T=1.0, r=0.05, sigma=0.30),
         dict(S=30, K=40, T=2.0, r=0.02, sigma=0.50)]


@pytest.mark.parametrize("p", CASES)
@pytest.mark.parametrize("option_type", ["call", "put"])
def test_mc_within_four_standard_errors_of_black_scholes(p, option_type):
    mc = mc_price(**p, option_type=option_type, n=200000, seed=1)
    se = mc_standard_error(**p, option_type=option_type, n=200000, seed=1)
    assert abs(mc - bs_price(**p, option_type=option_type)) < 4 * se


def test_error_shrinks_like_one_over_sqrt_n():
    p = CASES[0]
    small = mc_standard_error(**p, n=10000)
    large = mc_standard_error(**p, n=1000000)
    assert large == pytest.approx(small / 10, rel=0.05)


def test_rejects_unknown_option_type():
    with pytest.raises(ValueError):
        mc_price(**CASES[0], option_type="straddle")
