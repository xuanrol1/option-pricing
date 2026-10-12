import math
import pytest
from pricing import bs_price

# Hull, Options, Futures, and Other Derivatives, Example 15.6
HULL = dict(S=42, K=40, T=0.5, r=0.10, sigma=0.20)


def test_hull_textbook_example():
    assert bs_price(**HULL, option_type="call") == pytest.approx(4.76, abs=0.005)
    assert bs_price(**HULL, option_type="put") == pytest.approx(0.81, abs=0.005)


@pytest.mark.parametrize("S", [20, 40, 42, 60, 100])
@pytest.mark.parametrize("sigma", [0.05, 0.2, 0.6])
@pytest.mark.parametrize("T", [0.1, 0.5, 2.0])
def test_put_call_parity(S, sigma, T):
    K, r = 40, 0.05
    C = bs_price(S, K, T, r, sigma, "call")
    P = bs_price(S, K, T, r, sigma, "put")
    assert C - P == pytest.approx(S - K * math.exp(-r * T), abs=1e-10)


def test_rejects_unknown_option_type():
    with pytest.raises(ValueError):
        bs_price(**HULL, option_type="straddle")
