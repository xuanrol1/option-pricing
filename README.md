# option-pricing

Black–Scholes option pricing and Greeks in Python, with analytical, finite-difference and Monte Carlo validation.

## Status

| Component | Status |
| --- | --- |
| Black–Scholes call and put prices | Done |
| Put-call parity and textbook checks | Done |
| Greeks: Delta, Gamma, Vega, Theta, Rho | In progress |
| Finite-difference and Monte Carlo validation | Planned |

## Model

For a European option on a non-dividend-paying stock:

```text
d1 = [ln(S/K) + (r + σ²/2) T] / (σ √T)
d2 = d1 − σ √T

Call = S N(d1) − K e^(−rT) N(d2)
Put  = K e^(−rT) N(−d2) − S N(−d1)
```

## Validation

- **Textbook value:** Hull's Example 15.6 (S = 42, K = 40, T = 0.5, r = 10%, σ = 20%) gives a call of 4.76 and a put of 0.81.
- **Put-call parity:** `C − P = S − K e^(−rT)` holds to 1e-10 across a grid of prices, volatilities and maturities. Parity follows from no-arbitrage alone, so it catches sign errors in the put formula that would otherwise run without error.

## Run it

```bash
pip install -r requirements.txt
pytest
```

```python
from pricing import bs_price
bs_price(42, 40, 0.5, 0.10, 0.20, "call")   # 4.7594...
```
